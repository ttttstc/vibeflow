---
name: vibeflow-careful
version: 1.0.0
description: |
  VibeFlow safety guardrails for destructive commands. Warns before rm -rf, DROP TABLE,
  force-push, git reset --hard, kubectl delete, and similar destructive operations.
  User can override each warning. Use when touching prod, debugging live systems,
  or working in a shared environment.
  Use when asked to "be careful", "safety mode", "prod mode", "careful mode",
  or "/vibeflow-careful".
  **This skill is optional and defaults to OFF.** Activate it explicitly when needed.
allowed-tools:
  - Bash
  - Read
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/bin/check-careful.sh"
          statusMessage: "Checking for destructive commands..."
---

# /vibeflow-careful — Destructive Command Guardrails

Safety mode is now **active**. Every bash command will be checked for destructive
patterns before running. If a destructive command is detected, you'll be warned
and can choose to proceed or cancel.

**Note:** This skill requires hook script support. Ensure the hook script
`bin/check-careful.sh` is executable and properly installed.

## What's protected

| Pattern | Example | Risk |
|---------|---------|------|
| `rm -rf` / `rm -r` / `rm --recursive` | `rm -rf /var/data` | Recursive delete |
| `DROP TABLE` / `DROP DATABASE` | `DROP TABLE users;` | Data loss |
| `TRUNCATE` | `TRUNCATE orders;` | Data loss |
| `git push --force` / `-f` | `git push -f origin main` | History rewrite |
| `git reset --hard` | `git reset --hard HEAD~3` | Uncommitted work loss |
| `git checkout .` / `git restore .` | `git checkout .` | Uncommitted work loss |
| `kubectl delete` | `kubectl delete pod` | Production impact |
| `docker rm -f` / `docker system prune` | `docker system prune -a` | Container/image loss |

## Safe exceptions

These patterns are allowed without warning:
- `rm -rf node_modules` / `.next` / `dist` / `__pycache__` / `.cache` / `build` / `.turbo` / `coverage`

## How it works

The hook reads the command from the tool input JSON, checks it against the
patterns above, and returns `permissionDecision: "ask"` with a warning message
if a match is found. You can always override the warning and proceed.

To deactivate, end the conversation or start a new one. Hooks are session-scoped.

## Activation

To activate this skill, run:
```
Skill: vibeflow-careful
```

## 集成

**调用者：** 用户在 review 阶段或其他需要安全护栏的场景主动调用
**依赖：** `bin/check-careful.sh` hook 脚本存在且可执行
**状态：** 默认关闭，需要用户显式激活
**链接到：** vibeflow-guard（组合模式）/ vibeflow-unfreeze（解除）
