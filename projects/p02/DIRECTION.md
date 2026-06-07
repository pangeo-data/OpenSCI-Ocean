# 研究方向（DIRECTION.md）

> 立项种子（v0.0）。**写完即冻结**——v0.1 起所有方向调整通过 README.md 的版本号迭代。
> ClaudeA 与 ClaudeB 都会读这份文件作为项目"做什么"的 single source of truth。

## 1. 主题与工作标题

- **工作标题（EN）**: Robustness and breakdown of topological equatorial waves in the real ocean revealed by SWOT altimetry
- **中文一句话**: SWOT 揭示真实海洋中赤道拓扑波的鲁棒性与失效机制
- **核心科学问题**: 理论预言赤道 Kelvin/Yanai 波受拓扑保护（Chern 数 ±2），但真实海洋中这种保护是否留下可观测指纹？在什么条件下有效？什么条件下失效？
- **差异化（vs Delplace et al. 2017 Science）**: 标杆是纯理论，零观测验证。本文首次用 SWOT 2D SSH 在真实海洋中定量检验拓扑波鲁棒性，并提出有效谱隙-扰动比 Λ 作为失效判据。

## 2. 硬约束

| 项 | 值 |
|---|---|
| 投稿目标 / venue | Nature Communications |
| 篇幅上限 | NC 无严格限制；计划 ~6000 词 + 5 主图 + Extended Data |
| Deadline | 无硬性截止；Phase 1 可行性验证目标 4 周 |
| 算力 | 混合：Mac 本地（数据下载/分析/绘图） + 远程 WSL（AI 模型训练） |
| 数据 | 全部公开数据（SWOT/CMEMS/ERA5/PO.DAAC/PMEL） |
| Case / 对象 | 赤道太平洋 5°S–5°N, 130°E–80°W, 2023–2025 SWOT 时段 |

### 2.5 计算环境

| 项 | 值 |
|---|---|
| **执行环境** | 混合（本地 Mac + 远程 WSL） |
| **远程连接** | `ssh think@100.111.65.40`（Tailscale） |
| **本地 OS** | macOS Darwin 25.4.0 arm64 |
| **远程 OS** | Windows + WSL2 Ubuntu |
| **本地 Python** | 3.14.3 (homebrew, system) |
| **远程 Python** | 3.12.3 (WSL) |
| **本地 GPU** | 无（Apple Silicon，无 PyTorch） |
| **远程 GPU** | PyTorch 2.6.0+cu124（CUDA toolkit 已安装；需确认实际 GPU 硬件） |
| **本地关键依赖** | xarray 2026.2.0, numpy 2.4.3, scipy 1.17.1, matplotlib 3.10.8, cartopy 0.25.0, netCDF4 1.7.4, copernicusmarine, earthaccess, ee (GEE) |
| **远程关键依赖** | torch 2.6.0+cu124, xarray 2026.4.0, numpy 2.4.4, scipy 1.17.1, netCDF4 1.7.4 |
| **原始数据目录** | 本地: `/Users/zhulin/aitest/OpenSCI-Ocean/projects/p02/data/` |
| **输出目录** | `/Users/zhulin/aitest/OpenSCI-Ocean/projects/p02/figures/` |
| **文件同步** | 坚果云（Mac ↔ Windows 同步） |

**数据获取优先级（铁律）**：

| 优先级 | 方式 | 本项目示例 |
|---|---|---|
| **P0 本地已有** | 远程台式机 D 盘 | SWOT L3 全量数据（150 cycle, D:\v2_0_1\Basic\） |
| **P1 云端计算** | ARCO-ERA5 zarr / GEE | ERA5 风应力统计量 |
| **P2 云端导出（小量）** | CMEMS subset / GEE export | DUACS L4 SSH 赤道子集（~2GB） |
| **P3 公开直链** | NOAA/GEBCO | TAO 浮标、GEBCO 地形 |
| **P4 已认证下载** | earthaccess / CMEMS | Argo、GLORYS（Phase 3） |

**任务分工**：

| 任务类型 | 执行环境 | 备注 |
|---|---|---|
| SWOT 数据处理（大量 I/O） | **远程 WSL** | 数据在 D:\v2_0_1\Basic\，不搬回 Mac |
| DUACS/ERA5 小量下载 | 本地 Mac 或远程 | copernicusmarine/ARCO-ERA5 zarr |
| Hovmöller 分析/绘图 | 本地 Mac | xarray + matplotlib + cartopy |
| AI 模式分解训练 | 远程 WSL | PyTorch + CUDA（Phase 2） |
| 结果同步 | 坚果云 | 远程→Mac：结果文件放 /mnt/e/Documents/temp/ |

## 3. 初步判断

- **想抓的核心问题**: 拓扑理论预言的波保护在真实海洋中是条件性的，Λ 参数统一描述保护与失效的转变
- **担心的风险**:
  - SWOT 21 天重访太稀疏，可能无法追踪完整 Kelvin 波事件
  - AI 模式分解在真实数据上的可靠性
  - 审稿人可能认为"不需要拓扑框架也能解释观测"
  - 有效谱隙 Δω_eff 在真实海洋中的定义不清晰
- **不想做的事**: 不做全球尺度分析（聚焦赤道太平洋）；不做 GCM 耦合模拟；不声称"海洋是拓扑绝缘体"

## 4. 给 ClaudeA 的指示（v0.1 优先回答）

- 3 个 Science Questions 对应 3 个假设（H1 可观测指纹、H2 统计鲁棒性优势、H3 条件失效）
- Phase 1 时间分配：4 周内完成可行性验证
- 5 图 figure list（理论框架、SWOT 观测、AI 验证、鲁棒性证据、统一机制）
- 显式引用 Delplace et al. 2017 (Science) 作为理论锚点
- **Phase 1 第一步：先下载数据、做 Hovmöller 图，确认能看到 Kelvin 波事件**
- 参考文献：`literature/delplace2017_topological_origin_equatorial_waves.pdf`
- 研究方案：`literature/SWOT_topological_waves_research_plan.pdf`
- 数据清单：`literature/data_requirements.md`

## 5. 给 ClaudeB 的指示（R01 重点核）

- SQ 是否真有科学价值——"在真实海洋检验拓扑理论"是否足够 novel for NC，还是只是 confirmation study？
- 审稿人最可能的攻击路线："不需要拓扑也能解释"——A 是否准备了足够的 defense？
- Λ 参数的定义是否足够严格、物理上是否 well-motivated（还是 ad hoc fitting）？
- SWOT 时间采样限制是否被充分认识和处理？
- Phase 1 的止损点是否清晰：如果 Hovmöller 看不到 Kelvin 波事件，是否该放弃？

---

*DIRECTION.md v0.0 — 2026-06-07 冻结*
