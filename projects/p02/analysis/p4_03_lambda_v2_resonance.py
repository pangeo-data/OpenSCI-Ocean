"""
P4-03: Λ V2 — resonance-window criterion (triad/Bragg scattering).

Physics: the spectral gap protects the Kelvin mode against ELASTIC
(frequency-conserving) scattering. A static scatterer (island wake, ω≈0)
must supply Δk ≈ 6e-6 m⁻¹ (~1000 km structure) to connect the
intraseasonal Kelvin mode (k≈+1e-6) to the n=1 Rossby branch (k≈-5e-6);
island wakes carry their enstrophy at 10-100 km scales — mismatched by an
order of magnitude. TIWs (λ≈1100 km westward, 20-40 d) sit almost exactly
at the connecting (Δk, Δω): near-resonant triad Kelvin + TIW → westward
modes. Pointwise-magnitude criteria (V1, p4_01/p4_02) are blind to this.

V2: Λ₂ = Δω_eff / δω_res with δω_res = rms(ζ in the resonant window)/2.
The rms is computed per latitude (FFT in t,x) and power-weighted by the
Kelvin footprint w²(y), w = exp(-y²/2L_eq²). Power weighting is essential:
a coherent meridional average cancels the near-antisymmetric TIW vorticity
(first attempt failed exactly this way — symmetric and antisymmetric
perturbation components couple to different mode channels and must not be
summed by amplitude).

Resonant window: westward phase, zonal wavelength 700-2500 km, period
15-50 days. The (k,ω) filter excludes the Kelvin wave's own eastward
signal, removing the self-contamination caveat of p4_02.

Validation: per-event×zone correlation of Λ₂ against the observed DUACS
amplitude ratio (robustness_metrics_v2.json, kelvin, rms_up > 0.01 m
quality filter per R15). TIW seasonality (quiet boreal spring, active
fall/winter) provides within-zone variance that zone means cannot.

Input:  data/glorys/glorys_uv_<event>_<zone>.nc (full event windows)
        data/duacs/robustness_metrics_v2.json
Output: data/glorys/lambda_v2_resonance.json
        figures/p4_lambda_v2.png
"""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import yaml
from scipy import stats

BASE = Path(__file__).resolve().parents[1]
with open(BASE / "config.yaml") as f:
    cfg = yaml.safe_load(f)

GLORYS_DIR = BASE / "data" / "glorys"
FIG_DIR = BASE / "figures"

with open(BASE / cfg["data"]["events"]["catalog"]) as f:
    events = json.load(f)

DELTA_OMEGA_EFF = float(cfg["physics"]["delta_omega_eff"])
C1 = float(cfg["physics"]["c1"])
BETA = 2.3e-11
L_EQ_M = np.sqrt(C1 / BETA)
L_EQ_DEG = L_EQ_M / 111000

LAM_MIN_KM, LAM_MAX_KM = 700, 2500
T_MIN_D, T_MAX_D = 15, 50
RMS_UP_MIN = 0.01  # m, R15 quality filter for amp_ratio

zones = [
    {"name": "Gilbert Islands", "lon": 175, "width": 8},
    {"name": "Line Islands", "lon": 202, "width": 8},
    {"name": "TIW zone", "lon": 245, "width": 20},
]


def zeta_3d(ds):
    """ζ(t, y, x) and coordinates."""
    lon_name = "longitude" if "longitude" in ds.dims else "lon"
    lat_name = "latitude" if "latitude" in ds.dims else "lat"
    sub = ds.isel(depth=0) if "depth" in ds.dims else ds
    dx = 0.083 * 111000
    dy = 0.083 * 111000
    uo = sub["uo"].values
    vo = sub["vo"].values
    zeta = np.gradient(vo, dx, axis=-1) - np.gradient(uo, dy, axis=-2)
    return zeta, sub[lat_name].values, sub[lon_name].values


def window_masks(nt, nx, dx_m):
    freq = np.fft.fftfreq(nt, 86400.0)
    wav = np.fft.fftfreq(nx, dx_m)
    F, K = np.meshgrid(freq, wav, indexing="ij")
    lam = np.full_like(K, np.inf)
    nz = K != 0
    lam[nz] = 1.0 / np.abs(K[nz]) / 1000.0
    period = np.full_like(F, np.inf)
    nzf = F != 0
    period[nzf] = 1.0 / np.abs(F[nzf]) / 86400.0
    # numpy fft component exp(2πi(Ft + Kx)) has phase speed -F/K:
    # westward (toward -x) ⇔ F·K > 0
    in_band = (lam >= LAM_MIN_KM) & (lam <= LAM_MAX_KM) & \
              (period >= T_MIN_D) & (period <= T_MAX_D)
    win_res = in_band & ((F * K) > 0)
    win_east = in_band & ((F * K) < 0)
    return win_res, win_east


def resonant_rms_powerweighted(zeta, lats, lons):
    """Per-latitude (t,x) spectra, Kelvin-footprint power-weighted."""
    nt, ny, nx = zeta.shape
    dx_m = abs(float(np.mean(np.diff(lons)))) * 111000
    win_res, win_east = window_masks(nt, nx, dx_m)

    ht = np.hanning(nt)[:, None]
    hx = np.hanning(nx)[None, :]
    norm = np.sqrt(np.mean(ht**2) * np.mean(hx**2))

    w2 = np.exp(-((lats / L_EQ_DEG) ** 2))  # w² with w Gaussian
    ms_res = ms_east = ms_static = ms_total = wsum = 0.0
    for j in range(ny):
        z = zeta[:, j, :]
        z = np.nan_to_num(z - np.nanmean(z))
        Z = np.fft.fft2(z * ht * hx) / norm
        P = np.abs(Z) ** 2 / (nt * nx) ** 2
        ms_res += w2[j] * P[win_res].sum()
        ms_east += w2[j] * P[win_east].sum()
        ms_static += w2[j] * P[0, :].sum()
        ms_total += w2[j] * P.sum()
        wsum += w2[j]
    return {
        "rms_resonant": float(np.sqrt(ms_res / wsum)),
        "rms_eastward_band": float(np.sqrt(ms_east / wsum)),
        "rms_static": float(np.sqrt(ms_static / wsum)),
        "rms_total": float(np.sqrt(ms_total / wsum)),
        "resonant_fraction": float(ms_res / ms_total),
        "static_fraction": float(ms_static / ms_total),
    }


results = []
for event in events:
    for zone in zones:
        fname = GLORYS_DIR / f"glorys_uv_{event['id']}_{zone['name'].replace(' ', '_')}.nc"
        if not fname.exists():
            continue
        ds = xr.open_dataset(fname)
        zeta, lats, lons = zeta_3d(ds)
        ds.close()
        if zeta.shape[0] < 30:
            continue
        d = resonant_rms_powerweighted(zeta, lats, lons)
        dw_res = d["rms_resonant"] / 2
        r = {
            "event_id": event["id"],
            "zone": zone["name"],
            "n_days": int(zeta.shape[0]),
            "lambda_v2": round(DELTA_OMEGA_EFF / (dw_res + 1e-20), 2),
            "delta_omega_res": round(dw_res, 10),
            # R21 Concern 3: records shorter than 2x the longest resonant
            # period resolve that period with <2 frequency bins
            "window_caveat": bool(zeta.shape[0] < 2 * T_MAX_D),
            **{k: round(v, 10) for k, v in d.items()},
        }
        results.append(r)
        print(f"{r['event_id']} x {r['zone']:16s}: Λ₂={r['lambda_v2']:6.2f} "
              f"rms_res={d['rms_resonant']:.2e} res_frac={d['resonant_fraction']:.3f}")

out = GLORYS_DIR / "lambda_v2_resonance.json"
with open(out, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved: {out}")

print("\nZone summary:")
for zone in zones:
    zr = [r for r in results if r["zone"] == zone["name"]]
    lv = [r["lambda_v2"] for r in zr]
    rf = [r["resonant_fraction"] for r in zr]
    print(f"  {zone['name']:16s}: Λ₂ = {np.mean(lv):6.2f} ± {np.std(lv):5.2f} "
          f"(range {min(lv):.2f}-{max(lv):.2f}) | res_frac = {np.mean(rf):.3f}")

# --- validation against observed amplitude ratios ---
with open(BASE / "data" / "duacs" / "robustness_metrics_v2.json") as f:
    rob = json.load(f)["kelvin"]
amp = {(r["event"], r["zone"]): r for r in rob}

pairs = []
for r in results:
    key = (r["event_id"], r["zone"])
    if key in amp and amp[key]["rms_up"] >= RMS_UP_MIN:
        pairs.append((r["lambda_v2"], amp[key]["amp_ratio"], r["zone"], r["event_id"]))

x = np.log([p[0] for p in pairs])
y = np.log([p[1] for p in pairs])
rho_s, p_s = stats.spearmanr(x, y)
r_p, p_p = stats.pearsonr(x, y)
print(f"\nΛ₂ vs amp_ratio (n={len(pairs)}, rms_up>{RMS_UP_MIN}):")
print(f"  Spearman ρ = {rho_s:.3f} (p = {p_s:.4f})")
print(f"  Pearson r (log-log) = {r_p:.3f} (p = {p_p:.4f})")

# R21 Concern 1 / Q19: zone-specific correlations, reproducible here.
# Full-sample result above is reported first (Concern 2); zone subsets
# follow with their physical motivation: the resonance channel is expected
# to act in the TIW zone, not at the islands (focusing-dominated).
corr_summary = {"overall": {"n": len(pairs), "spearman_rho": round(rho_s, 3),
                            "spearman_p": round(p_s, 4),
                            "pearson_r_loglog": round(r_p, 3),
                            "pearson_p": round(p_p, 4)}}
for zone in zones:
    zp = [p for p in pairs if p[2] == zone["name"]]
    if len(zp) < 4:
        print(f"  {zone['name']}: n={len(zp)} too small, skipped")
        continue
    zx = np.log([p[0] for p in zp])
    zy = np.log([p[1] for p in zp])
    zr, zpp = stats.spearmanr(zx, zy)
    zrp, zppp = stats.pearsonr(zx, zy)
    corr_summary[zone["name"]] = {
        "n": len(zp), "spearman_rho": round(zr, 3), "spearman_p": round(zpp, 4),
        "pearson_r_loglog": round(zrp, 3), "pearson_p": round(zppp, 4)}
    print(f"  {zone['name']:16s}: n={len(zp)} Spearman ρ={zr:+.3f} (p={zpp:.4f}) "
          f"Pearson r={zrp:+.3f} (p={zppp:.4f})")

with open(GLORYS_DIR / "lambda_v2_correlations.json", "w") as f:
    json.dump(corr_summary, f, indent=2)
print(f"Saved: {GLORYS_DIR / 'lambda_v2_correlations.json'}")

# --- figure ---
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
colors = {"Gilbert Islands": "#1f77b4", "Line Islands": "#2ca02c", "TIW zone": "#d62728"}

ax = axes[0]
for i, zone in enumerate(zones):
    zr = [r for r in results if r["zone"] == zone["name"]]
    yv = [r["lambda_v2"] for r in zr]
    xv = np.random.default_rng(i).normal(i, 0.06, len(yv))
    ax.scatter(xv, yv, c=colors[zone["name"]], s=50, zorder=3)
    ax.hlines(np.mean(yv), i - 0.25, i + 0.25, color=colors[zone["name"]], lw=2)
ax.set_xticks(range(len(zones)), [z["name"].replace(" ", "\n") for z in zones])
ax.set_ylabel(r"$\Lambda_2 = \Delta\omega_\mathrm{eff}/\delta\omega_\mathrm{res}$")
ax.set_title("Resonance-window criterion by zone")

ax = axes[1]
for zone in zones:
    zp = [p for p in pairs if p[2] == zone["name"]]
    if zp:
        ax.scatter([p[0] for p in zp], [p[1] for p in zp],
                   c=colors[zone["name"]], s=50, label=zone["name"], zorder=3)
ax.set_xscale("log"), ax.set_yscale("log")
ax.axhline(1.0, color="gray", lw=0.8, ls=":")
ax.set_xlabel(r"$\Lambda_2$")
ax.set_ylabel("Observed amplitude ratio (DUACS)")
ax.set_title(f"Validation: Spearman ρ = {rho_s:.2f} (p = {p_s:.3f}, n = {len(pairs)})")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(FIG_DIR / "p4_lambda_v2.png", dpi=150)
print(f"Saved: {FIG_DIR / 'p4_lambda_v2.png'}")
