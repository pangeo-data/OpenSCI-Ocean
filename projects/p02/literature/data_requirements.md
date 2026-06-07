# P02 Data Requirements Checklist

> SWOT 赤道拓扑波研究：完整数据需求清单
>
> 最后更新：2026-06-07

---

## 一、卫星遥感数据

### 1.1 SWOT 宽刈幅高度计（核心数据源）

| 产品 | 级别 | 来源 | 用途 | 优先级 |
|---|---|---|---|---|
| SWOT KaRIn L2 LR SSH (Low Rate) | L2 | PO.DAAC | 宽刈幅二维 SSH，赤道波经向结构解析，质量控制和误差分析 | **必需** |
| SWOT KaRIn L3 LR SSH | L3 | AVISO / PO.DAAC | 网格化产品，快速构建分析流程和原型验证 | **必需** |
| SWOT L2 Expert SSH | L2 | PO.DAAC | 严格误差控制、敏感性检验（包含更多诊断变量） | 推荐 |
| SWOT Nadir SSH | L2 | PO.DAAC | 星下点沿轨高度计，与 KaRIn 互验，补充 Hovmöller | 推荐 |

**关键参数：**
- 空间覆盖：赤道太平洋 5°S–5°N, 130°E–80°W
- 时间范围：calval phase (2023.03–2023.07, ~1天重访) + science orbit (2023.08–2025.12, ~21天重访)
- 分辨率：KaRIn 刈幅 ~120 km (2×50 km + 20 km nadir gap)，沿轨分辨率 ~2 km
- 注意事项：赤道附近地转近似退化，SSH 到流速的反演需谨慎；潮汐校正质量需检查

### 1.2 传统沿轨高度计

| 产品 | 来源 | 用途 | 优先级 |
|---|---|---|---|
| Jason-3 GDR SSH | CMEMS / PO.DAAC | 沿轨 Hovmöller 追踪赤道 Kelvin 波传播，长时间序列 | **必需** |
| Sentinel-6 MF SSH | CMEMS / EUMETSAT | 接替 Jason-3 的高精度参考轨道高度计 | **必需** |
| Sentinel-3A/B SSH | CMEMS | 补充沿轨覆盖，增加采样密度 | 推荐 |
| HY-2B/C/D SSH | NSOAS | 中国高度计数据，增加赤道太平洋过境频次 | 可选 |
| SARAL/AltiKa SSH | AVISO | Ka 波段高度计，小尺度信号更敏感 | 可选 |

### 1.3 多源融合 SSH（网格化产品）

| 产品 | 来源 | 用途 | 优先级 |
|---|---|---|---|
| DUACS/AVISO L4 gridded SSH (daily) | CMEMS (SEALEVEL_GLO_PHY_L4) | 补足 SWOT 时间采样不足；赤道 Hovmöller 事件识别的主力数据；大尺度背景场去除 | **必需** |
| CMEMS SSH L4 (near-real-time) | CMEMS | 近实时产品用于最新事件追踪 | 可选 |

**注意：** DUACS 是补充而非替代 SWOT。DUACS 空间分辨率 ~100 km，无法解析赤道波经向精细结构。

### 1.4 海面温度（SST）

| 产品 | 来源 | 用途 | 优先级 |
|---|---|---|---|
| OSTIA L4 daily SST | CMEMS (SST_GLO_SST_L4) | TIW 识别（经典 SST 锋面振荡）、冷舌锋面位置标注 | **必需** |
| NOAA OISST v2.1 (daily, 0.25°) | NOAA/NCEI | TIW 和冷舌气候态参考，长时间序列 | **必需** |
| MUR L4 SST (daily, 0.01°) | PO.DAAC | 高分辨率 SST，亚中尺度锋面识别 | 推荐 |
| MW+IR OI SST (REMSS) | REMSS | 微波 SST 穿云能力强，赤道热带多云区有优势 | 推荐 |

### 1.5 卫星散射计/风场

| 产品 | 来源 | 用途 | 优先级 |
|---|---|---|---|
| ASCAT MetOp-B/C 25km winds | CMEMS / KNMI | 西太平洋风暴发（Westerly Wind Burst）识别——Kelvin 波激发源 | **必需** |
| CCMP V3.1 wind (6-hourly, 0.25°) | REMSS | 多源融合风场，时间连续性好 | 推荐 |

### 1.6 海洋颜色/叶绿素

| 产品 | 来源 | 用途 | 优先级 |
|---|---|---|---|
| GlobColour merged Chl-a (daily, 4km) | CMEMS (OCEANCOLOUR_GLO) | TIW 识别辅助（TIW 引起赤道冷舌叶绿素带摆动） | 可选 |
| MODIS Aqua/VIIRS Chl-a | NASA OB.DAAC | 高分辨率叶绿素，TIW 波前可视化 | 可选 |

### 1.7 卫星重力/大地水准面

| 产品 | 来源 | 用途 | 优先级 |
|---|---|---|---|
| EIGEN-6C4 / EGM2008 geoid | ICGEM | SWOT SSH 到动力地形（ADT）的转换基准 | 背景依赖（SWOT L2/L3 已内置） |
| DTU MSS (mean sea surface) | DTU Space | SSH anomaly 计算的参考面 | 背景依赖 |

---

## 二、现场观测数据

### 2.1 锚系浮标阵列

| 产品 | 来源 | 用途 | 优先级 |
|---|---|---|---|
| TAO/TRITON 赤道浮标阵列 | NOAA/PMEL | Kelvin 波过境验证（温跃层深度变化、表层流速变化）；赤道波事件独立确认 | **必需** |
| PIRATA (大西洋赤道浮标) | 扩展阶段用 | 跨洋盆对比（Phase 2 扩展到大西洋时使用） | 可选（后期） |
| RAMA (印度洋赤道浮标) | 扩展阶段用 | 跨洋盆对比 | 可选（后期） |

**TAO/TRITON 关键变量：** 海面温度、20°C 等温线深度（温跃层代理）、表层流速（u, v）、次表层温度剖面。

**注意：** TAO 阵列近年来维护退化，部分浮标数据中断，需检查 2023–2025 时段实际可用浮标位置。

### 2.2 Argo 浮标

| 产品 | 来源 | 用途 | 优先级 |
|---|---|---|---|
| Argo 温盐剖面 (delayed mode) | Argo GDAC (Ifremer/USGODAE) | 等效浅水模型相速度估计（需要温跃层深度和层化强度 N²）| **必需** |
| Argo 实时剖面 | Argo GDAC | 最新事件的近实时层化估计 | 推荐 |

**关键诊断：** 从 Argo T/S 剖面计算约化重力 g' 和等效深度 H_eq → 等效浅水相速度 c = √(g'·H_eq)，这是理论频散关系和 Δω_eff 估计的基础。

### 2.3 验潮站

| 产品 | 来源 | 用途 | 优先级 |
|---|---|---|---|
| UHSLC 太平洋岛屿验潮站 | U. Hawaii Sea Level Center | Kelvin 波到达时间独立验证；岛屿散射前后的振幅变化 | 推荐 |

**关键站点：** 圣诞岛 (Christmas Island)、塔拉瓦 (Tarawa)、马朱罗 (Majuro)、加拉帕戈斯 (Galápagos) — 这些站位直接位于赤道 Kelvin 波传播路径上，可以追踪波前到达和岛屿绕射。

### 2.4 走航/断面观测

| 产品 | 来源 | 用途 | 优先级 |
|---|---|---|---|
| 赤道太平洋 CTD 断面（历史） | WOCE/CLIVAR/GO-SHIP | 赤道层化气候态 | 可选 |

---

## 三、海洋模式与再分析数据

### 3.1 全球海洋再分析

| 产品 | 分辨率 | 来源 | 用途 | 优先级 |
|---|---|---|---|---|
| GLORYS12 v1 | 1/12° daily | CMEMS (GLOBAL_MULTIYEAR_PHY) | 背景流场（U, V）、相对涡度 ζ、经向剪切 ∂U/∂y — Λ 参数分母项估计 | **必需** |
| ECCO v4r4 / v5 | 1/2° → 1/3° | NASA/JPL | 动力一致的海洋状态估计；赤道动力学参考 | 推荐 |
| HYCOM GOFS 3.1 | 1/12° 3-hourly | HYCOM.org | 高时间分辨率流场，内潮能量估计 | 推荐 |

**GLORYS 关键输出变量：** SSH, U, V (3D), T, S → 计算背景剪切 |∂_y U|、相对涡度 ζ = ∂v/∂x - ∂u/∂y、Okubo-Weiss 参数。

### 3.2 高分辨率数值模拟（OSSE 和预实验用）

| 产品 | 分辨率 | 来源 | 用途 | 优先级 |
|---|---|---|---|---|
| LLC4320 MITgcm | ~1/48° (2 km), hourly | NASA ECCO | "完美数据"预实验——在已知真值上验证整套分析流程；包含内潮、亚中尺度、赤道波 | **强烈推荐** |
| HYCOM 1/25° nested runs | ~4 km | 视具体运行 | 备选高分辨率数据 | 可选 |

**LLC4320 使用策略：**
1. 从 LLC4320 SSH 中提取赤道太平洋完整 Kelvin/Yanai/Rossby/TIW 信号（"真值"）
2. 按 SWOT 科学轨道采样 → 加 KaRIn 类噪声 → 生成模拟 SWOT 观测
3. 用模拟观测跑全套分析（事件识别、模式分解、鲁棒性指标、Λ 参数）
4. 与真值对比 → 量化方法误差和灵敏度

### 3.3 大气再分析

| 产品 | 分辨率 | 来源 | 用途 | 优先级 |
|---|---|---|---|---|
| ERA5 surface fields | 0.25°, hourly | CDS (Copernicus) | 风应力 (τ_x, τ_y)：识别西太平洋风暴发（WWB），确认 Kelvin 波激发源 | **必需** |
| ERA5 pressure level winds | 0.25° | CDS | 大气环流背景态 | 可选 |

**ERA5 关键变量：** 10m 风速 (u10, v10)、风应力 (τ_x, τ_y)、海表气压 (msl)。

### 3.4 潮汐模式

| 产品 | 来源 | 用途 | 优先级 |
|---|---|---|---|
| FES2022 / FES2014 | AVISO / LEGOS | 内潮能量估计（E_IT）；SWOT SSH 中的潮汐残差评估 | **必需** |
| HRET (High Resolution Empirical Tide) | E. Zaron, OSU | 经验正压潮/内潮模型，SWOT 潮汐校正参考 | 推荐 |
| TPXO9 | OSU | 全球潮汐模型，验潮站比较 | 可选 |

**内潮能量是 Λ 参数的重要分母项。** 赤道太平洋（尤其是吉尔伯特群岛 Gilbert Islands 和莱恩群岛 Line Islands 附近）是全球内潮最活跃的区域之一。

---

## 四、理论与辅助数据

### 4.1 海底地形

| 产品 | 分辨率 | 来源 | 用途 | 优先级 |
|---|---|---|---|---|
| GEBCO 2024 | 15 arc-sec (~450m) | GEBCO | 岛屿链位置、海底地形交互区标注（岛屿散射是拓扑保护失效的关键场景） | **必需** |
| ETOPO 2022 | 15 arc-sec | NOAA/NCEI | 备选地形数据 | 可选 |
| Smith & Sandwell v23.1 | ~1 arc-min | SIO/UCSD | 重力派生地形 | 可选 |

**关键地形特征：**
- 吉尔伯特群岛 (Gilbert Islands, ~173°E) — Kelvin 波传播路径上的主要岛链障碍
- 莱恩群岛 (Line Islands, ~160°W) — 包含 Palmyra, Kiritimati (Christmas Island)
- 加拉帕戈斯群岛 (Galápagos, ~90°W) — 赤道东太平洋，波前终端
- 马绍尔群岛 (Marshall Islands, ~170°E)

### 4.2 等效浅水理论参考

| 内容 | 来源 | 用途 | 优先级 |
|---|---|---|---|
| 赤道浅水模型色散关系解析解 | Matsuno (1966); Vallis (2017) | Kelvin 波: ω = c·k_x; Yanai 波: ω 满足特征方程；Rossby 波、Poincaré 波频散关系 → 理论基准 | **必需** |
| 拓扑不变量（Chern 数 ±2）计算 | Delplace et al. (2017) | Berry 曲率和 Chern 数的参数空间 (k_x, k_y, f/c) 计算方法 → Figure 1 理论框架 | **必需** |
| Bulk-interface correspondence 推广 | Venaille & Delplace (后续 JFM 文章) | 从参数空间拓扑到物理空间边界态的严格对应 → 理论深度 | 推荐 |
| 等效深度 H_eq 与 baroclinic mode 对应 | Gill (1982); Vallis (2017) | 从 Argo 层化推算各斜压模态的等效浅水相速度 c_n → Δω_eff 估计 | **必需** |

### 4.3 合成实验（OSSE）所需构建的模拟数据

| 内容 | 方法 | 用途 | 优先级 |
|---|---|---|---|
| 1.5 层赤道浅水模型合成信号 | 赤道 β-平面浅水方程数值积分 | 生成理想 Kelvin/Yanai/Rossby 波信号，已知真值 | **必需** |
| TIW-like 扰动场 | 线性不稳定性模型 or 从 HYCOM/LLC4320 提取 | 叠加到合成波场上，模拟真实海洋背景扰动 | **必需** |
| SWOT 轨道采样模拟器 | SWOT Simulator (JPL/CNES) | 按真实 SWOT 轨道对合成场采样 + 加仪器噪声 | **必需** |
| KaRIn 噪声模型 | SWOT Simulator 内置 | 真实的 SWOT 观测噪声特征 | **必需** |

**SWOT Simulator 说明：** JPL/CNES 联合开发的 SWOT 模拟工具，可以将任意 SSH 场按照 SWOT 真实轨道参数采样，并添加 KaRIn 仪器噪声、滚动误差、基线膨胀误差等。这是 OSSE 实验的标准工具。

---

## 五、数据获取优先级总结

### 第一批（Phase 1 可行性验证，立即下载）

| # | 数据 | 来源 | 大小估计 |
|---|---|---|---|
| 1 | DUACS L4 daily SSH (赤道太平洋, 2023–2025) | CMEMS | ~2 GB |
| 2 | SWOT L3 LR SSH (赤道太平洋, 全时段) | PO.DAAC / AVISO | ~5–10 GB |
| 3 | ERA5 wind stress τ_x, τ_y (赤道太平洋, 2023–2025) | CDS | ~1 GB |
| 4 | OSTIA / OISST daily SST (赤道太平洋, 2023–2025) | CMEMS / NOAA | ~1 GB |
| 5 | TAO/TRITON 浮标数据 (赤道太平洋, 2023–2025) | NOAA/PMEL | ~100 MB |
| 6 | GEBCO 2024 bathymetry (赤道太平洋) | GEBCO | ~500 MB |

### 第二批（Phase 2 OSSE 和方法开发）

| # | 数据 | 来源 | 大小估计 |
|---|---|---|---|
| 7 | LLC4320 SSH (赤道太平洋区域子集) | NASA ECCO (via PO.DAAC) | ~50–200 GB |
| 8 | SWOT Simulator 工具 | GitHub (CNES/SWOT-simulator) | 代码 |
| 9 | Argo 剖面 (赤道太平洋, 2023–2025) | Argo GDAC | ~500 MB |
| 10 | FES2022 潮汐模型 (赤道太平洋) | AVISO | ~2 GB |

### 第三批（Phase 3 真实事件分析）

| # | 数据 | 来源 | 大小估计 |
|---|---|---|---|
| 11 | SWOT L2 Expert SSH (选定事件轨道) | PO.DAAC | ~10–20 GB |
| 12 | GLORYS12 日均流场 U, V (赤道太平洋, 2023–2025) | CMEMS | ~10 GB |
| 13 | HYCOM GOFS 3.1 3-hourly (赤道太平洋) | HYCOM.org | ~20 GB |
| 14 | UHSLC 验潮站 (太平洋岛屿) | U. Hawaii | ~50 MB |
| 15 | Jason-3 / Sentinel-6 沿轨 SSH | CMEMS | ~2 GB |

---

## 六、数据访问凭证备注

| 平台 | 注册地址 | 涉及数据 |
|---|---|---|
| CMEMS (Copernicus Marine) | marine.copernicus.eu | DUACS SSH, GLORYS, OSTIA SST, Ocean Colour |
| PO.DAAC (NASA Earthdata) | urs.earthdata.nasa.gov | SWOT, MUR SST, ECCO, LLC4320 |
| CDS (Copernicus Climate) | cds.climate.copernicus.eu | ERA5 |
| AVISO | aviso.altimetry.fr | SWOT L3, FES2022, DTU MSS |
| NOAA/PMEL | pmel.noaa.gov/tao | TAO/TRITON |
| Argo GDAC | data-argo.ifremer.fr | Argo 剖面 |
| GEBCO | gebco.net | 海底地形 |
| UHSLC | uhslc.soest.hawaii.edu | 验潮站 |
