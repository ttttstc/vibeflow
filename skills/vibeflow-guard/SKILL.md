---
name: vibeflow-guard
version: 1.0.0
description: |
  VibeFlow full safety mode: destructive command warnings + directory-scoped edits.
  Combines /vibeflow-careful (warns before rm -rf, DROP TABLE, force-push, etc.)
  with /vibeflow-freeze (blocks edits outside a specified directory).
  Use for maximum safety when touching prod or debugging live systems.
  Use when asked to "guard mode", "full safety", "lock it down",
  "maximum safety", or "/vibeflow-guard".
  **This skill is optional and defaults to OFF.** Activate it explicitly when needed.
allowed-tools:
  - Bash
  - Read
  - AskUserQuestion
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/../vibeflow-careful/bin/check-careful.sh"
          statusMessage: "Checking for destructive commands..."
    - matcher: "Edit"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/../vibeflow-freeze/bin/check-freeze.sh"
          statusMessage: "Checking freeze boundary..."
    - matcher: "Write"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/../vibeflow-freeze/bin/check-freeze.sh"
          statusMessage: "Checking freeze boundary..."
---

# /vibeflow-guard — Full Safety Mode

Activates both destructive command warnings and directory-scoped edit restrictions.
This is the combination of `/vibeflow-careful` + `/vibeflow-freeze` in a single command.

**Note:** This skill requires both `vibeflow-careful/bin/check-careful.sh` and
`vibeflow-freeze/bin/check-freeze.sh` hook scripts to be installed and executable.

## Setup

Ask the user which directory to restrict edits to. Use AskUserQuestion:

- Question: "Guard mode: which directory should edits be restricted to? Destructive command warnings are always on. Files outside the chosen path will be blocked from editing."
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

Tell the user:
- "**Guard mode active.** Two protections are now running:"
- "1. **Destructive command warnings** — rm -rf, DROP TABLE, force-push, etc. will warn before executing (you can override)"
- "2. **Edit boundary** — file edits restricted to `<path>/`. Edits outside this directory are blocked."
- "To remove the edit boundary, run `/vibeflow-unfreeze`. To deactivate everything, end the session."

## What's protected

See `/vibeflow-careful` for the full list of destructive command patterns and safe exceptions.
See `/vibeflow-freeze` for how edit boundary enforcement works.

## Activation

To activate this skill, run:
```
Skill: vibeflow-guard
```

## 集成

**调用者：** 用户在 review 阶段或其他需要最大安全保护的场景主动调用
**依赖：** `vibeflow-careful/bin/check-careful.sh` 和 `vibeflow-freeze/bin/check-freeze.sh` hook 脚本
**状态：** 默认关闭，需要用户显式激活
**链接到：** vibeflow-unfreeze（解除）
