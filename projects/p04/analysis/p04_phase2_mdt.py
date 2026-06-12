#!/usr/bin/env python3
"""
P04 Phase 2: Lorenz Energy Cycle from MDT -- Closing the Energy Chain

  tau_eff -> W_mean + W_eddy -> MKE --CK-> EKE

Computes:
  - u_bar, v_bar from CNES-CLS18 MDT (mean geostrophic currents)
  - Mean shear gradients: du/dx, du/dy, dv/dx, dv/dy
  - MKE = 0.5*(u_bar^2 + v_bar^2)
  - CK(t) = -[u'u'*du/dx + u'v'*(du/dy+dv/dx) + v'v'*dv/dy]
  - W_mean(t) = tau(t) . u_bar
  - Pre/post-2016 changes for each energy term

Author: anonymous  Date: 2026-06-12
"""

import numpy as np, xarray as xr, pandas as pd, os, warnings
warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

# -- Paths --------------------------------------------------------------
REPO = 'E:/OpenSCI-Ocean'
DATA = f'{REPO}/data'
OUT  = f'{REPO}/projects/p04/analysis'
FIG  = f'{REPO}/projects/p04/figures'
os.makedirs(OUT, exist_ok=True); os.makedirs(FIG, exist_ok=True)

# -- Constants ----------------------------------------------------------
RHO_AIR, CD, ALPHA = 1.225, 1.3e-3, 0.8
G, R_EARTH, OMEGA = 9.81, 6371e3, 7.2921e-5
DLON = 0.125 * np.pi / 180.0   # rad
DLAT = 0.125 * np.pi / 180.0   # rad
RHO_W = 1025.0                 # kg/m^3, seawater density

ICE_S, ICE_N = -74.9375, -55.0
ACC_S, ACC_N = -55.0, -40.0625

# ======================================================================
# 1. LOAD MDT & COMPUTE MEAN SHEAR GRADIENTS
# ======================================================================
print('=' * 60)
print('PHASE 2: LORENZ ENERGY CYCLE FROM MDT')
print('=' * 60)

print('\n1. Loading MDT...')
ds = xr.open_dataset(
    f'{DATA}/cnes_obs-sl_glo_phy-mdt_my_0.125deg_P20Y_1781169018418.nc',
    decode_times=False, engine='h5netcdf')
lat_m = ds.latitude.values.astype(np.float64)
lon_m = ds.longitude.values.astype(np.float64)

# Subset to Southern Ocean (matches CMEMS SSH domain)
i0 = np.searchsorted(lat_m, -75.0)   # index for -74.9375
i1 = np.searchsorted(lat_m, -40.0)   # index for -40.0625
lat_so = lat_m[i0:i1].copy()
u_bar = ds.u.values[0, i0:i1, :].astype(np.float64)   # (280, 2880)
v_bar = ds.v.values[0, i0:i1, :].astype(np.float64)
ds.close()

nlat, nlon = u_bar.shape
print(f'  Domain: {nlat} lat x {nlon} lon ({lat_so[0]:.4f} to {lat_so[-1]:.4f})')
print(f'  u_bar: [{np.nanmin(u_bar):.4f}, {np.nanmax(u_bar):.4f}] m/s')
print(f'  v_bar: [{np.nanmin(v_bar):.4f}, {np.nanmax(v_bar):.4f}] m/s')

# ---- Shear gradients on sphere ----
print('\n2. Computing mean shear gradients...')
cos_lat_so = np.cos(np.deg2rad(lat_so)).astype(np.float64)
dx = R_EARTH * cos_lat_so * DLON   # (nlat,) zonal spacing at each latitude [m]
dy = R_EARTH * DLAT                 # scalar meridional spacing [m]

def ddx(f):
    """Centered finite diff d/dx on (nlat,nlon), periodic in lon. Returns field in 1/m."""
    df = np.zeros_like(f)
    df[:, 1:-1] = (f[:, 2:] - f[:, :-2]) / (2.0 * dx[:, np.newaxis])
    # Periodic wrap
    df[:, 0] = (f[:, 1] - f[:, -1]) / (2.0 * dx[:])
    df[:, -1] = (f[:, 0] - f[:, -2]) / (2.0 * dx[:])
    return df

def ddy(f):
    """Centered finite diff d/dy on (nlat,nlon), one-sided at edges. Returns field in 1/m."""
    df = np.zeros_like(f)
    df[1:-1, :] = (f[2:, :] - f[:-2, :]) / (2.0 * dy)
    df[0, :] = (f[1, :] - f[0, :]) / dy
    df[-1, :] = (f[-1, :] - f[-2, :]) / dy
    return df

du_dx = ddx(u_bar)   # du_bar/dx
du_dy = ddy(u_bar)   # du_bar/dy
dv_dx = ddx(v_bar)   # dv_bar/dx
dv_dy = ddy(v_bar)   # dv_bar/dy

# Combined term for CK
shear_uu = du_dx                           # for u'u' term
shear_uv = du_dy + dv_dx                   # for u'v' term
shear_vv = dv_dy                           # for v'v' term

print(f'  du/dx: [{np.nanmin(du_dx):.2e}, {np.nanmax(du_dx):.2e}] 1/s')
print(f'  du/dy: [{np.nanmin(du_dy):.2e}, {np.nanmax(du_dy):.2e}] 1/s')
print(f'  dv/dx: [{np.nanmin(dv_dx):.2e}, {np.nanmax(dv_dx):.2e}] 1/s')
print(f'  dv/dy: [{np.nanmin(dv_dy):.2e}, {np.nanmax(dv_dy):.2e}] 1/s')

# ---- MKE ----
mke = 0.5 * (u_bar**2 + v_bar**2)
print(f'\n3. MKE computed: mean={np.nanmean(mke):.6f} m^2/s^2')

# ======================================================================
# 4. CMEMS GRID INFO (for region masks, Coriolis)
# ======================================================================
print('\n4. Setting up CMEMS grid...')
ds0 = xr.open_dataset(
    f'{DATA}/CMEMS-SSH/cmems_obs-sl_glo_phy-ssh_my_allsat-l4-duacs-0.125deg_P1M-m_1781066172836.nc',
    decode_times=False, engine='h5netcdf')
lat_c = ds0.latitude.values.astype(np.float64)
lon_c = ds0.longitude.values.astype(np.float64)
ds0.close()

cos_lat_c = np.cos(np.deg2rad(lat_c)).astype(np.float32)
f_cor = 2 * OMEGA * np.sin(np.deg2rad(lat_c))
valid_f = np.abs(f_cor) > 2e-6

# Region masks
region_masks = {}
for name, (s, n) in [('ice', (ICE_S, ICE_N)), ('acc', (ACC_S, ACC_N)),
                      ('full', (-90, -40))]:
    region_masks[name] = (lat_c >= s) & (lat_c <= n)

# Pre-compute spatial weights for each region
_weights = {}
for name in ['ice', 'acc', 'full']:
    m = region_masks[name]
    _weights[name] = (cos_lat_c * m)[:, np.newaxis].astype(np.float32)

def spatial_mean(field_2d, mask_name):
    """Area-weighted mean of a 2D field over a region."""
    w = _weights[mask_name]
    f = field_2d if field_2d.dtype == np.float32 else field_2d.astype(np.float32)
    ok = np.isfinite(f)
    num = np.nansum(f * w)
    den = np.nansum(w * ok.astype(np.float32))
    return num / den if den > 1e-30 else np.nan

# ======================================================================
# 5. ERA5 BILINEAR INTERPOLATION WEIGHTS
# ======================================================================
print('   Pre-computing bilinear interpolation (ERA5 -> CMEMS)...')
ds_w = xr.open_dataset(f'{DATA}/ERA5/era5_wind.nc', decode_times=False, engine='h5netcdf')
ds_w = ds_w.sortby('latitude')
lat_e = ds_w.latitude.values.astype(np.float64)
lon_e = ds_w.longitude.values.astype(np.float64)
ds_w.close()

# Latitude weights
li = np.searchsorted(lat_e, lat_c) - 1
li = np.clip(li, 0, len(lat_e) - 2)
lw = (lat_c - lat_e[li]) / (lat_e[li + 1] - lat_e[li])
lw = np.clip(lw, 0, 1).astype(np.float32)

# Longitude weights
oi = np.searchsorted(lon_e, lon_c) - 1
oi = np.clip(oi, 0, len(lon_e) - 2)
ow = (lon_c - lon_e[oi]) / (lon_e[np.minimum(oi + 1, len(lon_e) - 1)] - lon_e[oi])
ow = np.clip(ow, 0, 1).astype(np.float32)
oi2 = np.minimum(oi + 1, len(lon_e) - 1)

li_2d = li[:, np.newaxis]; oi_2d = oi[np.newaxis, :]
lw_2d = lw[:, np.newaxis]; ow_2d = ow[np.newaxis, :]
oi2_2d = oi2[np.newaxis, :]

def bilinear_interp(field):
    """Fast bilinear interpolation using pre-computed indices and weights."""
    f00 = field[li_2d, oi_2d]; f01 = field[li_2d, oi2_2d]
    f10 = field[li_2d + 1, oi_2d]; f11 = field[li_2d + 1, oi2_2d]
    return ((1 - lw_2d) * (1 - ow_2d) * f00 +
            (1 - lw_2d) * ow_2d * f01 +
            lw_2d * (1 - ow_2d) * f10 +
            lw_2d * ow_2d * f11)

# ======================================================================
# 6. LOAD DATA
# ======================================================================
print('\n5. Loading data...')

# SSH SLA
print('   SSH SLA...')
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
sla = ds_full.sla.values.astype(np.float32)
ds_full.close()
print(f'   SLA: {sla.shape}, {sla.nbytes/1e9:.2f} GB')

ssh_dates = pd.date_range('1993-01-01', '2024-11-01', freq='MS')
n_months = len(ssh_dates)

# ERA5 wind stress
print('   ERA5 wind stress...')
with xr.open_dataset(f'{DATA}/ERA5/era5_wind.nc', decode_times=False, engine='h5netcdf') as ds:
    era5_all_dates = pd.to_datetime(ds.valid_time.values, unit='s')
    ds = ds.sortby('latitude')
    era5_mask = (era5_all_dates >= '1993-01-01') & (era5_all_dates <= '2024-12-31')
    u10 = ds.u10.values[era5_mask].astype(np.float32)
    v10 = ds.v10.values[era5_mask].astype(np.float32)

spd = np.sqrt(u10**2 + v10**2)
tau_x_e = RHO_AIR * CD * spd * u10
tau_y_e = RHO_AIR * CD * spd * v10
del u10, v10, spd
print(f'   tau: {tau_x_e.shape}, {tau_x_e.nbytes/1e9:.2f} GB')

# ======================================================================
# 7. MONTHLY LOOP
# ======================================================================
print('\n6. Computing monthly CK, W_mean, and EKE...')

# Match SSH months to ERA5 months
ssh_ts = ssh_dates.values.astype('datetime64[ns]')
era5_dates_values = pd.to_datetime(era5_all_dates[era5_mask]).values.astype('datetime64[ns]')
era5_for_ssh = np.array([np.argmin(np.abs(era5_dates_values - t)) for t in ssh_ts])

# Pre-allocate
m = n_months
ck_ice = np.full(m, np.nan, np.float64)
ck_acc = np.full(m, np.nan, np.float64)
ck_full = np.full(m, np.nan, np.float64)
wm_ice = np.full(m, np.nan, np.float64)
wm_acc = np.full(m, np.nan, np.float64)
wm_full = np.full(m, np.nan, np.float64)
eke_ice = np.full(m, np.nan, np.float32)
eke_acc = np.full(m, np.nan, np.float32)

# CK units: m^2/s^3 = W/kg.  W_mean units: W/m^2.
# Use same naming convention

for t in range(m):
    if t % 60 == 0 and t > 0:
        print(f'   month {t}/{m}')

    # --- u_g', v_g' from SLA ---
    sla_t = sla[t]
    f_2d = f_cor[:, np.newaxis]

    # v' = (g/f) * d(SLA)/dx
    sla_pad = np.pad(sla_t, ((0, 0), (1, 1)), mode='wrap')
    deta_dlon = (sla_pad[:, 2:] - sla_pad[:, :-2]) / (2 * DLON)
    v_g_t = G / f_2d * deta_dlon / R_EARTH

    # u' = -(g/f) * d(SLA)/dy
    deta_dlat = np.zeros_like(sla_t)
    deta_dlat[1:-1, :] = (sla_t[2:, :] - sla_t[:-2, :]) / (2 * DLAT)
    deta_dlat[0, :] = (sla_t[1, :] - sla_t[0, :]) / DLAT
    deta_dlat[-1, :] = (sla_t[-1, :] - sla_t[-2, :]) / DLAT
    u_g_t = -G / f_2d * deta_dlat / R_EARTH

    # Mask equatorial region
    u_g_t[~valid_f, :] = np.nan
    v_g_t[~valid_f, :] = np.nan

    # --- EKE ---
    eke_t = 0.5 * (u_g_t**2 + v_g_t**2).astype(np.float32)
    eke_ice[t] = spatial_mean(eke_t, 'ice')
    eke_acc[t] = spatial_mean(eke_t, 'acc')

    # --- CK ---
    # Eddy momentum fluxes
    u2 = u_g_t * u_g_t
    uv = u_g_t * v_g_t
    v2 = v_g_t * v_g_t

    ck_t = -(u2 * shear_uu + uv * shear_uv + v2 * shear_vv)
    ck_ice[t] = spatial_mean(ck_t, 'ice')
    ck_acc[t] = spatial_mean(ck_t, 'acc')
    ck_full[t] = spatial_mean(ck_t, 'full')

    # --- W_mean = tau . u_bar ---
    ei = era5_for_ssh[t]
    tx_interp = bilinear_interp(tau_x_e[ei])
    ty_interp = bilinear_interp(tau_y_e[ei])
    wm_t = tx_interp * u_bar + ty_interp * v_bar
    wm_ice[t] = spatial_mean(wm_t, 'ice')
    wm_acc[t] = spatial_mean(wm_t, 'acc')
    wm_full[t] = spatial_mean(wm_t, 'full')

del sla, tau_x_e, tau_y_e

print(f'\n   Ice Zone results:')
print(f'     CK:     {np.nanmean(ck_ice):.2e} +/- {np.nanstd(ck_ice):.2e} m^2/s^3')
print(f'     W_mean: {np.nanmean(wm_ice):.2e} +/- {np.nanstd(wm_ice):.2e} W/m^2')
print(f'     EKE:    {np.nanmean(eke_ice):.6f} +/- {np.nanstd(eke_ice):.6f} m^2/s^2')

# ======================================================================
# 8. LOAD PHASE 1 DATA FOR W_eddy COMPARISON
# ======================================================================
print('\n7. Loading Phase 1 results...')
df1 = pd.read_pickle(f'{OUT}/p04_timeseries.pkl')

# Align dates
dates_p1 = df1['time'].values.astype('datetime64[ns]')
dates_p2 = ssh_dates.values.astype('datetime64[ns]')
common_mask = np.isin(dates_p2, dates_p1) & np.isfinite(eke_ice) & np.isfinite(ck_ice) & np.isfinite(wm_ice)
dates_common = dates_p2[common_mask]

# W_eddy from Phase 1
we_ice = np.full(m, np.nan, np.float64)
we_acc = np.full(m, np.nan, np.float64)
for i, d in enumerate(dates_p2):
    j = np.where(dates_p1 == d)[0]
    if len(j) > 0:
        we_ice[i] = df1['w_ice'].values[j[0]]
        we_acc[i] = df1['w_acc'].values[j[0]]

# Subsample to common valid mask
idx = np.where(common_mask)[0]
dates_c = dates_p2[common_mask]
eke_i = eke_ice[idx]; eke_a = eke_acc[idx]
ck_i = ck_ice[idx]; ck_a = ck_acc[idx]
wm_i = wm_ice[idx]; wm_a = wm_acc[idx]
we_i = we_ice[idx]; we_a = we_acc[idx]

n_valid = len(idx)
print(f'   {n_valid} valid months')

# ======================================================================
# 9. PRE/POST 2016 CHANGES
# ======================================================================
print('\n8. Pre- vs Post-2016 comparison...')

pre = dates_c < np.datetime64('2016-01-01')
post = dates_c >= np.datetime64('2016-01-01')
n_pre, n_post = pre.sum(), post.sum()
print(f'   Pre-2016: {n_pre} mo, Post-2016: {n_post} mo')

def pct_chg(pre_vals, post_vals):
    return (np.nanmean(post_vals) - np.nanmean(pre_vals)) / np.nanmean(pre_vals) * 100

print(f'\n   Ice Zone changes:')
vars_ice = [('CK', ck_i), ('W_mean', wm_i), ('W_eddy', we_i), ('EKE', eke_i)]
for name, vals in vars_ice:
    mp = np.nanmean(vals[pre]); mq = np.nanmean(vals[post])
    pc = (mq - mp) / abs(mp) * 100 if mp != 0 else 0
    print(f'     {name:8s}: {mp:.4e} -> {mq:.4e} ({pc:+.1f}%)')

print(f'\n   ACC changes:')
vars_acc = [('CK', ck_a), ('W_mean', wm_a), ('W_eddy', we_a), ('EKE', eke_a)]
for name, vals in vars_acc:
    mp = np.nanmean(vals[pre]); mq = np.nanmean(vals[post])
    pc = (mq - mp) / abs(mp) * 100 if mp != 0 else 0
    print(f'     {name:8s}: {mp:.4e} -> {mq:.4e} ({pc:+.1f}%)')

# ======================================================================
# 10. FIGURES
# ======================================================================
print('\n9. Generating figures...')
plt.rcParams.update({'font.size': 11, 'figure.dpi': 150})

# -- Fig 1: Four-panel timeseries --
fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)
dates_pd = pd.to_datetime(dates_c)

# Panel 1: EKE
ax = axes[0]
ax.plot(dates_pd, eke_i, 'b-', lw=0.8, label='Ice Zone')
ax.plot(dates_pd, eke_a, 'r-', lw=0.8, alpha=0.6, label='ACC')
ax.axvline('2016-01-01', color='k', ls='--', lw=0.8, alpha=0.5)
ax.set_ylabel('EKE (m^2/s^2)')
ax.legend(fontsize=9, ncol=2)
ax.set_title('Eddy Kinetic Energy')
ax.grid(True, alpha=0.3)

# Panel 2: CK
ax = axes[1]
ax.plot(dates_pd, ck_i * 1e7, 'b-', lw=0.8, label=f'Ice Zone (mean={np.nanmean(ck_i):.2e})')
ax.plot(dates_pd, ck_a * 1e7, 'r-', lw=0.8, alpha=0.6, label=f'ACC (mean={np.nanmean(ck_a):.2e})')
ax.axvline('2016-01-01', color='k', ls='--', lw=0.8, alpha=0.5)
ax.axhline(0, color='gray', lw=0.5)
ax.set_ylabel('CK x 1e7 (m^2/s^3)')
ax.legend(fontsize=9, ncol=2)
ax.set_title('Barotropic Conversion CK = -u_i.u_j . du_bar_i/dx_j')
ax.grid(True, alpha=0.3)

# Panel 3: W_mean
ax = axes[2]
ax.plot(dates_pd, wm_i * 1e3, 'b-', lw=0.8, label=f'Ice Zone (mean={np.nanmean(wm_i):.2e})')
ax.plot(dates_pd, wm_a * 1e3, 'r-', lw=0.8, alpha=0.6, label=f'ACC (mean={np.nanmean(wm_a):.2e})')
ax.axvline('2016-01-01', color='k', ls='--', lw=0.8, alpha=0.5)
ax.set_ylabel('W_mean x 1e3 (W/m^2)')
ax.legend(fontsize=9, ncol=2)
ax.set_title('Wind Work on Mean Flow: W_mean = tau . u_bar')
ax.grid(True, alpha=0.3)

# Panel 4: W_eddy
ax = axes[3]
ax.plot(dates_pd, we_i * 1e3, 'b-', lw=0.8, label=f'Ice Zone (mean={np.nanmean(we_i):.2e})')
ax.plot(dates_pd, we_a * 1e3, 'r-', lw=0.8, alpha=0.6, label=f'ACC (mean={np.nanmean(we_a):.2e})')
ax.axvline('2016-01-01', color='k', ls='--', lw=0.8, alpha=0.5)
ax.set_ylabel('W_eddy x 1e3 (W/m^2)')
ax.legend(fontsize=9, ncol=2)
ax.set_title('Wind Work on Eddies: W_eddy = tau . u_g')
ax.grid(True, alpha=0.3)
ax.set_xlabel('Time')

plt.suptitle('Southern Ocean Lorenz Energy Cycle Terms', fontsize=13, y=0.995)
plt.tight_layout()
plt.savefig(f'{FIG}/p04_fig_energy_timeseries.png', bbox_inches='tight')
plt.close()
print(f'   -> {FIG}/p04_fig_energy_timeseries.png')

# -- Fig 2: Pre/Post bar chart --
fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=False)

# Ice Zone
ax = axes[0]
labels = ['CK', 'W_mean', 'W_eddy', 'EKE']
# Scale for visibility: CK x1e7, W_mean x1e3, W_eddy x1e3, EKE x1e3
scales = [1e7, 1e3, 1e3, 1e3]
units = ['x1e-7 m^2/s^3', 'x1e-3 W/m^2', 'x1e-3 W/m^2', 'x1e-3 m^2/s^2']
pre_means = [np.nanmean(vals[pre]) for vals in [ck_i, wm_i, we_i, eke_i]]
post_means = [np.nanmean(vals[post]) for vals in [ck_i, wm_i, we_i, eke_i]]
pre_errs = [np.nanstd(vals[pre])/np.sqrt(n_pre) for vals in [ck_i, wm_i, we_i, eke_i]]
post_errs = [np.nanstd(vals[post])/np.sqrt(n_post) for vals in [ck_i, wm_i, we_i, eke_i]]

x = np.arange(len(labels))
w = 0.35
for idx, (p, q, pe, qe) in enumerate(zip(pre_means, post_means, pre_errs, post_errs)):
    s = scales[idx]
    ax.bar(x[idx]-w/2, p*s, w, yerr=1.96*pe*s, capsize=4, color='#1f77b4', alpha=0.8, label='Pre-2016' if idx==0 else '')
    ax.bar(x[idx]+w/2, q*s, w, yerr=1.96*qe*s, capsize=4, color='#ff7f0e', alpha=0.8, label='Post-2016' if idx==0 else '')

    # % change annotation
    pct = (q-p)/abs(p)*100 if p != 0 else 0
    ymax = max(p*s+qe*s, q*s+qe*s)
    ax.text(x[idx], ymax*1.1, f'{pct:+.1f}%', ha='center', fontsize=8, fontweight='bold')

ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylabel('Scaled Value')
ax.legend(fontsize=9)
ax.set_title('Ice Zone - Pre vs Post 2016')
ax.axhline(0, color='gray', lw=0.5)

# ACC
ax = axes[1]
pre_means_a = [np.nanmean(vals[pre]) for vals in [ck_a, wm_a, we_a, eke_a]]
post_means_a = [np.nanmean(vals[post]) for vals in [ck_a, wm_a, we_a, eke_a]]
pre_errs_a = [np.nanstd(vals[pre])/np.sqrt(n_pre) for vals in [ck_a, wm_a, we_a, eke_a]]
post_errs_a = [np.nanstd(vals[post])/np.sqrt(n_post) for vals in [ck_a, wm_a, we_a, eke_a]]

for idx, (p, q, pe, qe) in enumerate(zip(pre_means_a, post_means_a, pre_errs_a, post_errs_a)):
    s = scales[idx]
    ax.bar(x[idx]-w/2, p*s, w, yerr=1.96*pe*s, capsize=4, color='#1f77b4', alpha=0.8, label='Pre-2016' if idx==0 else '')
    ax.bar(x[idx]+w/2, q*s, w, yerr=1.96*qe*s, capsize=4, color='#ff7f0e', alpha=0.8, label='Post-2016' if idx==0 else '')

    pct = (q-p)/abs(p)*100 if p != 0 else 0
    ymax = max(p*s+qe*s, q*s+qe*s)
    ax.text(x[idx], ymax*1.1, f'{pct:+.1f}%', ha='center', fontsize=8, fontweight='bold')

ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylabel('Scaled Value')
ax.legend(fontsize=9)
ax.set_title('ACC Zone - Pre vs Post 2016')
ax.axhline(0, color='gray', lw=0.5)

plt.suptitle('Energy Terms: Pre-2016 vs Post-2016', fontsize=13)
plt.tight_layout()
plt.savefig(f'{FIG}/p04_fig_energy_budget.png', bbox_inches='tight')
plt.close()
print(f'   -> {FIG}/p04_fig_energy_budget.png')

# -- Fig 3: CK vs EKE scatter (is barotropic conversion driving EKE?) --
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for ax_i, region, ck_v, eke_v, lbl in [
    (axes[0], 'Ice Zone', ck_i, eke_i, 'Ice Zone'),
    (axes[1], 'ACC', ck_a, eke_a, 'ACC')]:

    ok = np.isfinite(ck_v) & np.isfinite(eke_v)
    c = ck_v[ok]; e = eke_v[ok]

    ax_i.scatter(c*1e7, e*1e3, s=8, alpha=0.4, c='steelblue')

    # Linear fit
    A = np.column_stack([np.ones(c.size), c])
    b = np.linalg.lstsq(A, e, rcond=None)[0]
    r = np.corrcoef(c, e)[0, 1]
    x_fit = np.linspace(c.min(), c.max(), 50)
    y_fit = b[0] + b[1]*x_fit
    ax_i.plot(x_fit*1e7, y_fit*1e3, 'r-', lw=2, label=f'r={r:.3f}')

    ax_i.axvline(0, color='gray', lw=0.5)
    ax_i.axhline(0, color='gray', lw=0.5)
    ax_i.set_xlabel('CK x 1e7 (m^2/s^3)')
    ax_i.set_ylabel('EKE x 1e3 (m^2/s^2)')
    ax_i.set_title(f'{lbl}: CK vs EKE')
    ax_i.legend()
    ax_i.grid(True, alpha=0.3)

plt.suptitle('Barotropic Conversion vs Eddy Kinetic Energy', fontsize=13)
plt.tight_layout()
plt.savefig(f'{FIG}/p04_fig_ck_vs_eke.png', bbox_inches='tight')
plt.close()
print(f'   -> {FIG}/p04_fig_ck_vs_eke.png')

# ======================================================================
# 11. SAVE RESULTS
# ======================================================================
print('\n10. Saving results...')
df_out = pd.DataFrame({
    'time': pd.to_datetime(dates_c),
    'eke_ice': eke_i, 'eke_acc': eke_a,
    'ck_ice': ck_i, 'ck_acc': ck_a,
    'wm_ice': wm_i, 'wm_acc': wm_a,
    'we_ice': we_i, 'we_acc': we_a,
})
df_out.to_pickle(f'{OUT}/p04_energy_cycle.pkl')
df_out.to_csv(f'{OUT}/p04_energy_cycle.csv', index=False)

# Save MDT fields for later use
np.savez(f'{OUT}/p04_mdt_fields.npz',
         lat=lat_so, lon=lon_m[:nlon],
         u_bar=u_bar, v_bar=v_bar,
         du_dx=du_dx, du_dy=du_dy, dv_dx=dv_dx, dv_dy=dv_dy,
         mke=mke)

print(f'   -> {OUT}/p04_energy_cycle.pkl')
print(f'   -> {OUT}/p04_mdt_fields.npz')

# ======================================================================
print('\n' + '='*60)
print('PHASE 2 COMPLETE')
print('='*60)

print(f'\n  CK (ice zone):   mean={np.nanmean(ck_i):.2e} m^2/s^3')
print(f'  W_mean (ice):    mean={np.nanmean(wm_i):.2e} W/m^2')
print(f'  W_eddy (ice):    mean={np.nanmean(we_i):.2e} W/m^2')
print(f'  EKE (ice zone):  mean={np.nanmean(eke_i):.6f} m^2/s^2')

print(f'\n  Energy chain changes (Ice Zone, post-2016 minus pre-2016):')
for name, vals in vars_ice:
    mp = np.nanmean(vals[pre]); mq = np.nanmean(vals[post])
    pc = (mq - mp) / abs(mp) * 100 if mp != 0 else 0
    print(f'    {name:8s}: {mp:.4e} -> {mq:.4e} ({pc:+.1f}%)')

print('\nDone.')
