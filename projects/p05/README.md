# P05: SWOT KaRIn 宽刈幅干涉测量验证深海混合的能量缺失假说

> 用 SWOT 二维 SSH 观测约束 Munk & Wunsch (1998) 框架中 25 年未闭合的"缺失能量"——从 ~1 TW 缩小至可接受范围。

## Status / 状态

| 项 | 内容 |
|---|---|
| 当前阶段 | ✍️ Draft（D1 AI 初稿已完成） |
| 负责人 | 匿名 |
| 目标期刊 (T1) | Geophysical Research Letters |
| 备选期刊 (T2) | Journal of Physical Oceanography |
| 备选期刊 (T3) | Remote Sensing of Environment |
| 启动日期 | 2026-06-08 |
| 预计投稿 | — |

## Scientific Question / 科学问题

深海混合维持全球海洋层结需要约 2 TW 机械能输入，但观测仅能约束约 1 TW——这 ~1 TW 的"缺失能量"是物理海洋学 25+ 年的核心未解问题。SWOT KaRIn 以 120 km 宽刈幅和 ~15 km 分辨率首次提供全球二维 SSH 观测，能够解析传统高度计遗漏的亚中尺度过程（15–50 km）对混合的能量贡献。

**核心问题：SWOT 二维 SSH 观测能否将缺失能量缩小 30–50%？亚中尺度过程的能量贡献是否被系统性低估？**

### 与现有研究的区别

- 传统高度计有效分辨率 >100 km，完全遗漏亚中尺度谱段
- 现有混合研究依赖微结构剖面（稀疏点）或数值模式（参数化依赖）
- **首次建立 SWOT 二维 SSH → 波数谱 → 能量级联 → 混合效率的系统性诊断框架**

## Hypothesis / 假设

1. 传统高度计系统性低估内部潮汐能量通量 30–50%（遗漏 15–50 km 谱段）
2. 纳入 SWOT 亚中尺度贡献后，缺失能量从 ~1 TW 缩小至 0.3–0.5 TW
3. SWOT SSH 波数谱斜率变化可直接诊断能量级联效率

## Data / 数据

- 公开数据：SWOT L3/L4 SSH、FES2022b 潮汐模型、ERA5、Argo、GEBCO、CMEMS 再分析
- 私有数据：无（本项目可全用公开数据完成）

## Method / 方法

1. SWOT SSH 异常 → 空间高通滤波（100 km）→ 潮汐去除（FES2022b）
2. 二维傅里叶波数谱 → 谱斜率诊断 → 能量级联率
3. 内潮能量通量 F_tide → Garrett & Kunze 参数化 → K_ρ 约束
4. 能量闭合评估 → Munk & Wunsch 框架对比

## D1 产出

- 分析代码：`analysis/p05_analysis.py`（591 行）
- 5 张图（300 DPI）：能量通量分布、波数谱、混合效率、能量闭合、总结
- 中文 LaTeX 初稿 + PDF：`manuscript/v1_ai_draft/P05-D1-Manuscript-CN.tex`

## Progress Log / 进度日志

| 日期 | 阶段 | 内容 | 产出 |
|---|---|---|---|
| 2026-06-08 | D0 | AI 辅助选题调研 | 文献调研（15篇）、数据可行性评估、方法框架 |
| 2026-06-08 | D1 | AI 生成分析代码 + 5 图 + LaTeX 全文 | 分析脚本、5 张图、完整中文论文初稿 + PDF |

## Key Findings

- Knowledge gap 独特：卫星 SSH 遥感 → 深海混合能量诊断链条无人建立
- SWOT 科学阶段 2023.07 开始 → 数据利用窗口刚开
- 数据全公开，南海是最佳 case study 区域
- 核心挑战：海表 SSH → 深海混合的垂向传递函数需通过 Argo + 模式辅助建立

## AI Interaction Log / AI 交互日志

- 2026-06-08: D0 调研 (见 `E:\4.23\obsidian\Spiral upward\RAW\P02-深海混合能量缺失-D0调研.md`)
- 2026-06-08: D1 生成 (见 `E:\4.23\obsidian\Spiral upward\RAW\P02-深海混合能量缺失-D0调研.md`)

## References / 参考文献

| # | 文献 | DOI | 核验状态 |
|---|---|---|---|
| 1 | Munk & Wunsch (1998) Abyssal recipes II | 10.1016/S0967-0637(98)00070-3 | ⚠️ |
| 2 | Wunsch & Ferrari (2004) Vertical mixing, energy, and the general circulation | 10.1146/annurev.fluid.36.050802.122121 | ⚠️ |
| 3 | Ferrari & Wunsch (2009) Ocean circulation kinetic energy | 10.1146/annurev.fluid.40.111406.102139 | ⚠️ |
| 4 | Egbert & Ray (2000) Tidal energy dissipation from altimetry | 10.1038/35015531 | ⚠️ |
| 5 | Garrett & Kunze (2007) Internal tide generation in the deep ocean | 10.1146/annurev.fluid.39.050905.110227 | ⚠️ |
| 6 | Fu et al. (2024) SWOT Mission Performance | — | ⚠️ 需核验 |
| 7 | Vic et al. (2019) Deep-ocean mixing by small-scale internal tides | 10.1038/s41467-019-10149-5 | ⚠️ |
| 8 | Waterhouse et al. (2014) Global patterns of diapycnal mixing | 10.1175/JPO-D-13-0104.1 | ⚠️ |
| 9 | Alford et al. (2015) Internal waves in the South China Sea | 10.1038/nature14399 | ⚠️ |
| 10 | Zhao et al. (2016) Global mode-1 M₂ internal tides | 10.1175/JPO-D-15-0101.1 | ⚠️ |
