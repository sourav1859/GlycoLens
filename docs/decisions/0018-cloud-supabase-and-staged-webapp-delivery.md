# ADR 0018: Cloud Supabase and staged web application delivery

**Date:** November 10, 2026.

**Status:** Accepted by the user for the implementation target and delivery approach; setup and implementation pending.

## Context

The user confirmed one repository and requested a detailed phase-wise implementation
plan with prerequisites, test cases, expected results and validation gates. The user
explicitly chose cloud Supabase from now on instead of local Supabase, a dedicated
GlycoLens cloud development project, email/password with verification/reset and the
full agreed feature set in staged releases.

The current prototype, migrations and historical acceptance evidence were developed
against local Supabase. The code is not automatically repointed by this decision.
Local start/reset/configuration wrappers are therefore historical tools, not the
new setup path. Managed Supabase for eventual hosting remains consistent with ADR 0016.

## Decision

- Keep the monorepo, FastAPI modular monolith and shared forecast adapters.
- Use a dedicated **cloud Supabase development project** for application DB/Auth,
  new schema migrations and hosted integration acceptance. Web/API processes may
  run locally while using that cloud project. Offline unit/fixture tests stay offline.
- Use email/password with verification, password reset and tested session lifecycle.
  Retain deliberate synthetic demo compatibility; do not add social providers by default.
- Keep migrations in `supabase/migrations/`. Inspect target/history first, preview
  changes and apply reviewed forward migrations through one controlled workflow.
  No cloud reset, destructive reseed or source/production mutation is authorized by drafting.
- Prefer the existing public application namespace in the dedicated project;
  preserve managed Auth and the separately gated catalog namespace. A different
  namespace requires a deliberate exposure/grant/client-contract change before apply.
- Run cloud integration tests only against an exact allowlisted development target
  with synthetic owners, explicit intent and run-scoped cleanup. Fresh migration
  replay and restore require a separately authorized cloud scratch project/branch.
- Keep ordinary CI independent of cloud secrets, local Supabase, model downloads
  and paid providers. Protected opt-in cloud/device/provider/model gates supplement it.
- Deliver the full agreed UI/features through the [implementation plan](../planning/GlycoLens_17_Webapp_Implementation_Plan.md),
  with [144 designed cases](../testing/webapp-cloud-test-cases.md) and a
  [result ledger](../testing/webapp-validation-results.json). A planned/skipped test
  is not passed, and a partial release is not full completion.
- Keep OpenAI recipe extraction. The user will confirm the model/test budget.
  Corrected catalog is not ready; develop with labeled fixtures/providers and
  activate only after validation. VPS/domain remain pending.
- Preserve research/safety/model-selection boundaries and course dates. No real
  patient data, dosing, pump control, clinical-safe labels or automatic model promotion.

## Alternatives and consequences

Continuing local Supabase as the required app/test target conflicts with the user's
explicit choice and is rejected for new implementation. A shared production database
for mutation tests is rejected because migrations/fixtures could affect users.
Separate cloud development plus optional cloud scratch/production targets introduces
network, credentials, quota, email and potential subscription dependencies, but
provides acceptance against the intended service. Extra projects/branches or paid
plans are not created without the relevant configuration/authorization.

This supersedes ADR 0006's **local-first target for future application work**, while
preserving its migration/RLS principles and recorded local evidence. It also changes
the future default environment from ADR 0009 without rewriting that historical result.
Local Supabase wrappers remain in source for historical reproducibility; future
agents must not run them as the new cloud setup path or overwrite cloud keys with local values.

Repository AGENTS.md records this durable project preference. The plan updates
living product, architecture, milestones, safety and testing documentation. No
credentials were collected, cloud schema created, migrations run or live tests executed
in the planning cycle. The result ledger begins entirely NOT_RUN.

## Recovery and validation

Retain current compatible app artifacts and the local prototype's historical
evidence. Roll back application releases with compatible schema; use reviewed
forward repairs and tested cloud backup/restore instead of destructive hosted resets.
Blocked SMTP/catalog/provider/host inputs remain visible phase gates. See the
[cloud setup guide](../tooling/cloud-supabase-setup.md) and
[planning handoff](../tooling/cloud-webapp-plan-handoff-2026-11-10.md).
