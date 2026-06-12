#!/usr/bin/env python3
"""
P04 tau_eff Spatial Analysis -- Core Physical Mechanism

tau_eff = tau x (1 - alpha x SIC)    where alpha = 0.8

All computations on ERA5 native 0.25-degree grid (no interpolation).

Author: anonymous  Date: 2026-06-12
"""

import numpy as np
import xarray as xr
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import gridspec
import os, warnings
warnings.filterwarnings('ignore')

REPO = 'E:/OpenSCI-Ocean'
DATA = f'{REPO}/data'
OUT  = f'{REPO}/projects/p04/analysis'
FIG  = f'{REPO}/projects/p04/figures'
os.makedirs(OUT, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

RHO_AIR, CD, ALPHA = 1.225, 1.3e-3, 0.8

# ---- 1. LOAD ERA5 DATA (native 0.25-deg grid) ----
print('='*60)
print('TAU_EFF SPATIAL ANALYSIS')
print('='*60)
print('\n1. Loading ERA5 data (0.25-deg grid)...')

with xr.open_dataset(f'{DATA}/ERA5/era5_wind.nc', decode_times=False, engine='h5netcdf') as ds:
    ds = ds.sortby('latitude')
    dates_all = pd.to_datetime(ds.valid_time.values, unit='s')
    msk = (dates_all >= '1993-01-01') & (dates_all <= '2024-12-31')
    u10 = ds.u10.values[msk].astype(np.float32)
    v10 = ds.v10.values[msk].astype(np.float32)
    lat = ds.latitude.values.astype(np.float64)
    lon = ds.longitude.values.astype(np.float64)
    dates = dates_all[msk]

spd = np.sqrt(u10**2 + v10**2)
tau_x = RHO_AIR * CD * spd * u10
tau_y = RHO_AIR * CD * spd * v10
tau_mag = np.sqrt(tau_x**2 + tau_y**2)
del u10, v10, spd
print(f'  Wind stress: {tau_x.shape}, {tau_x.nbytes/1e9:.2f} GB')

with xr.open_dataset(f'{DATA}/data_stream-moda_stepType-avgua.nc',
                     decode_times=False, engine='h5netcdf') as ds:
    ds = ds.sortby('latitude')
    sic = ds.siconc.values[msk].astype(np.float32)
    sic = np.clip(sic, 0, 1)
print(f'  SIC: {sic.shape}')

tau_eff_mag = tau_mag * (1 - ALPHA * sic)
n_time, n_lat, n_lon = tau_mag.shape
print(f'  Time: {n_time} months ({dates[0]:%Y-%m} to {dates[-1]:%Y-%m})')

# ---- 2. REGIONS ----
print('\n2. Defining regions...')
cos_lat = np.cos(np.deg2rad(lat)).astype(np.float32)
sic_clim = sic.mean(axis=0)

ice_mask = sic_clim > 0.15
ice_marg = (sic_clim > 0.05) & (sic_clim <= 0.15)
open_mask = sic_clim <= 0.05
acc_mask = (lat >= -55.0) & (lat <= -40.0)
subp_mask = (lat >= -65.0) & (lat < -55.0)

def m2d(lc):
    return lc[:, np.newaxis] & np.ones(n_lon, dtype=bool)

regions = {
    'Ice Zone (>15%)': ice_mask,
    'Marginal Ice (5-15%)': ice_marg,
    'Open Ocean (<=5%)': open_mask,
    'ACC (55-40S)': m2d(acc_mask),
    'Subpolar (65-55S)': m2d(subp_mask),
}

# ---- 3. REGIONAL TIMESERIES ----
print('\n3. Computing regional timeseries...')

def wmean(field, weights, mask):
    w = weights[:, np.newaxis] * mask
    f = field.astype(np.float32)
    ok = np.isfinite(f)
    num = np.nansum(f * w, axis=(1, 2))
    den = np.nansum(w * ok.astype(np.float32), axis=(1, 2))
    return np.where(den > 0, num / den, np.nan)

ts = {}
for name, mask in regions.items():
    ts[f'{name} tau'] = wmean(tau_mag, cos_lat, mask)
    ts[f'{name} taueff'] = wmean(tau_eff_mag, cos_lat, mask)
    ts[f'{name} SIC'] = wmean(sic, cos_lat, mask)
for name in regions:
    ts[f'{name} Amp'] = ts[f'{name} taueff'] / ts[f'{name} tau']
    ts[f'{name} Amp'][~np.isfinite(ts[f'{name} Amp'])] = 1.0

# ---- 4. PERIOD MEANS ----
print('\n4. Period means...')
pre = dates < '2016-01-01'
post = dates >= '2016-01-01'
n_pre, n_post = pre.sum(), post.sum()
print(f'  Pre-2016: {n_pre} mo, Post-2016: {n_post} mo')

tau_pre = np.nanmean(tau_mag[pre], axis=0)
tau_post = np.nanmean(tau_mag[post], axis=0)
te_pre = np.nanmean(tau_eff_mag[pre], axis=0)
te_post = np.nanmean(tau_eff_mag[post], axis=0)
sic_p = np.nanmean(sic[pre], axis=0)
sic_q = np.nanmean(sic[post], axis=0)
d_tau = tau_post - tau_pre
d_te = te_post - te_pre
d_sic = sic_q - sic_p
amp_pre = te_pre / tau_pre
amp_post = te_post / tau_post

iz = ice_mask
print(f'\n  Ice Zone metrics:')
print(f'    SIC:   {np.nanmean(sic_p[iz]):.3f} -> {np.nanmean(sic_q[iz]):.3f}')
print(f'    tau:   {np.nanmean(tau_pre[iz]):.4f} -> {np.nanmean(tau_post[iz]):.4f} N/m2')
print(f'    taueff:{np.nanmean(te_pre[iz]):.4f} -> {np.nanmean(te_post[iz]):.4f} N/m2')
print(f'    Amp:   {np.nanmean(amp_pre[iz]):.3f} -> {np.nanmean(amp_post[iz]):.3f}')

# ---- 5. FIGURES ----
print('\n5. Generating figures...')
plt.rcParams.update({'font.size': 12, 'figure.dpi': 200})

# -- Fig 1: Spatial maps (tau, taueff, SIC, Amp) --
fig = plt.figure(figsize=(18, 16))
gs = gridspec.GridSpec(4, 4, figure=fig, hspace=0.3, wspace=0.25)

datasets = [
    ('Wind Stress tau (N/m2)', tau_pre, tau_post, d_tau, (0, 0.12), (-0.025, 0.025), 'RdBu_r'),
    ('Eff. Stress taueff (N/m2)', te_pre, te_post, d_te, (0, 0.12), (-0.025, 0.025), 'RdBu_r'),
    ('Sea Ice Concentration', sic_p, sic_q, d_sic, (0, 1), (-0.5, 0.5), 'RdBu_r'),
    ('Amplification taueff/tau', amp_pre, amp_post, amp_post-amp_pre, (0.6, 1.5), (-0.3, 0.3), 'RdBu_r'),
]
lon2d, lat2d = np.meshgrid(lon, lat)

for i, (ttl, pf, qf, df, r1, r2, cm) in enumerate(datasets):
    for j, (d, r) in enumerate([(pf, r1), (qf, r1), (df, r2)]):
        ax = fig.add_subplot(gs[i, j])
        d_c = np.clip(d, r[0], r[1])
        ax.pcolormesh(lon2d, lat2d, d_c, cmap=cm, shading='auto')
        ax.set_xlim(-180, 180); ax.set_ylim(-75, -40)
        ax.set_xlabel('Lon'); ax.set_ylabel('Lat')
        if j == 0: ax.set_title(f'{ttl}\n1993-2015', fontsize=10)
        elif j == 1: ax.set_title('2016-2024', fontsize=10)
        else: ax.set_title('Difference', fontsize=10)
        if i < 2:
            ax.contour(lon2d, lat2d, sic_p, levels=[0.15], colors='k',
                      linewidths=0.4, linestyles='--', alpha=0.5)
            ax.contour(lon2d, lat2d, sic_q, levels=[0.15], colors='k',
                      linewidths=0.4, linestyles=':', alpha=0.5)

plt.suptitle('Southern Ocean Wind Stress and SIC Changes (ERA5)', fontsize=14, y=0.98)
plt.savefig(f'{FIG}/p04_fig_taueff_spatial.png', bbox_inches='tight')
plt.close()
print(f'  -> {FIG}/p04_fig_taueff_spatial.png')

# -- Fig 2: Timeseries --
fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
ax = axes[0]
for n, ls, c in [('Ice Zone (>15%)', '-', 'b'), ('ACC (55-40S)', '-', 'r'),
                 ('Subpolar (65-55S)', '--', 'orange')]:
    ax.plot(dates, ts[f'{n} taueff'], c=c, ls=ls, lw=0.8, label=f'{n} taueff')
ax.axvline('2016-01-01', color='k', ls='--', lw=0.8, alpha=0.5)
ax.set_ylabel('taueff (N/m2)'); ax.legend(fontsize=9, ncol=2)
ax.set_title('Effective Wind Stress taueff = tau x (1-0.8*SIC)'); ax.grid(True, alpha=0.3)

ax = axes[1]
for n, ls, c in [('Ice Zone (>15%)', '-', 'b'), ('ACC (55-40S)', '-', 'r'),
                 ('Subpolar (65-55S)', '--', 'orange')]:
    ax.plot(dates, ts[f'{n} Amp'], c=c, ls=ls, lw=0.8, label=n)
ax.axvline('2016-01-01', color='k', ls='--', lw=0.8, alpha=0.5)
ax.axhline(1, color='gray', lw=0.5)
ax.set_ylabel('Amplification (taueff/tau)'); ax.legend(fontsize=9, ncol=2)
ax.set_title('SIC-driven Stress Amplification'); ax.grid(True, alpha=0.3)

ax = axes[2]
d_ts = ts['Ice Zone (>15%) taueff'] - ts['Ice Zone (>15%) tau']
ax.plot(dates, d_ts, 'purple', lw=0.8, label='taueff - tau (ice zone)')
ax2 = ax.twinx()
ax2.plot(dates, ts['Ice Zone (>15%) SIC'], 'c-', lw=0.8, alpha=0.6, label='SIC')
ax2.set_ylabel('SIC', color='c'); ax2.tick_params(axis='y', labelcolor='c')
ax.axvline('2016-01-01', color='k', ls='--', lw=0.8, alpha=0.5)
ax.set_ylabel('Stress diff (N/m2)'); ax.set_xlabel('Time')
ax.legend(fontsize=9, loc='upper left'); ax.grid(True, alpha=0.3)
ax.set_title('SIC Loss and taueff Enhancement')
plt.tight_layout()
plt.savefig(f'{FIG}/p04_fig_taueff_timeseries.png', bbox_inches='tight')
plt.close()
print(f'  -> {FIG}/p04_fig_taueff_timeseries.png')

# -- Fig 3: Zonal profile --
fig, ax = plt.subplots(figsize=(8, 5))
zm_n = lambda f: np.nanmean(f, axis=1)
ax.plot(zm_n(tau_pre), lat, 'b-', lw=1.5, label='tau pre-2016')
ax.plot(zm_n(tau_post), lat, 'b--', lw=1.5, label='tau post-2016')
ax.plot(zm_n(te_pre), lat, 'r-', lw=1.5, label='taueff pre-2016')
ax.plot(zm_n(te_post), lat, 'r--', lw=1.5, label='taueff post-2016')
ax.axhline(-55, color='gray', lw=0.5, alpha=0.5)
ax.axhline(-65, color='gray', lw=0.5, alpha=0.5)
ax.set_ylim(-75, -40); ax.set_xlabel('Zonal Mean Stress (N/m2)')
ax.set_ylabel('Latitude'); ax.legend(fontsize=9); ax.grid(True, alpha=0.3)
ax.set_title('Zonal Mean: tau vs taueff')
ax2 = ax.twiny()
ax2.plot(zm_n(sic_p), lat, 'c-', lw=0.8, alpha=0.5, label='SIC pre')
ax2.plot(zm_n(sic_q), lat, 'c--', lw=0.8, alpha=0.5, label='SIC post')
ax2.set_xlabel('SIC', color='c'); ax2.tick_params(axis='x', labelcolor='c')
ax2.set_xlim(0, 1)
plt.tight_layout()
plt.savefig(f'{FIG}/p04_fig_taueff_zonal.png', bbox_inches='tight')
plt.close()
print(f'  -> {FIG}/p04_fig_taueff_zonal.png')

# ---- 6. SUMMARY ----
print('\n' + '='*60)
print('SUMMARY')
print('='*60)
for name in ['Ice Zone (>15%)', 'ACC (55-40S)', 'Subpolar (65-55S)']:
    if name not in regions: continue
    tp = np.nanmean(ts[f'{name} tau'][pre])
    tq = np.nanmean(ts[f'{name} tau'][post])
    ep = np.nanmean(ts[f'{name} taueff'][pre])
    eq = np.nanmean(ts[f'{name} taueff'][post])
    sp = np.nanmean(ts[f'{name} SIC'][pre])
    sq = np.nanmean(ts[f'{name} SIC'][post])
    print(f'\n  {name}')
    print(f'    tau:    {tp:.4f} -> {tq:.4f} ({(tq-tp)/tp*100:+.1f}%)')
    print(f'    taueff: {ep:.4f} -> {eq:.4f} ({(eq-ep)/ep*100:+.1f}%)')
    print(f'    SIC:    {sp:.3f} -> {sq:.3f}')
    print(f'    Amp:    {ep/tp:.2f} -> {eq/tq:.2f}')

print('\nDone.')
