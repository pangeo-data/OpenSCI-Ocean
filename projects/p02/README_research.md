# P02 Topological Equatorial Waves · 研究项目主控文件

> **v0.1** — ClaudeA 初稿，基于 DIRECTION.md + 参与者研究方案 + Delplace 2017 标杆拆解。
> 待 ClaudeB R01 审查。

---

## 0. 元数据

| 项 | 值 |
|---|---|
| 项目代号 | P02-TopologicalEquatorialWaves |
| 创建日期 | 2026-06-07 |
| 维护者 | ClaudeA (drafter) |
| 主控文件版本 | v0.1 |
| 投稿目标 | Nature Communications |
| Phase 1 Deadline | 2026-07-05（4 周可行性验证） |

---

## 1. 研究背景与动机

### 1.1 理论基础

Delplace, Marston & Venaille (2017, Science) 证明赤道 Kelvin 和 Yanai 波具有拓扑起源。在旋转浅水模型中，地球自转导致 Coriolis 参数 f 在赤道变号，破坏时间反演对称性。Bulk Poincaré 波模在参数空间 (k_x, k_y, f/c) 中具有非平凡 Chern 数 ±2，通过 bulk-boundary correspondence 保证赤道存在恰好两个单向边界态——Kelvin 波和 Yanai 波——填充 Rossby-Poincaré 频率间隙。

关键推论：拓扑保护不依赖地球的精确几何（"even a misshapen sphere would support the waves"），Kelvin/Yanai 波对扰动（如地形散射）具有免疫性——不存在背向散射。

### 1.2 观测缺口

上述理论完全建立在理想化线性旋转浅水模型上。真实海洋有：
- 风强迫和耗散（非 Hermitian）
- 背景流剪切（破坏模型对称性）
- 热带不稳定波（TIW）、涡旋、内潮（强扰动场）
- 岛屿链散射（吉尔伯特群岛、莱恩群岛）
- 非线性波-波相互作用

**核心缺口**：拓扑保护预言在真实海洋中是否留下可观测的动力学指纹，从未被系统检验。

### 1.3 SWOT 观测窗口

传统 nadir 高度计（Jason/Sentinel-6）提供沿轨一维 SSH 剖面，可做 Hovmöller 追踪但无法解析赤道波的二维经向结构。SWOT KaRIn 宽刈幅高度计（~120 km 刈幅宽度，~2 km 沿轨分辨率）首次提供赤道波的二维 SSH 快照，使得解析 Kelvin 波的经向 Gaussian 衰减结构、Yanai 波的反对称模态成为可能。

SWOT 的局限：科学轨道 ~21 天重访，赤道 Kelvin 波相速度 ~2.5 m/s（穿越太平洋 ~2 个月），需与 DUACS 日均产品融合弥补时间采样不足。

---

## 2. 科学问题（SQ）

### SQ1: SWOT 能否观测到赤道 Kelvin/Yanai 波的二维拓扑指纹？

"拓扑指纹"指：赤道局域结构（Gaussian 经向衰减）、东传相速度（~2.5 m/s for 1st baroclinic Kelvin）、频散关系与等效浅水理论一致、Kelvin/Yanai 与 Rossby/TIW/亚中尺度信号可分离。

**可证伪**：若 SWOT KaRIn 数据中无法在赤道太平洋识别出东传 Kelvin 波事件的二维 SSH 结构（经向半宽度、相速度、振幅与理论不符），则 SQ1 不成立，后续工作终止。

### SQ2: Kelvin/Yanai 波是否比非拓扑模式表现出更高的传播鲁棒性？

不是单独证明 Kelvin 波"稳定"，而是做对照比较：
- Kelvin/Yanai vs. Rossby/TIW/涡旋信号
- 在相同背景扰动强度下，比较下游相干保持率、背向散射指数、模式转换率、赤道泄漏率

**可证伪**：若 Kelvin/Yanai 波的四个鲁棒性指标与 Rossby/TIW 对照组无统计显著差异（p > 0.05），则拓扑保护在观测层面不可区分。

### SQ3: 拓扑保护在什么条件下失效？

预期：保护是条件性的（conditional robustness），受有效谱隙-扰动强度比 Λ 控制。

Λ = Δω_eff / (perturbation strength)

- Λ >> 1 → 高相干、低散射（保护有效）
- Λ ~ 1 → 模式转换、赤道泄漏、相干丧失（保护失效）

**可证伪**：若 Λ 与鲁棒性指标之间无显著相关（R² < 0.3 或 p > 0.05），则 Λ 参数不具备解释力，需要替代框架。

---

## 3. 研究区域与案例选择

### 3.1 主研究区

**赤道太平洋**：5°S–5°N, 130°E–80°W

理由：
- Kelvin 波活动最强（与 ENSO 动力学紧密关联）
- 西太平洋风暴发（WWB）是 Kelvin 波的明确激发源
- TIW、冷舌锋面、岛屿链（Gilbert, Line Islands）共存——天然的扰动实验场
- TAO/TRITON 浮标阵列提供独立验证

### 3.2 事件选择策略

聚焦 **3–5 个"黄金事件"**（而非大而全的事件库）：
- SWOT KaRIn 覆盖最好（多个轨道交叉）
- 扰动环境最清晰（明确经过 TIW 区或岛屿）
- 有 TAO 浮标同步验证

优先检查 **SWOT calval 快速采样期**（2023.03–2023.07，~1 天重访）是否有可用 Kelvin 波事件。

---

## 4. 数据源

详见 `literature/data_requirements.md`，此处仅列关键数据及阶段分配。

### Phase 1 数据（立即下载）

| 数据 | 来源 | 用途 |
|---|---|---|
| DUACS L4 daily SSH | CMEMS | Hovmöller 事件识别（主力） |
| SWOT L3 LR SSH | AVISO/PO.DAAC | 二维经向结构解析 |
| ERA5 wind stress (τ_x, τ_y) | CDS | WWB 识别（Kelvin 波源） |
| OSTIA daily SST | CMEMS | TIW 和冷舌标注 |
| TAO/TRITON equatorial moorings | NOAA/PMEL | 独立验证 |
| GEBCO 2024 bathymetry | GEBCO | 岛屿位置标注 |

### Phase 2 数据（OSSE 和方法开发）

| 数据 | 来源 | 用途 |
|---|---|---|
| LLC4320 SSH (赤道太平洋子集) | PO.DAAC/ECCO | 完美数据预实验 |
| SWOT Simulator | GitHub CNES | 轨道采样 + 噪声模拟 |
| Argo T/S 剖面 | GDAC | 等效浅水相速度估计 |
| FES2022 潮汐模型 | AVISO | 内潮能量估计 |

### Phase 3 数据（真实事件分析）

| 数据 | 来源 | 用途 |
|---|---|---|
| SWOT L2 Expert SSH | PO.DAAC | 精细误差分析 |
| GLORYS12 daily U, V | CMEMS | 背景流、涡度、剪切 |
| UHSLC 太平洋岛屿验潮站 | U. Hawaii | 岛屿散射前后振幅对比 |

---

## 5. 方法学

### 5.0 Phase 1: 传统方法先行（不依赖 AI）

Phase 1 完全使用传统海洋学方法，目的是验证可行性：

1. **SSH anomaly Hovmöller**：从 DUACS L4 daily SSH 构建赤道太平洋 Hovmöller 图（沿赤道平均 2°S–2°N），识别东传信号（斜率对应相速度）
2. **Kelvin 波事件识别**：相速度 ~2.5 m/s 的东传信号 + ERA5 风应力异常（WWB）源确认
3. **SWOT 2D 快照**：对已识别事件，提取 SWOT KaRIn 轨道覆盖，检查经向结构
4. **初步模式分离**：带通滤波（沿赤道东传 k>0 分量）+ 经向 EOF 分析

**Phase 1 止损点**：若 Hovmöller 中无法识别清晰的东传 Kelvin 波事件（≥3 个），或 SWOT 覆盖不足以解析经向结构，则该方向不可行，建议放弃或大幅调整。

### 5.1 Module A: 赤道波事件库构建

在 Phase 1 传统方法基础上扩展：

事件库字段：事件 ID、时间窗口、源区（WWB 位置）、传播路径、相速度、振幅、经向 e-folding 尺度、经过的扰动区域（TIW/岛屿/剪切带）、上游/下游分析窗口、SWOT 覆盖质量评分。

### 5.2 Module B: 物理约束 AI 模式分解（Phase 2）

Physics-guided multimodal decomposition framework。

**输入**: SSH_SWOT, SSH_DUACS, τ_x, τ_y, SST, U, V, N², bathymetry

**输出**: η = η_K + η_Y + η_R + η_TIW + η_sub + η_tide + ε

**架构推荐**: U-Net/ConvLSTM reconstruction + physics-guided latent decomposition + uncertainty ensemble

**物理约束损失函数**:

L = L_rec + λ₁L_disp + λ₂L_meridional + λ₃L_direction + λ₄L_energy + λ₅L_uncertainty

约束含义：重建误差、频散关系约束、赤道经向结构约束、传播方向约束、能量连续性约束、不确定性约束。

**OSSE 验证**（mandatory）：在 LLC4320 合成数据上训练和验证，与传统方法（EOF、波数-频率滤波）对比。

**简化策略**：若完整 AI 框架在 Phase 2 时间内无法完成，退化为传统滤波 + 物理约束后处理，核心鲁棒性分析不依赖 AI。

### 5.3 Module C: 拓扑鲁棒性指标

四个诊断量，对每个事件在扰动区上/下游计算：

| 指标 | 定义 | 物理含义 |
|---|---|---|
| 背向散射指数 B | E_west / (E_east + E_west) | 拓扑保护 → B 低 |
| 相干保持率 C | \|⟨A_up · A*_down⟩\| / √(⟨\|A_up\|²⟩⟨\|A_down\|²⟩) | 波前完整性 |
| 模式转换率 M | (E_R + E_TIW + E_sub) / (E_total) | 能量转移到非拓扑模式 |
| 赤道泄漏率 L | E(\|y\| > y_c) / E_total | 能量逃出赤道波导 |

对照实验：Kelvin/Yanai vs. Rossby/TIW，在匹配扰动强度下比较四个指标。

### 5.4 Module D: 有效拓扑控制参数 Λ（Phase 4）

**简化版本（V1）**：Λ_simple = Δω_eff / (S_bg + |ζ|)

其中 Δω_eff 从 Argo 层化 → 等效深度 → 等效浅水频率间隙估计；S_bg = |∂_y U| 为背景经向剪切（GLORYS12）；|ζ| 为相对涡度。

**完整版本（V2）**：Λ = Δω_eff / (|∂_y U| + |ζ| + α·E_IT + β·E_sub + γ·D)

仅在 V1 验证有效后扩展。避免过拟合。

检验：Λ vs. (B, C, M, L) 的散点图 + 回归，按扰动类型标色。

---

## 6. Figure List（计划 5 主图）

| Figure | 内容 | 回答的问题 |
|---|---|---|
| **Fig.1** | 理论与观测框架图。左：Coriolis 变号 + Berry 曲率（引用 Delplace 2017 可视化语言）；中：SWOT 刈幅覆盖赤道示意；右：真实海洋扰动类型标注 | 为什么做这个研究？ |
| **Fig.2** | SWOT 观测到的赤道波二维结构。Kelvin 波事件的 SSH anomaly 地图 + Hovmöller + 相速度估计 + 经向剖面 vs 理论 Gaussian | SWOT 真的看到了拓扑波吗？(SQ1) |
| **Fig.3** | AI 模式分解验证（OSSE）。合成真值 vs SWOT 采样 vs AI 重建 vs 传统滤波，误差表 | AI 分解可靠吗？ |
| **Fig.4** | 拓扑鲁棒性观测证据。Kelvin 波穿越扰动区前后的 B/C/M/L 对比 + Rossby/TIW 对照 | Kelvin 波真的比非拓扑模式更鲁棒吗？(SQ2) |
| **Fig.5** | 统一机制图。Λ vs 鲁棒性指标散点 + 按扰动类型标色 + 失效阈值标注 | 保护何时失效？(SQ3) |

---

## 7. 工作流（按阶段）

### P0: 数据获取与质量检查（Week 1）
- [ ] 下载 DUACS L4 daily SSH（赤道太平洋, 2023–2025）
- [ ] 下载 SWOT L3 LR SSH（赤道太平洋, 全时段）
- [ ] 下载 ERA5 风应力 τ_x, τ_y（赤道太平洋, 2023–2025）
- [ ] 下载 OSTIA daily SST
- [ ] 下载 TAO/TRITON 数据（检查 2023–2025 可用浮标）
- [ ] 下载 GEBCO 2024 地形
- [ ] 数据质量检查 + `notes/data_inventory.md`

### P1: Hovmöller 与事件识别（Week 2）
- [ ] 构建赤道太平洋 SSH anomaly Hovmöller 图
- [ ] 识别东传 Kelvin 波事件（相速度滤波）
- [ ] ERA5 风应力异常确认 WWB 源
- [ ] 初步事件库（≥3 事件才继续）

### P2: SWOT 2D 结构验证（Week 3）
- [ ] 对已识别事件提取 SWOT KaRIn 轨道数据
- [ ] 经向 SSH 剖面 vs 理论 Gaussian 比较
- [ ] Yanai 波候选搜索（反对称模态）
- [ ] Phase 1 可行性判断报告

### P3: OSSE 与方法开发（Week 5–8, Phase 2）
- [ ] 赤道浅水模型合成波
- [ ] SWOT Simulator 采样 + 噪声
- [ ] AI 模式分解开发与验证
- [ ] 传统方法对比

### P4: 真实事件鲁棒性分析（Week 9–12, Phase 3）
- [ ] 事件库完善（扰动区标注）
- [ ] 四个鲁棒性指标计算
- [ ] Kelvin/Yanai vs Rossby/TIW 对照统计
- [ ] Fig.4 主图生成

### P5: 统一机制与论文（Week 13–16, Phase 4）
- [ ] Argo → 等效深度 → Δω_eff
- [ ] GLORYS → 背景剪切、涡度
- [ ] Λ 参数构建与检验
- [ ] Fig.5 + 论文撰写

---

## 8. 风险与局限

| 风险 | 严重度 | 缓解策略 |
|---|---|---|
| SWOT 21 天重访太稀疏 | 高 | 与 DUACS 融合做事件追踪；SWOT 仅提供 2D 快照 |
| AI 模式分解不可靠 | 高 | OSSE mandatory；传统方法兜底；核心结论不依赖 AI |
| "不需要拓扑也能解释" | 中高 | Λ 参数直接连接谱隙与鲁棒性，经典理论无此预言 |
| Δω_eff 定义不清晰 | 中 | 从 Argo 层化估算等效浅水参数，给出误差带 |
| Kelvin 波事件太少 | 中 | 优先检查 calval 期；扩展到 2023–2025 全时段 |
| 跨学科审稿难度 | 中 | Fig.1 面向物理学+海洋学双方读者设计 |

---

## 9. 复现性约定

- 所有代码在 `analysis/` 目录，Python 脚本，注释说明输入/输出
- 数据下载脚本包含完整参数（时间范围、空间范围、变量）
- 中间结果不入库（.gitignore），仅保留脚本和最终图
- 每个 figure 对应一个独立脚本 `analysis/figXX_*.py`

---

## 10. 待审查的开放问题

请 ClaudeB 在 R01 中重点审查：

1. **SQ 的科学价值判断**："在真实海洋检验拓扑理论"是否足够 novel for NC，还是只是 confirmation study？如何让审稿人认为这不仅仅是"换个数据验证已知理论"？

2. **Λ 参数的物理 well-motivatedness**：分子 Δω_eff 和分母各项的量纲是否一致？Λ 是否只是一个 ad hoc fitting parameter？有没有更严格的理论推导路径？

3. **Phase 1 止损标准**：如果 Hovmöller 能看到 Kelvin 波但 SWOT 经向结构不清晰（信噪比不够），是否仍值得继续？可以只用传统高度计做全部分析吗？

4. **AI 的必要性**：如果传统方法（带通滤波 + EOF）已经能分离波模态，AI 的增量贡献是什么？是否存在"为了用 AI 而用 AI"的风险？

5. **"条件鲁棒性"vs 经典赤道波导理论**：审稿人最可能的攻击——"经典赤道波导理论已经预言 Kelvin 波被赤道束缚、背景流调制其传播，这里拓扑框架的额外解释力在哪？"

---

## 11. 当前状态

- [x] 项目骨架由 dual-ai-paper skill 生成
- [x] DIRECTION.md + refs/notes.md 已就位
- [x] Benchmark card (Delplace 2017) 完成
- [x] Paper direction 确定
- [x] 数据需求清单完成 (literature/data_requirements.md)
- [x] ClaudeA 起 README_research v0.1
- [ ] ClaudeB R01 审查
- [ ] Phase 1 数据下载
- [ ] Phase 1 Hovmöller 图
- [ ] Phase 1 可行性判断
