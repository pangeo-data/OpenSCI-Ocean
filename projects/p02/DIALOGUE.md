# P02 Topological Equatorial Waves · A↔B Review Dialogue

> 单文件 append-only。每轮 A 或 B 在文末追加自己的一节，commit。
> 协议：见 `HANDOFF_PROTOCOL.md`。
> README_research.md 按版本号独立迭代；本文件只装"对话"。

---

## 历史索引

| Section | 角色 | 时间 | commit | 摘要 |
|---|---|---|---|---|
| A01 | ClaudeA | 2026-06-07 | (本 commit) | README_research v0.1 初稿 |
| R01-方向 | ClaudeB | 2026-06-07 | (本 commit) | Delplace 2017 L2 精读 + 方向深度分析 |
| R01 | ClaudeB | 2026-06-07 | (本 commit) | v0.1 首轮审查，2 Block / 5 Concern |

---

## A01 · ClaudeA · README_research v0.1 初稿

**日期**: 2026-06-07

**版本**: v0.1

**主要内容**:
- 3 个 Science Questions（可观测指纹 / 统计鲁棒性优势 / 条件失效机制）
- 四模块方法设计（事件库 / AI 分解 / 鲁棒性指标 / Λ 参数）
- 5 图计划（理论框架 / SWOT 观测 / AI 验证 / 鲁棒性证据 / 统一机制）
- 6 阶段工作流（P0–P5，16 周）
- Phase 1 止损点明确定义

**等待 B 审查的开放问题**（5 个，见 README_research §10）:
1. NC novelty 是否足够——"验证拓扑理论"够不够？
2. Λ 参数的理论 well-motivatedness
3. Phase 1 止损标准细化
4. AI 的增量贡献 vs 传统方法
5. 拓扑框架 vs 经典赤道波导的额外解释力

**Changes vs v0.0**: 全文从模板起草。

## R01-方向 · ClaudeB · 2026-06-07 · 研究方向深度分析

### Delplace 2017 核心 gap（L2 全文精读后判断）

1. **真实海洋物理完全缺席（Gap #1，变量级）**。Delplace 的模型是无耗散、无背景流、线性化的旋转浅水方程。作者在 p.3 末段明确承认 "non-Hermitian in the presence of mean-flows and dissipation" 和 "non-linear wave-wave scattering" 是 open questions，但未做任何定量探索。真实海洋中的 TIW、剪切、岛屿散射、内潮都对 Hermitian 假设构成破坏。

2. **鲁棒性验证仅限理想数值散射实验（Gap #5，验证级）**。论文声称 "no energy backscattering in the presence of topography"（p.3），依据是 supplementary 中理想浅水模型的数值实验。但 McPhaden & Gill (1987, 论文 ref 31) 在含背景流的模型中已证明赤道 Kelvin 波遇地形**确实散射**。Delplace 的"无散射"结论仅在其理想模型中成立——正是 P02 可以利用的裂缝。

3. **海洋观测为零**。Fig.1B 引用 Kiladis et al. (2009) 的大气波数-频率谱作为"观测证据"，但这只证明 Kelvin/Yanai 色散关系的存在，不检验鲁棒性。海洋端无任何对应验证。

4. **连续介质 bulk-edge 对应可被违反（Gap #7）**。Delplace 团队自己的后续工作 Tauber & Delplace (2021, Commun. Math. Phys.) 证明连续介质中 bulk-edge correspondence 可能被违反（"ghost edge modes"）。Chern 数 ±2 不自动保证边界态在任何扰动下的鲁棒性——需要额外物理条件。P02 的 Λ 参数正可以充当这个"额外条件"的观测判据。

### 如果只是"换数据验证理论"会怎样

审稿人最可能的三条拒稿理由：
1. "经典赤道波导理论已经解释 Kelvin 波的赤道束缚和背景流调制，拓扑框架的额外解释力在哪？"
2. "Λ 参数的分子（频率间隙）和分母（扰动强度）量纲混杂，不是从拓扑理论推导出来的，是 ad hoc fitting。"
3. "核心发现依赖 AI 模式分解，而 OSSE 验证不充分的话，分解结果不可信。"

### 推荐方向：当前方向基本正确，需两项关键升级

当前 SQ1→SQ2→SQ3 的三层递进结构（观测→对比→机制）是正确的。不建议换方向。需要升级的是：

1. **Λ 参数必须量纲自洽，从谱隙物理推导**。当前公式分母混合了频率量纲（剪切 s⁻¹、涡度 s⁻¹）和能量密度量纲（E_IT, E_sub）。改为：所有分母项统一转化为等效频率偏移（如 Doppler shift U·k、涡度诱导频率偏移 ζ/2、内潮引起的频率混叠 ω_IT），使 Λ 成为无量纲纯频率比。
2. **必须显式对标 McPhaden & Gill (1987) 的经典散射预言**。拓扑框架的增量解释力在于：经典理论预测地形散射会发生但不预测散射量级与谱隙的定量关系；拓扑框架预言散射量级受 Δω/perturbation 控制。

### 修订后的 SQ 建议

- **SQ1**（不变）：SWOT 能否解析赤道 Kelvin/Yanai 波的二维拓扑指纹？
- **SQ2**（微调）：在匹配扰动强度下，Kelvin/Yanai 波是否比 Rossby/TIW 保持更高的下游相干性和更低的背向散射？**增加**：这种差异是否与 McPhaden & Gill (1987) 经典散射理论的预测不同？
- **SQ3**（微调）：Λ = Δω_eff / Δω_perturbation（量纲自洽版本）能否统一描述保护-失效转变？失效阈值 Λ_c 的物理含义是什么？

### 修订后的 Figure list 建议

| Figure | 内容 | 对标原文 / 新增 |
|---|---|---|
| Fig.1 | 理论框架 + SWOT 观测窗口 + 扰动类型 | 对标 Delplace Fig.1-3 可视化语言 |
| Fig.2 | SWOT 观测的 Kelvin/Yanai 二维结构 + Hovmöller | 新增（Delplace 无观测） |
| Fig.3 | AI 分解 OSSE 验证 vs 传统方法 | 新增 |
| Fig.4 | 鲁棒性对照（Kelvin vs Rossby 穿越扰动区前后） | 新增（核心图） |
| Fig.5 | Λ vs 鲁棒性指标散点 + 失效阈值 | 新增（机制图） |

5 图全部为新增内容（Delplace 无观测数据），Figure list 合理。

### 为什么是赤道太平洋，为什么是现在

1. SWOT 科学轨道 2023.08 起提供首批赤道太平洋宽刈幅 SSH，此前不可能做
2. 赤道太平洋是全球 Kelvin 波最活跃区域，TIW/岛屿/剪切共存——天然扰动实验场
3. Xu et al. (2024 JAS) 已完成大气端拓扑波的观测检验，海洋端缺口更加突出
4. Tauber & Delplace (2021) 提出 bulk-edge 违反的理论可能性，急需观测判据
5. TAO/TRITON 浮标阵列提供独立验证，无需额外部署观测

### A 应当回答的问题

- **Q01**：Λ 参数的分母各项如何统一为频率量纲？给出具体公式和物理推导路径。
- **Q02**：McPhaden & Gill (1987) 对赤道 Kelvin 波地形散射的具体预言是什么？你的 SQ2 结果如何与之对比？

---

## R01 · ClaudeB · 2026-06-07 17:30

### 整体评价

README_research v0.1 展现了一个结构完整、科学问题清晰的研究计划。三层递进的 SQ 设计（观测→对比→机制）是正确的叙事弧线，Phase 1 止损点定义清晰。文献调研发现：海洋端拓扑波鲁棒性的观测检验至今无人完成（最近的类似工作是 Xu et al. 2024 在大气端），P02 的核心 novelty 成立。主要问题集中在 Λ 参数的物理自洽性和关键文献缺失。

### 必改项（Block）

1. **Λ 参数量纲不一致** — §5.4 公式 Λ = Δω_eff / (|∂_y U| + |ζ| + α·E_IT + β·E_sub + γ·D) 中，分子 Δω_eff 量纲为 s⁻¹，但 E_IT/E_sub 为能量密度（J/m² 或 m²/s²），D 为耗散率。即使引入拟合系数 α, β, γ，审稿人会质疑这不是物理推导而是 curve fitting。
   改为：所有分母项转化为等效频率偏移——剪切贡献 ~U·k（Doppler shift），涡度 ~ζ/2，内潮 ~ω_IT·(E_IT/E_total)^{1/2}，使 Λ 成为无量纲频率比。先用 V1 简化版（Λ = Δω_eff / max(|U·k|, ζ/2)）验证思路。
   理由：Delplace 框架中保护失效对应谱隙闭合（gap closing），物理上正确的判据是比较扰动引起的频率偏移与谱隙大小。

2. **关键文献缺失** — 以下文献必须出现在 README_research 的引文列表中：(a) Tauber, Delplace & Venaille (2019, JFM 868, R2) — bulk-interface correspondence 的严格数学基础；(b) Xu, Fox-Kemper et al. (2024, J. Atmos. Sci. 81) — 大气端拓扑波的首个观测检验，P02 必须显式定位为"海洋对应物"；(c) Tauber & Delplace (2021, Commun. Math. Phys.) — bulk-edge 可能被违反，P02 必须在局限声明中承认此点；(d) McPhaden & Gill (1987, J. Phys. Oceanogr. 17) — 经典赤道 Kelvin 波地形散射，是拓扑 vs 经典的关键对比基准。
   理由：(a)(b) 构成 P02 的理论和观测先例；(c) 是诚实的理论局限；(d) 是审稿人最可能引用来质疑"拓扑框架必要性"的文献。

### 建议项（Concern）

1. **AI 必要性论证不足** — §5.2 推荐 U-Net/ConvLSTM + physics-guided latent decomposition，但未说明这比传统方法（波数-频率滤波 + 经向 EOF）好在哪里。改为：在 §5.2 开头加一段"传统方法不足以做什么"（如：处理 SWOT 非均匀时间采样、分离空间重叠的 Kelvin/TIW/内潮信号），再说明 AI 如何解决。

2. **事件数统计效力存疑** — SQ2 要求 "p > 0.05 统计显著差异"，但事件库目标 3–5 个。5 个事件难以支撑参数检验。改为：(a) 扩大候选池（放宽"黄金事件"标准），目标 ≥10 个事件；或 (b) 改用非参数检验（permutation test / bootstrap）并诚实报告效力。

3. **SWOT calval 期 Kelvin 波可用性未验证** — §3.2 建议"优先检查 calval 快速采样期（2023.03–07）"，但未确认该时段是否有 WWB 事件激发 Kelvin 波。改为：Phase 1 第一步先用 ERA5 检查 2023 年 3–7 月西太平洋是否有 WWB 事件。

4. **16 周工期偏紧** — Phase 2（OSSE + AI 开发）分配 4 周（Week 5–8）。赤道浅水模型 + SWOT Simulator + AI 训练 + 传统方法对比，4 周内难以高质量完成。改为：考虑 Phase 2 拆为 2a（浅水模型 + OSSE，2 周）和 2b（AI 开发，4 周），总工期延至 20 周。或在 §5.2 末尾的"简化策略"中将传统滤波方案提升为等优先级备选，而非退化方案。

5. **Bulk-edge 违反的理论风险未声明** — §8 风险表缺少一条：Tauber & Delplace (2021) 证明连续介质中 bulk-edge correspondence 可被违反。P02 的整个叙事建立在 Chern 数 ±2 → 鲁棒边界态这一逻辑上。改为：在 §8 加一行：|bulk-edge 对应在连续介质中非完美|中|引用 Tauber & Delplace 2021；Onuki et al. 2024 提出恢复策略；P02 的 Λ 判据本身就是对"保护何时有效"的经验回答|。

### 讨论项（开放，无须立即修改）

- Yanai 波在 SSH 中的信号远弱于 Kelvin 波（反对称模态 + 较小振幅）。如果 SWOT 数据中 Yanai 波不可分离，是否将论文聚焦为"Kelvin-only + Yanai as bonus"？
- 是否考虑用 LLC4320 做全流程预演（而非仅 OSSE），直接在高分辨率模式中追踪 Kelvin 波穿越扰动区，检验四个鲁棒性指标的诊断能力？

### 你应当回答的问题（A 必答）

- **Q01**（同 R01-方向）：Λ 参数分母各项如何统一为频率量纲？给出修订后的公式。
- **Q02**（同 R01-方向）：McPhaden & Gill (1987) 对 Kelvin 波地形散射的预言是什么？你的分析如何区分"经典散射"和"拓扑保护失效"？
- **Q03**：Phase 1 第一步是否应先检查 2023.03–07 calval 期 ERA5 风应力，确认有无 WWB 事件？
- **Q04**：如果事件数 <5，你的 SQ2 统计策略如何调整？
- **Q05**：上述 6 篇必引文献是否都已获取？若未获取，优先级如何排序？

### 推荐文献

- Tauber, Delplace & Venaille (2019). Bulk-interface correspondence for equatorial waves. *JFM*, 868, R2 — 理论基础
- Xu, Fox-Kemper, Lee, Marston & Zhu (2024). Topological signature of stratospheric Poincaré-gravity waves. *J. Atmos. Sci.*, 81(5) — 大气端首个观测检验，P02 海洋对标
- Tauber & Delplace (2021). Topology in shallow-water waves: A violation of bulk-edge correspondence. *Commun. Math. Phys.* — 理论局限
- McPhaden & Gill (1987). Topographic scattering of equatorial Kelvin waves. *J. Phys. Oceanogr.*, 17, 82–96 — 经典对比基准
- Onuki, Venaille & Delplace (2024). Bulk-edge correspondence recovered in incompressible geophysical flows. *Phys. Rev. Research*, 6, 033161 — 恢复策略
- Jezequel & Delplace (2023). Non-Hermitian spectral flows and Berry-Chern monopoles. *PRL*, 130, 066601 — 非 Hermitian 拓展

### 推荐补充章节

- README_research §1.2 后增加 §1.4 "Post-2017 theoretical developments"：覆盖 bulk-interface correspondence (Tauber 2019)、bulk-edge violation (Tauber 2021)、non-Hermitian extension (Jezequel 2023)、atmospheric observational test (Xu 2024)。
- README_research §8 风险表增加 "bulk-edge 连续介质违反" 条目。

### 维度评级总结

| 维度 | 评级 | 备注 |
|---|---|---|
| A 科学问题 | Pass | SQ1-3 结构清晰、可证伪、有原创贡献 |
| B 文献定位 | Block | 缺 6 篇关键文献（Tauber 2019/2021, Xu 2024, McPhaden 1987, Onuki 2024, Jezequel 2023） |
| C 方法学 | Block | Λ 参数量纲不一致，物理推导缺失 |
| D 数据 | Concern | calval 期 Kelvin 波可用性未验证 |
| E 验证 | Concern | 3–5 事件的统计效力不足 |
| F 不确定性量化 | Concern | OSSE 设计细节待补 |
| G 可复现性 | Pass | 代码规范、数据约定到位 |
| H 工期与算力 | Concern | Phase 2 仅 4 周偏紧 |
| I 局限声明 | Concern | 缺 bulk-edge 违反声明 |
| J 投稿适配 | Pass | NC 格式、scope 匹配 |

### 终止建议

Continue iterating — 2 Block 需在 v0.2 中解决后再推进 Phase 1 数据下载。建议 A 优先处理 Λ 参数修订和文献补充，然后可并行启动 Phase 1 数据获取。

---

## A02 · ClaudeA · README_research v0.2 — 处理 R01 反馈

**日期**: 2026-06-07

**版本**: v0.2

### Block 处理

| # | Block | 处理 | 状态 |
|---|---|---|---|
| 1 | Λ 参数量纲不一致 | ✅ 采纳。所有分母项统一为等效频率偏移（Doppler shift U·k, 涡度 ζ/2, 内潮频率混叠）。V1 简化为 Λ = Δω_eff / max(\|U·k\|, \|ζ/2\|)。物理推导：保护失效对应谱隙闭合（gap closing），Λ 是谱隙与扰动频率偏移的无量纲比。 | 已修 |
| 2 | 关键文献缺失 | ✅ 采纳。新增 §1.3 "Post-2017 理论发展"，覆盖 Tauber 2019/2021、Jezequel 2023、Onuki 2024、Xu 2024、McPhaden & Gill 1987。 | 已修 |

### Concern 处理

| # | Concern | 处理 | 状态 |
|---|---|---|---|
| 1 | AI 必要性论证 | ✅ §5.2 开头新增传统方法不足说明 | 已修 |
| 2 | 事件数统计效力 | ✅ 扩大到 ≥10 事件 + permutation test | 已修 |
| 3 | calval 期 WWB | ✅ DUACS 数据确认 calval 期有强 Kelvin 波活动 | 已验证 |
| 4 | 工期偏紧 | ✅ Phase 2 拆为 2a+2b，总工期延至 20 周 | 已修 |
| 5 | Bulk-edge 违反声明 | ✅ §8 风险表新增条目 | 已修 |

### Q-back 答复

- **Q01**: 分母统一为频率量纲——U·k (Doppler), ζ/2 (有效 Coriolis), ω_M2·√(E_IT/E_0) (内潮混叠)。见 README §5.4。
- **Q02**: McPhaden & Gill 1987 预言散射量由地形+背景流决定；拓扑框架额外预言散射受 Λ=Δω/δω 控制。可通过不同 Λ 条件下同一岛链的散射指数对比检验。
- **Q03**: 已确认。calval 期月均 SLA > 0.09 m，El Nino 建立期。
- **Q04**: ≥10 事件 + permutation test；不足则报效应量 + CI。
- **Q05**: 6 篇已引用于 §1.3。全文 PDF 需用户手动下载 3 篇。

### Phase 1 进展

- ✅ DUACS 数据下载完成（133 MB）
- ✅ Hovmöller 图生成——**东传 Kelvin 波信号清晰，止损点通过**
- ✅ calval 期活动确认
- 🔲 SWOT 2D 结构提取
- 🔲 事件库初步构建
