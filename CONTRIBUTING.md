# Contributing Guide / 参与指南

欢迎加入 OpenSCI-Ocean！本文档帮助你快速上手参与项目。

## 快速开始

### 1. Fork 与 Clone

```bash
# Fork 本仓库到你的 GitHub 账号（在 GitHub 页面点击 Fork 按钮）
# 然后 clone 你的 fork
git clone https://github.com/YOUR_USERNAME/OpenSCI-Ocean.git
cd OpenSCI-Ocean
git remote add upstream https://github.com/pangeo-data/OpenSCI-Ocean.git
```

### 2. 选择项目

浏览 [projects/DASHBOARD.md](projects/DASHBOARD.md) 了解当前所有项目的状态。

- 在感兴趣的项目 Issue 下留言表达参与意向
- 或直接提一个新的 Issue 提出你的研究想法

### 3. 创建分支

```bash
# 同步最新代码
git fetch upstream
git merge upstream/main

# 为你的工作创建分支
git checkout -b p01/feature/your-work-description
```

分支命名规范：`p##/feature/描述` 或 `p##/d#-stage-description`

### 4. 提交工作

```bash
# 添加你的修改
git add projects/p01/analysis/your_script.py
git add projects/p01/figures/fig01_spectrum.png

# 提交（遵循 commit message 规范）
git commit -m "[P01] D1: add SSH wavenumber spectrum analysis script"

# 推送到你的 fork
git push origin p01/feature/your-work-description
```

### 5. 提交 PR

在 GitHub 上从你的分支向 upstream/main 发起 Pull Request，按照 PR 模板填写描述。

## Commit Message 规范

格式：`[P##] D#: 简要描述`

```
[P01] D0: literature review on SWOT SSH validation
[P03] D1: AI-generated first draft with 4 figures
[P05] D2: fix spectral slope calculation, add physical interpretation
[P07] D3: address internal review comments
```

- `P##`：项目编号（P01–P10）
- `D#`：当前阶段（D0–D4）
- 描述用英文，简洁说明做了什么

## 文件组织

每个项目目录是自包含的：

```
projects/p01/
├── README.md              # 项目卡片（必须先填写）
├── literature/            # 文献笔记和调研材料
├── analysis/              # 分析脚本 + 数据源链接文件
│   ├── download_data.py   # 数据下载脚本
│   ├── data_sources.md    # 数据链接清单
│   └── *.py / *.ipynb     # 分析代码
├── figures/               # 所有图表
├── manuscript/
│   ├── v1_ai_draft/       # AI 初稿
│   ├── v2_delivery/       # 人类审查稿
│   ├── v3_final/          # 定稿
│   └── submitted/         # 投稿版 + Cover Letter
└── logs/                  # AI 交互日志
```

## 几个关键规则

1. **不上传原始数据**：只提交数据链接和下载脚本
2. **不编造文献**：AI 生成的每条引用必须经人工核验
3. **写清环境依赖**：脚本开头注明依赖库，或提供 requirements.txt
4. **图表可复现**：图表必须有对应的生成脚本

## 需要帮助？

- 在 GitHub Issue 中提问，标题格式：`[Help] 你的问题`
- 微信工作群内随时沟通

*详细的协作制度、署名规则和审查流程见 [COLLABORATION.md](COLLABORATION.md)*
