---
name: vibeflow-design
description: Use when VibeFlow needs a technical design document before initialization.
---

# Technical Design for VibeFlow

Produce the technical design document in `docs/plans/*-design.md`.

**Announce at start:** "I'm using the vibeflow-design skill to author the technical design."

## Purpose

Create a complete technical design based on:
- Approved requirements specification (SRS)
- Plan review scope tier
- Technical constraints and decisions

## Prerequisites

Before running this skill:
- Requirements stage complete (SRS exists at `docs/plans/*-srs.md`)
- Plan review approved

## Step 1: Load Input Context

### 1.1 Read Requirements Document

From `docs/plans/*-srs.md`:
- All functional requirements (FR-xxx)
- All non-functional requirements (NFR-xxx)
- All interface requirements (IFR-xxx)
- Acceptance criteria

### 1.2 Read Plan Review

From `.vibeflow/plan-review.md` or `docs/plans/YYYY-MM-DD-plan-review.md`:
- Scope tier
- Risk assessment
- Modifications

### 1.3 Read Workflow Config

From `.vibeflow/workflow.yaml`:
- Template selected
- Stage sequence
- Enabled features

## Step 2: Define Architecture

### 2.1 Architecture Overview

```markdown
## 1. Architecture Overview

### High-Level Architecture
[Architecture diagram or description]

### Design Principles
- [Principle 1]
- [Principle 2]
```

### 2.2 Technology Stack

Based on template tier and requirements:

**For Web Standard:**
```markdown
## 1.x Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Frontend | React/Vue/Svelte | x.y | UI framework |
| Backend | Node/Python/Go | x.y | API server |
| Database | PostgreSQL/MongoDB | x.y | Data store |
| ... | ... | ... | ... |
```

**For API Standard:**
```markdown
## 1.x Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| API | Node/Python/Go | x.y | REST API |
| Database | PostgreSQL/MongoDB | x.y | Data store |
| Cache | Redis/Memcached | x.y | Caching |
```

**For Enterprise:**
- More detailed technology decisions
- Integration middleware
- Enterprise messaging
- Security infrastructure

### 2.3 Component Architecture

For each major component:
```markdown
## 1.x [Component Name]

**Responsibility**: [What this component does]
**Dependencies**: [What it depends on]
**Public API**: [Key interfaces]
```

## Step 3: Design Data Model

### 3.1 Entity Relationship

```markdown
## 2. Data Model

### Entity Relationship Diagram
[ER diagram or description]

### Core Entities
```

### 3.2 Entity Definitions

For each entity:
```markdown
### [Entity Name]

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Primary key |
| name | string | NOT NULL | Entity name |
| ... | ... | ... | ... |
```

### 3.3 Database Schema (if applicable)

```markdown
## 2.x Database Schema

### [Table Name]
```sql
CREATE TABLE [table_name] (
  ...
);
```
```

## Step 4: Design API

### 4.1 API Overview

```markdown
## 3. API Design

### API Style
REST | GraphQL | gRPC

### Base URL
`/api/v1`
```

### 4.2 Endpoint Definitions

For each endpoint:
```markdown
### [METHOD] /api/v1/[resource]

**Description**: [What this endpoint does]

**Request**:
```json
{
  "field": "type — description"
}
```

**Response** (200):
```json
{
  "field": "type — description"
}
```

**Error Responses**:
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
```

### 4.3 Authentication (if applicable)

```markdown
## 3.x Authentication

**Method**: JWT | OAuth | API Key

**Flow**:
[Authentication flow description]
```

## Step 5: Design Module Structure

### 5.1 Directory Structure

```markdown
## 4. Module Structure

```
project/
├── src/
│   ├── [module1]/
│   │   ├── index.ts
│   │   ├── [module1].ts
│   │   └── types.ts
│   ├── [module2]/
│   └── ...
├── tests/
├── docs/
└── ...
```
```

### 5.2 Module Responsibilities

For each module:
```markdown
## 4.x [Module Name]

**Location**: `src/[module]/`
**Responsibility**: [What this module does]
**Public API**:
- `functionName(params): returnType` — [description]

**Dependencies**:
- [Other modules this depends on]
```

## Step 6: Design Security

### 6.1 Authentication & Authorization

```markdown
## 5. Security Design

### Authentication
[How users authenticate]

### Authorization
[How permissions are enforced]

### Data Protection
[How sensitive data is protected]
```

### 6.2 Security Controls

```markdown
### Input Validation
[How input is validated]

### Output Encoding
[How output is encoded]

### Audit Logging
[What is logged]
```

## Step 7: Design Testing Strategy

### 7.1 Test Types

```markdown
## 6. Testing Strategy

### Unit Tests
**Framework**: [Jest/Pytest/JUnit]
**Coverage target**: [X%]

### Integration Tests
**Scope**: [What is tested]
**Environment**: [How environment is set up]

### End-to-End Tests
**Framework**: [Playwright/Cypress]
**Scope**: [What is tested]
```

### 7.2 Quality Gates

```markdown
### Quality Gates

| Gate | Threshold |
|------|-----------|
| Line coverage | 80% |
| Branch coverage | 70% |
| Mutation score | 70% |
```

## Step 8: Design Deployment

### 8.1 Deployment Architecture

```markdown
## 7. Deployment Design

### Infrastructure
[Deployment infrastructure description]

### Configuration
[Environment configuration]
```

### 8.2 Environment Configuration

```markdown
### [Environment Name]
**URL**: [URL]
**Purpose**: [Purpose]
**Configuration**: [Key config values]
```

## Step 9: Document Design Decisions

### 9.1 Key Decisions

```markdown
## 8. Design Decisions

### DEC-xxx: [Title]
**Date**: YYYY-MM-DD
**Status**: Accepted

**Context**:
[Problem or decision required]

**Decision**:
[What was decided]

**Consequences**:
[What this affects]
```

## Step 10: Create Feature Designs

### 10.1 Feature Overview

For each FR requirement:
```markdown
## 9.x FR-xxx: [Feature Name]

### Overview
[What this feature does]

### Class Diagram
[UML class diagram if applicable]

### Sequence Diagram
[Sequence diagram for key interactions]

### Data Flow
[Data flow description]
```

### 10.2 Interface Contract

For each feature interface:
```markdown
### Interface Contract

| Method | Parameters | Return | Description |
|--------|------------|--------|-------------|
| methodName | Type | Type | Description |
```

### 10.3 Edge Cases

```markdown
### Edge Cases
- [Edge case 1]
- [Edge case 2]
```

## Step 11: Review and Finalize

### 11.1 Self-Review Checklist

- [ ] Architecture supports all requirements
- [ ] Technology stack appropriate
- [ ] Data model complete
- [ ] API design covers all interfaces
- [ ] Security requirements addressed
- [ ] Testing strategy defined
- [ ] Deployment architecture defined
- [ ] Design decisions documented

### 11.2 Alignment Check

- [ ] All FRs have corresponding design
- [ ] All NFRs addressed
- [ ] All interfaces designed
- [ ] No conflicting decisions

### 11.3 Save Document

File: `docs/plans/YYYY-MM-DD-<topic>-design.md`

```bash
git add docs/plans/YYYY-MM-DD-<topic>-design.md
git commit -m "docs: add technical design for [project name]"
```

## Checklist

Before marking design complete:

- [ ] Architecture overview complete
- [ ] Technology stack defined
- [ ] Data model designed
- [ ] API endpoints designed
- [ ] Module structure defined
- [ ] Security designed
- [ ] Testing strategy defined
- [ ] Deployment architecture defined
- [ ] Design decisions documented
- [ ] All FRs have feature designs
- [ ] Self-review passed
- [ ] Document saved to `docs/plans/*-design.md`
- [ ] Document committed to git

## Outputs

| Output | Location | Format |
|--------|----------|--------|
| Design Document | `docs/plans/YYYY-MM-DD-<topic>-design.md` | Markdown |

## Integration

**Called by:** `vibeflow` router (after requirements approved)
**Requires:**
- SRS at `docs/plans/*-srs.md`
- Plan review at `.vibeflow/plan-review.md`
- Workflow config at `.vibeflow/workflow.yaml`
**Produces:**
- Design document at `docs/plans/YYYY-MM-DD-<topic>-design.md`
**Chains to:** `vibeflow-build-init` (after design approved)
