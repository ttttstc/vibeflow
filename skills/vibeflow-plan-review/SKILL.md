---
name: vibeflow-plan-review
description: Use during Plan to run the executive scope review before specs are authored.
---

# Plan Review for VibeFlow

Perform the VibeFlow plan review pass before requirements and design authoring continue.

**Announce at start:** "I'm using the vibeflow-plan-review skill to run the plan review."

## Purpose

Before authoring requirements and design, validate:
- Problem framing is correct
- Scope tier is appropriate
- Major risks are identified
- Recommended path forward is sound

## When to Run

- After Think stage (vibeflow-think)
- Before Requirements stage (vibeflow-requirements)
- Invoked by `vibeflow` router

## Inputs

- `VIBEFLOW-DESIGN.md` (if exists)
- `.vibeflow/think-output.md` — Think stage output
- `.vibeflow/workflow.yaml` — Selected template config (if exists)

## Step 1: Load Review Context

### 1.1 Read Think Output

From `.vibeflow/think-output.md`:
- Problem statement
- Proposed solution
- Success criteria
- Initial scope assessment

### 1.2 Read Workflow Config

From `.vibeflow/workflow.yaml`:
- Selected template
- Stage sequence
- Enabled features

### 1.3 Read Design Doc (if exists)

From `VIBEFLOW-DESIGN.md` or `docs/plans/*-design.md`:
- Previous design work
- Architecture decisions

## Step 2: Challenge Problem Framing

### 2.1 Problem Validation

Review the problem statement:
- [ ] Problem is clearly stated
- [ ] Problem is actually the root cause
- [ ] Problem is worth solving
- [ ] Problem is scoped appropriately

### 2.2 Solution Validation

Review the proposed solution:
- [ ] Solution addresses root cause
- [ ] Solution is technically feasible
- [ ] Solution is cost-effective
- [ ] Alternative solutions considered

### 2.3 Success Criteria Validation

Review success criteria:
- [ ] Criteria are measurable
- [ ] Criteria are achievable
- [ ] Criteria validate problem solved
- [ ] Criteria don't miss important outcomes

## Step 3: Scope Tier Review

### 3.1 Assess Scope Tier

Based on the problem and solution, recommend scope tier:

| Tier | Characteristics | When |
|------|-----------------|------|
| **Prototype** | Quick validation, minimal features | Exploratory, learning |
| **Web Standard** | Full web app, no complex integrations | Standard web product |
| **API Standard** | Backend API, may have multiple clients | API-first product |
| **Enterprise** | Complex integrations, high reliability | Mission-critical |

### 3.2 Confirm Tier Appropriateness

- [ ] Template matches scope complexity
- [ ] Workflow steps appropriate for tier
- [ ] Quality gates appropriate for tier

### 3.3 Document Tier Decision

```markdown
## Scope Tier Recommendation

**Recommended tier**: [Tier name]
**Rationale**: Why this tier is appropriate
**Alternative considered**: [Tier name] — why not chosen
```

## Step 4: Risk Assessment

### 4.1 Product Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Risk 1 | High/Medium/Low | High/Medium/Low | Mitigation strategy |

### 4.2 Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Risk 1 | High/Medium/Low | High/Medium/Low | Mitigation strategy |

### 4.3 Delivery Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Risk 1 | High/Medium/Low | High/Medium/Low | Mitigation strategy |

## Step 5: Review Recommendations

### 5.1 Proceed to Requirements

**Recommended** — Problem framed correctly, risks manageable

**Conditional** — Proceed with modifications:
- [ ] Modification 1
- [ ] Modification 2

**Not Recommended** — Significant issues:
- [ ] Issue 1
- [ ] Issue 2

### 5.2 Scope Adjustments

If scope adjustments needed:
```
## Scope Adjustments

**Expand**:
- [Item to add to scope]

**Reduce**:
- [Item to remove from scope]

**Defer**:
- [Item to defer to later iteration]
```

## Step 6: Document Review

### 6.1 Create Review Notes

Save to `.vibeflow/plan-review.md` or `docs/plans/YYYY-MM-DD-plan-review.md`:

```markdown
# Plan Review — YYYY-MM-DD

## Summary
- **Review date**: YYYY-MM-DD
- **Think output**: `.vibeflow/think-output.md`
- **Workflow**: [template] — [stage sequence]

## Problem Framing
[Assessment of problem statement]

## Solution Validation
[Assessment of proposed solution]

## Scope Tier
**Recommended**: [Tier]
**Rationale**: [Why appropriate]

## Risk Assessment

### Product Risks
[Risks table]

### Technical Risks
[Risks table]

### Delivery Risks
[Risks table]

## Recommendations

**Decision**: Proceed | Conditional | Not Recommended

### Modifications (if conditional)
- [Modification 1]
- [Modification 2]

### Scope Adjustments (if any)
[Expand/Reduce/Defer items]

## Next Steps
- [ ] Proceed to Requirements (vibeflow-requirements)
- [ ] Address modifications before proceeding
```

### 6.2 Save Review Notes

Write review notes to appropriate location.

## Checklist

Before completing plan review:

- [ ] Problem framing validated
- [ ] Solution approach validated
- [ ] Success criteria validated
- [ ] Scope tier recommended
- [ ] Product risks identified
- [ ] Technical risks identified
- [ ] Delivery risks identified
- [ ] Recommendation documented
- [ ] Review notes saved
- [ ] Decision: Proceed / Conditional / Not Recommended

## Expected Output

| Output | Location | Purpose |
|--------|----------|---------|
| Scope decision | Review notes | Expand / Hold / Reduce |
| Review notes | `.vibeflow/plan-review.md` or `docs/plans/` | Decision documentation |
| Risk assessment | Review notes | Risk awareness |
| Recommendation | Review notes | Go/No-go guidance |

## Integration

**Called by:** `vibeflow` router (after Think, before Requirements)
**Requires:**
- Think output at `.vibeflow/think-output.md`
- Workflow config at `.vibeflow/workflow.yaml` (if exists)
- Design doc (if exists)
**Produces:**
- Review notes with scope decision
- Risk assessment
- Go/No-go recommendation
**Chains to:** `vibeflow-requirements` (if approved)
