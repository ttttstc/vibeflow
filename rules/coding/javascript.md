---
id: javascript-coding-standard
title: JavaScript Coding Standard
languages: [javascript, js]
globs: ["**/*.js", "**/*.jsx", "**/*.mjs", "**/*.cjs"]
layers: [runtime, ui, tests]
stages: [design, build, review]
checks: [js-no-throw-string]
---

# JavaScript Coding Standard

Apply these rules to JavaScript codebases that do not use TypeScript everywhere.

## Language Discipline

- Prefer modern ECMAScript syntax that improves clarity.
- Keep code strict, explicit, and lint-clean.
- Avoid clever prototype manipulation or metaprogramming unless the project truly depends on it.
- Use JSDoc on public APIs and complex modules when static types are unavailable.

## Data Safety

- Validate all external input at runtime.
- Normalize object shapes at boundaries instead of passing loose payloads through the system.
- Handle `null`, `undefined`, and empty values explicitly.
- Avoid mutating objects received from callers unless the contract clearly allows it.

## Functions And Modules

- Keep functions small and intention-revealing.
- Prefer pure helpers for business logic.
- Avoid large files that mix routing, validation, data access, and formatting.
- Keep module side effects minimal and visible.

## Async And Errors

- Use `async` and `await` for readability.
- Never leave rejected promises unhandled.
- Throw `Error` objects, not strings.
- Add context when rethrowing so failures remain diagnosable.

## Testing

- Prefer contract tests and behavior tests over brittle implementation mocks.
- Cover boundary validation and unhappy paths.
- Use fake timers and network mocks intentionally, not globally by default.

