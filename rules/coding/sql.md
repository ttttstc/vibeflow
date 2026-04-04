---
id: sql-database-standard
title: SQL And Database Standard
languages: [sql]
globs: ["**/*.sql"]
layers: [data]
stages: [design, build, review]
checks: [sql-no-select-star]
---

# SQL And Database Standard

Apply these rules to SQL migrations, queries, procedures, and data access layers.

## Safety

- Treat schema changes as production-affecting code.
- Preserve backward compatibility across rolling deployments.
- Prefer additive migrations before destructive cleanup.
- Never run destructive data changes without rollback or recovery planning.

## Query Quality

- Write queries for correctness first, then measure performance.
- Select only the columns you need.
- Use explicit joins and predicates.
- Avoid hidden cartesian products and accidental full-table scans.

## Schema Design

- Name tables, columns, indexes, and constraints consistently.
- Encode data integrity in the schema where practical.
- Keep nullable columns intentional and documented.
- Use proper data types instead of overloading text columns.

## Transactions

- Keep transactions as small as correctness allows.
- Make locking behavior intentional.
- Be careful with retry behavior around non-idempotent writes.

## Migrations

- Make migrations deterministic and reviewable.
- Separate schema changes from bulk backfills when operational risk is high.
- Add indexes with awareness of database-specific locking behavior.
- Document contract changes that application code must follow.

