# SWOT 揭示的亚中尺度海气耦合尺度依赖：基于 Gulf Stream 真实观测的 D1 初稿

**稿件状态：** D1 最终初稿（AI-assisted first complete draft）  
**项目编号：** P01  
**目标期刊：** GRL / JGR: Oceans；若后续跨区域样本和传统产品对照足够强，可再讨论 Nature Communications 级别叙事。  
**核心资料：** SWOT L2 wind speed、SWOT KaRIn SSH、GOES-16 ABI SST  
**重要边界：** 本稿完成真实数据闭环和初步科学叙事，但尚不能证明 regime transition。所有文献、物理解释和结论强度仍需 D2 人类专家审查。

---

## 摘要

中尺度海表温度锋面可以通过大气边界层稳定度和垂向动量混合调制近海面风速，但这种 SST-wind coupling 是否能连续延伸到亚中尺度，仍缺少直接观测约束。传统散射计和再分析风产品在西边界流区域通常能解析中尺度 SST-wind 关系，却可能平滑掉锋面、filaments 和 eddy edges 附近的细尺度风速响应。SWOT KaRIn 宽刈幅观测为这一问题提供了新的观测机会，因为 SWOT L2 产品不仅包含高分辨率 SSH，也包含由雷达后向散射反演的 wind speed。本文基于 Gulf Stream 区域真实 SWOT L2 LR SSH Expert 数据和同步 GOES-16 ABI L3C ACSPO SST，构建 SWOT wind speed、SWOT SSHA 与 geostationary SST 的小窗口配准流程，并计算近海面风速动能代理量、SST-wind 回归、梯度关系和快速相干诊断。2023 年 9 月 2-4 日的 8 个候选 SWOT/GOES case 中，3 个 case 通过质量控制和云筛选，配准像元数分别为 2709、6849 和 7436。两个 case 呈现正 SST-wind 关系，斜率约为 1.14 m s^-1 degC^-1，相关系数分别为 0.88 和 0.56；第三个 case 呈现负关系，斜率为 -1.49 m s^-1 degC^-1，相关系数为 -0.54。该结果表明真实 SWOT wind speed 与静止卫星 SST 可以形成可复现的亚中尺度海气耦合诊断链路，同时也说明 Gulf Stream 的风速响应并非简单、普适的线性 SST 函数。本文提出，P01 下一阶段应从单个正相关案例转向尺度依赖检验、背景大气控制、传统风产品对照和 Kuroshio Extension 跨区域验证。当前 D1 结果支持继续研究“中尺度到亚中尺度海气耦合是否发生尺度依赖或 regime transition”，但尚不能作为最终机制证明。

**关键词：** SWOT；Gulf Stream；亚中尺度；海气耦合；SST front；wind speed；GOES-16

---

## 1. 引言

海洋锋面、涡旋和西边界流延伸体能够在近海面大气中留下可观测信号。经典中尺度海气耦合框架认为，暖 SST 异常通常使大气边界层更不稳定，增强湍混合，使高空较强动量向近海面传递，从而提高近海面风速；冷 SST 异常则倾向于稳定边界层并减弱风速。这一机制在散射计风场和卫星 SST 产品中已有大量证据，尤其在 Gulf Stream、Kuroshio Extension、Agulhas Return Current 和 Southern Ocean eddies 等区域表现明显。

然而，传统观测对亚中尺度海气耦合的约束仍然不足。亚中尺度过程通常包含 O(1-50 km) 的 fronts、filaments、eddy edges 和 strain-dominated structures。这些结构具有更强的水平梯度和更短的演变时间。大气边界层是否能对这些细尺度 SST 和海洋动力结构作出连续响应，并不显然。一种可能是中尺度 SST-wind coupling 平滑延伸到亚中尺度；另一种可能是当锋面尺度足够小时，大气边界层调整时间不足，导致耦合衰减或饱和；第三种可能是 sharp fronts 和 filaments 触发不同的边界层响应，使耦合斜率、相干性、相位或风速动能异常出现 regime transition。

SWOT 为这一问题提供了新的观测窗口。与传统沿轨高度计不同，SWOT KaRIn 提供二维宽刈幅 SSH 结构，可以刻画 fronts、eddies 和 filaments 的空间形态。更重要的是，SWOT L2 产品还包含与雷达后向散射相关的 wind speed 变量。如果该变量经过质量控制后能有效描述近海面风速结构，它就不应只是辅助数据，而应成为研究亚中尺度风速响应的主资料。传统 ASCAT、ERA5 和 CCMP 风产品仍然重要，但它们更适合作为粗尺度对照和背景风场参考，而不是替代 SWOT wind speed 来支撑 sub-25-km 风速响应。

本文以 Gulf Stream 为第一试验区。Gulf Stream 具有强 SST fronts、活跃中尺度/亚中尺度过程和已知的大气边界层响应，是检验 SWOT wind speed 与 geostationary SST coupling 的理想区域。本文目标不是在 D1 阶段证明最终 regime transition，而是完成一个可复现的真实数据闭环：读取真实 SWOT 和 GOES 数据，完成质量控制和配准，生成初步耦合诊断，明确哪些信号可用、哪些结论还不能说。

本文回答三个具体问题：

1. SWOT L2 wind speed、SWOT SSH 和 GOES-16 SST 能否在 Gulf Stream 小窗口内形成有效配准样本？
2. 配准后的 SWOT wind speed 是否与 geostationary SST front 呈现可诊断的关系？
3. 不同 case 的 SST-wind 关系是否一致，还是显示出尺度依赖和背景状态调制的必要性？

---

## 2. 数据

### 2.1 SWOT L2 LR SSH Expert

本文使用 SWOT L2 LR SSH Expert NetCDF 文件。原始数据存放在仓库外：

```text
D:\AI-try\data\p01\batch_gs\swot\
```

使用变量包括：

- `wind_speed_karin`
- `ssha_karin`
- `sig0_karin`
- `wind_speed_karin_qual`
- `ssha_karin_qual`
- `sig0_karin_qual`
- `rain_flag`
- `ancillary_surface_classification_flag`
- `latitude`
- `longitude`

本文把 `wind_speed_karin` 作为主风场资料。需要强调的是，SWOT wind speed 是风速大小，不是矢量风，因此本文不计算 wind stress curl/divergence，也不讨论 `tau dot u_o` 型 oceanic wind work。

### 2.2 GOES-16 ABI L3C ACSPO SST

Gulf Stream 区域的高频 SST 来自 GOES-16 ABI L3C ACSPO SST，原始数据存放在：

```text
D:\AI-try\data\p01\batch_gs\goes16_sst\
```

使用变量包括：

- `sea_surface_temperature`
- `quality_level`
- `lat`
- `lon`

SST 被转换为摄氏度，并插值到 SWOT 像元位置。仅保留 `quality_level >= 5` 的 clear-sky SST 像元。

### 2.3 数据范围

本文的 D1 试验范围为 Gulf Stream box：

```text
82W-50W, 30N-46N
```

候选数据时间为 2023 年 9 月 1-4 日的 daylight-like SWOT passes 及其最近小时 GOES-16 SST 文件。脚本处理 8 个候选 case，其中 3 个通过质量控制和云筛选。

---

## 3. 方法

### 3.1 SWOT 质量控制

SWOT 像元保留条件如下：

```text
wind_speed_karin, ssha_karin, sig0_karin 均为有限值
wind_speed_karin_qual == 0
ssha_karin_qual == 0
sig0_karin_qual == 0
rain_flag == 0
ancillary_surface_classification_flag == 0
```

该筛选尽量保守，目的是在 D1 阶段优先保证 SWOT wind speed 和 SSH 的可解释性，而不是最大化样本量。

### 3.2 GOES SST 配准

对每个 SWOT pass，选择时间最近的 GOES-16 SST 文件。根据 SWOT 小窗口经纬度范围裁剪 GOES SST，再将 SST 和 `quality_level` 插值到 SWOT 像元。最终配准样本必须同时满足：

```text
SWOT QC 通过
GOES SST 有限值
GOES quality_level >= 5
```

### 3.3 风速动能代理量

本文使用近海面风速动能代理量：

```text
K10_SWOT = 0.5 * U10_SWOT^2
```

这里的 `K10_SWOT` 只表示风速大小对应的动能代理，单位可理解为 m2 s-2 量级，不等同于风对海洋做功，也不需要海洋表层流速。

### 3.4 初步耦合诊断

本文计算三类 D1 诊断：

1. **点对点 SST-wind 回归**

   ```text
   U10_SWOT = a SST_GOES + b
   ```

   该诊断检验同一小窗口内暖 SST 是否对应更强 SWOT wind speed。

2. **梯度关系**

   ```text
   |grad U10_SWOT| = alpha |grad SST_GOES| + residual
   ```

   该诊断尝试捕捉 front 附近风速梯度和 SST 梯度的局地关系。

3. **快速相干诊断**

   沿 SWOT 轨向对 `|grad SST|` 和 `|grad U10_SWOT|` 做平均，得到一维序列，并计算 coherence。该结果仅作为 D1 快速谱诊断，不作为最终统计证据。

### 3.5 可复现实现

全部流程由以下脚本完成：

```text
projects/p01/analysis/p01_d1_realdata_pipeline.py
```

脚本输出：

```text
projects/p01/analysis/d1_results_summary.json
projects/p01/figures/p01_d1_case*.png
projects/p01/figures/p01_d1_summary_scale_response.png
```

---

## 4. 结果

### 4.1 真实 SWOT/GOES 配准链路可运行

8 个候选 Gulf Stream SWOT/GOES case 中，3 个 case 通过质量控制和云筛选。保留 case 的基本信息如下。

| Case | SWOT 时间 | GOES 时间 | 有效 SWOT 像元 | 配准像元 | SST 覆盖率 |
|---|---|---|---:|---:|---:|
| 003_048 | 2023-09-02 15:23 UTC | 2023-09-02 16:00 UTC | 21109 | 2709 | 0.13 |
| 003_076 | 2023-09-03 15:22 UTC | 2023-09-03 16:00 UTC | 12619 | 6849 | 0.54 |
| 003_102 | 2023-09-04 13:40 UTC | 2023-09-04 14:00 UTC | 21685 | 7436 | 0.34 |

这说明真实 SWOT wind speed、SWOT SSHA 和 GOES SST 能够在 Gulf Stream 小窗口中形成有效配准样本。GOES 云筛选是当前样本量的主要限制之一。

### 4.2 SWOT wind speed 和 SST 的关系具有 case 依赖性

保留 case 的 SST、wind speed 和 `K10_SWOT` 范围如下。

| Case | SST 范围 | SWOT wind speed 范围 | `K10_SWOT` 范围 |
|---|---|---|---|
| 003_048 | 22.99-29.04 deg C | 2.74-10.95 m s^-1 | 3.75-59.90 |
| 003_076 | 26.47-29.84 deg C | 2.57-8.29 m s^-1 | 3.30-34.35 |
| 003_102 | 26.82-28.77 deg C | 4.59-12.91 m s^-1 | 10.52-83.30 |

点对点 SST-wind 回归显示两个正相关 case 和一个负相关 case：

| Case | SST-wind slope | r |
|---|---:|---:|
| 003_048 | 1.14 m s^-1 degC^-1 | 0.88 |
| 003_076 | 1.14 m s^-1 degC^-1 | 0.56 |
| 003_102 | -1.49 m s^-1 degC^-1 | -0.54 |

003_048 和 003_076 的正相关与经典 warm SST-enhanced wind speed 框架一致。003_102 的负相关说明 Gulf Stream 区域的局地关系并不总是线性正响应，可能受到背景风场、锋面方向、天气系统、云筛选和采样几何影响。

### 4.3 梯度耦合信号尚不稳健

梯度回归结果并不强：

```text
003_048: grad slope = -0.026, r = -0.052
003_076: grad slope = -0.040, r = -0.038
003_102: grad slope =  0.016, r =  0.010
```

这说明点对点 SST-wind 关系不能直接等同于亚中尺度 front-gradient coupling。当前小样本下，`|grad SST|` 与 `|grad U10_SWOT|` 的线性关系非常弱。这个结果非常重要，因为它防止我们过早声称“已经观测到亚中尺度耦合系数”。更合理的解释是：真实数据链路可行，但严格的尺度依赖耦合需要更多 case、更好的滤波和控制实验。

### 4.4 快速相干诊断提示需要更严格谱分析

三个 case 的 peak gradient coherence 均较高：

```text
003_048: peak coherence = 0.996, wavelength index scale ~2.67
003_076: peak coherence = 0.999, wavelength index scale ~11.64
003_102: peak coherence = 0.988, wavelength index scale ~2.46
```

这些数值不应被解释为最终物理相干性。当前 coherence 由沿轨平均梯度序列快速计算得到，有效自由度有限，且受云筛选、缺测分布和窗口长度影响。它的意义是提示“谱诊断值得继续做”，而不是证明 regime transition 已经存在。

---

## 5. 讨论

### 5.1 SWOT wind speed 应作为主资料

本文的核心立场是：若科学问题是“SWOT 是否揭示传统产品看不到的亚中尺度海气耦合”，那么 wind response 本身必须尽量来自 SWOT wind speed。ASCAT、ERA5 和 CCMP 可以提供中尺度对照和背景风参考，但不应替代 SWOT 来支撑 sub-25-km 风速响应。本文的真实数据试验表明，SWOT wind speed 在 Gulf Stream 小窗口中确实可以与 SST front 和 SSH 结构共同分析。

### 5.2 D1 结果支持 scale-dependent 问题，而非最终 regime transition 结论

本文最重要的科学信号不是某一个 case 的正相关，而是不同 case 之间的差异。若所有 case 都显示稳定的正 SST-wind 关系，那么经典中尺度耦合框架可能已经足够解释观测。相反，003_102 的负关系和弱梯度耦合提示：局地风速响应可能取决于背景大气状态、锋面方向、天气扰动和尺度选择。这正是 scale-dependent regime transition 问题成立的理由。

### 5.3 为什么不能过度解释

当前结果存在几个关键限制：

1. 只有 Gulf Stream，没有 Kuroshio Extension；
2. 只有 GOES SST，没有 Himawari SST；
3. 尚未加入 ASCAT/ERA5/CCMP 对照；
4. 未去除 synoptic-scale background wind；
5. GOES clear-sky 筛选可能造成采样偏差；
6. 当前相干诊断是快速估计，不是最终谱分析。

因此，本文不能声称“已经发现亚中尺度 regime transition”。更准确的表述是：本文建立了真实观测诊断链，并发现 Gulf Stream 小样本中的 SST-wind 关系存在 case 依赖性，支持后续开展严格尺度依赖检验。

### 5.4 下一阶段路线

下一阶段应按照以下顺序推进：

1. **传统产品对照。** 在相同 case 中加入 ASCAT、ERA5 和 CCMP，比较 SWOT-resolved wind structures 是否被传统产品平滑。
2. **背景风去除。** 使用 ERA5 或 CCMP 去除大尺度天气背景，重新计算 residual SST-wind coupling。
3. **尺度滤波。** 对 `U10_SWOT`、`K10_SWOT`、SST 和 SSH 做 10、20、50、100、200 km 的 band-pass 或 high-pass 分解。
4. **Kuroshio Extension 验证。** 使用 Himawari SST 复现同一流程，检验 Gulf Stream 结果是否具有跨盆地一致性。
5. **控制区。** 在弱 SST front 区域重复分析，建立 null baseline。

---

## 6. 结论

本文完成了 P01 的 D1 真实数据初稿。主要结论如下：

1. SWOT L2 wind speed、SWOT SSHA 和 GOES-16 SST 可以在 Gulf Stream 小窗口中形成有效配准样本。
2. 3 个真实 case 通过质量控制和云筛选，配准像元数为 2709-7436。
3. 两个 case 呈现正 SST-wind 关系，一个 case 呈现负 SST-wind 关系，说明 Gulf Stream 的局地风速响应并非简单普适线性关系。
4. 梯度回归目前较弱，说明点对点 SST-wind 相关不能直接等同于亚中尺度 front-gradient coupling。
5. 当前结果支持 P01 的科学问题继续推进，即检验海气耦合从中尺度到亚中尺度是否存在尺度依赖、衰减、饱和或 regime transition。
6. 最终论文级结论需要更多 case、Kuroshio Extension/Himawari 扩展、传统风产品对照、背景风去除和控制区检验。

---

## 图注

**图 1.** Gulf Stream case 003_048 的 SWOT/GOES 配准诊断。图中展示 GOES-16 SST、SWOT `wind_speed_karin`、SWOT SSHA、`|grad SST|`、`|grad SWOT wind|` 和 SST-wind 散点关系。该 case 显示正 SST-wind 关系，斜率为 1.14 m s^-1 degC^-1，r = 0.88。

**图 2.** Gulf Stream case 003_076 的 SWOT/GOES 配准诊断。该 case 保留 6849 个配准像元，显示正 SST-wind 关系，斜率为 1.14 m s^-1 degC^-1，r = 0.56。

**图 3.** Gulf Stream case 003_102 的 SWOT/GOES 配准诊断。该 case 呈现负 SST-wind 关系，斜率为 -1.49 m s^-1 degC^-1，r = -0.54，提示背景状态和尺度选择的重要性。

**图 4.** 三个有效 Gulf Stream case 的 D1 汇总图。左图为配准像元数，中图为 SST-wind 回归斜率，右图为快速梯度相干峰值。该图展示了真实数据链路可行，同时也显示不同 case 之间存在明显差异。

---

## 数据与代码可用性

原始 SWOT 和 GOES NetCDF 数据存放于本地仓库外：

```text
D:\AI-try\data\p01
```

仓库内保留可复现脚本、摘要和图件：

```text
projects/p01/analysis/p01_d1_realdata_pipeline.py
projects/p01/analysis/d1_results_summary.json
projects/p01/analysis/runbook_d1_realdata.md
projects/p01/figures/p01_d1_case*.png
projects/p01/figures/p01_d1_summary_scale_response.png
```

原始数据不提交到 GitHub，符合项目贡献指南。

---

## AI 使用声明

本文为 AI-assisted D1 初稿。AI 用于整理研究框架、生成可复现脚本、汇总结果、撰写初稿和标注风险边界。所有参考文献、数据质量控制、物理解释、结论强度和投稿判断均需要人类专家复核。本文不把 AI 输出视为最终科学结论。

---

## 参考文献种子

Small, R. J., deSzoeke, S. P., Xie, S.-P., O'Neill, L., Seo, H., Song, Q., Cornillon, P., Spall, M., & Minobe, S. (2008). Air-sea interaction over ocean fronts and eddies. *Dynamics of Atmospheres and Oceans*, 45, 274-319. DOI: 10.1016/j.dynatmoce.2008.01.001

Chelton, D. B., & Xie, S.-P. (2010). Coupled ocean-atmosphere interaction at oceanic mesoscales. *Oceanography*, 23, 52-69. DOI: 10.5670/oceanog.2010.05

O'Neill, L. W., Chelton, D. B., & Esbensen, S. K. (2010). The effects of SST-induced surface wind speed and direction gradients on midlatitude surface vorticity and divergence. *Journal of Climate*, 23, 255-281. DOI: 10.1175/2009JCLI2613.1

Morrow, R., Fu, L.-L., Ardhuin, F., et al. (2019). Global observations of fine-scale ocean surface topography with the Surface Water and Ocean Topography mission. *Frontiers in Marine Science*, 6, 232. DOI: 10.3389/fmars.2019.00232

McWilliams, J. C. (2016). Submesoscale currents in the ocean. *Proceedings of the Royal Society A*, 472, 20160117. DOI: 10.1098/rspa.2016.0117

Kaouah et al. (2025). "Submesoscale Air-Sea Interactions as Revealed by SWOT." *Geophysical Research Letters*. DOI 和正式出版信息需人工核验。
