# 第二轮外部审查 (R-EXT2) 逐项对照 + 修改计划

**审查文件**: `p02_second_review_nc_mechanism.md` (2026-06-10)
**对照版本**: A25 (commit 509c6aa)
**整理时间**: 2026-06-10

---

## 审查者核心判断

> 方向正确，机制新颖，具备冲 NC 的潜力；但当前版本更像"机制发现版/预注册检验前夜"。

**A24-A25 已解决的最大问题**: 样本量从 n=7 扩展到 n=84，核心观测主张（TIW 损失 vs 岛链保持）已跨 30 年显著。

---

## P0: Block 级（不改不能投）

### P0-1. Fig.6 脚本仍是 synthetic ❌ 确认存在

- `make_fig6_lambda.py`: 含 "CONCEPTUAL SCHEMATIC — all data points are synthetic random numbers"
- `make_fig6_lambda_real.py`: 读真实 JSON，但只有 V1 两面板
- `make_fig6_lambda_v2.py`: 读真实 JSON，三面板（V1 zone-mean / scale collapse / V2 resonance），与 caption 对应
- **committed figure**: `fig6_lambda.png/pdf` 是 `_v2.py` 生成的三面板真实数据图
- **修改方案**: 删除 `make_fig6_lambda.py` (synthetic) 和 `make_fig6_lambda_real.py` (过时 V1)，将 `make_fig6_lambda_v2.py` 重命名为 `make_fig6_lambda.py`

### P0-2. Fig.5 脚本与图件不一致 ❌ 确认存在

- `make_fig5_spectral.py`: 读 v1 `spectral_decomposition.npz`
- `make_fig_kw_spectra.py`: A22 新增的 ζ(k,ω) 机制谱图（当前论文 Fig.5）
- 论文 Fig.5 现在是 kw spectra 三联图（非 spectral decomposition 六面板）
- **修改方案**: 确认论文引用的 Fig.5 到底是哪个，然后统一脚本命名

### P0-3. Λ₂ 窗口 caveat 被低估 ❌ 确认存在

- `p4_03` 代码: `window_caveat = n_days < 2 * T_MAX_D` (T_MAX_D=50)
- 所有事件窗口 50–65 天 < 100 天 → **全部 window_caveat=true**
- 正文和 SI 只说 "mainly affects KE05"，与数据不一致
- **修改方案**:
  1. 正文修改为诚实陈述所有事件窗口都存在长周期端分辨率限制
  2. 做三组敏感性测试 (W1: 15-50d, W2: 15-40d, W3: 15-30d)
  3. 考虑扩大事件窗到 ±90d 或 ±120d 重算

### P0-4. SWOT event matching 没用真实 pass 时间 ❌ 确认存在

- `p1_07_swot_event_matching.py` 用 equator-crossing lon 反推 t_predicted，没有用 pass 实际 time 算 time_gap
- **修改方案**: 修复匹配逻辑，用 Δt = t_pass - t_peak(x_pass)，只保留 |Δt| < 1.5 或 3 天
- **或降级**: SWOT 定位为 illustrative snapshot，正文小标题从 "reveals" 改为 "illustrates"

### P0-5. amp_ratio 用 original SSH 而非 Kelvin-filtered ❌ 确认存在

- `p3_03_robustness_v2.py` 第 133 行: `compute_metrics(original, ...)` 而非 `kelvin_field`
- 这意味着 amp_ratio 是沿 ray 的 total SSH rms，不是 Kelvin 模态振幅
- **修改方案**: 新增 R_K (Kelvin-filtered amp_ratio) 作为主因变量；original 可保留作为辅助
- **注意**: A25 的 n=84 历史扩展 (p3_04) 也需要同步修改

### P0-6. stationary control 跨 zone 重复 ❌ 确认存在

- `p3_03` 第 76 行: `speed=0` → `dt_to_zone = 20` 固定，不随 zone 变化
- 同一事件在三个 zone 的 stationary metrics 完全相同
- **修改方案**: 删除 stationary control，或改为 randomized ray / phase-randomized / off-equatorial control
- A25 的 p3_04/p3_05 zone-matched 分析已不依赖 stationary，影响有限

### P0-7. 质量过滤后 n 不一致 ⚠️ 需核实

- rms_up > 0.01 过滤后 Line Islands 可能是 n=6 而非 n=7（KE01 Line rms_up=0.00933）
- **修改方案**: 统一过滤阈值，正文数字与实际一致
- **注意**: A25 n=84 版本可能已自动处理

### P0-8. 正文残留 "gap closes" 旧语言 ❌ 确认存在

- paper.tex 第 89 行: "perturbation amplitudes approach the frequency gap scale, is consistent with the topological prediction of protection breakdown when the effective gap closes"
- 这与 V1 失效、V2 共振机制矛盾
- **修改方案**: 删除或改写为 V2 共振机制语言

---

## P1: NC 门槛项

### P1-1. 扩展到 ≥20 事件 ✅ 已完成 (A24-A25)

- 84 事件，核心主张 TIW-Line diff = -0.68 [-0.88, -0.49] 显著 (n=82)

### P1-2. Λ₂ 窗口敏感性 ✅ 完成 (p4_04, 2026-06-11)

- 三组窗口全部完成: W15-50 / W15-40 / W15-30
- TIW zone 全部显著 (p < 0.01), 符号稳定
- W15-30 下 Line Islands 变为不显著 (p=0.52), Gilbert 也不显著 (p=0.38)
- 窗口敏感性通过：TIW 稳健，岛链随窄窗口变弱（符合预期）

### P1-3. Synthetic OSSE 验证 ❌ 待做

- 构造 Kelvin + static wake / Kelvin + TIW resonant perturbation，验证 Λ₂ 恢复已知 mode conversion

### P1-4. K→W mode-conversion metric ❌ 待做

- M_{K→W} = (E_westward^down - E_westward^up) / E_K^up
- 直接观测 mode conversion 而非仅看 amplitude loss

### P1-5. 独立 TIW index 验证 ❌ 待做

- 用 SST 或独立 TIW index 代替 GLORYS vorticity

### P1-6. event-level permutation / mixed model ⚠️ 待改进

- A25 用 block bootstrap，但审查者指出不是真正零假设检验
- 建议 sign-flip permutation 或 mixed-effects model

### P1-7. Fig.1 改成 spectral matching 新机制 ❌ 确认仍是旧版

- `make_fig1_framework.py` 第 169/171 行: 仍标注 Λ >> 1 和 Λ ~ 1
- 应改为 "spectrally mismatched" vs "resonant (k,ω) channel active"

---

## 额外审查要点

### 摘要口径过强

- 当前: "Resonant coupling, not perturbation strength, sets where oceanic topological protection fails."
- 建议改为: "The results suggest that breakdown is better organized by a resonance-window metric than by perturbation amplitude alone."
- **注意**: A25 n=84 结果可能允许更强措辞，但需等 Λ₂ 检验

### SWOT 小标题

- 当前: "SWOT reveals two-dimensional equatorial wave structure"
- 建议: "SWOT illustrates..." 或 "SWOT snapshots show..."

---

## 修改优先级

**第一阶段 (Λ₂ 检验优先)**:
1. GLORYS 252/252 完成 → 跑 Λ₂ 预登记检验 (p4_03 复用)
2. Λ₂ 窗口敏感性三组测试
3. 根据结果决定 NC vs GRL 定位

**第二阶段 (论文修订)**:
1. P0-1/2: 图件脚本清理
2. P0-3: 窗口 caveat 正文修正
3. P0-5: Kelvin-filtered amp_ratio
4. P0-6: 替换 stationary control
5. P0-7/8: 数字一致性 + 旧语言清理
6. P1-7: Fig.1 更新
7. 摘要降调

**第三阶段 (NC 增强，视 Λ₂ 结果决定)**:
1. P1-3: Synthetic OSSE
2. P1-4: K→W mode-conversion metric
3. P1-5: 独立 TIW index
4. P1-6: permutation / mixed model
