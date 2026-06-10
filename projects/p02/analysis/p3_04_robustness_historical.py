"""
P3-04 (remote, office WSL): ray-following robustness metrics for the
historical (1993-2022) event catalog — Kelvin + 3 controls + block bootstrap.

Same method as p3_03 (2023 events): along-ray rms in 20-deg upstream /
downstream windows around each perturbation zone, amp_ratio = rms_dn/rms_up,
controls = westward Rossby ray, stationary, time-shifted (+60 d) Kelvin.
Input field: 2S-2N mean SLA anomaly w.r.t. monthly climatology (identical
to the detection Hovmoller of p1_08).

At n = 84 events this also re-tests the Kelvin-vs-control comparisons that
were underpowered at n = 7 (95% CI included zero).

Output: /mnt/d/p02_data/duacs_hist/robustness_metrics_historical.json
"""
import glob
import json
import os

import numpy as np
import xarray as xr

DATA_DIR = "/mnt/d/p02_data/duacs_hist"
CATALOG = os.path.join(DATA_DIR, "kelvin_event_catalog_historical.json")
OUT = os.path.join(DATA_DIR, "robustness_metrics_historical.json")

KELVIN_SPEED = 1.95   # deg/day
ROSSBY_SPEED = -0.39  # deg/day

zones = [
    {"name": "Gilbert Islands", "lon": 175, "width": 8},
    {"name": "Line Islands", "lon": 202, "width": 8},
    {"name": "TIW zone", "lon": 245, "width": 20},
]

files = sorted(glob.glob(os.path.join(DATA_DIR, "duacs_eqpac_[0-9]*.nc")))
print(f"Loading {len(files)} yearly files...", flush=True)
ds = xr.open_mfdataset(files, combine="by_coords")
sla = ds["sla"].sel(latitude=slice(-2, 2)).mean("latitude").sel(longitude=slice(130, 280))
clim = sla.groupby("time.month").mean("time")
anom = (sla.groupby("time.month") - clim).load()
data = anom.values
times = anom.time.values
lon = anom.longitude.values
print(f"Hovmoller loaded: {data.shape}", flush=True)

with open(CATALOG) as f:
    events = json.load(f)


def compute_metrics(event, zone, speed):
    t0_idx = int(np.searchsorted(times, np.datetime64(event["start"])))
    lon0 = event["lon0"]
    z_center, z_half = zone["lon"], zone["width"] / 2

    if abs(speed) < 0.01:
        dt_to_zone = 20
    elif speed > 0:
        dt_to_zone = int((z_center - z_half - lon0) / speed)
    else:
        dt_to_zone = int((z_center + z_half - lon0) / speed)
    if dt_to_zone < 5 or dt_to_zone > 80:
        return None

    up_start = max(0, t0_idx + dt_to_zone - 20)
    up_end = t0_idx + dt_to_zone - 2
    if up_end <= up_start + 5:
        return None
    dt_across = min(int(zone["width"] / max(abs(speed), 0.01)) + 2, 30)
    dn_start = t0_idx + dt_to_zone + dt_across + 2
    dn_end = dn_start + 18
    if dn_end >= len(times):
        return None

    def ray_vals(a, b):
        out = []
        for t in range(a, b):
            lon_t = lon0 + speed * (t - t0_idx)
            if lon.min() <= lon_t <= lon.max():
                out.append(data[t, np.argmin(np.abs(lon - lon_t))])
        return np.array(out)

    ray_up, ray_dn = ray_vals(up_start, up_end), ray_vals(dn_start, dn_end)
    if len(ray_up) < 8 or len(ray_dn) < 8:
        return None
    rms_up = float(np.sqrt(np.nanmean(ray_up**2)))
    rms_dn = float(np.sqrt(np.nanmean(ray_dn**2)))
    n = min(len(ray_up), len(ray_dn))
    u, d = ray_up[:n], ray_dn[:n]
    coh = float(np.abs(np.corrcoef(u, d)[0, 1])) if np.std(u) > 1e-10 and np.std(d) > 1e-10 else 0.0
    return {"amp_ratio": round(rms_dn / (rms_up + 1e-10), 4),
            "coherence": round(coh, 4),
            "rms_up": round(rms_up, 5), "rms_dn": round(rms_dn, 5)}


all_results = {"kelvin": [], "rossby": [], "stationary": [], "time_shifted": []}
for event in events:
    for zone in zones:
        rossby_event = dict(event, lon0=zone["lon"] + zone["width"] + 25)
        shifted = dict(event, start=str(np.datetime64(event["start"]) + np.timedelta64(60, "D")))
        for label, m in [("kelvin", compute_metrics(event, zone, KELVIN_SPEED)),
                         ("rossby", compute_metrics(rossby_event, zone, ROSSBY_SPEED)),
                         ("stationary", compute_metrics(event, zone, 0.0)),
                         ("time_shifted", compute_metrics(shifted, zone, KELVIN_SPEED))]:
            if m:
                m["event"] = event["id"]
                m["zone"] = zone["name"]
                all_results[label].append(m)

for label, res in all_results.items():
    print(f"{label}: {len(res)} measurements", flush=True)

with open(OUT, "w") as f:
    json.dump(all_results, f, indent=2)
print(f"Saved: {OUT}", flush=True)

# block bootstrap, events as blocks
rng = np.random.default_rng(2026)


def block_bootstrap_diff(kelvin_data, control_data, metric, n_boot=10000):
    k_by, c_by = {}, {}
    for r in kelvin_data:
        k_by.setdefault(r["event"], []).append(r[metric])
    for r in control_data:
        c_by.setdefault(r["event"], []).append(r[metric])
    common = sorted(set(k_by) & set(c_by))
    if len(common) < 3:
        return None
    k_means = [np.mean(k_by[e]) for e in common]
    c_means = [np.mean(c_by[e]) for e in common]
    obs = np.mean(k_means) - np.mean(c_means)
    diffs = []
    n = len(common)
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        diffs.append(np.mean([k_means[i] for i in idx]) - np.mean([c_means[i] for i in idx]))
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return obs, lo, hi, len(common)


print("\n=== Block bootstrap (events as blocks, n_boot=10000) ===", flush=True)
for ctrl in ["rossby", "stationary", "time_shifted"]:
    for metric in ["amp_ratio", "coherence"]:
        r = block_bootstrap_diff(all_results["kelvin"], all_results[ctrl], metric)
        if r:
            obs, lo, hi, n = r
            sig = " SIGNIFICANT" if (lo > 0 or hi < 0) else ""
            print(f"kelvin-vs-{ctrl} {metric}: diff={obs:+.4f} CI=[{lo:+.4f},{hi:+.4f}] n_events={n}{sig}", flush=True)

print("ROBUSTNESS DONE", flush=True)
