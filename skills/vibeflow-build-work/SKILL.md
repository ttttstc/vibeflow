---
name: vibeflow-build-work
description: Use when build initialization is done and some features are still failing.
---

# Build Work Orchestration for VibeFlow

Drive one feature at a time through the implementation pipeline. Each feature follows a strict sequence: TDD → Quality Gates → Feature Acceptance → Spec Review.

**Announce at start:** "I'm using the vibeflow-build-work skill. Let me orient myself on the current state."

## The Iron Law

```
ONE FEATURE PER CYCLE — DO NOT SKIP STEPS
```

Each step has its own skill. Follow the orchestration order exactly. No shortcuts.

## Step 1: Orient — Load Current State

### 1.1 Read Work Config

Read `.vibeflow/work-config.json` to determine enabled steps:
```json
{
  "build": {
    "tdd": true,
    "quality": true,
    "feature_st": true,
    "spec_review": true
  }
}
```

### 1.2 Read Feature List

Read `feature-list.json`:
- Note all features with `"status": "failing"`
- Note feature priorities
- Note feature dependencies
- Skip features with `"deprecated": true`

### 1.3 Read Task Progress

Read `task-progress.md`:
- Progress stats (X/Y features passing)
- Last completed feature
- Next feature up

### 1.4 Select Next Feature

**Dependency satisfaction check:**
1. Pick next `"status": "failing"` feature by priority (high → medium → low)
2. Verify ALL features in `dependencies[]` have `"status": "passing"`
3. If any dependency is still `"failing"`:
   - Log: "Feature #{id} ({title}) skipped — unsatisfied deps: #{dep1}, #{dep2}"
   - Pick the next eligible failing feature
4. If NO features have all dependencies satisfied → escalate to user

### 1.5 Load Feature Context

For the selected feature, read:
- Feature spec from `feature-list.json`
- Requirements section from `docs/plans/*-srs.md`
- Design section from `docs/plans/*-design.md`
- Any previous implementation notes from `task-progress.md`

## Step 2: TDD Cycle (if enabled in work-config)

**Invoke skill:** `vibeflow-tdd`

### 2.1 TDD Red — Write Failing Tests

Context to carry forward:
- Feature object from `feature-list.json`
- `verification_steps[]` from the feature
- `tech_stack` from `feature-list.json`

### 2.2 TDD Green — Minimal Implementation

Implement only enough to pass failing tests.

### 2.3 TDD Refactor — Clean Up

Clean up without breaking green.

### 2.4 Verify TDD Complete

All tests pass. Proceed to Step 3.

## Step 3: Quality Gates (if enabled in work-config)

**Invoke skill:** `vibeflow-quality`

### 3.1 Gate 0: Real Test Verification

Verify integration tests exist and pass (or exemption declared).

### 3.2 Gate 1: Coverage

Run coverage tool. Verify line and branch coverage meet thresholds.

### 3.3 Gate 2: Mutation Testing

Run mutation testing. Verify mutation score meets threshold.

### 3.4 Gate 3: Verify & Mark

Run full verification in session. Mark feature passing only if all gates pass.

### 3.5 Verify Quality Complete

All gates pass. Proceed to Step 4.

## Step 4: Feature Acceptance Testing (if enabled)

**Invoke skill:** `vibeflow-feature-st`

### 4.1 Create Test Cases

For each `verification_step`, create black-box acceptance test cases:
- Happy path tests
- Error handling tests
- Boundary tests
- UI tests (if `ui: true`)

### 4.2 Execute Test Cases

Run all test cases against the running system.
Document results in `docs/test-cases/feature-{id}-{slug}.md`.

### 4.3 Verify All Pass

All acceptance tests pass. Proceed to Step 5.

## Step 5: Spec Compliance Review (if enabled)

**Invoke skill:** `vibeflow-spec-review`

### 5.1 Review Against Spec

Verify implementation matches:
- SRS requirement section
- Design document
- Plan document

### 5.2 Review Against UCD (if ui: true)

Verify implementation follows UCD style guide.

### 5.3 Verify Compliance

Spec compliance confirmed. Proceed to Step 6.

## Step 6: Persist

### 6.1 Git Commit

Commit the completed feature:
- Implementation code
- Tests
- Test case documents
- Updated `task-progress.md`

### 6.2 Update Feature Status

In `feature-list.json`:
```json
{
  "id": 1,
  "status": "passing",
  "completed_date": "2026-03-21"
}
```

### 6.3 Update Task Progress

In `task-progress.md`:
- Update progress count
- Record completed feature
- Note next feature

## Step 7: Continue or Complete

### 7.1 Check Remaining Features

If failing non-deprecated features remain → return to Step 1.

### 7.2 All Features Complete

If NO failing features remain:
- All active features are passing
- Invoke `vibeflow-test-system` to begin system testing

## Checklist

Per feature cycle:

- [ ] Step 1: Orient — state loaded, next feature selected
- [ ] Step 2: TDD complete (if enabled) — all tests pass
- [ ] Step 3: Quality gates pass (if enabled) — coverage, mutation verified
- [ ] Step 4: Feature acceptance pass (if enabled) — test cases executed
- [ ] Step 5: Spec review pass (if enabled) — compliance confirmed
- [ ] Step 6: Persist — git commit, status updated
- [ ] Step 7: Continue or complete

## Critical Rules

- **One feature per cycle** — prevents context exhaustion
- **Strict step order** — no skipping, no reordering
- **Never mark "passing" without fresh evidence** — run tests, read output, then mark
- **Dependency check before starting** — never develop a feature whose dependencies are still failing
- **Config gate before planning** — never code when required configs are missing

## Integration

**Called by:** `vibeflow` router (when feature-list.json exists and build is active)
**Invokes (in strict order when enabled):**
1. `vibeflow-tdd` (Step 2) — Red-Green-Refactor
2. `vibeflow-quality` (Step 3) — Coverage + Mutation
3. `vibeflow-feature-st` (Step 4) — Black-Box Feature Acceptance
4. `vibeflow-spec-review` (Step 5) — Spec & Design Compliance
**Reads/Writes:** `feature-list.json`, `task-progress.md`
**Chains to:** `vibeflow-test-system` (when all features pass)
