#!/usr/bin/env python3
"""
P04 v2 Phase 2c: Simplified fetch + ice-edge-relative SWH

Fetch proxy: zonal-mean ice edge latitude (SIC=15% contour)
  - More poleward edge = longer fetch (more open water for westerlies)
  - This captures the dominant zonal wind fetch geometry of the Southern Ocean

SWH: sampled at the ice edge (not fixed lat band)

Fixes:
  - R03 Block 1: uses ice edge position (not OW fraction) as fetch proxy
  - R03 Block 2: SWH sampled relative to ice edge (not fixed lat band)
  - R03 Block 3: Pettitt p capped at 1.0
"""

import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
from scipy import stats
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

REPO = str(Path(__file__).resolve().parents[3])
P04 = f'{REPO}/projects/p04'
DATA = f'{P04}/data'
FIG = f'{P04}/figures'
OUT = f'{P04}/analysis'

def pettitt_test(y):
    n = len(y)
    U = np.zeros(n)
    for t in range(1, n):
        s = sum(np.sign(y[i] - y[j]) for i in range(t) for j in range(t, n))
        U[t] = abs(s)
    K = U.max(); cp = int(U.argmax())
    p = min(2 * np.exp(-6 * K**2 / (n**3 + n**2)), 1.0)
    return cp, K, p

def granger_test(y, x, max_lag=6):
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
print('PHASE 2c: ICE-EDGE FETCH + SWH (FIXED)')
print('='*60)

# Load
print('\n1. Loading data...')
ds_sic = xr.open_dataset(f'{DATA}/era5_sic_SO_1979_2024.nc')
if 'expver' in ds_sic.dims: ds_sic = ds_sic.sel(expver=1)
sic_var = 'siconc' if 'siconc' in ds_sic else 'ci'
sic = np.clip(ds_sic[sic_var].values, 0, 1)
lat_s = ds_sic.latitude.values; lon_s = ds_sic.longitude.values
times = pd.to_datetime(ds_sic.valid_time.values)
ds_sic.close()

ds_w = xr.open_dataset(f'{DATA}/era5_wind_SO_1979_2024.nc')
if 'expver' in ds_w.dims: ds_w = ds_w.sel(expver=1)
wspd = np.sqrt(ds_w['u10'].values**2 + ds_w['v10'].values**2)
ds_w.close()

ds_swh = xr.open_dataset(f'{DATA}/era5_waves_SO_1979_2024.nc')
if 'expver' in ds_swh.dims: ds_swh = ds_swh.sel(expver=1)
swh = ds_swh['swh'].values; lat_w = ds_swh.latitude.values; lon_w = ds_swh.longitude.values
ds_swh.close()

nt = len(times)
cos_lat = np.cos(np.deg2rad(lat_s))
R_EARTH = 6371.0
swh_lat_idx = np.array([np.argmin(np.abs(lat_w - ls)) for ls in lat_s])

# ====================================================================
# 2. Compute ice edge lat + SWH at edge + fetch proxy
# ====================================================================
print('\n2. Computing ice edge + edge SWH + fetch...')

ice_edge_lat = np.full(nt, np.nan)
swh_at_edge = np.full(nt, np.nan)
fetch_proxy = np.full(nt, np.nan)
sic_mean_ice = np.full(nt, np.nan)
wspd_mean = np.full(nt, np.nan)

ice_mask = (lat_s >= -75) & (lat_s <= -55)

for t in range(nt):
    sic_t = sic[t]
    swh_t = swh[t]
    ws_t = wspd[t]

    # Ice edge: for each longitude, find first lat where SIC > 0.15 (searching poleward)
    edge_lats = []
    edge_swh_vals = []

    for j in range(0, len(lon_s), 2):
        col = sic_t[:, j]
        for i in range(len(lat_s)):
            if col[i] > 0.15:
                edge_lat_val = lat_s[i]
                if -74 < edge_lat_val < -50:
                    edge_lats.append(edge_lat_val)

                    # SWH at 2° equatorward of ice edge
                    eq_i = max(0, i - 8)
                    swh_li = swh_lat_idx[eq_i]
                    swh_ji = np.argmin(np.abs(lon_w - lon_s[j]))
                    sv = swh_t[swh_li, swh_ji]
                    if np.isfinite(sv):
                        edge_swh_vals.append(sv)
                break

    if edge_lats:
        mean_edge = np.mean(edge_lats)
        ice_edge_lat[t] = mean_edge
        # Fetch proxy: distance from -40° (northern domain boundary) to ice edge
        # This is the zonal fetch available for westerlies
        fetch_proxy[t] = abs(mean_edge - (-40.0)) * np.pi / 180 * R_EARTH

    if edge_swh_vals:
        swh_at_edge[t] = np.mean(edge_swh_vals)

    # Context: SIC mean, wind speed mean
    w = cos_lat[ice_mask][:, np.newaxis]
    s = sic_t[ice_mask, :]
    ok_s = np.isfinite(s)
    sic_mean_ice[t] = np.nansum(s * w) / np.nansum(w * ok_s) if np.nansum(w * ok_s) > 0 else np.nan

    ws = ws_t[ice_mask, :]
    ok_w = np.isfinite(ws)
    wspd_mean[t] = np.nansum(ws * w) / np.nansum(w * ok_w) if np.nansum(w * ok_w) > 0 else np.nan

print(f'  Ice edge lat: mean={np.nanmean(ice_edge_lat):.2f}°, valid={np.isfinite(ice_edge_lat).sum()}/{nt}')
print(f'  Fetch proxy: mean={np.nanmean(fetch_proxy):.0f} km')
print(f'  SWH at edge: mean={np.nanmean(swh_at_edge):.3f} m, valid={np.isfinite(swh_at_edge).sum()}/{nt}')

# ====================================================================
# 3. Deseasonalize + annual means
# ====================================================================
print('\n3. Deseasonalizing...')
months = times.month.values; years = times.year.values

variables = {
    'IceEdge': ice_edge_lat, 'Fetch': fetch_proxy, 'SWH_edge': swh_at_edge,
    'SIC': sic_mean_ice, 'Wind': wspd_mean,
}
anom = {}
for name, vals in variables.items():
    clim = np.array([np.nanmean(vals[months == m]) for m in range(1, 13)])
    anom[name] = vals - clim[months - 1]

ann = {}; yr_list = []
for y in range(1979, 2025):
    mask = years == y
    if mask.sum() >= 6:
        yr_list.append(y)
        for name in variables:
            if name not in ann: ann[name] = []
            ann[name].append(np.nanmean(anom[name][mask]))
yr_arr = np.array(yr_list)
for name in ann: ann[name] = np.array(ann[name])

# ====================================================================
# 4. Pettitt + Granger
# ====================================================================
print('\n4. Change point detection...')
cp_results = {}
for name, vals in ann.items():
    ok = np.isfinite(vals)
    if ok.sum() < 15: continue
    ci, Ki, pi = pettitt_test(vals[ok])
    cp_yr = yr_arr[ok][ci]
    pre = vals[ok][:ci].mean(); post = vals[ok][ci:].mean()
    sig = '***' if pi < 0.001 else '**' if pi < 0.01 else '*' if pi < 0.05 else 'ns'
    print(f'  {name:12s}: CP={cp_yr}, p={pi:.4f} {sig}, {pre:.4f} → {post:.4f}')
    cp_results[name] = {'year': cp_yr, 'p': pi, 'pre': pre, 'post': post}

print('\n5. Granger causality...')
std = {}
for name, vals in anom.items():
    sigma = np.nanstd(vals)
    std[name] = (vals - np.nanmean(vals)) / sigma if sigma > 0 else vals * 0

pairs = [
    ('SIC', 'Fetch', 'SIC → Fetch'),
    ('Fetch', 'SWH_edge', 'Fetch → SWH at edge'),
    ('SWH_edge', 'IceEdge', 'SWH → Ice edge'),
    ('IceEdge', 'SIC', 'Ice edge → SIC (feedback)'),
    ('Wind', 'SWH_edge', 'Wind → SWH at edge'),
    ('SIC', 'SWH_edge', 'SIC → SWH (direct)'),
]

gc_results = []
for x_name, y_name, label in pairs:
    x = std[x_name]; y = std[y_name]
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 50:
        print(f'  {label:30s}: insufficient data ({ok.sum()})')
        continue
    F, p, lag = granger_test(y[ok], x[ok], max_lag=6)
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
    print(f'  {label:30s}: F={F:.2f}, p={p:.4f} {sig}, lag={lag}')
    gc_results.append({'label': label, 'x': x_name, 'y': y_name, 'F': F, 'p': p, 'lag': lag})

# ====================================================================
# 6. Figures
# ====================================================================
print('\n6. Generating figures...')
plt.rcParams.update({'font.size': 11, 'figure.dpi': 150})

fig, axes = plt.subplots(3, 2, figsize=(14, 12))

# A: Fetch proxy
ax = axes[0, 0]
ax.plot(yr_arr, ann['Fetch'], 'o-', color='darkorange', lw=1.5, ms=4)
cp = cp_results.get('Fetch', {})
if cp: ax.axvline(cp['year'], color='r', ls='--', lw=1.5)
ax.axhline(0, color='gray', lw=0.5); ax.set_ylabel('Fetch anomaly (km)')
ax.set_title(f'(a) Zonal Fetch Proxy\nCP={cp.get("year","?")}, p={cp.get("p",1):.4f}')
ax.grid(True, alpha=0.3)

# B: SWH at ice edge
ax = axes[0, 1]
ax.plot(yr_arr, ann['SWH_edge'], 'o-', color='steelblue', lw=1.5, ms=4)
cp = cp_results.get('SWH_edge', {})
if cp: ax.axvline(cp['year'], color='r', ls='--', lw=1.5)
ax.axhline(0, color='gray', lw=0.5); ax.set_ylabel('SWH anomaly (m)')
ax.set_title(f'(b) SWH at Ice Edge\nCP={cp.get("year","?")}, p={cp.get("p",1):.4f}')
ax.grid(True, alpha=0.3)

# C: Fetch vs SWH
ax = axes[1, 0]
ok = np.isfinite(ann['Fetch']) & np.isfinite(ann['SWH_edge'])
if ok.sum() > 5:
    r, p = stats.pearsonr(ann['Fetch'][ok], ann['SWH_edge'][ok])
    ax.scatter(ann['Fetch'][ok], ann['SWH_edge'][ok], c=yr_arr[ok], cmap='RdYlBu_r', s=40, edgecolors='k', lw=0.5)
    z = np.polyfit(ann['Fetch'][ok], ann['SWH_edge'][ok], 1)
    x_fit = np.linspace(ann['Fetch'][ok].min(), ann['Fetch'][ok].max(), 50)
    ax.plot(x_fit, np.polyval(z, x_fit), 'r-', lw=2)
    ax.set_title(f'(c) Fetch vs SWH at Edge\nr={r:.3f}, p={p:.4f}')
ax.set_xlabel('Fetch anomaly (km)'); ax.set_ylabel('SWH anomaly (m)'); ax.grid(True, alpha=0.3)

# D: Ice edge lat
ax = axes[1, 1]
ax.plot(yr_arr, ann['IceEdge'], 'o-', color='green', lw=1.5, ms=4)
cp = cp_results.get('IceEdge', {})
if cp: ax.axvline(cp['year'], color='r', ls='--', lw=1.5)
ax.axhline(0, color='gray', lw=0.5); ax.set_ylabel('Ice edge lat anomaly (°)')
ax.set_title(f'(d) Ice Edge Latitude\nCP={cp.get("year","?")}, p={cp.get("p",1):.4f}')
ax.grid(True, alpha=0.3)

# E: Granger
ax = axes[2, 0]
if gc_results:
    labels_gc = [r['label'] for r in gc_results]
    f_vals = [r['F'] for r in gc_results]
    colors_gc = ['green' if r['p'] < 0.05 else 'orange' if r['p'] < 0.1 else 'red' for r in gc_results]
    ax.barh(range(len(gc_results)), f_vals, color=colors_gc, alpha=0.7)
    for i, r in enumerate(gc_results):
        sig = '***' if r['p']<0.001 else '**' if r['p']<0.01 else '*' if r['p']<0.05 else 'ns'
        ax.text(f_vals[i]+0.1, i, f'p={r["p"]:.3f} {sig}', va='center', fontsize=8)
    ax.set_yticks(range(len(gc_results))); ax.set_yticklabels(labels_gc, fontsize=8)
ax.set_xlabel('F-statistic'); ax.set_title('(e) Granger Causality (Fixed Fetch)')
ax.grid(True, alpha=0.3)

# F: Seasonal cycle
ax = axes[2, 1]
edge_clim = np.array([np.nanmean(ice_edge_lat[months == m]) for m in range(1, 13)])
swh_clim = np.array([np.nanmean(swh_at_edge[months == m]) for m in range(1, 13)])
ax.plot(range(1, 13), edge_clim, 'o-', color='green', lw=2, label='Ice edge (°lat)')
ax2 = ax.twinx()
ax2.plot(range(1, 13), swh_clim, 's-', color='steelblue', lw=2, label='SWH (m)')
ax2.set_ylabel('SWH (m)', color='steelblue')
ax.set_xlabel('Month'); ax.set_ylabel('Ice edge (°lat)', color='green')
ax.set_xticks(range(1, 13)); ax.set_xticklabels(['J','F','M','A','M','J','J','A','S','O','N','D'])
ax.set_title('(f) Seasonal Cycle: Ice Edge & SWH')
ax.grid(True, alpha=0.3)

plt.suptitle('P04 v2 Phase 2c: Ice-Edge Fetch + SWH (R03 fixes)', fontsize=14, y=1.01)
plt.tight_layout()
plt.savefig(f'{FIG}/p04v2_fig_fetch_fixed.png', bbox_inches='tight')
plt.close()
print(f'  -> {FIG}/p04v2_fig_fetch_fixed.png')

# Save
with open(f'{OUT}/p04v2_phase2c_summary.txt', 'w') as f:
    f.write('P04 v2 Phase 2c: Ice-Edge Fetch Summary (R03 fixes)\n\n')
    f.write('Change Points:\n')
    for name, cp in cp_results.items():
        sig = '***' if cp['p']<0.001 else '**' if cp['p']<0.01 else '*' if cp['p']<0.05 else 'ns'
        f.write(f'  {name:12s}: CP={cp["year"]}, p={cp["p"]:.6f} {sig}\n')
    f.write('\nGranger Causality:\n')
    for r in gc_results:
        sig = '***' if r['p']<0.001 else '**' if r['p']<0.01 else '*' if r['p']<0.05 else 'ns'
        f.write(f'  {r["label"]:30s}: F={r["F"]:.3f}, p={r["p"]:.6f} {sig}, lag={r["lag"]}\n')

print('\nDone.')
