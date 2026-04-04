---
id: typescript-coding-standard
title: TypeScript Coding Standard
languages: [typescript, ts]
globs: ["**/*.ts", "**/*.tsx"]
layers: [runtime, ui, tests]
stages: [design, build, review]
checks: [ts-no-explicit-any]
---

# TypeScript Coding Standard

Apply these rules to TypeScript apps, services, libraries, and tooling.

## Types First

- Prefer precise types over `any`, wide unions, or unchecked casts.
- Use `unknown` instead of `any` when data is untrusted.
- Narrow types close to the boundary where data is validated.
- Prefer discriminated unions for stateful workflows.
- Export stable public types intentionally instead of leaking internal implementation types.

## APIs And State

- Keep function signatures small and explicit.
- Prefer immutable updates for shared state.
- Avoid boolean parameter traps; use object parameters or separate functions when meaning is ambiguous.
- Do not overload one type to represent many unrelated shapes.

## Runtime Safety

- Validate external input at runtime even if static types exist.
- Do not assume API payloads match compile-time declarations.
- Handle `null` and `undefined` deliberately.
- Make error cases part of the design instead of throwing generic strings.

## Module Structure

- Keep modules organized by domain, not by incidental technical labels alone.
- Avoid barrels that create import cycles or unclear ownership.
- Limit default exports; prefer named exports for maintainability.
- Keep top-level side effects rare and obvious.

## Async

- Always await or intentionally handle promises.
- Use `Promise.all` only when operations are independent and failure semantics are acceptable.
- Propagate cancellation and timeout behavior where the platform supports it.

## Frontend Guidance

- Keep components focused and split view logic from data orchestration when complexity grows.
- Derive UI state where possible instead of duplicating it.
- Do not bury business rules in JSX branches or event handlers.
- Prefer accessible semantics before custom interaction code.

## Testing

- Test behavior and contracts, not implementation trivia.
- Cover runtime validation, async failure paths, and state transitions.
- Avoid snapshot sprawl; use snapshots only when they capture stable intent.

