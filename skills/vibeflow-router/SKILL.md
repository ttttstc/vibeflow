---
name: vibeflow-router
description: Use at session start in this repo to route work across the full VibeFlow lifecycle.
---

<EXTREMELY-IMPORTANT>
If this repository contains `VIBEFLOW-DESIGN.md`, you must use this router before doing phase work.
</EXTREMELY-IMPORTANT>

## Routing Contract

The router is file-driven. Determine the current phase from `scripts/get-vibeflow-phase.py`.

Return values and required actions:

- `increment` -> process the latest incremental request before any other stage work
- `think` -> use `skills/vibeflow-think/SKILL.md`
- `template-selection` -> create `.vibeflow/workflow.yaml` from `templates/`
- `plan-review` -> use `skills/vibeflow-plan-review/SKILL.md`
- `requirements` -> use `skills/vibeflow-requirements/SKILL.md`
- `ucd` -> use `skills/vibeflow-ucd/SKILL.md`
- `design` -> use `skills/vibeflow-design/SKILL.md`
- `build-init` -> use `skills/vibeflow-build-init/SKILL.md`
- `build-config` -> run `scripts/new-vibeflow-work-config.py`
- `build-work` -> use `skills/vibeflow-build-work/SKILL.md`
- `review` -> use `skills/vibeflow-review/SKILL.md`
- `test-system` -> use `skills/vibeflow-test-system/SKILL.md`
- `test-qa` -> use `skills/vibeflow-test-qa/SKILL.md`
- `ship` -> use `skills/vibeflow-ship/SKILL.md`
- `reflect` -> use `skills/vibeflow-reflect/SKILL.md`
- `done` -> report completion summary and next optional actions

## Template Selection

When phase is `template-selection`:

1. Read `.vibeflow/think-output.md`
2. Recommend one of:
   - `prototype`
   - `web-standard`
   - `api-standard`
   - `enterprise`
3. After confirmation, run:
   - `python scripts/new-vibeflow-config.py --template <template>`
4. Then generate work config:
   - `python scripts/new-vibeflow-work-config.py`

## Build Rules

- `feature-list.json` is the build inventory source of truth
- `.vibeflow/work-config.json` is the step-trimming source of truth
- build flow order is: init -> work -> review -> system test

## Hard Rules

- Keep project-facing naming vendor-neutral.
- Prefer the VibeFlow alias names over underlying foundation names.
- Never infer phase from memory when file state is available.

