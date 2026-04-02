---
id: global-engineering-rules
title: Global Engineering Rules
languages: [all]
layers: [all]
stages: [design, build, review]
checks: [design-rules-documented]
---

# Global Engineering Rules

These rules apply across all languages and stacks in this repository unless a more specific rule overrides them.

## Core Principles

- Optimize for readability, correctness, and safe change over cleverness.
- Make the smallest change that fully solves the problem.
- Prefer explicit code over magical or highly implicit behavior.
- Keep modules cohesive and responsibilities narrow.
- Do not introduce a new abstraction until duplication or volatility justifies it.

## Change Boundaries

- Do not change public contracts, storage formats, or externally visible behavior without updating docs and migration notes.
- Do not mix unrelated refactors with feature work or bug fixes.
- Preserve backward compatibility by default.
- Prefer additive changes before destructive changes.

## Naming And Structure

- Use names that describe business meaning, not temporary implementation detail.
- Keep files and directories predictable and aligned with domain boundaries.
- Avoid generic utility dumping grounds such as `misc`, `helpers`, or `common` unless they have a clear contract.
- Move shared logic into well-named modules only after a real second use appears.

## Functions And APIs

- Keep functions focused on one job.
- Pass explicit inputs and return explicit outputs.
- Avoid hidden mutation of shared state.
- Validate inputs at system boundaries.
- Fail early on invalid state instead of silently continuing.

## Errors And Observability

- Never swallow errors without a deliberate fallback.
- Include actionable context in logs and error messages.
- Do not log secrets, tokens, passwords, or raw personal data.
- Use structured logging where the stack supports it.

## Data And Security

- Sanitize and validate all external input.
- Use parameterized queries and safe escaping primitives.
- Do not hardcode credentials, private keys, or environment-specific secrets.
- Apply least privilege to filesystem, network, and database access.

## Testing

- Add or update tests for every behavior change.
- Prefer fast unit tests close to the changed logic.
- Add integration tests when behavior crosses process, network, database, or framework boundaries.
- Test error paths and edge cases, not only happy paths.
- Keep test fixtures minimal and intention-revealing.

## Review Gates

- Code should be understandable without reading the entire repository.
- New dependencies must have clear justification.
- Temporary workarounds must be marked with context and a cleanup path.
- If a rule here conflicts with a stack-specific file, follow the more specific file and document the reason in the change.

