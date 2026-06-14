# P04 数据来源清单

> 以下数据均为公开数据源。原始 NetCDF 文件（~2.5 GB）因体积过大未提交至 GitHub 仓库。
> 如需复现分析，请按以下说明下载。

---

## 1. CMEMS DUACS L4 SLA

| 项 | 内容 |
|---|---|
| 变量 | 海面高度异常（sla） |
| 分辨率 | 0.125° × 0.125°，月均 |
| 范围 | 全球（本分析使用南大洋 75°S–40°S） |
| 时段 | 1993-01 至 2024-11 |
| 来源 | CMEMS（哥白尼海洋服务） |
| 产品ID | `cmems_obs-sl_glo_phy-ssh_my_allsat-l4-duacs-0.125deg_P1M-m` |
| DOI | 10.48670/moi-00148 |
| 文件 | `data/CMEMS-SSH/` |
| 下载方式 | `copernicusmarine subset` 或 CMEMS 网页 |

## 2. ERA5 月平均再分析

### 2.1 近地面风场

| 项 | 内容 |
|---|---|
| 变量 | u10, v10 |
| 分辨率 | 0.25° × 0.25°，月均 |
| 范围 | 全球（本分析使用南大洋） |
| 时段 | 1940-01 至 2025-05 |
| 来源 | ECMWF / CDS |
| DOI | 10.24381/cds.f17050d7 |
| 文件 | `data/ERA5/era5_wind.nc` |
| 下载方式 | CDS API 或 ARCO-ERA5 Zarr |

### 2.2 海冰浓度

| 项 | 内容 |
|---|---|
| 变量 | siconc |
| 分辨率 | 0.25° × 0.25°，月均 |
| 时段 | 1940-01 至 2025-05 |
| 来源 | ECMWF / CDS |
| 文件 | `data/data_stream-moda_stepType-avgua.nc` |
| 备注 | ERA5 SIC 由 OSTIA 卫星数据同化（1979起），1940-1978为重建 |

## 3. CNES-CLS18 平均动力地形（MDT）

| 项 | 内容 |
|---|---|
| 变量 | mdt, u, v（地转速度） |
| 分辨率 | 0.125° × 0.125°，气候态（20年） |
| 来源 | AVISO+ / CNES |
| DOI | 10.24400/527896/a01-2020.001 |
| 文件 | `data/cnes_obs-sl_glo_phy-mdt_my_0.125deg_P20Y_*.nc` |

## 4. NSIDC 海冰指数

| 项 | 内容 |
|---|---|
| 变量 | 南极海冰范围（extent）、面积（area） |
| 分辨率 | 月均，1979-2026 |
| 来源 | NSIDC |
| DOI | 10.5067/ETIIOCY7J9HJ |
| 文件 | `data/NSIDC Sea Ice Index/` |
| 版本 | v4.0 |

## 5. 气候指数

| 指数 | 来源 | 文件 | 时段 |
|------|------|------|------|
| AAO（南极涛动） | CPC/NOAA | `climate-indices/aao_monthly.txt` | 1979-2024 |
| Niño3.4 | CPC/ERSST | `climate-indices/nino34_ersst.txt` | 1950-2024 |

---

## 数据文件大小与 Git LFS 建议

| 文件 | 大小 | 建议 |
|------|------|------|
| `CMEMS-SSH/*.nc` | ~1.2 GB | ❌ Git LFS 或外部存储 |
| `ERA5/era5_wind.nc` | ~761 MB | ❌ Git LFS 或外部存储 |
| `ERA5/era5_stress.nc` | ~170 MB | ❌ Git LFS 或外部存储 |
| `data_stream-moda_stepType-avgua.nc` | ~340 MB | ❌ Git LFS 或外部存储 |
| MDT (.nc) | ~95 MB | ⚠️ 可 LFS |
| NSIDC (.csv) | ~几十 KB | ✅ 可直接提交 |
| 气候指数 (.txt) | ~几十 KB | ✅ 可直接提交 |

如需将原始数据纳入版本控制，建议使用 Git LFS 并单独管理。

## 可再生中间文件（未提交）

| 文件 | 大小 | 生成脚本 | 说明 |
|------|------|---------|------|
| `p04_mdt_fields.npz` | ~43 MB | `p04_phase2_mdt.py` | MDT 梯度场，可从源数据重新生成 |
