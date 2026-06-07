"""
P0-02: Extract ERA5 wind stress for equatorial Pacific
Source: ARCO-ERA5 on Google Cloud Storage (zarr, no download needed)
Region: 10S-10N, 130E-80W (wider than study area for context)
Period: 2023-01-01 to 2025-12-31
Variables: mean_eastward_turbulent_surface_stress (ewss),
           mean_northward_turbulent_surface_stress (nsss)
           -> convert from accumulated J/m² to N/m² (divide by accumulation period)

Note: ARCO-ERA5 monthly is available via GEE (ECMWF/ERA5/MONTHLY, to 2020).
For 2023-2025 daily, use CDS API or ARCO-ERA5 zarr on GCS.
"""
import xarray as xr
import os
import numpy as np

OUT_DIR = "/Users/zhulin/aitest/OpenSCI-Ocean/projects/p02/data/era5"
os.makedirs(OUT_DIR, exist_ok=True)

out_file = os.path.join(OUT_DIR, "era5_wind_stress_eqpac_2023_2025.nc")
if os.path.exists(out_file):
    print(f"File already exists: {out_file}, skipping")
    exit(0)

print("Opening ARCO-ERA5 zarr from GCS...")
try:
    ds = xr.open_zarr(
        "gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3",
        chunks={"time": 24},
        storage_options={"token": "anon"},
    )
    print(f"Dataset opened. Variables: {list(ds.data_vars)[:20]}")

    # Select region and time
    # ERA5 longitudes are 0-360
    ds_sub = ds[["mean_eastward_turbulent_surface_stress",
                 "mean_northward_turbulent_surface_stress"]].sel(
        latitude=slice(10, -10),  # ERA5 lat is descending
        longitude=slice(130, 280),
        time=slice("2023-01-01", "2025-12-31"),
    )

    # Resample to daily mean
    print("Resampling to daily mean...")
    ds_daily = ds_sub.resample(time="1D").mean()

    print(f"Saving to {out_file}...")
    ds_daily.to_netcdf(out_file)
    print("Done!")

except Exception as e:
    print(f"ARCO-ERA5 zarr failed: {e}")
    print("Falling back to CDS API...")

    import cdsapi
    c = cdsapi.Client()
    for year in [2023, 2024, 2025]:
        ofile = os.path.join(OUT_DIR, f"era5_wind_stress_eqpac_{year}.nc")
        if os.path.exists(ofile):
            print(f"  {ofile} exists, skipping")
            continue
        print(f"  Requesting {year} from CDS...")
        c.retrieve(
            "reanalysis-era5-single-levels",
            {
                "product_type": "reanalysis",
                "variable": [
                    "mean_eastward_turbulent_surface_stress",
                    "mean_northward_turbulent_surface_stress",
                ],
                "year": str(year),
                "month": [f"{m:02d}" for m in range(1, 13)],
                "day": [f"{d:02d}" for d in range(1, 32)],
                "time": ["00:00", "06:00", "12:00", "18:00"],
                "area": [10, 130, -10, -80],  # N, W, S, E
                "format": "netcdf",
            },
            ofile,
        )
        print(f"  Saved: {ofile}")
