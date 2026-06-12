# P04: 南极海冰临界点与南大洋能量响应

> 利用 CMEMS SSH、ERA5 风场和海冰数据，结合 CNES-CLS18 MDT，诊断 2016 年南极海冰骤降后的南大洋能量循环响应。

## Status / 状态

| 项 | 内容 |
|---|---|
| 当前阶段 | 🔬 D1 分析完成（待评估方向聚焦） |
| 执行人 | **Tim** |
| 合作人 | **张肚肚** |
| 目标期刊 (T1) | Nature Climate Change |
| 备选期刊 (T2) | Nature Communications |
| 备选期刊 (T3) | JGR-Oceans |
| 启动日期 | 2026-06-08 |
| 提交日期 | 2026-06-12 |

## 研究诚实评估

本项目完成了 D1 阶段的主要分析工作，但存在以下问题：

### 已完成的分析链

```
海冰2016突变 (Pettitt CP=2016, p=0.004)
  ↓ (tau不变, taueff增加源自海冰损失)
τ_eff +16% (CP=2015, p=0.018)
  ↓ (W→EKE Granger p=0.0004)
W (风应力做功) 主导 EKE 增加
  ↓
EKE +10% (post-2016 vs pre-2016)
```

### 存在的问题

1. **要素过多**：从临界点检测到 τ_eff 机制到 Lorenz 能量循环到 Granger 因果，研究链条过长
2. **因果时序倒挂**：EKE 突变点（2013）早于海冰突变点（2016），"海冰→EKE"的因果方向存在疑问
3. **不可逆性不可测**：后 2016 仅 8 年数据，无法区分"临界点"与"多年代际波动"
4. **CK 链路易断裂**：正压转换→EKE 的 Granger 因果不成立（p=0.93）
5. **假设需要重新聚焦**：原设想的 SWOT 观测因数据条件限制未能实施，实际路径为传统高度计+再分析资料

### 数据来源

- CMEMS DUACS L4 SLA（0.125°, 1993-2024）
- ERA5 风场 + 海冰浓度（0.25°, 1940-2024）
- CNES-CLS18 MDT（0.125° 气候态）
- NSIDC 海冰指数（1979-2024）
- CPC AAO / Niño3.4 指数

## 文件结构

```
projects/p04/
├── README.md                 # 本文件
├── COLLABORATION.md          # 合作协议
├── analysis/
│   ├── p04_phase1_regression.py   # Phase 1: EKE 多元回归
│   ├── p04_taueff_spatial.py      # τ_eff 空间分析
│   ├── p04_phase2_mdt.py          # Phase 2: MDT 能量循环
│   ├── p04_tipping_point.py       # 临界点检测
│   ├── p04_final_chain.py         # 证据链闭合分析
│   ├── p04_timeseries.pkl/.csv    # Phase 1 输出
│   ├── p04_energy_cycle.pkl/.csv  # Phase 2 输出
│   ├── p04_mdt_fields.npz         # MDT 梯度场
│   ├── P04-Phase2-Summary-CN.md   # 能量循环总结
│   ├── P04_TippingPoint_Chain_CN.md # 完整证据链报告
│   └── p04_regression_results.txt # 回归结果
├── figures/
│   ├── p04_fig_timeseries.png        # EKE/W 时序
│   ├── p04_fig_regression_coeffs.png # 回归系数
│   ├── p04_fig_taueff_spatial.png    # τ_eff 空间图
│   ├── p04_fig_taueff_timeseries.png # τ_eff 时序
│   ├── p04_fig_energy_timeseries.png # 能量循环时序
│   ├── p04_fig_energy_budget.png     # 能量预算对比
│   ├── p04_fig_tipping_point.png     # 临界点证据
│   ├── p04_fig_multivar_cp.png       # 多变量突变同步
│   ├── p04_fig_phase_space.png       # 相空间轨迹
│   ├── p04_fig_evidence_chain.png    # 证据链合成
│   └── p04_fig_* (共16图)
├── manuscript/                # 手稿（待完善）
├── methodology/               # 方法学资料
└── COLABORATION.md            # 合作说明

## Progress Log / 进度日志

| 日期 | 阶段 | 内容 | 产出 |
|---|---|---|---|
| 2026-06-08 | D0 | AI 辅助选题调研 | 文献调研（15篇）、数据可行性评估、方法框架、D0 调研文档 |

## Key Findings

- Knowledge gap 极强且话题紧迫：海冰临界点的海洋观测证据完全空白
- SWOT 南大洋数据窗口刚开（2023.07），几乎无人发表
- 数据全公开，发表潜力 Nature Climate Change 级
- 核心挑战：SWOT ~2 年记录 vs 气候尺度 → 需巧妙的设计（骤降后状态对比，非追踪骤降过程）

## AI Interaction Log / AI 交互日志

- 2026-06-08: D0 调研 (见 `E:\4.23\obsidian\Spiral upward\RAW\P04-南极海冰临界点-D0调研.md`)

## References / 参考文献

| # | 文献 | DOI | 核验状态 |
|---|---|---|---|
| 1 | Turner et al. (2017) Unprecedented Antarctic sea ice retreat 2016 | 10.1002/2017GL073656 | ⚠️ |
| 2 | Parkinson (2019) 40-y Antarctic sea ice record | 10.1073/pnas.1906556116 | ⚠️ |
| 3 | Meehl et al. (2019) Ocean changes and Antarctic sea ice retreat | 10.1038/s41467-018-07865-9 | ⚠️ |
| 4 | Lenton et al. (2008) Tipping elements in Earth's climate system | 10.1073/pnas.0705414105 | ⚠️ |
| 5 | Purich et al. (2022) Record low Antarctic sea ice 2022 | 10.1029/2022GL100904 | ⚠️ |
| 6 | Fu et al. (2024) SWOT Mission Performance | — | ⚠️ 需核验 |
| 7 | Gille et al. (2025) SWOT Southern Ocean mesoscale | — | ⚠️ 需核验 |
| 8 | Holland et al. (2019) Antarctic sea ice in changing climate | 10.1038/s41558-019-0483-z | ⚠️ |
| 9 | Thompson et al. (2018) Southern Ocean eddy dynamics review | 10.1175/JPO-D-18-0082.1 | ⚠️ |
| 10 | Rintoul et al. (2018) Southern Ocean in coupled climate system | 10.1038/s41561-018-0185-6 | ⚠️ |
