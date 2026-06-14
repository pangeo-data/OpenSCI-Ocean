# 论文方向（notes/paper_direction.md）

## 工作标题
**EN**: Wave-ice feedback amplifies Antarctic sea ice loss: fetch lengthening, marginal ice zone erosion, and ice shelf exposure since the 2016 regime shift
**CN**: 波浪-海冰正反馈加速南极海冰损失：2016年状态转变以来的 fetch 增长、边缘冰区侵蚀与冰架暴露

## 核心科学问题
2016年南极海冰发生显著状态转变后，海冰退缩是否通过延长风区（fetch）→ 增强波浪 → 加速边缘冰区破碎 → 暴露冰架前缘的正反馈链，使冰损失自我加速？该反馈环的强度是否足以构成不可逆的临界行为？

## 切入的 gap
- 波浪-海冰正反馈已在理论和模型中被提出（Squire 2020; Roach et al. 2022），但**尚无基于长期再分析数据（45年）对南极 fetch-SWH-MIZ 反馈的定量观测诊断**
- Massom et al. (2018, Nature) 证明了波浪→冰架崩解的机制，但仅针对 Larsen/Wilkins 历史事件，**未量化 2016 年后全南极冰架前方海冰缓冲带的系统性退缩**
- P04 v1 已证明 SIC 在 2016 年突变（Pettitt p=0.004），但因果方向搞反了——新方向将因果翻转为"海洋→冰"

## 预期核心发现
1. 2016年后南极冰缘区 fetch 增长 15-30%，ERA5 SWH 在 MIZ 区增强 10-20%
2. MIZ 宽度（SIC 15%-80%带）系统性收窄，波浪穿透深度增加
3. 环南极主要冰架（Ross/Filchner-Ronne/Amery/Larsen C）前方海冰缓冲天数显著减少
4. fetch-SWH-MIZ 构成正反馈环：Granger 因果 fetch→SWH→MIZ宽度 成立

## 差异化（vs 最接近文献）
- vs Massom et al. (2018, Nature)：他们做冰架崩解的**定性机制**，我们做 fetch-SWH-MIZ-冰架缓冲的**定量时间序列诊断**，覆盖全南极45年
- vs Squire (2020, Phil Trans A)：他们做波浪-冰相互作用的综述/理论框架，我们做**基于 ERA5 的实证闭环验证**
- vs Kohout et al. (2026, The Cryosphere)：他们做波浪对海冰融化/反照率的影响（wave flooding/pulverisation），我们做 **fetch→SWH 的正反馈环** 和冰架暴露的联合诊断

## 数据策略
| 数据类型 | 具体数据集 | 角色 | 主要/辅助 |
|---|---|---|---|
| 再分析-波浪 | ERA5 SWH/MWP/MWD (1979-2024, 0.5°, 月均) | 核心：波浪场时序 | 主要 |
| 再分析-风场 | ERA5 u10/v10 (已有, 0.25°) | 核心：fetch 计算 | 主要 |
| 再分析-海冰 | ERA5 SIC (已有, 0.25°) | 核心：MIZ 边界/fetch 终点 | 主要 |
| 卫星海冰指数 | NSIDC Sea Ice Index (已有) | 独立验证 | 主要 |
| 卫星高度计 | CMEMS DUACS SLA (已有, 0.125°) | 辅助：涡旋背景 | 辅助 |
| 冰架位置 | MEaSUREs/BedMachine/NSIDC | 冰架前缘位置 | 辅助 |
| 气候指数 | AAO/SAM/Niño3.4 (已有) | 控制变量 | 辅助 |

## 目标期刊
Nature Communications（主）/ GRL（备选，若精简到 5 图 4500 词）

## 用户确认时间
2026-06-14
