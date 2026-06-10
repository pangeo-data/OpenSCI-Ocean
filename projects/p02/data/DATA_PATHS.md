# P02 数据路径登记（DATA_PATHS.md）

> 约定（用户指示，2026-06-10）：**新的数据下载一律在远程办公室台式机执行**，不占用 Mac 本地磁盘。
> 远程访问：`ssh think@100.111.65.40`，WSL 内用户为 `yangleir`（详见 office-windows-remote skill）。
> 小型衍生产物（JSON/PNG）回传本仓库；大型 .nc 留在远程 D 盘（根 .gitignore 忽略所有 *.nc）。

## 远程（办公室 Windows，D 盘 / WSL `/mnt/d/`）

| 数据集 | 路径（WSL 视角） | 内容 | 生成脚本 | 状态 |
|---|---|---|---|---|
| DUACS L4 历史（事件库扩展用） | `/mnt/d/p02_data/duacs_hist/duacs_eqpac_<YYYY>.nc` | sla 日均，1993–2022 逐年，5°S–5°N，130°E–80°W，0.125°（MY 数据集 `cmems_obs-sl_glo_phy-ssh_my_allsat-l4-duacs-0.125deg_P1D`，version 202411），约 133 MB/年 | `~/p02/download_duacs_hist.py`（日志 `~/p02/duacs_hist.log`） | ✅ 完成（30/30 年，2026-06-10） |
| 历史事件目录 | `/mnt/d/p02_data/duacs_hist/kelvin_event_catalog_historical.json` | p1_08 射线检测 + τ 去重，1993–2022，84 events | `~/p02/p1_08_detect_events_historical.py`（日志 `~/p02/p1_08.log`；仓库内 `analysis/p1_08_*.py`） | ✅ 完成（2026-06-10） |
| GLORYS 历史事件子集 | `/mnt/d/p02_data/glorys_hist/glorys_uv_<KH>_<zone>.nc` | uo/vo 表层日均，84 events × 3 zones = 252 文件；全部使用 `my` 数据集（MY 已扩展覆盖 2022+） | `~/p02/p0_05_download_glorys_historical.py`（仓库内 `analysis/p0_05_*.py`） | ✅ 完成（252/252，2026-06-10） |
| ERA5 u10 扩展域（WWB 边界复查用） | `/mnt/d/p02_data/era5/u10_eq_fullyear_130E-180E.nc` | 10m 纬向风日均，2022-12-01–2024-01-15，5°S–5°N，130–180°E，0.25°（ARCO-ERA5 zarr，逐月临时文件在 `monthly_tmp/`） | `~/p02/download_era5_u10.py`（日志 `~/p02/era5_u10.log`） | 下载中（曾因脚本传空卡住，2026-06-10 修复重启） |
| SWOT L3 LR SSH 全量 | `D:\v2_0_1\Basic\`（WSL `/mnt/d/v2_0_1/Basic/`） | 150 cycles, science orbit, v2.0.1 Basic | （项目启动前已有） | 完整 |

## 本地 Mac（`projects/p02/data/`，*.nc 被 .gitignore 忽略）

| 数据集 | 路径 | 内容 | 生成脚本 |
|---|---|---|---|
| DUACS L4 NRT 2023–2025 | `data/duacs/duacs_eqpac_daily_2023_2025.nc` | sla+adt 日均，0.25°，论文主分析时段 | `analysis/p0_01_download_duacs.py` |
| GLORYS12 事件×扰动区 | `data/glorys/glorys_uv_<KE>_<zone>.nc`（21 个） | uo/vo 表层日均，1/12°，7 事件 × 3 zones 事件窗口 | `analysis/p4_01_lambda_glorys.py` |
| ERA5 u10 事件窗口 | `data/era5/u10_wwb_<event_start>.nc`（7 个） | 10m u 日均，150–180°E，事件 onset −20d..+5d | `analysis/p1_06_wwb_confirmation.py` |
| Λ 结果 JSON | `data/glorys/lambda_event_zone.json` / `lambda_along_ray.json` / `lambda_v2_resonance.json` | V1 zone 均值 / 沿射线局地 / V2 共振窗 | p4_01 / p4_02 / p4_03 |
| WWB 确认 JSON | `data/era5/wwb_event_confirmation*.json` | box 平均（已弃用，留作审计）与局地化检测结果 | p1_06 / p1_06b |
| 事件目录 | `data/kelvin_event_catalog_deduped.json` | 7 个去重事件 + WWB 标记 | p1_04 / p1_05 / p1_06b |
| 鲁棒性指标 | `data/duacs/robustness_metrics_v2.json` | amp_ratio/coherence，Kelvin + 3 对照组 | p3_03 |

## CMEMS 凭证

- Mac：`~/.copernicusmarine/.copernicusmarine-credentials`
- 远程 WSL：`~/.copernicusmarine/.copernicusmarine-credentials`（2026-06-10 从 Mac 复制）

## 回传约定

远程跑出的小型结果（JSON/PNG/事件目录）通过 stdin/scp 回传本仓库 `data/` 与 `figures/` 并 commit；
或经坚果云 `E:\Documents\reseach\` ↔ `/Users/zhulin/Nutstore Files/Documents/reseach/` 同步。
