# VibeFlow Design

> Version: v1.5
> Date: 2026-04-04
> Status: Simplified surface aligned to `Spark -> Design -> Tasks -> Build -> Review -> Test -> Ship -> Reflect`

## Related Docs

- [README.md](README.md) - 项目介绍、安装和快速开始
- [USAGE.md](USAGE.md) - 实际使用说明和项目产物概览
- [ARCHITECTURE.md](ARCHITECTURE.md) - 状态机、路由和组件关系

## 1. Overview

VibeFlow is a repo-local control plane for AI delivery.

Its job is to keep the workflow legible, resumable, and artifact-driven without rebuilding the host agent runtime.

User-facing lifecycle:

1. Spark
2. Design
3. Tasks
4. Build
5. Review
6. Test
7. Ship
8. Reflect

## 2. Naming Rules

Use only these project-facing names:

- workflow state lives under `.vibeflow/`
- change artifacts live under `docs/changes/`
- long-lived project docs live under `docs/overview/`
- execution truth lives in `feature-list.json`

Do not expose internal subphases such as old build/test micro-steps as separate product phases.

## 3. File Layout

```text
skills/
  vibeflow/
  vibeflow-router/
  vibeflow-spark/
  vibeflow-office-hours/
  vibeflow-plan-value-review/
  vibeflow-plan-eng-review/
  vibeflow-plan-design-review/
  vibeflow-design/
  vibeflow-tasks/
  vibeflow-brainstorming/
  vibeflow-build-init/
  vibeflow-build-work/
  vibeflow-tdd/
  vibeflow-quality/
  vibeflow-feature-st/
  vibeflow-spec-review/
  vibeflow-review/
  vibeflow-test-system/
  vibeflow-test-qa/
  vibeflow-ship/
  vibeflow-reflect/

hooks/
  hooks.json
  session-start.ps1
  session-start.sh

scripts/
  get-vibeflow-phase.py
  get-vibeflow-paths.py
  vibeflow_paths.py
  increment-handler.py
  migrate-vibeflow-v2.py
  promote-vibeflow-quick.py
  new-vibeflow-config.py
  test-vibeflow-setup.py
  run-vibeflow-autopilot.py
  run-vibeflow-dashboard.py

templates/
  prototype.yaml
  web-standard.yaml
  api-standard.yaml
  enterprise.yaml
```

## 4. Router State Machine

Routing is file-driven through `scripts/get-vibeflow-phase.py`.

Detected phases:

- `increment`
- `quick`
- `spark`
- `design`
- `tasks`
- `build`
- `review`
- `test`
- `ship`
- `reflect`
- `done`

## 5. Runtime Artifacts

### 5.1 VibeFlow State

- `.vibeflow/state.json` — workflow state, current phase, checkpoints, active change, phase history, runtime resume hints
- `.vibeflow/workflow.yaml` — workflow policy and template-derived behavior
- `.vibeflow/guides/build.md` — build session guide
- `.vibeflow/guides/services.md` — service lifecycle guide when services apply
- `.vibeflow/logs/session-log.md` — progress log, generated on first write
- `.vibeflow/logs/retro-YYYY-MM-DD.md` — iteration retrospective
- `.vibeflow/increments/queue.json` — pending increments queue
- `.vibeflow/increments/requests/*.json` — increment request payloads
- `.vibeflow/increments/history.json` — increment processing history

### 5.2 Project Artifacts

- `docs/overview/PROJECT.md` — long-lived project context
- `docs/overview/ARCHITECTURE.md` — long-lived project architecture
- `docs/overview/CURRENT-STATE.md` — current workflow snapshot
- `docs/changes/<change-id>/brief.md` — Spark artifact with goal, scope, constraints, and acceptance
- `docs/changes/<change-id>/ucd.md` — optional UI design artifact
- `docs/changes/<change-id>/design.md` — technical design plus review summary and scope decision
- `docs/changes/<change-id>/tasks.md` — execution-grade handoff
- `docs/changes/<change-id>/verification/review.md` — global review report
- `docs/changes/<change-id>/verification/system-test.md` — system test report
- `docs/changes/<change-id>/verification/qa.md` — QA report when UI applies
- `docs/test-cases/feature-*.md` — feature test case documents
- `feature-list.json` — Build truth source
- `RELEASE_NOTES.md` — release notes

## 6. Templates

The project includes four static templates:

- `prototype`
- `web-standard`
- `api-standard`
- `enterprise`

Template selection writes `.vibeflow/workflow.yaml`.

There is no separate user-facing build-config file anymore; execution behavior is read from `workflow.yaml` and current state.

## 7. Skill Catalog

### 7.1 Core Layer

- `vibeflow` — framework entry point
- `vibeflow-router` — session router and phase dispatch
- `vibeflow-spark` — Spark phase

### 7.2 Exploratory Layer

- `vibeflow-office-hours` — optional pre-Spark brainstorming
- `vibeflow-brainstorming` — optional pre-Design exploration

### 7.3 Definition Layer

- `vibeflow-plan-value-review` — value review
- `vibeflow-plan-eng-review` — engineering review
- `vibeflow-plan-design-review` — design review
- `vibeflow-design` — technical design and inlined review summary
- `vibeflow-tasks` — execution-grade planning handoff

### 7.4 Build Layer

- `vibeflow-build-init` — internal Build preparation step
- `vibeflow-build-work` — internal Build execution step
- `vibeflow-tdd` — TDD cycle
- `vibeflow-quality` — quality gates
- `vibeflow-feature-st` — feature acceptance testing
- `vibeflow-spec-review` — spec compliance review

### 7.5 Verification and Release Layer

- `vibeflow-review` — holistic review
- `vibeflow-test-system` — system tests
- `vibeflow-test-qa` — browser QA
- `vibeflow-ship` — release and changelog
- `vibeflow-reflect` — retrospective

## 8. Internal vs External Mapping

This table is the canonical translation layer between product-facing names and internal implementation names.

### 8.1 Phase Mapping

| 对外产品名 | 内部检测相位 / 技能 / 脚本 | 说明 |
|---|---|---|
| `Spark` | `spark` / `vibeflow-spark` | 产出 `brief.md` |
| `Design` | `design` / `vibeflow-design` | 产出 `design.md`，内含评审结论 |
| `Tasks` | `tasks` / `vibeflow-tasks` | 产出 execution-grade `tasks.md` |
| `Build` | `build` / `vibeflow-build-init` + `vibeflow-build-work` | 对外一个阶段，对内包含准备和执行两个子步骤 |
| `Review` | `review` / `vibeflow-review` | 产出全局审查报告 |
| `Test` | `test` / `vibeflow-test-system` + `vibeflow-test-qa` | 对外一个阶段，对内按是否需要 UI QA 决定是否追加浏览器验证 |
| `Ship` | `ship` / `vibeflow-ship` | 产出 `RELEASE_NOTES.md` |
| `Reflect` | `reflect` / `vibeflow-reflect` | 产出复盘 |

### 8.2 Artifact Mapping

| 对外产物 | 内部实现细节 | 说明 |
|---|---|---|
| `brief.md` | Spark artifact | 取代过去更模糊的 `context.md` 叙事 |
| `design.md` | design + review summary | 不再单独暴露 `design-review.md` |
| `tasks.md` | execution planning handoff | Build 的正式输入 |
| `verification/` | `review.md` + `system-test.md` + `qa.md` | 对外按目录理解，对内仍保留分文件 |
| `.vibeflow/state.json` | state + runtime resume hints | 不再单独暴露 `runtime.json` |
| `.vibeflow/workflow.yaml` | workflow policy | 不再单独暴露 `work-config.json` |

### 8.3 User-Facing vs Internal Files

| 应该直接面向用户 | 主要供系统内部使用 |
|---|---|
| `docs/overview/CURRENT-STATE.md` | `.vibeflow/state.json` |
| `docs/overview/PROJECT.md` | `.vibeflow/workflow.yaml` |
| `docs/overview/ARCHITECTURE.md` | `.vibeflow/guides/build.md` |
| `docs/changes/<change-id>/brief.md` | `.vibeflow/guides/services.md` |
| `docs/changes/<change-id>/design.md` | `.vibeflow/logs/session-log.md` |
| `docs/changes/<change-id>/tasks.md` | `.vibeflow/increments/*` |
| `docs/changes/<change-id>/verification/` | `.vibeflow/build-reports/*` |
| `feature-list.json` |  |

### 8.4 Recovery Surface Mapping

| 用户看到的恢复提示 | 内部来源 |
|---|---|
| 当前停在什么阶段 | `get-vibeflow-phase.py` 输出的 `phase` |
| 为什么停在这里 | `reason` |
| 现在应该做什么 | `next_action` |
| 建议先打开哪些文件 | `open_files` |
| 是否会自动继续 | `resume_mode` |

## 9. Human-Facing Document Surface

Users normally need only these documents:

- `docs/overview/CURRENT-STATE.md`
- `docs/overview/PROJECT.md`
- `docs/overview/ARCHITECTURE.md`
- `docs/changes/<change-id>/brief.md`
- `docs/changes/<change-id>/design.md`
- `docs/changes/<change-id>/tasks.md`
- `docs/changes/<change-id>/verification/`
- `feature-list.json`

Everything else in `.vibeflow/` should be treated as internal control-plane state.

## 10. Recovery Behavior

When Claude closes unexpectedly, rerunning `/vibeflow` should restore context from `.vibeflow/state.json`.

The resume surface must explicitly tell the user:

- current phase
- why the workflow is paused
- what to do next
- which files to open

## 11. Design Constraints

- Spark owns the problem brief
- Design owns the technical solution and review summary
- Tasks owns the execution-grade handoff
- Build owns feature execution state
- Review and Test own verification evidence

VibeFlow should remain a control plane:

- scripts only automate deterministic work
- state machines only encode stable transitions
- gates only cover things that are easy to forget and expensive to miss
- everything else stays with the agent runtime, skill prompts, and repo artifacts

## 12. Verification

Use these commands locally:

```powershell
python scripts/get-vibeflow-phase.py
python scripts/get-vibeflow-phase.py --verbose
python scripts/test-vibeflow-setup.py --json
python scripts/run_vibeflow_repo_tests.py
```
