# Sample Priority API SRS

## Objective
Provide deterministic normalization of free-form priority labels and return an aggregate summary for downstream automation.

## Functional Requirements

### FR-001 Normalize Priority Labels
When a caller submits a work item with a free-form priority label, the system shall map it to `high`, `medium`, or `low`.

Acceptance criteria:
- Given `urgent`, when normalized, then the result is `high`.
- Given `normal`, when normalized, then the result is `medium`.
- Given an unknown label, when normalized, then the result is `medium`.

### FR-002 Summarize Work Items
When a caller submits a non-empty list of work items, the system shall return normalized items and a count summary by priority.

Acceptance criteria:
- Given a list of valid items, when summarized, then the response contains normalized items and total/high/medium/low counts.
- Given an item with a missing title, when summarized, then the system rejects the input.

## Non-Functional Requirements
- NFR-001 Testability: all core behaviors must be covered by automated tests using Python standard library tooling.
- NFR-002 Determinism: identical inputs must produce identical outputs.
- NFR-003 Simplicity: implementation shall avoid non-standard dependencies.

## Out of Scope
- HTTP transport
- Persistence
- Authentication
- UI
