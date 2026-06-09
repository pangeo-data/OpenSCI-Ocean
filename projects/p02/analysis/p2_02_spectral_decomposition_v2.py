"""
P2-02: Improved spectral decomposition of equatorial SSH.

Fixes from external review:
1. Replace NaN→0 with linear interpolation
2. Add Hann window (taper) to reduce spectral leakage
3. Remove linear trend and 90-day low-pass (ENSO background)
4. Validate FFT sign convention with synthetic test
5. Report energy fractions honestly

Method: Wheeler-Kiladis style k-ω filtering on detrended,
tapered Hovmöller data.
"""
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import yaml
from scipy.ndimage import uniform_filter1d
from scipy.signal import detrend
from scipy.signal.windows import tukey

BASE = Path(__file__).resolve().parents[1]
with open(BASE / "config.yaml") as f:
    cfg = yaml.safe_load(f)

DATA_DIR = BASE / "data" / "duacs"
FIG_DIR = BASE / "figures"

ds = xr.open_dataset(DATA_DIR / "duacs_eqpac_daily_2023_2025.nc")
sla = ds["sla"]

lon_raw = sla.longitude.values
lon_360 = np.where(lon_raw < 0, lon_raw + 360, lon_raw)
sort_idx = np.argsort(lon_360)
sla_sorted = sla.isel(longitude=sort_idx)
lon_sorted = lon_360[sort_idx]
mask_lon = (lon_sorted >= 130) & (lon_sorted <= 280)
sla_pac = sla_sorted.isel(longitude=mask_lon)
lon_pac = lon_sorted[mask_lon]
sla_eq = sla_pac.sel(latitude=slice(-2, 2)).mean(dim="latitude")
sla_clim = sla_eq.groupby("time.month").mean("time")
sla_anom = (sla_eq.groupby("time.month") - sla_clim).values
times = sla_eq.time.values
nt, nx = sla_anom.shape
dlon = float(lon_pac[1] - lon_pac[0])

print(f"Hovmöller: {nt} days × {nx} lon points, dlon={dlon}°")

# --- Step 0: Validate FFT sign convention ---
print("\n=== FFT sign convention test ===")
x_test = np.linspace(0, 2 * np.pi * 10, nx)
t_test = np.linspace(0, 2 * np.pi * 5, nt)
T_test, X_test = np.meshgrid(t_test, x_test, indexing="ij")
eastward_syn = np.cos(3 * X_test - 2 * T_test)
westward_syn = np.cos(3 * X_test + 2 * T_test)

for label, field in [("eastward", eastward_syn), ("westward", westward_syn)]:
    fft2 = np.fft.fft2(field)
    power = np.abs(fft2) ** 2
    freq_k = np.fft.fftfreq(nx)
    freq_w = np.fft.fftfreq(nt)
    KK, WW = np.meshgrid(freq_k, freq_w)
    e_q1 = np.sum(power[(WW > 0) & (KK > 0)])
    e_q3 = np.sum(power[(WW < 0) & (KK < 0)])
    e_q2 = np.sum(power[(WW > 0) & (KK < 0)])
    e_q4 = np.sum(power[(WW < 0) & (KK > 0)])
    print(f"  {label}: Q1(ω>0,k>0)={e_q1:.0f}, Q2(ω>0,k<0)={e_q2:.0f}, "
          f"Q3(ω<0,k<0)={e_q3:.0f}, Q4(ω<0,k>0)={e_q4:.0f}")

# --- Step 1: Interpolate NaN (not fill with 0) ---
data = sla_anom.copy()
for i in range(nt):
    row = data[i, :]
    nans = np.isnan(row)
    if nans.any() and not nans.all():
        good = ~nans
        data[i, nans] = np.interp(
            np.flatnonzero(nans), np.flatnonzero(good), row[good]
        )
    elif nans.all():
        data[i, :] = 0.0

nan_frac = np.isnan(sla_anom).sum() / sla_anom.size
print(f"\nNaN fraction before interp: {nan_frac:.4f}")

# --- Step 2: Remove linear trend ---
data = detrend(data, axis=0, type="linear")

# --- Step 3: Remove 90-day low-pass (ENSO background) ---
bg = uniform_filter1d(data, size=90, axis=0, mode="reflect")
data_hp = data - bg
print(f"After 90-day highpass: std reduced from {np.std(data):.4f} to {np.std(data_hp):.4f}")

# --- Step 4: Apply 2D Tukey taper ---
taper_t = tukey(nt, alpha=0.1)
taper_x = tukey(nx, alpha=0.1)
taper_2d = np.outer(taper_t, taper_x)
data_tapered = data_hp * taper_2d

# --- Step 5: 2D FFT ---
fft2d = np.fft.fft2(data_tapered)
power = np.abs(fft2d) ** 2
total_power = np.sum(power)

freq_k = np.fft.fftfreq(nx, d=dlon)
freq_w = np.fft.fftfreq(nt, d=1.0)
KK, WW = np.meshgrid(freq_k, freq_w)

with np.errstate(divide="ignore", invalid="ignore"):
    cp = np.where(KK != 0, WW / KK, 0)

# --- Step 6: Mode filters ---
# FFT sign convention (verified by synthetic test above):
#   eastward cos(kx - ωt) → energy in Q2(ω>0,k<0) + Q4(ω<0,k>0)
#   i.e. eastward = WW * KK < 0
#   westward cos(kx + ωt) → energy in Q1(ω>0,k>0) + Q3(ω<0,k<0)
#   i.e. westward = WW * KK > 0

# Eastward Kelvin: WW*KK < 0, phase speed 1.0-4.0 deg/day, period 10-200 days
kelvin_mask = (
    (WW * KK < 0) &
    (np.abs(cp) >= 1.0) & (np.abs(cp) <= 4.0) &
    (np.abs(WW) > 1 / 200) & (np.abs(WW) < 1 / 10)
)

# Westward Rossby: WW*KK > 0, phase speed 0.1-1.5 deg/day, period 20-200 days
rossby_mask = (
    (WW * KK > 0) &
    (np.abs(cp) >= 0.1) & (np.abs(cp) <= 1.5) &
    (np.abs(WW) > 1 / 200) & (np.abs(WW) < 1 / 20)
)

# TIW: period 15-40 days, wavelength 800-2500 km (~7-23°)
tiw_mask = (
    (np.abs(WW) > 1 / 40) & (np.abs(WW) < 1 / 15) &
    (np.abs(KK) > 1 / 23) & (np.abs(KK) < 1 / 7) &
    ~kelvin_mask & ~rossby_mask
)

# --- Step 7: Reconstruct filtered fields ---
def apply_filter(fft_data, mask):
    filtered = fft_data.copy()
    filtered[~mask] = 0
    return np.real(np.fft.ifft2(filtered))

kelvin = apply_filter(fft2d, kelvin_mask)
rossby = apply_filter(fft2d, rossby_mask)
tiw = apply_filter(fft2d, tiw_mask)
residual = data_tapered - kelvin - rossby - tiw

e_kelvin = np.sum(power[kelvin_mask]) / total_power * 100
e_rossby = np.sum(power[rossby_mask]) / total_power * 100
e_tiw = np.sum(power[tiw_mask]) / total_power * 100
e_resid = 100 - e_kelvin - e_rossby - e_tiw

print(f"\n=== Energy partition (after 90-day highpass + taper) ===")
print(f"  Kelvin:   {e_kelvin:.1f}%")
print(f"  Rossby:   {e_rossby:.1f}%")
print(f"  TIW:      {e_tiw:.1f}%")
print(f"  Residual: {e_resid:.1f}%")
print(f"  (Residual includes internal tides, submesoscale, noise, "
      f"and modes not captured by the three filters)")

# --- Step 8: Save ---
out_npz = DATA_DIR / "spectral_decomposition_v2.npz"
np.savez(out_npz,
         kelvin=kelvin, rossby=rossby, tiw=tiw, residual=residual,
         original=data_tapered, lon=lon_pac, times=times,
         e_kelvin=e_kelvin, e_rossby=e_rossby, e_tiw=e_tiw, e_resid=e_resid)
print(f"Saved: {out_npz}")

# --- Step 9: Figure ---
fig, axes = plt.subplots(2, 3, figsize=(16, 8))

panels = [
    (axes[0, 0], data_tapered, "Original (90d HP + taper)", "RdBu_r"),
    (axes[0, 1], kelvin, f"Kelvin ({e_kelvin:.1f}%)", "RdBu_r"),
    (axes[0, 2], rossby, f"Rossby ({e_rossby:.1f}%)", "RdBu_r"),
    (axes[1, 0], tiw, f"TIW ({e_tiw:.1f}%)", "RdBu_r"),
    (axes[1, 1], residual, f"Residual ({e_resid:.1f}%)", "RdBu_r"),
]

import matplotlib.dates as mdates
import pandas as pd
times_num = mdates.date2num(pd.to_datetime(times))

for ax, field, title, cmap in panels:
    vmax = np.percentile(np.abs(field), 99)
    ax.pcolormesh(lon_pac, times_num, field, cmap=cmap,
                  vmin=-vmax, vmax=vmax, shading="auto", rasterized=True)
    ax.set_title(title, fontsize=10)
    ax.yaxis_date()
    ax.yaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.yaxis.set_major_locator(mdates.MonthLocator(interval=4))
    ax.set_xlabel("Longitude (°E)")

# k-ω power spectrum
ax_kw = axes[1, 2]
freq_k_shift = np.fft.fftshift(freq_k)
freq_w_shift = np.fft.fftshift(freq_w)
power_shift = np.fft.fftshift(np.log10(power + 1))
ax_kw.pcolormesh(freq_k_shift, freq_w_shift, power_shift,
                 cmap="inferno", shading="auto", rasterized=True)
ax_kw.set_xlabel("Wavenumber (cpd)")
ax_kw.set_ylabel("Frequency (cpd)")
ax_kw.set_title("log₁₀ k-ω Power")
ax_kw.set_xlim(-0.15, 0.15)
ax_kw.set_ylim(-0.08, 0.08)
for c in [1.0, 2.0, 3.0]:
    kk = np.linspace(0.001, 0.15, 50)
    ax_kw.plot(kk, c * kk, "w--", linewidth=0.5, alpha=0.5)
    ax_kw.plot(-kk, -c * kk, "w--", linewidth=0.5, alpha=0.5)

fig.suptitle("P02 Spectral Decomposition v2 (improved: interp NaN, detrend, 90d HP, Tukey taper)",
             fontsize=11)
plt.tight_layout()
out_fig = FIG_DIR / "p2_spectral_decomposition_v2.png"
fig.savefig(out_fig, dpi=150, bbox_inches="tight")
plt.close()
print(f"Figure: {out_fig}")

ds.close()
