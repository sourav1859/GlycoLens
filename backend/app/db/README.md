# Database Access

Reserve this package for application database sessions, repositories, and persistence mappings. Research datasets remain outside the application database.

`client.py` verifies user tokens through Supabase Auth and forwards them to PostgREST
so ownership/RLS applies to every user request. Atomic SECURITY INVOKER RPCs own
meal/forecast writes. Privileged food caching lives only in the trusted nutrition
provider service, never the user-record path. Configuration is loaded from ignored files.
