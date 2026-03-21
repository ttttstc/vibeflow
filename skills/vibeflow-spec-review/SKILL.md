---
name: vibeflow-spec-review
description: Use for per-feature compliance review against requirements and design.
---

# Spec Compliance Review for VibeFlow

Review the implemented feature against the approved requirements and design. Per-feature review before marking complete.

**Announce at start:** "I'm using the vibeflow-spec-review skill to review this feature's compliance."

## Purpose

Verify that implementation matches:
1. Approved requirements specification (SRS)
2. Approved technical design
3. Agreed implementation approach
4. UCD style guide (for UI features)

## When to Run

- After TDD cycle completes
- After quality gates pass
- After feature acceptance testing (if enabled)
- Before marking feature complete
- Invoked by `vibeflow-build-work` (Step 5)

## Step 1: Load Review Context

### 1.1 Read Feature Spec

From `feature-list.json`:
- Feature ID, title, description
- `verification_steps[]`
- `dependencies[]`
- `ui` flag

### 1.2 Read SRS Requirement Section

From `docs/plans/*-srs.md`:
- Full FR-xxx section for this feature
- Given/When/Then acceptance criteria
- Priority and severity
- Related NFRs

### 1.3 Read Design Section

From `docs/plans/*-design.md`:
- Full §4.N subsection for this feature
- Architecture decisions
- Interface contracts
- Data flows

### 1.4 Read Plan Document

From `docs/plans/YYYY-MM-DD-<feature-name>.md`:
- Implementation approach agreed
- Task decomposition
- Design decisions made

### 1.5 Read UCD (if ui: true)

From `docs/plans/*-ucd.md`:
- Style tokens
- Component visual spec
- Page layouts

### 1.6 Read Test Results

From `docs/test-cases/feature-{id}-{slug}.md`:
- Executed test case results
- PASS/FAIL status
- Any failures encountered

### 1.7 Read Git Diff

Get changes made during implementation:
```bash
git diff --stat
git diff
```

## Step 2: Spec Compliance Review

### 2.1 Requirements Traceability

For each `verification_step`:
- [ ] Step is covered by at least one test
- [ ] Test verifies the behavior described in the step
- [ ] Test result is PASS
- [ ] No undocumented side effects

### 2.2 Acceptance Criteria Compliance

For each Given/When/Then from SRS:
- [ ] Given conditions are met in implementation
- [ ] When actions trigger expected behavior
- [ ] Then results match expected outcomes
- [ ] Edge cases from spec are handled

### 2.3 Verification Completeness

- [ ] All `verification_steps` have corresponding tests
- [ ] Tests verify behavior, not implementation details
- [ ] No verification gaps

## Step 3: Design Compliance Review

### 3.1 Architecture Compliance

- [ ] Class/module structure matches design
- [ ] Interaction flows match design
- [ ] Third-party dependency versions match design
- [ ] Architectural layers/boundaries respected

### 3.2 Interface Compliance

For each interface contract in design:
- [ ] Method signatures match
- [ ] Parameter types match
- [ ] Return types match
- [ ] Exception handling matches

### 3.3 Algorithm Compliance

- [ ] Core algorithm matches pseudocode
- [ ] Control flow matches design
- [ ] Data transformations correct
- [ ] Boundary conditions handled

## Step 4: Implementation Review

### 4.1 Code Quality

- [ ] No placeholder comments (TODO with no follow-up)
- [ ] No commented-out code
- [ ] Consistent naming conventions
- [ ] Error handling appropriate

### 4.2 Test Quality

- [ ] Unit tests exist for core logic
- [ ] Integration tests exist for external dependencies
- [ ] Tests are maintainable
- [ ] No test code duplication

## Step 5: UCD Compliance (if ui: true)

### 5.1 Visual Compliance

- [ ] Color values match UCD palette tokens
- [ ] Typography matches UCD scale
- [ ] Spacing follows UCD tokens
- [ ] Component structure matches UCD prompts

### 5.2 Interaction Compliance

- [ ] Interactive elements behave as specified
- [ ] State transitions match UCD descriptions
- [ ] Accessibility features implemented

## Step 6: Compile Review Findings

### 6.1 Issue List

For each issue found:
```
## Issue: [Title]
**Severity:** Critical | Important | Minor
**Location:** File, line, component
**Description:** What is wrong
**Evidence:** How it was detected
**Fix:** Recommended fix
```

### 6.2 Severity Classification

| Severity | Response | Blocks? |
|----------|----------|---------|
| Critical | Fix immediately | Yes |
| Important | Fix before next feature | Yes |
| Minor | Fix in refactor or next session | No |

### 6.3 Review Verdict

**PASS** — All critical and important issues fixed
**FAIL** — Critical or important issues remain

## Step 7: Fix Issues (if any)

### 7.1 For Critical Issues

1. Fix immediately in this session
2. Re-run relevant tests
3. Re-verify the fix
4. Update issue status

### 7.2 For Important Issues

1. Fix before proceeding to next feature
2. Document fix in task-progress.md
3. Track for follow-up

### 7.3 For Minor Issues

1. Document for refactor or next session
2. Track in issue list

## Step 8: Complete Review

### 8.1 Update Feature Status

If review PASS:
- Mark feature review complete in task-progress.md
- Proceed to persist (git commit)

### 8.2 Escalation (if review fails after fixes)

After 3 rounds of fixes:
- Document all issues found
- Document what was tried
- Escalate to user

## Checklist

Before marking spec review complete:

- [ ] All verification_steps verified by tests
- [ ] All Given/When/Then acceptance criteria met
- [ ] Architecture matches design document
- [ ] Interface contracts match design
- [ ] Algorithm matches pseudocode
- [ ] UCD style guide followed (if ui: true)
- [ ] No critical issues remain
- [ ] No important issues remain (or tracked for fix)
- [ ] Review verdict: PASS

## Integration

**Called by:** `vibeflow-build-work` (Step 5 — Spec review)
**Requires:**
- Feature spec from `feature-list.json`
- SRS requirement section from `docs/plans/*-srs.md`
- Design section from `docs/plans/*-design.md`
- Plan document from `docs/plans/YYYY-MM-DD-<feature-name>.md`
- Test case document from `docs/test-cases/feature-{id}-{slug}.md`
- UCD (if ui: true) from `docs/plans/*-ucd.md`
- Git diff of implementation changes
**Produces:** Review verdict with findings
**Returns to:** `vibeflow-build-work` for persist step
