---
id: ruby-coding-standard
title: Ruby Coding Standard
languages: [ruby]
globs: ["**/*.rb"]
layers: [runtime, tests]
stages: [design, build, review]
---

# Ruby Coding Standard

Apply these rules to Ruby applications, scripts, and services.

## Style And Design

- Follow standard Ruby style and keep code expressive rather than clever.
- Prefer small objects with clear responsibilities.
- Keep metaprogramming rare, obvious, and justified.
- Avoid service classes that become generic dumping grounds.

## Data And Boundaries

- Normalize external input at boundaries.
- Use keyword arguments where they improve clarity.
- Keep domain invariants close to the objects that own them.
- Avoid passing large option hashes through many layers unchecked.

## Errors

- Raise meaningful exceptions with context.
- Do not rescue broadly unless translating or handling at a boundary.
- Never silently ignore failures that affect correctness.

## Framework Use

- Keep Rails or framework callbacks understandable and minimal.
- Prefer explicit workflow code over callback chains that hide side effects.
- Separate persistence concerns from business rules when complexity grows.

## Testing

- Favor fast unit tests and focused request or integration tests.
- Keep factories lean and avoid creating excessive unrelated records.
- Test validations, authorization, and background job behavior explicitly.

