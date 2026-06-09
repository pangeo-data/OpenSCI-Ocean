"""P01 D1 real-data pipeline.

This script builds a compact, reproducible Gulf Stream pilot for P01 using
local raw data stored outside the repository:

- SWOT L2 LR SSH Expert NetCDF files under D:/AI-try/data/p01/batch_gs/swot
- GOES-16 ABI L3C ACSPO SST NetCDF files under D:/AI-try/data/p01/batch_gs/goes16_sst

Raw data are not committed. The script writes only summaries and figures.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from scipy.interpolate import RegularGridInterpolator
from scipy.ndimage import gaussian_filter
from scipy.signal import coherence
from scipy.stats import linregress


REPO = Path(__file__).resolve().parents[3]
RAW = Path(r"D:\AI-try\data\p01")
SWOT_DIR = RAW / "batch_gs" / "swot"
SST_DIR = RAW / "batch_gs" / "goes16_sst"
FIG_DIR = REPO / "projects" / "p01" / "figures"
OUT = REPO / "projects" / "p01" / "analysis" / "d1_results_summary.json"

BBOX = (-82.0, -50.0, 30.0, 46.0)  # lon_min, lon_max, lat_min, lat_max
MAX_CASES = 8


@dataclass
class CaseResult:
    case_id: str
    swot_file: str
    sst_file: str
    swot_start: str
    goes_time: str
    lon_min: float
    lon_max: float
    lat_min: float
    lat_max: float
    swot_good_pixels: int
    collocated_pixels: int
    sst_coverage: float
    sst_range_c: list[float]
    wind_range_ms: list[float]
    k10_range: list[float]
    ssha_range_m: list[float]
    sst_wind_slope: float | None
    sst_wind_r: float | None
    grad_slope: float | None
    grad_r: float | None
    peak_coherence: float | None
    peak_coherence_wavelength_km: float | None
    figure: str


def parse_swot_start(path: Path) -> datetime:
    m = re.search(r"_(\d{8}T\d{6})_", path.name)
    if not m:
        raise ValueError(f"Cannot parse SWOT time from {path.name}")
    return datetime.strptime(m.group(1), "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)


def parse_goes_time(path: Path) -> datetime:
    m = re.match(r"(\d{14})-", path.name)
    if not m:
        raise ValueError(f"Cannot parse GOES time from {path.name}")
    return datetime.strptime(m.group(1), "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)


def nearest_goes_file(t: datetime, files: list[Path]) -> Path:
    return min(files, key=lambda f: abs((parse_goes_time(f) - t).total_seconds()))


def as_float_array(da: xr.DataArray) -> np.ndarray:
    return np.asarray(da.values, dtype=float)


def normalize_lon(lon: np.ndarray) -> np.ndarray:
    """Convert longitude to the [-180, 180) convention used by GOES files."""
    return ((lon + 180.0) % 360.0) - 180.0


def choose_window(mask: np.ndarray, width: int = 420, step: int = 80) -> tuple[int, int]:
    """Choose a compact along-track window with many valid pixels."""
    n = mask.shape[0]
    if n <= width:
        return 0, n
    best = (0, width, -1)
    for start in range(0, n - width + 1, step):
        stop = start + width
        score = int(np.count_nonzero(mask[start:stop]))
        if score > best[2]:
            best = (start, stop, score)
    return best[0], best[1]


def swot_qc(ds: xr.Dataset) -> np.ndarray:
    wind = as_float_array(ds["wind_speed_karin"])
    ssha = as_float_array(ds["ssha_karin"])
    sig0 = as_float_array(ds["sig0_karin"])
    mask = np.isfinite(wind) & np.isfinite(ssha) & np.isfinite(sig0)
    for name in ["wind_speed_karin_qual", "ssha_karin_qual", "sig0_karin_qual"]:
        if name in ds:
            mask &= as_float_array(ds[name]) == 0
    if "rain_flag" in ds:
        mask &= as_float_array(ds["rain_flag"]) == 0
    if "ancillary_surface_classification_flag" in ds:
        mask &= as_float_array(ds["ancillary_surface_classification_flag"]) == 0
    return mask


def interp_sst_to_points(sst_file: Path, lon: np.ndarray, lat: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    lon_min, lon_max = float(np.nanmin(lon)) - 0.5, float(np.nanmax(lon)) + 0.5
    lat_min, lat_max = float(np.nanmin(lat)) - 0.5, float(np.nanmax(lat)) + 0.5
    ds = xr.open_dataset(sst_file)
    try:
        sub = ds.sel(lon=slice(lon_min, lon_max), lat=slice(lat_max, lat_min))
        sst = sub["sea_surface_temperature"].isel(time=0).load()
        ql = sub["quality_level"].isel(time=0).load()
        lat_vals = np.asarray(sub["lat"].values, dtype=float)
        lon_vals = np.asarray(sub["lon"].values, dtype=float)
        sst_vals = np.asarray(sst.values, dtype=float)
        ql_vals = np.asarray(ql.values, dtype=float)
    finally:
        ds.close()

    if lat_vals[0] > lat_vals[-1]:
        lat_vals = lat_vals[::-1]
        sst_vals = sst_vals[::-1, :]
        ql_vals = ql_vals[::-1, :]

    sst_interp = RegularGridInterpolator(
        (lat_vals, lon_vals), sst_vals, bounds_error=False, fill_value=np.nan
    )
    ql_interp = RegularGridInterpolator(
        (lat_vals, lon_vals), ql_vals, bounds_error=False, fill_value=np.nan, method="nearest"
    )
    pts = np.column_stack([lat.ravel(), lon.ravel()])
    sst_out = sst_interp(pts).reshape(lat.shape)
    ql_out = ql_interp(pts).reshape(lat.shape)
    sst_out = np.where(sst_out > 100, sst_out - 273.15, sst_out)
    return sst_out, ql_out


def gradients_km(field: np.ndarray, lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    valid = np.isfinite(field)
    filled = np.where(valid, field, np.nanmedian(field[valid]) if np.any(valid) else 0.0)
    filled = gaussian_filter(filled, sigma=1.0)
    d0, d1 = np.gradient(filled)
    lat0 = float(np.nanmedian(lat))
    dy = max(abs(float(np.nanmedian(np.gradient(lat, axis=0)))) * 111.0, 0.5)
    dx = max(abs(float(np.nanmedian(np.gradient(lon, axis=1)))) * 111.0 * math.cos(math.radians(lat0)), 0.5)
    grad = np.sqrt((d0 / dy) ** 2 + (d1 / dx) ** 2)
    return np.where(valid, grad, np.nan)


def scale_slopes(x: np.ndarray, y: np.ndarray, mask: np.ndarray) -> list[dict[str, float]]:
    out = []
    for sigma_px, label in [(1, "fine"), (3, "intermediate"), (7, "coarse")]:
        xs = gaussian_filter(np.where(np.isfinite(x), x, np.nanmedian(x[mask])), sigma=sigma_px)
        ys = gaussian_filter(np.where(np.isfinite(y), y, np.nanmedian(y[mask])), sigma=sigma_px)
        xv = xs[mask]
        yv = ys[mask]
        if xv.size > 20 and np.nanstd(xv) > 0 and np.nanstd(yv) > 0:
            reg = linregress(xv, yv)
            out.append({"scale": label, "sigma_px": sigma_px, "slope": float(reg.slope), "r": float(reg.rvalue), "n": int(xv.size)})
    return out


def spectrum_summary(sst_grad: np.ndarray, wind_grad: np.ndarray, mask: np.ndarray) -> tuple[float | None, float | None]:
    series_x = np.nanmean(np.where(mask, sst_grad, np.nan), axis=1)
    series_y = np.nanmean(np.where(mask, wind_grad, np.nan), axis=1)
    good = np.isfinite(series_x) & np.isfinite(series_y)
    if np.count_nonzero(good) < 64:
        return None, None
    x = series_x[good] - np.nanmean(series_x[good])
    y = series_y[good] - np.nanmean(series_y[good])
    f, cxy = coherence(x, y, nperseg=min(128, x.size))
    if f.size <= 1:
        return None, None
    idx = int(np.nanargmax(cxy[1:]) + 1)
    wavelength = 1.0 / f[idx] if f[idx] > 0 else np.nan
    return float(cxy[idx]), float(wavelength)


def process_case(swot_file: Path, sst_file: Path, idx: int) -> CaseResult | None:
    ds = xr.open_dataset(swot_file)
    try:
        lon = normalize_lon(as_float_array(ds["longitude"]))
        lat = as_float_array(ds["latitude"])
        in_box = (lon >= BBOX[0]) & (lon <= BBOX[1]) & (lat >= BBOX[2]) & (lat <= BBOX[3])
        qc = swot_qc(ds) & in_box
        if np.count_nonzero(qc) < 500:
            return None
        start, stop = choose_window(qc)
        sl = slice(start, stop)
        lon_w, lat_w, qc_w = lon[sl], lat[sl], qc[sl]
        wind = as_float_array(ds["wind_speed_karin"])[sl]
        ssha = as_float_array(ds["ssha_karin"])[sl]
        sig0 = as_float_array(ds["sig0_karin"])[sl]
    finally:
        ds.close()

    sst, ql = interp_sst_to_points(sst_file, lon_w, lat_w)
    mask = qc_w & np.isfinite(sst) & (ql >= 5)
    if np.count_nonzero(mask) < 500:
        return None

    k10 = 0.5 * wind**2
    sst_grad = gradients_km(sst, lat_w, lon_w)
    wind_grad = gradients_km(wind, lat_w, lon_w)
    k10_grad = gradients_km(k10, lat_w, lon_w)
    ssha_grad = gradients_km(ssha, lat_w, lon_w)

    v_sst = sst[mask]
    v_wind = wind[mask]
    v_sst_grad = sst_grad[mask]
    v_wind_grad = wind_grad[mask]
    reg = linregress(v_sst, v_wind) if v_sst.size > 20 else None
    greg = linregress(v_sst_grad, v_wind_grad) if v_sst_grad.size > 20 else None
    peak_coh, peak_wl = spectrum_summary(sst_grad, wind_grad, mask)
    scale = scale_slopes(sst, wind, mask)

    fig_path = FIG_DIR / f"p01_d1_case{idx:02d}_{swot_file.stem}_swot_goes.png"
    make_case_figure(fig_path, lon_w, lat_w, sst, wind, ssha, sst_grad, wind_grad, mask, reg, greg, scale)

    case_id = swot_file.stem.replace("SWOT_L2_LR_SSH_Expert_", "")
    return CaseResult(
        case_id=case_id,
        swot_file=str(swot_file),
        sst_file=str(sst_file),
        swot_start=parse_swot_start(swot_file).isoformat(),
        goes_time=parse_goes_time(sst_file).isoformat(),
        lon_min=float(np.nanmin(lon_w[qc_w])),
        lon_max=float(np.nanmax(lon_w[qc_w])),
        lat_min=float(np.nanmin(lat_w[qc_w])),
        lat_max=float(np.nanmax(lat_w[qc_w])),
        swot_good_pixels=int(np.count_nonzero(qc_w)),
        collocated_pixels=int(np.count_nonzero(mask)),
        sst_coverage=float(np.count_nonzero(mask) / max(np.count_nonzero(qc_w), 1)),
        sst_range_c=[float(np.nanmin(v_sst)), float(np.nanmax(v_sst))],
        wind_range_ms=[float(np.nanmin(v_wind)), float(np.nanmax(v_wind))],
        k10_range=[float(np.nanmin(k10[mask])), float(np.nanmax(k10[mask]))],
        ssha_range_m=[float(np.nanmin(ssha[qc_w])), float(np.nanmax(ssha[qc_w]))],
        sst_wind_slope=float(reg.slope) if reg else None,
        sst_wind_r=float(reg.rvalue) if reg else None,
        grad_slope=float(greg.slope) if greg else None,
        grad_r=float(greg.rvalue) if greg else None,
        peak_coherence=peak_coh,
        peak_coherence_wavelength_km=peak_wl,
        figure=str(fig_path),
    )


def make_case_figure(path: Path, lon, lat, sst, wind, ssha, sst_grad, wind_grad, mask, reg, greg, scale):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, axs = plt.subplots(2, 3, figsize=(16, 9), constrained_layout=True)
    panels = [
        (axs[0, 0], sst, "GOES-16 SST (deg C)", "turbo"),
        (axs[0, 1], wind, "SWOT wind_speed_karin (m s$^{-1}$)", "magma"),
        (axs[0, 2], ssha, "SWOT SSHA (m)", "RdBu_r"),
        (axs[1, 0], sst_grad, "|grad SST| (deg C km$^{-1}$)", "viridis"),
        (axs[1, 1], wind_grad, "|grad SWOT wind| (m s$^{-1}$ km$^{-1}$)", "viridis"),
    ]
    for ax, field, title, cmap in panels:
        arr = np.where(mask | np.isfinite(field), field, np.nan)
        im = ax.pcolormesh(lon, lat, arr, shading="auto", cmap=cmap)
        ax.contour(lon, lat, sst, colors="white", linewidths=0.4, alpha=0.7)
        ax.set_title(title)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        fig.colorbar(im, ax=ax, shrink=0.8)

    ax = axs[1, 2]
    ax.scatter(sst[mask], wind[mask], s=3, alpha=0.25, color="#0b7285")
    if reg:
        xs = np.linspace(float(np.nanmin(sst[mask])), float(np.nanmax(sst[mask])), 50)
        ax.plot(xs, reg.intercept + reg.slope * xs, color="black", lw=1)
        ax.set_title(f"SST vs SWOT wind: slope={reg.slope:.2f}, r={reg.rvalue:.2f}")
    else:
        ax.set_title("SST vs SWOT wind")
    txt = ""
    if greg:
        txt += f"grad slope={greg.slope:.2f}, r={greg.rvalue:.2f}\n"
    if scale:
        txt += "scale slopes: " + ", ".join(f"{d['scale']}={d['slope']:.2f}" for d in scale)
    ax.text(0.03, 0.97, txt, transform=ax.transAxes, va="top", fontsize=9)
    ax.set_xlabel("GOES SST (deg C)")
    ax.set_ylabel("SWOT wind speed (m s$^{-1}$)")
    ax.grid(alpha=0.25)
    fig.suptitle("P01 D1 real-data pilot: SWOT wind speed, SWOT SSH, and GOES SST", fontsize=15)
    fig.savefig(path, dpi=220)
    plt.close(fig)


def make_summary_figure(cases: list[CaseResult]):
    fig_path = FIG_DIR / "p01_d1_summary_scale_response.png"
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.5), constrained_layout=True)
    x = np.arange(len(cases))
    labels = [c.case_id.split("_")[1] if "_" in c.case_id else str(i + 1) for i, c in enumerate(cases)]
    axs[0].bar(x, [c.collocated_pixels for c in cases], color="#4c78a8")
    axs[0].set_title("Collocated SWOT/GOES pixels")
    axs[0].set_xticks(x, labels, rotation=45, ha="right")
    axs[0].set_ylabel("n")
    axs[1].bar(x, [c.sst_wind_slope or np.nan for c in cases], color="#f58518")
    axs[1].set_title("SST-wind slope")
    axs[1].set_xticks(x, labels, rotation=45, ha="right")
    axs[1].set_ylabel("m s$^{-1}$ degC$^{-1}$")
    axs[2].bar(x, [c.peak_coherence or np.nan for c in cases], color="#54a24b")
    axs[2].set_title("Peak gradient coherence")
    axs[2].set_xticks(x, labels, rotation=45, ha="right")
    axs[2].set_ylim(0, 1.05)
    fig.suptitle("P01 D1 Gulf Stream batch diagnostics")
    fig.savefig(fig_path, dpi=220)
    plt.close(fig)
    return fig_path


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    swot_files = sorted(SWOT_DIR.glob("SWOT_L2_LR_SSH_Expert_*.nc"))
    sst_files = sorted(SST_DIR.glob("*.nc"))
    results: list[CaseResult] = []
    for swot in swot_files[:MAX_CASES]:
        sst = nearest_goes_file(parse_swot_start(swot), sst_files)
        print(f"Processing {swot.name} with {sst.name}")
        try:
            res = process_case(swot, sst, len(results) + 1)
        except Exception as exc:
            print(f"  skipped: {exc}")
            res = None
        if res:
            results.append(res)
    summary_fig = make_summary_figure(results) if results else None
    payload = {
        "stage": "D1 real-data pilot",
        "generated_by": "projects/p01/analysis/p01_d1_realdata_pipeline.py",
        "raw_data_root": str(RAW),
        "note": "Raw data are stored outside the repository. Results are first-pass D1 diagnostics, not final science.",
        "bbox": BBOX,
        "case_count": len(results),
        "summary_figure": str(summary_fig) if summary_fig else None,
        "cases": [r.__dict__ for r in results],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
