---
id: kotlin-coding-standard
title: Kotlin Coding Standard
languages: [kotlin]
globs: ["**/*.kt", "**/*.kts"]
layers: [runtime, tests, ui]
stages: [design, build, review]
---

# Kotlin Coding Standard

Apply these rules to Kotlin backends, Android code, and multiplatform modules where relevant.

## Idiomatic Kotlin

- Prefer immutable values with `val` by default.
- Use null-safety features deliberately; avoid `!!` except in proven impossible states.
- Prefer data classes and sealed hierarchies for modeled state.
- Keep extension functions small and unsurprising.

## Architecture

- Keep business logic out of framework glue and UI glue.
- Separate transport, domain, and persistence concerns when they evolve differently.
- Do not hide important control flow inside DSL layers unless readability genuinely improves.
- Keep coroutine scope ownership explicit.

## Coroutines

- Avoid blocking calls inside suspending code.
- Propagate cancellation correctly.
- Do not launch unmanaged background work from arbitrary layers.
- Prefer structured concurrency over ad hoc jobs.

## Errors And Validation

- Validate boundary inputs explicitly.
- Use meaningful exceptions or sealed result types at boundaries.
- Include enough diagnostic context to debug failures safely.

## Testing

- Keep unit tests fast and readable.
- Test coroutine cancellation, timeout, and dispatcher-sensitive behavior where relevant.
- Avoid over-mocking core business rules.

