description: 从 Build 阶段开始自动继续后续链路
---
先运行 `python scripts/get-vibeflow-phase.py --project-root . --json` 确认当前阶段。

如果当前阶段属于：
- `build-init`
- `build-config`
- `build-work`
- `review`
- `test-system`
- `test-qa`
- `ship`
- `reflect`

则不要逐段停下来等待用户确认，而是按 `skills/vibeflow-router/SKILL.md` 的“Build 后自动继续规则”继续推进，直到：
- `done`
- 阻塞
- 需要人工确认

只有在用户明确要求调试单个阶段时，才单独调用 `vibeflow-build-init`、`vibeflow-build-work`、`vibeflow-review` 或 `vibeflow-test-system`。
