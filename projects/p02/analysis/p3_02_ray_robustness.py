"""
P3-02: Ray-following robustness metrics on original SSH
Instead of spectral decomposition first, track signal along propagation rays:
- Kelvin ray: eastward at c=2.5 m/s (~1.95 deg/day)
- Rossby ray: westward at c=-0.5 m/s (~-0.39 deg/day)

For each event, extract SSH along the ray, compute:
1. Coherence between upstream and downstream segments
2. Amplitude retention (rms ratio downstream/upstream)
3. Spectral broadening (bandwidth increase after perturbation zone)
"""
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import json, os
from scipy import signal as sig

DATA_DIR = "/Users/zhulin/aitest/OpenSCI-Ocean/projects/p02/data/duacs"
FIG_DIR = "/Users/zhulin/aitest/OpenSCI-Ocean/projects/p02/figures"

ds = xr.open_dataset(os.path.join(DATA_DIR, "duacs_eqpac_daily_2023_2025.nc"))
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
dlon = float(lon_pac[1] - lon_pac[0])

# Perturbation zones
zones = [
    {"name": "Gilbert Islands", "lon": 175, "width": 8},
    {"name": "Line Islands", "lon": 202, "width": 8},
    {"name": "TIW zone", "lon": 245, "width": 20},
]

def extract_ray(data, lon, times, t0_idx, lon0, speed_deg_day, duration=40):
    """Extract SSH along a propagation ray."""
    ray = []
    for dt in range(duration):
        t = t0_idx + dt
        if t >= len(times):
            break
        lon_at_t = lon0 + speed_deg_day * dt
        if lon_at_t < lon.min() or lon_at_t > lon.max():
            break
        li = np.argmin(np.abs(lon - lon_at_t))
        ray.append(data[t, li])
    return np.array(ray)

def compute_ray_metrics(data, lon, times, event, zone, speed_deg_day):
    """Compute metrics along a ray crossing a perturbation zone."""
    t_start = np.datetime64(event["start"])
    t0_idx = np.searchsorted(times, t_start)

    z_center = zone["lon"]
    z_half = zone["width"] / 2

    # Find the time when the ray reaches the zone
    lon0 = event["lon0"]
    if abs(speed_deg_day) < 0.01:
        dt_to_zone = 20
    elif speed_deg_day > 0:
        dt_to_zone = (z_center - z_half - lon0) / speed_deg_day
    else:
        dt_to_zone = (z_center + z_half - lon0) / speed_deg_day
    dt_to_zone = int(dt_to_zone)

    if dt_to_zone < 5 or dt_to_zone > 70:
        return None

    # Upstream ray: 20 days before reaching zone
    up_start = max(0, t0_idx + dt_to_zone - 20)
    up_end = t0_idx + dt_to_zone - 2
    if up_end <= up_start + 5:
        return None

    # Downstream ray: 20 days after leaving zone
    dt_across = int(zone["width"] / max(abs(speed_deg_day), 0.01)) + 2
    dt_across = min(dt_across, 30)
    dn_start = t0_idx + dt_to_zone + dt_across + 2
    dn_end = dn_start + 18
    if dn_end >= len(times):
        return None

    # Extract upstream and downstream SSH along the ray
    ray_up = []
    for t in range(up_start, up_end):
        lon_at_t = lon0 + speed_deg_day * (t - t0_idx)
        if lon_at_t < lon.min() or lon_at_t > lon.max():
            continue
        li = np.argmin(np.abs(lon - lon_at_t))
        ray_up.append(data[t, li])

    ray_dn = []
    for t in range(dn_start, dn_end):
        lon_at_t = lon0 + speed_deg_day * (t - t0_idx)
        if lon_at_t < lon.min() or lon_at_t > lon.max():
            continue
        li = np.argmin(np.abs(lon - lon_at_t))
        ray_dn.append(data[t, li])

    ray_up = np.array(ray_up)
    ray_dn = np.array(ray_dn)

    if len(ray_up) < 8 or len(ray_dn) < 8:
        return None

    # Metrics
    rms_up = np.sqrt(np.nanmean(ray_up**2))
    rms_dn = np.sqrt(np.nanmean(ray_dn**2))
    amp_ratio = rms_dn / (rms_up + 1e-10)

    # Coherence via cross-correlation at zero lag
    min_len = min(len(ray_up), len(ray_dn))
    up_trunc = ray_up[:min_len]
    dn_trunc = ray_dn[:min_len]
    if np.std(up_trunc) > 1e-10 and np.std(dn_trunc) > 1e-10:
        coherence = float(np.abs(np.corrcoef(up_trunc, dn_trunc)[0, 1]))
    else:
        coherence = 0.0

    # Signal persistence: autocorrelation lag-1 (proxy for temporal coherence)
    if len(ray_dn) > 3:
        ac_dn = np.corrcoef(ray_dn[:-1], ray_dn[1:])[0, 1]
    else:
        ac_dn = 0
    if len(ray_up) > 3:
        ac_up = np.corrcoef(ray_up[:-1], ray_up[1:])[0, 1]
    else:
        ac_up = 0

    return {
        "rms_up": round(float(rms_up), 5),
        "rms_dn": round(float(rms_dn), 5),
        "amp_ratio": round(float(amp_ratio), 4),
        "coherence": round(float(coherence), 4),
        "persistence_up": round(float(ac_up), 4),
        "persistence_dn": round(float(ac_dn), 4),
    }

# Load events
with open("/Users/zhulin/aitest/OpenSCI-Ocean/projects/p02/data/kelvin_event_catalog.json") as f:
    events = json.load(f)

kelvin_speed = 1.95  # deg/day (~2.5 m/s)
# Control: fixed-longitude (no propagation) — measures temporal persistence
# without the benefit of tracking a propagating wave packet
control_speed = 0.0

kelvin_results = []
rossby_results = []  # actually "control" results (stationary)

for event in events:
    for zone in zones:
        m_k = compute_ray_metrics(sla_anom, lon_pac, times, event, zone, kelvin_speed)
        m_r = compute_ray_metrics(sla_anom, lon_pac, times, event, zone, control_speed)
        if m_k:
            m_k["event"] = event["id"]
            m_k["zone"] = zone["name"]
            kelvin_results.append(m_k)
        if m_r:
            m_r["event"] = event["id"]
            m_r["zone"] = zone["name"]
            rossby_results.append(m_r)

print(f"Ray-following metrics: {len(kelvin_results)} Kelvin, {len(rossby_results)} Rossby")

if kelvin_results and rossby_results:
    k_amp = [r["amp_ratio"] for r in kelvin_results]
    r_amp = [r["amp_ratio"] for r in rossby_results]
    k_coh = [r["coherence"] for r in kelvin_results]
    r_coh = [r["coherence"] for r in rossby_results]
    k_per = [r["persistence_dn"] for r in kelvin_results]
    r_per = [r["persistence_dn"] for r in rossby_results]

    print(f"\nRay-following robustness (mean ± std):")
    print(f"{'Metric':<25} {'Kelvin (east)':<20} {'Control (stationary)':<20}")
    print(f"{'Amp ratio (dn/up)':<25} {np.mean(k_amp):.3f} ± {np.std(k_amp):.3f}{'':<5} {np.mean(r_amp):.3f} ± {np.std(r_amp):.3f}")
    print(f"{'Coherence (up-dn)':<25} {np.mean(k_coh):.3f} ± {np.std(k_coh):.3f}{'':<5} {np.mean(r_coh):.3f} ± {np.std(r_coh):.3f}")
    print(f"{'Persistence (dn)':<25} {np.mean(k_per):.3f} ± {np.std(k_per):.3f}{'':<5} {np.mean(r_per):.3f} ± {np.std(r_per):.3f}")

    # Permutation tests
    for metric_name, k_vals, r_vals in [
        ("Amp ratio", k_amp, r_amp),
        ("Coherence", k_coh, r_coh),
        ("Persistence", k_per, r_per)
    ]:
        combined = k_vals + r_vals
        n_k = len(k_vals)
        obs = np.mean(k_vals) - np.mean(r_vals)
        perms = [np.mean(np.random.permutation(combined)[:n_k]) - np.mean(np.random.permutation(combined)[n_k:]) for _ in range(5000)]
        if obs > 0:
            p = np.mean(np.array(perms) >= obs)
        else:
            p = np.mean(np.array(perms) <= obs)
        print(f"  {metric_name}: Kelvin-Control diff = {obs:+.4f}, p = {p:.4f} {'*' if p < 0.05 else ''}")

    # Figure: 3 panel comparison
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for ax, metric, k_v, r_v, ylabel, title in [
        (axes[0], "Amplitude Retention", k_amp, r_amp, "dn/up ratio", "(a) Amplitude Retention"),
        (axes[1], "Coherence", k_coh, r_coh, "Correlation", "(b) Up-Down Coherence"),
        (axes[2], "Persistence", k_per, r_per, "Lag-1 Autocorr", "(c) Signal Persistence"),
    ]:
        bp = ax.boxplot([k_v, r_v], tick_labels=["Kelvin\n(eastward)", "Control\n(stationary)"],
                       patch_artist=True, widths=0.5)
        bp["boxes"][0].set_facecolor("#ff7f7f")
        bp["boxes"][1].set_facecolor("#7f7fff")
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(title, fontsize=11)
        ax.scatter(np.ones(len(k_v)) + np.random.normal(0, 0.04, len(k_v)),
                  k_v, alpha=0.5, color="red", s=20, zorder=3)
        ax.scatter(2 * np.ones(len(r_v)) + np.random.normal(0, 0.04, len(r_v)),
                  r_v, alpha=0.5, color="blue", s=20, zorder=3)

    plt.suptitle("Topological Robustness: Kelvin vs Control (Ray-Following)", fontsize=13, y=1.02)
    plt.tight_layout()
    out = os.path.join(FIG_DIR, "p3_ray_robustness_comparison.png")
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\nFigure saved: {out}")

    # Save by zone
    print("\nBy perturbation zone:")
    for z in zones:
        zn = z["name"]
        kz = [r for r in kelvin_results if r["zone"] == zn]
        rz = [r for r in rossby_results if r["zone"] == zn]
        if kz and rz:
            print(f"  {zn}: Kelvin amp={np.mean([r['amp_ratio'] for r in kz]):.3f}, "
                  f"Control amp={np.mean([r['amp_ratio'] for r in rz]):.3f}")

ds.close()
