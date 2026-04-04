---
id: go-coding-standard
title: Go Coding Standard
languages: [go]
globs: ["**/*.go"]
layers: [runtime, tests]
stages: [design, build, review]
---

# Go Coding Standard

Apply these rules to Go services, CLIs, and libraries.

## Simplicity

- Prefer simple packages and straightforward control flow.
- Follow standard Go formatting and naming conventions.
- Do not introduce abstraction layers before they pay for themselves.
- Keep interfaces small and consumer-driven.

## Errors

- Return errors with actionable context.
- Do not panic for expected runtime failures.
- Handle errors immediately and explicitly.
- Use wrapping consistently so root causes remain visible.

## Package Design

- Organize packages by domain capability, not by generic technical buckets only.
- Keep exported surface area minimal.
- Avoid cyclic dependencies by improving boundaries.
- Keep `main` packages thin and move logic into reusable packages.

## Concurrency

- Use goroutines deliberately, not as a default.
- Own channel lifecycle clearly and document who closes what.
- Prefer context propagation for cancellation and deadlines.
- Avoid shared mutable state when message passing or ownership transfer is clearer.

## Data And APIs

- Keep structs cohesive and explicit.
- Avoid massive config structs with loosely related fields.
- Validate input at boundaries.
- Preserve backward compatibility in public JSON and RPC contracts.

## Testing

- Write table-driven tests where they improve coverage and readability.
- Keep tests deterministic and fast.
- Prefer real behavior over excessive mocking.
- Test concurrent behavior with timeouts and race-aware design.

