---
name: vibeflow-review
description: Use after build completion for whole-change review across the branch or diff.
---

# Whole-Change Review for VibeFlow

Run a full review of all completed features before shipping. Cross-feature analysis for structural issues, hidden regressions, and completeness gaps.

**Announce at start:** "I'm using the vibeflow-review skill to run the whole-change review."

## Purpose

After all features pass their individual reviews, verify the complete change set is shippable:
- Structural issues across the codebase
- Hidden regressions from feature interactions
- Missing tests at the integration level
- Completeness gaps in the deliverable

## When to Run

- After ALL features pass individual spec reviews
- After system testing completes (if enabled)
- Before shipping
- Invoked by `vibeflow` router (between build and ship stages)

## Step 1: Load Review Context

### 1.1 Read Feature List

From `feature-list.json`:
- All features with `"status": "passing"`
- All feature IDs, titles, categories
- Feature dependencies

### 1.2 Read Task Progress

From `task-progress.md`:
- Session log of completed work
- Any issues recorded during build
- Open questions or known limitations

### 1.3 Read All Spec Docs

From `docs/plans/`:
- All SRS sections
- All design sections
- All plan documents

### 1.4 Get Git Diff

```bash
git diff main...HEAD --stat
git diff main...HEAD
```

This gives the full change set since the base branch.

## Step 2: Structural Review

### 2.1 Architecture Integrity

Review the complete change set:
- [ ] New modules/classes follow architecture
- [ ] Cross-feature dependencies are managed
- [ ] No circular dependencies introduced
- [ ] API contracts between modules maintained

### 2.2 Code Organization

- [ ] Files organized by convention
- [ ] No oversized files requiring splitting
- [ ] No duplicate code across features
- [ ] Configuration properly externalized

### 2.3 Dependency Management

- [ ] New dependencies justified
- [ ] Dependency versions locked
- [ ] No vulnerable dependencies
- [ ] Dependency licenses acceptable

## Step 3: Regression Analysis

### 3.1 Feature Interaction

For each pair of features that may interact:
- [ ] Features work correctly together
- [ ] No resource conflicts
- [ ] No data corruption between features
- [ ] API endpoints don't conflict

### 3.2 Integration Points

- [ ] All integration points tested
- [ ] Error handling at boundaries works
- [ ] Data flows correctly between features
- [ ] No data loss at integration points

### 3.3 Side Effects

- [ ] No unintended side effects from changes
- [ ] Global state changes are intentional
- [ ] Configuration changes are backward compatible
- [ ] No breaking changes to existing APIs

## Step 4: Test Coverage Review

### 4.1 Unit Test Coverage

From all test results:
- [ ] Core logic has adequate unit tests
- [ ] Edge cases covered
- [ ] Error paths covered

### 4.2 Integration Test Coverage

- [ ] Cross-feature interactions tested
- [ ] End-to-end scenarios covered
- [ ] Integration points exercised

### 4.3 System Test Coverage

If system testing was run:
- [ ] All system test cases passed
- [ ] NFRs verified
- [ ] Performance acceptable

## Step 5: Documentation Review

### 5.1 Code Documentation

- [ ] Public APIs documented
- [ ] Complex logic explained
- [ ] No missing documentation for new public interfaces

### 5.2 User Documentation

- [ ] User-facing changes documented
- [ ] API changes documented (if applicable)
- [ ] Breaking changes documented

### 5.3 Release Notes

- [ ] All new features listed
- [ ] Bug fixes documented
- [ ] Breaking changes highlighted
- [ ] Migration steps provided (if needed)

## Step 6: Security Review

### 6.1 Authentication & Authorization

- [ ] New endpoints secured
- [ ] Permissions correctly enforced
- [ ] No privilege escalation

### 6.2 Input Validation

- [ ] All user input validated
- [ ] Injection attacks prevented
- [ ] Sensitive data sanitized from logs

### 6.3 Data Handling

- [ ] Sensitive data encrypted
- [ ] PII handled correctly
- [ ] Data retention policies followed

## Step 7: Compile Review Findings

### 7.1 Issue List

Document each finding:
```
## Finding: [Title]
**Severity:** Critical | Important | Minor
**Category:** Structure | Regression | Coverage | Docs | Security
**Description:** What was found
**Evidence:** Where/how detected
**Impact:** What could go wrong
**Fix:** Recommended fix
```

### 7.2 Severity Classification

| Severity | Action | Blocks Ship? |
|----------|--------|-------------|
| Critical | Fix immediately | Yes |
| Important | Fix before ship | Yes |
| Minor | Fix in next release | No |

### 7.3 Review Verdict

**APPROVED** — Ready to ship
**CONDITIONAL** — Ship with known issues (documented)
**BLOCKED** — Must fix before ship

## Step 8: Address Findings

### 8.1 Fix Critical Issues

For each critical finding:
1. Fix in this session
2. Re-run relevant tests
3. Verify fix
4. Document resolution

### 8.2 Document Important Issues

For each important finding:
1. Document as known limitation
2. Add to release notes if customer-facing
3. Add to backlog for next iteration

### 8.3 Update Task Progress

Record findings and resolutions in `task-progress.md`.

## Checklist

Before marking whole-change review complete:

- [ ] All features reviewed for structural issues
- [ ] Feature interactions verified
- [ ] Integration tests adequate
- [ ] Documentation complete
- [ ] Security review passed
- [ ] No critical issues remain
- [ ] Review verdict: APPROVED or CONDITIONAL

## Integration

**Called by:** `vibeflow` router (after build complete, before ship)
**Requires:**
- `feature-list.json` (all features passing)
- `task-progress.md` (session log)
- All spec docs from `docs/plans/`
- Git diff from base branch
- System test results (if applicable)
**Produces:** Review verdict with findings
**Chains to:** `vibeflow-ship` (if approved)
