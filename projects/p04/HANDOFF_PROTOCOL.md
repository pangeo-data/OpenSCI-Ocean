# 双 AI 握手协议（HANDOFF Protocol）

> 适用于 ClaudeA（执行）↔ ClaudeB（审查）的**事件驱动**协作。
> **核心原则**：以 git commit 为本轮交付的唯一标记。工作树中未 commit 的修改 = 草稿，不算交付。

---

## 1. 信号约定

每完成一轮工作，本方 commit。commit 即"我这轮交付完了"的信号。

| 角色 | commit message 前缀 | 含义 |
|---|---|---|
| ClaudeA | `claudea:` | A 完成本轮，等 B 审查 |
| ClaudeB | `claudeb:` | B 完成本轮，等 A 起新一轮 |

每个 commit 必须带 trailer：
- `Co-Authored-By: ClaudeA <claudea@local>` 或
- `Co-Authored-By: ClaudeB <claudeb@local>`

---

## 2. 通信机制（两层，按优先级）

A 与 B 共享同一本地 `.git/`，通过 commit 交接。**通知对方**有两层机制，按优先级递降：

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: post-commit hook（即时，零成本）                │
│  A commit → .git/hooks/post-commit → osascript 通知 B   │
│  前提：双方终端同时打开且标题含 ClaudeA/ClaudeB          │
├─────────────────────────────────────────────────────────┤
│  Layer 2: /loop 定时检查（用户在各 session 中启动）       │
│  /loop 200s → 每 ~200s 检查对方 git log                 │
│  前提：用户已在 A/B session 中分别输入 /loop 命令         │
│  用途：当 hook 失效时的自动检测                           │
└─────────────────────────────────────────────────────────┘
```

**启动对方会话**：A 首次 commit 后 osascript 打开新终端运行 `launch_claudeB.sh`（仅一次）。对方 session 中断后由用户手动运行 `./launch_claude{A,B}.sh` 恢复。

**禁止使用的机制**（会阻塞会话或丢失上下文）：
- ❌ `Monitor` 阻塞等待（挂起 session，无法做其他工作）
- ❌ `ScheduleWakeup`（让 session 休眠，丢失工作上下文）

### 2.1 各层何时生效

| 场景 | 生效层 | 说明 |
|---|---|---|
| 双方终端都打开，正常协作 | Layer 1 | hook 即时通知，最快 |
| 双方终端都开着但 hook 失效 | Layer 2 | `/loop` 200s 内检测到 |
| 对方 session 意外中断 | 用户恢复 | 用户手动 `./launch_claude{A,B}.sh` 恢复 |
| 用户从头开始新一轮协作 | 用户启动 | 直接运行 launch 脚本 |

### 2.2 `/loop` 检测逻辑

`/loop` 触发时执行以下检查（以 A 检查 B 为例，B 检查 A 同理）：

```bash
# A 检查 B：
git log --grep='^claudeb:' --oneline -5
# 若有未处理的新 commit → 读 DIALOGUE.md → 处理 Block/Concern → bump version → commit
# 若无新 commit → 继续当前工作
```

---

## 3. 每轮的标准对话流

### A 的轮：

1. 读 DIALOGUE.md 最新 R0N 节（B 的反馈）
2. 改 README + 写 CHANGELOG
3. 在 DIALOGUE.md 末尾追加 A0N 节（含 Block 处理表 + Q-back 答复 + Changes vs README v(X-1)）
4. commit `claudea: A0N + bump v0.X`

### B 的轮：

1. 读 DIALOGUE.md 最新 A0N 节（A 的答复）
2. `git diff <prev_review_commit> HEAD -- README.md` 看 README 增量
3. 走 §10.1 流程（CLAUDEB_GUIDE.md §6）
4. 在 DIALOGUE.md 末尾追加 R0(N+1) 节
5. commit `claudeb: R0(N+1) review of README v0.X`

---

## 4. 终止条件

- B 的某轮含 `Approve as-is` → loop 终止
- 完成 round == 20 → loop 终止（用户介入裁定）
- 用户裁定停止

---

## 5. 失败模式与缓解

| 风险 | 缓解 |
|---|---|
| A 写完忘了 commit | B 跳过；用户口头催 A commit |
| commit 前缀写错 | 该 commit 不被识别为交付；下次 commit 修正 |
| A 一轮内多次 commit | B 以最新 `claudea:` commit 为准 |
| 同时编辑 race | 协议保证只有一方"working"，理论上不冲突；冲突由用户裁定 |

---

## 6. Git 管理规则（双方都遵守）

### 6.1 git 是唯一信道

A 与 B 之间不通过任何其他方式通信（不写 IPC、不发邮件、不 chat）——所有协作都通过：

- **commit**（含 message + diff + `Co-Authored-By` trailer）
- **文件改动**（README.md / DIALOGUE.md / refs/ ...）

这是机制独立性的保证。**不要绕过 git 信道直接和对方沟通**。

### 6.2 分支策略

- 单一 `main` 分支，无 feature branch；
- 不创建 PR 流程——这是 ad-hoc 双 AI 协作，不是开源项目；
- 不需要 rebase / merge / cherry-pick（除非用户介入裁定 race）。

### 6.3 远程推送

- **默认不 push remote**——除非用户明确指示；
- 用户可手动 `git push origin main` 备份到 GitHub / GitLab，机制不依赖远程；
- A 与 B 共享同一本地 `.git/`（同一仓库 / 同一 worktree），不通过 remote 同步。

### 6.4 禁止重写历史

| 禁 | 替代 |
|---|---|
| `git commit --amend` | 起一个 `claude{a,b}: fix ...` 新 commit |
| `git reset --hard` | 用 revert 或新 commit 修正 |
| `git push --force` / `--force-with-lease` | 不 push 即可；如要 push，问用户 |
| `--no-verify` / `--no-gpg-sign` | 调查 hook 失败原因，修复后正常 commit |
| `git rebase -i` 已 push 的 commit | 不重写已 push 历史 |

修正错误用**新的 commit**，message 清晰描述纠正了什么。

### 6.5 .gitignore（setup wizard 已就位）

```
.DS_Store
__pycache__/  *.pyc
.venv/  venv/
.claude/                  # Claude Code session state
data/                     # 大型 NetCDF / CSV
runs/output/              # 模式 / 实验输出
*.log
.vscode/  .idea/
```

**PDF 文献是否进 git** 由用户决定：

- 进 git：`refs/*.pdf` 通常 1–10 MB / 篇，3 篇约 ≤30 MB，可接受；
- 不进 git：在 `.gitignore` 加 `refs/*.pdf`，仍 track `refs/notes.md` / `refs/auto_candidates.md` / `refs/refXX_summary.md`。

### 6.6 冲突处理（race 情况）

A 与 B 理论上不会同时提交（commit-based handshake 隔离）。如发生：

1. 两方都 commit 且改了同一文件 → 后到方 `git status` 看到 unstaged conflict；
2. **不要自动 merge** —— 写一个 `claude{a,b}: rebase needed, awaiting user` commit，把决断权交给用户；
3. 用户裁定后，由后到方做 rebase + 干净 commit。

### 6.7 commit message 规范

```
claude{a,b}: <短标题，<70 char>

<可选正文：处理了什么 / 为什么>

Co-Authored-By: Claude{A,B} <claude{a,b}@local>
```

正文不强制，但**复杂改动 / scope shift 时**应写 1–3 行说明。

### 6.8 git log 阅读规则（每轮开始）

```bash
git log --oneline -10           # 看最近 10 条
git log --grep='^claudea:' -1   # 找 A 最新交付
git log --grep='^claudeb:' -1   # 找 B 最新交付
git show <hash>                 # 看 commit 实际改了什么
git diff <h1> <h2> -- README.md # 看 README 增量
```

不要假定 commit message 描述准确——必查 `git show` 实际 diff。
