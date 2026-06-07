"""
P0-01: Download DUACS L4 daily SSH for equatorial Pacific
Dataset: cmems_obs-sl_glo_phy-ssh_nrt_allsat-l4-duacs-0.25deg_P1D
Region: 5S-5N, 130E-80W (equatorial Pacific)
Period: 2023-01-01 to 2025-12-31
Variables: sla, adt
"""
import copernicusmarine
import os

OUT_DIR = "/Users/zhulin/aitest/OpenSCI-Ocean/projects/p02/data/duacs"
os.makedirs(OUT_DIR, exist_ok=True)

out_file = os.path.join(OUT_DIR, "duacs_eqpac_daily_2023_2025.nc")
if os.path.exists(out_file):
    print(f"File already exists: {out_file}, skipping download")
else:
    copernicusmarine.subset(
        dataset_id="cmems_obs-sl_glo_phy-ssh_nrt_allsat-l4-duacs-0.25deg_P1D",
        variables=["sla", "adt"],
        minimum_longitude=130,
        maximum_longitude=180,
        minimum_latitude=-5,
        maximum_latitude=5,
        start_datetime="2023-01-01",
        end_datetime="2025-12-31",
        output_filename="duacs_eqpac_daily_2023_2025_east.nc",
        output_directory=OUT_DIR,
    )
    copernicusmarine.subset(
        dataset_id="cmems_obs-sl_glo_phy-ssh_nrt_allsat-l4-duacs-0.25deg_P1D",
        variables=["sla", "adt"],
        minimum_longitude=-180,
        maximum_longitude=-80,
        minimum_latitude=-5,
        maximum_latitude=5,
        start_datetime="2023-01-01",
        end_datetime="2025-12-31",
        output_filename="duacs_eqpac_daily_2023_2025_west.nc",
        output_directory=OUT_DIR,
    )
    # Merge the two parts
    import xarray as xr
    ds_e = xr.open_dataset(os.path.join(OUT_DIR, "duacs_eqpac_daily_2023_2025_east.nc"))
    ds_w = xr.open_dataset(os.path.join(OUT_DIR, "duacs_eqpac_daily_2023_2025_west.nc"))
    ds = xr.concat([ds_e, ds_w], dim="longitude")
    ds.to_netcdf(out_file)
    ds_e.close(); ds_w.close()
    os.remove(os.path.join(OUT_DIR, "duacs_eqpac_daily_2023_2025_east.nc"))
    os.remove(os.path.join(OUT_DIR, "duacs_eqpac_daily_2023_2025_west.nc"))
    print(f"Downloaded and merged to {out_file}")
