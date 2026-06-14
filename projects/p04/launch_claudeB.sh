#!/usr/bin/env bash
# launch_claudeB.sh — 启动/恢复 ClaudeB (reviewer) session
# 由 dual-ai-paper skill 生成，放在项目根目录
# ClaudeB 由 ClaudeA 在 v0.1 commit 后自动启动（新终端窗口）
# 也可手动运行以恢复中断的 B session

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

for f in CLAUDEB_GUIDE.md HANDOFF_PROTOCOL.md DIRECTION.md refs/notes.md; do
    if [ ! -f "$f" ]; then
        echo "ERROR: $f not found in $PROJECT_DIR" >&2
        exit 1
    fi
done

# 设置终端标题，供 post-commit hook 识别
echo -ne "\033]0;ClaudeB\007"

echo "=== Launching ClaudeB (reviewer) in: $PROJECT_DIR ==="
echo "=== 事件驱动模式：ClaudeA commit 后会通过 git hook 即时通知本终端 ==="

SYSPROMPT_FILE="$PROJECT_DIR/.claudeB_system.tmp"
cat > "$SYSPROMPT_FILE" <<SYSPROMPT
你是 ClaudeB — 审查者 / reviewer。你不是 ClaudeA，你不写论文，你只审查。
严格遵守 CLAUDEB_GUIDE.md 的所有规则（§4 审查维度、§5 反馈格式、§6 审查流程）。
本项目：波浪-海冰正反馈加速南极海冰损失
目标期刊：Nature Communications
核心方法：ERA5 fetch-SWH-MIZ 反馈诊断 + Pettitt突变检测
禁止：不改 README、不改 DIALOGUE.md 既往节、不 push remote、不 --amend、不 git add -A。
SYSPROMPT

PROMPT=$(cat <<'CLAUDEB_PROMPT'
读 CLAUDEB_GUIDE.md、DIRECTION.md、refs/notes.md、notes/paper_direction.md、notes/prior_work.md，然后检查 git log --oneline -5 看是否有待审查的 claudea: commit。若有，立即按 CLAUDEB_GUIDE.md §6 流程审查。

## 启动后自动执行（不等用户指示）
1. 启动 Monitor 持续监控 ClaudeA 的 commit（后台运行，不阻塞）
2. 检查是否有待审的 claudea: commit，有则立即审查
3. 审查完一轮后继续做辅助工作（代码预审、文献深读、gap 更新），绝不自动退出
4. Monitor 检测到新 commit 时立即进入下一轮审查
CLAUDEB_PROMPT
)

exec claude --name "ClaudeB-reviewer" \
    --dangerously-skip-permissions \
    --append-system-prompt-file "$SYSPROMPT_FILE" \
    "$PROMPT"
