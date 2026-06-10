"""Fig.1: Theoretical framework and observational approach
Schematic figure showing: (a) Coriolis sign reversal + topological edge modes,
(b) SWOT observation geometry over equatorial Pacific with perturbation zones.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import numpy as np
import os

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "pdf.fonttype": 42, "font.size": 7,
    "axes.linewidth": 0.6, "legend.frameon": False,
})

OUT = "/Users/zhulin/aitest/OpenSCI-Ocean/projects/p02/manuscript/figures"

fig = plt.figure(figsize=(7.09, 5.5))

# === Panel (a): Dispersion relation + topological edge modes ===
ax_a = fig.add_axes([0.06, 0.52, 0.42, 0.44])

kx = np.linspace(-3, 3, 300)

# Poincaré bands (f-plane): ω = ±sqrt(f² + c²k²), normalized
f_norm = 1.0
omega_plus = np.sqrt(f_norm**2 + kx**2)
omega_minus = -np.sqrt(f_norm**2 + kx**2)

# Rossby band (β-plane approximation, simplified)
omega_rossby = -0.3 * kx / (1 + kx**2)

# Kelvin wave: ω = c*kx (fills upper gap)
kx_kelvin = np.linspace(0, 3, 100)
omega_kelvin = kx_kelvin * 0.8

# Yanai wave: mixed Rossby-gravity
kx_yanai = np.linspace(-2, 3, 100)
omega_yanai = 0.5 * (kx_yanai + np.sqrt(kx_yanai**2 + 4))
omega_yanai_neg = -0.5 * (-kx_yanai + np.sqrt(kx_yanai**2 + 4))

# Plot bands
ax_a.fill_between(kx, omega_plus, 3.5, alpha=0.08, color="#3498DB")
ax_a.fill_between(kx, omega_minus, -3.5, alpha=0.08, color="#3498DB")
ax_a.plot(kx, omega_plus, color="#2980B9", linewidth=1.2, label="Poincaré")
ax_a.plot(kx, omega_minus, color="#2980B9", linewidth=1.2)
ax_a.plot(kx, omega_rossby, color="#27AE60", linewidth=1.2, label="Rossby")

# Edge modes
ax_a.plot(kx_kelvin, omega_kelvin, color="#E74C3C", linewidth=2.0, label="Kelvin")
ax_a.plot(kx_yanai[kx_yanai > -1.5], omega_yanai[kx_yanai > -1.5] * 0.45,
          color="#E67E22", linewidth=2.0, label="Yanai")

# Gap annotation
ax_a.annotate("", xy=(3.2, f_norm), xytext=(3.2, 0.15),
             arrowprops=dict(arrowstyle="<->", color="grey", lw=0.8))
ax_a.text(3.35, 0.55, "$\\Delta\\omega$\ngap", fontsize=6, color="grey",
         ha="left", va="center")

# Chern numbers
ax_a.text(-2.5, 2.2, "$\\mathcal{C}_+ = +2$", fontsize=8, color="#2980B9",
         fontweight="bold", ha="center")
ax_a.text(-2.5, -2.2, "$\\mathcal{C}_- = -2$", fontsize=8, color="#2980B9",
         fontweight="bold", ha="center")
ax_a.text(-2.5, -0.15, "$\\mathcal{C}_0 = 0$", fontsize=7, color="#27AE60",
         ha="center")

ax_a.set_xlabel("Zonal wavenumber $k_x$", fontsize=7)
ax_a.set_ylabel("Frequency $\\omega$", fontsize=7)
ax_a.set_xlim(-3.5, 3.8)
ax_a.set_ylim(-3, 3)
ax_a.axhline(0, color="grey", linewidth=0.3)
ax_a.axvline(0, color="grey", linewidth=0.3)
ax_a.set_xticks([])
ax_a.set_yticks([])
ax_a.legend(fontsize=6, loc="upper left", handlelength=1.5)
ax_a.text(0.02, 0.96, "a", transform=ax_a.transAxes, fontsize=10,
         fontweight="bold", va="top")

# === Panel (b): Coriolis parameter sign reversal ===
ax_b = fig.add_axes([0.55, 0.52, 0.42, 0.44])

y = np.linspace(-30, 30, 200)
f_coriolis = 2 * 7.292e-5 * np.sin(np.radians(y))
f_norm_plot = f_coriolis / (2 * 7.292e-5)

ax_b.fill_between(y, 0, f_norm_plot, where=(f_norm_plot > 0),
                  alpha=0.15, color="#E74C3C")
ax_b.fill_between(y, 0, f_norm_plot, where=(f_norm_plot < 0),
                  alpha=0.15, color="#3498DB")
ax_b.plot(y, f_norm_plot, "k-", linewidth=1.5)
ax_b.axhline(0, color="grey", linewidth=0.5)
ax_b.axvline(0, color="grey", linewidth=0.5, linestyle=":")

ax_b.text(15, 0.35, "$f > 0$\nNorthern\nHemisphere", fontsize=6.5,
         ha="center", color="#C0392B")
ax_b.text(-15, -0.35, "$f < 0$\nSouthern\nHemisphere", fontsize=6.5,
         ha="center", color="#2471A3")
ax_b.text(2, 0.08, "Equator\n$f = 0$", fontsize=6, ha="left",
         color="grey", style="italic")

# Arrow showing edge modes at equator
ax_b.annotate("Kelvin/Yanai\nedge modes", xy=(0, 0), xytext=(12, -0.55),
             fontsize=6, color="#E74C3C", fontweight="bold",
             arrowprops=dict(arrowstyle="->", color="#E74C3C", lw=1.2),
             ha="center")

ax_b.set_xlabel("Latitude (°)", fontsize=7)
ax_b.set_ylabel("$f / 2\\Omega$", fontsize=7)
ax_b.set_xlim(-30, 30)
ax_b.set_ylim(-0.7, 0.7)
ax_b.text(0.02, 0.96, "b", transform=ax_b.transAxes, fontsize=10,
         fontweight="bold", va="top")

# === Panel (c): Study region map with perturbation zones ===
ax_c = fig.add_axes([0.06, 0.05, 0.90, 0.40])

# Simple equatorial Pacific map (no cartopy needed for schematic)
# Ocean background
ax_c.set_facecolor("#E8F4FD")

# Landmasses (simplified)
# Australia-PNG
ax_c.fill([130, 155, 155, 145, 130], [-10, -10, -2, 0, 0],
          color="#D5DBDB", edgecolor="#95A5A6", linewidth=0.5)
# Americas
ax_c.fill([275, 280, 280, 275], [-10, -10, 10, 10],
          color="#D5DBDB", edgecolor="#95A5A6", linewidth=0.5)

# Equator
ax_c.axhline(0, color="k", linewidth=0.8, linestyle="--", alpha=0.5)
ax_c.text(132, 0.5, "Equator", fontsize=5.5, color="k", alpha=0.6, style="italic")

# Equatorial waveguide
ax_c.fill_between([130, 280], -3, 3, alpha=0.1, color="#F39C12")
ax_c.text(205, 3.5, "Equatorial waveguide ($\\pm L_{eq}$)", fontsize=5.5,
         ha="center", color="#F39C12", style="italic")

# Kelvin wave arrow
ax_c.annotate("", xy=(265, 0), xytext=(155, 0),
             arrowprops=dict(arrowstyle="-|>", color="#E74C3C",
                            lw=2.5, mutation_scale=15))
ax_c.text(210, -1.5, "Kelvin wave (eastward)", fontsize=7,
         ha="center", color="#E74C3C", fontweight="bold")

# Perturbation zones
for lon, name, color, w in [(175, "Gilbert\nIslands", "#27AE60", 8),
                              (202, "Line\nIslands", "#2980B9", 8),
                              (240, "TIW\nzone", "#E74C3C", 30)]:
    rect = mpatches.FancyBboxPatch((lon - w/2, -8), w, 16,
                                    boxstyle="round,pad=0.5",
                                    facecolor=color, alpha=0.15,
                                    edgecolor=color, linewidth=1.0)
    ax_c.add_patch(rect)
    ax_c.text(lon, 7, name, fontsize=6, ha="center", va="bottom",
             color=color, fontweight="bold")

# SWOT swath illustration
for swot_lon in [160, 190, 220, 250]:
    ax_c.plot([swot_lon-0.5, swot_lon+0.5], [-8, 8], color="#8E44AD",
             linewidth=3, alpha=0.2)
ax_c.text(270, 8, "SWOT\nswaths", fontsize=5.5, color="#8E44AD",
         ha="center", style="italic")

# Mechanism annotation (V2: spectral matching, not amplitude)
ax_c.text(175, -9.5, "spectrally\nmismatched", fontsize=6, ha="center",
         color="#27AE60", fontweight="bold", linespacing=1.1)
ax_c.text(240, -9.5, "resonant\n$(k,\\omega)$ channel", fontsize=6, ha="center",
         color="#E74C3C", fontweight="bold", linespacing=1.1)

ax_c.set_xlabel("Longitude (°E)", fontsize=7)
ax_c.set_ylabel("Latitude (°N)", fontsize=7)
ax_c.set_xlim(128, 282)
ax_c.set_ylim(-11, 11)
ax_c.text(0.01, 0.96, "c", transform=ax_c.transAxes, fontsize=10,
         fontweight="bold", va="top")

fig.savefig(os.path.join(OUT, "fig1_framework.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(OUT, "fig1_framework.png"), dpi=300, bbox_inches="tight")
plt.close()
print("Fig.1 saved")
