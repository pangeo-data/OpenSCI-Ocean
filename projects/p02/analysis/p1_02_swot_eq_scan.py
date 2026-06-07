"""
P1-02: Scan SWOT L3 data for equatorial Pacific passes
Run on remote WSL: python3 /mnt/e/Documents/temp/p1_02_swot_eq_scan.py
"""
import xarray as xr
import numpy as np
import os, glob, json

base = "/mnt/d/v2_0_1/Basic"
out_file = "/mnt/e/Documents/temp/swot_eq_pac_passes.json"

results = []
for cycle_num in [10, 20, 30, 40, 50]:
    cycle_dir = os.path.join(base, f"cycle_{cycle_num:03d}")
    if not os.path.isdir(cycle_dir):
        continue
    files = sorted(glob.glob(os.path.join(cycle_dir, "*.nc")))
    for f in files:
        try:
            ds = xr.open_dataset(f)
            lat = ds["latitude"].values
            lon = ds["longitude"].values
            eq_mask = (lat > -5) & (lat < 5)
            eq_lines = np.any(eq_mask, axis=1)
            if eq_lines.sum() > 50:
                eq_idx = np.where(eq_lines)[0]
                eq_lon = float(np.nanmean(lon[eq_idx, :]))
                if 130 <= eq_lon <= 280:
                    pass_id = os.path.basename(f).split("_")[5]
                    ssha = ds["ssha_filtered"].values[eq_idx, :]
                    valid_pct = float(np.sum(~np.isnan(ssha)) / ssha.size * 100)
                    time_str = os.path.basename(f).split("_")[6]
                    results.append({
                        "cycle": cycle_num,
                        "pass": pass_id,
                        "eq_lon": round(eq_lon, 1),
                        "n_lines": int(eq_lines.sum()),
                        "valid_pct": round(valid_pct, 1),
                        "time": time_str,
                    })
            ds.close()
        except Exception as e:
            print(f"Error: {f}: {e}")

with open(out_file, "w") as fj:
    json.dump(results, fj, indent=2)

print(f"Found {len(results)} equatorial Pacific passes across 5 sampled cycles")
print(f"Saved to {out_file}")
for r in results[:10]:
    k = "pass"
    print(f"  Cycle {r['cycle']} Pass {r[k]}: lon={r['eq_lon']}E, valid={r['valid_pct']}%")
