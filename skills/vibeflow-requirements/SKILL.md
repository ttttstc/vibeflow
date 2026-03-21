---
name: vibeflow-requirements
description: Use when VibeFlow needs an approved requirements specification in docs/plans.
---

# Requirements Specification for VibeFlow

Produce the project requirements document (SRS) in `docs/plans/*-srs.md`.

**Announce at start:** "I'm using the vibeflow-requirements skill to author the requirements specification."

## Purpose

Create a complete requirements specification based on:
- Think stage output
- Plan review decisions
- Workflow template requirements

## Prerequisites

Before running this skill:
- Think stage complete (`.vibeflow/think-output.md` exists)
- Plan review approved
- Scope tier determined

## Step 1: Load Input Context

### 1.1 Read Think Output

From `.vibeflow/think-output.md`:
- Problem statement
- Proposed solution
- Success criteria
- User stories (if any)

### 1.2 Read Plan Review

From `.vibeflow/plan-review.md` or `docs/plans/YYYY-MM-DD-plan-review.md`:
- Scope tier
- Risk assessment
- Modifications required
- Scope adjustments

### 1.3 Read Workflow Config

From `.vibeflow/workflow.yaml`:
- Template selected
- Stage sequence
- Quality requirements

## Step 2: Define Document Structure

### 2.1 SRS Template Structure

Based on template tier:

**Prototype:**
```
1. Introduction
   1.1 Purpose
   1.2 Scope
   1.3 Definitions
2. Overall Description
   2.1 User Personas
   2.2 Assumptions
3. Functional Requirements
   3.1 FR-xxx: [Feature]
4. Acceptance Criteria
```

**Web Standard / API Standard:**
```
1. Introduction
   1.1 Purpose
   1.2 Scope
   1.3 Definitions
   1.4 References
2. Overall Description
   2.1 User Personas
   2.2 Assumptions
   2.3 Constraints
3. Functional Requirements
   3.1 FR-xxx: [Feature]
4. Non-Functional Requirements
   4.1 NFR-xxx: [Requirement]
5. Interface Requirements
   5.1 IFR-xxx: [Interface]
6. Acceptance Criteria
```

**Enterprise:**
```
1. Introduction
   1.1 Purpose
   1.2 Scope
   1.3 Definitions
   1.4 References
2. Overall Description
   2.1 User Personas
   2.2 Assumptions
   2.3 Constraints
   2.4 Dependencies
3. Functional Requirements
   3.1 FR-xxx: [Feature]
4. Non-Functional Requirements
   4.1 NFR-xxx: [Requirement]
5. Interface Requirements
   5.1 IFR-xxx: [Interface]
6. Data Requirements
   6.1 DR-xxx: [Data]
7. Acceptance Criteria
8. Glossary
```

## Step 3: Author Introduction Section

### 3.1 Purpose

Define why this document exists:
```markdown
## 1.1 Purpose

This Software Requirements Specification (SRS) describes the functional and non-functional requirements for [project name]. This document specifies what the system must do and the constraints it must operate within.
```

### 3.2 Scope

Define what the project includes/excludes:
```markdown
## 1.2 Scope

**In scope:**
- [What is included]

**Out of scope:**
- [What is explicitly excluded]
```

### 3.3 Definitions

Define key terms:
```markdown
## 1.3 Definitions

| Term | Definition |
|------|------------|
| Term 1 | Definition |
| Term 2 | Definition |
```

### 3.4 References (if applicable)

List referenced documents:
```markdown
## 1.4 References

- [Reference 1]
- [Reference 2]
```

## Step 4: Author Overall Description

### 4.1 User Personas

Define target users:
```markdown
## 2.1 User Personas

### Persona 1: [Name]
**Role**: [What they do]
**Goals**: [What they want to achieve]
**Pain points**: [Their challenges]

### Persona 2: [Name]
...
```

### 4.2 Assumptions

Document assumptions:
```markdown
## 2.2 Assumptions

- ASM-xxx: [Assumption description]
- ASM-xxx: [Assumption description]
```

### 4.3 Constraints (if applicable)

Document constraints:
```markdown
## 2.3 Constraints

- CON-xxx: [Constraint description]
- CON-xxx: [Constraint description]
```

## Step 5: Author Functional Requirements

### 5.1 Identify Features

Based on Think output and plan review:
1. List all features
2. Group by module/area
3. Prioritize (high/medium/low)

### 5.2 Document Each Requirement

For each feature (FR-xxx):

```markdown
## 3.x FR-xxx: [Feature Name]

**Priority**: High | Medium | Low
**Module**: [Module name]

### Description
[What this feature does]

### User Story
As a [persona], I want [action], so that [benefit].

### Given/When/Then Acceptance Criteria
**Given** [precondition]
**When** [action]
**Then** [expected result]

**Given** [precondition]
**When** [action]
**Then** [expected result]
```

### 5.3 Verify Completeness

- [ ] All user needs addressed
- [ ] All features from Think output captured
- [ ] Acceptance criteria specific and testable
- [ ] Priority levels assigned

## Step 6: Author Non-Functional Requirements

### 6.1 Performance

```markdown
## 4.x NFR-xxx: Performance

**Metric**: [What is measured]
**Target**: [Numeric target]
**Measurement**: [How to verify]
```

### 6.2 Security

```markdown
## 4.x NFR-xxx: Security

**Requirement**: [What is required]
**Validation**: [How to verify]
```

### 6.3 Reliability

```markdown
## 4.x NFR-xxx: Reliability

**Requirement**: [What is required]
**Validation**: [How to verify]
```

### 6.4 Scalability

```markdown
## 4.x NFR-xxx: Scalability

**Requirement**: [What is required]
**Validation**: [How to verify]
```

## Step 7: Author Interface Requirements (if applicable)

### 7.1 User Interfaces

```markdown
## 5.x IFR-xxx: [Interface Name]

**Type**: Web | CLI | API | Mobile
**Entry point**: [URL/path]
**Description**: [What this interface provides]
```

### 7.2 External Interfaces

```markdown
## 5.x IFR-xxx: [External Service]

**Type**: REST | GraphQL | gRPC | Webhook
**Endpoint**: [URL]
**Description**: [What is exchanged]
```

### 7.3 Internal Interfaces

```markdown
## 5.x IFR-xxx: [Internal API]

**Module**: [Module name]
**Interface**: [Method/endpoint]
**Description**: [What it provides]
```

## Step 8: Author Acceptance Criteria

### 8.1 Overall Acceptance Criteria

```markdown
## 6. Acceptance Criteria

The system is considered complete when:

1. [ ] All functional requirements verified
2. [ ] All NFR metrics met
3. [ ] All interfaces operational
4. [ ] Documentation complete
```

### 8.2 Definition of Done

```markdown
## 6.x [Feature Area]

**Done when**:
- [ ] [Criterion 1]
- [ ] [Criterion 2]
```

## Step 9: Review and Finalize

### 9.1 Self-Review Checklist

- [ ] All Think output requirements captured
- [ ] All plan review modifications addressed
- [ ] Requirements are complete and consistent
- [ ] Acceptance criteria are testable
- [ ] No conflicting requirements
- [ ] Scope boundaries clear

### 9.2 Peer Review (if available)

If another human reviewer available:
- Submit for review
- Address feedback
- Finalize document

### 9.3 Save Document

File: `docs/plans/YYYY-MM-DD-<topic>-srs.md`

```bash
git add docs/plans/YYYY-MM-DD-<topic>-srs.md
git commit -m "docs: add SRS for [project name]"
```

## Checklist

Before marking requirements complete:

- [ ] Introduction section complete
- [ ] Overall description section complete
- [ ] All functional requirements documented
- [ ] All NFRs documented
- [ ] All interfaces documented (if applicable)
- [ ] Acceptance criteria defined
- [ ] Self-review passed
- [ ] Document saved to `docs/plans/*-srs.md`
- [ ] Document committed to git

## Outputs

| Output | Location | Format |
|--------|----------|--------|
| SRS Document | `docs/plans/YYYY-MM-DD-<topic>-srs.md` | Markdown |

## Integration

**Called by:** `vibeflow` router (after plan review approved)
**Requires:**
- Think output at `.vibeflow/think-output.md`
- Plan review at `.vibeflow/plan-review.md`
- Workflow config at `.vibeflow/workflow.yaml`
**Produces:**
- SRS document at `docs/plans/YYYY-MM-DD-<topic>-srs.md`
**Chains to:** `vibeflow-design` (after SRS approved)
