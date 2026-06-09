# P01 D1 真实数据运行说明

本文档说明如何复现 P01 D1 Gulf Stream 真实数据试验。原始数据保存在仓库外，仓库内只保留脚本、摘要和图。

## 运行环境

使用 Codex bundled Python：

```powershell
& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -V
```

已使用的核心包：

- `xarray`
- `numpy`
- `matplotlib`
- `scipy`
- `netCDF4`

## 原始数据

原始数据不提交到仓库：

```text
D:\AI-try\data\p01\batch_gs\swot\
D:\AI-try\data\p01\batch_gs\goes16_sst\
```

SWOT 数据为 L2 LR SSH Expert NetCDF，使用变量：

- `wind_speed_karin`
- `ssha_karin`
- `sig0_karin`
- `wind_speed_karin_qual`
- `ssha_karin_qual`
- `sig0_karin_qual`
- `rain_flag`
- `ancillary_surface_classification_flag`

GOES-16 数据为 ABI L3C ACSPO SST，使用变量：

- `sea_surface_temperature`
- `quality_level`

## 运行命令

```powershell
& 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' projects\p01\analysis\p01_d1_realdata_pipeline.py
```

## 输出文件

| 文件 | 用途 |
|---|---|
| `analysis/d1_results_summary.json` | D1 机器可读结果摘要 |
| `figures/p01_d1_case*.png` | 每个有效 case 的 SWOT/GOES 配准和诊断图 |
| `figures/p01_d1_summary_scale_response.png` | 三个有效 case 的样本量、SST-wind 斜率和峰值相干性汇总 |
| `manuscript/v1_ai_draft/P01-D1-Manuscript-CN.md` | 中文 D1 初稿 |

## 当前结果

脚本处理了 2023-09-01 至 2023-09-04 的 Gulf Stream SWOT/GOES 匹配数据。经过质量控制和云筛选，3 个 case 保留：

| Case | 有效配准像元 | SST-wind 斜率 | 相关系数 |
|---|---:|---:|---:|
| 003_048 | 2709 | 1.14 m s^-1 degC^-1 | 0.88 |
| 003_076 | 6849 | 1.14 m s^-1 degC^-1 | 0.56 |
| 003_102 | 7436 | -1.49 m s^-1 degC^-1 | -0.54 |

结果说明：

- 真实 SWOT wind speed、SWOT SSH 和 GOES SST 可以配准到同一个小窗口；
- 两个 case 显示正 SST-wind 关系，一个 case 显示负关系；
- 这支持“尺度依赖/背景状态重要”的研究动机，但不能直接证明 regime transition；
- 当前谱相干结果应视为 D1 快速诊断，后续需要更严格的尺度滤波、背景风去除和控制区。

## 重要限制

1. 当前只做 Gulf Stream，尚未做 Kuroshio Extension。
2. 未引入 ASCAT/ERA5/CCMP 对照。
3. 没有做天气背景去除，SST-wind 斜率可能混入大尺度大气梯度。
4. GOES 云筛选会造成空间采样偏差。
5. SWOT wind speed 是风速大小，不是矢量风；本阶段不做 wind stress curl/divergence。
