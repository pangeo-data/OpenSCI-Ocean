# 研究方向（DIRECTION.md）— P04 v2 方向重建

> 立项种子（v0.0）。**写完即冻结**——v0.1 起所有方向调整通过 README.md 的版本号迭代。
> ClaudeA 与 ClaudeB 都会读这份文件作为项目"做什么"的 single source of truth。
>
> **注意**：本文件取代 P04 v1 的 DIRECTION.md（已存档为负结果）。v1 尝试"冰→EKE"因果链失败，v2 翻转因果方向为"海洋（浪）→冰"。

## 1. 主题与工作标题

- **工作标题（EN）**: Wave-ice feedback amplifies Antarctic sea ice loss: fetch lengthening, marginal ice zone erosion, and ice shelf exposure since the 2016 regime shift
- **中文一句话**: 波浪-海冰正反馈加速南极海冰损失——2016年状态转变以来的 fetch 增长、边缘冰区侵蚀与冰架暴露
- **核心科学问题**: 2016年南极海冰状态转变后，海冰退缩是否通过延长 fetch → 增强波浪 → 加速 MIZ 破碎 → 暴露冰架前缘的正反馈链，使冰损失自我加速？
- **差异化（vs Massom 2018 Nature）**: Massom 做了冰架崩解的定性机制（3个历史事件），我们做 fetch-SWH-MIZ-冰架缓冲的**定量时间序列诊断**，覆盖全南极 45 年，闭合正反馈环

## 2. 硬约束

| 项 | 值 |
|---|---|
| 投稿目标 / venue | Nature Communications（主）/ GRL（备选） |
| 篇幅上限 | NC: ~5000 词 + 5-6 主图 + SI; GRL: ≤4500 词 + ≤5 图 |
| Deadline | 无硬性截止；Phase 1 可行性验证目标 2 周 |
| 算力 | 本地 Mac（分析/绘图）+ 远程 WSL（大数据下载） |
| 数据 | 全部公开数据（ERA5 / NSIDC / CMEMS） |
| Case / 对象 | 南大洋 40°S–75°S，全经度，1979–2024 |

### 2.5 计算环境

| 项 | 值 |
|---|---|
| **执行环境** | 混合（本地 Mac + 远程 WSL） |
| **远程连接** | `ssh think@100.111.65.40`（Tailscale） |
| **本地 Python** | 3.14.3 (homebrew) |
| **本地关键依赖** | xarray, numpy, scipy, matplotlib, cartopy, netCDF4, copernicusmarine |
| **原始数据目录** | `/Users/zhulin/aitest/OpenSCI-Ocean/data/` |
| **输出目录** | `/Users/zhulin/aitest/OpenSCI-Ocean/projects/p04/` |

### 2.6 数据策略

| 数据类型 | 具体数据集 | 时段 | 分辨率 | 角色 | 状态 |
|---|---|---|---|---|---|
| 再分析-风场 | ERA5 u10/v10 | 1979-2024 | 0.25°, 月均 | fetch 计算 | ✅ 已有 |
| 再分析-海冰 | ERA5 SIC | 1979-2024 | 0.25°, 月均 | MIZ 边界 | ✅ 已有 |
| 再分析-波浪 | ERA5 SWH/MWP/MWD | 1979-2024 | 0.5°, 月均 | 波浪场 | ❌ 需下载 |
| 卫星海冰 | NSIDC Sea Ice Index | 1979-2024 | 月均 | 独立验证 | ✅ 已有 |
| 卫星高度计 | CMEMS DUACS SLA | 1993-2024 | 0.125°, 月均 | 辅助 | ✅ 已有 |
| 气候指数 | AAO/SAM/Niño3.4 | 1979-2024 | 月均 | 控制变量 | ✅ 已有 |
| 冰架位置 | MEaSUREs Antarctic boundaries | 静态 | — | 冰架前缘 | ❌ 需下载 |

## 3. 核心科学假设（可证伪）

**H1 (Fetch-SWH link)**: 2016年后南极冰缘区 fetch 系统性增长（>15%），导致 ERA5 SWH 在 MIZ 邻近海域同步增强。
- 证伪条件：fetch 增长 <5% 或 SWH 无显著趋势

**H2 (MIZ erosion feedback)**: fetch 增长和 SWH 增强与 MIZ 宽度收窄存在 Granger 因果关系，构成正反馈环。
- 证伪条件：Granger 因果不成立，或 MIZ 宽度无显著变化

**H3 (Ice shelf buffer loss)**: 2016年后主要冰架前方的海冰缓冲天数（SIC>15% 的年度天数）显著减少，冰架暴露于波浪的时间增加。
- 证伪条件：缓冲天数无显著变化

**H4 (Climate feedback loop)**: fetch-SWH-MIZ 正反馈的强度在 2016 年后发生结构性增强（feedback gain 增大），暗示可能的不可逆转换。
- 证伪条件：反馈增益无变化或减弱

## 4. 方法框架

```
Phase 0: 数据准备
  下载 ERA5 波浪产品 → 与已有风场/海冰对齐

Phase 1: Fetch 计算
  对每个网格点，沿主风向追踪开阔水面距离（SIC<15%为开阔水面）
  → 月度 fetch 场 → 2016 前后对比

Phase 2: SWH-Fetch-MIZ 诊断
  定义 MIZ = SIC 15%–80% 带
  MIZ 宽度 = 该带的经向跨度
  → fetch vs SWH 相关 → SWH vs MIZ 宽度 Granger 因果
  → 闭合正反馈环：fetch↑ → SWH↑ → MIZ 收窄 → fetch↑

Phase 3: 冰架缓冲带诊断
  选取 5 个主要冰架（Ross / Filchner-Ronne / Amery / Larsen C / Totten）
  → 冰架前方 200 km 扇区的 SIC 月度时序
  → "缓冲天数"（SIC>15% 的月数/年）→ 2016 前后对比
  → 缓冲天数 vs 区域 SWH 的关系

Phase 4: 反馈增益估计
  构建简化反馈模型：dSIC/dt = -α·SWH - β·fetch + γ·SIC + noise
  → 滚动窗口回归估计 α, β → 2016 前后 feedback gain 变化
  → 与 P04 v1 的 Pettitt 突变检测对接
```

## 5. 预期图表（5-6 张）

1. **Fig.1 概念图**: 正反馈环示意 + 南极地图（MIZ/冰架位置标注）
2. **Fig.2 Fetch 变化**: (a) 2016 前 fetch 气候态 (b) 2016 后 (c) 差值 + 显著性
3. **Fig.3 SWH-MIZ 时序**: (a) MIZ 邻近 SWH 年际变化 (b) MIZ 宽度年际变化 (c) Granger 因果
4. **Fig.4 冰架缓冲带**: 5 个冰架的缓冲天数时序 + 2016 突变检测
5. **Fig.5 反馈闭环**: (a) fetch→SWH→MIZ 的因果网络 (b) 滚动 feedback gain
6. **Fig.6 气候情景**: 反馈增益外推 → 冰架暴露风险预估

## 6. 风险与止损

| 风险 | 严重性 | 缓解 |
|---|---|---|
| ERA5 波浪模型在 SIC>30% 区不计算波浪 | 高 | 聚焦 MIZ 外侧（SIC<30%），用 fetch 代替直接 SWH |
| fetch 计算在月均尺度可能被平滑 | 中 | 用冬/夏季节分层，或用日均数据做敏感性测试 |
| MIZ 宽度定义敏感 | 中 | 对 15%/30%/50% 阈值做敏感性分析 |
| 正反馈可能太弱无法检测 | 高 | 若 H2 被证伪，转为描述性论文"2016后fetch/SWH/MIZ变化的联合诊断" |

## 7. P04 v1 → v2 继承关系

| v1 资产 | v2 复用方式 |
|---|---|
| Pettitt 突变检测 | 直接复用于 fetch/SWH/MIZ 突变检测 |
| τ_eff 空间分析框架 | 改造为 fetch 空间分析 |
| 区域掩膜/权重代码 | 直接复用 |
| SIC 2016 突变结论 | 作为出发点事实 |
| "因果时序倒挂"教训 | v2 先验证时序再做因果（先 fetch 再 SWH 再 MIZ） |
