---
id: java-coding-standard
title: Java Coding Standard
languages: [java]
globs: ["**/*.java"]
layers: [runtime, tests, api]
stages: [design, build, review]
checks: [java-no-field-injection]
---

# Java Coding Standard

Apply these rules to Java applications, libraries, and services.

## Core Design

- Prefer clear object models and explicit dependencies over annotation-heavy magic.
- Use constructor injection by default.
- Keep domain logic out of controllers and transport DTOs.
- Separate API models, domain models, and persistence models when their responsibilities differ.

## Types And Nullability

- Model absence explicitly and minimize nullable values.
- Do not return `null` collections; return empty collections.
- Avoid using `Optional` for fields, serialization payloads, or method parameters.
- Use enums and value objects to encode constrained states instead of raw strings.

## Classes And Methods

- Keep classes cohesive and focused on one responsibility.
- Keep methods short enough to read top-to-bottom without scrolling through unrelated branches.
- Prefer descriptive method names over comment-heavy code.
- Do not expose mutable internal state from getters.

## Collections And Streams

- Prefer simple loops when they are clearer than stream pipelines.
- Do not use streams for control flow with hidden side effects.
- Be careful with parallel streams; use them only with measured benefit.
- Preserve collection ordering intentionally rather than by accident.

## Exceptions And Logging

- Throw domain-meaningful exceptions at boundaries.
- Do not catch `Exception` unless translating it at an application boundary.
- Include identifiers and business context in logs.
- Never log secrets or raw sensitive payloads.

## Persistence And Transactions

- Keep transaction boundaries explicit and small.
- Do not hide expensive queries behind innocent-looking accessors.
- Avoid N+1 query patterns.
- Keep repository methods intention-revealing and bounded to aggregate needs.

## Framework Use

- Keep framework annotations at edges where possible.
- Avoid static service locators and global mutable state.
- Prefer explicit configuration over convention chains that are hard to debug.

## Testing

- Favor unit tests for domain logic and focused integration tests for framework wiring.
- Test serialization, transaction behavior, and validation at boundaries.
- Use test data builders for complex objects instead of unreadable constructor calls.

