---
name: vibeflow-freeze
version: 1.0.0
description: |
  VibeFlow file edit boundary. Restricts Edit and Write operations to a specific
  directory for the session. Blocks edits outside the allowed path.
  Use when debugging to prevent accidentally "fixing" unrelated code,
  or when you want to scope changes to one module.
  Use when asked to "freeze", "restrict edits", "only edit this folder",
  "lock down edits", or "/vibeflow-freeze".
  **This skill is optional and defaults to OFF.** Activate it explicitly when needed.
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
hooks:
  PreToolUse:
    - matcher: "Edit"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/bin/check-freeze.sh"
          statusMessage: "Checking freeze boundary..."
    - matcher: "Write"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/bin/check-freeze.sh"
          statusMessage: "Checking freeze boundary..."
---

# /vibeflow-freeze — Restrict Edits to a Directory

Lock file edits to a specific directory. Any Edit or Write operation targeting
a file outside the allowed path will be **blocked** (not just warned).

**Note:** This skill requires hook script support. Ensure the hook script
`bin/check-freeze.sh` is executable and properly installed. The freeze boundary
is stored in `~/.vibeflow/freeze-dir.txt`.

## Setup

Ask the user which directory to restrict edits to. Use AskUserQuestion:

- Question: "Which directory should I restrict edits to? Files outside this path will be blocked from editing."
- Text input (not multiple choice) — the user types a path.

Once the user provides a directory path:

1. Resolve it to an absolute path:
```bash
FREEZE_DIR=$(cd "<user-provided-path>" 2>/dev/null && pwd)
echo "$FREEZE_DIR"
```

2. Ensure trailing slash and save to the freeze state file:
```bash
FREEZE_DIR="${FREEZE_DIR%/}/"
STATE_DIR="${VIBEFLOW_STATE_DIR:-${HOME}/.vibeflow}"
mkdir -p "$STATE_DIR"
echo "$FREEZE_DIR" > "$STATE_DIR/freeze-dir.txt"
echo "Freeze boundary set: $FREEZE_DIR"
```

Tell the user: "Edits are now restricted to `<path>/`. Any Edit or Write
outside this directory will be blocked. To change the boundary, run `/vibeflow-freeze`
again. To remove it, run `/vibeflow-unfreeze` or end the session."

## How it works

The hook reads `file_path` from the Edit/Write tool input JSON, then checks
whether the path starts with the freeze directory. If not, it returns
`permissionDecision: "deny"` to block the operation.

The freeze boundary persists for the session via the state file. The hook
script reads it on every Edit/Write invocation.

## Notes

- The trailing `/` on the freeze directory prevents `/src` from matching `/src-old`
- Freeze applies to Edit and Write tools only — Read, Bash, Glob, Grep are unaffected
- This prevents accidental edits, not a security boundary — Bash commands like `sed` can still modify files outside the boundary
- To deactivate, run `/vibeflow-unfreeze` or end the conversation

## Activation

To activate this skill, run:
```
Skill: vibeflow-freeze
```

## 集成

**调用者：** 用户在 review 阶段或其他需要文件边界保护的场景主动调用
**依赖：** `bin/check-freeze.sh` hook 脚本存在且可执行；`~/.vibeflow/freeze-dir.txt` 状态文件
**状态：** 默认关闭，需要用户显式激活
**链接到：** vibeflow-guard（组合模式）/ vibeflow-unfreeze（解除）
