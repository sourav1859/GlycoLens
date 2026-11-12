# Webapp implementation handoff - November 11, 2026

Latest follow-up: [November 12 review](../reports/demo-logout-compose-review-2026-11-12.md) adds demo/logout/local Compose changes and two planned P09 cases (146 current cases). Dated observations below remain historical.

Goal: execute plan 17 in the existing monorepo with real tests, preserving cloud
Supabase, adapter, synthetic-data and nonclinical boundaries. Keep changes local
for review; do not commit or push. Fresh scratch replay is explicitly deferred.

The [implementation report](../reports/webapp-implementation-checkpoint-2026-11-11.md),
[manifest](../reports/webapp-release-manifest-2026-11-11.json) and
[case ledger](../testing/webapp-validation-results.json) own current status. Core
code and cloud schema are implemented with partial full-case acceptance; do not
restart baseline work or rerun passed expensive/provider tests without a reason.
P07 corrected catalog, P08 policy-sensitive lifecycle and P10 hosted acceptance
need outstanding user inputs. Optional goal entry/history acceptance remains open.

New cloud migrations are canonical under `supabase/migrations/`; normalized SQL
hashes match all 14 cloud history rows. Ordinary reads use caller JWT/RLS; narrow
trusted invoker writes inject verified owner. Exact Auth-session revocation also
gates direct Data API reads. Never use old local reset/demo setup helpers.

Changed areas: backend account/trusted writes, meal revisions/source partitions,
immutable forecasts/scenarios/follow-up/aggregate/export/notifications; frontend
Auth/onboarding/layout and shared responsive routes; guarded cloud runners,
offline tests/CI/contracts; Linux web packaging and deployment preparation.
Planning 00/01/03/04/06/08/09/10/17, UI architecture, setup, ADR 0019 and README
were synchronized. Scientific protocols/model selection remain unchanged.

Evidence: 160 relevant Python tests pass in a fresh minimal offline environment,
24 frontend unit tests pass, 20 isolated browser journeys pass; lint/types and
production builds pass. Real simulator/Chronos and owner/aggregate/privacy/scenario
cloud runs are recorded separately. Linux web runtime smoke passed as nonroot
with synthetic public settings. No new paid LLM calls or email messages were sent.
Private-file checks and repository skill validation pass. Temporary cloud test
users/foods and local review container were cleaned; public food cache entries
and the labeled demo seed are intentional. Browser screenshots/traces, model and
source artifacts stay ignored.

Earlier failed runs were retained: domain-error classification, SQL alias,
missing browser runtime, selector mismatches, a refused overlapping browser run,
and an optional-state TypeScript error were corrected. The case ledger maps actual
observations rather than trusting early incorrect harness case labels. Exact local
worktree hashes were not captured before every earlier cloud run; before release,
revalidate from a recorded reviewed revision instead of inventing provenance.

Implemented: immediate password-confirmed deletion with no recovery window,
owned cascades and durable private-file retry (ADR 0020). Awaiting project
support/contact email and provider backup/log retention/restore acceptance;
corrected catalog release; VPS/domain and eventual SMTP; physical/manual UAT;
scratch replay/restore remains deferred. Uncached Open Food Facts reads are
guarded until a proper project contact is privately configured. Existing v2
compatibility/staging/v3 and attribution/license acceptance require follow-up.
Do not substitute a personal address or silently enable email delivery.

Next: consume the user's pending project-contact answer, finish the corresponding
bounded lifecycle/provider work, then corrected-catalog admission and remaining
manual/hosted gates. API/isolated simulator Linux packaging/readiness/resource and
recovery acceptance remain partial; web-only smoke is not full hosting readiness.
Graphify's final local AST/Markdown/scoped semantic refresh and limits are recorded
under ignored `graphify-out/semantic-refresh-evidence.json`; no external semantic
API is authorized by this handoff.
