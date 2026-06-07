"""
P3-01: Compute topological robustness metrics for Kelvin wave events
For each event, define upstream/downstream windows around perturbation zones,
compute 4 robustness metrics, and compare Kelvin vs westward-propagating signals.

Perturbation zones (from bathymetry + TIW climatology):
- Gilbert Islands: ~173°E (175°E in 0-360)
- Line Islands: ~200°E (160°W)
- TIW-active zone: ~220-260°E (cold tongue, 140-100°W)
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json, os

DATA_DIR = "/Users/zhulin/aitest/OpenSCI-Ocean/projects/p02/data/duacs"
FIG_DIR = "/Users/zhulin/aitest/OpenSCI-Ocean/projects/p02/figures"

# Load decomposed fields
dec = np.load(os.path.join(DATA_DIR, "spectral_decomposition.npz"), allow_pickle=True)
kelvin = dec["kelvin"]
rossby = dec["rossby"]
original = dec["original"]
lon = dec["lon"]
times = dec["times"]

# Load event catalog
with open("/Users/zhulin/aitest/OpenSCI-Ocean/projects/p02/data/kelvin_event_catalog.json") as f:
    events = json.load(f)

# Define perturbation zones
perturb_zones = [
    {"name": "Gilbert_Is", "lon_center": 175, "lon_width": 10},
    {"name": "Line_Is", "lon_center": 200, "lon_width": 10},
    {"name": "TIW_zone", "lon_center": 240, "lon_width": 30},
]

def compute_metrics(signal, lon, times, event, zone):
    """Compute robustness metrics upstream/downstream of a perturbation zone."""
    # Time window for this event
    t_start = np.datetime64(event["start"])
    t_end = np.datetime64(event["end"])
    t_mask = (times >= t_start) & (times <= t_end)
    if t_mask.sum() < 10:
        return None

    # Longitude windows
    z_lo = zone["lon_center"] - zone["lon_width"]
    z_hi = zone["lon_center"] + zone["lon_width"]

    # Upstream: 20° west of zone
    up_lo = z_lo - 25
    up_hi = z_lo - 5
    # Downstream: 20° east of zone
    dn_lo = z_hi + 5
    dn_hi = z_hi + 25

    # Check bounds
    if up_lo < lon.min() or dn_hi > lon.max():
        return None

    up_mask = (lon >= up_lo) & (lon <= up_hi)
    dn_mask = (lon >= dn_lo) & (lon <= dn_hi)

    if up_mask.sum() < 5 or dn_mask.sum() < 5:
        return None

    sig_up = signal[t_mask][:, up_mask]
    sig_dn = signal[t_mask][:, dn_mask]

    # 1. Backward scattering index B
    # Use 2D FFT on each window, compare eastward vs westward energy
    def east_west_ratio(field):
        fft = np.fft.fft2(field)
        power = np.abs(fft)**2
        nt, nx = field.shape
        # Positive kx = eastward (first half in FFT)
        e_east = np.sum(power[:, 1:nx//2])
        e_west = np.sum(power[:, nx//2+1:])
        return e_west / (e_east + e_west + 1e-20)

    B_up = east_west_ratio(sig_up)
    B_dn = east_west_ratio(sig_dn)

    # 2. Phase coherence C
    # Cross-correlation between upstream and downstream time series (spatially averaged)
    ts_up = np.nanmean(sig_up, axis=1)
    ts_dn = np.nanmean(sig_dn, axis=1)
    if np.std(ts_up) < 1e-10 or np.std(ts_dn) < 1e-10:
        C = 0
    else:
        C = float(np.abs(np.corrcoef(ts_up, ts_dn)[0, 1]))

    # 3. Amplitude retention
    amp_up = np.std(sig_up)
    amp_dn = np.std(sig_dn)
    A_ratio = amp_dn / (amp_up + 1e-20)

    # 4. Energy in equatorial band (using full original field)
    # Not computable from 1D Hovmöller — skip for now, use amplitude as proxy

    return {
        "B_upstream": round(float(B_up), 4),
        "B_downstream": round(float(B_dn), 4),
        "coherence_C": round(float(C), 4),
        "amp_ratio": round(float(A_ratio), 4),
        "amp_up": round(float(amp_up), 5),
        "amp_dn": round(float(amp_dn), 5),
    }

# Compute metrics for all events × all zones
results_kelvin = []
results_rossby = []

for event in events:
    for zone in perturb_zones:
        m_k = compute_metrics(kelvin, lon, times, event, zone)
        m_r = compute_metrics(rossby, lon, times, event, zone)
        if m_k is not None:
            m_k["event"] = event["id"]
            m_k["zone"] = zone["name"]
            m_k["mode"] = "Kelvin"
            results_kelvin.append(m_k)
        if m_r is not None:
            m_r["event"] = event["id"]
            m_r["zone"] = zone["name"]
            m_r["mode"] = "Rossby"
            results_rossby.append(m_r)

print(f"Computed metrics: {len(results_kelvin)} Kelvin, {len(results_rossby)} Rossby")

# Summary statistics
if results_kelvin and results_rossby:
    k_coh = [r["coherence_C"] for r in results_kelvin]
    r_coh = [r["coherence_C"] for r in results_rossby]
    k_B = [r["B_downstream"] for r in results_kelvin]
    r_B = [r["B_downstream"] for r in results_rossby]
    k_amp = [r["amp_ratio"] for r in results_kelvin]
    r_amp = [r["amp_ratio"] for r in results_rossby]

    print(f"\nRobustness comparison (mean ± std):")
    print(f"{'Metric':<20} {'Kelvin':<20} {'Rossby':<20} {'Kelvin advantage?'}")
    print(f"{'Coherence C':<20} {np.mean(k_coh):.3f} ± {np.std(k_coh):.3f}{'':<5} {np.mean(r_coh):.3f} ± {np.std(r_coh):.3f}{'':<5} {'YES' if np.mean(k_coh) > np.mean(r_coh) else 'no'}")
    print(f"{'Backscatter B_dn':<20} {np.mean(k_B):.3f} ± {np.std(k_B):.3f}{'':<5} {np.mean(r_B):.3f} ± {np.std(r_B):.3f}{'':<5} {'YES (lower)' if np.mean(k_B) < np.mean(r_B) else 'no'}")
    print(f"{'Amp ratio dn/up':<20} {np.mean(k_amp):.3f} ± {np.std(k_amp):.3f}{'':<5} {np.mean(r_amp):.3f} ± {np.std(r_amp):.3f}{'':<5} {'YES (higher)' if np.mean(k_amp) > np.mean(r_amp) else 'no'}")

    # Permutation test for coherence
    from scipy import stats
    combined = k_coh + r_coh
    n_k = len(k_coh)
    observed_diff = np.mean(k_coh) - np.mean(r_coh)
    n_perm = 10000
    perm_diffs = []
    for _ in range(n_perm):
        perm = np.random.permutation(combined)
        perm_diffs.append(np.mean(perm[:n_k]) - np.mean(perm[n_k:]))
    p_value = np.mean(np.array(perm_diffs) >= observed_diff)
    print(f"\nPermutation test (coherence): observed diff = {observed_diff:.4f}, p = {p_value:.4f}")

    # Plot: Kelvin vs Rossby robustness comparison
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Panel (a): Coherence
    ax = axes[0]
    ax.boxplot([k_coh, r_coh], labels=["Kelvin", "Rossby"])
    ax.set_ylabel("Phase Coherence C")
    ax.set_title(f"(a) Downstream Coherence\np = {p_value:.3f}")

    # Panel (b): Backscatter index
    ax = axes[1]
    ax.boxplot([k_B, r_B], labels=["Kelvin", "Rossby"])
    ax.set_ylabel("Backscatter Index B")
    ax.set_title("(b) Downstream Backscatter")

    # Panel (c): Amplitude ratio
    ax = axes[2]
    ax.boxplot([k_amp, r_amp], labels=["Kelvin", "Rossby"])
    ax.set_ylabel("Amplitude Ratio (dn/up)")
    ax.set_title("(c) Amplitude Retention")

    plt.suptitle("Topological Robustness: Kelvin vs Rossby Wave Modes", fontsize=13)
    plt.tight_layout()
    out_path = os.path.join(FIG_DIR, "p3_robustness_comparison.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\nFigure saved: {out_path}")

    # Save results
    all_results = results_kelvin + results_rossby
    with open(os.path.join(DATA_DIR, "robustness_metrics.json"), "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"Results saved: {len(all_results)} measurements")
