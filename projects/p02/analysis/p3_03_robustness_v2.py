"""
P3-03: Robustness metrics v2 — using deduped events + v2 spectral decomposition.

Improvements over p3_01/p3_02:
1. Uses deduped 7-event catalog (not 11 candidates)
2. Three control groups: Rossby ray, stationary, time-shifted Kelvin
3. Block bootstrap over independent events (not event×zone as independent)
4. Uses v2 spectral decomposition (with proper preprocessing)
5. All paths from config.yaml
"""
import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import yaml

BASE = Path(__file__).resolve().parents[1]
with open(BASE / "config.yaml") as f:
    cfg = yaml.safe_load(f)

DATA_DIR = BASE / "data" / "duacs"
FIG_DIR = BASE / "figures"

# Load v2 spectral decomposition
dec = np.load(DATA_DIR / "spectral_decomposition_v2.npz", allow_pickle=True)
kelvin_field = dec["kelvin"]
rossby_field = dec["rossby"]
original = dec["original"]
lon = dec["lon"]
times = dec["times"]

# Load deduped events
with open(BASE / cfg["data"]["events"]["catalog"]) as f:
    events = json.load(f)

print(f"Loaded {len(events)} deduped events, {len(times)} time steps, {len(lon)} lon points")

kelvin_speed = float(cfg["analysis"]["kelvin_speed_deg_day"])
rossby_speed = float(cfg["analysis"]["rossby_speed_deg_day"])
dlon = float(lon[1] - lon[0])

zones = [
    {"name": "Gilbert Islands", "lon": 175, "width": 8},
    {"name": "Line Islands", "lon": 202, "width": 8},
    {"name": "TIW zone", "lon": 245, "width": 20},
]


def extract_ray_segment(data, lon, times, t0_idx, lon0, speed, duration):
    """Extract SSH along a propagation ray."""
    vals = []
    for dt in range(duration):
        t = t0_idx + dt
        if t >= len(times):
            break
        lon_at_t = lon0 + speed * dt
        if lon_at_t < lon.min() or lon_at_t > lon.max():
            break
        li = np.argmin(np.abs(lon - lon_at_t))
        vals.append(data[t, li])
    return np.array(vals) if vals else np.array([])


def compute_metrics(data, lon, times, event, zone, speed):
    """Compute robustness metrics for a ray crossing a perturbation zone."""
    t_start = np.datetime64(event["start"])
    t0_idx = int(np.searchsorted(times, t_start))
    lon0 = event["lon0"]

    z_center = zone["lon"]
    z_half = zone["width"] / 2

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

    ray_up = []
    for t in range(up_start, up_end):
        lon_t = lon0 + speed * (t - t0_idx)
        if lon.min() <= lon_t <= lon.max():
            ray_up.append(data[t, np.argmin(np.abs(lon - lon_t))])
    ray_dn = []
    for t in range(dn_start, dn_end):
        lon_t = lon0 + speed * (t - t0_idx)
        if lon.min() <= lon_t <= lon.max():
            ray_dn.append(data[t, np.argmin(np.abs(lon - lon_t))])

    ray_up = np.array(ray_up)
    ray_dn = np.array(ray_dn)
    if len(ray_up) < 8 or len(ray_dn) < 8:
        return None

    rms_up = np.sqrt(np.nanmean(ray_up ** 2))
    rms_dn = np.sqrt(np.nanmean(ray_dn ** 2))
    amp_ratio = rms_dn / (rms_up + 1e-10)

    min_len = min(len(ray_up), len(ray_dn))
    u, d = ray_up[:min_len], ray_dn[:min_len]
    coh = float(np.abs(np.corrcoef(u, d)[0, 1])) if np.std(u) > 1e-10 and np.std(d) > 1e-10 else 0.0

    return {
        "amp_ratio": round(float(amp_ratio), 4),
        "coherence": round(float(coh), 4),
        "rms_up": round(float(rms_up), 5),
        "rms_dn": round(float(rms_dn), 5),
    }


# Compute for all events × zones × control types
all_results = {"kelvin": [], "rossby": [], "stationary": [], "time_shifted": []}

for event in events:
    for zone in zones:
        m_k = compute_metrics(original, lon, times, event, zone, kelvin_speed)
        m_r = compute_metrics(original, lon, times, event, zone, rossby_speed)
        m_s = compute_metrics(original, lon, times, event, zone, 0.0)

        # Time-shifted control: same Kelvin speed but 60 days offset
        shifted = event.copy()
        t_orig = np.datetime64(event["start"])
        shifted["start"] = str(t_orig + np.timedelta64(60, "D"))
        m_ts = compute_metrics(original, lon, times, shifted, zone, kelvin_speed)

        for label, m in [("kelvin", m_k), ("rossby", m_r),
                         ("stationary", m_s), ("time_shifted", m_ts)]:
            if m:
                m["event"] = event["id"]
                m["zone"] = zone["name"]
                all_results[label].append(m)

for label, results in all_results.items():
    print(f"{label}: {len(results)} measurements")

# Block bootstrap (events as blocks)
rng = np.random.default_rng(2026)

def block_bootstrap_diff(kelvin_data, control_data, events_list, metric, n_boot=10000):
    """Bootstrap difference of means using events as blocks."""
    k_by_event = {}
    c_by_event = {}
    for r in kelvin_data:
        k_by_event.setdefault(r["event"], []).append(r[metric])
    for r in control_data:
        c_by_event.setdefault(r["event"], []).append(r[metric])
    common = sorted(set(k_by_event.keys()) & set(c_by_event.keys()))
    if len(common) < 3:
        return None, None

    k_means = [np.mean(k_by_event[e]) for e in common]
    c_means = [np.mean(c_by_event[e]) for e in common]
    obs_diff = np.mean(k_means) - np.mean(c_means)

    diffs = []
    n = len(common)
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        k_boot = np.mean([k_means[i] for i in idx])
        c_boot = np.mean([c_means[i] for i in idx])
        diffs.append(k_boot - c_boot)

    ci_lo = np.percentile(diffs, 2.5)
    ci_hi = np.percentile(diffs, 97.5)
    p = np.mean(np.abs(diffs) >= abs(obs_diff)) if obs_diff != 0 else 1.0

    return obs_diff, (ci_lo, ci_hi, p)


print("\n=== Block Bootstrap Results (events as blocks) ===")
for control_name in ["rossby", "stationary", "time_shifted"]:
    print(f"\nKelvin vs {control_name}:")
    for metric in ["amp_ratio", "coherence"]:
        diff, stats = block_bootstrap_diff(
            all_results["kelvin"], all_results[control_name],
            [e["id"] for e in events], metric
        )
        if diff is not None:
            ci_lo, ci_hi, p = stats
            sig = "*" if p < 0.05 else ""
            print(f"  {metric}: diff={diff:+.4f}, 95% CI=[{ci_lo:.4f}, {ci_hi:.4f}], p={p:.4f} {sig}")
        else:
            print(f"  {metric}: insufficient common events")

# Save results
out_file = DATA_DIR / "robustness_metrics_v2.json"
with open(out_file, "w") as f:
    json.dump(all_results, f, indent=2, default=str)
print(f"\nSaved: {out_file}")

# Figure: 4-panel comparison
fig, axes = plt.subplots(1, 4, figsize=(18, 5))
labels_map = {"kelvin": "Kelvin\n(east)", "rossby": "Rossby\n(west)",
              "stationary": "Stationary\n(control)", "time_shifted": "Time-shifted\n(placebo)"}
colors = {"kelvin": "#C0392B", "rossby": "#2980B9", "stationary": "#7F8C8D", "time_shifted": "#F39C12"}

for ax, metric, ylabel, title in [
    (axes[0], "amp_ratio", "dn/up ratio", "(a) Amplitude Retention"),
    (axes[1], "coherence", "Correlation", "(b) Up-Down Coherence"),
]:
    data_lists = []
    tick_labels = []
    box_colors = []
    for label in ["kelvin", "rossby", "stationary", "time_shifted"]:
        vals = [r[metric] for r in all_results[label]]
        if vals:
            data_lists.append(vals)
            tick_labels.append(labels_map[label])
            box_colors.append(colors[label])
    bp = ax.boxplot(data_lists, tick_labels=tick_labels, patch_artist=True, widths=0.5)
    for patch, col in zip(bp["boxes"], box_colors):
        patch.set_facecolor(col)
        patch.set_alpha(0.35)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=11)

# By-zone breakdown
for ax_idx, metric in [(2, "amp_ratio"), (3, "coherence")]:
    ax = axes[ax_idx]
    zone_names = [z["name"] for z in zones]
    x = np.arange(len(zone_names))
    width = 0.2
    for i, (label, col) in enumerate([("kelvin", "#C0392B"), ("rossby", "#2980B9")]):
        means = []
        stds = []
        for zn in zone_names:
            vals = [r[metric] for r in all_results[label] if r["zone"] == zn]
            means.append(np.mean(vals) if vals else 0)
            stds.append(np.std(vals) if vals else 0)
        ax.bar(x + i * width - width / 2, means, width, yerr=stds,
               label=label.capitalize(), color=col, alpha=0.6, capsize=3)
    ax.set_xticks(x)
    ax.set_xticklabels([z.replace(" ", "\n") for z in zone_names], fontsize=8)
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.set_title(f"({'c' if ax_idx == 2 else 'd'}) {metric.replace('_', ' ').title()} by Zone")
    ax.legend(fontsize=8)

fig.suptitle("P02 Robustness v2: Kelvin vs 3 Controls (7 deduped events)", fontsize=12)
plt.tight_layout()
out_fig = FIG_DIR / "p3_robustness_v2.png"
fig.savefig(out_fig, dpi=150, bbox_inches="tight")
plt.close()
print(f"Figure: {out_fig}")
