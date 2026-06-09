"""Fig.6: Real Λ from GLORYS12 vs amplitude retention from ray-following."""
import json
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "pdf.fonttype": 42, "font.size": 7,
    "axes.spines.right": False, "axes.spines.top": False,
    "axes.linewidth": 0.6, "legend.frameon": False,
})

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(BASE, "manuscript", "figures")

with open(os.path.join(BASE, "data", "glorys", "lambda_event_zone.json")) as f:
    lambda_data = json.load(f)

with open(os.path.join(BASE, "data", "duacs", "robustness_metrics_v2.json")) as f:
    rob_data = json.load(f)

MIN_RMS_UP = 0.01
rob_kelvin = {(r["event"], r["zone"]): r for r in rob_data["kelvin"]
              if r["rms_up"] > MIN_RMS_UP}

zone_colors = {
    "Gilbert Islands": "#27AE60",
    "Line Islands": "#2980B9",
    "TIW zone": "#E74C3C",
}
zone_markers = {
    "Gilbert Islands": "o",
    "Line Islands": "s",
    "TIW zone": "D",
}

fig, axes = plt.subplots(1, 2, figsize=(7.09, 3.2))

# Panel (a): Λ vs amplitude ratio
ax = axes[0]
for ld in lambda_data:
    key = (ld["event_id"], ld["zone"])
    if key not in rob_kelvin:
        continue
    rob = rob_kelvin[key]
    ax.scatter(ld["lambda"], rob["amp_ratio"],
               c=zone_colors[ld["zone"]], marker=zone_markers[ld["zone"]],
               s=35, alpha=0.8, edgecolors="k", linewidths=0.3,
               label=ld["zone"], zorder=3)

handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys(), fontsize=6, loc="upper left")

ax.axhline(1.0, color="grey", linewidth=0.6, linestyle="--", alpha=0.5)
ax.set_xlabel(r"$\Lambda = \Delta\omega_{\mathrm{eff}} / \delta\omega_{\mathrm{pert}}$", fontsize=8)
ax.set_ylabel("Amplitude ratio (dn/up)", fontsize=7)
ax.set_title("(a) Real GLORYS-derived $\\Lambda$ vs robustness", fontsize=8)
ax.text(0.02, 0.96, "a", transform=ax.transAxes, fontsize=10, fontweight="bold", va="top")

# Panel (b): Λ distribution by zone
ax2 = axes[1]
for i, (zone, col) in enumerate(zone_colors.items()):
    vals = [ld["lambda"] for ld in lambda_data if ld["zone"] == zone]
    if vals:
        bp = ax2.boxplot([vals], positions=[i], widths=0.5, patch_artist=True,
                         medianprops=dict(color="k", linewidth=1),
                         whiskerprops=dict(linewidth=0.6),
                         capprops=dict(linewidth=0.6))
        bp["boxes"][0].set_facecolor(col)
        bp["boxes"][0].set_alpha(0.35)
        rng = np.random.default_rng(42)
        jitter = rng.normal(0, 0.05, len(vals))
        ax2.scatter(np.full(len(vals), i) + jitter, vals,
                    c=col, s=15, alpha=0.7, zorder=3, edgecolors="none")

ax2.axhline(1.0, color="grey", linewidth=1.0, linestyle=":", alpha=0.7)
ax2.text(2.4, 1.15, "$\\Lambda_c \\sim 1$", fontsize=7, color="grey", style="italic")
ax2.set_xticks(range(3))
ax2.set_xticklabels(["Gilbert\nIslands", "Line\nIslands", "TIW\nzone"], fontsize=6)
ax2.set_ylabel("$\\Lambda$", fontsize=9)
ax2.set_title("(b) $\\Lambda$ distribution by perturbation zone", fontsize=8)
ax2.text(0.02, 0.96, "b", transform=ax2.transAxes, fontsize=10, fontweight="bold", va="top")

plt.tight_layout(w_pad=1.5)
fig.savefig(os.path.join(OUT, "fig6_lambda.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(OUT, "fig6_lambda.png"), dpi=300, bbox_inches="tight")
plt.close()
print("Fig.6 saved (REAL GLORYS data)")
