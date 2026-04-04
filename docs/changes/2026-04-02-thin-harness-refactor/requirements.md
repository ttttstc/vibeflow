# Requirements

## Functional Requirements

### FR-001 Preserve the current workflow
The refactor must preserve the existing phase sequence starting from `spark` through `reflect`, including the current build auto-continue behavior.

### FR-002 Preserve existing skills
The refactor must preserve the current functional skills and keep them as the main workflow surface for the agent.

### FR-003 Preserve project rules
The refactor must preserve `rules/` loading, scoping, design-stage documentation, and executable rule checks.

### FR-004 Make artifacts authoritative for build
`build-work` must be able to derive its execution input from repository artifacts, especially:

- `design.md`
- `tasks.md`
- `feature-list.json`
- `rules/`

### FR-005 Make packets optional
Packets may still be generated for caching, debugging, or backward compatibility, but missing or stale packets must not block normal build/review flow when the authoritative artifacts are valid.

### FR-006 Review real delivery evidence
`review` must validate:

- design/spec contract consistency
- applicable rules
- implementation evidence

It must not fail solely because a legacy packet is missing or no longer matches the primary artifact contract.

### FR-007 Keep deterministic validation
Deterministic checks must remain script-backed for:

- phase detection
- design contract extraction
- rules parsing and executable checks
- work config generation
- test and readiness checks

## Non-Functional Requirements

### NFR-001 Lower coupling
The main flow must require fewer synchronized runtime layers than before.

### NFR-002 Recoverability
A new agent should be able to resume by reading artifacts and phase state without needing packet history.

### NFR-003 Backward compatibility
Existing packet directories and result files may remain for compatibility, but the primary workflow must no longer depend on them.

### NFR-004 Regression safety
The repository test suite must be updated so the refactor is covered by automated regression checks.
