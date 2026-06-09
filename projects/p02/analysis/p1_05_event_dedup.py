"""
P1-05: Kelvin event deduplication via ridge intercept clustering.

For each event, compute the Kelvin ray intercept:
    τ = t_start - lon0 / c    (days)

Events on the same SSH anomaly ridge share similar τ. Cluster by τ
and merge duplicates, keeping the event with the longest duration or
highest mean SLA as the representative.

Output: data/kelvin_event_catalog_deduped.json
"""
import json
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

import yaml

CONFIG = Path(__file__).resolve().parents[1] / "config.yaml"
with open(CONFIG) as f:
    cfg = yaml.safe_load(f)

CATALOG = Path(__file__).resolve().parents[1] / cfg["data"]["events"]["catalog"]
OUT = CATALOG.parent / "kelvin_event_catalog_deduped.json"

KELVIN_SPEED = cfg["analysis"]["kelvin_speed_deg_day"]
TAU_CLUSTER_THRESHOLD_DAYS = 10  # events within 10 days of τ are same ridge

with open(CATALOG) as f:
    events = json.load(f)

ref_date = datetime(2023, 1, 1)


def compute_tau(event):
    t_start = datetime.fromisoformat(event["start"])
    days_from_ref = (t_start - ref_date).total_seconds() / 86400
    tau = days_from_ref - event["lon0"] / KELVIN_SPEED
    return tau


for e in events:
    e["tau"] = compute_tau(e)

events_sorted = sorted(events, key=lambda e: e["tau"])

clusters = []
current_cluster = [events_sorted[0]]

for e in events_sorted[1:]:
    if abs(e["tau"] - current_cluster[-1]["tau"]) < TAU_CLUSTER_THRESHOLD_DAYS:
        current_cluster.append(e)
    else:
        clusters.append(current_cluster)
        current_cluster = [e]
clusters.append(current_cluster)

print(f"Original events: {len(events)}")
print(f"Clusters found: {len(clusters)}")
print()

deduped = []
for i, cluster in enumerate(clusters):
    ids = [e["id"] for e in cluster]
    taus = [e["tau"] for e in cluster]
    rep = max(cluster, key=lambda e: e["days"])

    new_id = f"KE{i+1:02d}"
    rep_out = {
        "id": new_id,
        "original_ids": ids,
        "start": rep["start"],
        "end": rep["end"],
        "lon0": min(e["lon0"] for e in cluster),
        "lon1": max(e["lon1"] for e in cluster),
        "days": rep["days"],
        "mean_sla": round(max(e["mean_sla"] for e in cluster), 4),
        "max_sla": round(max(e["max_sla"] for e in cluster), 4),
        "phase_speed_mps": cfg["analysis"]["kelvin_speed_mps"],
        "tau_intercept": round(np.mean(taus), 1),
        "cluster_size": len(cluster),
        "confidence": "high" if rep["mean_sla"] > 0.06 else "moderate",
        "source_wind_flag": "pending_era5",
    }
    deduped.append(rep_out)

    print(f"  Cluster {new_id}: {ids} → τ_mean={np.mean(taus):.1f} d, "
          f"representative={rep['id']}, days={rep['days']}")

print(f"\nDeduped events: {len(deduped)}")

with open(OUT, "w") as f:
    json.dump(deduped, f, indent=2)

print(f"Saved: {OUT}")
