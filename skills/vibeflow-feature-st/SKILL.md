---
name: vibeflow-feature-st
description: Use for feature-level acceptance testing during the VibeFlow build stage.
---

# Feature System Testing for VibeFlow

Create and execute black-box acceptance test cases for a feature. Runs after TDD and quality gates pass.

**Announce at start:** "I'm using the vibeflow-feature-st skill to run acceptance testing for this feature."

## Purpose

Verify the feature works as a user or external system would see it. Tests validate behavior through the real interface (API, UI, CLI), not by inspecting implementation code.

## When to Run

- After TDD cycle completes (all tests pass)
- After quality gates pass (coverage, mutation)
- Before spec compliance review
- Invoked by `vibeflow-build-work` (Step 4)

## Black-Box Philosophy

TDD has verified the implementation from the inside (unit tests, coverage, mutation). This skill verifies from the **outside**:

- Inputs go through the real interface (HTTP endpoints, UI, CLI)
- Outputs observed through the real interface (responses, rendered UI, stdout)
- Internal implementation is NOT consulted during test design
- Expected results derivable from SRS specification only

**Rule:** If a test case requires reading source code to determine expected result, it is not a black-box test.

## Step 1: Load Feature Context

### 1.1 Read Feature Spec

From `feature-list.json`:
- Feature ID, title, description
- `verification_steps[]`
- `ui` flag
- `dependencies[]`

### 1.2 Read Requirements Section

From `docs/plans/*-srs.md`:
- FR-xxx section for this feature
- Given/When/Then acceptance criteria
- Boundary conditions
- Error paths

### 1.3 Read Design Section

From `docs/plans/*-design.md`:
- Interface contracts
- Data flows
- Integration points

### 1.4 Read UCD (if ui: true)

From `docs/plans/*-ucd.md`:
- Style tokens
- Component visual spec
- Page layouts

## Step 2: Derive Test Cases

### 2.1 Category Assignment

For each `verification_step`, derive test cases:

| Category | When to generate |
|----------|-----------------|
| `functional` | Always — happy path + error path |
| `boundary` | Always — edge cases, limits, empty/max/zero |
| `ui` | Only when `"ui": true` — browser interaction |
| `security` | When feature handles user input or auth |
| `accessibility` | Only when `"ui": true` — WCAG checks |

### 2.2 Minimum Coverage

Every feature MUST have:
- At least one functional test case
- At least one boundary test case
- At least one UI test case (if `"ui": true`)
- At least one accessibility test case (if `"ui": true`)

### 2.3 Test Case Format

**Case ID:** `ST-{CATEGORY}-{FEATURE_ID}-{SEQ}`
Examples: `ST-FUNC-001-001`, `ST-BNDRY-001-002`, `ST-UI-001-001`

**Test Case Structure:**
```
## Test Case: ST-FUNC-001-001

**Feature:** Feature title
**Category:** functional
**Test type:** Real (not mock)

### Preconditions
- Condition 1
- Condition 2

### Test Steps
1. Step description
2. Step description

### Expected Results
- Result 1
- Result 2

### Verification Steps
- Check 1
- Check 2
```

### 2.4 UI Test Case Requirements (if ui: true)

For UI features, test cases must include:
- Navigation path from `ui_entry` or specific route
- Interaction sequence (click, fill, press_key)
- EXPECT/REJECT clauses for each verification point
- Console error check (0 errors unless expected)
- Accessibility checkpoint (keyboard navigability, ARIA if applicable)

## Step 3: Write Test Case Document

### 3.1 Create Document

Output file: `docs/test-cases/feature-{id}-{slug}.md`

Document structure:
1. **Header** — Feature ID, related requirements, date
2. **Summary table** — count by category
3. **Test case blocks** — one per case
4. **Traceability matrix** — Case ID ↔ Requirement ↔ verification_step ↔ Result

### 3.2 Traceability Matrix

| Case ID | Category | verification_step | Status |
|---------|----------|-------------------|--------|
| ST-FUNC-001-001 | functional | Step 1 text | PENDING |
| ST-BNDRY-001-001 | boundary | Step 2 text | PENDING |

## Step 4: Execute Test Cases

### 4.1 Start Services (if needed)

For features requiring running services:
1. Read service start commands from project documentation
2. Start services
3. Verify health endpoints respond
4. Record service PIDs for cleanup

### 4.2 Execute Non-UI Tests

Run test cases against the running system:
1. For each functional test: execute via API/CLI
2. For each boundary test: execute with edge case inputs
3. Record PASS/FAIL for each

### 4.3 Execute UI Tests (if ui: true)

For UI features:
1. Use browser automation (e.g., Chrome DevTools MCP or project tool)
2. Navigate to the UI entry point
3. Execute interaction sequences
4. Verify EXPECT/REJECT conditions
5. Check for console errors

### 4.4 Update Traceability Matrix

After each test case:
- Update result to PASS or FAIL
- If FAIL: record actual vs expected

## Step 5: Handle Failures

### 5.1 Any Test Case Failure

- Report failed case ID, step details, actual vs expected
- Fix implementation code
- Re-execute failed test cases
- Do NOT skip or bypass any test case

### 5.2 Escalation

After 3 failed attempts to fix:
- Document the issue
- Escalate to user via `AskUserQuestion`
- Options: fix code, modify test case, terminate feature

## Step 6: Complete Testing

### 6.1 Final Status

If ALL test cases PASS:
- Update final status in traceability matrix
- Proceed to spec review (vibeflow-spec-review)

### 6.2 Stop Services

If services were started for testing:
1. Stop services by PID
2. Verify ports no longer respond
3. Record cleanup status

## Checklist

Before marking feature acceptance complete:

- [ ] All test cases written and documented
- [ ] Test case document saved to `docs/test-cases/feature-{id}-{slug}.md`
- [ ] All functional tests executed and passed
- [ ] All boundary tests executed and passed
- [ ] All UI tests executed and passed (if ui: true)
- [ ] All accessibility tests executed and passed (if ui: true)
- [ ] All console error checks passed (if ui: true)
- [ ] Services stopped and cleaned up
- [ ] Traceability matrix updated with final results

## Quality Gates

| Gate | Requirement |
|------|-------------|
| Coverage | All verification_steps have corresponding test cases |
| Execution | All test cases executed with PASS result |
| Traceability | Traceability matrix complete |

## Integration

**Called by:** `vibeflow-build-work` (Step 4 — Feature acceptance)
**Requires:**
- Feature spec from `feature-list.json`
- SRS requirement section from `docs/plans/*-srs.md`
- Design section from `docs/plans/*-design.md`
- UCD (if ui: true) from `docs/plans/*-ucd.md`
- TDD tests passing
- Quality gates passing
**Produces:**
- Test case document at `docs/test-cases/feature-{id}-{slug}.md`
- Executed results in traceability matrix
**Chains to:** `vibeflow-spec-review` (after all tests pass)
