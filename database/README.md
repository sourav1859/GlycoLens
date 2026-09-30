# Database

The executable Supabase PostgreSQL contract uses the standard CLI layout under `supabase/`:

- `supabase/migrations/` - versioned application schema and row-level-security policies;
- `supabase/tests/` - local pgTAP schema, constraint, and authorization tests; and
- `supabase/seed.sql` - synthetic catalog fixtures only.

The generated local `supabase/config.toml`, runtime state, endpoints, and credentials are ignored.
Run `supabase init` once per clone, then use `scripts/database/Test-LocalSupabase.ps1` to start the
local stack without printing generated connection details, rebuild from zero, lint, and test.

The application database is for app users, selected synthetic/demo timelines, meals, forecasts,
and personal history. Full research datasets remain outside the application database.
