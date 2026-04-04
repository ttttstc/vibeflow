---
id: rust-coding-standard
title: Rust Coding Standard
languages: [rust]
globs: ["**/*.rs"]
layers: [runtime, tests]
stages: [design, build, review]
---

# Rust Coding Standard

Apply these rules to Rust libraries, services, CLIs, and async systems.

## Ownership And API Design

- Use ownership and borrowing to make invariants explicit.
- Prefer domain types over primitive obsession.
- Keep public APIs small, consistent, and hard to misuse.
- Reach for traits when they model stable behavior, not just to imitate inheritance.

## Error Handling

- Return rich error types for library and service boundaries.
- Use `Result` for recoverable failures and reserve `panic!` for impossible states.
- Add context when converting lower-level errors.
- Do not hide errors behind `Option` unless absence is the full story.

## Concurrency And Async

- Use async only when the surrounding stack benefits from it.
- Avoid holding locks across await points.
- Prefer message passing or ownership transfer to broad shared mutability.
- Make cancellation and shutdown behavior explicit.

## Modules And Traits

- Keep modules focused and names intention-revealing.
- Limit trait surface area to what callers actually need.
- Avoid macro-heavy APIs when plain Rust is clearer.
- Use `pub` sparingly.

## Performance

- Measure before optimizing.
- Avoid unnecessary cloning in hot paths.
- Be explicit about allocation-sensitive code.
- Prefer clarity first unless profiling proves a bottleneck.

## Testing

- Test success paths, edge cases, and error contracts.
- Keep unit tests near the code when it helps readability.
- Use integration tests for crate boundaries and real workflows.

