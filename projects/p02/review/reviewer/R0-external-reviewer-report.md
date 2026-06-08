# OpenSCI-Ocean p02 项目审查与修改建议

> 对象：<https://github.com/pangeo-data/OpenSCI-Ocean/tree/main/projects/p02>  
> 主题：基于 SWOT / DUACS / AI 的赤道 Kelvin/Yanai 拓扑波鲁棒性研究  
> 目标期刊参考：Nature Communications（NC）

---

## 总体判断

我仔细看了你这个 `p02` 项目的目录结构、`analysis/` 脚本、`figures/` 初步图、`manuscript/paper.tex`、`manuscript/figures/` 的投稿图脚本，以及 `README_research.md` 和内部 AI 审查记录。原始 NetCDF 数据没有随仓库提交，这和项目说明“raw data must not be committed”的原则一致，所以我做的是**静态代码审查 + 图面审查 + 初稿逻辑审查**，不是完整数值复算。

项目主问题、假设和数据路线在 README 中写得比较清楚：核心是检验赤道 Kelvin/Yanai 波的拓扑鲁棒性及其失效条件，数据上以 SWOT、DUACS、ERA5、TAO/TRITON、Argo、GLORYS 等为支撑。

**大方向是值得继续的，但目前这个版本离 Nature Communications 还差一大截。**

它现在更像是一个由 AI 快速搭建出来的“可行性原型”：科学故事有潜力，代码骨架也有雏形，但当前结果链条还不能支撑论文里的强结论，尤其不能支撑 “SWOT revealed”、“first observational test”、“protection holds/breaks down near Λ≈1” 这类 NC 级表述。

最主要的问题不是选题方向，而是**证据等级不够**。目前最像真实观测结果的是 DUACS Hovmöller 图和初步事件检测；SWOT 只展示了一个经向剖面，而且这个剖面并不支持典型 Kelvin 波赤道局域结构；鲁棒性分析主要来自 DUACS 射线追踪和固定点对照；Λ 图和部分振幅统计图存在硬编码或合成数据问题。投稿前必须把“示意图 / 合成图 / 真实计算结果”严格分开，否则会被审稿人直接否掉。

---

## 1. 大方向：科学故事是对的，但要收窄

你现在的主线是：

> 拓扑理论预言赤道 Kelvin/Yanai 波具有保护性；真实海洋中这种保护是否可观测，何时失效？

这个故事是好的。README 里已经明确说这不是证明“海洋是拓扑绝缘体”，而是量化拓扑鲁棒性在真实海洋中的适用条件，这个定位是正确的。

但目前的实证分析主要集中在 Kelvin 波，Yanai 波基本没有进入实际计算。初稿虽然多次把 Kelvin 和 Yanai 并列为理论对象，但 Results 中只分析了 Kelvin wave events，Limitations 中也承认 Yanai 波因 SSH 信号较弱而没有做。这意味着当前稿件应该收窄为：

> **真实海洋中赤道 Kelvin 波的拓扑型条件鲁棒性观测检验。**

Yanai 波可以保留在引言和未来工作中，但不要把它写成本文已经验证的对象。

建议把标题从：

> Robustness and breakdown of topological equatorial waves in the real ocean revealed by SWOT altimetry

改成更稳的版本：

> **Conditional robustness of equatorial Kelvin waves in the real ocean from multi-mission altimetry and SWOT snapshots**

或者：

> **Observational constraints on topological-like robustness of equatorial Kelvin waves**

这样更符合当前证据强度。

---

## 2. 当前最严重的几个问题

### 2.1 部分投稿图不是实际观测结果，而是硬编码或合成数据

这是目前最严重的问题。

`make_fig2.py` 中 Fig.2c 的 Gilbert、Line、TIW 振幅保持率是直接写死的数组，例如 Gilbert `[2.65, 3.1, 2.2, ...]`，Line 和 TIW 也是手动数组，不是从 `robustness_metrics.json` 或真实计算输出读取。

更严重的是 `make_fig6_lambda.py` 明确写着 “Generate synthetic but physically motivated data points”，然后用随机数生成 Λ 与 amplitude ratio 的散点。这个图在论文中被表述为 “Λ collapses the observed robustness and breakdown regimes”，这在目前版本中是不成立的。

**修改建议：**

Fig.2c 和 Fig.6 必须改成真实数据驱动：

```text
event × perturbation zone
→ upstream/downstream amplitude
→ coherence / backscatter / leakage / mode conversion
→ GLORYS/Argo/ERA5 估计 δωpert 和 Δωeff
→ 真实 Λ
→ 真实散点图
```

如果 Fig.6 只是概念图，必须在 caption 中写成：

> Schematic illustration of the proposed Λ framework.

不能写成 observed evidence。

---

### 2.2 当前 SWOT 证据不足以支撑 “SWOT revealed”

你的核心创新本来应该是 SWOT 的二维宽刈幅观测。但目前实际 SWOT 分析很弱。

`p1_03_swot_meridional_profile.py` 只是从 cycle 20 中找一个中心太平洋通过赤道的 pass，然后提取一个经向剖面；它没有严格匹配事件库中的 Kelvin 波事件、没有根据事件传播射线判断该 pass 是否正好采到波峰、也没有做背景场扣除。

图上也很明显：所谓 SWOT meridional profile 的最大值在约 6–7°N，赤道附近反而不是峰值；红色理论 Gaussian 以赤道为中心，而蓝色 SWOT 曲线和它严重不一致。这个图更像是 “SWOT 剖面受到 off-equatorial TIW/Rossby/背景 SSH 污染”，不能作为 Kelvin 波赤道俘获结构的正证据。

论文里也写了 “observed peak near 5–7°N rather than centred on the equator”，这和 “SWOT resolves Kelvin wave meridional trapping” 之间存在张力。

**修改建议：**

不要用这个图证明 Kelvin 波。要么把它改成反例，说明真实 SWOT 剖面是多模态叠加；要么重新做 SWOT 匹配分析：

1. 对每个 Kelvin 事件计算预测波峰位置：

   $$
   x(t)=x_0+c(t-t_0)
   $$

2. 搜索 SWOT pass 是否在事件窗口内穿过预测波峰附近，例如：

   $$
   |x_\mathrm{SWOT}-x(t)|<5^\circ,\quad |t_\mathrm{SWOT}-t_\mathrm{event}|<3\ \mathrm{days}
   $$

3. 对该 pass 做局地背景扣除，例如减去 ±10–20° 经向 / 纬向低通背景；
4. 拟合赤道模态，而不是只画 Gaussian：

   $$
   \eta(y)=a_0+a_K\phi_K(y)+a_Y\phi_Y(y)+a_R\phi_R(y)+\epsilon
   $$

   其中 Kelvin 模态近似对称 Gaussian，Yanai 模态近似反对称结构；

5. 只有当 $a_K$ 显著、峰值接近赤道、且与 DUACS/TAO 事件时间一致时，才称为 SWOT 观测到 Kelvin 结构。

---

### 2.3 事件库 “11 个事件” 很可能不是 11 个独立事件

事件 catalog 里有明显重复：K01/K02、K03/K04、K06/K07、K09/K10 都是时间上高度重叠、只是起始经度略有不同的同一波列或同一宽信号脊线。catalog 中 K01 和 K02 都从 2023 年 5 月中下旬传播到 7 月中旬，终点都在约 274–275°E；K03/K04、K06/K07、K09/K10 也有类似重叠。

Hovmöller 图也显示多条黑线贴在同一片红色背景异常上，很难把它们视为独立 Kelvin 波事件。

`p1_04_kelvin_event_detection.py` 的检测逻辑是沿固定相速度 $c=2.5\,\mathrm{m\,s^{-1}}$ 的 ray 取平均，只要 mean SLA > 0.03 m 就保留。这在 2023 El Niño 背景下很容易把宽广的正 SSH anomaly 当成多个 Kelvin 事件。

**修改建议：**

事件识别不要按起点经度去重，而要按 Kelvin ray 的截距聚类。定义：

$$
\tau = t - \frac{x}{c}
$$

同一个 Kelvin wave ridge 的 $\tau$ 应该相近。可以用 Hough/Radon transform 在 $c=1.5$–$3.5\,\mathrm{m\,s^{-1}}$ 范围内搜索斜线，然后按 $\tau$、持续时间、空间覆盖和振幅聚类。每个事件输出：

```text
event_id
ridge_intercept τ
best_phase_speed c
confidence score
start/end time
start/end longitude
wind forcing evidence
TAO validation flag
SWOT coverage score
```

当前 11 个事件很可能应合并成约 6–7 个独立事件。统计检验中的 $n=11$ 和 event×zone 的 $n=24$ 不能直接当作独立样本。

---

### 2.4 频谱分解目前不能作为 Kelvin/Rossby/TIW 分离证据

`p2_01_spectral_decomposition.py` 用 2D FFT 做波数-频率滤波，先把 NaN 直接填成 0，然后按 $k$ 和 $\omega$ 的符号和相速范围划分 Kelvin、Rossby、TIW。

这里有几个问题：

第一，NaN → 0 会产生明显谱泄漏。第二，赤道太平洋有限区域 + 2023–2024 强 ENSO 背景下，未充分 detrend / window / taper 就做全域 FFT，会把低频大尺度背景泄漏到各个频带。第三，代码中 eastward / westward 的符号约定没有用合成波验证，很可能和 numpy FFT 的符号约定相反。第四，输出图中 Kelvin 只有 2.3% 能量，Rossby 2.0%，TIW 0.2%，Residual 高达 95.7%，这说明该分解没有真正解释主信号。

这个图目前不能作为“模式分离成功”的证据。相反，它暴露了方法尚未成熟。

**修改建议：**

做一个合成验证脚本：

```python
eta = cos(k*x - omega*t)  # eastward
eta = cos(k*x + omega*t)  # westward
```

确认你的 FFT 符号和 filter mask 是否正确。然后真实数据处理至少要加入：

1. 线性插值或基于背景场的缺测填补，不能 NaN → 0；
2. Hann / Tukey taper；
3. 去线性趋势、去 ENSO 低频背景或 90–120 天高通；
4. 用 cycles/day 与 rad/s 的单位转换说明；
5. 用合成 Kelvin/Rossby/TIW 混合场做 OSSE，报告分离误差；
6. 最好采用 Wheeler–Kiladis 风格的 $k$-$\omega$ 滤波或 Radon / wavelet 方法，而不是一次性 2D FFT。

---

### 2.5 鲁棒性指标目前不支持强结论

`p3_01_robustness_metrics.py` 中的 backscatter index 是在局地窗口中只按空间波数正负分能量，没有真正区分传播方向；传播方向必须在 $k$-$\omega$ 空间定义，而不是只看 $k_x$。此外它是在已经滤波后的 Kelvin/Rossby 字段上再算 backscatter，这会把结论强烈依赖于前面的滤波定义。

图 `p3_robustness_comparison.png` 显示 Kelvin 与 Rossby 的 coherence 差异 p=0.762，backscatter B 基本都是 0.5，没有任何区分力。这张图不能用来支持“Kelvin 更鲁棒”。

`p3_02_ray_robustness.py` 的问题更关键：所谓 control 实际上是 stationary control，即 speed=0，不是 Rossby control。代码里也写了 `rossby_results = [] # actually "control" results (stationary)`。图上 Kelvin 的 up-down coherence 和 lag-1 persistence 还低于 stationary control，唯一看起来强的是 amplitude ratio，但这可能来自背景海平面梯度、风强迫持续输入、El Niño 大尺度正异常或波导聚焦，并不等于拓扑保护。

还有一个统计 bug：`p3_02` permutation test 中每次 permutation 调用了两次 `np.random.permutation(combined)`，前半组和后半组不是同一个随机重排的互补分组，p 值不可靠。

**修改建议：**

立即重写鲁棒性分析。最低要求：

1. 使用真正的对照组：
   - westward Rossby ray，速度约 $-0.2$ 到 $-0.8\,\mathrm{m\,s^{-1}}$；
   - off-equatorial control，例如 5–8°N/S；
   - time-shifted placebo event；
   - randomized perturbation-zone control。
2. 统计上用 paired design：同一个 event 经过不同 zone，或同一个 zone 对 Kelvin/control。
3. 用 two-sided permutation 或 bootstrap，event 作为 block，而不是把 event×zone 当完全独立样本。
4. 把 amplitude ratio、coherence、backscatter、mode conversion 分开，不要只靠 amplitude ratio。
5. 如果 amplitude ratio > 1，只能解释为“局地放大 / 聚焦 / 强迫输入”，不能直接解释为“鲁棒性”。

正确的 permutation 应类似：

```python
rng = np.random.default_rng(2026)
combined = np.r_[k_vals, r_vals]
n_k = len(k_vals)
obs = np.mean(k_vals) - np.mean(r_vals)

diffs = []
for _ in range(10000):
    perm = rng.permutation(combined)
    diffs.append(np.mean(perm[:n_k]) - np.mean(perm[n_k:]))

p_two_sided = np.mean(np.abs(diffs) >= abs(obs))
```

---

## 3. Λ 参数：概念有价值，但当前数值和图都不可靠

你提出的 Λ：

$$
\Lambda = \frac{\Delta\omega_{\mathrm{eff}}}{\delta\omega_{\mathrm{pert}}}
$$

是这个课题最有希望变成 NC 级别机制图的部分。README_research 已经把分母统一成频率量纲，这是正确方向。

但当前仍有三个问题。

第一，README_research 中还残留了错误表达：

> $\Delta\omega_\mathrm{eff}=\beta c/f_0\approx f$ at equator

这个公式不合适。paper.tex 中改成了 $\sqrt{\beta c_1}$，方向对了。

第二，数值算错了。若取：

$$
\beta \approx 2.3\times10^{-11}\ \mathrm{m^{-1}s^{-1}},\quad c_1 \approx 2.5\ \mathrm{m\,s^{-1}}
$$

则：

$$
\sqrt{\beta c_1}
= \sqrt{2.3\times10^{-11}\times 2.5}
\approx 7.6\times10^{-6}\ \mathrm{s^{-1}}
$$

不是 manuscript 中写的 $2.4\times10^{-6}\ \mathrm{s^{-1}}$。如果你要换成 cycles/day，还要除以 $2\pi$ 再乘以 86400；如果用 rad/day，则直接乘以 86400。现在文稿里 angular frequency 和 cycles/day 有混用风险。

第三，Fig.6 的 Λ 散点是合成随机数据，不是 GLORYS/Argo 计算结果。这张图如果作为“结果图”非常危险。

**修改建议：**

把 Λ 的计算落到真实数据：

$$
\Delta\omega_{\mathrm{eff}} = \sqrt{\beta c_1}
$$

$$
\delta\omega_{\mathrm{pert}} =
\max\left(
|\zeta|/2,\ |U k_x|,\ |\partial_y U|,\ \delta\omega_{\mathrm{TIW}}
\right)
$$

其中 $c_1$ 来自 Argo / TAO / 文献敏感性范围；$\zeta$、$U$、$\partial_yU$ 来自 GLORYS；$k_x = 2\pi/\lambda_K$；$\delta\omega_{\mathrm{TIW}}$ 可从 SST / SSH 的 20–40 天带通信号估算。每个 event×zone 都给出一个 $\Lambda$ 和不确定性区间，然后再画真实 Fig.6。

---

## 4. 脚本层面的具体问题

### 4.1 可复现性不足

很多脚本写死了本地路径，比如 `/Users/zhulin/aitest/...` 或 `/mnt/d/v2_0_1/Basic`。`p0_01_download_duacs.py`、`p1_01_hovmoller_equatorial.py`、`p1_02_swot_eq_scan.py`、`p1_03_swot_meridional_profile.py` 都有这个问题。

建议建立：

```text
projects/p02/config.yaml
projects/p02/environment.yml
projects/p02/analysis/utils/paths.py
projects/p02/analysis/utils/geo.py
projects/p02/analysis/utils/wave_filters.py
```

并把脚本改成：

```bash
python analysis/p1_01_hovmoller_equatorial.py --config config.yaml
```

`.gitignore` 目前只忽略了 aux、pdf、npz 等，没有系统忽略 `.nc`、`.zarr`、credential、large intermediate files。建议补充：

```gitignore
data/**/*.nc
data/**/*.zarr/
data/**/*.grib
data/**/*.h5
data/**/raw/
data/**/interim/
*.cdsapirc
.env
__pycache__/
.ipynb_checkpoints/
```

---

### 4.2 DUACS 下载与经度处理需要规范化

`p0_01_download_duacs.py` 把太平洋分成 130–180 和 -180–-80 两段下载，再 concat。这个思路可以，但最好在合并时直接把经度统一成 0–360，并排序后写入文件，否则后续每个脚本都要重复 remap / sort。

另外，当前使用的是 NRT allsat L4 DUACS。投稿级研究最好优先使用 delayed-time / reprocessed 产品，NRT 适合快速探索，不适合作为最终论文主数据。这个问题需要在数据源说明中澄清。

---

### 4.3 ERA5 风应力脚本目前没有真正进入分析

README 和方法计划说要用 ERA5 / CCMP 风应力确认 WWB 源，但当前 Kelvin 事件检测和 manuscript 并没有完成风强迫确认。`p0_02_download_era5_wind.py` 只是下载脚本，而且注释中提到 “convert from accumulated J/m² to N/m²”，但代码没有做单位转换。

建议增加一个脚本：

```text
p1_05_wind_burst_confirmation.py
```

输出每个 Kelvin event 的 WWB 支撑证据：

```text
event_id
τx anomaly max
WWB longitude/time
lag to Kelvin event
correlation with ray amplitude
confidence flag
```

没有风强迫或 TAO 验证的事件，不应进入“高置信度事件库”。

---

### 4.4 p1_04 和后续脚本字段不一致

`p1_04_kelvin_event_detection.py` 生成的事件字段是 `start_time`, `end_time`, `start_lon`, `end_lon` 等。但 `p3_01_robustness_metrics.py` 和 `p3_02_ray_robustness.py` 使用的是 `event["start"]`, `event["end"]`, `event["lon0"]`, `event["id"]`。

当前 committed 的 `kelvin_event_catalog.json` 是手工整理后的字段，所以能跑后续脚本；但如果重新运行 `p1_04`，会覆盖出不兼容 catalog。这是复现性硬伤。

建议统一 catalog schema，并用一个 `events.py` 校验：

```python
REQUIRED_EVENT_FIELDS = [
    "id", "start", "end", "lon0", "lon1",
    "phase_speed_mps", "mean_sla", "max_sla",
    "confidence", "source_wind_flag"
]
```

---

## 5. 图件逐张审查

### Fig. Hovmöller：可以保留为可行性图，但不要过度解释

`p1_hovmoller_equatorial_ssh.png` 能显示 2023 El Niño 期间赤道太平洋 SSH anomaly 的大尺度东传结构，是一个不错的 Phase 1 可行性图。

但它目前没有证明“拓扑波鲁棒性”。它只能证明：

> DUACS SSH 中存在与 Kelvin 波相速相近的东传 anomaly ridge。

需要补充：

1. 更长气候态或高通滤波；
2. 相速自动估计，不只是画参考斜率；
3. 风强迫确认；
4. 事件去重；
5. TAO / 潮位站独立验证。

---

### Fig. Kelvin events：事件线过密，重复明显

`p1_kelvin_events_detected.png` 标出 11 条事件线，但很多线明显贴在同一 anomaly ridge 上。

建议重新画成：

- 每条 ridge 只保留一个事件；
- 用透明度表示 event confidence；
- 在图上标注 WWB 时间、扰动区、SWOT pass；
- 对每个事件给出 best-fit speed 和置信区间，而不是固定 $c=2.5\,\mathrm{m\,s^{-1}}$。

---

### Fig. SWOT meridional profile：目前不能作为 Kelvin 证据

这张图显示的蓝色 SWOT 曲线与赤道 Gaussian 完全不匹配，峰值在 6–7°N，赤道附近有低值。

建议改标题为：

> **Example SWOT meridional profile showing strong off-equatorial mode contamination**

或者重做事件匹配和模态拟合后再作为 Kelvin 结构图。

---

### Fig. Spectral decomposition：当前结果显示方法失败，而不是成功

`p2_spectral_decomposition.png` 中 residual 占 95.7%，Kelvin/Rossby/TIW 总共解释不到 5%。这说明当前滤波没有有效分离主信号。

建议不要把它作为 Results 主图。可以放到 Supplementary Methods，说明传统 FFT 分解的局限，进而引出更可靠的 OSSE / AI / 波模拟合方法。

---

### Fig. Robustness comparison：不能支持拓扑鲁棒性

`p3_robustness_comparison.png` 中 Kelvin vs Rossby coherence p=0.762，backscatter 基本都是 0.5。这不是正结果。

`p3_ray_robustness_comparison.png` 显示 Kelvin amplitude ratio 较高，但 coherence 和 persistence 并没有优势，stationary control 甚至更强。

建议在当前版本中删除 “topological robustness evidence” 这个图题。改成：

> **Preliminary ray-following amplitude diagnostics**

不要称其为“拓扑鲁棒性”。

---

### Fig. Λ：不能用合成数据冒充观测图

`fig6_lambda.png` 看起来很漂亮，但它来自随机生成的 “synthetic but physically motivated data points”。

这张图可以保留为 Fig.1 里的 conceptual schematic，但绝不能作为 Results 机制图。NC 审稿人如果发现这一点，会直接认为论文不可信。

---

## 6. 初稿 `paper.tex` 的主要问题

### 6.1 Abstract 过度声称

摘要目前说 “we show Kelvin waves maintain or enhance their amplitude at island chains... lose energy in TIW zones... introduce Λ that collapses observed regimes”。

这个表述目前不成立，因为：

- 振幅结果部分来自硬编码或弱诊断；
- control 不是真正 Rossby / TIW 对照；
- Λ 图是合成随机点；
- SWOT 证据只是一张不匹配的经向剖面。

建议改成非常保守的版本：

> Here we develop a preliminary observational framework combining DUACS event tracking and SWOT wide-swath snapshots to test whether equatorial Kelvin waves retain topological-like robustness in the real ocean. Initial ray-following diagnostics suggest strong sensitivity to perturbation type, but robust attribution requires event-matched SWOT sampling, independent wind/mooring validation, and data-derived estimates of the effective gap-to-perturbation ratio.

在完成真实 Λ 和对照实验前，不要写 “we show”。

---

### 6.2 “SWOT revealed” 与实际分析不匹配

Methods 里真正用于事件识别和鲁棒性分析的是 DUACS L4 daily SSH；SWOT 用于经向剖面快照。因此标题和摘要中 “revealed by SWOT altimetry” 过强。

建议改为：

> from multi-mission altimetry and SWOT snapshots

或者先补上真正的 SWOT event-matched 统计，再保留 SWOT 主标题。

---

### 6.3 “11 distinct events” 需要改成 “candidate events”

当前事件库中重复较多。文稿里 “11 distinct equatorial Kelvin wave events” 应改成：

> 11 candidate Kelvin wave rays, corresponding to approximately N independent wave events after ridge clustering.

等你完成事件去重后，再给正式数字。

---

### 6.4 $\Delta\omega_\mathrm{eff}$ 数值必须修正

`paper.tex` 中写：

$$
\Delta\omega_\mathrm{eff} = \sqrt{\beta c_1} \approx 2.4\times10^{-6}\ \mathrm{s^{-1}}
$$

这个数值不对。若 $c_1=2.5\,\mathrm{m\,s^{-1}}$，应约为：

$$
7.6\times10^{-6}\ \mathrm{s^{-1}}
$$

同时必须说明你用的是 angular frequency 还是 cycles frequency。

---

### 6.5 统计显著性目前不能写得这么强

`paper.tex` 写 amplitude ratio 差异显著，permutation test $p=0.001$。但当前 `p3_02` 的 permutation 实现有 bug，对照组也偏弱。

建议先删除 p 值，或者重算后写：

> using a block bootstrap over independent events

而不是把 event×zone 当独立样本。

---

## 7. 我建议的修订路线

### 第一阶段：把项目从“AI 原型”变成可复现科学分析

优先级最高，建议先完成。

1. 删除或标注所有硬编码 / 合成数据图。尤其是 Fig.2c 和 Fig.6。
2. 所有脚本改成相对路径 + config。
3. 统一 event catalog schema。
4. 更新 `.gitignore`，防止大数据误提交。
5. 建立 `make all` 或 `snakemake` 工作流：

   ```text
   download → preprocess → event_detection → swot_match → metrics → figures → paper
   ```

6. 在每张图 caption 中标注数据来源：DUACS / SWOT / synthetic / schematic。

---

### 第二阶段：重建可信事件库

建议路线：

1. 用 1993–2022 或至少 2010–2022 DUACS 月气候态去除季节循环；
2. 对 2023–2025 SSH 做 20–120 天带通或 90 天高通；
3. 用 Hough/Radon 检测 Kelvin ridge；
4. 允许相速范围 $1.5$–$3.5\,\mathrm{m\,s^{-1}}$，不要固定 2.5；
5. 按 ridge intercept 聚类去重；
6. 用 ERA5 / CCMP WWB 和 TAO / TRITON 验证事件；
7. 每个事件输出 confidence score。

---

### 第三阶段：真正使用 SWOT

建议路线：

1. 全周期扫描 SWOT，不要只扫 cycle 10 / 20 / 30 / 40 / 50；
2. 对每个事件匹配 SWOT pass：事件时间、预测波峰经度、SWOT 覆盖质量、有效像元比例；
3. 做 SSH 背景扣除、质量标志筛选、潮汐 / 内潮敏感性测试；
4. 做经向模态拟合，而不是只画一条 profile；
5. 输出每个事件的 SWOT coverage score。

如果最后发现 SWOT 只提供少量高质量快照，也没关系。那论文标题和贡献要改成 “DUACS 事件追踪 + SWOT case snapshots”，不要把 SWOT 写成主证据来源。

---

### 第四阶段：重做鲁棒性指标

对每个 event×zone 计算：

$$
R_A = \frac{\mathrm{rms}(A_\mathrm{down})}{\mathrm{rms}(A_\mathrm{up})}
$$

$$
C = \frac{|\langle A_\mathrm{up}A_\mathrm{down}^*\rangle|}
{\sqrt{\langle |A_\mathrm{up}|^2\rangle \langle |A_\mathrm{down}|^2\rangle}}
$$

$$
B = \frac{E_\mathrm{west}}{E_\mathrm{east}+E_\mathrm{west}}
$$

$$
M = \frac{E_{\mathrm{Rossby/TIW/residual}}}{E_\mathrm{total}}
$$

但 $B$ 必须来自局地 $k$-$\omega$、wavelet 或 Radon 能量分解，不能只按空间波数正负。对照组至少包括：

- Rossby westward ray；
- stationary placebo；
- time-shifted Kelvin ray；
- off-equatorial ray；
- randomized perturbation-zone ray。

统计上用 paired / block bootstrap：

```text
block = independent Kelvin event
paired unit = event crossing same perturbation zone
test = Kelvin metric - control metric
```

---

### 第五阶段：用真实数据计算 Λ

建议路线：

1. $c_1$：Argo / TAO / 文献范围，给不确定性；
2. $\zeta, U, \partial_yU$：GLORYS；
3. TIW 强度：SST / SSH 20–40 天带通能量；
4. 内潮：先作为敏感性项，不要一开始放进主公式；
5. 每个 event×zone 一个 $\Lambda$，不要用场景平均替代。

真正的主图应该是：

```text
x-axis: Λ with uncertainty
y-axis: coherence / backscatter / amplitude retention
colors: perturbation type
markers: independent event
statistics: mixed-effect regression or bootstrap CI
```

如果这张图能成立，NC 才有希望。

---

## 8. 建议重写后的论文主线

当前稿件应该从“已经证明”改成“建立并验证框架”。重写后的 Results 可以是：

### 8.1 DUACS identifies candidate Kelvin wave events during the 2023 El Niño buildup

先讲候选事件，而不是 11 个独立事件。

### 8.2 SWOT snapshots reveal strong multimodal contamination of the equatorial waveguide

如果当前 profile 不匹配 Gaussian，就把它诚实地变成“真实海洋比理想 Kelvin 模态复杂”的证据。

### 8.3 Ray-following diagnostics show perturbation-dependent amplitude changes, but robustness attribution requires matched controls

当前 amplitude ratio 只能说“有扰动类型依赖”，不能说“拓扑保护”。

### 8.4 A data-derived Λ framework is proposed and tested

等真实 Λ 算完，再把它作为机制结果。

---

## 9. 是否还值得按 NC 做？

**值得继续，但不要用当前版本投稿。**

当前版本最适合定位为：

> Phase 0 / Phase 1 feasibility prototype.

它已经证明了三件有用的事：

1. 赤道太平洋 2023–2024 DUACS Hovmöller 里确实有明显东传 Kelvin-like SSH anomaly；
2. SWOT 数据可以提取赤道经向剖面，但真实剖面很复杂；
3. “条件鲁棒性 + Λ”这个科学故事有潜力，但需要真实数据支撑。

达到 NC 至少还需要补齐四个硬条件：

1. 独立、可验证的 Kelvin event catalog；
2. 事件匹配的 SWOT 二维结构证据；
3. 严格的 Kelvin vs control 鲁棒性统计；
4. 真实 GLORYS / Argo / TAO / ERA5 支撑的 $\Lambda$ 机制图。

---

## 10. 最优先修改清单

按优先级排序：

1. **删除或重标所有 synthetic / hard-coded 结果图**，尤其是 Fig.2c 和 Fig.6。
2. **修正 $\Delta\omega_\mathrm{eff}$ 数值和 angular / cyclic frequency 单位。**
3. **重做事件去重**，把 11 candidate rays 改成独立 event clusters。
4. **修复 `p3_02` permutation test bug。**
5. **加入真正 Rossby / time-shift / off-equator controls。**
6. **把 SWOT pass 严格匹配到 Kelvin event ray。**
7. **补 ERA5 wind burst 和 TAO / TRITON 验证。**
8. **不要把当前 SWOT profile 称为 Kelvin Gaussian 证据。**
9. **把论文标题从 “revealed by SWOT” 改成更保守的 “multi-mission altimetry with SWOT snapshots”。**
10. **在 Methods 里明确哪些图是真实观测、哪些是 schematic、哪些是 synthetic OSSE。**

---

## 一句话总结

**方向对，故事有潜力，但当前证据链有明显断点；先把“真实计算结果”和“AI 生成 / 硬编码示意”彻底分离，再重建事件库、SWOT 匹配、对照组和 Λ 实证图。完成这些后，这个课题才有资格冲 Nature Communications。**
