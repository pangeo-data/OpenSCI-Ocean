#!/usr/bin/env python3
"""
P04 v2 Revision Step 4: ERA5 SIC masking sensitivity test

Reviewer 1 concern: ERA5 WAM sets SWH=NaN where SIC>30%.
When SIC drops from 35%→25%, a grid point gains SWH data,
mechanically increasing area-averaged SWH near the ice edge.

Test: compare SWH trends at:
  (a) "always ice-free" grid points (SIC always < 15% in all months)
  (b) "transitional" grid points (SIC crosses 30% threshold over time)
  (c) "always masked" grid points (SIC always > 30%)

If the SIC→SWH link is an artifact, the trend at transitional
points should be much larger than at always-ice-free points.
"""

import numpy as np
import xarray as xr
import pandas as pd
from pathlib import Path
from scipy import stats
import json

REPO = str(Path(__file__).resolve().parents[3])
P04 = f'{REPO}/projects/p04'
DATA = f'{P04}/data'
OUT = f'{P04}/analysis'

print('='*60)
print('REVISION STEP 4: ERA5 MASKING SENSITIVITY')
print('='*60)

print('\n1. Loading SIC and SWH...')
ds_sic = xr.open_dataset(f'{DATA}/era5_sic_SO_1979_2024.nc')
if 'expver' in ds_sic.dims: ds_sic = ds_sic.sel(expver=1)
sic_var = 'siconc' if 'siconc' in ds_sic else 'ci'
sic = np.clip(ds_sic[sic_var].values, 0, 1)
lat_s = ds_sic.latitude.values
times = pd.to_datetime(ds_sic.valid_time.values)
ds_sic.close()

ds_swh = xr.open_dataset(f'{DATA}/era5_waves_SO_1979_2024.nc')
if 'expver' in ds_swh.dims: ds_swh = ds_swh.sel(expver=1)
swh = ds_swh['swh'].values
lat_w = ds_swh.latitude.values
lon_w = ds_swh.longitude.values
ds_swh.close()

# Work on SWH grid (coarser, 0.5°)
nt, nlat_w, nlon_w = swh.shape

# Interpolate SIC to SWH grid (nearest neighbor)
print('2. Interpolating SIC to SWH grid...')
sic_on_swh = np.full((nt, nlat_w, nlon_w), np.nan)
lat_idx = np.array([np.argmin(np.abs(lat_s - lw)) for lw in lat_w])
lon_idx = np.array([np.argmin(np.abs(ds_sic.longitude.values - lw))
                     for lw in lon_w]) if hasattr(ds_sic, 'longitude') else np.arange(nlon_w)

# Reload lon_s
ds_sic2 = xr.open_dataset(f'{DATA}/era5_sic_SO_1979_2024.nc')
if 'expver' in ds_sic2.dims: ds_sic2 = ds_sic2.sel(expver=1)
lon_s = ds_sic2.longitude.values
ds_sic2.close()

lon_idx = np.array([np.argmin(np.abs(lon_s - lw)) for lw in lon_w])

for t in range(nt):
    sic_on_swh[t] = sic[t][np.ix_(lat_idx, lon_idx)]

del sic

# Classify grid points
print('3. Classifying grid points...')
# For each grid point, compute the fraction of months with SIC > 30%
frac_above30 = np.nanmean(sic_on_swh > 0.30, axis=0)
frac_above15 = np.nanmean(sic_on_swh > 0.15, axis=0)

# Always ice-free: SIC < 15% in >95% of months
always_free = frac_above15 < 0.05
# Transitional: SIC crosses 30% in 10-90% of months
transitional = (frac_above30 > 0.10) & (frac_above30 < 0.90)
# Always masked: SIC > 30% in >90% of months (mostly NaN in SWH)
always_masked = frac_above30 > 0.90

# Restrict to Southern Ocean latitudes relevant to MIZ
lat_mask = (lat_w >= -70) & (lat_w <= -50)
always_free_so = always_free & lat_mask[:, np.newaxis]
transitional_so = transitional & lat_mask[:, np.newaxis]

n_free = np.sum(always_free_so)
n_trans = np.sum(transitional_so)
print(f'  Always ice-free (50-70S): {n_free} grid points')
print(f'  Transitional (50-70S): {n_trans} grid points')

# Compute area-weighted SWH time series for each category
print('4. Computing SWH time series by category...')
cos_w = np.cos(np.deg2rad(lat_w))

def weighted_ts(data, mask):
    w = cos_w[:, np.newaxis] * mask
    d = data.copy()
    d[:, ~mask] = np.nan
    num = np.nansum(d * w[np.newaxis], axis=(1,2))
    den = np.nansum(np.isfinite(d) * w[np.newaxis], axis=(1,2))
    return np.where(den > 0, num/den, np.nan)

swh_free = weighted_ts(swh, always_free_so)
swh_trans = weighted_ts(swh, transitional_so)

# Deseasonalize
months = times.month.values
years = times.year.values

def deseason(vals):
    clim = np.array([np.nanmean(vals[months == m]) for m in range(1, 13)])
    return vals - clim[months - 1]

swh_free_anom = deseason(swh_free)
swh_trans_anom = deseason(swh_trans)

# Annual means
def annual(vals):
    yrs = []; avs = []
    for y in range(1979, 2025):
        m = years == y
        if m.sum() >= 6 and np.isfinite(vals[m]).sum() > 3:
            yrs.append(y); avs.append(np.nanmean(vals[m]))
    return np.array(yrs), np.array(avs)

yr_f, ann_f = annual(swh_free_anom)
yr_t, ann_t = annual(swh_trans_anom)

# Trends
print('\n5. Trend comparison...')
for label, yrs, vals in [('Always ice-free', yr_f, ann_f), ('Transitional', yr_t, ann_t)]:
    ok = np.isfinite(vals)
    if ok.sum() < 10:
        print(f'  {label}: insufficient data')
        continue
    slope, _, r, p, se = stats.linregress(yrs[ok].astype(float), vals[ok])
    print(f'  {label}: slope={slope*10:.4f} m/decade, R²={r**2:.3f}, p={p:.4f}')

# Pre/post 2016 comparison
print('\n6. Pre/post 2016 comparison...')
for label, yrs, vals in [('Always ice-free', yr_f, ann_f), ('Transitional', yr_t, ann_t)]:
    pre = vals[yrs < 2016]; post = vals[yrs >= 2016]
    ok_pre = np.isfinite(pre); ok_post = np.isfinite(post)
    if ok_pre.sum() < 5 or ok_post.sum() < 3:
        print(f'  {label}: insufficient data for comparison')
        continue
    _, p_tt = stats.ttest_ind(pre[ok_pre], post[ok_post])
    diff = np.nanmean(post) - np.nanmean(pre)
    print(f'  {label}: pre={np.nanmean(pre):.4f}, post={np.nanmean(post):.4f}, '
          f'diff={diff:+.4f} m, t-test p={p_tt:.4f}')

# Granger: SIC→SWH separately for each category
print('\n7. Granger SIC→SWH by grid category...')
# Use total SIC mean for both
ds_sic3 = xr.open_dataset(f'{DATA}/era5_sic_SO_1979_2024.nc')
if 'expver' in ds_sic3.dims: ds_sic3 = ds_sic3.sel(expver=1)
sic3 = np.clip(ds_sic3[sic_var].values, 0, 1)
ds_sic3.close()

ice_mask = (lat_s >= -75) & (lat_s <= -55)
cos_s = np.cos(np.deg2rad(lat_s))
sic_mean = np.full(nt, np.nan)
for t in range(nt):
    w = cos_s[ice_mask][:, np.newaxis]
    s = sic3[t, ice_mask, :]
    ok = np.isfinite(s)
    sic_mean[t] = np.nansum(s*w)/np.nansum(w*ok) if np.nansum(w*ok)>0 else np.nan
del sic3

sic_anom = deseason(sic_mean)

def granger_test(y, x, max_lag=6):
    n = len(y)
    best_aic = np.inf; best_f = 0; best_p = 1; best_lag = 1
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
            b_r = np.linalg.lstsq(X_full[:, :x_col], Y, rcond=None)[0]
            rss_red = np.sum((Y - X_full[:, :x_col] @ b_r)**2)
            dfn = lag; dfd = T - X_full.shape[1]
            if dfd <= 0 or rss_full <= 0: continue
            F = ((rss_red - rss_full) / dfn) / (rss_full / dfd)
            p = 1 - stats.f.cdf(F, dfn, dfd)
            aic = T * np.log(rss_full/T) + 2 * X_full.shape[1]
            if aic < best_aic:
                best_aic = aic; best_f = F; best_p = p; best_lag = lag
        except np.linalg.LinAlgError:
            continue
    return best_f, best_p, best_lag

# Standardize
def standardize(v):
    s = np.nanstd(v)
    return (v - np.nanmean(v)) / s if s > 0 else v * 0

sic_std = standardize(sic_anom)
swh_free_std = standardize(swh_free_anom)
swh_trans_std = standardize(swh_trans_anom)

for label, swh_s in [('Always ice-free', swh_free_std), ('Transitional', swh_trans_std)]:
    ok = np.isfinite(sic_std) & np.isfinite(swh_s)
    if ok.sum() < 50:
        print(f'  SIC→SWH ({label}): insufficient data')
        continue
    F, p, lag = granger_test(swh_s[ok], sic_std[ok])
    sig = '*' if p < 0.05 else 'ns'
    print(f'  SIC→SWH ({label}): F={F:.2f}, p={p:.4f} {sig}, lag={lag}')

# Save
results = {
    'n_always_free': int(n_free),
    'n_transitional': int(n_trans),
}
with open(f'{OUT}/p04v2_revision_step4.json', 'w') as f:
    json.dump(results, f, indent=2)

print('\nDone.')
