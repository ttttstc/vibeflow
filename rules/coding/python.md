---
id: python-coding-standard
title: Python Coding Standard
languages: [python]
globs: ["**/*.py"]
layers: [runtime, tests, scripts]
stages: [design, build, review]
checks: [python-no-bare-except, python-no-print-runtime]
---

# Python Coding Standard

Apply these rules to Python modules, scripts, services, and tests.

## Style And Typing

- Follow PEP 8 and prefer readability over dense one-liners.
- Use type hints for public functions, methods, and complex internal helpers.
- Prefer `pathlib` over manual path string handling.
- Prefer `dataclass` or typed models for structured data over untyped dicts passed through many layers.
- Avoid overly dynamic patterns that defeat static analysis.

## Module Design

- Keep modules small and organized around one domain or responsibility.
- Do not place business logic in import side effects.
- Avoid circular imports by improving module boundaries instead of using local-import hacks by default.
- Keep CLI entrypoints thin and move logic into testable functions.

## Functions

- Prefer explicit return values over mutating caller-owned objects.
- Raise specific exceptions with useful context.
- Avoid boolean flag parameters when separate functions would be clearer.
- Break up functions that mix parsing, validation, business logic, and I/O.

## Data And Models

- Validate inbound data at boundaries using typed schemas or explicit checks.
- Do not return partially shaped dicts with unstable keys.
- Use timezone-aware datetimes for persisted or cross-system timestamps.
- Treat `None` handling explicitly instead of relying on truthiness.

## Concurrency And Async

- Use `async` only when the full call path benefits from it.
- Do not block the event loop with file, network, or CPU-heavy work.
- Keep sync and async APIs clearly separated.

## Logging And Errors

- Use `logging` instead of `print` outside local scripts.
- Never use bare `except:`.
- Catch the narrowest useful exception type.
- Log enough context to debug failures without leaking secrets.

## Testing

- Use `pytest`.
- Prefer plain fixtures over hidden magic in fixture pyramids.
- Mock network and time carefully, but avoid mocking your own core domain logic.
- Cover serialization, boundary validation, and failure behavior.

## Packaging And Tooling

- Keep dependencies minimal and pinned according to project policy.
- Prefer standard library solutions when they are clear and sufficient.
- Run formatting, lint, and tests before merging.

