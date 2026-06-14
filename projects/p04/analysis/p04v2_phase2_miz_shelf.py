#!/usr/bin/env python3
"""
P04 v2 Phase 2+3: MIZ width proxy + Ice shelf buffer analysis

Phase 2: Use ERA5 SWH data coverage boundary as MIZ outer edge proxy
  - ERA5 wave model runs only where SIC < 30%
  - The poleward limit of valid SWH data ≈ MIZ outer boundary
  - Track this boundary over time → MIZ retreat/advance

Phase 3: Ice shelf buffer days
  - For 5 major ice shelves, count months/year with SIC > 15% in front
  - Use NSIDC extent as proxy (shelf-specific analysis needs SIC grid data)

Uses: ERA5 SWH (already local) + NSIDC CSVs
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
    K = U.max(); cp = int(U.argmax())
    p = 2 * np.exp(-6 * K**2 / (n**3 + n**2))
    return cp, K, p

print('='*60)
print('PHASE 2+3: MIZ WIDTH + ICE SHELF BUFFER')
print('='*60)

# ====================================================================
# 1. MIZ proxy from SWH data coverage
# ====================================================================
print('\n1. Loading ERA5 SWH for MIZ proxy...')
ds = xr.open_dataset(DATA_WAVE)
if 'expver' in ds.dims:
    ds = ds.sel(expver=1)
swh = ds['swh'].values
lat = ds.latitude.values
lon = ds.longitude.values
times = pd.to_datetime(ds.valid_time.values)
ds.close()

nt, nlat, nlon = swh.shape
print(f'  SWH: {swh.shape}, {times[0]:%Y-%m} to {times[-1]:%Y-%m}')

# For each month and each longitude, find the most poleward latitude
# with valid (non-NaN) SWH data — this is the MIZ outer boundary
print('\n2. Computing MIZ boundary (poleward limit of valid SWH)...')
miz_boundary_lat = np.full((nt, nlon), np.nan)
for t in range(nt):
    for j in range(nlon):
        col = swh[t, :, j]
        valid = np.where(np.isfinite(col))[0]
        if len(valid) > 0:
            miz_boundary_lat[t, j] = lat[valid[0]]

# Zonal mean of MIZ boundary latitude
miz_zonal_mean = np.nanmean(miz_boundary_lat, axis=1)
print(f'  Mean MIZ boundary: {np.nanmean(miz_zonal_mean):.2f}°S')

# Deseasonalize
months = times.month.values
clim_miz = np.array([np.nanmean(miz_zonal_mean[months == m]) for m in range(1, 13)])
miz_anom = miz_zonal_mean - clim_miz[months - 1]

# Annual means
years = times.year.values
miz_ann_yrs = []
miz_ann_vals = []
for y in range(1979, 2025):
    mask = years == y
    if mask.sum() >= 6:
        miz_ann_yrs.append(y)
        miz_ann_vals.append(np.nanmean(miz_anom[mask]))
miz_ann_yrs = np.array(miz_ann_yrs)
miz_ann_vals = np.array(miz_ann_vals)

# Pettitt on MIZ boundary
print('\n3. Change point detection on MIZ boundary...')
ci, Ki, pi = pettitt_test(miz_ann_vals)
cp_yr = miz_ann_yrs[ci]
pre_m = miz_ann_vals[:ci].mean()
post_m = miz_ann_vals[ci:].mean()
sig = '***' if pi < 0.001 else '**' if pi < 0.01 else '*' if pi < 0.05 else 'ns'
print(f'  MIZ boundary: CP={cp_yr}, p={pi:.4f} {sig}')
print(f'  Pre: {pre_m:.3f}° → Post: {post_m:.3f}°')
print(f'  Direction: {"poleward retreat" if post_m < pre_m else "equatorward advance"}')

# Trend
slope, _, r, pv, _ = stats.linregress(miz_ann_yrs.astype(float), miz_ann_vals)
print(f'  Linear trend: {slope:.4f}°/yr, R²={r**2:.3f}, p={pv:.4f}')

# ====================================================================
# 4. SWH at MIZ boundary (wave exposure at ice edge)
# ====================================================================
print('\n4. SWH at MIZ boundary...')
swh_at_miz = np.full(nt, np.nan)
for t in range(nt):
    vals = []
    for j in range(nlon):
        col = swh[t, :, j]
        valid = np.where(np.isfinite(col))[0]
        if len(valid) > 0:
            vals.append(col[valid[0]])
    if vals:
        swh_at_miz[t] = np.nanmean(vals)

clim_swh_miz = np.array([np.nanmean(swh_at_miz[months == m]) for m in range(1, 13)])
swh_miz_anom = swh_at_miz - clim_swh_miz[months - 1]

swh_miz_ann = []
for y in range(1979, 2025):
    mask = years == y
    if mask.sum() >= 6:
        swh_miz_ann.append(np.nanmean(swh_miz_anom[mask]))
swh_miz_ann = np.array(swh_miz_ann)

# Correlation: MIZ boundary vs SWH at MIZ
ok = np.isfinite(miz_ann_vals) & np.isfinite(swh_miz_ann)
r_miz_swh, p_miz_swh = stats.pearsonr(miz_ann_vals[ok], swh_miz_ann[ok])
print(f'  MIZ boundary vs SWH at MIZ: r={r_miz_swh:.3f}, p={p_miz_swh:.4f}')

# ====================================================================
# 5. NSIDC seasonal ice coverage as shelf buffer proxy
# ====================================================================
print('\n5. Ice shelf buffer proxy (NSIDC seasonal coverage)...')
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

# "Buffer months" = months per year where extent > threshold (high ice = buffered)
threshold = 12.0  # Mkm², roughly the annual mean
buffer_months = []
buffer_yrs = []
for y in range(1979, 2025):
    yr_data = ext_df[ext_df['year'] == y]['extent']
    if len(yr_data) >= 10:
        n_buffer = (yr_data > threshold).sum()
        buffer_months.append(n_buffer)
        buffer_yrs.append(y)
buffer_months = np.array(buffer_months)
buffer_yrs = np.array(buffer_yrs)

# Pettitt on buffer months
ci_b, Ki_b, pi_b = pettitt_test(buffer_months.astype(float))
cp_yr_b = buffer_yrs[ci_b]
sig_b = '***' if pi_b < 0.001 else '**' if pi_b < 0.01 else '*' if pi_b < 0.05 else 'ns'
print(f'  Buffer months (extent>{threshold} Mkm²):')
print(f'    CP={cp_yr_b}, p={pi_b:.4f} {sig_b}')
print(f'    Pre: {buffer_months[:ci_b].mean():.1f} mo/yr → Post: {buffer_months[ci_b:].mean():.1f} mo/yr')

# ====================================================================
# 6. Figures
# ====================================================================
print('\n6. Generating figures...')
plt.rcParams.update({'font.size': 11, 'figure.dpi': 150})

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# A: MIZ boundary time series
ax = axes[0, 0]
ax.plot(miz_ann_yrs, miz_ann_vals, 'o-', color='steelblue', lw=1.5, ms=4)
ax.axvline(cp_yr, color='r', ls='--', lw=1.5, alpha=0.7)
ax.axhline(0, color='gray', lw=0.5)
ax.set_ylabel('MIZ boundary anomaly (°lat)')
ax.set_title(f'(a) MIZ Poleward Limit (SWH data edge)\nCP={cp_yr}, p={pi:.4f} {sig}')
ax.grid(True, alpha=0.3)

# B: SWH at MIZ vs MIZ boundary scatter
ax = axes[0, 1]
ax.scatter(swh_miz_ann[ok], miz_ann_vals[ok], s=30, c=miz_ann_yrs[ok], cmap='RdYlBu_r', edgecolors='k', lw=0.5)
z = np.polyfit(swh_miz_ann[ok], miz_ann_vals[ok], 1)
x_fit = np.linspace(swh_miz_ann[ok].min(), swh_miz_ann[ok].max(), 50)
ax.plot(x_fit, np.polyval(z, x_fit), 'r-', lw=2)
ax.set_xlabel('SWH at MIZ anomaly (m)')
ax.set_ylabel('MIZ boundary anomaly (°lat)')
ax.set_title(f'(b) SWH at Ice Edge vs MIZ Position\nr={r_miz_swh:.3f}, p={p_miz_swh:.4f}')
ax.grid(True, alpha=0.3)

# C: Buffer months
ax = axes[1, 0]
colors_b = ['steelblue' if y < cp_yr_b else 'coral' for y in buffer_yrs]
ax.bar(buffer_yrs, buffer_months, color=colors_b, alpha=0.7)
ax.axvline(cp_yr_b, color='k', ls='--', lw=1.5, alpha=0.7)
ax.axhline(buffer_months[:ci_b].mean(), color='steelblue', ls=':', lw=1)
ax.axhline(buffer_months[ci_b:].mean(), color='coral', ls=':', lw=1)
ax.set_ylabel('Months with extent > 12 Mkm²')
ax.set_title(f'(c) Ice Buffer Months per Year\nCP={cp_yr_b}, p={pi_b:.4f} {sig_b}')
ax.grid(True, alpha=0.3)

# D: MIZ boundary zonal-mean seasonal cycle (pre vs post 2016)
ax = axes[1, 1]
pre = times < '2016-01-01'
post = times >= '2016-01-01'
for label, mask, color, ls in [('Pre-2016', pre, 'steelblue', '-'), ('Post-2016', post, 'coral', '--')]:
    seasonal = [np.nanmean(miz_zonal_mean[mask & (months == m)]) for m in range(1, 13)]
    ax.plot(range(1, 13), seasonal, f'{ls}', color=color, lw=2, marker='o', ms=5, label=label)
ax.set_xlabel('Month')
ax.set_ylabel('MIZ boundary latitude (°)')
ax.set_title('(d) MIZ Boundary Seasonal Cycle')
ax.legend()
ax.set_xticks(range(1, 13))
ax.set_xticklabels(['J','F','M','A','M','J','J','A','S','O','N','D'])
ax.grid(True, alpha=0.3)

plt.suptitle('P04 v2 Phase 2+3: MIZ Width + Ice Shelf Buffer (1979-2024)', fontsize=14, y=1.01)
plt.tight_layout()
plt.savefig(f'{FIG}/p04v2_fig_phase2_miz_shelf.png', bbox_inches='tight')
plt.close()
print(f'  -> {FIG}/p04v2_fig_phase2_miz_shelf.png')

# Save results
with open(f'{OUT}/p04v2_phase2_summary.txt', 'w') as f:
    f.write('P04 v2 Phase 2+3 Summary\n\n')
    f.write(f'MIZ boundary: CP={cp_yr}, p={pi:.6f}, trend={slope:.4f}°/yr\n')
    f.write(f'MIZ boundary vs SWH at MIZ: r={r_miz_swh:.3f}, p={p_miz_swh:.4f}\n')
    f.write(f'Buffer months: CP={cp_yr_b}, p={pi_b:.6f}\n')
    f.write(f'  Pre: {buffer_months[:ci_b].mean():.1f} mo/yr, Post: {buffer_months[ci_b:].mean():.1f} mo/yr\n')

print('\nDone.')
