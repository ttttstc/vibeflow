---
name: vibeflow-think
description: Use for the Think phase in VibeFlow projects to define the problem, boundaries, opportunity scan, and choose a workflow template.
---

## Goal

Produce the Phase 1 MVP artifacts:

- `.vibeflow/think-output.md`
- `.vibeflow/workflow.yaml` after template confirmation

## Reuse First

Before questioning or writing:

1. Read `VIBEFLOW-DESIGN.md`
2. Reuse the existing product-discovery foundation already available in the workspace

Use that foundation for questioning style and problem-reframing mindset.
Do not duplicate its broader setup behavior here.

## Required Inputs

Gather enough context from:

- the user's request
- `VIBEFLOW-DESIGN.md`
- existing root docs in the repo

## Think Flow

### 1. Problem framing

Drive the conversation toward:

- the actual problem being solved
- who the user is
- what is explicitly out of scope
- the smallest useful first version

### 2. Complexity and risk scan

State:

- project type
- expected scale
- major risks

### 3. Opportunity scan

Produce:

- a 10x version
- the minimum viable version
- one fast value-add that fits in roughly 30 minutes

### 4. Template recommendation

Choose one static template from `templates/`:

| Template | Use when |
|---|---|
| `prototype` | fast validation, reduced gates, speed over rigor |
| `web-standard` | UI-heavy product or general full-stack app |
| `api-standard` | backend or integration-first system without UI-heavy work |
| `enterprise` | strict review, auditability, and higher quality thresholds |

### 5. Write think output

Write `.vibeflow/think-output.md` using exactly this structure:

```markdown
# Think Output

## Problem Statement
[1-3 sentences]

## Boundaries
### In Scope
- [...]

### Out of Scope
- [...]

## User Profile
- Primary user: [...]
- Usage scenario: [...]
- Success criteria: [...]

## Complexity Assessment
- Project type: [...]
- Scale: [...]
- Key risks:
  - [...]

## Opportunity Scan
- 10x version: [...]
- Minimum viable version: [...]
- Quick value add: [...]

## Recommended Template
[prototype | web-standard | api-standard | enterprise]
Reason: [...]
```

### 6. Confirm and create workflow

After writing `think-output.md`:

- ask for template confirmation if the user has not already made the choice explicit
- create `.vibeflow/`
- copy `templates/<template>.yaml` to `.vibeflow/workflow.yaml`
- set `created_at` to the current date

## Hard Rules

- Do not create new workflow schemas dynamically.
- Do not invent new templates.
- Keep this skill thin and orchestration-focused.
- If the repo direction clearly conflicts with the currently recommended template, explain the conflict before writing `workflow.yaml`.

