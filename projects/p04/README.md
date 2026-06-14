# P04: Antarctic Sea Ice Retreated Into Pre-existing Waves

> **项目状态：✅ D1 Complete — 论文投稿就绪**
>
> v1（冰→EKE因果链）失败后方向重建为 v2（海洋波浪→冰），发现涌浪衰减而非 fetch 是波浪-海冰耦合的主导机制。

---

## Status / 状态

| 项 | 内容 |
|---|---|
| 当前阶段 | ✅ D1 Complete — 论文投稿就绪 |
| 执行人 | **Tim** |
| 合作人 | **张肚肚** |
| 目标期刊 | Nature Communications |
| 启动日期 | 2026-06-08（v1）/ 2026-06-14（v2 重建） |
| 论文完成 | 2026-06-14 |
| ClaudeB 终审 | R16: Approve (0 Block) |
| Nature 模拟审稿 | 3 轮，3 位审稿人均 supportive |

---

## v2 核心发现

**标题**: *Antarctic sea ice retreated into pre-existing waves: swell attenuation, not fetch, controls wave exposure at the ice edge*

1. **Fetch 假设失败**（Granger p=0.74）：更多开阔水面不产生更大波浪
2. **涌浪衰减假设成立**（冬季偏 Granger p=0.040）：海冰退缩减少了对远程涌浪的衰减
3. **冰缘处波浪能量几乎不变**（+2.4%年均，+0.1%冬季）：冰退缩进入了已有波场
4. **MWP = 9.0 s** 确认涌浪主导；SIC-MWP 正相关（r=0.24）支持低通滤波机制
5. **ERA5 掩膜伪影被排除**：ice-free 格点趋势更强

## v2 论文统计

| 项 | 数值 |
|---|---|
| 正文 | 3981 词 / 15 页 |
| 图表 | 6 图 + 1 表 |
| 参考文献 | 25 篇 |
| SI | 2 页 / 4 节 |
| 分析脚本 | 8 个 Python 文件 |
| ERA5 数据 | SWH + Wind + SIC (1979-2024) |
| A/B 迭代 | 19 轮 ClaudeA + 16 轮 ClaudeB |

## 投稿前待办

- [ ] 填写作者信息和单位
- [ ] 填写推荐审稿人
- [ ] SeaVision 实测数据 SI 图（PANGAEA 维护恢复后）

---

## v1 负结果存档

> v1（2026-06-08 至 06-12）尝试 "海冰→τ_eff→EKE" 因果链，因 EKE 突变（2013）早于 SIC 突变（2016）而终止。
> 详见 v1 相关文件（analysis/p04_*.py, figures/p04_fig_*.png）。

---

## 原始假设

**H0（未验证）**：2016年南极海冰骤降后，海冰屏蔽效应减弱（τ_eff上升）→ 风能输入增加（W↑）→ 涡动能增加（EKE↑）。

## 验证结果

| 检验 | 结果 | 支持假设？ |
|------|------|-----------|
| τ_eff 是否增加 | ✅ 冰区τ_eff +16%（放大因子2.3×） | 是 |
| τ（风应力）是否不变 | ✅ τ CP不显著（p=0.065） | 是——τ_eff增加由海冰驱动 |
| W 是否预测 EKE | ✅ Granger p=0.0004*** | 是——风能做功传递到EKE |
| τ_eff 是否预测 EKE | ❌ Granger p=0.064（不显著） | **否** |
| SIC 突变在 EKE 突变之前 | ❌ **EKE的CP在2013，SIC的CP在2016** | **否——因果倒挂** |
| 回归中τ_eff系数为正 | ❌ **τ_eff系数为负（β=-0.18, p=0.002）** | **否——与假设相反** |
| 能量循环（CK→EKE） | ❌ Granger p=0.93 | **否** |
| 不可逆性可验证 | ❌ 仅8年后数据 | 不可能 |

### 核心矛盾

> **EKE的突变发生在2013年，比SIC的突变（2016年）早3年。** 因果方向不成立。

这排除了"海冰损失→EKE增加"的因果链。W（风应力做功）确实是EKE的最强预测因子，但W的变化并非由海冰损失驱动，而是大尺度大气环流变化的结果。

---

## 终止原因总结

| 原因 | 说明 |
|------|------|
| **数据时间不够** | 后2016仅8年，无法验证"临界点"或"不可逆转换" |
| **因果时序倒挂** | EKE的突变（2013）早于SIC的突变（2016） |
| **τ_eff系数为负** | 回归中τ_eff对EKE的独立贡献为负，与假设相反 |
| **能量路径断裂** | CK→EKE的Granger因果不成立（p=0.93） |
| **解释度低** | 回归R²=0.13，87%的EKE方差无法解释 |

---

## 仍然成立的事实（负结果的组成部分）

1. **τ_eff 机制具有物理合理性**：海冰区τ_eff +16%，τ仅+7%，放大因子2.3×——海冰确实修饰了风应力输入
2. **W（风应力做功）是EKE的最强预测因子**（Granger p=0.0004, 回归β=0.40）——能量确实进入了海洋
3. **SIC在2016年发生显著状态转变**——这是观测事实，但后续影响尚不明确
4. **AAO/Niño3.4不相关**——排除大气环流模态混淆的替代解释

这些事实本身有价值，但不足以支持"海冰损失驱动EKE增加"的因果叙事。

---

## 文件清单

```
projects/p04/
├── DIRECTION.md                          # 研究方向和终止说明
├── README.md                             # 本文件
├── COLLABORATION.md                      # 合作协议
├── analysis/
│   ├── p04_phase1_regression.py          # Phase 1: EKE多元回归
│   ├── p04_taueff_spatial.py             # τ_eff空间分析
│   ├── p04_phase2_mdt.py                 # Phase 2: MDT能量循环（不成功）
│   ├── p04_tipping_point.py              # 临界点检测（发现CP倒挂）
│   ├── p04_final_chain.py                # 证据链闭合（最终检验）
│   ├── p04_timeseries.pkl/.csv           # Phase 1输出
│   ├── p04_energy_cycle.pkl/.csv         # Phase 2输出
│   ├── p04_mdt_fields.npz                # MDT梯度场（未提交，由 p04_phase2_mdt.py 生成）
│   ├── p04_regression_results.txt        # 回归结果
│   ├── P04-Phase2-Summary-CN.md          # 能量循环总结
│   └── P04_TippingPoint_Chain_CN.md      # 证据链报告
├── figures/                              # 16张分析图
│   ├── p04_fig_timeseries.png            # EKE/W时序
│   ├── p04_fig_regression_coeffs.png     # 回归系数
│   ├── p04_fig_taueff_spatial.png        # τ_eff空间
│   ├── p04_fig_taueff_timeseries.png     # τ_eff时序
│   ├── p04_fig_energy_timeseries.png     # 能量循环
│   ├── p04_fig_energy_budget.png         # 能量预算
│   ├── p04_fig_tipping_point.png         # 临界点证据
│   ├── p04_fig_multivar_cp.png           # 多变量突变同步
│   ├── p04_fig_phase_space.png           # 相空间轨迹
│   ├── p04_fig_evidence_chain.png        # 证据链合成
│   └── ...（共16图）
├── manuscript/                           # 手稿（未完成，存档）
└── methodology/                          # 方法学资料
```

---

## 对后续研究的建议

1. **至少15-20年后数据**才能验证SIC的2016年下降是否为不可逆临界点
2. **先验方向假设**：τ_eff和EKE的因果关系需要动力学机制（如涡分辨率模型）的独立验证，仅靠统计归因不够
3. **更高时间分辨率数据**（日或周尺度）才能解析能量从风到涡流的传递过程，月分辨率太粗
4. **负结果也值得发表**——"海冰损失和EKE增加同时发生但无因果关系"是有价值的科学发现

---

## 免责声明

本研究结论仅基于 CMEMS SSH、ERA5、NSIDC 和 CPC 公开数据（1993-2024年）。分析方法和代码均公开。研究终止是因为数据时间跨度的根本性限制，**不构成对"南极海冰是否越过临界点"这一科学问题的最终判定**。

---

*存档于 2026-06-12。项目已终止，代码和图表保留作为负结果参考。*
