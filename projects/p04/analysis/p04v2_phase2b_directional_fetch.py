#!/usr/bin/env python3
"""
P04 v2 Phase 2b: Directional fetch + ice-edge-relative SWH

Fixes R03 Block 1+2:
  Block 1: OW fraction ≠ fetch → compute TRUE directional fetch
  Block 2: fixed lat band → use ice-edge-relative SWH sampling

Method:
  For each month, at each 0.25° grid point on the SIC=15% contour (ice edge):
    1. Get local wind direction from ERA5 (u10, v10)
    2. Trace UPWIND from the ice edge into open water
    3. Count distance until SIC > 15% or 2000 km reached
    4. This distance = directional fetch at the ice edge

  SWH sampling: for each point on the ice edge, sample SWH at the nearest
  equatorward grid point (not a fixed lat band)

Also fixes Pettitt p > 1 bug (cap at 1.0).
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
            if dfd <= 0 or rss_full <= 0:
                continue
            F = ((rss_red - rss_full) / dfn) / (rss_full / dfd)
            p = 1 - stats.f.cdf(F, dfn, dfd)
            aic = T * np.log(rss_full/T) + 2 * X_full.shape[1]
            if aic < best_aic:
                best_aic = aic; best_lag = lag; best_f = F; best_p = p
        except np.linalg.LinAlgError:
            continue
    return best_f, best_p, best_lag

print('='*60)
print('PHASE 2b: DIRECTIONAL FETCH + ICE-EDGE SWH')
print('='*60)

# Load data
print('\n1. Loading data...')
ds_sic = xr.open_dataset(f'{DATA}/era5_sic_SO_1979_2024.nc')
if 'expver' in ds_sic.dims:
    ds_sic = ds_sic.sel(expver=1)
sic_var = 'siconc' if 'siconc' in ds_sic else 'ci'
sic = np.clip(ds_sic[sic_var].values, 0, 1)
lat_s = ds_sic.latitude.values
lon_s = ds_sic.longitude.values
times = pd.to_datetime(ds_sic.valid_time.values)
ds_sic.close()

ds_w = xr.open_dataset(f'{DATA}/era5_wind_SO_1979_2024.nc')
if 'expver' in ds_w.dims:
    ds_w = ds_w.sel(expver=1)
u10 = ds_w['u10'].values
v10 = ds_w['v10'].values
ds_w.close()

ds_swh = xr.open_dataset(f'{DATA}/era5_waves_SO_1979_2024.nc')
if 'expver' in ds_swh.dims:
    ds_swh = ds_swh.sel(expver=1)
swh = ds_swh['swh'].values
lat_w = ds_swh.latitude.values
lon_w = ds_swh.longitude.values
ds_swh.close()

nt = len(times)
R_EARTH = 6371e3
dlat = abs(lat_s[1] - lat_s[0])
dlon = abs(lon_s[1] - lon_s[0])
print(f'  SIC: {sic.shape}, Wind: {u10.shape}, SWH: {swh.shape}')

# Precompute SWH interpolation: nearest lat_w for each lat_s
swh_lat_idx = np.array([np.argmin(np.abs(lat_w - ls)) for ls in lat_s])

# ====================================================================
# 2. Compute directional fetch at ice edge
# ====================================================================
print('\n2. Computing directional fetch at ice edge...')

fetch_monthly = np.full(nt, np.nan)
swh_at_edge = np.full(nt, np.nan)
ice_edge_lat = np.full(nt, np.nan)

for t in range(nt):
    if t % 60 == 0:
        print(f'  month {t}/{nt}')

    sic_t = sic[t]
    u_t = u10[t]
    v_t = v10[t]
    swh_t = swh[t]

    fetch_list = []
    swh_list = []
    edge_lats = []

    for j in range(0, len(lon_s), 4):
        col = sic_t[:, j]
        above = col > 0.15
        below = col <= 0.15

        for i in range(1, len(lat_s)):
            if i >= len(lat_s) - 1:
                continue
            if above[i] and below[i-1]:
                edge_i = i
                edge_lat_val = lat_s[edge_i]

                if edge_lat_val > -50 or edge_lat_val < -74:
                    continue

                wind_u = u_t[edge_i, j]
                wind_v = v_t[edge_i, j]
                wspd = np.sqrt(wind_u**2 + wind_v**2)
                if wspd < 0.5:
                    continue

                upwind_di = -wind_v / wspd
                upwind_dj = -wind_u / wspd

                dist = 0
                ci, cj = float(edge_i), float(j)
                step_km = dlat * R_EARTH / 1000 * 0.5
                max_dist = 2000

                while dist < max_dist:
                    ci += upwind_di * 0.5
                    cj += upwind_dj * 0.5
                    ii = int(round(ci))
                    jj = int(round(cj)) % len(lon_s)

                    if ii < 0 or ii >= len(lat_s):
                        break
                    if sic_t[ii, jj] > 0.15:
                        break
                    dist += step_km

                if dist > 10:
                    fetch_list.append(dist)
                    edge_lats.append(edge_lat_val)

                    equatorward_i = max(0, edge_i - 2)
                    swh_li = swh_lat_idx[equatorward_i]
                    swh_ji = np.argmin(np.abs(lon_w - lon_s[j]))
                    sv = swh_t[swh_li, swh_ji]
                    if np.isfinite(sv):
                        swh_list.append(sv)

    if fetch_list:
        fetch_monthly[t] = np.mean(fetch_list)
        ice_edge_lat[t] = np.mean(edge_lats)
    if swh_list:
        swh_at_edge[t] = np.mean(swh_list)

del sic, u10, v10, swh

# ====================================================================
# 3. Also compute SIC mean and wind speed for context
# ====================================================================
print('\n3. Computing context variables...')
ds_sic2 = xr.open_dataset(f'{DATA}/era5_sic_SO_1979_2024.nc')
if 'expver' in ds_sic2.dims:
    ds_sic2 = ds_sic2.sel(expver=1)
sic2 = np.clip(ds_sic2[sic_var].values, 0, 1)
ds_sic2.close()

ds_w2 = xr.open_dataset(f'{DATA}/era5_wind_SO_1979_2024.nc')
if 'expver' in ds_w2.dims:
    ds_w2 = ds_w2.sel(expver=1)
wspd_all = np.sqrt(ds_w2['u10'].values**2 + ds_w2['v10'].values**2)
ds_w2.close()

cos_lat = np.cos(np.deg2rad(lat_s))
ice_mask = (lat_s >= -75) & (lat_s <= -55)

sic_mean = np.full(nt, np.nan)
wspd_mean = np.full(nt, np.nan)
for t in range(nt):
    w = cos_lat[ice_mask][:, np.newaxis]
    s = sic2[t, ice_mask, :]
    ok = np.isfinite(s)
    sic_mean[t] = np.nansum(s * w) / np.nansum(w * ok) if np.nansum(w * ok) > 0 else np.nan
    ws = wspd_all[t, ice_mask, :]
    ok_w = np.isfinite(ws)
    wspd_mean[t] = np.nansum(ws * w) / np.nansum(w * ok_w) if np.nansum(w * ok_w) > 0 else np.nan

del sic2, wspd_all

# ====================================================================
# 4. Deseasonalize
# ====================================================================
print('\n4. Deseasonalizing...')
months = times.month.values
years = times.year.values

variables = {
    'Fetch': fetch_monthly,
    'SWH_edge': swh_at_edge,
    'SIC': sic_mean,
    'Wind': wspd_mean,
    'IceEdgeLat': ice_edge_lat,
}

anom = {}
for name, vals in variables.items():
    clim = np.array([np.nanmean(vals[months == m]) for m in range(1, 13)])
    anom[name] = vals - clim[months - 1]

# Annual means
ann = {}
yr_list = []
for y in range(1979, 2025):
    mask = years == y
    if mask.sum() >= 6:
        yr_list.append(y)
        for name in variables:
            if name not in ann:
                ann[name] = []
            ann[name].append(np.nanmean(anom[name][mask]))
yr_arr = np.array(yr_list)
for name in ann:
    ann[name] = np.array(ann[name])

# ====================================================================
# 5. Change point detection
# ====================================================================
print('\n5. Change point detection...')
cp_results = {}
for name, vals in ann.items():
    ok = np.isfinite(vals)
    if ok.sum() < 15:
        print(f'  {name}: insufficient data')
        continue
    ci, Ki, pi = pettitt_test(vals[ok])
    cp_yr = yr_arr[ok][ci]
    pre = vals[ok][:ci].mean()
    post = vals[ok][ci:].mean()
    sig = '***' if pi < 0.001 else '**' if pi < 0.01 else '*' if pi < 0.05 else 'ns'
    print(f'  {name:12s}: CP={cp_yr}, p={pi:.4f} {sig}, {pre:.4f} → {post:.4f}')
    cp_results[name] = {'year': cp_yr, 'p': pi, 'pre': pre, 'post': post}

# ====================================================================
# 6. Granger causality with CORRECT variables
# ====================================================================
print('\n6. Granger causality (directional fetch)...')
std = {}
for name, vals in anom.items():
    mu = np.nanmean(vals); sigma = np.nanstd(vals)
    std[name] = (vals - mu) / sigma if sigma > 0 else vals * 0

pairs = [
    ('SIC', 'Fetch', 'SIC → Fetch'),
    ('Fetch', 'SWH_edge', 'Fetch → SWH at edge'),
    ('SWH_edge', 'IceEdgeLat', 'SWH → Ice edge retreat'),
    ('IceEdgeLat', 'SIC', 'Ice edge → SIC (feedback)'),
    ('Wind', 'SWH_edge', 'Wind → SWH at edge'),
    ('Wind', 'Fetch', 'Wind → Fetch'),
]

gc_results = []
for x_name, y_name, label in pairs:
    x = std[x_name]; y = std[y_name]
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 50:
        print(f'  {label:30s}: insufficient data ({ok.sum()} pts)')
        continue
    F, p, lag = granger_test(y[ok], x[ok], max_lag=6)
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
    print(f'  {label:30s}: F={F:.2f}, p={p:.4f} {sig}, lag={lag}mo')
    gc_results.append({'label': label, 'x': x_name, 'y': y_name, 'F': F, 'p': p, 'lag': lag})

# ====================================================================
# 7. Figures
# ====================================================================
print('\n7. Generating figures...')
plt.rcParams.update({'font.size': 11, 'figure.dpi': 150})

fig, axes = plt.subplots(3, 2, figsize=(14, 12))

# A: Directional fetch time series
ax = axes[0, 0]
ax.plot(yr_arr, ann['Fetch'], 'o-', color='darkorange', lw=1.5, ms=4)
if 'Fetch' in cp_results:
    ax.axvline(cp_results['Fetch']['year'], color='r', ls='--', lw=1.5)
ax.axhline(0, color='gray', lw=0.5)
ax.set_ylabel('Fetch anomaly (km)')
cp_f = cp_results.get('Fetch', {})
ax.set_title(f'(a) Directional Fetch at Ice Edge\nCP={cp_f.get("year","?")}, p={cp_f.get("p",1):.4f}')
ax.grid(True, alpha=0.3)

# B: SWH at ice edge
ax = axes[0, 1]
ax.plot(yr_arr, ann['SWH_edge'], 'o-', color='steelblue', lw=1.5, ms=4)
if 'SWH_edge' in cp_results:
    ax.axvline(cp_results['SWH_edge']['year'], color='r', ls='--', lw=1.5)
ax.axhline(0, color='gray', lw=0.5)
ax.set_ylabel('SWH anomaly (m)')
cp_s = cp_results.get('SWH_edge', {})
ax.set_title(f'(b) SWH at Ice Edge\nCP={cp_s.get("year","?")}, p={cp_s.get("p",1):.4f}')
ax.grid(True, alpha=0.3)

# C: Fetch vs SWH scatter
ax = axes[1, 0]
ok = np.isfinite(ann['Fetch']) & np.isfinite(ann['SWH_edge'])
if ok.sum() > 5:
    ax.scatter(ann['Fetch'][ok], ann['SWH_edge'][ok], c=yr_arr[ok], cmap='RdYlBu_r',
              s=40, edgecolors='k', lw=0.5)
    r, p = stats.pearsonr(ann['Fetch'][ok], ann['SWH_edge'][ok])
    z = np.polyfit(ann['Fetch'][ok], ann['SWH_edge'][ok], 1)
    x_fit = np.linspace(ann['Fetch'][ok].min(), ann['Fetch'][ok].max(), 50)
    ax.plot(x_fit, np.polyval(z, x_fit), 'r-', lw=2)
    ax.set_title(f'(c) Fetch vs SWH at Edge\nr={r:.3f}, p={p:.4f}')
else:
    ax.set_title('(c) Fetch vs SWH (insufficient data)')
ax.set_xlabel('Fetch anomaly (km)'); ax.set_ylabel('SWH anomaly (m)')
ax.grid(True, alpha=0.3)

# D: Ice edge latitude
ax = axes[1, 1]
ax.plot(yr_arr, ann['IceEdgeLat'], 'o-', color='green', lw=1.5, ms=4)
if 'IceEdgeLat' in cp_results:
    ax.axvline(cp_results['IceEdgeLat']['year'], color='r', ls='--', lw=1.5)
ax.axhline(0, color='gray', lw=0.5)
ax.set_ylabel('Ice edge lat anomaly (°)')
cp_ie = cp_results.get('IceEdgeLat', {})
ax.set_title(f'(d) Ice Edge Latitude\nCP={cp_ie.get("year","?")}, p={cp_ie.get("p",1):.4f}')
ax.grid(True, alpha=0.3)

# E: Granger results
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
ax.set_xlabel('F-statistic'); ax.set_title('(e) Granger Causality (Directional Fetch)')
ax.grid(True, alpha=0.3)

# F: Fetch climatology
ax = axes[2, 1]
fetch_clim = np.array([np.nanmean(fetch_monthly[months == m]) for m in range(1, 13)])
swh_clim = np.array([np.nanmean(swh_at_edge[months == m]) for m in range(1, 13)])
ax.plot(range(1, 13), fetch_clim, 'o-', color='darkorange', lw=2, label='Fetch (km)')
ax2 = ax.twinx()
ax2.plot(range(1, 13), swh_clim, 's-', color='steelblue', lw=2, label='SWH (m)')
ax2.set_ylabel('SWH (m)', color='steelblue')
ax.set_xlabel('Month'); ax.set_ylabel('Fetch (km)', color='darkorange')
ax.set_xticks(range(1, 13)); ax.set_xticklabels(['J','F','M','A','M','J','J','A','S','O','N','D'])
ax.set_title('(f) Seasonal Cycle: Fetch & SWH at Ice Edge')
ax.grid(True, alpha=0.3)

plt.suptitle('P04 v2 Phase 2b: Directional Fetch + Ice-Edge SWH (1979-2024)', fontsize=14, y=1.01)
plt.tight_layout()
plt.savefig(f'{FIG}/p04v2_fig_directional_fetch.png', bbox_inches='tight')
plt.close()
print(f'  -> {FIG}/p04v2_fig_directional_fetch.png')

# Save
with open(f'{OUT}/p04v2_phase2b_summary.txt', 'w') as f:
    f.write('P04 v2 Phase 2b: Directional Fetch Summary\n\n')
    f.write(f'Mean fetch: {np.nanmean(fetch_monthly):.0f} km\n')
    f.write(f'Mean SWH at edge: {np.nanmean(swh_at_edge):.3f} m\n\n')
    f.write('Change Points:\n')
    for name, cp in cp_results.items():
        sig = '***' if cp['p']<0.001 else '**' if cp['p']<0.01 else '*' if cp['p']<0.05 else 'ns'
        f.write(f'  {name:12s}: CP={cp["year"]}, p={cp["p"]:.6f} {sig}\n')
    f.write('\nGranger Causality (directional fetch):\n')
    for r in gc_results:
        sig = '***' if r['p']<0.001 else '**' if r['p']<0.01 else '*' if r['p']<0.05 else 'ns'
        f.write(f'  {r["label"]:30s}: F={r["F"]:.3f}, p={r["p"]:.6f} {sig}, lag={r["lag"]}\n')

print('\nDone.')
