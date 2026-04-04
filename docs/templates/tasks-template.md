# <Project Name> — Tasks

> 这是 `tasks` 阶段的 execution-grade handoff 模板。
>
> 目标：把 `context.md + design.md + design-review.md` 翻译成 build-init / build-work 可稳定消费的任务计划。

## Feature <id> - <title>

### Task <task-id>

- `feature_id`: <id>
- `goal`: <one-sentence goal>
- `change_type`: <code|test|config|docs|migration|qa>
- `design_section`: <for example 4.1>
- `build_contract_ref`: <for example docs/changes/<change-id>/design.md#build-contract>
- `exact_file_paths`:
  - `<repo-relative-path>`
  - `<repo-relative-path>`
- `depends_on`:
  - `<task-id or none>`
- `steps`:
  - `<ordered implementation step>`
  - `<ordered implementation step>`
- `verification_steps`:
  - `<exact command or exact manual verification>`
  - `<exact command or exact manual verification>`
- `rollback_note`: <smallest safe rollback path>
- `expected_duration_min`: <2-5 by default>

### Task <task-id>

- `feature_id`: <id>
- `goal`: <one-sentence goal>
- `change_type`: <code|test|config|docs|migration|qa>
- `design_section`: <for example 4.1>
- `build_contract_ref`: <for example docs/changes/<change-id>/design.md#build-contract>
- `exact_file_paths`:
  - `<repo-relative-path>`
- `depends_on`:
  - `<task-id or none>`
- `steps`:
  - `<ordered implementation step>`
- `verification_steps`:
  - `<exact command or exact manual verification>`
- `rollback_note`: <smallest safe rollback path>
- `expected_duration_min`: <2-5 by default>
