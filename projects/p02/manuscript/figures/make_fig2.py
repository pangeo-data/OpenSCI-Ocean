"""
Fig.2: SWOT-observed equatorial Kelvin wave events
Nature Communications format, double-column (180 mm = 7.09 in)

Panels:
  (a) Equatorial Hovmöller with detected event rays
  (b) SWOT meridional SSH profile vs theoretical Gaussian
  (c) Amplitude retention by perturbation zone
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import xarray as xr
import json
import os
from scipy.ndimage import uniform_filter1d

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "font.size": 7,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.6,
    "legend.frameon": False,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "xtick.major.size": 3,
    "ytick.major.size": 3,
})

BASE = "/Users/zhulin/aitest/OpenSCI-Ocean/projects/p02"
OUT = os.path.join(BASE, "manuscript", "figures")
os.makedirs(OUT, exist_ok=True)

# --- Load data ---
ds = xr.open_dataset(os.path.join(BASE, "data/duacs/duacs_eqpac_daily_2023_2025.nc"))
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

with open(os.path.join(BASE, "data/kelvin_event_catalog.json")) as f:
    events = json.load(f)

with open(os.path.join(BASE, "data/swot/swot_meridional_profile.json")) as f:
    swot = json.load(f)

ds.close()

# --- Colors ---
COL_KELVIN = "#C0392B"
COL_CONTROL = "#2980B9"
COL_THEORY = "#E74C3C"
COL_SWOT = "#2C3E50"
COL_GILBERT = "#27AE60"
COL_LINE = "#2980B9"
COL_TIW = "#E74C3C"

# --- Figure: 3 panels ---
fig = plt.figure(figsize=(7.09, 6.5))

gs = fig.add_gridspec(2, 2, height_ratios=[1.2, 1],
                      hspace=0.35, wspace=0.32,
                      left=0.08, right=0.95, top=0.96, bottom=0.08)

# === Panel (a): Hovmöller (spans full top row) ===
ax_a = fig.add_subplot(gs[0, :])

# Convert datetime64 to matplotlib date numbers for uniform Y axis
import pandas as pd
times_dt = pd.to_datetime(times)
times_num = mdates.date2num(times_dt)

pcm = ax_a.pcolormesh(lon_pac, times_num, sla_anom,
                       cmap="RdBu_r", vmin=-0.15, vmax=0.15,
                       shading="auto", rasterized=True)

for i, e in enumerate(events):
    t0 = mdates.date2num(pd.Timestamp(e["start"]))
    t1 = mdates.date2num(pd.Timestamp(e["end"]))
    ax_a.plot([e["lon0"], e["lon1"]], [t0, t1],
             color="k", linewidth=1.2, alpha=0.8, solid_capstyle="round")

# Reference slope
t_ref = mdates.date2num(pd.Timestamp("2023-02-15"))
t_ref_end = mdates.date2num(pd.Timestamp("2023-02-15") + pd.Timedelta(days=60))
kelvin_speed = 1.95
ax_a.plot([140, 140 + kelvin_speed * 60],
         [t_ref, t_ref_end],
         "k--", linewidth=0.8, alpha=0.6)
ax_a.text(140 + kelvin_speed * 62, t_ref_end - 5,
         "c = 2.5 m s$^{-1}$", fontsize=6, ha="left", va="center",
         style="italic")

# Perturbation zone markers
for lon_c, name, col in [(175, "Gilbert\nIs.", COL_GILBERT),
                          (202, "Line\nIs.", COL_LINE),
                          (240, "TIW", COL_TIW)]:
    ax_a.axvline(lon_c, color=col, linewidth=0.6, linestyle=":", alpha=0.6)
    ax_a.text(lon_c, times_num[-1] + 15, name,
             fontsize=5.5, ha="center", va="bottom", color=col, fontweight="bold")

ax_a.set_xlabel("Longitude (°E)", fontsize=7)
ax_a.set_ylabel("Time", fontsize=7)
ax_a.yaxis_date()
ax_a.yaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
ax_a.yaxis.set_major_locator(mdates.MonthLocator(interval=3))
ax_a.set_xlim(130, 280)
ax_a.set_ylim(times_num[0], times_num[-1])

cb = plt.colorbar(pcm, ax=ax_a, shrink=0.7, aspect=25, pad=0.02)
cb.set_label("SLA (m)", fontsize=6.5)
cb.ax.tick_params(labelsize=6)

ax_a.text(0.02, 0.96, "a", transform=ax_a.transAxes,
         fontsize=10, fontweight="bold", va="top", ha="left")

# === Panel (b): SWOT meridional profile ===
ax_b = fig.add_subplot(gs[1, 0])

lat_swot = np.array(swot["lat"])
ssha_raw = np.array([x if x is not None else np.nan for x in swot["ssha_meridional"]])
valid = ~np.isnan(ssha_raw)
ssha_smooth = np.full_like(ssha_raw, np.nan)
ssha_smooth[valid] = uniform_filter1d(ssha_raw[valid], size=20)

y_th = np.linspace(-10, 10, 200)
L_eq = 3.0
gauss = np.nanmax(ssha_smooth) * np.exp(-y_th**2 / (2 * L_eq**2))

ax_b.fill_between(lat_swot, 0, ssha_raw, alpha=0.08, color=COL_SWOT)
ax_b.plot(lat_swot, ssha_smooth, color=COL_SWOT, linewidth=1.2,
          label="SWOT KaRIn")
ax_b.plot(y_th, gauss, color=COL_THEORY, linewidth=1.0, linestyle="--",
          label=f"Gaussian ($L_{{eq}}$ = {L_eq}°)")
ax_b.axhline(0, color="grey", linewidth=0.4)
ax_b.axvline(0, color="grey", linewidth=0.4, linestyle=":")
ax_b.set_xlabel("Latitude (°N)", fontsize=7)
ax_b.set_ylabel("SSHA (m)", fontsize=7)
ax_b.set_xlim(-10, 10)
ax_b.set_ylim(-0.01, 0.22)
ax_b.legend(fontsize=6, loc="upper right")

ax_b.text(0.02, 0.96, "b", transform=ax_b.transAxes,
         fontsize=10, fontweight="bold", va="top", ha="left")

# === Panel (c): Amplitude retention boxplot ===
ax_c = fig.add_subplot(gs[1, 1])

# ⚠️ PLACEHOLDER — hardcoded values from initial AI prototype.
# Must be replaced with real data from robustness_metrics.json or
# recomputed ray-following amplitude ratios before any publication.
gilbert = [2.65, 3.1, 2.2, 1.8, 3.5, 2.9, 2.4, 2.0]
line_is = [2.13, 1.8, 2.5, 1.9, 2.3, 2.0, 2.1, 1.7]
tiw = [0.88, 0.92, 0.75, 0.95, 0.82, 0.90, 0.85, 0.93]

bp = ax_c.boxplot([gilbert, line_is, tiw],
                   tick_labels=["Gilbert\nIslands", "Line\nIslands", "TIW\nzone"],
                   patch_artist=True, widths=0.55,
                   medianprops=dict(color="k", linewidth=1),
                   whiskerprops=dict(linewidth=0.6),
                   capprops=dict(linewidth=0.6),
                   flierprops=dict(markersize=3))

colors_box = [COL_GILBERT, COL_LINE, COL_TIW]
for patch, color in zip(bp["boxes"], colors_box):
    patch.set_facecolor(color)
    patch.set_alpha(0.35)
    patch.set_edgecolor(color)

for i, (data, color) in enumerate(zip([gilbert, line_is, tiw], colors_box)):
    jitter = np.random.default_rng(42).normal(0, 0.06, len(data))
    ax_c.scatter(np.full(len(data), i + 1) + jitter, data,
                color=color, s=12, alpha=0.7, zorder=3, edgecolors="none")

ax_c.axhline(1.0, color="grey", linewidth=0.6, linestyle="--")
ax_c.text(3.35, 1.02, "no change", fontsize=5.5, va="bottom", ha="right",
         color="grey", style="italic")

ax_c.set_ylabel("Amplitude ratio (downstream / upstream)", fontsize=7)
ax_c.set_ylim(0.4, 4.0)

# Watermark: data source warning
ax_c.text(0.5, 0.5, "PLACEHOLDER\n(hardcoded data)", transform=ax_c.transAxes,
         fontsize=8, ha="center", va="center", color="red", alpha=0.3,
         fontweight="bold", rotation=30)

ax_c.text(0.02, 0.96, "c", transform=ax_c.transAxes,
         fontsize=10, fontweight="bold", va="top", ha="left")

# --- Save ---
fig.savefig(os.path.join(OUT, "fig2_kelvin_events.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(OUT, "fig2_kelvin_events.png"), dpi=300, bbox_inches="tight")
plt.close()
print(f"Saved: {OUT}/fig2_kelvin_events.pdf + .png")
