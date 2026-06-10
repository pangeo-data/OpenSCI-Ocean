"""
P4-04 (remote, office WSL): Λ₂ resonance-window criterion for the
historical (1993–2022) event catalog — the pre-registered test.

Same physics as p4_03 (2023 events): Λ₂ = Δω_eff / δω_res with δω_res
from vorticity power in the resonant (k,ω) window (westward phase,
λ = 700–2500 km, T = 15–50 d), power-weighted by the Kelvin meridional
footprint.

Pre-registered hypothesis (from A25):
  H: TIW-zone Λ₂ correlates with amplitude loss (r > 0), n ≥ 20, p < 0.01,
     across multiple ENSO cycles. Island chains show no correlation.

Also runs window-sensitivity tests (15–30d, 15–40d, 15–50d) per EXT-R2 §3.1.

Input:
  /mnt/d/p02_data/glorys_hist/glorys_uv_<KH>_<zone>.nc (252 files)
  /mnt/d/p02_data/duacs_hist/robustness_metrics_historical.json
Output:
  /mnt/d/p02_data/glorys_hist/lambda_v2_historical.json
  /mnt/d/p02_data/glorys_hist/lambda_v2_historical_correlations.json
  /mnt/d/p02_data/glorys_hist/lambda_v2_sensitivity.json
"""
import json
import os
import sys

import numpy as np
from scipy import stats

DATA_DIR = "/mnt/d/p02_data"
GLORYS_DIR = os.path.join(DATA_DIR, "glorys_hist")
CATALOG = os.path.join(DATA_DIR, "duacs_hist", "kelvin_event_catalog_historical.json")
ROB_FILE = os.path.join(DATA_DIR, "duacs_hist", "robustness_metrics_historical.json")

DELTA_OMEGA_EFF = 7.6e-6  # sqrt(beta * c1), s^-1
C1 = 2.5  # m/s
BETA = 2.3e-11
L_EQ_M = np.sqrt(C1 / BETA)
L_EQ_DEG = L_EQ_M / 111000

LAM_MIN_KM, LAM_MAX_KM = 700, 2500
RMS_UP_MIN = 0.01

zones = [
    {"name": "Gilbert Islands", "lon": 175, "width": 8},
    {"name": "Line Islands", "lon": 202, "width": 8},
    {"name": "TIW zone", "lon": 245, "width": 20},
]

with open(CATALOG) as f:
    events = json.load(f)
print(f"Loaded {len(events)} events", flush=True)


def zeta_3d(fname):
    import xarray as xr
    ds = xr.open_dataset(fname)
    lon_name = "longitude" if "longitude" in ds.dims else "lon"
    lat_name = "latitude" if "latitude" in ds.dims else "lat"
    sub = ds.isel(depth=0) if "depth" in ds.dims else ds
    dx = 0.083 * 111000
    dy = 0.083 * 111000
    uo = sub["uo"].values
    vo = sub["vo"].values
    zeta = np.gradient(vo, dx, axis=-1) - np.gradient(uo, dy, axis=-2)
    lats = sub[lat_name].values
    lons = sub[lon_name].values
    ds.close()
    return zeta, lats, lons


def window_masks(nt, nx, dx_m, t_min_d, t_max_d):
    freq = np.fft.fftfreq(nt, 86400.0)
    wav = np.fft.fftfreq(nx, dx_m)
    F, K = np.meshgrid(freq, wav, indexing="ij")
    lam = np.full_like(K, np.inf)
    nz = K != 0
    lam[nz] = 1.0 / np.abs(K[nz]) / 1000.0
    period = np.full_like(F, np.inf)
    nzf = F != 0
    period[nzf] = 1.0 / np.abs(F[nzf]) / 86400.0
    in_band = (lam >= LAM_MIN_KM) & (lam <= LAM_MAX_KM) & \
              (period >= t_min_d) & (period <= t_max_d)
    win_res = in_band & ((F * K) > 0)
    return win_res


def resonant_rms(zeta, lats, lons, t_min_d=15, t_max_d=50):
    nt, ny, nx = zeta.shape
    dx_m = abs(float(np.mean(np.diff(lons)))) * 111000
    win_res = window_masks(nt, nx, dx_m, t_min_d, t_max_d)

    ht = np.hanning(nt)[:, None]
    hx = np.hanning(nx)[None, :]
    norm = np.sqrt(np.mean(ht**2) * np.mean(hx**2))

    w2 = np.exp(-((lats / L_EQ_DEG) ** 2))
    ms_res = ms_total = wsum = 0.0
    for j in range(ny):
        z = zeta[:, j, :]
        z = np.nan_to_num(z - np.nanmean(z))
        Z = np.fft.fft2(z * ht * hx) / norm
        P = np.abs(Z) ** 2 / (nt * nx) ** 2
        ms_res += w2[j] * P[win_res].sum()
        ms_total += w2[j] * P.sum()
        wsum += w2[j]
    rms_r = float(np.sqrt(ms_res / wsum))
    res_frac = float(ms_res / ms_total) if ms_total > 0 else 0.0
    return rms_r, res_frac


# === Main computation ===
WINDOWS = [(15, 50), (15, 40), (15, 30)]

results_main = []
results_sensitivity = {f"W{t_min}-{t_max}": [] for t_min, t_max in WINDOWS}

n_ok = n_skip = 0
for ei, event in enumerate(events):
    for zone in zones:
        tag = zone["name"].replace(" ", "_")
        fname = os.path.join(GLORYS_DIR, f"glorys_uv_{event['id']}_{tag}.nc")
        if not os.path.exists(fname):
            n_skip += 1
            continue
        try:
            zeta, lats, lons = zeta_3d(fname)
        except Exception as e:
            print(f"{event['id']} x {tag}: READ ERROR — {e}", flush=True)
            n_skip += 1
            continue
        if zeta.shape[0] < 30:
            n_skip += 1
            continue

        for t_min, t_max in WINDOWS:
            rms_r, res_frac = resonant_rms(zeta, lats, lons, t_min, t_max)
            dw_res = rms_r / 2
            lam2 = round(DELTA_OMEGA_EFF / (dw_res + 1e-20), 2)
            wkey = f"W{t_min}-{t_max}"
            rec = {
                "event_id": event["id"],
                "zone": zone["name"],
                "n_days": int(zeta.shape[0]),
                "lambda_v2": lam2,
                "delta_omega_res": round(dw_res, 10),
                "resonant_fraction": round(res_frac, 6),
                "window": wkey,
            }
            results_sensitivity[wkey].append(rec)
            if t_min == 15 and t_max == 50:
                results_main.append(rec)

        n_ok += 1

    if (ei + 1) % 10 == 0:
        print(f"  {ei+1}/{len(events)} events processed ({n_ok} ok, {n_skip} skip)", flush=True)

print(f"\nDone: {n_ok} event-zone computed, {n_skip} skipped", flush=True)

# Save main results
out_main = os.path.join(GLORYS_DIR, "lambda_v2_historical.json")
with open(out_main, "w") as f:
    json.dump(results_main, f, indent=2)
print(f"Saved: {out_main}", flush=True)

# Save sensitivity results
out_sens = os.path.join(GLORYS_DIR, "lambda_v2_sensitivity.json")
with open(out_sens, "w") as f:
    json.dump(results_sensitivity, f, indent=2)
print(f"Saved: {out_sens}", flush=True)

# === Correlations ===
with open(ROB_FILE) as f:
    rob_all = json.load(f)
amp = {(r["event"], r["zone"]): r for r in rob_all["kelvin"]}

corr_results = {}
for wkey, res_list in results_sensitivity.items():
    pairs_all = []
    for r in res_list:
        key = (r["event_id"], r["zone"])
        if key in amp and amp[key]["rms_up"] >= RMS_UP_MIN:
            pairs_all.append((r["lambda_v2"], amp[key]["amp_ratio"], r["zone"], r["event_id"]))

    if len(pairs_all) < 5:
        print(f"\n{wkey}: only {len(pairs_all)} pairs, skipping", flush=True)
        continue

    x = np.log([p[0] for p in pairs_all])
    y = np.log([p[1] for p in pairs_all])
    rho_s, p_s = stats.spearmanr(x, y)
    r_p, p_p = stats.pearsonr(x, y)

    print(f"\n=== {wkey} (n={len(pairs_all)}) ===", flush=True)
    print(f"  Overall: Spearman ρ={rho_s:.3f} (p={p_s:.4f}), Pearson r={r_p:.3f} (p={p_p:.4f})", flush=True)

    wc = {"overall": {"n": len(pairs_all), "spearman_rho": round(rho_s, 3),
                       "spearman_p": round(p_s, 4),
                       "pearson_r": round(r_p, 3), "pearson_p": round(p_p, 4)}}

    for zone in zones:
        zp = [p for p in pairs_all if p[2] == zone["name"]]
        if len(zp) < 4:
            print(f"  {zone['name']}: n={len(zp)} too small", flush=True)
            continue
        zx = np.log([p[0] for p in zp])
        zy = np.log([p[1] for p in zp])
        zr, zpp = stats.spearmanr(zx, zy)
        zrp, zppp = stats.pearsonr(zx, zy)
        wc[zone["name"]] = {
            "n": len(zp), "spearman_rho": round(zr, 3), "spearman_p": round(zpp, 4),
            "pearson_r": round(zrp, 3), "pearson_p": round(zppp, 4)}
        sig = " ***" if zppp < 0.001 else " **" if zppp < 0.01 else " *" if zppp < 0.05 else ""
        print(f"  {zone['name']:16s}: n={len(zp)} Spearman ρ={zr:+.3f} (p={zpp:.4f}) "
              f"Pearson r={zrp:+.3f} (p={zppp:.4f}){sig}", flush=True)

    corr_results[wkey] = wc

out_corr = os.path.join(GLORYS_DIR, "lambda_v2_historical_correlations.json")
with open(out_corr, "w") as f:
    json.dump(corr_results, f, indent=2)
print(f"\nSaved: {out_corr}", flush=True)

print("\n=== PRE-REGISTERED TEST SUMMARY ===", flush=True)
main_corr = corr_results.get("W15-50", {})
tiw = main_corr.get("TIW zone", {})
line = main_corr.get("Line Islands", {})
gilbert = main_corr.get("Gilbert Islands", {})
print(f"TIW zone:       n={tiw.get('n','?')} r={tiw.get('pearson_r','?')} p={tiw.get('pearson_p','?')}", flush=True)
print(f"Line Islands:   n={line.get('n','?')} r={line.get('pearson_r','?')} p={line.get('pearson_p','?')}", flush=True)
print(f"Gilbert Islands:n={gilbert.get('n','?')} r={gilbert.get('pearson_r','?')} p={gilbert.get('pearson_p','?')}", flush=True)

h_pass = tiw.get("pearson_p", 1) < 0.01 and tiw.get("pearson_r", 0) > 0
print(f"\nH passed (TIW r>0, p<0.01): {'YES' if h_pass else 'NO'}", flush=True)

sens_stable = all(
    corr_results.get(f"W15-{t}", {}).get("TIW zone", {}).get("pearson_r", 0) > 0
    for t in [30, 40, 50]
)
print(f"Sensitivity stable (TIW r>0 for all windows): {'YES' if sens_stable else 'NO'}", flush=True)
print("LAMBDA_V2_HISTORICAL DONE", flush=True)
