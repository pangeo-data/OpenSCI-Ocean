# P02 最新研究结果审查：新解释机制、NC 水平判断与修改建议

## 结论先说

**新的解释机制有潜力，但目前还不能说“结果已经成立”，也还没有达到 Nature Communications 的证据强度。**

你这版比上一版进步非常明显：事件去重、WWB 验证、频谱符号修正、真实 GLORYS 计算、V1 机制被数据否定、再转向 V2 共振窗口机制，这些都是正确方向。尤其是你从“扰动幅度导致拓扑保护失效”转向：

> **不是扰动强度本身，而是扰动是否占据能够把 Kelvin 模态耦合到西传模态的 \((k,\omega)\) 共振窗口。**

这个机制比原来的 \(\Lambda=\Delta\omega/\delta\omega\) 更有科学价值，也更有 NC 潜力。

但目前它仍然是**强假说 + 初步支持**，不是已经被观测严格证明。原因主要有四个：

1. 核心相关性只有 \(n=7\)，TIW 区 \(r=0.69, p=0.086\)，还未达到常规显著性。
2. 所有 \(\Lambda_2\) 事件窗口都存在频率分辨率 caveat，而文稿里说只影响 KE05，这与数据不一致。
3. 鲁棒性指标仍然基于 `original` SSH 场，而不是 Kelvin-filtered/complex-amplitude Kelvin 模态，机制验证的因变量还不够干净。
4. 图件生成脚本与已提交图片/正文描述存在明显不一致，尤其 Fig.6 和 Fig.5 的可复现性需要立即修复。

所以我建议判断为：

> **方向正确，机制新颖，具备冲 NC 的潜力；但当前版本更像“机制发现版/预注册检验前夜”，还不适合直接作为 NC 投稿终稿。**

---

# 1. 这版最大的进步是什么？

你这次修订确实解决了上一轮很多关键问题。`PROGRESS_SUMMARY.md` 里记录了从 11 个候选 Kelvin ray 去重到 7 个独立事件、修正 \(\Delta\omega_\mathrm{eff}\)、加入 GLORYS 真实 \(\Lambda\)、加入 WWB 验证、修复 FFT 符号等步骤；特别是 FFT 符号修正后，Kelvin 成分从原先错误的 2.3% 变成 41.6%，这是一个实质性修复。

事件库也比之前合理。`kelvin_event_catalog_deduped.json` 中现在保留 7 个 KE01–KE07 事件，并记录了原始重复 ID、传播时间、经度范围、SLA 强度、phase speed、wind flag 和 WWB note；其中 5 个事件被标为 confirmed WWB，2 个为 marginal。 这比上一版“11 个事件”中明显重复的情况强很多。

WWB 部分也有重要改进。`p1_06b_wwb_localized.py` 明确指出原先整盒平均会稀释局地 WWB，因此改成 \(2^\circ S–2^\circ N\) 纬向平均、5° 经向滑动、每日最大西风的局地检测方法。 结果文件显示 KE03–KE07 为 confirmed，KE01–KE02 为 marginal，这与事件目录中的 wind flag 一致。

最重要的是你现在没有死守原始 \(\Lambda\) 机制。真实 GLORYS 计算显示 zone-mean \(\Lambda\) 全部在约 4.84–8.25 之间，且 dominant perturbation 都是 vorticity，并没有出现预期的 \(\Lambda\sim1\) 失效阈值。 这说明你没有强行把旧故事套在数据上，而是让数据逼出新机制。这一点是非常好的科学直觉。

---

# 2. 新机制是否成立？

## 2.1 V1 机制“不成立”这一点基本成立

原始机制是：

\[
\Lambda = \frac{\Delta \omega_\mathrm{eff}}{\delta\omega_\mathrm{pert}}
\]

其中 \(\delta\omega_\mathrm{pert}\) 用 \(|\zeta|/2\) 或 \(U k_x\) 表征。这个机制希望解释：

\[
\Lambda \gg 1 \Rightarrow \text{保护有效}
\]

\[
\Lambda \sim 1 \Rightarrow \text{保护失效}
\]

但你提交的数据清楚显示，zone-mean \(\Lambda\) 全部远大于 1，且 TIW 区并没有比 island zones 更接近 1。 论文正文也已经写出：zone-averaged \(\Lambda\) 在 Gilbert、Line、TIW 三个区分别约为 \(6.2\pm0.8\)、\(5.8\pm0.6\)、\(6.5\pm1.0\)，没有区分力；沿 ray 的局地 \(\Lambda_\mathrm{min}\) 也让三个区都塌缩到 \(\sim1\)，但仍不能解释为什么 Line Islands 保持而 TIW 损失。

所以这个结论可以写得很强：

> **A perturbation-amplitude criterion fails in the real ocean.**

这是目前最稳的结果之一。它是一个扎实的负结果，而且负结果本身有价值。

---

## 2.2 V2 共振窗口机制“有支持”，但还没有严格成立

你现在提出的 V2 是：

\[
\Lambda_2 = \frac{\Delta \omega_\mathrm{eff}}{\delta\omega_\mathrm{res}}
\]

其中 \(\delta\omega_\mathrm{res}\) 来自 vorticity power 在特定 \((k,\omega)\) 共振窗口内的 rms。`p4_03_lambda_v2_resonance.py` 的物理逻辑写得清楚：静态 island wake 主要是高 \(k\)、近零频率扰动，难以提供 Kelvin 模态到西传模态所需的 \((\Delta k,\Delta \omega)\)；而 TIW 的波长约 700–2500 km、周期 15–50 天、西传，正好落入可耦合 Kelvin 到 westward modes 的窗口。

这个机制在物理上是合理的，而且比 V1 更有解释力。数据上也有初步支持：`lambda_v2_correlations.json` 显示全部 event-zone pairs 的 Spearman \(\rho=0.42, p=0.135\)，TIW zone 内 Pearson \(r=0.69, p=0.086\)，Spearman \(\rho=0.643, p=0.119\)。 论文正文也诚实写了这些相关性 “suggestive but not significant”，这比前一版强行宣称显著好很多。

但是，目前不能写成：

> Resonant coupling, not perturbation strength, sets where oceanic topological protection fails.

这句话在摘要里太强了。摘要目前说 “The breakdown instead proceeds by resonant triad scattering” 和 “Resonant coupling, not perturbation strength, sets where oceanic topological protection fails.” 以 \(n=7, p=0.086\) 的证据强度，这更应该改成：

> The results suggest that breakdown is better organized by a resonance-window metric than by perturbation amplitude alone.

或者：

> These preliminary results identify resonant triad scattering as a plausible breakdown pathway.

---

# 3. 目前最严重的问题

## 3.1 \(\Lambda_2\) 的时间窗 caveat 被低估了

这是目前最关键的科学问题。

论文和 SI 里说，短于 \(2\times50\) 天的窗口会影响最长共振周期解析，并称这主要影响 KE05。 但 `lambda_v2_resonance.json` 中每一个 event-zone pair 的 `window_caveat` 都是 `true`，因为所有 \(n_\mathrm{days}\) 都只有 50–65 天，全部短于 \(2\times50\) 天。

这意味着：

> 不是 KE05 一个事件存在频率分辨率问题，而是整个 \(\Lambda_2\) 数据集都存在长周期端解析不足问题。

这会直接影响 NC 审稿人对 Fig.5/Fig.6 的信任。你现在的 resonant window 是 15–50 天，但每个事件窗只有 50–65 天。用 50–65 天窗口去估计 40–50 天周期能量，频率 bin 非常粗，统计方差会很大。这个问题不能只放在 SI 里轻描淡写。

建议立即做三组敏感性测试：

\[
W_1: 15{-}50\ \mathrm{days}
\]

\[
W_2: 15{-}40\ \mathrm{days}
\]

\[
W_3: 15{-}30\ \mathrm{days}
\]

同时把时间窗口扩为 event crossing 前后，例如 \(\pm90\) 天或 \(\pm120\) 天，然后比较 \(\Lambda_2\) 排序是否稳定。如果只有 15–50 天窗口给出 \(r=0.69\)，而 15–30 天或长窗口下相关性消失，那么 V2 机制会被认为是窗口选择敏感。

---

## 3.2 鲁棒性因变量还不够干净

`p3_03_robustness_v2.py` 虽然加载了 `kelvin_field` 和 `rossby_field`，但实际计算 Kelvin、Rossby、stationary、time-shifted metrics 时用的是 `original`，不是 filtered Kelvin mode。 也就是说，现在的 amplitude ratio 本质上是沿 Kelvin ray 的原始高通 SSH rms，而不是 Kelvin 模态振幅。

这会导致一个大问题：

> 你用 \(\Lambda_2\) 解释的是“原始 SSH 沿 ray 的下游/上游 rms 变化”，而不是“Kelvin 模态能量损失”。

这两者差别很大。TIW 区的 rms 下降可能来自背景 ENSO 高通异常、局地风强迫、低频场、滤波残差、DUACS 平滑、或路径选择，而不一定是 Kelvin \(\rightarrow\) westward modes 的共振散射。

你需要至少给出三类因变量：

\[
R_K = \frac{\mathrm{rms}(\eta_K^\mathrm{down})}{\mathrm{rms}(\eta_K^\mathrm{up})}
\]

\[
M_{K\rightarrow W} =
\frac{E_\mathrm{westward}^{down} - E_\mathrm{westward}^{up}}
{E_K^{up}}
\]

\[
L =
\frac{E(|y|>y_c)}{E(|y|<y_c)+E(|y|>y_c)}
\]

当前只有 \(R\)，而且 \(R\) 不是严格 Kelvin-filtered。这是机制证明的主要短板。

---

## 3.3 stationary control 仍然不合格

`robustness_metrics_v2.json` 里 stationary control 对同一个事件在 Gilbert、Line、TIW 三个区的数值完全重复。例如 KE01 stationary 在三个 zone 下都是 amp_ratio 3.5856、coherence 0.3284；KE02 也在三个 zone 完全重复。 这是由代码中 stationary speed 为 0 时固定 `dt_to_zone = 20` 造成的。

这说明 stationary control 不是一个真正的“穿越不同扰动区”的对照。它只能说明背景场在固定时间窗里的 rms 变化，不能检验 perturbation-zone dependence。建议删除 stationary control，或改成：

1. **randomized ray control**：随机选相同月份、相同纬带、相同路径长度的 eastward rays；
2. **phase-randomized control**：保留频谱、随机相位；
3. **time-shift ensemble**：不是固定 +60 天，而是 \(\pm 30\) 到 \(\pm 180\) 天的多个 shift；
4. **off-equatorial control**：同样 ray 速度，但纬度移到 \(5^\circ N/S\)。

现在的 stationary control 不应该在正文中作为 “three independent controls” 之一。

---

## 3.4 bootstrap p 值仍然不是真正的假设检验 p 值

`p3_03_robustness_v2.py` 的 block bootstrap 计算了 bootstrap 分布，然后用：

\[
p = \Pr(|d_\mathrm{boot}| \ge |d_\mathrm{obs}|)
\]

但这个 bootstrap 分布是围绕 observed difference 生成的，不是零假设分布。因此这个 \(p\) 不应当被解释为两组均值差异的显著性 p 值。

你可以继续报告 bootstrap CI，但如果要报告 p 值，建议用 event-level paired sign-flip / permutation：

\[
d_i = R_{K,i} - R_{control,i}
\]

在零假设下随机翻转 \(d_i\) 的符号，构造 null distribution。或者用 mixed-effects model：

\[
\log R_{i,z} = \alpha + \beta_1 \mathrm{mode}_i + \beta_2 \mathrm{zone}_z + \beta_3 \Lambda_{2,i,z} + u_i + \epsilon_{i,z}
\]

其中 \(u_i\) 是 event random effect。

---

## 3.5 质量过滤后的 n 与正文不一致

Fig.2 脚本里对 amplitude ratio 使用了 `rms_up > 0.01` 的质量过滤。 但 `robustness_metrics_v2.json` 中 KE01 Line Islands 的 `rms_up=0.00933`，按这个标准应被排除；KE01 Gilbert 的 `rms_up=0.0016` 更应排除。

正文写 Line Islands \(n=7\)，但严格按 `rms_up > 0.01`，Line Islands 应该是 \(n=6\)，TIW 是 \(n=7\)，Gilbert 是 \(n=1\)。 这个细节必须修正。NC 审稿人非常容易抓这种 n 不一致问题。

---

# 4. SWOT 部分仍然不能支撑强结论

论文现在标题已经降调为 “multi-mission altimetry and SWOT snapshots”，这是对的。 但是正文小标题仍写：

> SWOT reveals two-dimensional equatorial wave structure

而图中 SWOT 剖面的峰值在 \(5^\circ\)–\(7^\circ N\)，不是赤道中心。正文也承认这更可能是 Kelvin + TIW/Rossby 多模态叠加。

更严重的是，`p1_07_swot_event_matching.py` 的匹配逻辑目前还没有真正使用 SWOT pass 的观测时间来和预测波峰时间比较。脚本文档说要筛选 \(|x_\mathrm{SWOT}-x(t)|<5^\circ\) 且 \(|t_\mathrm{SWOT}-t|<1.5\) 天，但代码实际根据 pass 的 equator-crossing longitude 反推一个 `t_predicted`，却没有用 pass 的真实 `time` 计算 `time_gap_days`。这样 `lon_gap` 本质上被构造成接近 0，coverage_score 主要变成 valid_pct。

这意味着目前不能写：

> SWOT passes coincident with identified Kelvin wave events.

更稳妥的写法是：

> SWOT snapshots provide high-resolution meridional SSH structure within the equatorial waveguide, but event-phase matching remains preliminary.

如果要让 SWOT 成为 NC 亮点，必须修复匹配：

\[
t_\mathrm{peak}(x_\mathrm{pass}) = t_0 + \frac{x_\mathrm{pass}-x_0}{c}
\]

\[
\Delta t = t_\mathrm{pass} - t_\mathrm{peak}(x_\mathrm{pass})
\]

只保留 \(|\Delta t|<1.5\) 或 3 天的 pass，并输出 `time_gap_days`。否则 SWOT 只能是 illustrative snapshot，不是 event-matched evidence。

---

# 5. 图件和脚本可复现性存在硬伤

这是投稿前必须清理的部分。

## 5.1 Fig.6 脚本仍是 synthetic schematic

`make_fig6_lambda.py` 里明确写着：

> CONCEPTUAL SCHEMATIC — all data points are synthetic random numbers.

并且脚本仍在生成 synthetic \(\Lambda\) 点。 但 GitHub 上的 `fig6_lambda.png` 显示的是 “Real GLORYS-derived Λ vs robustness” 的两面板图。 同时论文正文的 Fig.6 caption 又描述了三面板：zone-mean \(\Lambda\)、along-ray \(\Lambda_\mathrm{min}\)、\(\Lambda_2\) vs amplitude ratio。

也就是说，目前至少有三套 Fig.6 版本互相不一致：

1. 脚本：synthetic schematic；
2. committed PNG：real V1 two-panel；
3. paper caption：V1 + local + V2 three-panel。

这是 NC 投稿前的 block 级问题。必须做到：

```text
make_fig6_lambda.py
→ 读取 lambda_event_zone.json
→ 读取 lambda_along_ray.json
→ 读取 lambda_v2_resonance.json
→ 读取 robustness_metrics_v2.json
→ 生成与 paper caption 完全一致的 final Fig.6
```

并删除 synthetic 旧脚本或重命名为 `make_fig6_schematic_old.py`，不能留在投稿仓库里。

---

## 5.2 Fig.5 脚本也不像是当前图的生成脚本

`make_fig5_spectral.py` 读取的是 `spectral_decomposition.npz`，而不是 `spectral_decomposition_v2.npz`。 但当前 GitHub 上的 `fig5_spectral.png` 是一个 v2 六面板图，标题写着 “P02 Spectral Decomposition v2”，包括 original、Kelvin、Rossby、TIW、Residual 和 log10 k-ω power。

这说明当前图件可能是由另一个未提交脚本生成的，或者脚本没有更新。投稿前必须保证所有主图由提交的脚本一键生成。

---

## 5.3 Fig.1 仍残留旧机制

`fig1_framework.png` 的 TIW 区仍标着 \(\Lambda\sim1\)，island 区标着 \(\Lambda\gg1\)。 但现在 V1 \(\Lambda\sim1\) 失效机制已经被你自己否定，论文正文也说初始 \(\Lambda\sim1\) 假设被修正为 \(\Lambda_2\) 共振窗口准则。

Fig.1 应该改成：

```text
Island wakes: amplitude can be large, but spectrally mismatched
TIW: resonant (k,ω) channel active
```

不要再画 \(\Lambda\sim1\) 作为 TIW 失效机制。

---

# 6. 新机制的科学故事该怎么改得更强？

目前最好的故事不是：

> TIW 区扰动强，所以保护失效。

也不是：

> \(\Lambda\sim1\) 导致 gap closure。

而是：

> **真实海洋中，拓扑型鲁棒性不是由扰动幅度控制，而是由扰动是否打开 Kelvin 与西传模态之间的 resonant scattering channel 控制。静态或准静态 island wakes 即使涡度很强，也主要在高波数/近零频率上，不容易满足 \((\Delta k,\Delta\omega)\) 匹配；TIW 则天然处在 700–2500 km、15–50 天、西传的窗口内，能提供 Kelvin \(\rightarrow\) westward modes 的三波/Bragg 型耦合通道。**

这个故事有 NC 潜力，因为它不仅是“看到了 Kelvin 波”，而是提出了一个可证伪的新判据：

\[
S_\mathrm{res} =
\int_{W_\mathrm{res}} |\hat{\zeta}(k,\omega)|^2\,dk\,d\omega
\]

\[
\Lambda_2 =
\frac{\Delta\omega_\mathrm{eff}}
{\frac{1}{2}\sqrt{S_\mathrm{res}}}
\]

预测：

\[
S_\mathrm{res} \uparrow
\Rightarrow
R_K \downarrow,\quad M_{K\rightarrow W}\uparrow,\quad B\uparrow
\]

这里不要只看 amplitude ratio。一定要把 \(M_{K\rightarrow W}\) 或 westward energy increase 做出来。否则“共振散射”只是对 Kelvin amplitude loss 的解释，而不是直接观测到的 mode conversion。

---

# 7. 是否达到 NC 水平？

## 当前版本：还没有

以现在的结果，NC 的风险很高。主要原因是：论文自己的 limitations 已经承认 robustness comparisons 都不显著，\(\Lambda_2\) 也只是 TIW 区 \(r=0.69, p=0.09, n=7\)。 这种证据强度更像：

- **GRL / JGR Oceans / JPO 的 strong preliminary mechanism paper**；
- 或者 **EarthArXiv/preprint + 预注册扩展检验**；
- 但直接投 NC 可能被认为“机制有趣但样本不足、统计不显著、SWOT 证据弱”。

## 如果扩展验证成功：有 NC 潜力

如果你正在跑的 1993–2025 历史 DUACS 扩展能做到以下几点，就可以重新冲 NC：

1. 独立 Kelvin 事件数 \(\geq20\)，最好 \(\geq40\)；
2. TIW zone 内 \(\Lambda_2\) 或 \(S_\mathrm{res}\) 与 \(R_K\) 的相关性保持，且 \(p<0.01\)；
3. Line/Gilbert negative controls 仍然不相关；
4. 换窗口 15–30、15–40、15–50 天后结论稳；
5. 换 DUACS/CMEMS/SST TIW index/GLORYS 版本后结论稳；
6. 能展示 Kelvin energy loss 对应 westward/Rossby/TIW 能量增长，而不是单纯 SSH rms 变小；
7. SWOT 作为 event-matched case snapshots 支持“真实二维波导复杂性”，但不承担主证据。

如果这些成立，文章可以升格为：

> **A resonance-window criterion for the breakdown of topological equatorial wave protection in the real ocean**

这就有 NC 水平。

---

# 8. 投稿前必须修改的清单

## P0：不改不能投

1. **修复 Fig.6 可复现性。** 当前 `make_fig6_lambda.py` 仍是 synthetic，但正文和 committed figure 都不是这个版本。
2. **修复 Fig.5 脚本与图件不一致。** 当前脚本不明显对应 v2 六面板图。
3. **修正 \(\Lambda_2\) 时间窗 caveat。** 不是 KE05 一个事件，而是所有 event-zone pairs 都 `window_caveat=true`。
4. **修复 SWOT event matching。** 必须使用 pass 的真实时间计算 `time_gap_days`。
5. **把 amplitude ratio 重新算在 Kelvin-filtered 或 complex-amplitude Kelvin mode 上。** 现在 p3 脚本实际用的是 `original`。
6. **删除或替换 stationary control。** 当前 stationary values 对同一事件跨 zone 完全重复，不适合作为 perturbation control。
7. **修正正文 n。** Line Islands 质量过滤后应是 \(n=6\)，不是 \(n=7\)。
8. **删掉“gap closes”旧语言。** 正文仍有“TIW perturbation amplitudes approach the frequency gap scale / gap closes”的表述，但 V1 已证明这个解释失败。

## P1：决定能不能冲 NC

1. 用 1993–2025 历史 DUACS 扩展到 \(\geq20\) 个独立事件。
2. 对 \(\Lambda_2\) 做窗口敏感性：15–30、15–40、15–50 天。
3. 做 synthetic OSSE：构造 Kelvin + static wake、Kelvin + TIW resonant perturbation，验证 \(\Lambda_2\) 能恢复已知 mode conversion。
4. 加入 \(K\rightarrow W\) mode-conversion metric，而不是只看 amplitude ratio。
5. 用 SST 或独立 TIW index 验证 GLORYS vorticity resonance window，不要完全依赖 reanalysis vorticity。
6. 用 event-level mixed model 或 sign-flip permutation，避免当前 bootstrap p 值解释问题。
7. 把 Fig.1 改成“spectral matching vs mismatch”，不要再画旧 \(\Lambda\sim1\) 故事。

---

# 9. 我建议的新摘要口径

现在摘要应该从“已经证明机制”改成“发现并初步验证机制”。可以写成：

> Topological theory predicts robust equatorial Kelvin waves, yet the mechanism controlling their breakdown in the real ocean remains unclear. Here we combine multi-mission altimetry, SWOT snapshots, ERA5 winds and GLORYS currents to track seven Kelvin wave events during the 2023–2024 El Niño. A perturbation-amplitude criterion fails: island wakes and TIW vortices can have comparable local vorticity but produce opposite wave responses. We propose a resonance-window criterion in which protection fails only when perturbations occupy the \((k,\omega)\) window capable of coupling Kelvin waves to westward modes. TIW-zone events show a suggestive relation between resonant vorticity power and Kelvin amplitude loss, whereas island-chain controls do not. Although the present sample is not yet statistically conclusive, the framework defines a pre-registered test for the 30-year altimetric record.

这个版本更稳。它不会因为 \(p=0.086\) 被审稿人抓住说 overclaim。

---

# 10. 最终判断

**机制方向：值得继续，而且比上一版更有冲击力。**

V1 被数据否定，V2 共振窗口机制是一个真正有意思的新解释。这个转折本身是科学上的进步。

**结果是否成立：部分成立。**

成立的是：V1 扰动幅度判据失败；TIW 区与 island 区的谱结构确实不同；\(\Lambda_2\) 与 TIW 区 amplitude retention 有 suggestive correlation。

尚未成立的是：\(\Lambda_2\) 已经证明控制拓扑保护失效；TIW 共振散射已经被直接观测到；SWOT 已经 event-matched 解析 Kelvin 二维结构。

**是否达到 NC：现在还不到。**

如果 1993–2025 扩展事件库验证 \(\Lambda_2\) 机制，并补上 mode conversion、窗口敏感性、SWOT 时间匹配和可复现图件脚本，就有机会冲 NC。当前版本更适合定位为“机制发现 + 预注册验证前的初稿”，不建议直接作为 NC 最终稿提交。
