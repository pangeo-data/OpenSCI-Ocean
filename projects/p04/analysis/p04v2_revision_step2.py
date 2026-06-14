#!/usr/bin/env python3
"""
P04 v2 Revision Step 2: Seasonal Granger + MWP swell evidence

Addresses:
  Reviewer 3: seasonal decomposition of Granger
  Reviewer 3: direct evidence for swell attenuation (wave period analysis)
"""

import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
from scipy import stats
import json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

REPO = str(Path(__file__).resolve().parents[3])
P04 = f'{REPO}/projects/p04'
DATA = f'{P04}/data'
OUT = f'{P04}/analysis'
FIG = f'{P04}/figures'

def granger_test(y, x, max_lag=4):
    n = len(y)
    best_aic = np.inf; best_lag = 1; best_f = 0; best_p = 1
    for lag in range(1, max_lag+1):
        T = n - lag; Y = y[lag:]
        X_full = np.ones((T, 1))
        for l in range(1, lag+1):
            X_full = np.column_stack([X_full, y[lag-l:n-l]])
        x_col = X_full.shape[1]
        for l in range(1, lag+1):
            X_full = np.column_stack([X_full, x[lag-l:n-l]])
        try:
            b = np.linalg.lstsq(X_full, Y, rcond=None)[0]
            rss_full = np.sum((Y - X_full @ b)**2)
            X_red = X_full[:, :x_col]
            b_r = np.linalg.lstsq(X_red, Y, rcond=None)[0]
            rss_red = np.sum((Y - X_red @ b_r)**2)
            dfn = lag; dfd = T - X_full.shape[1]
            if dfd <= 0 or rss_full <= 0: continue
            F = ((rss_red - rss_full) / dfn) / (rss_full / dfd)
            p = 1 - stats.f.cdf(F, dfn, dfd)
            aic = T * np.log(rss_full/T) + 2 * X_full.shape[1]
            if aic < best_aic:
                best_aic = aic; best_lag = lag; best_f = F; best_p = p
        except np.linalg.LinAlgError:
            continue
    return best_f, best_p, best_lag

print('='*60)
print('REVISION STEP 2: SEASONAL GRANGER + MWP ANALYSIS')
print('='*60)

# ---- Load precomputed variables from step1 JSON ----
# Recompute monthly variables (need raw data for seasonal split)
print('\n1. Loading data...')
ds_sic = xr.open_dataset(f'{DATA}/era5_sic_SO_1979_2024.nc')
if 'expver' in ds_sic.dims: ds_sic = ds_sic.sel(expver=1)
sic_var = 'siconc' if 'siconc' in ds_sic else 'ci'
sic = np.clip(ds_sic[sic_var].values, 0, 1)
lat_s = ds_sic.latitude.values; lon_s = ds_sic.longitude.values
times = pd.to_datetime(ds_sic.valid_time.values)
ds_sic.close()

ds_swh = xr.open_dataset(f'{DATA}/era5_waves_SO_1979_2024.nc')
if 'expver' in ds_swh.dims: ds_swh = ds_swh.sel(expver=1)
swh = ds_swh['swh'].values
mwp = ds_swh['mwp'].values  # Mean wave period - key for swell evidence
lat_w = ds_swh.latitude.values; lon_w = ds_swh.longitude.values
ds_swh.close()

ds_w = xr.open_dataset(f'{DATA}/era5_wind_SO_1979_2024.nc')
if 'expver' in ds_w.dims: ds_w = ds_w.sel(expver=1)
wspd = np.sqrt(ds_w['u10'].values**2 + ds_w['v10'].values**2)
ds_w.close()

nt = len(times)
cos_lat = np.cos(np.deg2rad(lat_s))
ice_mask = (lat_s >= -75) & (lat_s <= -55)
swh_lat_idx = np.array([np.argmin(np.abs(lat_w - ls)) for ls in lat_s])

# Compute monthly variables
print('2. Computing monthly variables...')
ice_edge_lat = np.full(nt, np.nan)
fetch_proxy = np.full(nt, np.nan)
swh_at_edge = np.full(nt, np.nan)
mwp_at_edge = np.full(nt, np.nan)
sic_mean = np.full(nt, np.nan)
wspd_mean = np.full(nt, np.nan)

for t in range(nt):
    edge_lats = []; swh_vals = []; mwp_vals = []
    for j in range(0, len(lon_s), 2):
        col = sic[t, :, j]
        for i in range(len(lat_s)):
            if col[i] > 0.15 and -74 < lat_s[i] < -50:
                edge_lats.append(lat_s[i])
                eq_i = max(0, i - 8)
                swh_ji = np.argmin(np.abs(lon_w - lon_s[j]))
                sv = swh[t, swh_lat_idx[eq_i], swh_ji]
                mv = mwp[t, swh_lat_idx[eq_i], swh_ji]
                if np.isfinite(sv): swh_vals.append(sv)
                if np.isfinite(mv): mwp_vals.append(mv)
                break
    if edge_lats:
        m = np.mean(edge_lats)
        ice_edge_lat[t] = m
        fetch_proxy[t] = abs(m - (-40.0)) * np.pi / 180 * 6371.0
    if swh_vals: swh_at_edge[t] = np.mean(swh_vals)
    if mwp_vals: mwp_at_edge[t] = np.mean(mwp_vals)
    w = cos_lat[ice_mask][:, np.newaxis]
    s = sic[t, ice_mask, :]; ok = np.isfinite(s)
    sic_mean[t] = np.nansum(s*w)/np.nansum(w*ok) if np.nansum(w*ok)>0 else np.nan
    ws = wspd[t, ice_mask, :]; ok_w = np.isfinite(ws)
    wspd_mean[t] = np.nansum(ws*w)/np.nansum(w*ok_w) if np.nansum(w*ok_w)>0 else np.nan

del sic, wspd, swh, mwp
months = times.month.values

# Deseasonalize
print('3. Deseasonalizing...')
variables = {'SIC': sic_mean, 'Fetch': fetch_proxy, 'SWH_edge': swh_at_edge,
             'IceEdge': ice_edge_lat, 'Wind': wspd_mean, 'MWP_edge': mwp_at_edge}
anom = {}
for name, vals in variables.items():
    clim = np.array([np.nanmean(vals[months == m]) for m in range(1, 13)])
    anom[name] = vals - clim[months - 1]

std = {}
for name, vals in anom.items():
    sigma = np.nanstd(vals)
    std[name] = (vals - np.nanmean(vals)) / sigma if sigma > 0 else vals * 0

# ---- SEASONAL GRANGER ----
print('\n4. Seasonal Granger causality...')
seasons = {'DJF': [12, 1, 2], 'MAM': [3, 4, 5], 'JJA': [6, 7, 8], 'SON': [9, 10, 11]}
key_pair = ('SIC', 'SWH_edge', 'SIC -> SWH')  # Most important link to test seasonally

seasonal_results = {}
for sname, smonths in seasons.items():
    smask = np.isin(months, smonths)
    x = std[key_pair[0]][smask]; y = std[key_pair[1]][smask]
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 30:
        seasonal_results[sname] = {'F': 0, 'p': 1, 'n': int(ok.sum())}
        continue
    F, p, lag = granger_test(y[ok], x[ok], max_lag=3)
    seasonal_results[sname] = {'F': round(F, 2), 'p': round(p, 4), 'lag': lag, 'n': int(ok.sum())}
    sig = '*' if p < 0.05 else 'ns'
    print(f'  {sname}: SIC->SWH F={F:.2f}, p={p:.4f} {sig}, n={ok.sum()}')

# ---- MWP ANALYSIS (swell evidence) ----
print('\n5. MWP analysis (swell evidence)...')
# If swell attenuation is the mechanism, we expect:
# 1. MWP at ice edge should be long (consistent with swell, not wind-sea)
# 2. MWP should increase when SIC decreases (less attenuation of long-period swell)
print(f'  Mean MWP at ice edge: {np.nanmean(mwp_at_edge):.1f} s')
print(f'  MWP range: {np.nanmin(mwp_at_edge[np.isfinite(mwp_at_edge)]):.1f} - {np.nanmax(mwp_at_edge[np.isfinite(mwp_at_edge)]):.1f} s')

# Correlation: SIC anomaly vs MWP anomaly (expect negative: less ice = longer period swell)
ok_mwp = np.isfinite(anom['SIC']) & np.isfinite(anom['MWP_edge'])
r_mwp, p_mwp = stats.pearsonr(anom['SIC'][ok_mwp], anom['MWP_edge'][ok_mwp])
print(f'  SIC vs MWP correlation: r={r_mwp:.3f}, p={p_mwp:.4f} (expect negative)')

# Pre/post 2016 MWP comparison
pre = times < '2016-01-01'; post = times >= '2016-01-01'
mwp_pre = np.nanmean(mwp_at_edge[pre])
mwp_post = np.nanmean(mwp_at_edge[post])
_, p_ttest = stats.ttest_ind(mwp_at_edge[pre & np.isfinite(mwp_at_edge)],
                              mwp_at_edge[post & np.isfinite(mwp_at_edge)])
print(f'  MWP pre-2016: {mwp_pre:.2f} s, post-2016: {mwp_post:.2f} s')
print(f'  MWP change: {mwp_post - mwp_pre:+.3f} s, t-test p={p_ttest:.4f}')

# MWP Granger: SIC -> MWP (if swell attenuation, SIC should Granger-cause MWP)
ok_gc = np.isfinite(std['SIC']) & np.isfinite(std['MWP_edge'])
F_mwp, p_gc_mwp, lag_mwp = granger_test(std['MWP_edge'][ok_gc], std['SIC'][ok_gc])
print(f'  Granger SIC -> MWP: F={F_mwp:.2f}, p={p_gc_mwp:.4f}, lag={lag_mwp}')

# ---- FIGURES ----
print('\n6. Generating figures...')
plt.rcParams.update({'font.size': 11, 'figure.dpi': 150})
fig, axes = plt.subplots(2, 2, figsize=(12, 9))

# A: Seasonal Granger bar chart
ax = axes[0, 0]
snames = list(seasonal_results.keys())
f_vals = [seasonal_results[s]['F'] for s in snames]
p_vals = [seasonal_results[s]['p'] for s in snames]
colors = ['green' if p < 0.05 else 'orange' if p < 0.1 else 'red' for p in p_vals]
ax.bar(snames, f_vals, color=colors, alpha=0.7, edgecolor='k')
for i, (s, r) in enumerate(seasonal_results.items()):
    sig = '*' if r['p'] < 0.05 else 'ns'
    ax.text(i, r['F'] + 0.1, f'p={r["p"]:.3f} {sig}', ha='center', fontsize=9)
ax.set_ylabel('F-statistic')
ax.set_title('(a) SIC → SWH Granger by Season')
ax.grid(True, alpha=0.3)

# B: MWP at ice edge time series
ax = axes[0, 1]
years = times.year.values
mwp_ann = []
yr_list = []
for y in range(1979, 2025):
    mask = years == y
    if mask.sum() >= 6:
        yr_list.append(y)
        mwp_ann.append(np.nanmean(anom['MWP_edge'][mask]))
ax.plot(yr_list, mwp_ann, 'o-', color='purple', lw=1.5, ms=4)
ax.axhline(0, color='gray', lw=0.5)
ax.axvline(2016, color='r', ls='--', lw=1.5, alpha=0.7)
ax.set_ylabel('MWP anomaly (s)')
ax.set_title(f'(b) Mean Wave Period at Ice Edge\npre={mwp_pre:.2f}s, post={mwp_post:.2f}s, p={p_ttest:.3f}')
ax.grid(True, alpha=0.3)

# C: SIC vs MWP scatter
ax = axes[1, 0]
ax.scatter(anom['SIC'][ok_mwp], anom['MWP_edge'][ok_mwp], s=5, alpha=0.3, color='purple')
z = np.polyfit(anom['SIC'][ok_mwp], anom['MWP_edge'][ok_mwp], 1)
x_fit = np.linspace(-0.1, 0.1, 50)
ax.plot(x_fit, np.polyval(z, x_fit), 'r-', lw=2)
ax.set_xlabel('SIC anomaly')
ax.set_ylabel('MWP anomaly (s)')
ax.set_title(f'(c) SIC vs MWP at Ice Edge\nr={r_mwp:.3f}, p={p_mwp:.4f}')
ax.grid(True, alpha=0.3)

# D: MWP seasonal cycle pre/post
ax = axes[1, 1]
mwp_clim_pre = [np.nanmean(mwp_at_edge[pre & (months == m)]) for m in range(1, 13)]
mwp_clim_post = [np.nanmean(mwp_at_edge[post & (months == m)]) for m in range(1, 13)]
ax.plot(range(1, 13), mwp_clim_pre, 'o-', color='steelblue', lw=2, label='Pre-2016')
ax.plot(range(1, 13), mwp_clim_post, 's--', color='coral', lw=2, label='Post-2016')
ax.set_xlabel('Month')
ax.set_ylabel('MWP (s)')
ax.set_xticks(range(1, 13))
ax.set_xticklabels(['J','F','M','A','M','J','J','A','S','O','N','D'])
ax.set_title('(d) MWP Seasonal Cycle at Ice Edge')
ax.legend(); ax.grid(True, alpha=0.3)

plt.suptitle('P04 v2 Revision: Seasonal Granger + MWP Swell Evidence', fontsize=13, y=1.01)
plt.tight_layout()
plt.savefig(f'{FIG}/p04v2_fig_revision_step2.png', bbox_inches='tight')
plt.close()
print(f'  -> {FIG}/p04v2_fig_revision_step2.png')

# Save
output = {
    'seasonal_granger': seasonal_results,
    'mwp_correlation': {'r': round(r_mwp, 4), 'p': round(p_mwp, 6)},
    'mwp_pre_post': {'pre': round(mwp_pre, 3), 'post': round(mwp_post, 3),
                     'diff': round(mwp_post - mwp_pre, 4), 'p_ttest': round(p_ttest, 6)},
    'granger_sic_mwp': {'F': round(F_mwp, 2), 'p': round(p_gc_mwp, 6), 'lag': lag_mwp}
}
with open(f'{OUT}/p04v2_revision_step2.json', 'w') as f:
    json.dump(output, f, indent=2)

print('\nDone.')
