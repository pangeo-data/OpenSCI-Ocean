#!/usr/bin/env python3
"""
P04 Tipping Point Analysis: Did Antarctic sea ice cross a tipping point in 2016?

Three lines of evidence:
  1. Multi-variable change point detection (Pettitt test)
  2. Critical slowing down indicators (AC1, variance)
  3. Phase space trajectory (PCA regime shift)

Author: anonymous  Date: 2026-06-12
"""

import numpy as np, xarray as xr, pandas as pd, os, warnings
from pathlib import Path
warnings.filterwarnings('ignore')
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from scipy import stats

# -- Paths --------------------------------------------------------------
REPO = str(Path(__file__).resolve().parents[2])
DATA = f'{REPO}/data'
OUT  = f'{REPO}/projects/p04/analysis'
FIG  = f'{REPO}/projects/p04/figures'
os.makedirs(OUT, exist_ok=True); os.makedirs(FIG, exist_ok=True)

RHO_AIR, CD, ALPHA = 1.225, 1.3e-3, 0.8
G, R_EARTH, OMEGA = 9.81, 6371e3, 7.2921e-5

ICE_S, ICE_N = -74.9375, -55.0

# ======================================================================
# UTILITY FUNCTIONS
# ======================================================================

def pettitt_test(y):
    """Pettitt test for a single change point in the mean.

    Returns: (cp_idx, cp_year, K_stat, p_value)
    cp_idx: index of the change point (0-based)
    cp_year: year of the change point (for yearly data)
    """
    n = len(y)
    if n < 10:
        return 0, y.index[0] if hasattr(y, 'index') else 0, 0, 1.0

    # Compute U(t) = |sum_{i=1}^{t} sum_{j=t+1}^{n} sign(y_i - y_j)|
    U = np.zeros(n)
    # Efficient computation: U(t+1) = U(t) + V(t+1) where V(t+1) = sum_{j=t+2}^{n} sign(y_{t+1} - y_j)
    # But for simplicity and correctness, use direct computation
    for t in range(1, n):
        s = 0
        for i in range(t):
            for j in range(t, n):
                s += np.sign(y[i] - y[j])
        U[t] = abs(s)

    K = U.max()
    cp = U.argmax()
    # p-value approximation
    p = 2 * np.exp(-6 * K**2 / (n**3 + n**2))
    return cp, K, p

def confidence_ellipse(x, y, ax, n_std=1.5, **kwargs):
    """Draw a confidence ellipse around (x,y) points."""
    cov = np.cov(x, y)
    pearson = cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2,
                      facecolor='none', **kwargs)
    scale_x = np.sqrt(cov[0, 0]) * n_std
    scale_y = np.sqrt(cov[1, 1]) * n_std
    transf = ax.transData.get_affine() + plt.matplotlib.transforms.Affine2D().rotate_deg(
        45).scale(scale_x, scale_y).translate(np.mean(x), np.mean(y))
    ellipse.set_transform(transf)
    return ax.add_patch(ellipse)

# ======================================================================
# 1. LOAD DATA
# ======================================================================
print('='*60)
print('TIPPING POINT ANALYSIS')
print('='*60)
print('\n1. Loading data...')

# --- NSIDC Sea Ice Index: total Antarctic extent ---
print('   NSIDC Sea Ice Index...')
all_ext = []
for m in range(1, 13):
    fp = f'{DATA}/NSIDC Sea Ice Index/S_{m:02d}_extent_v4.0.csv'
    d = pd.read_csv(fp, skiprows=1, names=['year','mo','source','region','extent','area'])
    yr = d['year'].values.astype(int)
    ext = pd.to_numeric(d['extent'], errors='coerce').values
    ext[ext < -100] = np.nan
    for y, e in zip(yr, ext):
        all_ext.append({'year': int(y), 'month': m, 'extent': e})
dext = pd.DataFrame(all_ext)
dext['time'] = pd.to_datetime(dext.apply(lambda r: f'{int(r.year)}-{int(r.month):02d}-01', axis=1))
dext = dext.sort_values('time').set_index('time')
dext = dext[dext.index >= '1979-01-01']
n_ext = dext['extent'].notna().sum()
print(f'   NSIDC total extent: {n_ext} months ({dext.index[0].year}-{dext.index[-1].year})')

# --- ERA5 SIC ---
print('   ERA5 SIC...')
with xr.open_dataset(f'{DATA}/data_stream-moda_stepType-avgua.nc',
                     decode_times=False, engine='h5netcdf') as ds:
    ds = ds.sortby('latitude')
    dates_sic = pd.to_datetime(ds.valid_time.values, unit='s')
    sic_all = np.clip(ds.siconc.values.astype(np.float32), 0, 1)
    lat_e = ds.latitude.values.astype(np.float64)
    lon_e = ds.longitude.values.astype(np.float64)

# Region mean
cos_lat_e = np.cos(np.deg2rad(lat_e)).astype(np.float32)
ice_mask_e = (lat_e >= ICE_S) & (lat_e <= ICE_N)
ice_w_e = (cos_lat_e * ice_mask_e)[:, np.newaxis]

# Mask for the ice zone: also exclude open ocean pixels
# Use climatological SIC > 15% to define the ice zone
sic_clim = np.nanmean(sic_all, axis=0)
ice_pixels = sic_clim > 0.15

def sic_weighted_mean(field):
    w = ice_w_e * ice_pixels
    ok = np.isfinite(field)
    num = np.nansum(field * w)
    den = np.nansum(w * ok.astype(np.float32))
    return num / den if den > 1e-30 else np.nan

# Compute monthly SIC for ice zone
sic_ts = np.array([sic_weighted_mean(sic_all[t]) for t in range(len(dates_sic))])
df_sic = pd.DataFrame({'sic': sic_ts}, index=dates_sic)

# --- Phase 1 & Phase 2 saved data ---
print('   Phase 1/2 results...')
df1 = pd.read_pickle(f'{OUT}/p04_timeseries.pkl') if os.path.exists(f'{OUT}/p04_timeseries.pkl') else None
df2 = pd.read_pickle(f'{OUT}/p04_energy_cycle.pkl') if os.path.exists(f'{OUT}/p04_energy_cycle.pkl') else None

# --- Climate indices ---
def load_idx_3col(path):
    d = np.loadtxt(path)
    return pd.Series(d[:, 2], index=pd.to_datetime(
        [f'{int(y)}-{int(m):02d}-01' for y, m in zip(d[:, 0], d[:, 1])]))
def load_nino34(path):
    d = np.loadtxt(path, skiprows=1)
    return pd.Series(d[:, 8], index=pd.to_datetime(
        [f'{int(y)}-{int(m):02d}-01' for y, m in zip(d[:, 0], d[:, 1])]))
aao = load_idx_3col(f'{DATA}/climate-indices/aao_monthly.txt')
nino34 = load_nino34(f'{DATA}/climate-indices/nino34_ersst.txt')

# ======================================================================
# 2. DESEASONALIZE
# ======================================================================
print('\n2. Deseasonalizing...')

def deseason(series):
    s = series.copy()
    clim = s.groupby(s.index.month).mean()
    return s - clim.loc[s.index.month].values

# NSIDC extent
dext['anom'] = deseason(dext['extent'])
# SIC
df_sic['anom'] = deseason(df_sic['sic'])

# Phase 1/2 variables
if df1 is not None:
    df1['time'] = pd.to_datetime(df1['time'])
    df1 = df1.set_index('time')
    # Already deseasoned from Phase 1

if df2 is not None:
    df2['time'] = pd.to_datetime(df2['time'])
    df2 = df2.set_index('time')

# ======================================================================
# 3. ANNUAL MEANS
# ======================================================================
print('\n3. Computing annual means...')

def annual_mean(series):
    return series.groupby(series.index.year).mean()

def annual_n(series):
    return series.groupby(series.index.year).count()

# NSIDC
ext_ann = annual_mean(dext['extent'])
ext_ann_a = annual_mean(dext['anom'])

# SIC (from ERA5, full record)
sic_ann_a = annual_mean(df_sic['anom'])

# Combined multivariate dataset for common period (1993-2024)
comb_vars = {
    'SIC': df_sic['anom'],
    'tau_eff': df1['taueff_ice_anom'] if df1 is not None else None,
    'EKE': df1['eke_ice_anom'] if df1 is not None else None,
    'W_eddy': df1['w_ice_anom'] if df1 is not None else None,
    'CK': df2['ck_ice'] if df2 is not None else None,
    'W_mean': df2['wm_ice'] if df2 is not None else None,
}
comb_vars = {k: v for k, v in comb_vars.items() if v is not None}
# Align to common dates
common_idx = None
for k, v in comb_vars.items():
    if common_idx is None:
        common_idx = set(v.index)
    else:
        common_idx = common_idx & set(v.index)
common_idx = sorted(common_idx)

comb_df = pd.DataFrame({k: v.loc[common_idx] for k, v in comb_vars.items()}, index=common_idx)
comb_ann = comb_df.groupby(comb_df.index.year).mean()
comb_ann_std = comb_df.groupby(comb_df.index.year).std(ddof=1)
comb_n = comb_df.groupby(comb_df.index.year).count()

print(f'   Common period: {comb_ann.index[0]}-{comb_ann.index[-1]} ({len(comb_ann)} years)')
print(f'   Variables: {list(comb_ann.columns)}')

# AAO annual
aao_ann = annual_mean(aao.reindex(common_idx)).loc[comb_ann.index]
nino_ann = annual_mean(nino34.reindex(common_idx)).loc[comb_ann.index]

# ======================================================================
# 4. CHANGE POINT DETECTION
# ======================================================================
print('\n4. Pettitt change point detection...')

def detect_cp(annual_series, label=''):
    vals = annual_series.values
    years = annual_series.index.values
    ok = np.isfinite(vals)
    if ok.sum() < 10:
        print(f'   {label}: insufficient data ({ok.sum()} years)')
        return None
    try:
        cp_idx, K, p = pettitt_test(vals[ok])
        cp_year = years[ok][cp_idx]
        pre_mean = np.nanmean(vals[ok][:cp_idx])
        post_mean = np.nanmean(vals[ok][cp_idx:])
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'
        print(f'   {label:12s}: cp={cp_year}, K={K:.0f}, p={p:.4f} {sig}  ({pre_mean:.3f} -> {post_mean:.3f})')
        return {'year': cp_year, 'K': K, 'p': p, 'pre_mean': pre_mean, 'post_mean': post_mean}
    except Exception as e:
        print(f'   {label}: ERROR {e}')
        return None

cp_results = {}
# NSIDC extent
cp_results['NSIDC Extent'] = detect_cp(ext_ann, 'NSIDC Extent')
cp_results['NSIDC Anom'] = detect_cp(ext_ann_a, 'NSIDC Anom')
# ERA5 SIC (1979-)
sic_era_79 = df_sic[df_sic.index >= '1979-01-01']
sic_era_ann_79 = sic_era_79['anom'].groupby(sic_era_79.index.year).mean()
cp_results['ERA5 SIC'] = detect_cp(sic_era_ann_79, 'ERA5 SIC')
# Phase 1/2 variables
for v in comb_ann.columns:
    cp_results[v] = detect_cp(comb_ann[v], v)
# AAO
cp_results['AAO'] = detect_cp(aao_ann, 'AAO')
cp_results['Nino34'] = detect_cp(nino_ann, 'Nino34')

# ======================================================================
# 5. CRITICAL SLOWING DOWN
# ======================================================================
print('\n5. Critical slowing down indicators...')

def sliding_ac1(series, window=120):  # 10-year window
    vals = series.values
    n = len(vals)
    ac1 = np.full(n, np.nan)
    var = np.full(n, np.nan)
    for i in range(window//2, n - window//2):
        w = vals[i - window//2 : i + window//2]
        ok = np.isfinite(w)
        if ok.sum() >= 60:
            wc = w[ok]
            # AC1
            ac1[i] = np.corrcoef(wc[:-1], wc[1:])[0, 1]
            # Variance
            var[i] = np.var(wc, ddof=1)
    return ac1, var

# SIC CSD
# Use ERA5 SIC from 1979-2015 (before tipping point) for CSD
sic_pre2016 = df_sic['anom'][(df_sic.index >= '1979-01-01') & (df_sic.index < '2016-01-01')]
ac1_sic, var_sic = sliding_ac1(sic_pre2016, window=120)

# Also extend to full record to see post-2016
sic_full = df_sic['anom'][df_sic.index >= '1979-01-01']
ac1_full, var_full = sliding_ac1(sic_full, window=120)
dates_csd = sic_full.index

# ======================================================================
# 6. PCA PHASE SPACE
# ======================================================================
print('\n6. Phase space PCA...')

# Select variables for PCA
pca_vars = ['SIC', 'tau_eff', 'EKE', 'CK', 'W_mean', 'W_eddy']
pca_available = [v for v in pca_vars if v in comb_ann.columns]
print(f'   PCA variables: {pca_available}')

X = comb_ann[pca_available].values.copy()
# Standardize
X_mean = np.nanmean(X, axis=0)
X_std = np.nanstd(X, axis=0)
Xs = (X - X_mean) / X_std

# Handle NaN
ok = np.all(np.isfinite(Xs), axis=1)
Xs_ok = Xs[ok]
years_ok = comb_ann.index[ok].values

# SVD PCA
U, s, Vt = np.linalg.svd(Xs_ok, full_matrices=False)
pc1 = U[:, 0] * s[0]
pc2 = U[:, 1] * s[1]
var_explained = s**2 / (s**2).sum()

print(f'   PC1: {var_explained[0]*100:.1f}% variance')
print(f'   PC2: {var_explained[1]*100:.1f}% variance')

# Loadings
loadings = Vt.T
print(f'   PC1 loadings: {dict(zip(pca_available, [f"{l:.3f}" for l in loadings[:, 0]]))}')
print(f'   PC2 loadings: {dict(zip(pca_available, [f"{l:.3f}" for l in loadings[:, 1]]))}')

# ======================================================================
# 7. FIGURES
# ======================================================================
print('\n7. Generating figures...')
plt.rcParams.update({'font.size': 11, 'figure.dpi': 150})

# ---- Fig 1: Antarctic sea ice tipping point ----
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 2, hspace=0.35, wspace=0.3)

# Panel A: Monthly extent anomalies
ax = fig.add_subplot(gs[0, :])
ax.plot(dext.index, dext['anom'], 'steelblue', lw=0.3, alpha=0.5, label='Monthly anom')
roll = dext['anom'].rolling(12, center=True).mean()
ax.plot(dext.index, roll, 'k-', lw=1.5, label='12-mo running mean')
ax.axvline('2016-01-01', color='r', ls='--', lw=1.5, alpha=0.7, label='2016')
ax.axhline(0, color='gray', lw=0.5)
ax.set_ylabel('Extent anom (million km^2)')
ax.set_title('(a) Antarctic Sea Ice Extent Anomaly (NSIDC)')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# Panel B: Annual means + change point
ax = fig.add_subplot(gs[1, 0])
yrs = ext_ann.index.values
vals = ext_ann.values
ax.plot(yrs, vals, 'o-', color='steelblue', lw=1.5, markersize=5)
cp_e = cp_results.get('NSIDC Extent')
if cp_e:
    ax.axvline(cp_e['year'], color='r', ls='--', lw=1.5, alpha=0.7)
    ax.axhline(cp_e['pre_mean'], color='steelblue', ls=':', lw=1, alpha=0.5)
    ax.axhline(cp_e['post_mean'], color='red', ls=':', lw=1, alpha=0.5)
    sig = ['ns', '*', '**', '***'][min(3, int(-np.log10(max(cp_e['p'], 1e-15))))]
    ax.text(cp_e['year'], ax.get_ylim()[1]*0.9, f'CP={cp_e["year"]} p={cp_e["p"]:.3f} {sig}',
            ha='center', fontsize=9, bbox=dict(facecolor='white', alpha=0.8))
ax.set_ylabel('Extent (million km^2)')
ax.set_title(f'(b) Annual Mean + Pettitt CP')
ax.grid(True, alpha=0.3)

# Panel C: Era5 SIC annual anomalies
ax = fig.add_subplot(gs[1, 1])
sic_ann_a_79 = sic_era_ann_79
yrs_s = sic_ann_a_79.index.values
vals_s = sic_ann_a_79.values
ax.plot(yrs_s, vals_s, 'o-', color='darkcyan', lw=1.5, markersize=5)
cp_s = cp_results.get('ERA5 SIC')
if cp_s:
    ax.axvline(cp_s['year'], color='r', ls='--', lw=1.5, alpha=0.7)
    sig = ['ns', '*', '**', '***'][min(3, int(-np.log10(max(cp_s['p'], 1e-15))))]
    ax.text(cp_s['year'], ax.get_ylim()[1]*0.9, f'CP={cp_s["year"]} p={cp_s["p"]:.3f} {sig}',
            ha='center', fontsize=9, bbox=dict(facecolor='white', alpha=0.8))
ax.set_ylabel('SIC anom (ERA5 ice zone)')
ax.set_title(f'(c) ERA5 SIC Anomaly + Pettitt CP')
ax.grid(True, alpha=0.3)

# Panel D: CSD - sliding AC1
ax = fig.add_subplot(gs[2, 0])
# Plot AC1 for full record
ax.plot(dates_csd, ac1_full, 'darkred', lw=1)
ax.axvline('2016-01-01', color='r', ls='--', lw=1.5, alpha=0.5)
# Mark the AC1 increase before 2016
pre_mask = dates_csd < '2016-01-01'
ac1_pre_early = np.nanmean(ac1_full[pre_mask][:60]) if sum(pre_mask)>60 else np.nan
ac1_pre_late = np.nanmean(ac1_full[pre_mask][-60:]) if sum(pre_mask)>60 else np.nan
if np.isfinite(ac1_pre_early) and np.isfinite(ac1_pre_late):
    ax.annotate(f'AC1: {ac1_pre_early:.2f} -> {ac1_pre_late:.2f}',
                xy=(0.7, 0.95), xycoords='axes fraction', fontsize=9,
                ha='center', bbox=dict(facecolor='white', alpha=0.8))
ax.axhline(0, color='gray', lw=0.5)
ax.set_ylabel('Lag-1 AC (10yr window)')
ax.set_title('(d) Critical Slowing Down: AC1')
ax.grid(True, alpha=0.3)

# Panel E: CSD - sliding variance
ax = fig.add_subplot(gs[2, 1])
var_norm = var_full / np.nanmedian(var_full[pre_mask]) * 100  # % of baseline
ax.plot(dates_csd, var_norm, 'darkgreen', lw=1)
ax.axvline('2016-01-01', color='r', ls='--', lw=1.5, alpha=0.5)
var_pre_early = np.nanmedian(var_norm[pre_mask][:60]) if sum(pre_mask)>60 else np.nan
var_pre_late = np.nanmedian(var_norm[pre_mask][-60:]) if sum(pre_mask)>60 else np.nan
if np.isfinite(var_pre_early) and np.isfinite(var_pre_late):
    ax.annotate(f'Var: {var_pre_early:.0f}% -> {var_pre_late:.0f}%',
                xy=(0.7, 0.95), xycoords='axes fraction', fontsize=9,
                ha='center', bbox=dict(facecolor='white', alpha=0.8))
ax.set_ylabel('Variance (% of baseline)')
ax.set_title('(e) Critical Slowing Down: Variance')
ax.grid(True, alpha=0.3)

plt.suptitle('Antarctic Sea Ice Tipping Point Evidence (NSIDC + ERA5)', fontsize=14, y=0.995)
plt.tight_layout()
plt.savefig(f'{FIG}/p04_fig_tipping_point.png', bbox_inches='tight')
plt.close()
print(f'   -> {FIG}/p04_fig_tipping_point.png')

# ---- Fig 2: Multi-variable synchronization ----
n_vars = len(comb_ann.columns)
n_cols = 3
n_rows = int(np.ceil(n_vars / n_cols))

fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 3*n_rows))
axes = axes.flatten()
colors = plt.cm.Set2(np.linspace(0, 1, n_vars))

for idx, v in enumerate(comb_ann.columns):
    ax = axes[idx]
    vals = comb_ann[v]
    yrs = vals.index.values
    ax.plot(yrs, vals.values, 'o-', color=colors[idx], lw=1.5, markersize=4)

    cp = cp_results.get(v)
    if cp:
        ax.axvline(cp['year'], color='r', ls='--', lw=1.5, alpha=0.7)
        sig = ['ns', '*', '**', '***'][min(3, int(-np.log10(max(cp['p'], 1e-15))))]
        ax.text(0.98, 0.05, f'CP={cp["year"]} {sig}', transform=ax.transAxes,
                fontsize=8, ha='right', bbox=dict(facecolor='white', alpha=0.8))
        # Pre/post means
        ax.axhline(cp['pre_mean'], color='gray', ls=':', lw=0.8, alpha=0.5)
        ax.axhline(cp['post_mean'], color='red', ls=':', lw=0.8, alpha=0.5)

    ax.axvline('2016-01-01', color='k', ls='--', lw=0.8, alpha=0.3)
    ax.set_title(v, fontsize=11)
    ax.grid(True, alpha=0.3)

# Hide unused subplots
for idx in range(n_vars, len(axes)):
    axes[idx].set_visible(False)

plt.suptitle('Multi-Variable Regime Shift: Annual Means (1993-2024)', fontsize=14, y=0.995)
plt.tight_layout()
plt.savefig(f'{FIG}/p04_fig_multivar_cp.png', bbox_inches='tight')
plt.close()
print(f'   -> {FIG}/p04_fig_multivar_cp.png')

# ---- Fig 3: Phase space PCA ----
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Panel A: PCA trajectory
ax = axes[0]
sc = ax.scatter(pc1, pc2, c=years_ok, cmap='RdYlBu_r', s=50, edgecolors='k', linewidth=0.5, zorder=3)
# Connect trajectory
ax.plot(pc1, pc2, 'k-', lw=0.5, alpha=0.3, zorder=1)
# Highlight pre/post
pre_yr = years_ok < 2016
post_yr = years_ok >= 2016
if pre_yr.sum() > 2:
    confidence_ellipse(pc1[pre_yr], pc2[pre_yr], ax, n_std=1.5,
                       edgecolor='steelblue', lw=2, linestyle='--', label='Pre-2016')
if post_yr.sum() > 2:
    confidence_ellipse(pc1[post_yr], pc2[post_yr], ax, n_std=1.5,
                       edgecolor='red', lw=2, linestyle='--', label='Post-2016')
# Mark start/end
ax.scatter(pc1[0], pc2[0], c='green', s=120, marker='*', zorder=5, label=f'{years_ok[0]}')
ax.scatter(pc1[-1], pc2[-1], c='red', s=120, marker='*', zorder=5, label=f'{years_ok[-1]}')
plt.colorbar(sc, ax=ax, label='Year')
ax.set_xlabel(f'PC1 ({var_explained[0]*100:.1f}%)')
ax.set_ylabel(f'PC2 ({var_explained[1]*100:.1f}%)')
ax.set_title('(a) Phase Space Trajectory')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Panel B: Loadings
ax = axes[1]
x_load = loadings[:, 0]
y_load = loadings[:, 1]
for i, v in enumerate(pca_available):
    ax.arrow(0, 0, x_load[i], y_load[i], color=colors[i], width=0.02,
             head_width=0.08, head_length=0.08)
    ax.text(x_load[i]*1.15, y_load[i]*1.15, v, fontsize=10, color=colors[i])
# Add PC variance explained
ax.set_xlabel(f'PC1 ({var_explained[0]*100:.1f}%)')
ax.set_ylabel(f'PC2 ({var_explained[1]*100:.1f}%)')
ax.set_title('(b) Variable Loadings')
ax.axhline(0, color='gray', lw=0.5)
ax.axvline(0, color='gray', lw=0.5)
ax.grid(True, alpha=0.3)
ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-1.2, 1.2)

plt.suptitle('Southern Ocean Coupled System Regime Shift (PCA)', fontsize=14)
plt.tight_layout()
plt.savefig(f'{FIG}/p04_fig_phase_space.png', bbox_inches='tight')
plt.close()
print(f'   -> {FIG}/p04_fig_phase_space.png')

# ======================================================================
# 8. SUMMARY
# ======================================================================
print('\n' + '='*60)
print('SUMMARY: TIPPING POINT EVIDENCE')
print('='*60)

print('\n--- Change Point Detection (Pettitt test) ---')
print(f'{"Variable":15s} {"CP Year":8s} {"p-value":8s} {"Sig":5s} {"Change":10s}')
print('-'*46)
for v, r in cp_results.items():
    if r:
        sig = '***' if r['p']<0.001 else '**' if r['p']<0.01 else '*' if r['p']<0.05 else 'ns'
        chg = f"{r['post_mean']-r['pre_mean']:+.3f}"
        print(f'{v:15s} {r["year"]:<8d} {r["p"]:<8.4f} {sig:<5s} {chg}')
    else:
        print(f'{v:15s} {"FAIL":8s}')

print('\n--- Critical Slowing Down (SIC, 1979-2015) ---')
ac1_trend = ac1_sic[~np.isnan(ac1_sic)]
if len(ac1_trend) > 20:
    half = len(ac1_trend)//2
    print(f'  AC1:      early {np.nanmean(ac1_trend[:half]):.3f} -> late {np.nanmean(ac1_trend[-half:]):.3f}')
    print(f'  Variance: early {np.nanmean(var_sic[:half]):.2e} -> late {np.nanmean(var_sic[-half:]):.2e}')

print('\n--- Phase Space ---')
print(f'  PC1: {var_explained[0]*100:.1f}% variance (regime shift axis)')
print(f'  PC2: {var_explained[1]*100:.1f}% variance')
print(f'  PC1 loadings: {dict(zip(pca_available, [f"{l:.3f}" for l in loadings[:, 0]]))}')

print('\n--- Key Findings ---')
# Find the range of CP years
cp_years = [r['year'] for r in cp_results.values() if r]
if cp_years:
    print(f'  Change points range: {min(cp_years)}-{max(cp_years)}')
    n_sig = sum(1 for r in cp_results.values() if r and r['p'] < 0.05)
    print(f'  Significant (p<0.05): {n_sig}/{len(cp_results)}')
    print(f'  Variables with CP near 2016 (2014-2018):',
          sum(1 for r in cp_results.values() if r and 2014 <= r['year'] <= 2018))
print('\nDone.')
