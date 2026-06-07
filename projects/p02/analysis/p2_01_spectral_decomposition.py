"""
P2-01: Spectral decomposition of equatorial SSH — separate eastward/westward modes
Traditional method (wavenumber-frequency filtering) as primary approach.

Method: 2D FFT on Hovmöller (time-longitude) → filter by propagation direction
- Eastward (k>0, ω>0): Kelvin wave band
- Westward (k<0, ω<0): Rossby wave band
- TIW band: period 20-40 days, wavelength 1000-2000 km

Output: separated SSH fields for Kelvin, Rossby, TIW + residual
"""
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

DATA_DIR = "/Users/zhulin/aitest/OpenSCI-Ocean/projects/p02/data/duacs"
FIG_DIR = "/Users/zhulin/aitest/OpenSCI-Ocean/projects/p02/figures"

ds = xr.open_dataset(os.path.join(DATA_DIR, "duacs_eqpac_daily_2023_2025.nc"))
sla = ds["sla"]

# Remap to 0-360 Pacific
lon = sla.longitude.values
lon_360 = np.where(lon < 0, lon + 360, lon)
sort_idx = np.argsort(lon_360)
sla_sorted = sla.isel(longitude=sort_idx)
lon_sorted = lon_360[sort_idx]

mask_lon = (lon_sorted >= 130) & (lon_sorted <= 280)
sla_pac = sla_sorted.isel(longitude=mask_lon)
lon_pac = lon_sorted[mask_lon]

sla_eq = sla_pac.sel(latitude=slice(-2, 2)).mean(dim="latitude")
sla_clim = sla_eq.groupby("time.month").mean("time")
sla_anom = (sla_eq.groupby("time.month") - sla_clim).values  # (time, lon)

times = sla_eq.time.values
nt, nx = sla_anom.shape

# Fill NaN with 0 for FFT
data = np.nan_to_num(sla_anom, nan=0.0)

# 2D FFT
fft2d = np.fft.fft2(data)
fft2d_shift = np.fft.fftshift(fft2d)

# Frequency axes
freq_t = np.fft.fftshift(np.fft.fftfreq(nt, d=1.0))  # cycles per day
freq_x = np.fft.fftshift(np.fft.fftfreq(nx, d=0.25))  # cycles per degree

# Wavenumber-frequency spectrum (power)
power = np.abs(fft2d_shift) ** 2

# Define mode filters
# Eastward propagating (Kelvin-like): positive k, positive ω (or negative k, negative ω in FFT convention)
# In shifted FFT: center is (0,0)
ky, kx = np.meshgrid(freq_t, freq_x, indexing='ij')

# Phase speed in deg/day: c = ω/k (where ω in cpd, k in cpd/deg → c in deg/day)
# Kelvin wave: c ~ 1.5-3.0 deg/day (1.7-3.4 m/s)
# Rossby wave: c ~ -0.2 to -1.0 deg/day (westward)

# Kelvin filter: eastward, phase speed 1.0-4.0 deg/day, period > 10 days
kelvin_mask = np.zeros_like(power, dtype=bool)
with np.errstate(divide='ignore', invalid='ignore'):
    cp = np.where(kx != 0, ky / kx, 0)  # phase speed
    # Eastward: kx > 0 and ky > 0 (or kx < 0 and ky < 0)
    eastward = (kx * ky) > 0
    kelvin_speed = (np.abs(cp) >= 1.0) & (np.abs(cp) <= 4.0)
    kelvin_period = np.abs(ky) < 1/10  # period > 10 days
    kelvin_mask = eastward & kelvin_speed & kelvin_period & (np.abs(ky) > 1/200)  # exclude very low freq

# Rossby filter: westward, phase speed 0.1-1.5 deg/day, period > 20 days
rossby_mask = np.zeros_like(power, dtype=bool)
westward = (kx * ky) < 0
rossby_speed = (np.abs(cp) >= 0.1) & (np.abs(cp) <= 1.5)
rossby_period = np.abs(ky) < 1/20  # period > 20 days
rossby_mask = westward & rossby_speed & rossby_period & (np.abs(ky) > 1/200)

# TIW filter: period 15-40 days, wavelength 800-2500 km (~7-22 deg)
tiw_mask = np.zeros_like(power, dtype=bool)
tiw_period = (np.abs(ky) >= 1/40) & (np.abs(ky) <= 1/15)
tiw_wavelength = (np.abs(kx) >= 1/22) & (np.abs(kx) <= 1/7)
tiw_mask = tiw_period & tiw_wavelength & westward  # TIW propagates westward

# Apply filters and inverse FFT
def apply_filter(fft_shifted, mask):
    filtered = fft_shifted * mask
    return np.real(np.fft.ifft2(np.fft.ifftshift(filtered)))

kelvin_field = apply_filter(fft2d_shift, kelvin_mask)
rossby_field = apply_filter(fft2d_shift, rossby_mask)
tiw_field = apply_filter(fft2d_shift, tiw_mask)
residual = data - kelvin_field - rossby_field - tiw_field

# Save decomposed fields
np.savez(
    os.path.join(DATA_DIR, "spectral_decomposition.npz"),
    kelvin=kelvin_field, rossby=rossby_field, tiw=tiw_field,
    residual=residual, original=data,
    lon=lon_pac, times=times,
)
print("Decomposition saved.")

# Energy fractions
e_total = np.nansum(data**2)
e_kelvin = np.nansum(kelvin_field**2)
e_rossby = np.nansum(rossby_field**2)
e_tiw = np.nansum(tiw_field**2)
e_resid = np.nansum(residual**2)

print(f"\nEnergy fractions:")
print(f"  Kelvin (eastward): {e_kelvin/e_total*100:.1f}%")
print(f"  Rossby (westward): {e_rossby/e_total*100:.1f}%")
print(f"  TIW:               {e_tiw/e_total*100:.1f}%")
print(f"  Residual:          {e_resid/e_total*100:.1f}%")

# Plot 4-panel decomposition
fig, axes = plt.subplots(4, 1, figsize=(14, 16), sharex=True, sharey=True)
titles = ["(a) Kelvin wave (eastward, c=1-4 °/day)",
          "(b) Rossby wave (westward, c=0.1-1.5 °/day)",
          "(c) TIW (westward, T=15-40d, λ=800-2500km)",
          "(d) Residual"]
fields = [kelvin_field, rossby_field, tiw_field, residual]
energies = [e_kelvin, e_rossby, e_tiw, e_resid]

for ax, title, field, energy in zip(axes, titles, fields, energies):
    pcm = ax.pcolormesh(lon_pac, times, field, cmap="RdBu_r",
                        vmin=-0.08, vmax=0.08, shading="auto")
    ax.set_title(f"{title}  [{energy/e_total*100:.1f}% energy]", fontsize=11)
    ax.set_ylabel("Time")
    ax.yaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.yaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.colorbar(pcm, ax=ax, label="SLA (m)", shrink=0.8)

axes[-1].set_xlabel("Longitude (°E)")
plt.suptitle("Spectral Decomposition of Equatorial Pacific SSH", fontsize=13, y=1.01)
plt.tight_layout()
out_path = os.path.join(FIG_DIR, "p2_spectral_decomposition.png")
plt.savefig(out_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Figure saved: {out_path}")

ds.close()
