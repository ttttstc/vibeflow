# VibeFlow Pre-Build Workflow Refactor

**Date:** 2026-04-04  
**Status:** Draft  
**Scope:** 将前置主链从 `spark -> requirements -> design` 重构为 `spark -> design -> tasks`，并使 `tasks` 成为独立的执行级 handoff 阶段。  
**Positioning:** 这是一份 workflow / artifact / router 重构方案，不是 another runtime 设计。

## 1. 目标

将当前前置主链重构为更短、更清晰、职责更单一的三段：

- `spark`：想清楚做什么
- `design`：设计具体实现
- `tasks`：把设计翻译成可执行任务

然后进入既有实施链：

- `build-init`
- `build-config`
- `build-work`
- `review`
- `test-system`
- `test-qa`
- `ship`
- `reflect`

## 2. 背景与判断

当前仓库前置链路存在三个问题：

1. `requirements` 与 `spark`、`design` 存在职责重叠
2. `tasks.md` 已经越来越重要，但仍挂在 `design` 的尾部，未成为正式 phase
3. 语义层仍有历史残留：部分配置、文档、兼容层仍保留 `think / plan`

结合前期讨论与 `Superpowers` 的 `writing-plans` 方法，这轮重构的核心判断是：

- `requirements` 作为独立 phase 的收益已经变低
- `spark` 应吸收“做什么、不做什么、验收标准、约束和假设”
- `design` 应只负责“怎么实现”
- `tasks` 应成为独立 phase，承担执行级 planning

## 3. 设计原则

本方案遵守根目录 [vision.md](../../../vision.md)：

- 只把 100% 可机械化的东西写成脚本
- 只把必须稳定复现的东西固化成状态机
- 只把经常忘、忘了就出事的东西做成 gate
- 其他尽量留给 agent runtime + skills + 项目产物

因此：

- `tasks` 是一个 artifact-driven handoff phase
- `tasks` 不是新的通用 planner runtime
- `build-init` 只做 gate 和初始化，不负责现场脑补任务
- `build-work` 只消费已批准的 `tasks.md`

## 4. 目标流程

### 4.1 新主链

```text
increment
-> spark
-> design
-> tasks
-> build-init
-> build-config
-> build-work
-> review
-> test-system
-> test-qa
-> ship
-> reflect
-> done
```

### 4.2 Quick Mode

Quick Mode 仍保留，但其语义需要与新主链对齐：

- Full Mode 的最早前置链为 `spark -> design -> tasks`
- Quick Mode 在 scope 足够小且风险足够低时，可跳过完整前置探索
- 一旦 Quick Mode 升级回 Full Mode，回退目标应为最早缺失的：
  - `spark`
  - 或 `design`
  - 或 `tasks`

不再出现“回退到 requirements”。

## 5. 各阶段职责

### 5.1 `spark`

**职责：** 想清楚做什么。

**必须回答：**

- 为什么做
- 做什么
- 明确不做什么
- 验收标准是什么
- 约束和假设是什么
- 尚未解决的问题是什么

**主要产物：**

- `docs/changes/<change-id>/context.md`

**说明：**

- `spark` 吸收原 `requirements` 的“行为边界契约”职责
- `spark` 不负责技术实现细节

### 5.2 `design`

**职责：** 设计具体实现。

**必须回答：**

- 架构如何接入现有系统
- 模块怎么拆
- 数据/接口/状态如何组织
- 如何验证设计是否被正确实现
- 哪些规则和约束必须贯穿实现

**主要产物：**

- `docs/changes/<change-id>/design.md`
- `docs/changes/<change-id>/design-review.md`

**说明：**

- `design` 只负责 how，不再重复写需求边界
- `Build Contract` 与 `Implementation Contract` 继续保留

### 5.3 `tasks`

**职责：** 将设计翻译成可执行任务。

**位置：**

- `design` 之后
- `build-init` 之前

**主要产物：**

- `docs/changes/<change-id>/tasks.md`

**角色边界：**

- `spark` 负责 what
- `design` 负责 how
- `tasks` 负责 exactly how to execute

**`tasks.md` 的最低字段：**

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

**任务质量要求：**

- 每个 task 只覆盖一个明确动作
- 默认 2-5 分钟粒度
- 超过 10 分钟必须拆分
- `exact_file_paths` 必须是仓库内精确路径
- `verification_steps` 必须是可执行验证
- `rollback_note` 必须说明最小撤销路径

**说明：**

- `tasks` 对齐 `Superpowers` 的 `writing-plans`
- 但在 VibeFlow 中它是独立 phase，而不是 design 的附属注脚

## 6. Artifact 模型变更

### 6.1 保留

- `docs/changes/<change-id>/context.md`
- `docs/changes/<change-id>/design.md`
- `docs/changes/<change-id>/design-review.md`
- `docs/changes/<change-id>/tasks.md`
- `feature-list.json`
- `docs/changes/<change-id>/verification/*`
- `RELEASE_NOTES.md`

### 6.2 退场

从主流程中退场：

- `docs/changes/<change-id>/requirements.md`

### 6.3 兼容策略

短期兼容读取但不再作为主写入路径：

- `requirements.md`
- 旧版 `proposal.md`
- 旧版 `think / plan` artifacts

兼容层原则：

- 可以读取
- 可以迁移
- 不再作为新项目默认产物

## 7. Router / State / Policy 变更

### 7.1 Phase 列表

正式 phase 变更为：

- `increment`
- `quick`
- `spark`
- `design`
- `tasks`
- `build-init`
- `build-config`
- `build-work`
- `review`
- `test-system`
- `test-qa`
- `ship`
- `reflect`
- `done`

移除：

- `requirements`

### 7.2 `.vibeflow/state.json`

需要变更：

- `current_phase` 不再出现 `requirements`
- `checkpoints.requirements` 删除
- 新增 `checkpoints.tasks`

### 7.3 `.vibeflow/policy.yaml`

需要变更：

- 删除 `requirements`
- 新增 `tasks`

目标结构：

```yaml
phases:
  spark:
    required_artifacts: ["spark"]
  design:
    required_artifacts: ["design", "design_review"]
  tasks:
    required_artifacts: ["tasks"]
```

### 7.4 `get-vibeflow-phase.py`

需要变更：

- `spark` 完成后，直接进入 `design`
- `design` 完成但 `tasks.md` 缺失时，返回 `tasks`
- `build-init` readiness 之前必须存在 `tasks.md`

### 7.5 `validate_phase_invariants.py`

需要变更：

- 删除 `requirements` 的 invariant
- 新增 `tasks` invariant
- `build-init` 的 completion evidence 必须包含 `artifact:tasks`

## 8. Skill 变更

### 8.1 `vibeflow-spark`

需要增强：

- 输出升级版 `context.md`
- 明确包含：
  - scope
  - non-goals
  - acceptance criteria
  - constraints
  - assumptions
  - open questions

### 8.2 `vibeflow-requirements`

建议处理方式：

- 从主链退役
- 保留为兼容或 legacy migration skill
- 不再作为 router 主路径的一部分

### 8.3 `vibeflow-design`

需要调整：

- 输入改为 `context.md` + 可选 `ucd.md` + `rules/`
- 不再要求 `requirements.md` 作为正式前置条件
- 输出 `design.md` + `design-review.md`
- 不再把 `tasks.md` 视为 design 阶段附属产物

### 8.4 新增 `vibeflow-tasks`

新增独立 skill：

- 名称：`vibeflow-tasks`
- phase：`tasks`

职责：

- 读取 `context.md`
- 读取 `design.md`
- 读取 `design-review.md`
- 读取 `rules/`
- 读取 `ucd.md`（如存在）
- 生成执行级 `tasks.md`

### 8.5 `vibeflow-build-init`

需要调整：

- 增加 `tasks` gate
- 缺少 `tasks.md` 时阻塞
- `tasks.md` 字段不全、粒度过粗时阻塞

### 8.6 `vibeflow-build-work`

需要调整：

- 明确只消费已批准的 `tasks.md`
- 不再现场重写执行计划
- 当任务缺失或过粗时回退到 `tasks` phase

## 9. Workflow Template 变更

当前模板仍残留 `think / plan` 配置语义，需要一起收口。

### 9.1 目标 schema

将模板从：

```yaml
think:
plan:
```

重构为：

```yaml
spark:
design:
tasks:
```

### 9.2 设计原则

- `spark`：探索深度与价值评估策略
- `design`：是否需要 UCD / design review / eng review
- `tasks`：任务粒度、强制字段、gate 严格度

## 10. 脚本改动清单

预计需要修改：

- `scripts/get-vibeflow-phase.py`
- `scripts/validate_phase_invariants.py`
- `scripts/vibeflow_paths.py`
- `scripts/vibeflow_automation.py`
- `scripts/increment-handler.py`
- `scripts/new-vibeflow-config.py`
- `scripts/new-vibeflow-work-config.py`
- `scripts/vibeflow_overview.py`
- `scripts/vibeflow_dashboard.py`
- `scripts/migrate-vibeflow-v2.py`

预计需要新增：

- `skills/vibeflow-tasks/SKILL.md`
- `docs/templates/tasks-template.md`（如尚未存在）
- `scripts/validate_execution_plan.py`（如果执行级 gate 继续独立实现）

## 11. 测试与验证

必须覆盖的测试面：

- phase detection：`spark -> design -> tasks -> build-init`
- policy invariant：`tasks` 缺失时阻塞 build-init
- quick promote：回退目标不再出现 `requirements`
- sample project：state / workflow / overview 一致
- dashboard：workflow card 不再出现 `requirements`
- migration：旧项目可从 `think / plan / requirements` 迁移到新模型

建议新增或更新：

- `tests/test_detect_phase.py`
- `tests/test_vibeflow_v2.py`
- `tests/test_vibeflow_dashboard.py`
- `tests/test_vibeflow_e2e_modes.py`
- `tests/test_vibeflow_autopilot.py`

## 12. 迁移策略

### 12.1 新项目

直接使用新链路：

- `spark`
- `design`
- `tasks`

### 12.2 旧项目

兼容规则：

- 若存在 `requirements.md`，允许 design 继续读取
- 若缺少 `tasks.md`，router 返回 `tasks`
- migration 脚本可将旧 `requirements` 内容并入 `context.md` 或保留为 legacy archive

### 12.3 文档迁移

需要同步更新：

- `README.md`
- `README_EN.md`
- `USAGE.md`
- `ARCHITECTURE.md`
- `VIBEFLOW-DESIGN.md`
- sample project overview

## 13. 非目标

本轮不做：

- 重造通用 planner
- 重造通用 multi-agent runtime
- 自动根据对话直接生成完整计划并绕过 `design`
- 在 `build-work` 里隐式补写任务

## 14. 分期建议

### Wave 1

- phase model 重构
- policy / state / router 收口
- `requirements` 从主链移除

### Wave 2

- 新增 `vibeflow-tasks`
- `tasks.md` 执行级 schema 和 gate
- `build-init` / `build-work` 对接

### Wave 3

- workflow template schema 收口
- sample project / overview / dashboard 刷新
- migration 和兼容层整理

## 15. 最终判断

这轮重构的本质不是“少一个文档”，而是把前置主链收敛成更清晰的三问：

- `spark`：做什么
- `design`：怎么做
- `tasks`：怎么按稳定顺序执行

这比当前 `spark -> requirements -> design` 更接近：

- VibeFlow 的 control plane 定位
- `Superpowers` 的 `writing-plans` 思路
- 以及后续 build gate / execution planning 的自然衔接
