# Context

## Problem

VibeFlow currently preserves the intended phase flow well, but parts of the implementation lean on a thick external harness:

- `packet` files are treated as the primary execution input for `build-work`
- review validates packet propagation, not only delivery correctness
- phase readiness still partially depends on packet side effects
- `autopilot` and runtime bookkeeping own workflow details that should live in artifacts and skills

This makes the chain harder to reason about, more brittle to recover, and more expensive to evolve.

## Direction

Keep the current VibeFlow phase flow unchanged:

`spark -> requirements -> design -> build-init -> build-work -> review -> test-system -> test-qa -> ship -> reflect`

Keep:

- current phase names and order
- current skill system
- `rules/` custom rules
- auto-continue after `build-init`

Refactor:

- make repository artifacts the primary source of truth
- make skills own workflow reasoning
- keep scripts for deterministic parsing, validation, and execution
- downgrade packets to optional cached handoff artifacts instead of primary truth

## Success Criteria

- `build-work` can execute from `feature-list.json + design/tasks/rules` even when packets are absent
- `review` validates design/rules/evidence directly, not packet propagation
- `build-init` readiness no longer depends on packet generation
- existing phases and user-facing flow remain intact
- sample autopilot flow and regression tests still pass
