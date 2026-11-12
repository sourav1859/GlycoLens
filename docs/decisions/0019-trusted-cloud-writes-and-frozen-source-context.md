# ADR 0019: Trusted cloud writes and frozen source context

Status: implemented in development, November 11, 2026; release acceptance open.

The multi-page app needs editable meals without browser-forged totals or rewritten
forecast evidence. Supabase Auth remains canonical. FastAPI verifies the user with
Auth and checks the JWT's exact session ID against managed `auth.sessions`.

Ordinary reads use the caller JWT and owner RLS. Browser writes are revoked;
narrow `SECURITY INVOKER` RPCs receive an owner overwritten from the independently
verified session by `db/trusted.py`. Modern server keys use `apikey`, never a fake
bearer JWT. The service-role boundary requires explicit parent ownership checks.

| Resource | Browser | Trusted API |
|---|---|---|
| Profile/preferences/onboarding/notice | Owned SELECT | Validated CAS transitions and versioned completion |
| Provider food facts | SELECT | Facts fetched by provider adapters; no client totals |
| Meals/items/revisions | Owned SELECT | Atomic gram calculation, frozen ingredient facts, receipt/CAS and cancellation |
| Source partitions/CGM/insulin | Owned SELECT | Reviewed simulation/replay and bounded clock advance |
| Forecasts/points/scenarios/outcomes | Owned SELECT | Validated adapter outputs, frozen context and genuine later coverage |
| Notifications | Owned SELECT | Trusted event triggers; bounded owned mark-read |
| Private receipts/LLM reservations | No access | Transactional idempotency and conservative budget reserve |

The only new definer is **private.session_is_active()**, in a non-exposed schema,
with an empty search path. It derives `auth.uid()` and the signed `session_id` and
returns only a boolean; it accepts no arbitrary owner/session parameter. A public
invoker wrapper supports API verification. Restrictive active-session policies
also deny direct Data API reads after logout. It gives browsers no Auth-table grants.

Each simulation/replay gets a distinct owned source UUID even when timestamps
overlap. Meals freeze reviewed facts; every edit stores a new revision. Forecasts
freeze that revision, origin, CGM/insulin input and validated response. Historical
reads use the frozen response. Editing/cancelling a meal or replacing the source
cannot rewrite an old forecast. Scenarios use the same frozen context and remain
separate from consumption. Later observations are available only after advancing
the source clock with checksum-verified synthetic artifacts. No future trajectory
is served directly or supplied to inference. The current bridge's insulin context
ends at its original origin: advancing glucose for follow-up does not extend
inference eligibility; prepare a new reviewed source for a later forecast.

The application recipe endpoint conservatively reserves USD 0.01 before each
approved-model call, includes prior USD 0.00763580 spend, and refuses reservations
above USD 5 or 10 calls/owner/day. Reservations are not refunded on failed or
uncertain requests. This is a conservative test allowance, not provider billing
reconciliation or a production spending policy. No further paid calls were made
in the implementation checks.

The first four migrations were preserved. Initial cloud bootstrap and permission
hardening ran atomically; subsequent changes are forward migrations. MCP's
generated history timestamps were aligned with canonical repo filenames and SQL
statements; comparisons normalize line endings. No hosted reset was used. Fresh
scratch replay was explicitly deferred by the user, and new changes stay local.

See the [implementation evidence](../reports/webapp-implementation-checkpoint-2026-11-11.md)
and [case ledger](../testing/webapp-validation-results.json) for actual passes,
partial coverage, failures and pending acceptance.

Reviewed food facts are also compared atomically with the trusted facts used for
calculation. Current composer/demo requests carry this guard; a mismatch returns
409. Copies load current facts, edits preserve frozen facts. Older API requests
may omit the guard for compatibility and still use server-calculated nutrition.
