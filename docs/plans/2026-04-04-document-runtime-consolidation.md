# VibeFlow Document And Runtime Consolidation

## Goal

Reduce the number of developer-facing documents and internal runtime files so the framework is easier to understand and maintain.

## Decisions

### 1. Rename Spark artifact

- Spark no longer writes `context.md`.
- Spark now writes `docs/changes/<change-id>/brief.md`.
- `brief.md` is the human-readable contract for:
  - goal
  - scope
  - non-goals
  - acceptance criteria
  - constraints
  - assumptions

### 2. Simplify global vs per-change docs

Global project docs live under `docs/overview/`:

- `CURRENT-STATE.md`
- `PROJECT.md`
- `ARCHITECTURE.md`

Per-change docs live under `docs/changes/<change-id>/`:

- `brief.md`
- `design.md`
- `tasks.md`
- `verification/`

`PRODUCT.md` is removed. Stable product-facing information moves into `PROJECT.md`.

### 3. Reduce internal runtime surface

Keep as core runtime files:

- `.vibeflow/state.json`
- `.vibeflow/workflow.yaml`
- `.vibeflow/runtime.json`
- `.vibeflow/work-config.json`

Reduce or defer:

- `phase-history.json` is removed as a standalone file and embedded into `state.json` as `phase_history`.
- `session-log.md` is no longer pre-created during init; it is generated lazily when build automation first writes to it.

### 4. Update rule for global doc synchronization

Per-change docs do not automatically overwrite global docs.

Global docs are updated only when the change affects long-lived facts, such as:

- project positioning
- stable capabilities
- architecture or module boundaries
- repo-wide constraints

## Implementation Notes

- Use `brief.md` everywhere the mainline previously referenced `context.md`.
- Stop generating `PRODUCT.md` in overview refresh logic.
- Keep `docs/overview/README.md` as a lightweight index only.
- Preserve `feature-list.json` as the build-time source of truth.

## Expected Outcome

Developers should be able to answer:

1. What is this project and where is it now?
   - `docs/overview/CURRENT-STATE.md`
   - `docs/overview/PROJECT.md`
   - `docs/overview/ARCHITECTURE.md`

2. What is this specific change doing?
   - `docs/changes/<change-id>/brief.md`
   - `docs/changes/<change-id>/design.md`
   - `docs/changes/<change-id>/tasks.md`
   - `docs/changes/<change-id>/verification/`
