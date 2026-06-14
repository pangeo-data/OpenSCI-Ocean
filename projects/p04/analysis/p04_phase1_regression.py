#!/usr/bin/env python3
"""
P04 Phase 1: Multivariate Regression Attribution of Southern Ocean EKE

Equation: ΔEKE(t) = β₁·W(t) + β₂·tau_eff(t) + β₃·AAO(t) + β₄·Niño3.4(t) + ε

Optimized version: pre-loads all data, fast bilinear interpolation via
pre-computed weights + numpy slicing.

Author: 匿名作者  Date: 2026-06-12
"""

import numpy as np, xarray as xr, pandas as pd, os, warnings
from pathlib import Path
warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats

# -- Paths --------------------------------------------------------------
REPO = str(Path(__file__).resolve().parents[2])
DATA = f'{REPO}/data'
OUT  = f'{REPO}/projects/p04/analysis'
FIG  = f'{REPO}/projects/p04/figures'
os.makedirs(OUT, exist_ok=True); os.makedirs(FIG, exist_ok=True)

# -- Constants ----------------------------------------------------------
RHO_AIR, CD, ALPHA = 1.225, 1.3e-3, 0.8
G, R_EARTH, OMEGA = 9.81, 6371e3, 7.2921e-5
DLON = 0.125 * np.pi / 180.0; DLAT = 0.125 * np.pi / 180.0
ICE_S, ICE_N, ACC_S, ACC_N = -74.9375, -55.0, -55.0, -40.0625

# ======================================================================
# 1. LOAD GRID METADATA
# ======================================================================
print('=' * 60)
print('PHASE 1: EKE REGRESSION (optimized)')
print('=' * 60)

# CMEMS grid
ds0 = xr.open_dataset(
    f'{DATA}/CMEMS-SSH/cmems_obs-sl_glo_phy-ssh_my_allsat-l4-duacs-0.125deg_P1M-m_1781066172836.nc',
    decode_times=False, engine='h5netcdf')
lat_c = ds0.latitude.values.astype(np.float64)
lon_c = ds0.longitude.values.astype(np.float64)
ds0.close()

# ERA5 grid
ds_w = xr.open_dataset(f'{DATA}/ERA5/era5_wind.nc', decode_times=False, engine='h5netcdf')
ds_w = ds_w.sortby('latitude')
lat_e = ds_w.latitude.values.astype(np.float64)
lon_e = ds_w.longitude.values.astype(np.float64)
ds_w.close()

# Pre-compute region masks and weights
cos_lat_c = np.cos(np.deg2rad(lat_c)).astype(np.float32)
f_cor = 2 * OMEGA * np.sin(np.deg2rad(lat_c))
valid_f = np.abs(f_cor) > 2e-6
region_masks = {}
for name, (s, n) in [('ice', (ICE_S, ICE_N)), ('acc', (ACC_S, ACC_N)),
                      ('full', (-90, -40))]:
    region_masks[name] = (lat_c >= s) & (lat_c <= n)

# SSH & ERA5 time axes
ssh_dates = pd.date_range('1993-01-01', '2024-11-01', freq='MS')
ds_w = xr.open_dataset(f'{DATA}/ERA5/era5_wind.nc', decode_times=False, engine='h5netcdf')
era5_all_dates = pd.to_datetime(ds_w.valid_time.values, unit='s')
ds_w.close()
era5_mask = (era5_all_dates >= '1993-01-01') & (era5_all_dates <= '2024-12-31')
era5_idx_offset = np.where(era5_mask)[0][0]
n_era5 = era5_mask.sum()
era5_dates = era5_all_dates[era5_mask]

n_months = len(ssh_dates)
print(f'  SSH: {n_months} months, ERA5: {n_era5} months')

# ======================================================================
# 2. LOAD ALL DATA INTO MEMORY (once)
# ======================================================================
print('\n2. Loading all data into memory...')

# --- SSH SLA ---
print('  SSH SLA...')
ssh_files = sorted([f for f in os.listdir(f'{DATA}/CMEMS-SSH') if f.endswith('.nc')])
ds_list = []
for f in ssh_files:
    ds = xr.open_dataset(f'{DATA}/CMEMS-SSH/{f}', decode_times=False, engine='h5netcdf')
    ds['time'] = pd.to_datetime(ds.time.values, unit='s')
    ds = ds.sel(time=slice('1993-01-01', '2024-12-31'))
    ds_list.append(ds)
ds_full = xr.concat(ds_list, dim='time')
_, uni = np.unique(ds_full.time.values, return_index=True)
ds_full = ds_full.isel(time=np.sort(uni)).sortby('time')
sla = ds_full.sla.values.astype(np.float32)  # (nt, lat, lon)
ds_full.close()
print(f'    SLA: {sla.shape}, {sla.nbytes/1e9:.2f} GB')

# --- ERA5 wind stress ---
print('  ERA5 wind stress...')
with xr.open_dataset(f'{DATA}/ERA5/era5_wind.nc', decode_times=False, engine='h5netcdf') as ds:
    ds = ds.sortby('latitude').isel(valid_time=era5_mask)
    u10 = ds.u10.values.astype(np.float32)
    v10 = ds.v10.values.astype(np.float32)
wspd = np.sqrt(u10**2 + v10**2)
tau_x = RHO_AIR * CD * wspd * u10
tau_y = RHO_AIR * CD * wspd * v10
del u10, v10, wspd
print(f'    tau: {tau_x.shape}, {tau_x.nbytes/1e9:.2f} GB')

# --- ERA5 siconc ---
print('  ERA5 siconc...')
with xr.open_dataset(f'{DATA}/data_stream-moda_stepType-avgua.nc',
                     decode_times=False, engine='h5netcdf') as ds:
    ds = ds.sortby('latitude').isel(valid_time=era5_mask)
    sic = np.clip(ds.siconc.values.astype(np.float32), 0, 1)
print(f'    sic: {sic.shape}, {sic.nbytes/1e9:.2f} GB')

# --- Climate indices ---
def load_idx_3col(path):
    """Load 3-column (year, month, value) index file."""
    d = np.loadtxt(path)
    return pd.Series(d[:, 2], index=pd.to_datetime(
        [f'{int(y)}-{int(m):02d}-01' for y, m in zip(d[:, 0], d[:, 1])]))

def load_nino34_ersst(path):
    """Load Nino3.4 from ERSST file (header + 10-col: YR MON 1+2 ANOM 3 ANOM 4 ANOM 3.4 ANOM).
       Uses column 8 (NINO3.4 SST)."""
    d = np.loadtxt(path, skiprows=1)
    return pd.Series(d[:, 8], index=pd.to_datetime(
        [f'{int(y)}-{int(m):02d}-01' for y, m in zip(d[:, 0], d[:, 1])]))

aao = load_idx_3col(f'{DATA}/climate-indices/aao_monthly.txt')
nino34 = load_nino34_ersst(f'{DATA}/climate-indices/nino34_ersst.txt')

# ======================================================================
# 3. PRE-COMPUTE BILINEAR INTERPOLATION WEIGHTS
# ======================================================================
print('\n3. Pre-computing bilinear interpolation weights...')

# ERA5 to CMEMS grid mapping
# Lat: lat_e has 141 pts [-75..-40], lat_c has 280 pts [-74.9375..-40.0625]
# Lon: lon_e has 1440 pts [-180..179.75], lon_c has 2880 pts [-179.9375..179.9375]
# Find 4 neighbors for each target point
# Pre-compute indices and weights once

# For latitude
lat_tgt = lat_c
lat_src = lat_e
li = np.searchsorted(lat_src, lat_tgt) - 1
li = np.clip(li, 0, len(lat_src) - 2)
lw = (lat_tgt - lat_src[li]) / (lat_src[li + 1] - lat_src[li])
lw = np.clip(lw, 0, 1).astype(np.float32)

# For longitude (with wrap-around)
lon_tgt = lon_c
lon_src = np.asarray(lon_e)
# Handle potential wrap: lon_c goes -179.9375..179.9375, lon_e goes -180..179.75
# We need to map lon_c to lon_e indices
# Simple approach: for each lon_tgt, find 2 neighbors in lon_src
# Apply modulo for wrap-around

oi = np.searchsorted(lon_src, lon_tgt) - 1
# Handle wrap: points near -180 may have oi = -1
wrap_mask = oi < 0
oi[wrap_mask] = len(lon_src) - 1 + oi[wrap_mask] + 1  # This won't work for -180
# Actually, for points < lon_src[0], oi = -1 means we need the last point as neighbor
oi = np.clip(oi, 0, len(lon_src) - 2)
# For points near 180, same wrap issue
# lon_c spans -179.9375..179.9375, lon_e spans -180..179.75
# lon_c[0] = -179.9375 > lon_e[0] = -180, so searchsorted returns 0 (since -179.9375 > -180)
# But we want -180 and -179.75 as neighbors
# Actually let me just handle the simple case: both span same physical range
# oi should mostly be correct for points > lon_e[0]

ow = (lon_tgt - lon_src[oi]) / (lon_src[np.minimum(oi + 1, len(lon_src) - 1)] - lon_src[oi])
ow = np.clip(ow, 0, 1).astype(np.float32)
# Handle wrap: ensure oi+1 doesn't go out of bounds
oi2 = np.minimum(oi + 1, len(lon_src) - 1)
# For points near the end of lon_e, clip to valid range

# Build output mesh coordinates for fast indexing
li_2d = li[:, np.newaxis]      # (lat_tgt, 1)
oi_2d = oi[np.newaxis, :]      # (1, lon_tgt)
lw_2d = lw[:, np.newaxis]      # (lat_tgt, 1)
ow_2d = ow[np.newaxis, :]      # (1, lon_tgt)

# 4 corner indices (ensure valid)
oi2_2d = oi2[np.newaxis, :]

print(f'  Weights pre-computed: {len(lat_tgt)} lat x {len(lon_tgt)} lon')

def bilinear_interp(field):
    """Fast bilinear interpolation using pre-computed indices and weights.
    field: (lat_src, lon_src) float32"""
    f00 = field[li_2d, oi_2d]
    f01 = field[li_2d, oi2_2d]
    f10 = field[li_2d + 1, oi_2d]
    f11 = field[li_2d + 1, oi2_2d]
    return ((1 - lw_2d) * (1 - ow_2d) * f00 +
            (1 - lw_2d) * ow_2d * f01 +
            lw_2d * (1 - ow_2d) * f10 +
            lw_2d * ow_2d * f11)

# ======================================================================
# 4. COMPUTE SPATIAL MEAN FUNCTION
# ======================================================================
# Pre-compute spatial mean weights
_weights = {}
for name in ['ice', 'acc', 'full']:
    m = region_masks[name]
    _weights[name] = (cos_lat_c * m)[:, np.newaxis].astype(np.float32)  # (lat, 1)

def spatial_mean(field_2d, mask_name):
    """Area-weighted mean of a 2D field over a region."""
    w = _weights[mask_name]
    f = field_2d if field_2d.dtype == np.float32 else field_2d.astype(np.float32)
    ok = np.isfinite(f)
    num = np.nansum(f * w)
    den = np.nansum(w * ok.astype(np.float32))
    return num / den if den > 1e-30 else np.nan

# ======================================================================
# 5. LOOP OVER MONTHS
# ======================================================================
print('\n4. Computing monthly timeseries...')

# Match SSH months to ERA5 months
ssh_ts = ssh_dates.values.astype('datetime64[ns]')
era5_ts = era5_dates.values.astype('datetime64[ns]')
# For each SSH month, find closest ERA5 month (should be same month for most)
era5_for_ssh = np.array([np.argmin(np.abs(era5_ts - t)) for t in ssh_ts])

# Pre-allocate timeseries
m = n_months
eke_ice = np.full(m, np.nan, np.float32)
eke_acc = np.full(m, np.nan, np.float32)
eke_full = np.full(m, np.nan, np.float32)
tau_ice = np.full(m, np.nan, np.float32)
tau_acc = np.full(m, np.nan, np.float32)
taueff_ice = np.full(m, np.nan, np.float32)
taueff_acc = np.full(m, np.nan, np.float32)
w_ice = np.full(m, np.nan, np.float32)
w_acc = np.full(m, np.nan, np.float32)
weff_ice = np.full(m, np.nan, np.float32)
sic_ice = np.full(m, np.nan, np.float32)

# Process all months (no interpolation needed in the inner loop!)
print('  Computing EKE...')
for t in range(m):
    if t % 60 == 0 and t > 0:
        print(f'    month {t}/{m}')

    # -- EKE from SLA --
    sla_t = sla[t]                          # (lat, lon)
    f_2d = f_cor[:, np.newaxis]

    sla_pad = np.pad(sla_t, ((0, 0), (1, 1)), mode='wrap')
    deta_dlon = (sla_pad[:, 2:] - sla_pad[:, :-2]) / (2 * DLON)
    v_g_t = G / f_2d * deta_dlon / R_EARTH

    deta_dlat = np.zeros_like(sla_t)
    deta_dlat[1:-1, :] = (sla_t[2:, :] - sla_t[:-2, :]) / (2 * DLAT)
    deta_dlat[0, :] = (sla_t[1, :] - sla_t[0, :]) / DLAT
    deta_dlat[-1, :] = (sla_t[-1, :] - sla_t[-2, :]) / DLAT
    u_g_t = -G / f_2d * deta_dlat / R_EARTH

    u_g_t[~valid_f, :] = np.nan
    v_g_t[~valid_f, :] = np.nan
    eke_t = 0.5 * (u_g_t**2 + v_g_t**2)

    eke_ice[t] = spatial_mean(eke_t, 'ice')
    eke_acc[t] = spatial_mean(eke_t, 'acc')
    eke_full[t] = spatial_mean(eke_t, 'full')

    # -- Wind stress & W --
    ei = era5_for_ssh[t]
    tau_x_e = tau_x[ei]                      # (lat_e, lon_e)
    tau_y_e = tau_y[ei]                      # (lat_e, lon_e)
    sic_e = sic[ei]                          # (lat_e, lon_e)

    # Interpolate to CMEMS grid
    txc = bilinear_interp(tau_x_e)
    tyc = bilinear_interp(tau_y_e)
    sc = bilinear_interp(sic_e)

    tau_mag_c = np.sqrt(txc**2 + tyc**2)
    tau_eff_x_c = txc * (1 - ALPHA * sc)
    tau_eff_y_c = tyc * (1 - ALPHA * sc)
    tau_eff_mag_c = np.sqrt(tau_eff_x_c**2 + tau_eff_y_c**2)

    w_t = txc * u_g_t + tyc * v_g_t
    w_eff_t = tau_eff_x_c * u_g_t + tau_eff_y_c * v_g_t

    tau_ice[t] = spatial_mean(tau_mag_c, 'ice')
    tau_acc[t] = spatial_mean(tau_mag_c, 'acc')
    taueff_ice[t] = spatial_mean(tau_eff_mag_c, 'ice')
    taueff_acc[t] = spatial_mean(tau_eff_mag_c, 'acc')
    w_ice[t] = spatial_mean(w_t, 'ice')
    w_acc[t] = spatial_mean(w_t, 'acc')
    weff_ice[t] = spatial_mean(w_eff_t, 'ice')
    sic_ice[t] = spatial_mean(sc, 'ice')

# Free large arrays
del sla, tau_x, tau_y, sic

print(f'\n  EKE ice: {np.nanmean(eke_ice):.6f} +/- {np.nanstd(eke_ice):.6f} m^2/s^2')
print(f'  EKE ACC: {np.nanmean(eke_acc):.6f} +/- {np.nanstd(eke_acc):.6f} m^2/s^2')

# ======================================================================
# 6. BUILD DATAFRAME
# ======================================================================
print('\n5. Building DataFrame...')
df = pd.DataFrame({'time': ssh_dates})
df['eke_ice'] = eke_ice; df['eke_acc'] = eke_acc; df['eke_full'] = eke_full
df['tau_ice'] = tau_ice; df['tau_acc'] = tau_acc
df['taueff_ice'] = taueff_ice; df['taueff_acc'] = taueff_acc
df['w_ice'] = w_ice; df['w_acc'] = w_acc
df['weff_ice'] = weff_ice; df['sic_ice'] = sic_ice
df['aao'] = aao.reindex(ssh_dates).values
df['nino34'] = nino34.reindex(ssh_dates).values
df = df.dropna(subset=['eke_ice'])

# Deseason & standardize
for var in ['eke_ice', 'eke_acc', 'eke_full', 'tau_ice', 'tau_acc',
            'taueff_ice', 'taueff_acc', 'w_ice', 'w_acc', 'weff_ice',
            'sic_ice', 'aao', 'nino34']:
    clim = df.groupby(df['time'].dt.month)[var].transform('mean')
    df[f'{var}_anom'] = df[var] - clim
    df[f'{var}_std'] = (df[f'{var}_anom'] - df[f'{var}_anom'].mean()) / df[f'{var}_anom'].std(ddof=1)

print(f'  DataFrame: {len(df)} months')

# ======================================================================
# 7. REGRESSION
# ======================================================================
def ols(y, Xl, names):
    from scipy import stats as st
    Xa = np.column_stack(Xl)
    X = np.column_stack([np.ones(Xa.shape[0]), Xa])
    n, p = X.shape
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    yp = X @ b; res = y - yp
    rss, tss = np.sum(res**2), np.sum((y - y.mean())**2)
    r2 = 1 - rss/tss; r2a = 1 - (1-r2)*(n-1)/(n-p)
    v = rss/(n-p) * np.linalg.inv(X.T @ X)
    se = np.sqrt(np.diag(v))
    t = b / se; pv = 2*(1-st.t.cdf(np.abs(t), n-p))
    bs = b[1:] * np.std(Xa, axis=0, ddof=1) / np.std(y, ddof=1)
    return {'b':b, 'bs':bs, 'se':se, 't':t, 'p':pv, 'r2':r2, 'r2a':r2a,
            'names':['const']+list(names), 'n':n, 'res':res, 'yp':yp}

preg = lambda mask: ols(
    df['eke_ice_std'].values[mask],
    [df[w].values[mask] for w in ['w_ice_std', 'taueff_ice_std', 'aao_std', 'nino34_std']],
    ['W', 'taueff', 'AAO', 'Nino34'])

def pr(r, title):
    print(f'\n  {title}')
    print(f'  R^2={r["r2"]:.4f} R2a={r["r2a"]:.4f} n={r["n"]}')
    for i, n in enumerate(r['names']):
        s = '**' if r['p'][i]<0.01 else '*' if r['p'][i]<0.05 else ''
        print(f'  {n:<12s} beta={r["b"][i]:8.4f} std={r["bs"][i-1] if i>0 else 0:7.4f} t={r["t"][i]:6.2f} p={r["p"][i]:.5f} {s}')

mask_all = (np.isfinite(df['eke_ice_std'].values) &
            np.isfinite(df['w_ice_std'].values) &
            np.isfinite(df['taueff_ice_std'].values) &
            np.isfinite(df['aao_std'].values) &
            np.isfinite(df['nino34_std'].values))
dates_clean = df['time'].values[mask_all]

r_all = preg(mask_all)
pr(r_all, 'FULL PERIOD (1993-2024) - Ice Zone')

pre = dates_clean < np.datetime64('2016-01-01')
post = dates_clean >= np.datetime64('2016-01-01')
r_pre = preg(mask_all & (df['time'].values < np.datetime64('2016-01-01')))
r_post = preg(mask_all & (df['time'].values >= np.datetime64('2016-01-01')))
pr(r_pre, 'PRE-2016'); pr(r_post, 'POST-2016')

# ACC zone
mask_acc = (np.isfinite(df['eke_acc_std'].values) &
            np.isfinite(df['w_acc_std'].values) &
            np.isfinite(df['taueff_acc_std'].values) &
            np.isfinite(df['aao_std'].values) &
            np.isfinite(df['nino34_std'].values))
r_acc = ols(df['eke_acc_std'].values[mask_acc],
            [df[w].values[mask_acc] for w in ['w_acc_std', 'taueff_acc_std', 'aao_std', 'nino34_std']],
            ['W','taueff','AAO','Nino34'])
pr(r_acc, 'ACC ZONE - Full Period')

# With SIC
r_sic = ols(df['eke_ice_std'].values[mask_all],
            [df[w].values[mask_all] for w in ['w_ice_std', 'taueff_ice_std', 'sic_ice_std', 'aao_std', 'nino34_std']],
            ['W','taueff','SIC','AAO','Nino34'])
pr(r_sic, 'FULL with SIC')

# ======================================================================
# 8. ROLLING REGRESSION
# ======================================================================
y = df['eke_ice_std'].values[mask_all]
Xv = [df[w].values[mask_all] for w in ['w_ice_std', 'taueff_ice_std', 'aao_std', 'nino34_std']]
wn = 120
roll_dates, roll_b = [], {k: [] for k in ['W','taueff','AAO','Nino34','r2']}
for i in range(len(y)-wn+1):
    rw = ols(y[i:i+wn], [x[i:i+wn] for x in Xv], ['W','taueff','AAO','Nino34'])
    roll_dates.append(pd.Timestamp(dates_clean[i+wn//2]))
    for j, k in enumerate(['W','taueff','AAO','Nino34']):
        roll_b[k].append(rw['bs'][j])
    roll_b['r2'].append(rw['r2'])

# ======================================================================
# 9. SAVE
# ======================================================================
print('\n6. Saving results...')
df.to_pickle(f'{OUT}/p04_timeseries.pkl')
df.to_csv(f'{OUT}/p04_timeseries.csv')

with open(f'{OUT}/p04_regression_results.txt', 'w', encoding='utf-8') as f:
    f.write('P04 Phase 1 Regression Results\n')
    for r, t in [(r_all,'Full'), (r_pre,'Pre-2016'), (r_post,'Post-2016'), (r_acc,'ACC'), (r_sic,'Full+SIC')]:
        f.write(f'\n{t}\n')
        for i, n in enumerate(r['names']):
            f.write(f'{n:12s} b={r["b"][i]:8.4f} se={r["se"][i]:7.4f} t={r["t"][i]:6.2f} p={r["p"][i]:.5f}\n')
        f.write(f'R2={r["r2"]:.4f} R2a={r["r2a"]:.4f}\n')

if roll_dates:
    np.savez(f'{OUT}/p04_rolling_regression.npz',
             years=np.array([d.toordinal() for d in roll_dates]),
             **{k: np.array(v) for k, v in roll_b.items()})

print('  Timeseries + regression results saved to', OUT)

# ======================================================================
# 10. FIGURES
# ======================================================================
print('\n7. Figures...')
plt.rcParams.update({'font.size': 11, 'figure.dpi': 150})

# Fig 1: Timeseries
fig, ax = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
ax[0].plot(df.time, df.eke_ice, 'b-', lw=0.8, label='Ice zone')
ax[0].plot(df.time, df.eke_acc, 'r-', lw=0.8, alpha=0.6, label='ACC')
ax[0].axvline('2016-01-01', color='k', ls='--', lw=0.8)
ax[0].set_ylabel('EKE (m^2/s^2)'); ax[0].legend(); ax[0].set_title('EKE')

ax[1].plot(df.time, df.taueff_ice, 'g-', lw=0.8, label='taueff ice')
ax[1].plot(df.time, df.tau_ice, 'orange', lw=0.8, alpha=0.6, label='tau ice')
ax[1].axvline('2016-01-01', color='k', ls='--', lw=0.8)
ax[1].set_ylabel('Stress (N/m^2)'); ax[1].legend()

ax[2].plot(df.time, df.w_ice, 'purple', lw=0.8, label='W=tau*u_g')
ax[2].plot(df.time, df.weff_ice, 'darkgreen', lw=0.8, alpha=0.7, label='W_eff')
ax[2].axvline('2016-01-01', color='k', ls='--', lw=0.8)
ax[2].set_ylabel('Wind Work (W/m^2)'); ax[2].legend()

ax[3].plot(df.time, df.aao, 'c-', lw=0.8, label='AAO')
ax[3].plot(df.time, df.nino34, 'm-', lw=0.8, alpha=0.7, label='Nino3.4')
ax[3].axvline('2016-01-01', color='k', ls='--', lw=0.8)
ax[3].set_ylabel('Index'); ax[3].legend(); ax[3].set_xlabel('Time')
plt.tight_layout()
plt.savefig(f'{FIG}/p04_fig_timeseries.png', bbox_inches='tight'); plt.close()
print(f'  timeseries -> {FIG}/p04_fig_timeseries.png')

# Fig 2: Regression coefficients
names = ['W', 'taueff', 'AAO', 'Nino34']
fig, ax = plt.subplots(figsize=(8, 5))
x = np.arange(4)
ax.bar(x, r_all['bs'], yerr=1.96*r_all['se'][1:], capsize=5,
       color=['#1f77b4','#ff7f0e','#2ca02c','#d62728'], alpha=0.8)
for xi, bi, ci, p in zip(x, r_all['bs'], 1.96*r_all['se'][1:], r_all['p'][1:]):
    s = '**' if p<0.01 else '*' if p<0.05 else 'ns'
    ax.text(xi, bi+ci+0.02, s, ha='center', fontsize=10, fontweight='bold')
ax.axhline(0, color='k', lw=0.5)
ax.set_xticks(x); ax.set_xticklabels(names)
ax.set_ylabel('Standardized beta')
ax.set_title(f'EKE Regression (R^2={r_all["r2"]:.3f})')
plt.tight_layout()
plt.savefig(f'{FIG}/p04_fig_regression_coeffs.png', bbox_inches='tight'); plt.close()
print(f'  coeffs -> {FIG}/p04_fig_regression_coeffs.png')

# Fig 3: Pre/Post
fig, ax = plt.subplots(figsize=(8, 5))
width = 0.35
ax.bar(x-width/2, r_pre['bs'], width, yerr=1.96*r_pre['se'][1:],
       capsize=4, color='#1f77b4', alpha=0.8, label=f'Pre (R^2={r_pre["r2"]:.3f})')
ax.bar(x+width/2, r_post['bs'], width, yerr=1.96*r_post['se'][1:],
       capsize=4, color='#ff7f0e', alpha=0.8, label=f'Post (R^2={r_post["r2"]:.3f})')
ax.axhline(0, color='k', lw=0.5)
ax.set_xticks(x); ax.set_xticklabels(names)
ax.set_ylabel('Standardized beta'); ax.legend(); ax.set_title('Pre vs Post 2016')
plt.tight_layout()
plt.savefig(f'{FIG}/p04_fig_pre_post_comparison.png', bbox_inches='tight'); plt.close()
print(f'  pre/post -> {FIG}/p04_fig_pre_post_comparison.png')

# Fig 4: Rolling
if roll_dates:
    fig, ax = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    for k in ['W','taueff','AAO','Nino34']:
        ax[0].plot(roll_dates, roll_b[k], label=k, lw=1.5)
    ax[0].axhline(0, color='gray', lw=0.5); ax[0].axvline('2016-01-01', color='k', ls='--', lw=0.8, alpha=0.5)
    ax[0].set_ylabel('Std beta'); ax[0].legend(); ax[0].set_title('Rolling 10yr Coeffs')
    ax[1].plot(roll_dates, roll_b['r2'], 'k-', lw=1.5)
    ax[1].axvline('2016-01-01', color='k', ls='--', lw=0.8, alpha=0.5)
    ax[1].set_ylabel('R^2'); ax[1].set_ylim(0, 1); ax[1].set_xlabel('Year')
    plt.tight_layout()
    plt.savefig(f'{FIG}/p04_fig_rolling_regression.png', bbox_inches='tight'); plt.close()
    print(f'  rolling -> {FIG}/p04_fig_rolling_regression.png')

# Fig 5: Obs vs Pred
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(pd.to_datetime(dates_clean), y, 'k-', lw=0.6, alpha=0.5, label='Obs')
ax.plot(pd.to_datetime(dates_clean), r_all['yp'], 'r-', lw=0.8,
        label=f'OLS (R^2={r_all["r2"]:.3f})')
ax.axvline('2016-01-01', color='b', ls='--', lw=0.8, alpha=0.5)
ax.set_ylabel('Std EKE'); ax.set_xlabel('Time'); ax.legend()
ax.set_title('EKE: Observed vs Regression')
plt.tight_layout()
plt.savefig(f'{FIG}/p04_fig_obs_vs_pred.png', bbox_inches='tight'); plt.close()
print(f'  obs_vs_pred -> {FIG}/p04_fig_obs_vs_pred.png')

# ======================================================================
print('\n' + '=' * 60)
print('DONE')
print('=' * 60)
print(f'\nR^2 (full)    = {r_all["r2"]:.4f}')
print(f'R^2 (pre-16)  = {r_pre["r2"]:.4f}')
print(f'R^2 (post-16) = {r_post["r2"]:.4f}')
for i, n in enumerate(names):
    s = '**' if r_all['p'][i+1]<0.01 else '*' if r_all['p'][i+1]<0.05 else ''
    print(f'{n:<12s} beta_std = {r_all["bs"][i]:.4f}  p = {r_all["p"][i+1]:.5f} {s}')
