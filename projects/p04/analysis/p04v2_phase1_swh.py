#!/usr/bin/env python3
"""
P04 v2 Phase 1: ERA5 SWH analysis — wave height trends and 2016 regime shift

Core questions:
  1. Did SWH increase in the Southern Ocean after 2016?
  2. Is the increase concentrated near the MIZ (ice edge)?
  3. Is there a correlation between SWH and sea ice extent?

Uses ERA5 monthly SWH (0.5°, 1979-2024) — note ERA5 wave model only runs
where SIC < 30%, so SWH data is inherently limited to open/marginal waters.
"""

import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
from scipy import stats
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

REPO = str(Path(__file__).resolve().parents[3])
DATA_WAVE = f'{REPO}/projects/p04/data/era5_waves_SO_1979_2024.nc'
DATA_NSIDC = f'{REPO}/data/NSIDC Sea Ice Index'
FIG = f'{REPO}/projects/p04/figures'
OUT = f'{REPO}/projects/p04/analysis'

def pettitt_test(y):
    n = len(y)
    U = np.zeros(n)
    for t in range(1, n):
        s = sum(np.sign(y[i] - y[j]) for i in range(t) for j in range(t, n))
        U[t] = abs(s)
    K = U.max()
    cp = int(U.argmax())
    p = 2 * np.exp(-6 * K**2 / (n**3 + n**2))
    return cp, K, p

# ====================================================================
# 1. Load ERA5 SWH
# ====================================================================
print('='*60)
print('PHASE 1: ERA5 SWH ANALYSIS')
print('='*60)

print('\n1. Loading ERA5 SWH...')
ds = xr.open_dataset(DATA_WAVE)
if 'expver' in ds.dims:
    ds = ds.sel(expver=1)
swh = ds['swh']
mwp = ds['mwp']
lat = ds.latitude.values
lon = ds.longitude.values
times = pd.to_datetime(ds.valid_time.values)
print(f'  SWH: {swh.shape}, {times[0]:%Y-%m} to {times[-1]:%Y-%m}')
print(f'  Lat: {lat.min():.1f} to {lat.max():.1f}, Lon: {lon.min():.1f} to {lon.max():.1f}')

# ====================================================================
# 2. Define regions
# ====================================================================
cos_lat = np.cos(np.deg2rad(lat))

regions = {
    'Full SO (40-75S)': (lat >= -75) & (lat <= -40),
    'Near-MIZ (55-65S)': (lat >= -65) & (lat <= -55),
    'ACC belt (45-55S)': (lat >= -55) & (lat <= -45),
    'Deep ice edge (65-75S)': (lat >= -75) & (lat <= -65),
}

def area_mean(da, lat_mask):
    w = cos_lat[lat_mask]
    d = da[:, lat_mask, :]
    return np.nansum(d * w[np.newaxis, :, np.newaxis], axis=(1,2)) / np.nansum(
        np.isfinite(d) * w[np.newaxis, :, np.newaxis], axis=(1,2))

# ====================================================================
# 3. Regional SWH time series
# ====================================================================
print('\n2. Computing regional SWH time series...')
ts = {}
for name, mask in regions.items():
    ts[name] = area_mean(swh.values, mask)
    ok = np.isfinite(ts[name])
    print(f'  {name}: mean={np.nanmean(ts[name]):.3f} m, valid={ok.sum()}/{len(ok)}')

# ====================================================================
# 4. Deseasonalize
# ====================================================================
print('\n3. Deseasonalizing...')
months = times.month.values
ts_anom = {}
for name, vals in ts.items():
    clim = np.array([np.nanmean(vals[months == m]) for m in range(1, 13)])
    ts_anom[name] = vals - clim[months - 1]

# ====================================================================
# 5. Annual means + Pettitt
# ====================================================================
print('\n4. Annual means + change point detection...')
years = times.year.values
ann = {}
for name, vals in ts_anom.items():
    yr_vals = []
    yr_list = []
    for y in range(1979, 2025):
        mask = years == y
        if mask.sum() >= 6:
            yr_vals.append(np.nanmean(vals[mask]))
            yr_list.append(y)
    ann[name] = (np.array(yr_list), np.array(yr_vals))

print('\n  Pettitt change point detection (SWH anomaly):')
cp_results = {}
for name, (yrs, vals) in ann.items():
    ok = np.isfinite(vals)
    if ok.sum() < 15:
        continue
    ci, Ki, pi = pettitt_test(vals[ok])
    cp_yr = yrs[ok][ci]
    pre = vals[ok][:ci].mean()
    post = vals[ok][ci:].mean()
    sig = '***' if pi < 0.001 else '**' if pi < 0.01 else '*' if pi < 0.05 else 'ns'
    print(f'    {name}: CP={cp_yr}, p={pi:.4f} {sig}, {pre:.4f} → {post:.4f} m')
    cp_results[name] = {'year': cp_yr, 'p': pi, 'pre': pre, 'post': post}

# ====================================================================
# 6. Spatial trend map (pre vs post 2016)
# ====================================================================
print('\n5. Computing spatial SWH changes...')
pre_mask = times < '2016-01-01'
post_mask = times >= '2016-01-01'
swh_pre = np.nanmean(swh.values[pre_mask], axis=0)
swh_post = np.nanmean(swh.values[post_mask], axis=0)
swh_diff = swh_post - swh_pre
swh_pct = swh_diff / swh_pre * 100

mwp_pre = np.nanmean(mwp.values[pre_mask], axis=0)
mwp_post = np.nanmean(mwp.values[post_mask], axis=0)
mwp_diff = mwp_post - mwp_pre

# Significance test (t-test each grid point)
from scipy.stats import ttest_ind
n_lat, n_lon = swh_pre.shape
pval_map = np.full((n_lat, n_lon), np.nan)
for i in range(n_lat):
    for j in range(n_lon):
        a = swh.values[pre_mask, i, j]
        b = swh.values[post_mask, i, j]
        ok_a = np.isfinite(a)
        ok_b = np.isfinite(b)
        if ok_a.sum() > 20 and ok_b.sum() > 10:
            _, pval_map[i, j] = ttest_ind(a[ok_a], b[ok_b])

sig_mask = pval_map < 0.05
print(f'  Significant (p<0.05) grid points: {np.nansum(sig_mask)}/{np.nansum(np.isfinite(pval_map))} ({np.nansum(sig_mask)/max(1,np.nansum(np.isfinite(pval_map)))*100:.1f}%)')

# ====================================================================
# 7. Correlation with NSIDC extent
# ====================================================================
print('\n6. SWH vs sea ice extent correlation...')
all_ext = []
for m in range(1, 13):
    fp = f'{DATA_NSIDC}/S_{m:02d}_extent_v4.0.csv'
    d = pd.read_csv(fp, skiprows=1, names=['year','mo','source','region','extent','area'])
    d['year'] = d['year'].astype(int)
    d['extent'] = pd.to_numeric(d['extent'], errors='coerce')
    for _, row in d.iterrows():
        if np.isfinite(row['extent']) and row['extent'] > 0:
            all_ext.append({'year': row['year'], 'month': m, 'extent': row['extent']})
ext_df = pd.DataFrame(all_ext)
ext_df['time'] = pd.to_datetime(ext_df.apply(lambda r: f"{int(r['year'])}-{int(r['month']):02d}-01", axis=1))
ext_ts = ext_df.set_index('time')['extent'].sort_index()
ext_clim = ext_ts.groupby(ext_ts.index.month).mean()
ext_anom = ext_ts - ext_clim.loc[ext_ts.index.month].values

common_times = sorted(set(times) & set(ext_anom.index))
if len(common_times) > 100:
    swh_common = np.array([ts_anom['Near-MIZ (55-65S)'][np.argmin(np.abs(times - t))] for t in common_times])
    ext_common = ext_anom.loc[common_times].values
    ok = np.isfinite(swh_common) & np.isfinite(ext_common)
    r, p = stats.pearsonr(swh_common[ok], ext_common[ok])
    print(f'  Near-MIZ SWH vs extent anomaly: r={r:.3f}, p={p:.4f}, n={ok.sum()}')
else:
    print(f'  Insufficient overlap: {len(common_times)} months')

# ====================================================================
# 8. Figures
# ====================================================================
print('\n7. Generating figures...')
plt.rcParams.update({'font.size': 11, 'figure.dpi': 150})

fig = plt.figure(figsize=(18, 14))
gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

# Panel A: SWH spatial change
ax = fig.add_subplot(gs[0, :])
lon2d, lat2d = np.meshgrid(lon, lat)
pcm = ax.pcolormesh(lon2d, lat2d, swh_pct, cmap='RdBu_r', vmin=-15, vmax=15, shading='auto')
ax.contour(lon2d, lat2d, sig_mask.astype(float), levels=[0.5], colors='k', linewidths=0.5, linestyles='-')
plt.colorbar(pcm, ax=ax, label='SWH change (%)', shrink=0.7)
ax.set_xlim(-180, 180); ax.set_ylim(-75, -40)
ax.set_ylabel('Latitude'); ax.set_xlabel('Longitude')
ax.set_title('(a) SWH Change: Post-2016 minus Pre-2016 (%, black contour = p<0.05)')

# Panel B: Regional SWH time series
ax = fig.add_subplot(gs[1, 0])
colors = {'Full SO (40-75S)': 'k', 'Near-MIZ (55-65S)': 'blue',
          'ACC belt (45-55S)': 'red', 'Deep ice edge (65-75S)': 'green'}
for name, (yrs, vals) in ann.items():
    ax.plot(yrs, vals, 'o-', color=colors.get(name, 'gray'), lw=1.2, ms=3, label=name, alpha=0.8)
ax.axvline(2016, color='k', ls='--', lw=1, alpha=0.5)
ax.axhline(0, color='gray', lw=0.5)
ax.set_ylabel('SWH anomaly (m)')
ax.set_title('(b) Regional SWH Annual Anomaly')
ax.legend(fontsize=7)
ax.grid(True, alpha=0.3)

# Panel C: SWH Pettitt
ax = fig.add_subplot(gs[1, 1])
name = 'Near-MIZ (55-65S)'
yrs, vals = ann[name]
ax.plot(yrs, vals, 'o-', color='blue', lw=1.5, ms=4)
if name in cp_results:
    cp = cp_results[name]
    ax.axvline(cp['year'], color='r', ls='--', lw=1.5)
    ax.axhline(cp['pre'], color='blue', ls=':', lw=1, alpha=0.5)
    ax.axhline(cp['post'], color='red', ls=':', lw=1, alpha=0.5)
    ax.text(0.02, 0.95, f'CP={cp["year"]}, p={cp["p"]:.4f}', transform=ax.transAxes,
            fontsize=9, va='top', bbox=dict(facecolor='white', alpha=0.8))
ax.set_ylabel('SWH anomaly (m)')
ax.set_title(f'(c) {name} — Pettitt CP')
ax.grid(True, alpha=0.3)

# Panel D: SWH vs extent scatter
ax = fig.add_subplot(gs[2, 0])
if len(common_times) > 100:
    ax.scatter(ext_common[ok], swh_common[ok], s=5, alpha=0.3, color='steelblue')
    z = np.polyfit(ext_common[ok], swh_common[ok], 1)
    x_fit = np.linspace(ext_common[ok].min(), ext_common[ok].max(), 50)
    ax.plot(x_fit, np.polyval(z, x_fit), 'r-', lw=2, label=f'r={r:.3f}, p={p:.1e}')
    ax.set_xlabel('Sea ice extent anomaly (Mkm²)')
    ax.set_ylabel('SWH anomaly (m)')
    ax.legend()
ax.set_title('(d) Near-MIZ SWH vs Extent Anomaly')
ax.grid(True, alpha=0.3)

# Panel E: Spatial MWP change
ax = fig.add_subplot(gs[2, 1])
pcm = ax.pcolormesh(lon2d, lat2d, mwp_diff, cmap='RdBu_r', vmin=-0.5, vmax=0.5, shading='auto')
plt.colorbar(pcm, ax=ax, label='MWP change (s)', shrink=0.7)
ax.set_xlim(-180, 180); ax.set_ylim(-75, -40)
ax.set_ylabel('Latitude'); ax.set_xlabel('Longitude')
ax.set_title('(e) Mean Wave Period Change: Post-2016 minus Pre-2016 (s)')

plt.suptitle('P04 v2 Phase 1: ERA5 Wave Height Analysis (1979-2024)', fontsize=14, y=1.01)
plt.tight_layout()
plt.savefig(f'{FIG}/p04v2_fig_phase1_swh.png', bbox_inches='tight')
plt.close()
print(f'  -> {FIG}/p04v2_fig_phase1_swh.png')

# Save summary
with open(f'{OUT}/p04v2_phase1_summary.txt', 'w') as f:
    f.write('P04 v2 Phase 1: ERA5 SWH Analysis Summary\n\n')
    for name, cp in cp_results.items():
        f.write(f'{name}: CP={cp["year"]}, p={cp["p"]:.6f}, '
                f'pre={cp["pre"]:.4f} → post={cp["post"]:.4f} m\n')
    f.write(f'\nNear-MIZ SWH vs extent: r={r:.3f}, p={p:.4f}\n')
    f.write(f'Significant grid points (p<0.05): {np.nansum(sig_mask)}/{np.nansum(np.isfinite(pval_map))}\n')

ds.close()
print('\nDone.')
