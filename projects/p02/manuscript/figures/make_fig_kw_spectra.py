"""Fig (k,omega): vorticity wavenumber-frequency spectra showing the
resonance mechanism directly.

Three representative event-zone pairs:
  a - Line Islands, KE07 (winter): wake enstrophy outside the window
  b - TIW zone, KE02 (boreal spring, TIWs suppressed): window nearly empty
  c - TIW zone, KE07 (winter, TIWs active): strong power inside the window

Spectra are computed exactly as in p4_03 (per-latitude 2D FFT of zeta(t,x),
Kelvin-footprint power weighting), then folded to the f > 0 half plane with
signed zonal wavenumber (negative = westward). The dashed box marks the
resonant window (westward, 700-2500 km, 15-50 d); the grey line marks the
Kelvin dispersion omega = c1 * k (eastward, c1 = 2.5 m/s).
"""
import json
import os

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import yaml

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "pdf.fonttype": 42, "font.size": 7,
    "axes.linewidth": 0.6,
})

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(BASE, "manuscript", "figures")
GLORYS_DIR = os.path.join(BASE, "data", "glorys")

with open(os.path.join(BASE, "config.yaml")) as f:
    cfg = yaml.safe_load(f)
C1 = float(cfg["physics"]["c1"])
BETA = 2.3e-11
L_EQ_DEG = np.sqrt(C1 / BETA) / 111000

LAM_MIN_KM, LAM_MAX_KM = 700, 2500
T_MIN_D, T_MAX_D = 15, 50

PANELS = [
    ("KE07", "Line_Islands", "Line Islands\nKE07 (Dec)"),
    ("KE02", "TIW_zone", "TIW zone\nKE02 (Mar, TIWs off)"),
    ("KE07", "TIW_zone", "TIW zone\nKE07 (Dec, TIWs on)"),
]

with open(os.path.join(GLORYS_DIR, "lambda_v2_resonance.json")) as f:
    RES = {(r["event_id"], r["zone"]): r["resonant_fraction"] for r in json.load(f)}
ZONE_NAME = {"Line_Islands": "Line Islands", "TIW_zone": "TIW zone"}


def folded_spectrum(event_id, zone_tag):
    """Kelvin-footprint power-weighted zeta spectrum, folded to f>0."""
    ds = xr.open_dataset(os.path.join(GLORYS_DIR, f"glorys_uv_{event_id}_{zone_tag}.nc"))
    sub = ds.isel(depth=0) if "depth" in ds.dims else ds
    lat_name = "latitude" if "latitude" in sub.dims else "lat"
    lon_name = "longitude" if "longitude" in sub.dims else "lon"
    lats = sub[lat_name].values
    uo, vo = sub["uo"].values, sub["vo"].values
    ds.close()

    dxy = 0.083 * 111000
    zeta = np.gradient(vo, dxy, axis=-1) - np.gradient(uo, dxy, axis=-2)
    nt, ny, nx = zeta.shape

    ht = np.hanning(nt)[:, None]
    hx = np.hanning(nx)[None, :]
    norm = np.sqrt(np.mean(ht**2) * np.mean(hx**2))
    w2 = np.exp(-((lats / L_EQ_DEG) ** 2))

    P = np.zeros((nt, nx))
    for j in range(ny):
        z = zeta[:, j, :]
        z = np.nan_to_num(z - np.nanmean(z))
        Z = np.fft.fft2(z * ht * hx) / norm
        P += w2[j] * (np.abs(Z) ** 2) / (nt * nx) ** 2
    P /= w2.sum()

    freq = np.fft.fftfreq(nt, 1.0)            # cycles/day
    wav = np.fft.fftfreq(nx, dxy / 1000.0)    # cycles/km

    # fold: keep F > 0; display k with westward negative.
    # numpy component exp(2pi i(Ft+Kx)) has phase speed -F/K, so for F>0
    # K>0 is westward -> display k_disp = -K
    fpos = freq > 0
    f_disp = freq[fpos]
    order = np.argsort(-wav)                  # so k_disp = -K is ascending
    k_disp = -wav[order]
    P_disp = P[fpos][:, order]
    return f_disp, k_disp * 1000.0, P_disp    # k in cycles/1000 km


fig, axes = plt.subplots(1, 3, figsize=(7.09, 2.7), sharey=True)
specs = [folded_spectrum(e, z) for e, z, _ in PANELS]

for ax, (f, k, P), (ev, zone, title) in zip(axes, specs, PANELS):
    # show within the displayed range, normalized per panel; cross-panel
    # comparison is carried by the annotated resonant fraction
    sel_f = (f >= 0.012) & (f <= 0.1)
    Pn = P[sel_f] / np.nanmax(P[sel_f])
    pm = ax.pcolormesh(k, f[sel_f], np.clip(Pn, 1e-3, None), shading="auto",
                       norm=mpl.colors.LogNorm(vmin=1e-3, vmax=1.0),
                       cmap="magma", rasterized=True)
    k1, k2 = -1000.0 / LAM_MIN_KM, -1000.0 / LAM_MAX_KM
    f1, f2 = 1.0 / T_MAX_D, 1.0 / T_MIN_D
    ax.add_patch(mpl.patches.Rectangle((k1, f1), k2 - k1, f2 - f1,
                                       fill=False, edgecolor="cyan", ls="--", lw=1.3))
    kk = np.linspace(0, 2.0, 50)
    f_kelvin = C1 * kk * 86400.0 / 1e6  # c1[m/s] * k[c/1000km] -> cycles/day
    ax.plot(kk, f_kelvin, color="w", lw=0.8, alpha=0.7)
    ax.set_xlim(-2, 2)
    ax.set_ylim(0.012, 0.094)
    ax.axvline(0, color="w", lw=0.4, alpha=0.4)
    ax.set_title(title, fontsize=7)
    rf = RES[(ev, ZONE_NAME[zone])]
    ax.text(0.04, 0.05, f"resonant fraction = {rf:.2f}", color="k", fontsize=6.5,
            transform=ax.transAxes,
            bbox=dict(facecolor="w", alpha=0.75, edgecolor="none", pad=1.2))
axes[1].set_xlabel("Zonal wavenumber (cycles per 1,000 km)", fontsize=7)
axes[0].set_ylabel("Frequency (cycles per day)", fontsize=7)
for x, lab in [(0.22, "westward"), (0.78, "eastward")]:
    axes[0].text(x, 0.93, lab, fontsize=6, color="k", ha="center",
                 transform=axes[0].transAxes,
                 bbox=dict(facecolor="w", alpha=0.6, edgecolor="none", pad=1.0))
axes[2].text(0.83, 0.55, "Kelvin", color="w", fontsize=6, rotation=52,
             transform=axes[2].transAxes)
for ax, lab in zip(axes, "abc"):
    ax.text(-0.14 if lab == "a" else -0.07, 1.13, lab, transform=ax.transAxes,
            fontsize=10, fontweight="bold", va="top")
cb = fig.colorbar(pm, ax=axes, shrink=0.85, pad=0.015)
cb.set_label(r"Normalized $\zeta$ power", fontsize=7)

fig.savefig(os.path.join(OUT, "fig_kw_spectra.pdf"), bbox_inches="tight", dpi=300)
fig.savefig(os.path.join(OUT, "fig_kw_spectra.png"), bbox_inches="tight", dpi=300)
print("k-omega spectra figure saved")
