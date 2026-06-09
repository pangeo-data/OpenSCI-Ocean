"""Fig.6: Effective topological control parameter Lambda vs robustness metrics"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import os

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "pdf.fonttype": 42, "font.size": 7,
    "axes.spines.right": False, "axes.spines.top": False,
    "axes.linewidth": 0.6, "legend.frameon": False,
})

OUT = "/Users/zhulin/aitest/OpenSCI-Ocean/projects/p02/manuscript/figures"

# ⚠️ CONCEPTUAL SCHEMATIC — all data points are synthetic random numbers.
# Must be replaced with real GLORYS/Argo-derived Λ values before publication.
# Corrected Δω_eff = sqrt(β * c1) ≈ 7.6e-6 s⁻¹ (not 2.4e-6 as previously stated)
# where β = 2.3e-11 m⁻¹s⁻¹, c1 = 2.5 m/s
rng = np.random.default_rng(2026)

# Generate synthetic but physically motivated data points (SCHEMATIC ONLY)
# Each point = one event × one perturbation zone
zones = {
    "Gilbert Islands": {"n": 8, "lambda_range": (8.0, 20.0), "amp_range": (1.8, 3.5),
                        "color": "#27AE60", "marker": "o"},
    "Line Islands":    {"n": 8, "lambda_range": (6.0, 15.0), "amp_range": (1.5, 2.8),
                        "color": "#2980B9", "marker": "s"},
    "TIW zone":        {"n": 8, "lambda_range": (1.0, 4.0), "amp_range": (0.6, 1.1),
                        "color": "#E74C3C", "marker": "D"},
}

fig, axes = plt.subplots(1, 2, figsize=(7.09, 3.2))

# Panel (a): Lambda vs amplitude ratio
ax = axes[0]
all_lambda = []; all_amp = []
for zname, z in zones.items():
    lam = rng.uniform(z["lambda_range"][0], z["lambda_range"][1], z["n"])
    amp = rng.uniform(z["amp_range"][0], z["amp_range"][1], z["n"])
    # Add correlation: higher lambda → higher amp
    amp = amp * (0.7 + 0.3 * (lam - lam.min()) / (lam.max() - lam.min() + 0.1))
    ax.scatter(lam, amp, c=z["color"], marker=z["marker"], s=30, alpha=0.8,
              edgecolors="k", linewidths=0.3, label=zname, zorder=3)
    all_lambda.extend(lam); all_amp.extend(amp)

# Fit line
all_lambda = np.array(all_lambda); all_amp = np.array(all_amp)
from numpy.polynomial import polynomial as P
coeffs = P.polyfit(np.log(all_lambda), all_amp, 1)
x_fit = np.linspace(0.3, 9, 100)
y_fit = P.polyval(np.log(x_fit), coeffs)
ax.plot(x_fit, y_fit, "k--", linewidth=0.8, alpha=0.5)

# Threshold
ax.axvline(1.0, color="grey", linewidth=1.0, linestyle=":", alpha=0.7)
ax.axhline(1.0, color="grey", linewidth=0.6, linestyle="--", alpha=0.5)
ax.text(1.05, 3.2, "$\\Lambda_c \\sim 1$", fontsize=7, color="grey", style="italic")

# Shading
ax.axvspan(0.3, 1.0, alpha=0.06, color="red")
ax.axvspan(1.0, 9.0, alpha=0.06, color="green")
ax.text(0.55, 0.5, "breakdown", fontsize=6, color="#C0392B", ha="center",
        style="italic", alpha=0.7)
ax.text(4.5, 0.5, "protection", fontsize=6, color="#27AE60", ha="center",
        style="italic", alpha=0.7)

ax.set_xlabel("$\\Lambda = \\Delta\\omega_{\\mathrm{eff}} \\,/\\, \\delta\\omega_{\\mathrm{pert}}$", fontsize=8)
ax.set_ylabel("Amplitude ratio (dn/up)", fontsize=7)
ax.set_xlim(0.5, 25)
ax.set_ylim(0.3, 3.8)
ax.set_xscale("log")
ax.legend(fontsize=6, loc="upper left", handletextpad=0.3)
ax.text(0.02, 0.96, "a", transform=ax.transAxes, fontsize=10, fontweight="bold", va="top")

# Panel (b): Lambda estimates by scenario
ax2 = axes[1]
scenarios = ["Quiescent\nPacific", "Moderate\nTIW", "Strong\nTIW/eddy", "Cold tongue\nfront"]
lambda_vals = [15.0, 4.0, 1.5, 2.4]
lambda_err = [4.0, 1.2, 0.5, 0.8]
colors_bar = ["#27AE60", "#F39C12", "#E74C3C", "#E74C3C"]

bars = ax2.bar(range(len(scenarios)), lambda_vals, yerr=lambda_err,
               color=colors_bar, alpha=0.6, edgecolor="k", linewidth=0.4,
               capsize=3, error_kw={"linewidth": 0.6})
ax2.axhline(1.0, color="grey", linewidth=1.0, linestyle=":", alpha=0.7)
ax2.text(3.6, 1.1, "$\\Lambda_c \\sim 1$", fontsize=7, color="grey", style="italic")

ax2.set_xticks(range(len(scenarios)))
ax2.set_xticklabels(scenarios, fontsize=6)
ax2.set_ylabel("$\\Lambda$", fontsize=9)
ax2.set_ylim(0, 22)
ax2.text(0.02, 0.96, "b", transform=ax2.transAxes, fontsize=10, fontweight="bold", va="top")

plt.tight_layout(w_pad=1.5)
# Watermark both panels
for ax_w in axes:
    ax_w.text(0.5, 0.5, "SCHEMATIC\n(synthetic data)", transform=ax_w.transAxes,
             fontsize=9, ha="center", va="center", color="red", alpha=0.25,
             fontweight="bold", rotation=30)

fig.savefig(os.path.join(OUT, "fig6_lambda.pdf"), bbox_inches="tight")
fig.savefig(os.path.join(OUT, "fig6_lambda.png"), dpi=300, bbox_inches="tight")
plt.close()
print("Fig.6 saved (SCHEMATIC — synthetic data, not observations)")
