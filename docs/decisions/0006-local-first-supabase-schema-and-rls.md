# ADR 0006: Local-first Supabase schema and row-level security

- **Status:** Accepted
- **Date:** September 29, 2026

## Context

Milestone 1 requires an executable PostgreSQL/Supabase schema. Creating tables manually in a
hosted dashboard would make the result difficult to reproduce and could expose project-specific
connection information before the authorization boundary is tested. The database will eventually
hold health-related application records, so denial by default and cross-user isolation must be
part of the first migration rather than later hardening.

## Decision

- Develop and validate the initial database locally with Docker and Supabase CLI.
- Keep versioned migrations, pgTAP tests, and synthetic seed data under the standard `supabase/`
  layout.
- Ignore generated `supabase/config.toml`, runtime state, local endpoints, project references,
  connection strings, and keys.
- Link `public.users` one-to-one with `auth.users` and use `auth.uid()` for ownership policies.
- Enable RLS on every exposed application table. Anonymous access is denied; authenticated users
  may access only their own records. The shared food catalog is authenticated-read-only.
- Keep the full T1D-UOM research dataset outside the application database.
- Store the meal embedding as an unconstrained `vector` until the embedding model and dimension
  are selected; add an index only after that decision.
- Do not create or link a hosted Supabase project during this phase.

## Alternatives considered

### Create tables manually in a hosted Supabase dashboard

Rejected because it creates schema drift, weakens reproducibility, and makes rollback and review
harder.

### Start with plain PostgreSQL scripts outside Supabase conventions

Rejected because the project already selected Supabase Auth/RLS and the standard CLI layout gives
repeatable migration, reset, lint, seed, and pgTAP workflows.

### Import the research dataset into the application database

Rejected because it is unnecessary for the M1 app schema and expands privacy, storage, and
operational risk.

## Consequences

- A clean local database can be rebuilt and tested without a cloud account.
- Policies and tables are applied atomically in the same migration.
- A future hosted deployment should use `supabase db push` only after explicit authorization and
  review of the target project.
- Changing the embedding model may require a later migration that fixes vector dimension and adds
  an approximate-nearest-neighbor index.

## Recovery and change conditions

During local-only development, correct the initial migration and rerun a clean reset. After any
hosted deployment, use forward-only corrective migrations rather than rewriting applied history.
If Supabase is replaced, retain PostgreSQL constraints and equivalent owner-isolation tests.
