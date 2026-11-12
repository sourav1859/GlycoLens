# Webapp follow-up handoff — November 12, 2026

Goal: deliver clearer demo controls, discoverable managed logout, explicit
meal-response validation milestones and one-command local app startup. The user
authorized committing/pushing this checkpoint on November 12; see the
[delivery record](../reports/github-checkpoint-delivery-2026-11-12.md). Public deployment
remains separate. Managed cloud Supabase remains the
application target. Scratch replay stays deferred; no new paid LLM calls.

See [findings/evidence](../reports/demo-logout-compose-review-2026-11-12.md),
[current manifest](../reports/webapp-release-manifest-2026-11-12.json),
[case ledger](../testing/webapp-validation-results.json), [ADR 0021](../decisions/0021-local-compose-runtime.md)
and [runtime commands](../../infra/README.md).

Demo buttons are Run new simulation / Replay saved simulation. Shared header/demo
logout uses existing Supabase Auth and anonymous confirmation. Identity-keyed demo
state clears after cross-tab sign-out. The fixture Next server uses ignored
`.next-e2e` output to coexist with the user's running development server.

Root Compose starts web plus one API worker. Chronos is still CPU inference inside
the API. Simulator uses its own Linux venv and verified source commit. Preserving
the venv executable path fixed a real Linux symlink bug. Model cache is read-only;
local simulation artifacts bind the existing host directory so PowerShell and
container deletion workers see the same complete source store. A custom empty
store against the same cloud project is unsafe for cleanup acknowledgement.
Final runtime validation disables the existing cloud deletion worker; normal app
startup must keep cleanup enabled. Temporary review containers were stopped.

Validated: 171 offline Python tests + one opt-in reproducibility skip; 24 frontend
unit tests; lint/types/build; 26 desktop/mobile fixture journeys; real Linux fixed
simulator and cached 24-point forecast; HTTP/auth/CORS boundaries, scoped image
secret review and restart/storage persistence. No complete phase/release closure.

Next: execute the predeclared [meal-response sensitivity protocol](../testing/meal-response-validation-protocol.md)
(GL-P09-011) without changing model selection. Matching-outcome accuracy
(GL-P09-012) needs an approved untouched evaluation target. Never use arbitrary
user meals versus the fixed simulator's preset outcomes as validation. Existing
primary/PEDAP research tests are consumed. Catalog, SMTP/domain/VPS, scratch
restore, readiness/performance and physical/manual UAT remain separate gates.
