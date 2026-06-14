#!/usr/bin/env python3
"""
P04 v2 Phase 2 (revised): Complete wave-ice feedback diagnostic

With all three ERA5 datasets now available:
  - SIC (0.25°): define MIZ boundary, ice-free area
  - Wind (0.25°): wind speed, fetch proxy
  - SWH (0.5°): wave height response

Core analysis:
  1. MIZ width from SIC (15%-80% band)
  2. Open-water fraction south of 55°S as fetch proxy
  3. Wind speed trends
  4. SWH near MIZ
  5. Correlation matrix + Granger causality: SIC→fetch→SWH feedback
  6. Ice shelf buffer days (SIC-based, 5 major shelves)
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
    p = 2 * np.exp(-6 * K**2 / (n**3 + n**2))
    return cp, K, p

def granger_test(y, x, max_lag=6):
    n = len(y)
    best_aic = np.inf; best_lag = 1; best_f = 0; best_p = 1
    for lag in range(1, max_lag+1):
        T = n - lag
        Y = y[lag:]
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
            F = ((rss_red - rss_full) / dfn) / (rss_full / dfd)
            p = 1 - stats.f.cdf(F, dfn, dfd)
            aic = T * np.log(rss_full/T) + 2 * X_full.shape[1]
            if aic < best_aic:
                best_aic = aic; best_lag = lag; best_f = F; best_p = p
        except:
            pass
    return best_f, best_p, best_lag

print('='*60)
print('PHASE 2 REVISED: COMPLETE FEEDBACK DIAGNOSTIC')
print('='*60)

# ====================================================================
# 1. Load all data
# ====================================================================
print('\n1. Loading data...')

# SIC
ds_sic = xr.open_dataset(f'{DATA}/era5_sic_SO_1979_2024.nc')
if 'expver' in ds_sic.dims:
    ds_sic = ds_sic.sel(expver=1)
sic = ds_sic['siconc'].values if 'siconc' in ds_sic else ds_sic['ci'].values
lat_s = ds_sic.latitude.values
lon_s = ds_sic.longitude.values
times_s = pd.to_datetime(ds_sic.valid_time.values)
ds_sic.close()
sic = np.clip(sic, 0, 1)
print(f'  SIC: {sic.shape}, var name found, lat {lat_s.min():.1f} to {lat_s.max():.1f}')

# Wind
ds_w = xr.open_dataset(f'{DATA}/era5_wind_SO_1979_2024.nc')
if 'expver' in ds_w.dims:
    ds_w = ds_w.sel(expver=1)
u10 = ds_w['u10'].values
v10 = ds_w['v10'].values
wspd = np.sqrt(u10**2 + v10**2)
ds_w.close()
del u10, v10
print(f'  Wind: {wspd.shape}')

# SWH
ds_swh = xr.open_dataset(f'{DATA}/era5_waves_SO_1979_2024.nc')
if 'expver' in ds_swh.dims:
    ds_swh = ds_swh.sel(expver=1)
swh = ds_swh['swh'].values
lat_w = ds_swh.latitude.values
ds_swh.close()
print(f'  SWH: {swh.shape}')

nt = len(times_s)
cos_lat_s = np.cos(np.deg2rad(lat_s))

# ====================================================================
# 2. Compute monthly diagnostics
# ====================================================================
print('\n2. Computing monthly diagnostics...')

# Regions
ice_mask = (lat_s >= -75) & (lat_s <= -55)
miz_mask = (lat_s >= -65) & (lat_s <= -55)
near_miz_w = (lat_w >= -60) & (lat_w <= -50)

def wmean(field, lat_mask, wts):
    w = wts[lat_mask][:, np.newaxis]
    d = field[:, lat_mask, :]
    num = np.nansum(d * w[np.newaxis], axis=(1,2))
    den = np.nansum(np.isfinite(d).astype(float) * w[np.newaxis], axis=(1,2))
    return np.where(den > 0, num/den, np.nan)

# Mean SIC in ice zone
sic_mean = wmean(sic, ice_mask, cos_lat_s)

# Open-water fraction (SIC < 0.15) south of 55S — fetch proxy
ow_frac = np.full(nt, np.nan)
for t in range(nt):
    s = sic[t, ice_mask, :]
    w = cos_lat_s[ice_mask][:, np.newaxis] * np.ones_like(s)
    ok = np.isfinite(s)
    total_w = np.nansum(w * ok)
    if total_w > 0:
        ow_frac[t] = np.nansum(w * (s < 0.15).astype(float)) / total_w

# MIZ width: zonal-mean meridional extent of 0.15 < SIC < 0.80
miz_width = np.full(nt, np.nan)
for t in range(nt):
    widths = []
    for j in range(sic.shape[2]):
        col = sic[t, :, j]
        in_miz = (col > 0.15) & (col < 0.80)
        if in_miz.any():
            idx = np.where(in_miz)[0]
            widths.append(abs(lat_s[idx[-1]] - lat_s[idx[0]]))
    if widths:
        miz_width[t] = np.nanmean(widths)

# Wind speed in ice zone
wspd_ice = wmean(wspd, ice_mask, cos_lat_s)

# SWH near MIZ
swh_miz = wmean(swh, near_miz_w, np.cos(np.deg2rad(lat_w)))

print(f'  SIC mean: {np.nanmean(sic_mean):.3f}')
print(f'  OW fraction: {np.nanmean(ow_frac):.3f}')
print(f'  MIZ width: {np.nanmean(miz_width):.2f}°')
print(f'  Wind speed: {np.nanmean(wspd_ice):.2f} m/s')
print(f'  SWH near MIZ: {np.nanmean(swh_miz):.3f} m')

# ====================================================================
# 3. Deseasonalize + annual means
# ====================================================================
print('\n3. Deseasonalizing...')
months = times_s.month.values
years = times_s.year.values

variables = {
    'SIC': sic_mean, 'OW_frac': ow_frac, 'MIZ_width': miz_width,
    'Wind': wspd_ice, 'SWH': swh_miz
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
# 4. Change point detection
# ====================================================================
print('\n4. Pettitt change point detection...')
cp_results = {}
for name, vals in ann.items():
    ok = np.isfinite(vals)
    if ok.sum() < 15:
        continue
    ci, Ki, pi = pettitt_test(vals[ok])
    cp_yr = yr_arr[ok][ci]
    pre = vals[ok][:ci].mean(); post = vals[ok][ci:].mean()
    sig = '***' if pi < 0.001 else '**' if pi < 0.01 else '*' if pi < 0.05 else 'ns'
    print(f'  {name:12s}: CP={cp_yr}, p={pi:.4f} {sig}, {pre:.4f} → {post:.4f}')
    cp_results[name] = {'year': cp_yr, 'p': pi, 'pre': pre, 'post': post}

# ====================================================================
# 5. Granger causality tests
# ====================================================================
print('\n5. Granger causality (feedback chain)...')
# Standardize monthly anomalies
std = {}
for name, vals in anom.items():
    ok = np.isfinite(vals)
    mu = np.nanmean(vals); sigma = np.nanstd(vals)
    std[name] = (vals - mu) / sigma if sigma > 0 else vals * 0

pairs = [
    ('SIC', 'OW_frac', 'SIC → OW fraction'),
    ('OW_frac', 'SWH', 'OW fraction → SWH'),
    ('SWH', 'MIZ_width', 'SWH → MIZ width'),
    ('MIZ_width', 'SIC', 'MIZ width → SIC (feedback)'),
    ('Wind', 'SWH', 'Wind → SWH'),
    ('SIC', 'SWH', 'SIC → SWH (direct)'),
]

gc_results = []
for x_name, y_name, label in pairs:
    x = std[x_name]; y = std[y_name]
    ok = np.isfinite(x) & np.isfinite(y)
    F, p, lag = granger_test(y[ok], x[ok], max_lag=6)
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
    print(f'  {label:30s}: F={F:.2f}, p={p:.4f} {sig}, lag={lag}mo')
    gc_results.append({'label': label, 'x': x_name, 'y': y_name, 'F': F, 'p': p, 'lag': lag})

# ====================================================================
# 6. Ice shelf buffer analysis
# ====================================================================
print('\n6. Ice shelf buffer analysis...')
shelves = {
    'Ross': {'lat': (-85, -75), 'lon': (155, -150)},
    'Filchner-Ronne': {'lat': (-85, -75), 'lon': (-80, -20)},
    'Amery': {'lat': (-72, -68), 'lon': (68, 75)},
    'Larsen C': {'lat': (-70, -65), 'lon': (-65, -58)},
    'Totten': {'lat': (-68, -65), 'lon': (113, 122)},
}

buffer_results = {}
for shelf_name, bounds in shelves.items():
    lat_m = (lat_s >= bounds['lat'][0]) & (lat_s <= bounds['lat'][1])
    if bounds['lon'][0] < bounds['lon'][1]:
        lon_m = (lon_s >= bounds['lon'][0]) & (lon_s <= bounds['lon'][1])
    else:
        lon_m = (lon_s >= bounds['lon'][0]) | (lon_s <= bounds['lon'][1])

    buffer_days_yr = []
    for y in range(1979, 2025):
        yr_mask = years == y
        if yr_mask.sum() < 6:
            continue
        n_buffered = 0
        for t in np.where(yr_mask)[0]:
            region_sic = sic[t][np.ix_(lat_m, lon_m)]
            mean_sic = np.nanmean(region_sic)
            if mean_sic > 0.15:
                n_buffered += 1
        buffer_days_yr.append(n_buffered)

    buffer_days_yr = np.array(buffer_days_yr)
    if len(buffer_days_yr) >= 15:
        ci, Ki, pi = pettitt_test(buffer_days_yr.astype(float))
        cp_yr_s = yr_arr[ci] if ci < len(yr_arr) else yr_arr[-1]
        sig_s = '***' if pi < 0.001 else '**' if pi < 0.01 else '*' if pi < 0.05 else 'ns'
        pre_b = buffer_days_yr[:ci].mean(); post_b = buffer_days_yr[ci:].mean()
        print(f'  {shelf_name:15s}: CP={cp_yr_s}, p={pi:.4f} {sig_s}, {pre_b:.1f} → {post_b:.1f} mo/yr')
        buffer_results[shelf_name] = {
            'data': buffer_days_yr, 'cp': cp_yr_s, 'p': pi,
            'pre': pre_b, 'post': post_b
        }

# ====================================================================
# 7. Figures
# ====================================================================
print('\n7. Generating figures...')
plt.rcParams.update({'font.size': 10, 'figure.dpi': 150})

fig = plt.figure(figsize=(18, 18))
gs = fig.add_gridspec(4, 3, hspace=0.4, wspace=0.3)

# Row 1: Time series
for i, (name, color) in enumerate([('SIC', 'cyan'), ('OW_frac', 'orange'), ('SWH', 'blue')]):
    ax = fig.add_subplot(gs[0, i])
    ax.plot(yr_arr, ann[name], 'o-', color=color, lw=1.2, ms=3)
    if name in cp_results:
        cp = cp_results[name]
        ax.axvline(cp['year'], color='r', ls='--', lw=1.5, alpha=0.7)
    ax.axhline(0, color='gray', lw=0.5)
    ax.set_title(f'{name} (CP={cp_results.get(name,{}).get("year","?")})'); ax.grid(True, alpha=0.3)

# Row 2: More time series + MIZ
for i, (name, color) in enumerate([('MIZ_width', 'green'), ('Wind', 'purple')]):
    ax = fig.add_subplot(gs[1, i])
    ax.plot(yr_arr, ann[name], 'o-', color=color, lw=1.2, ms=3)
    if name in cp_results:
        ax.axvline(cp_results[name]['year'], color='r', ls='--', lw=1.5, alpha=0.7)
    ax.axhline(0, color='gray', lw=0.5)
    ax.set_title(f'{name} (CP={cp_results.get(name,{}).get("year","?")})'); ax.grid(True, alpha=0.3)

# Row 2, col 3: Granger results
ax = fig.add_subplot(gs[1, 2])
labels_gc = [r['label'].split('→')[0].strip()+'→'+r['label'].split('→')[1].strip()[:8] for r in gc_results]
f_vals = [r['F'] for r in gc_results]
colors_gc = ['green' if r['p'] < 0.05 else 'orange' if r['p'] < 0.1 else 'red' for r in gc_results]
ax.barh(range(len(gc_results)), f_vals, color=colors_gc, alpha=0.7)
for i, r in enumerate(gc_results):
    sig = '***' if r['p']<0.001 else '**' if r['p']<0.01 else '*' if r['p']<0.05 else 'ns'
    ax.text(f_vals[i]+0.1, i, f'p={r["p"]:.3f} {sig}', va='center', fontsize=8)
ax.set_yticks(range(len(gc_results))); ax.set_yticklabels(labels_gc, fontsize=8)
ax.set_xlabel('F-statistic'); ax.set_title('Granger Causality')
ax.grid(True, alpha=0.3)

# Row 3: Ice shelf buffer
ax = fig.add_subplot(gs[2, :])
x_pos = 0
shelf_names = list(buffer_results.keys())
width = 0.35
for i, sn in enumerate(shelf_names):
    br = buffer_results[sn]
    ci_idx = np.argmin(np.abs(yr_arr - br['cp']))
    ax.bar(i-width/2, br['pre'], width, color='steelblue', alpha=0.8,
           label='Pre-CP' if i == 0 else '')
    ax.bar(i+width/2, br['post'], width, color='coral', alpha=0.8,
           label='Post-CP' if i == 0 else '')
    sig = '***' if br['p']<0.001 else '**' if br['p']<0.01 else '*' if br['p']<0.05 else 'ns'
    pct = (br['post']-br['pre'])/br['pre']*100
    ax.text(i, max(br['pre'],br['post'])+0.3, f'CP={br["cp"]}\n{pct:+.0f}% {sig}',
            ha='center', fontsize=8)
ax.set_xticks(range(len(shelf_names))); ax.set_xticklabels(shelf_names)
ax.set_ylabel('Buffer months / year'); ax.set_title('Ice Shelf Buffer: Pre vs Post Change Point')
ax.legend(); ax.grid(True, alpha=0.3)

# Row 4: Correlation matrix
ax = fig.add_subplot(gs[3, 0])
var_names = ['SIC', 'OW_frac', 'Wind', 'SWH', 'MIZ_width']
n_v = len(var_names)
corr_mat = np.full((n_v, n_v), np.nan)
for i, a in enumerate(var_names):
    for j, b in enumerate(var_names):
        ok = np.isfinite(ann[a]) & np.isfinite(ann[b])
        if ok.sum() > 5:
            corr_mat[i, j] = np.corrcoef(ann[a][ok], ann[b][ok])[0, 1]
pcm = ax.imshow(corr_mat, cmap='RdBu_r', vmin=-1, vmax=1)
ax.set_xticks(range(n_v)); ax.set_xticklabels(var_names, fontsize=8, rotation=45)
ax.set_yticks(range(n_v)); ax.set_yticklabels(var_names, fontsize=8)
for i in range(n_v):
    for j in range(n_v):
        if np.isfinite(corr_mat[i,j]):
            ax.text(j, i, f'{corr_mat[i,j]:.2f}', ha='center', va='center', fontsize=8)
plt.colorbar(pcm, ax=ax, shrink=0.8); ax.set_title('Annual Correlation Matrix')

# Row 4: Feedback diagram (text)
ax = fig.add_subplot(gs[3, 1:])
ax.axis('off')
diag_text = 'WAVE-ICE FEEDBACK CHAIN DIAGNOSTIC\n\n'
for r in gc_results:
    sig = '***' if r['p']<0.001 else '**' if r['p']<0.01 else '*' if r['p']<0.05 else 'ns'
    arrow = '→' if r['p'] < 0.05 else '⇢'
    diag_text += f"  {r['x']:12s} {arrow} {r['y']:12s}  F={r['F']:.1f} p={r['p']:.3f} {sig}\n"
diag_text += '\n'
for sn, br in buffer_results.items():
    sig = '***' if br['p']<0.001 else '**' if br['p']<0.01 else '*' if br['p']<0.05 else 'ns'
    pct = (br['post']-br['pre'])/br['pre']*100
    diag_text += f"  {sn:15s} buffer: {br['pre']:.1f}→{br['post']:.1f} mo ({pct:+.0f}%) CP={br['cp']} {sig}\n"

ax.text(0.05, 0.95, diag_text, transform=ax.transAxes, va='top', fontfamily='monospace',
        fontsize=9, bbox=dict(facecolor='#f8f8f8', alpha=0.9))
ax.set_title('Feedback Chain Summary')

plt.suptitle('P04 v2: Wave-Ice Feedback Complete Diagnostic (1979-2024)', fontsize=14, y=1.01)
plt.tight_layout()
plt.savefig(f'{FIG}/p04v2_fig_feedback_diagnostic.png', bbox_inches='tight', dpi=200)
plt.close()
print(f'  -> {FIG}/p04v2_fig_feedback_diagnostic.png')

# Save summary
with open(f'{OUT}/p04v2_feedback_summary.txt', 'w') as f:
    f.write('P04 v2 Feedback Diagnostic Summary\n\n')
    f.write('Change Points:\n')
    for name, cp in cp_results.items():
        sig = '***' if cp['p']<0.001 else '**' if cp['p']<0.01 else '*' if cp['p']<0.05 else 'ns'
        f.write(f'  {name:12s}: CP={cp["year"]}, p={cp["p"]:.6f} {sig}\n')
    f.write('\nGranger Causality:\n')
    for r in gc_results:
        sig = '***' if r['p']<0.001 else '**' if r['p']<0.01 else '*' if r['p']<0.05 else 'ns'
        f.write(f'  {r["label"]:30s}: F={r["F"]:.3f}, p={r["p"]:.6f} {sig}, lag={r["lag"]}\n')
    f.write('\nIce Shelf Buffer:\n')
    for sn, br in buffer_results.items():
        f.write(f'  {sn:15s}: {br["pre"]:.1f} → {br["post"]:.1f} mo/yr, CP={br["cp"]}, p={br["p"]:.6f}\n')

print('\nDone.')
