# Shared Data Sources / 公共数据源清单

本文档列出项目常用的公开数据源及其访问方式。各项目在 `analysis/data_sources.md` 中引用本清单或补充项目专用数据。

## 卫星高度计 / Satellite Altimetry

| 数据集 | 来源 | 访问方式 |
|---|---|---|
| AVISO+ 多卫星融合 SSH | CMEMS | `copernicusmarine` Python API |
| SWOT L3 沿轨 SSH | AVISO+/PO.DAAC | https://www.aviso.altimetry.fr/ |
| SWOT L4 网格化 SSH | CMEMS | `copernicusmarine` Python API |
| Jason-3 / Sentinel-6 GDR | EUMETSAT | https://navigator.eumetsat.int/ |

## 再分析 / Reanalysis

| 数据集 | 来源 | 访问方式 |
|---|---|---|
| ERA5 大气再分析 | CDS (Copernicus) | `cdsapi` Python API |
| GLORYS12V1 海洋再分析 | CMEMS | `copernicusmarine` Python API |

## 现场观测 / In-situ

| 数据集 | 来源 | 访问方式 |
|---|---|---|
| Argo 剖面浮标 | Argo GDAC | https://argo.ucsd.edu/ |
| WOD (World Ocean Database) | NOAA/NCEI | https://www.ncei.noaa.gov/products/world-ocean-database |
| 验潮站 | UHSLC / PSMSL | https://uhslc.soest.hawaii.edu/ |

## 海面温度 / SST

| 数据集 | 来源 | 访问方式 |
|---|---|---|
| OSTIA SST | CMEMS | `copernicusmarine` Python API |
| HadISST | Met Office | https://www.metoffice.gov.uk/hadobs/hadisst/ |

## 风场 / Wind

| 数据集 | 来源 | 访问方式 |
|---|---|---|
| CCMP 风场 | RSS (Remote Sensing Systems) | https://www.remss.com/measurements/ccmp/ |
| ERA5 10m 风场 | CDS | `cdsapi` Python API |
| ASCAT 散射计风场 | EUMETSAT/KNMI | https://scatterometer.knmi.nl/ |

## 海冰 / Sea Ice

| 数据集 | 来源 | 访问方式 |
|---|---|---|
| NSIDC 海冰密集度 | NSIDC | https://nsidc.org/ |
| OSI SAF 海冰产品 | EUMETSAT | https://osi-saf.eumetsat.int/ |
| CryoSat-2 冰厚 | ESA/AWI | https://www.meereisportal.de/ |

## 私有数据 / Proprietary

| 数据集 | 来源 | 说明 |
|---|---|---|
| GNSS 波浪潮汐浮标 | 青岛安海 | 不在 GitHub 公开，项目内部共享 |

---

*使用数据时务必在论文中正确引用数据集的 DOI 和版本号。*
