"""
P1-01: Build equatorial SSH anomaly Hovmöller diagram
Core Phase 1 feasibility test: can we see eastward-propagating Kelvin wave events?

Input: DUACS L4 daily SSH (SLA), equatorial Pacific
Method: Average SLA over 2°S-2°N band, plot longitude vs time
Expected: eastward-propagating signals with phase speed ~2.5 m/s (~220 km/day)
"""
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os

DATA_DIR = "/Users/zhulin/aitest/OpenSCI-Ocean/projects/p02/data/duacs"
FIG_DIR = "/Users/zhulin/aitest/OpenSCI-Ocean/projects/p02/figures"
os.makedirs(FIG_DIR, exist_ok=True)

ds = xr.open_dataset(os.path.join(DATA_DIR, "duacs_eqpac_daily_2023_2025.nc"))

sla = ds["sla"]

# Sort longitude to be continuous: remap to 0-360 for Pacific view
lon = sla.longitude.values
lon_360 = np.where(lon < 0, lon + 360, lon)
sort_idx = np.argsort(lon_360)
sla_sorted = sla.isel(longitude=sort_idx)
lon_sorted = lon_360[sort_idx]

# Select equatorial Pacific: 130E-280E (=80W), within 2S-2N
mask_lon = (lon_sorted >= 130) & (lon_sorted <= 280)
sla_pac = sla_sorted.isel(longitude=mask_lon)
lon_pac = lon_sorted[mask_lon]

# Average over 2S-2N equatorial band
sla_eq = sla_pac.sel(latitude=slice(-2, 2)).mean(dim="latitude")

# Remove seasonal cycle (climatological monthly mean)
sla_clim = sla_eq.groupby("time.month").mean("time")
sla_anom = sla_eq.groupby("time.month") - sla_clim

# --- Plot Hovmöller ---
fig, axes = plt.subplots(2, 1, figsize=(14, 12), sharex=False)

# Panel (a): Full time series
ax = axes[0]
time_vals = sla_anom.time.values
lon_vals = lon_pac

pcm = ax.pcolormesh(
    lon_vals, time_vals, sla_anom.values,
    cmap="RdBu_r", vmin=-0.15, vmax=0.15, shading="auto"
)
ax.set_ylabel("Time")
ax.set_xlabel("Longitude (°E)")
ax.set_title("(a) Equatorial Pacific SSH Anomaly Hovmöller (2°S–2°N mean)")
ax.yaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax.yaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.colorbar(pcm, ax=ax, label="SLA (m)", shrink=0.8)

# Add reference slope for Kelvin wave speed ~2.5 m/s
# 2.5 m/s = 216 km/day. At equator, 1° ≈ 111 km, so ~1.95 °/day
# Over 150° longitude, takes ~77 days
kelvin_speed_deg_per_day = 2.5 * 86400 / 111000  # ~1.95 deg/day
t0_idx = 100  # arbitrary start
t0 = time_vals[t0_idx]
t1 = time_vals[t0_idx + 70]
lon0, lon1 = 150, 150 + kelvin_speed_deg_per_day * 70
ax.plot([lon0, lon1], [t0, t1], 'k--', linewidth=2, label=f"c = 2.5 m/s")
ax.legend(loc="lower right", fontsize=10)

# Panel (b): Zoom into a 6-month window to see individual events
ax2 = axes[1]
t_start = np.datetime64("2024-01-01")
t_end = np.datetime64("2024-07-01")
sla_zoom = sla_anom.sel(time=slice(t_start, t_end))

pcm2 = ax2.pcolormesh(
    lon_vals, sla_zoom.time.values, sla_zoom.values,
    cmap="RdBu_r", vmin=-0.15, vmax=0.15, shading="auto"
)
ax2.set_ylabel("Time")
ax2.set_xlabel("Longitude (°E)")
ax2.set_title("(b) Zoom: 2024 Jan–Jun — identifying Kelvin wave candidates")
ax2.yaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
ax2.yaxis.set_major_locator(mdates.MonthLocator())
plt.colorbar(pcm2, ax=ax2, label="SLA (m)", shrink=0.8)

# Reference slopes
for t_offset in [10, 40, 70, 100, 130]:
    if t_offset + 70 < len(sla_zoom.time):
        t0 = sla_zoom.time.values[t_offset]
        t1 = sla_zoom.time.values[t_offset + 70]
        ax2.plot([150, 150 + kelvin_speed_deg_per_day * 70], [t0, t1],
                 'k--', linewidth=0.8, alpha=0.5)

plt.tight_layout()
out_path = os.path.join(FIG_DIR, "p1_hovmoller_equatorial_ssh.png")
plt.savefig(out_path, dpi=150, bbox_inches="tight")
plt.close()
print(f"Saved: {out_path}")

# Print some statistics
print(f"\nData summary:")
print(f"  Time range: {str(time_vals[0])[:10]} to {str(time_vals[-1])[:10]}")
print(f"  Longitude range: {lon_pac[0]:.1f}°E to {lon_pac[-1]:.1f}°E")
print(f"  SLA range: {float(sla_anom.min()):.3f} to {float(sla_anom.max()):.3f} m")
print(f"  SLA std: {float(sla_anom.std()):.3f} m")

ds.close()
