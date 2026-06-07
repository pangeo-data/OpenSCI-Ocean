"""Fig.5: Spectral decomposition of equatorial SSH into wave modes"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "pdf.fonttype": 42, "font.size": 7,
    "axes.spines.right": False, "axes.spines.top": False,
    "axes.linewidth": 0.6, "legend.frameon": False,
})

BASE = "/Users/zhulin/aitest/OpenSCI-Ocean/projects/p02"
OUT = os.path.join(BASE, "manuscript", "figures")
dec = np.load(os.path.join(BASE, "data/duacs/spectral_decomposition.npz"), allow_pickle=True)

kelvin = dec["kelvin"]; rossby = dec["rossby"]; tiw = dec["tiw"]
residual = dec["residual"]; original = dec["original"]
lon = dec["lon"]; times = dec["times"]

e_total = np.nansum(original**2)
energies = [np.nansum(f**2)/e_total*100 for f in [kelvin, rossby, tiw, residual]]

fig, axes = plt.subplots(4, 1, figsize=(7.09, 7.5), sharex=True, sharey=True)
titles = [f"a  Kelvin (eastward, c = 1--4 deg day$^{{-1}}$) [{energies[0]:.1f}%]",
          f"b  Rossby (westward, c = 0.1--1.5 deg day$^{{-1}}$) [{energies[1]:.1f}%]",
          f"c  TIW (T = 15--40 d, $\\lambda$ = 800--2500 km) [{energies[2]:.1f}%]",
          f"d  Residual (low-frequency + noise) [{energies[3]:.1f}%]"]
fields = [kelvin, rossby, tiw, residual]
cmaps = ["Reds", "Blues", "Oranges", "RdBu_r"]

for ax, title, field, cmap in zip(axes, titles, fields, cmaps):
    vmax = 0.06 if cmap != "RdBu_r" else 0.08
    vmin = -vmax if cmap == "RdBu_r" else 0
    data_plot = field if cmap == "RdBu_r" else np.abs(field)
    pcm = ax.pcolormesh(lon, times, data_plot, cmap=cmap,
                        vmin=vmin, vmax=vmax, shading="auto", rasterized=True)
    ax.text(0.01, 0.92, title, transform=ax.transAxes, fontsize=7,
            fontweight="bold", va="top", ha="left",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", alpha=0.8, lw=0))
    ax.set_ylabel("Time", fontsize=7)
    ax.yaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.yaxis.set_major_locator(mdates.MonthLocator(interval=4))
    cb = plt.colorbar(pcm, ax=ax, shrink=0.6, aspect=20, pad=0.015)
    cb.ax.tick_params(labelsize=5.5)
    cb.set_label("SLA (m)", fontsize=6)

axes[-1].set_xlabel("Longitude (°E)", fontsize=7)
axes[0].set_xlim(130, 280)
plt.tight_layout(h_pad=0.3)
fig.savefig(os.path.join(OUT, "fig5_spectral.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(OUT, "fig5_spectral.png"), dpi=300, bbox_inches="tight")
plt.close()
print("Fig.5 saved")
