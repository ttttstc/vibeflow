---
name: vibeflow-tasks
description: "Tasks 阶段 — 基于 spark brief 与 design 产出 execution-grade tasks.md，作为 Build 的正式交接输入。"
---

# VibeFlow Tasks

`tasks` 阶段位于 `design` 之后、`build` 之前。

它回答的不是“做什么”，而是“**具体按什么顺序执行**”。

## 输入

- `docs/changes/<change-id>/brief.md`
- `docs/changes/<change-id>/design.md`
- `docs/changes/<change-id>/ucd.md`（如存在）
- `rules/`（如存在）
- `docs/templates/tasks-template.md`

## 输出

- `docs/changes/<change-id>/tasks.md`

## 硬要求

每个任务块都必须包含：

- `task_id`
- `feature_id`
- `goal`
- `exact_file_paths`
- `change_type`
- `depends_on`
- `steps`
- `verification_steps`
- `rollback_note`
- `expected_duration_min`

## 质量门

- 一个任务块只做一个明确动作
- 默认控制在 2-5 分钟粒度
- 超过 10 分钟必须拆分
- `exact_file_paths` 必须是仓库内精确路径
- `verification_steps` 必须是可执行验证
- `rollback_note` 必须说明最小撤销路径
- 每个任务块必须能追溯到 `feature_id`、`build_contract_ref`、`design_section` 中至少一个正式索引

## 生成流程

1. 运行 `python scripts/get-vibeflow-paths.py --json` 确认当前 change root
2. 读取 `brief.md`，提炼目标、范围、非目标、验收标准、约束
3. 读取 `design.md` 中的设计、评审结论与范围决策，提炼 feature、文件范围、依赖、验证策略
4. 如有 `rules/`，确保任务拆分不违背项目规则
5. 使用 `docs/templates/tasks-template.md` 生成 `tasks.md`
6. 保存后，等待进入 `build`

## 边界

- 不在这里重写设计
- 不在这里生成 `feature-list.json`
- 不在这里启动实现
- `tasks.md` 是 handoff plan，不是 another runtime

## 完成标准

- `tasks.md` 已生成
- 每个实现 feature 至少有一个任务块
- Build 可以直接把它当作 execution planning input 使用
