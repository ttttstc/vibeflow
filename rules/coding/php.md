---
id: php-coding-standard
title: PHP Coding Standard
languages: [php]
globs: ["**/*.php"]
layers: [runtime, tests, api]
stages: [design, build, review]
---

# PHP Coding Standard

Apply these rules to modern PHP applications and services.

## Baseline

- Follow PSR-12 formatting and standard community conventions.
- Prefer strict typing and explicit return types where supported.
- Keep framework glue thin and move business logic into testable services.
- Avoid large associative arrays as hidden schemas when dedicated objects are clearer.

## Design

- Separate controllers, services, domain logic, and persistence responsibilities.
- Keep public methods small and intention-revealing.
- Prefer constructor injection over service locator patterns.
- Model important concepts with value objects rather than raw arrays or strings.

## Data And Security

- Validate all request input at boundaries.
- Escape output in the presentation layer.
- Use parameterized queries or ORM protections correctly.
- Never concatenate untrusted SQL fragments directly.

## Errors And Logging

- Throw specific exceptions with useful context.
- Do not swallow exceptions silently.
- Keep logs structured and free of secrets.

## Testing

- Cover domain logic with fast unit tests.
- Use integration tests for framework wiring, database behavior, and HTTP contracts.
- Keep fixtures minimal and intention-revealing.

