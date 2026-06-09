# P01 数据需求与优先级清单

> 目标：用真实 SWOT wind speed、SWOT SSH 与静止卫星 SST 检验 Gulf Stream / Kuroshio Extension 区域海气耦合是否存在从中尺度到亚中尺度的尺度依赖或 regime transition。
>
> 最后更新：2026-06-09

---

## 一、核心观测数据

| 数据 | 来源 | 用途 | 优先级 |
|---|---|---|---|
| SWOT L2 LR SSH Expert / WindWave | PO.DAAC / NASA Earthdata | 主资料；读取 `wind_speed_karin`、`ssha_karin`、`sig0_karin` 和质量标记 | **必需** |
| GOES-16 ABI L3C ACSPO SST | NOAA CoastWatch / GHRSST | Gulf Stream 高频 SST front，与 SWOT pass 配准 | **必需** |
| Himawari-8/9 AHI SST | JAXA / GHRSST / NOAA ACSPO | Kuroshio Extension 高频 SST front | **下一阶段必需** |

**关键原则：** 本项目的主风场是 SWOT wind speed。ASCAT、ERA5、CCMP 不替代 SWOT，只作为传统风产品对照和背景参考。

## 二、辅助对照数据

| 数据 | 来源 | 用途 | 优先级 |
|---|---|---|---|
| ASCAT vector winds | PO.DAAC / EUMETSAT / OSI SAF | 传统散射计风场对照，评估 SWOT 细尺度结构是否被传统产品平滑 | 推荐 |
| ERA5 10 m winds / surface fields | CDS / ECMWF | 大尺度背景风、天气尺度控制、稳定度背景 | 推荐 |
| CCMP winds | PO.DAAC / RSS | 格点化传统风产品对照 | 可选 |

## 三、D1 已完成的真实数据范围

| 项 | 内容 |
|---|---|
| 区域 | Gulf Stream, 82W-50W, 30N-46N |
| 时间 | 2023-09-01 至 2023-09-04 的部分 daylight SWOT passes |
| SWOT 原始数据位置 | `D:\AI-try\data\p01\batch_gs\swot\` |
| GOES 原始数据位置 | `D:\AI-try\data\p01\batch_gs\goes16_sst\` |
| 仓库内输出 | 脚本、结果摘要和图，不提交原始 NetCDF |

## 四、质量控制要求

SWOT 像元保留条件：

- `wind_speed_karin`、`ssha_karin`、`sig0_karin` 有限值；
- `wind_speed_karin_qual == 0`；
- `ssha_karin_qual == 0`；
- `sig0_karin_qual == 0`；
- `rain_flag == 0`；
- `ancillary_surface_classification_flag == 0`。

GOES SST 保留条件：

- 与 SWOT swath 时间相近；
- `quality_level >= 5`；
- 与 SWOT 像元空间配准后仍有足够有效样本。

## 五、当前缺口

1. 还没有完成 Himawari / Kuroshio Extension 阶段。
2. 还没有引入 ASCAT、ERA5、CCMP 做传统产品对照。
3. 当前 coherence 诊断是 D1 快速谱诊断，受到样本长度和云筛选影响，不能作为最终 regime transition 证据。
4. 需要增加弱锋面控制区，避免把天气背景梯度误判为 ocean-front coupling。
