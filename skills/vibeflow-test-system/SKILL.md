---
name: vibeflow-test-system
description: Use when all active features are passing and system-level testing must begin.
---

# System Testing for VibeFlow

Run system-level testing after build completion. Validate integration behavior across all features.

**Announce at start:** "I'm using the vibeflow-test-system skill to run system-level testing."

## Purpose

Verify the complete system works correctly:
- All features integrated together
- End-to-end scenarios work
- Non-functional requirements met
- No regressions introduced

## When to Run

- After ALL individual features pass their reviews
- After build-work completes
- Before ship stage
- Invoked by `vibeflow-build-work` (when all features pass) or `vibeflow` router

## Prerequisites

Before running this skill:
- All features marked `"status": "passing"` in `feature-list.json`
- System documentation available
- Test environment ready

## Step 1: Load System Context

### 1.1 Read Feature List

From `feature-list.json`:
- All completed features
- Feature categories
- Feature integration points

### 1.2 Read System Documentation

From `docs/plans/`:
- System architecture
- Integration points
- Data flows
- External dependencies

### 1.3 Read Requirements

From `docs/plans/*-srs.md`:
- NFR-xxx (non-functional requirements)
- System-level acceptance criteria
- Performance requirements
- Security requirements

### 1.4 Read Design Document

From `docs/plans/*-design.md`:
- System architecture
- Component interactions
- External service integrations

## Step 2: Identify System Test Scenarios

### 2.1 End-to-End Scenarios

For each major user journey:
- [ ] Complete user workflow tested
- [ ] All features in path verified
- [ ] Data flows correctly end-to-end
- [ ] Error handling works

### 2.2 Integration Points

For each integration:
- [ ] Data exchange verified
- [ ] Error handling at boundaries
- [ ] Timeout behavior correct
- [ ] Retry logic works

### 2.3 NFR Verification

For each NFR:
- [ ] Performance criteria measurable
- [ ] Security criteria testable
- [ ] Scalability criteria verifiable
- [ ] Reliability criteria demonstrable

## Step 3: Create System Test Cases

### 3.1 Define Test Cases

**Case ID:** `ST-SYS-{SEQ}`

**Categories:**

| Category | Description |
|----------|-------------|
| `e2e` | End-to-end user scenarios |
| `integration` | Component integrations |
| `performance` | NFR performance tests |
| `security` | NFR security tests |
| `regression` | Previously fixed bugs |

### 3.2 Minimum System Tests

Every system test cycle MUST include:

**End-to-end tests (at least):**
- Primary user journey test
- Secondary user journey test
- Error recovery journey test

**Integration tests (at least):**
- All external service integrations tested
- All internal component integrations tested

**NFR tests (if specified):**
- Performance test (response time < threshold)
- Load test (concurrent users)
- Security test (auth/authz verification)

## Step 4: Execute System Tests

### 4.1 Start Test Environment

1. Start all required services
2. Verify health endpoints
3. Ensure test data is available
4. Record PIDs for cleanup

### 4.2 Run End-to-End Tests

For each E2E scenario:
1. Execute the complete user journey
2. Verify all steps complete successfully
3. Verify data integrity at end
4. Record PASS/FAIL

### 4.3 Run Integration Tests

For each integration point:
1. Trigger integration
2. Verify data exchange
3. Verify error handling
4. Record PASS/FAIL

### 4.4 Run NFR Tests

For each NFR requirement:
1. Execute performance/load/security test
2. Measure against threshold
3. Record metric value
4. Record PASS/FAIL

### 4.5 Run Regression Tests

For each previously fixed bug:
1. Execute regression scenario
2. Verify fix still works
3. No new side effects
4. Record PASS/FAIL

## Step 5: Handle Failures

### 5.1 Any Test Failure

Document failure:
```
## Failure: [Test case ID]
**Type:** E2E | Integration | NFR | Regression
**Description:** What failed
**Expected:** What should happen
**Actual:** What happened
**Impact:** System impact
**Fix:** Required fix
```

### 5.2 Fix or Escalate

**For critical failures:**
1. Fix implementation
2. Re-run failed tests
3. Re-run related tests
4. Do not skip or bypass

**For NFR failures:**
1. Document the gap
2. Determine if shippable
3. Escalate to user if blocking

## Step 6: Compile Results

### 6.1 Test Summary

```
## System Test Summary

**Date**: YYYY-MM-DD
**Total tests**: N
**Passed**: N
**Failed**: N

### Results by Category
| Category | Total | Pass | Fail |
|----------|-------|------|------|
| E2E | N | N | N |
| Integration | N | N | N |
| Performance | N | N | N |
| Security | N | N | N |
| Regression | N | N | N |
```

### 6.2 Create Report

File: `docs/plans/*-st-report.md`

```markdown
# System Test Report — YYYY-MM-DD

## Summary
- **System**: [Project name]
- **Version**: [Version]
- **Date**: YYYY-MM-DD
- **Overall Status**: PASS | FAIL

## Test Results

### End-to-End Tests
[Results table]

### Integration Tests
[Results table]

### NFR Tests
[Results table with metrics]

### Regression Tests
[Results table]

## Issues Found

### Critical
[Issues that must be fixed]

### Important
[Issues that should be fixed]

### Minor
[Issues to address later]

## Sign-off

- [ ] System testing complete
- [ ] All critical issues resolved
- [ ] Ready for ship
```

### 6.3 Save Report

Write to `docs/plans/*-st-report.md`.

## Step 7: Complete Testing

### 7.1 Final Status

If ALL tests pass:
- System testing complete
- Proceed to review (vibeflow-review)

If tests fail with known issues:
- Document as conditional approval
- Proceed to review

If tests fail critically:
- Fix issues
- Re-run system tests

### 7.2 Stop Test Environment

1. Stop all test services
2. Verify cleanup
3. Record status

## Checklist

Before marking system testing complete:

- [ ] All E2E scenarios tested and passed
- [ ] All integration points tested and passed
- [ ] All NFR tests executed with results documented
- [ ] All regression tests passed
- [ ] Report saved to `docs/plans/*-st-report.md`
- [ ] Test environment stopped and cleaned up
- [ ] System testing verdict: PASS or CONDITIONAL

## Quality Gates

| Gate | Requirement |
|------|-------------|
| E2E coverage | All primary user journeys tested |
| Integration coverage | All integration points tested |
| NFR verification | All NFR requirements verified |
| Regression | All previously fixed bugs verified |

## Integration

**Called by:** `vibeflow` router (after all features pass) or `vibeflow-build-work` (Step 7)
**Requires:**
- All features `"status": "passing"`
- System documentation at `docs/plans/`
- SRS with NFRs
- Test environment ready
**Produces:**
- System test report at `docs/plans/*-st-report.md`
- Test execution evidence
**Chains to:** `vibeflow-review` (if tests pass)
