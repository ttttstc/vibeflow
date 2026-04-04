---
id: csharp-coding-standard
title: CSharp Coding Standard
languages: [csharp, c#, dotnet]
globs: ["**/*.cs"]
layers: [runtime, tests, api]
stages: [design, build, review]
---

# CSharp Coding Standard

Apply these rules to C# applications, services, libraries, and tools.

## Design

- Prefer clear, composable services over framework-driven hidden behavior.
- Use dependency injection explicitly and keep composition at the edge.
- Keep domain logic out of controllers, handlers, and EF models where possible.
- Model business concepts with strong types instead of raw strings or integers.

## Nullability And Collections

- Enable and respect nullable reference types.
- Do not return null collections.
- Validate external input before it enters core logic.
- Keep DTOs and domain models separate when their evolution differs.

## Async

- Use async end-to-end when I/O is asynchronous.
- Do not block on tasks with `.Result` or `.Wait()`.
- Name asynchronous methods with the `Async` suffix.
- Propagate cancellation tokens at application boundaries.

## Exceptions And Logging

- Throw exceptions for exceptional cases, not normal branching.
- Catch exceptions at boundaries where recovery, translation, or logging is meaningful.
- Include correlation identifiers and useful context in logs.
- Never log secrets or sensitive payloads.

## Persistence

- Keep query intent explicit and avoid accidental client-side evaluation.
- Prevent N+1 access patterns.
- Use transactions deliberately around multi-step consistency changes.

## Testing

- Favor unit tests for domain logic and focused integration tests for infrastructure.
- Test serialization, validation, and authorization boundaries.
- Use builders or fixtures that keep test intent obvious.

