# Database

**Current target:** a dedicated managed **cloud Supabase development project**,
confirmed November 10 in [ADR 0018](../docs/decisions/0018-cloud-supabase-and-staged-webapp-delivery.md).
Use the [cloud setup guide](../docs/tooling/cloud-supabase-setup.md) and
[implementation plan P01](../docs/planning/GlycoLens_17_Webapp_Implementation_Plan.md#p01---create-and-connect-the-cloud-application-schema)
for reviewed hosted schema creation, grants/RLS and integration acceptance. The
cloud schema has not been applied merely by updating these documents.

The executable Supabase PostgreSQL contract uses the standard CLI layout under `supabase/`:

- `supabase/migrations/` - versioned application schema and row-level-security policies;
- `supabase/tests/` - existing pgTAP schema, constraint, and authorization assertions to adapt for controlled cloud testing; and
- `supabase/seed.sql` - synthetic catalog fixtures only.

Project-specific configuration, runtime state, endpoints and credentials remain ignored.
The old `scripts/database/Test-LocalSupabase.ps1` starts/resets a local stack and is
retained for historical reproducibility. It is not the current cloud setup/test
path. Never reset a hosted project or overwrite cloud keys through local helpers;
use exact target guards and run-scoped synthetic fixtures with scoped cleanup.

The application database is for app users, selected synthetic/demo timelines, meals, forecasts,
and personal history. Full research datasets remain outside the application database.
