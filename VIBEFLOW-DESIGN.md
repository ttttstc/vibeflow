# VibeFlow Design

> Version: v1.4
> Date: 2026-03-23
> Status: Full local workflow scaffold implemented + 7-phase architecture

## Overview

VibeFlow is a 7-phase workflow for iterative product delivery:

**决策阶段（Human）：**
1. Think
2. Plan
3. Requirements
4. Design

**执行阶段（Automated via Build Handoff）：**
5. Build
6. Review
7. Test

**可选阶段：**
- Ship（发布）
- Reflect（复盘）

The repository contains the complete local scaffold for all phases.
All project-facing names are unified under `vibeflow`.

## Naming Rules

Use only these project-facing names:

- skills live under `skills/`
- runtime state lives under `.vibeflow/`
- design contract is `VIBEFLOW-DESIGN.md`
- helper scripts live under `scripts/`
- templates live under `templates/`

## File Layout

```text
skills/
  vibeflow/
  vibeflow-router/
  vibeflow-think/
  vibeflow-office-hours/           # YC Office Hours (optional pre-Think)
  vibeflow-plan/
  vibeflow-plan-value-review/      # CEO value review
  vibeflow-plan-eng-review/        # Engineering review (Design phase Step 5.1)
  vibeflow-plan-design-review/     # Design review (Design phase Step 5.2)
  vibeflow-requirements/
  vibeflow-design/                 # Tech design (UCD inlined + 3-perspective review)
  vibeflow-brainstorming/          # Problem exploration (optional pre-Design)
  vibeflow-build-init/
  vibeflow-build-config/
  vibeflow-build-work/
  vibeflow-tdd/
  vibeflow-quality/
  vibeflow-feature-st/
  vibeflow-spec-review/
  vibeflow-review/
  vibeflow-careful/                # Safety: destructive command warnings
  vibeflow-freeze/                 # Safety: edit boundary restrictions
  vibeflow-guard/                  # Safety: careful + freeze combined
  vibeflow-unfreeze/              # Safety: clear freeze boundary
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
  new-vibeflow-work-config.py
  test-vibeflow-setup.py

templates/
  prototype.yaml
  web-standard.yaml
  api-standard.yaml
  enterprise.yaml

claude-code/
  install.sh
  install.ps1

.claude-plugin/
  marketplace.json
  plugin.json
```

## Router State Machine

Routing is file-driven through `scripts/get-vibeflow-phase.py`.

Detected phases:

- `increment`
- `think`
- `template-selection`
- `plan`
- `requirements`
- `design`
- `build-init`
- `build-config`
- `build-work`
- `review`
- `test-system`
- `test-qa`
- `ship`
- `reflect`
- `done`

## Runtime Artifacts

### VibeFlow State (`.vibeflow/`)

- `.vibeflow/state.json` — Workflow state, current phase, active change, artifact map
- `.vibeflow/state.json.quick_meta` — Quick Mode eligibility, risk, validation, rollback, promotion rules
- `.vibeflow/workflow.yaml` — Workflow config (from template)
- `.vibeflow/work-config.json` — Build config (quality gates, enabled steps)
- `.vibeflow/guides/build.md` — Build session guide
- `.vibeflow/guides/services.md` — Service lifecycle guide
- `.vibeflow/logs/session-log.md` — Human-readable progress log
- `.vibeflow/logs/retro-YYYY-MM-DD.md` — Iteration retrospective
- `.vibeflow/increments/queue.json` — Pending increments queue
- `.vibeflow/increments/requests/*.json` — Increment request payloads
- `.vibeflow/increments/history.json` — Increment processing history

### Project Artifacts

- `docs/changes/<change-id>/context.md` — Think artifact
- `docs/changes/<change-id>/proposal.md` — Plan / value-review artifact
- `docs/changes/<change-id>/requirements.md` — Software Requirements Specification
- `docs/changes/<change-id>/ucd.md` — UCD artifact (when UI applies)
- `docs/changes/<change-id>/design.md` — Technical design document
- `docs/changes/<change-id>/design-review.md` — Engineering + design review conclusions
- `docs/changes/<change-id>/tasks.md` — Build task breakdown
- `docs/changes/<change-id>/verification/review.md` — Global review report
- `docs/changes/<change-id>/verification/system-test.md` — System test report
- `docs/changes/<change-id>/verification/qa.md` — QA test report
- `docs/plans/*-brainstorming.md` — Brainstorming output (optional)
- `docs/test-cases/feature-*.md` — Feature test case documents
- `feature-list.json` — Feature inventory (single source of truth during Build)
- `RELEASE_NOTES.md` — Release notes

## Templates

The project includes four static templates:

- `prototype`
- `web-standard`
- `api-standard`
- `enterprise`

Template selection writes `.vibeflow/workflow.yaml`.
Template-derived build trimming writes `.vibeflow/work-config.json`.

## Skill Catalog

### Core Layer

- `vibeflow` — Framework entry point
- `vibeflow-router` — Session router, file-driven phase dispatch, Build handoff into the implementation loop
- `vibeflow-think` — Think phase: problem framing and template selection

### Exploratory Layer (Optional)

- `vibeflow-office-hours` — YC Office Hours style brainstorming (pre-Think)
- `vibeflow-brainstorming` — Problem exploration (pre-Design)

### Planning Layer

- `vibeflow-plan` — Plan phase entry: CEO value review gate
- `vibeflow-plan-value-review` — CEO/Founder perspective value review (fail-fast gate)
- `vibeflow-plan-eng-review` — Engineering perspective review (architecture, code quality, testing, performance)
- `vibeflow-plan-design-review` — Design perspective review (7-round review: IA, interaction, journey, AI slop, design system, a11y, unresolved)
- `vibeflow-requirements` — Software Requirements Specification (ISO 29148)
- `vibeflow-design` — Technical design document (with inline UCD + 3-perspective review at Step 5)

### Build Layer

- `vibeflow-build-init` — Initialize build artifacts
- `vibeflow-build-config` — Configure feature implementation details
- `vibeflow-build-work` — Single-feature orchestrator: TDD → Quality → ST → Review
- `vibeflow-tdd` — TDD Red-Green-Refactor cycle
- `vibeflow-quality` — Quality gates: line coverage, branch coverage, mutation score
- `vibeflow-feature-st` — Feature-level acceptance testing (ISO 29119)
- `vibeflow-spec-review` — Spec compliance review against SRS and Design

### Safety Guardrails Layer (Optional)

- `vibeflow-careful` — Warns before destructive commands (rm -rf, DROP TABLE, etc.)
- `vibeflow-freeze` — Restricts Edit/Write to specified directory
- `vibeflow-guard` — Combines careful + freeze for maximum safety mode
- `vibeflow-unfreeze` — Clears freeze boundary

### Verification & Release Layer

- `vibeflow-review` — Cross-feature holistic change review
- `vibeflow-test-system` — System-level integration tests and NFR validation
- `vibeflow-test-qa` — Browser-driven QA verification (UI projects only)
- `vibeflow-ship` — Version release, PR creation, changelog
- `vibeflow-reflect` — Iteration retrospective and improvement suggestions

## Implementation Notes

- the repository contains the full local alias layer for all stages
- routing is deterministic and based on files rather than memory
- UCD is inlined into the Design phase (Step 1), not a separate phase
- Plan phase only does CEO value review; eng/design reviews happen at Design phase Step 5
- safety guardrails are opt-in (not enabled by default)
- exploratory skills (office-hours, brainstorming) are optional pre-cursors

## Verification

Use these commands locally:

```powershell
python scripts/get-vibeflow-phase.py
python scripts/get-vibeflow-phase.py --verbose
python scripts/test-vibeflow-setup.py --json
```
