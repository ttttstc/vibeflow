---
name: vibeflow-build-init
description: Use when design exists but feature-list.json has not been initialized.
---

# Build Initialization for VibeFlow

Initialize implementation artifacts for the build stage. Run once after requirements and design are approved.

**Announce at start:** "I'm using the vibeflow-build-init skill to scaffold the build stage."

## Purpose

Create all persistent artifacts needed for the VibeFlow build stage:
- Feature inventory with status tracking
- Work configuration
- Progress tracking

## Prerequisites

Before running this skill:
- Requirements document exists at `docs/plans/*-srs.md`
- Design document exists at `docs/plans/*-design.md`
- Think output exists at `.vibeflow/think-output.md`
- Workflow config exists at `.vibeflow/workflow.yaml`

## Step 1: Read Input Documents

### 1.1 Read Requirements (SRS)

Read `docs/plans/*-srs.md`:
- Functional requirements (FR-xxx)
- Non-functional requirements (NFR-xxx)
- Constraints (CON-xxx)
- Assumptions (ASM-xxx)
- Acceptance criteria
- Interface requirements

### 1.2 Read Design Document

Read `docs/plans/*-design.md`:
- Tech stack
- Architecture
- Data model
- API design
- Testing strategy
- Task decomposition

### 1.3 Read Workflow Config

Read `.vibeflow/workflow.yaml`:
- Selected template (prototype, web-standard, api-standard, enterprise)
- Stage sequence
- Enabled features

## Step 2: Create Work Config

### 2.1 Create `.vibeflow/work-config.json`

```json
{
  "build": {
    "tdd": true,
    "quality": true,
    "feature_st": true,
    "spec_review": true
  },
  "quality": {
    "tdd": true,
    "quality_gates": {
      "line_coverage_min": 80,
      "branch_coverage_min": 70,
      "mutation_score_min": 70
    }
  }
}
```

Adjust thresholds based on:
- Project template (prototype may have lower thresholds)
- Tech stack capabilities
- Team preferences

### 2.2 Save Work Config

Write to `.vibeflow/work-config.json`.

## Step 3: Create Feature List

### 3.1 Decompose Requirements

From the SRS and design documents, decompose into features:

**For each FR-xxx:**
1. Create one or more features with:
   - `id`: sequential integer
   - `category`: "core", "backend", "frontend", "infrastructure", "non-functional"
   - `title`: concise feature name
   - `description`: what it does
   - `priority`: "high", "medium", "low"
   - `status`: always `"failing"` at init
   - `verification_steps[]`: acceptance criteria derived from SRS
   - `dependencies[]`: feature IDs that must complete first

### 3.2 Feature Schema

```json
{
  "id": 1,
  "category": "core",
  "title": "Feature title",
  "description": "What it does",
  "priority": "high|medium|low",
  "status": "failing",
  "verification_steps": [
    "Given [context], when [action], then [result]"
  ],
  "dependencies": []
}
```

### 3.3 Handle UI Features

For features with UI components (`"ui": true`):
- Set `"ui": true`
- Add `"ui_entry": "/optional-path"` if applicable
- Ensure dependencies include backend API features
- Reference UCD document for style requirements

### 3.4 Handle Non-Functional Requirements

For NFR-xxx items:
- Create features with `category: "non-functional"`
- Include measurable `verification_steps` (e.g., "response time < 200ms")
- Quality gates (tdd, quality) may not apply — set accordingly in work-config

### 3.5 Dependency Ordering

Order features in the array respecting dependencies:
1. Infrastructure/core features first
2. Backend features before frontend features
3. Dependent features after their dependencies

## Step 4: Create Task Progress

### 4.1 Create `task-progress.md`

```markdown
# Task Progress

## Current State

- **Progress**: 0/N features passing
- **Last completed**: None
- **Next feature**: #1 [feature title]

---

## Session Log

### Session 0 (Init)
- Date: YYYY-MM-DD
- Action: Build initialization
- Features initialized: N
```

## Step 5: Validate

### 5.1 Validate Feature List

Verify feature-list.json is valid JSON:
- All required fields present
- No circular dependencies
- All dependency IDs reference existing features

### 5.2 Check Document Paths

Verify referenced documents exist:
- `docs/plans/*-srs.md`
- `docs/plans/*-design.md`

## Step 6: Initial Commit

### 6.1 Git Add

Stage all new files:
- `.vibeflow/work-config.json`
- `feature-list.json`
- `task-progress.md`

### 6.2 Git Commit

```
feat: initialize build stage artifacts

- Add work-config.json with quality thresholds
- Add feature-list.json with N features
- Add task-progress.md for session tracking
```

## Checklist

Before marking initialization complete:

- [ ] Work config created at `.vibeflow/work-config.json`
- [ ] Feature list created at `feature-list.json`
- [ ] Task progress created at `task-progress.md`
- [ ] All features have valid `verification_steps`
- [ ] Dependencies form a DAG (no cycles)
- [ ] UI features marked with `"ui": true`
- [ ] NFR features marked with `category: "non-functional"`
- [ ] Initial git commit created
- [ ] Build stage ready for `vibeflow-build-work`

## Outputs

| File | Purpose |
|------|---------|
| `.vibeflow/work-config.json` | Build stage configuration and quality thresholds |
| `feature-list.json` | Structured task inventory with status |
| `task-progress.md` | Session-by-session progress log |

## Integration

**Called by:** `vibeflow` router (when requirements and design exist, but feature-list.json does not)
**Requires:**
- Requirements doc at `docs/plans/*-srs.md`
- Design doc at `docs/plans/*-design.md`
- Think output at `.vibeflow/think-output.md`
- Workflow config at `.vibeflow/workflow.yaml`
**Produces:** `work-config.json`, `feature-list.json`, `task-progress.md`
**Chains to:** `vibeflow-build-work` (first feature cycle)
