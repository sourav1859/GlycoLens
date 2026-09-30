# Database Policies

Row-level-security policies are versioned with their tables in `supabase/migrations/` so a clean
database cannot exist temporarily without its authorization boundary. Behavioral allow/deny tests
live in `supabase/tests/`.
