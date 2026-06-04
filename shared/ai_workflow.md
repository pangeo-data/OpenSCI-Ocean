# AI Workflow Guide / AI 工作流指南

本文档定义每个项目各阶段 AI 的标准使用方式和 Prompt 模板。

---

## D0: Explore — AI 辅助选题

### 目标
快速评估一个研究方向的新颖性、可行性和发表潜力。

### AI 任务清单
1. 文献快速调研（最近 3 年该方向的关键论文）
2. 识别 knowledge gap
3. 评估数据可用性
4. 初步判断适合哪个期刊

### Prompt 模板

```
我想研究 [科学问题]。请帮我完成以下任务：

1. 列出该方向最近 3 年最重要的 10 篇论文（标题、作者、期刊、年份、DOI）
2. 总结目前的研究现状和共识
3. 识别尚未解决的关键科学问题（knowledge gaps）
4. 评估使用 [具体数据集] 研究这个问题的可行性
5. 建议最适合投稿的 2-3 个期刊及理由

注意：列出的文献必须是真实存在的，我会逐一核验。如果不确定某篇文献是否存在，请明确标注"需要核验"。
```

### 人类审查重点
- [ ] 核验 AI 列出的每一篇文献是否真实存在
- [ ] 判断 knowledge gap 是否真的存在（而非 AI 编造）
- [ ] 评估选题的物理意义

---

## D1: Draft — AI 生成初稿

### 目标
在 1 天内用 AI 生成包含完整结构的论文初稿。

### AI 任务清单（按顺序）

#### Step 1: 研究设计
```
基于以下科学问题：[问题描述]
数据来源：[数据集列表及时空范围]

请设计一个完整的研究方案，包括：
1. 研究假设
2. 数据处理流程
3. 分析方法（具体到算法和公式）
4. 预期结果
5. 可能的物理解释
```

#### Step 2: 数据分析代码
```
请为以下分析任务编写 Python 代码：
[具体分析任务描述]

要求：
- 使用 xarray 处理 NetCDF 数据
- 使用 matplotlib + cartopy 绑图
- 代码中注明数据来源 URL
- 输出图表保存为 PNG（300 DPI）
- 包含 requirements.txt
```

#### Step 3: 论文撰写
```
请基于以下分析结果撰写论文初稿，目标期刊为 [期刊名]。

分析结果摘要：[粘贴关键发现]
图表列表：[图 1 描述]、[图 2 描述]...

论文结构要求：
- Abstract（~250 words）
- Introduction（~800 words，从大背景到具体问题，结尾明确提出本文目标）
- Data and Methods（~600 words，数据来源、处理方法、分析方法）
- Results（~1000 words，逐图逐表描述发现）
- Discussion（~800 words，物理解释、与前人对比、局限性、未来展望）
- Conclusions（~300 words）

写作风格：
- 简洁直接，避免空洞套话
- 每个段落有明确的论点
- 不使用 "it is worth noting"、"delve into"、"comprehensive" 等 AI 典型用语
- 避免过度 hedge（不要 "may potentially"、"could possibly"）
```

### 产出
- `manuscript/v1_ai_draft/` 下的初稿（LaTeX 或 Markdown）
- `analysis/` 下的全部代码
- `figures/` 下的全部图表
- `logs/` 下的 AI 交互日志

---

## D2: Deliver — 人类审查

### 目标
Domain Expert 审查 AI 初稿，纠正科学错误，补充物理解释。

### 工作流
1. 使用 [REVIEW_CHECKLIST.md](../REVIEW_CHECKLIST.md) 中的 D2 清单逐项检查
2. 在 GitHub PR 中逐行评论标注问题
3. 对重大科学问题提交 Issue 讨论
4. 修改后产出 `manuscript/v2_delivery/`

### AI 辅助修改 Prompt
```
审稿人/审查者提出了以下问题，请据此修改论文：

问题 1：[具体问题]
问题 2：[具体问题]
...

修改要求：
- 只修改被指出的部分，不要改动其他内容
- 对每处修改说明理由
- 如果审查意见涉及物理机制，请给出你的分析但标注"需人工确认"
```

---

## D3: Review — 内部评审

### 目标
模拟期刊审稿流程，由另一位参与者扮演审稿人。

### AI 辅助模拟审稿
```
请扮演 [目标期刊] 的审稿人，对以下论文进行严格评审。

[粘贴论文全文或关键章节]

请按以下格式给出审稿意见：
1. 总体评价（1 段）
2. 主要问题（Major Issues）：逐条列出
3. 次要问题（Minor Issues）：逐条列出
4. 推荐决定：Accept / Minor Revision / Major Revision / Reject

审稿标准：
- 科学新颖性和重要性
- 方法是否严谨
- 数据是否充分支撑结论
- 写作质量
- 与该期刊已发表论文的水平对比
```

### 产出
- 审稿意见记录在 Issue 中
- 逐条回复（Response to Reviewers）
- 修改后产出 `manuscript/v3_final/`

---

## D4: Submit — 投稿准备

### AI 辅助任务
- 生成 Cover Letter
- 格式检查（字数、图表数量、参考文献格式）
- 撰写 Data Availability Statement
- 撰写 CRediT Author Contribution Statement
- 撰写 AI Usage Declaration

### Cover Letter Prompt
```
请为以下论文撰写投稿 Cover Letter，目标期刊为 [期刊名]。

论文标题：[标题]
核心发现：[1-2 句话总结]

Cover Letter 要求：
- 简要说明论文的核心贡献和创新点
- 解释为什么适合该期刊
- 声明 AI 的使用方式
- 提议 3-5 位潜在审稿人（需人工确认真实性）
- 语气专业但不过分谦卑
```

### 产出
- `manuscript/submitted/` 下的最终版论文
- Cover Letter
- 投稿截图或确认记录

---

## AI 交互日志格式

每次关键 AI 交互记录在 `logs/` 目录，文件名格式：`YYYY-MM-DD_D#_task.md`

```markdown
# AI Interaction Log

- Date: 2026-06-04
- Stage: D1
- Model: Claude Opus 4
- Task: Generate SSH wavenumber spectrum analysis code

## Prompt Summary
[简述给 AI 的指令]

## Key Output
[AI 输出的关键结果摘要]

## Human Assessment
[人类对 AI 输出质量的简要评价：哪些可用、哪些需要修改]
```
