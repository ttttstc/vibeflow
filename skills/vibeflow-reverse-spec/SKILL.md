---
name: vibeflow-reverse-spec
description: Refreshes docs/overview architecture context for an existing codebase (Python + TypeScript)
---

# Reverse-Generated Overview Context

[VibeFlow skill for automatic architecture documentation generation]

## Goal
Refresh the current `docs/overview/` context for an existing codebase so new contributors can immediately understand:
- current module layout
- key entry points
- current change focus
- risks and suggested reading order

## Trigger
- Explicit: `/vibeflow-reverse-spec`
- Auto-trigger: VibeFlow detects non-empty project with missing or stale `docs/overview/ARCHITECTURE.md`

## Prerequisites
- Project must contain Python (.py) or TypeScript (.ts/.tsx/.js/.jsx) source files
- Non-empty project (at least 1 module detected)

## Execution Flow

### Step 1: Refresh project and architecture overview
```
Run: python scripts/map-codebase.py --project-root {project_root} --refresh force
Output: docs/overview/PROJECT.md + docs/overview/ARCHITECTURE.md
```

### Step 2: Refresh current change focus
```
Run: python scripts/map-change-impact.py --project-root {project_root} --source design
Output: docs/overview/CURRENT-STATE.md
```

### Step 3: Verify output
- Check `docs/overview/PROJECT.md` exists
- Check `docs/overview/ARCHITECTURE.md` exists
- Check `docs/overview/CURRENT-STATE.md` exists
- Confirm `CURRENT-STATE.md` includes current change focus and overview sync status

## Output
- `docs/overview/PROJECT.md` — long-lived project context
- `docs/overview/ARCHITECTURE.md` — long-lived architecture context
- `docs/overview/CURRENT-STATE.md` — current change focus and sync status
- `.vibeflow/wiki-status.json` — freshness tracking

## Quality Gate
- Module graph must have > 0 nodes
- If 0 modules detected → exit with error: "No source modules detected. Ensure this is a non-empty project with Python or TypeScript source files."

## Integration
- This skill is a pre-Design step
- If overview docs are already fresh → silently succeed
- Design phase should read `docs/overview/PROJECT.md` and `docs/overview/ARCHITECTURE.md`
