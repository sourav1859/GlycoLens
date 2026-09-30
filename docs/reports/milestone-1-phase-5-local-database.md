# Milestone 1 Phase 5: Local Supabase Database

**Date:** September 29, 2026
**Status:** Implemented and validated locally
**Scope:** Executable PostgreSQL schema, constraints, RLS, synthetic seed, and database tests

## Outcome

The documented GlycoLens application schema now exists as a reproducible Supabase migration. A
clean local database reset successfully applied the migration and synthetic seed, the schema
linter reported no errors, and all 20 pgTAP tests passed.

No hosted Supabase project was created or modified. Generated local configuration, endpoints,
connection strings, project references, and credentials remain ignored and were suppressed during
validation.

## Implemented schema

The initial migration creates:

- `users`, linked one-to-one with Supabase Auth;
- `cgm_readings`;
- `insulin_events`;
- `activity_events`;
- `foods`;
- `meals`;
- `meal_items`;
- `forecasts`;
- `forecast_points`; and
- `meal_outcomes`.

It also installs pgvector, creates timeline and lookup indexes, enforces numeric/JSON/quantile
constraints, and links dependent records with explicit delete behavior.

The vector column is intentionally dimensionless in Phase 5. The embedding model and dimension
have not been selected, so an indexed fixed-width representation would be premature.

## Authorization and privacy controls

- RLS is enabled on all ten exposed application tables.
- Anonymous users receive no table privileges.
- Authenticated users can access only rows they own directly or through their parent meal or
  forecast.
- Shared foods are readable only by authenticated users; client-side writes are denied.
- Research datasets are not loaded into the application database.
- The committed seed contains one explicitly synthetic food-catalog fixture and no user account,
  email address, credential, or health record.
- Local configuration and runtime state are excluded by `supabase/.gitignore`.

## Test traceability

| Requirement or risk | Scenario | Layer | Evidence | Result |
|---|---|---|---|---|
| Reproducible schema | Reset an empty local database | Migration | `supabase db reset --local` | Pass |
| Valid PostgreSQL objects | Lint public and extensions schemas | Database lint | `supabase db lint --local` | Pass: no errors |
| Required tables | Assert all ten tables | pgTAP | `database_contract.test.sql` | Pass |
| pgvector availability | Assert extension exists | pgTAP | `database_contract.test.sql` | Pass |
| Denial by default | Anonymous food query | RLS/privilege | SQLSTATE `42501` | Pass |
| Owner access | User inserts and reads own CGM | RLS | Synthetic user fixture | Pass |
| Cross-user isolation | Second user cannot read/insert first user's CGM | RLS | Synthetic users | Pass |
| Input integrity | Reject negative glucose | Constraint | SQLSTATE `23514` | Pass |
| Forecast integrity | Reject crossing q10/q50/q90 | Constraint | SQLSTATE `23514` | Pass |
| Repository privacy | Scan committed DB contract | Static pytest | No endpoints/credentials | Pass |

## Verification record

| Check | Result |
|---|---|
| Clean local database reset | Passed |
| Supabase schema lint | Passed: no errors |
| pgTAP database suite | Passed: 20 tests |
| Static database contract suite | Passed: 4 tests |
| Local configuration ignored | Passed |
| Hosted project interaction | Not performed |
| Graphify 0.9.69 code-only refresh | Passed: 1,200 nodes, 1,730 edges, 157 communities |

Graphify reported that SQL AST extraction needs its optional `tree_sitter_sql` dependency. This
does not affect database evidence: the SQL was executed from a clean reset, linted by Supabase,
and tested behaviorally with pgTAP.

## Reproduce safely

Prerequisites are Docker Desktop and Supabase CLI. Initialize a machine-local configuration once:

```powershell
supabase init
```

The generated `supabase/config.toml` is ignored. Run the repository wrapper to suppress generated
connection details while resetting, linting, and testing:

```powershell
./scripts/database/Test-LocalSupabase.ps1
```

Do not copy local keys or connection output into documentation, issues, commits, or chat. A hosted
project should be linked only after explicit authorization in a later deployment step.

## Milestone 1 closure

Phase 5 closes the executable PostgreSQL/Supabase schema requirement. Phase 6 subsequently
completed the validated py-mgipsim virtual-patient scenario, and the final presentation and
closure audit are now complete. See [the Phase 6 report](milestone-1-phase-6-pymgipsim-scenario.md)
and [the final closure audit](milestone-1-closure-audit.md).
