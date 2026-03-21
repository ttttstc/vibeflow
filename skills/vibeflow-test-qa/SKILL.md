---
name: vibeflow-test-qa
description: Use when UI validation is required after system testing.
---

# QA Testing for VibeFlow

Run browser-oriented QA validation after system testing. Generate QA report.

**Announce at start:** "I'm using the vibeflow-test-qa skill to run QA validation."

## Purpose

Perform human-oriented QA validation for UI-bearing features:
- Browser-based testing
- Visual verification
- User experience validation
- Accessibility checks

## When to Run

- After system testing (vibeflow-test-system)
- For UI-bearing projects (features with `"ui": true`)
- Before ship stage
- Invoked by `vibeflow` router when UI validation required

## Prerequisites

Before running this skill:
- UI features implemented
- System testing passed
- Browser automation tools available
- QA environment ready

## Step 1: Load QA Context

### 1.1 Read Feature List

From `feature-list.json`:
- All features with `"ui": true`
- UI entry points
- UI interaction requirements

### 1.2 Read UCD

From `docs/plans/*-ucd.md`:
- Design specifications
- Visual requirements
- Component behaviors

### 1.3 Read Test Case Documents

From `docs/test-cases/feature-{id}-{slug}.md`:
- UI test case results
- Known issues

### 1.4 Read System Test Report

From `docs/plans/*-st-report.md`:
- Overall system status
- UI-related findings

## Step 2: Define QA Test Cases

### 2.1 Visual QA Tests

For each UI feature:
- [ ] Page renders correctly
- [ ] Colors match design spec
- [ ] Typography matches design spec
- [ ] Spacing consistent with design
- [ ] Images load correctly
- [ ] Responsive behavior correct

### 2.2 Interaction QA Tests

For each UI feature:
- [ ] Button clicks work
- [ ] Form submissions work
- [ ] Navigation works
- [ ] State changes correct
- [ ] Animations smooth
- [ ] Loading states work

### 2.3 Accessibility QA Tests

For each UI feature:
- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] Color contrast adequate
- [ ] Screen reader compatible
- [ ] ARIA labels present
- [ ] Skip links work (if applicable)

### 2.4 Cross-browser QA Tests

For each UI feature:
- [ ] Chrome works
- [ ] Firefox works (if supported)
- [ ] Safari works (if supported)
- [ ] Mobile browsers work (if applicable)

## Step 3: Execute QA Tests

### 3.1 Start Browser Environment

1. Start application in browser-capable environment
2. Verify application loads
3. Record browser version
4. Prepare screenshot tools

### 3.2 Execute Visual QA

For each UI feature:
1. Navigate to UI entry point
2. Take snapshot
3. Compare against design spec
4. Document any visual discrepancies

### 3.3 Execute Interaction QA

For each UI feature:
1. Execute critical user interactions
2. Verify response
3. Check error handling
4. Document any issues

### 3.4 Execute Accessibility QA

For each UI feature:
1. Run keyboard-only navigation
2. Run screen reader test (if tools available)
3. Check color contrast ratios
4. Document accessibility issues

### 3.5 Execute Cross-browser QA

For each UI feature:
1. Test in primary browser
2. Test in secondary browsers
3. Document browser-specific issues

## Step 4: Document Findings

### 4.1 QA Issue Format

```
## QA-XXX: [Issue Title]
**Feature**: [Feature name]
**Severity**: Critical | Important | Minor
**Category**: Visual | Interaction | Accessibility | Cross-browser
**Description**: Detailed description
**Expected**: What should happen
**Actual**: What is happening
**Evidence**: Screenshots/Steps to reproduce
**Fix**: Recommended fix
```

### 4.2 Issue Categories

| Severity | Definition | Action |
|----------|------------|--------|
| Critical | Blocks usage | Fix immediately |
| Important | Degrades experience | Fix before ship |
| Minor | Cosmetic issue | Fix in next release |

## Step 5: Fix Issues

### 5.1 Fix Critical Issues

For each critical QA issue:
1. Fix implementation
2. Re-test the fix
3. Verify issue resolved
4. Document resolution

### 5.2 Document Unfixed Issues

For issues not fixed:
1. Document as known limitation
2. Assess impact on ship decision
3. Update issue with explanation

## Step 6: Generate QA Report

### 6.1 Create QA Report

File: `.vibeflow/qa-report.md`

```markdown
# QA Report — YYYY-MM-DD

## Summary
- **Project**: [Project name]
- **Version**: [Version]
- **Date**: YYYY-MM-DD
- **QA performed by**: [Name/tool]
- **Overall Status**: PASS | CONDITIONAL | FAIL

## Features Tested

| Feature ID | Feature | Status |
|------------|---------|--------|
| 1 | Feature name | Pass/Fail |
| 2 | Feature name | Pass/Fail |

## Visual QA Results

| Feature | Page | Colors | Typography | Spacing | Images |
|---------|------|--------|-----------|---------|--------|
| 1 | Pass | Pass | Pass | Fail | Pass |

## Interaction QA Results

| Feature | Buttons | Forms | Navigation | States |
|---------|---------|-------|------------|--------|
| 1 | Pass | Pass | Pass | Pass |

## Accessibility QA Results

| Feature | Keyboard | Focus | Contrast | ARIA |
|---------|----------|-------|----------|------|
| 1 | Pass | Pass | Fail | Pass |

## Cross-browser QA Results

| Feature | Chrome | Firefox | Safari | Mobile |
|---------|--------|---------|--------|--------|
| 1 | Pass | N/A | N/A | Pass |

## Issues Found

### Critical
[Issues]

### Important
[Issues]

### Minor
[Issues]

## Resolutions

| Issue | Resolution | Verified |
|-------|------------|----------|
| QA-001 | Fixed | Yes |
| QA-002 | Known limitation | No |

## Sign-off

- [ ] All critical issues resolved
- [ ] All important issues documented
- [ ] QA report complete
- [ ] Ready for ship
```

### 6.2 Save QA Report

Write to `.vibeflow/qa-report.md`.

## Step 7: Complete QA

### 7.1 Final Status

If ALL QA passes:
- QA validation complete
- Ready for ship

If critical issues fixed but important remain:
- Document as conditional
- Ready for ship with known issues

If critical issues remain:
- Cannot ship
- Fix issues first

### 7.2 Update Task Progress

In `task-progress.md`:
- QA status
- Issues found and resolved
- Any known limitations

## Checklist

Before marking QA complete:

- [ ] All UI features tested visually
- [ ] All UI interactions tested
- [ ] Accessibility tests executed
- [ ] Cross-browser tests executed (if applicable)
- [ ] Critical issues fixed
- [ ] Important issues documented
- [ ] QA report saved to `.vibeflow/qa-report.md`
- [ ] QA verdict: PASS or CONDITIONAL

## Integration

**Called by:** `vibeflow` router (after system testing, when UI features exist)
**Requires:**
- All UI features implemented
- System test report
- UCD design spec
- Browser automation tools
**Produces:**
- QA report at `.vibeflow/qa-report.md`
- QA findings with resolutions
**Chains to:** `vibeflow-review` or `vibeflow-ship`
