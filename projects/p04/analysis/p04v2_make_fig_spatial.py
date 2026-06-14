#!/usr/bin/env python3
"""
P04 v2: Spatial maps — SIC change + SWH change + ice edge shift
Uses cartopy for proper Antarctic projection with real coastlines.
"""

import numpy as np
import xarray as xr
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path

REPO = str(Path(__file__).resolve().parents[3])
P04 = f'{REPO}/projects/p04'
DATA = f'{P04}/data'
FIG = f'{P04}/manuscript_v2/figures'

print('Loading data...')
ds_sic = xr.open_dataset(f'{DATA}/era5_sic_SO_1979_2024.nc')
if 'expver' in ds_sic.dims: ds_sic = ds_sic.sel(expver=1)
sic_var = 'siconc' if 'siconc' in ds_sic else 'ci'
sic = np.clip(ds_sic[sic_var].values, 0, 1)
lat_s = ds_sic.latitude.values; lon_s = ds_sic.longitude.values
import pandas as pd
times = pd.to_datetime(ds_sic.valid_time.values)
ds_sic.close()

ds_swh = xr.open_dataset(f'{DATA}/era5_waves_SO_1979_2024.nc')
if 'expver' in ds_swh.dims: ds_swh = ds_swh.sel(expver=1)
swh = ds_swh['swh'].values
lat_w = ds_swh.latitude.values; lon_w = ds_swh.longitude.values
ds_swh.close()

pre = times < '2016-01-01'; post = times >= '2016-01-01'

sic_pre = np.nanmean(sic[pre], axis=0)
sic_post = np.nanmean(sic[post], axis=0)
sic_diff = sic_post - sic_pre

swh_pre = np.nanmean(swh[pre], axis=0)
swh_post = np.nanmean(swh[post], axis=0)
swh_diff = swh_post - swh_pre

# Ice edge contour (SIC = 0.15)
lon2d_s, lat2d_s = np.meshgrid(lon_s, lat_s)
lon2d_w, lat2d_w = np.meshgrid(lon_w, lat_w)

print('Generating figure...')
proj = ccrs.SouthPolarStereo()
data_crs = ccrs.PlateCarree()

fig, axes = plt.subplots(1, 3, figsize=(18, 7),
                          subplot_kw={'projection': proj})

# Panel A: SIC difference
ax = axes[0]
ax.set_extent([-180, 180, -75, -40], crs=data_crs)
ax.add_feature(cfeature.LAND, facecolor='#D2B48C', zorder=2)
ax.add_feature(cfeature.COASTLINE, linewidth=0.5, zorder=3)
pcm = ax.pcolormesh(lon2d_s, lat2d_s, sic_diff, transform=data_crs,
                     cmap='RdBu_r', vmin=-0.15, vmax=0.15, zorder=1)
ax.contour(lon2d_s, lat2d_s, sic_pre, levels=[0.15], colors='blue',
           linewidths=1.5, linestyles='--', transform=data_crs, zorder=4)
ax.contour(lon2d_s, lat2d_s, sic_post, levels=[0.15], colors='red',
           linewidths=1.5, linestyles='-', transform=data_crs, zorder=4)
cb = plt.colorbar(pcm, ax=ax, shrink=0.7, pad=0.05)
cb.set_label('SIC change')
ax.set_title('(a) Sea ice concentration change\n(post-2016 minus pre-2016)', fontsize=11)
ax.text(0.02, 0.02, 'Blue dashed: pre-2016 edge\nRed solid: post-2016 edge',
        transform=ax.transAxes, fontsize=7, va='bottom',
        bbox=dict(facecolor='white', alpha=0.8))

# Panel B: SWH difference
ax = axes[1]
ax.set_extent([-180, 180, -75, -40], crs=data_crs)
ax.add_feature(cfeature.LAND, facecolor='#D2B48C', zorder=2)
ax.add_feature(cfeature.COASTLINE, linewidth=0.5, zorder=3)
pcm = ax.pcolormesh(lon2d_w, lat2d_w, swh_diff, transform=data_crs,
                     cmap='RdBu_r', vmin=-0.3, vmax=0.3, zorder=1)
ax.contour(lon2d_s, lat2d_s, sic_pre, levels=[0.15], colors='gray',
           linewidths=1, linestyles='--', transform=data_crs, zorder=4)
cb = plt.colorbar(pcm, ax=ax, shrink=0.7, pad=0.05)
cb.set_label('SWH change (m)')
ax.set_title('(b) Significant wave height change\n(post-2016 minus pre-2016)', fontsize=11)

# Panel C: SIC climatology pre vs post with ice shelf locations
ax = axes[2]
ax.set_extent([-180, 180, -75, -40], crs=data_crs)
ax.add_feature(cfeature.LAND, facecolor='#D2B48C', zorder=2)
ax.add_feature(cfeature.COASTLINE, linewidth=0.5, zorder=3)
pcm = ax.pcolormesh(lon2d_s, lat2d_s, sic_pre, transform=data_crs,
                     cmap='Blues', vmin=0, vmax=1, zorder=1, alpha=0.6)
ax.contour(lon2d_s, lat2d_s, sic_pre, levels=[0.15], colors='blue',
           linewidths=2, linestyles='--', transform=data_crs, zorder=4)
ax.contour(lon2d_s, lat2d_s, sic_post, levels=[0.15], colors='red',
           linewidths=2, linestyles='-', transform=data_crs, zorder=4)
cb = plt.colorbar(pcm, ax=ax, shrink=0.7, pad=0.05)
cb.set_label('SIC (pre-2016 mean)')

shelves = [('Ross', 175, -78), ('F-R', -45, -78), ('Amery', 72, -70),
           ('Larsen C', -62, -68), ('Totten', 117, -67)]
for name, lo, la in shelves:
    ax.plot(lo, la, 'r^', ms=10, transform=data_crs, zorder=5)
    ax.text(lo+5, la+1, name, transform=data_crs, fontsize=7,
            fontweight='bold', color='red', zorder=6)

ax.set_title('(c) Ice edge retreat + ice shelf locations', fontsize=11)
ax.text(0.02, 0.02, 'Blue dashed: pre-2016 edge\nRed solid: post-2016 edge\nTriangles: ice shelves',
        transform=ax.transAxes, fontsize=7, va='bottom',
        bbox=dict(facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig(f'{FIG}/fig2_spatial.png', bbox_inches='tight', dpi=300)
plt.close()
print(f'-> {FIG}/fig2_spatial.png')
