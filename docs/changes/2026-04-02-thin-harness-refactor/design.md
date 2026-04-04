# Design

## 1. Summary

This refactor keeps the current VibeFlow phase topology and skills, but shifts the execution model from:

- runtime-first
- packet-centric
- propagation-validated

to:

- artifact-first
- skill-driven
- evidence-validated

## 2. Source Of Truth

### 2.1 Phase truth

The current phase continues to come from:

- `.vibeflow/state.json`
- required artifacts
- required checkpoints
- policy checks

### 2.2 Build truth

The build phase becomes authoritative from:

- `feature-list.json`
- `docs/changes/<change-id>/design.md`
- `docs/changes/<change-id>/tasks.md`
- `rules/`

Packets remain optional cached handoff artifacts.

### 2.3 Review truth

Review becomes authoritative from:

- feature contracts stored in `feature-list.json`
- applicable project rules
- build reports
- implementation result files
- review/system-test artifacts

## 3. Architecture Changes

### 3.1 Packet layer becomes optional

`scripts/vibeflow_packets.py` still normalizes features and can still write packet files, but:

- build execution no longer fails when a packet is absent
- batch scope selection prefers feature artifact scope first
- review no longer treats packet propagation as the main compliance signal

### 3.2 Build execution uses normalized feature artifacts

`build-work` derives execution input from normalized feature contracts built from:

- feature payload
- design contracts
- rules selection

If a persisted packet exists, it can still be used as a cached view, but it is no longer required.

### 3.3 Review validates contracts, rules, and evidence

Review now checks:

- whether feature artifacts materialize the applicable rules
- whether result/build evidence exists and passes
- whether executable rule checks pass on implemented files

Legacy packet drift is downgraded from a blocking truth source to compatibility-only behavior.

### 3.4 Build-init readiness no longer depends on packets

Phase detection and invariant validation stop using packet existence as a required build-init readiness signal.

Build-init is considered complete when the authoritative build artifacts exist, especially:

- `feature-list.json`
- active features
- downstream build-config/work markers as applicable

## 4. Skill Contract Updates

### 4.1 build-init

The skill continues to generate feature-list and may generate packet cache files, but the canonical handoff is:

- normalized features in `feature-list.json`
- project guides
- design/tasks/rules references

### 4.2 build-work

The skill now treats packets as optional cached handoff files. Primary input becomes:

- `feature-list.json`
- `design.md`
- `tasks.md`
- `rules/`

### 4.3 review

The skill now focuses on:

- spec compliance
- code quality
- executable rule checks
- delivery evidence

and no longer centers packet propagation as a review goal.

## 5. Risks

### 5.1 Existing packet-oriented tests

Some tests currently assert packet-centric behavior. These need to be updated to keep compatibility coverage while shifting the primary truth model.

### 5.2 Documentation drift

README, usage, architecture, and skill docs must be updated together, otherwise the refactor will remain conceptually inconsistent.

## 6. Validation Plan

- update unit and integration tests for packet-optional flow
- keep packet generation coverage
- add build/review tests that succeed without packets
- run the full repository test suite
