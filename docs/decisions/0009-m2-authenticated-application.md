# ADR 0009: Authenticated local simulation and nutrition application

Status: Accepted, October 14, 2026 under the approved M2 plan.

Current implementation target: [ADR 0018](0018-cloud-supabase-and-staged-webapp-delivery.md)
uses dedicated cloud Supabase and verified email/password accounts for new work.
The local/anonymous implementation recorded here is historical evidence, retained
without claiming cloud setup or changing the model/scientific result.

## Decision

Keep FastAPI as modular monolith and reuse the canonical research adapter. Use local
Supabase anonymous Auth for no-contact demo entry, user-token PostgREST for RLS,
and SECURITY INVOKER transaction functions for calculated/idempotent meal and forecast
writes. Client owner fields are rejected. Repeated ingredients aggregate by food/grams.
Snapshot source nutrient facts at save time. Strict forecast-grid/quantile validation
precedes persistence. Privileged server catalog writes accept provider facts only.

The public M1 synthetic endpoint remains distinct. Real forecasts use `simulated`
provenance and explicit C3 context. Chronos C3 was validation-frozen before test and
is cached once per API process with bounded concurrency; errors are redacted.

Execute only the reviewed fixed simulator through the isolated subprocess, with a
timeout and execution lock. Retain public M1 dose-free exports. A separate private
synthetic context export is needed for C1-C3 application inference; use actual simulator
basal U/h and bolus U observations, never fabricate insulin. Only glucose available by
the generated lunch-origin fixture clock enters the app. UTC fixture dates are explicitly
simulated, not converted research timestamps. Public scenario responses omit insulin.

Food facts normalize to a 100-g basis; missing nutrients stay unknown. The prepared
OpenAI Responses adapter extracts ingredients/quantities only, requires a configurable
model/key, disables retention, and never receives patient context. Deterministic food
facts and user-confirmed grams/servings establish nutrition. Live provider verification
is a gate; mocking cannot complete it. No automatic paid request is issued.

Numeric historical retrieval uses same-user earlier meals whose outcomes were available
by query time; macro scaling constants are fixed, not test-fitted. One simulator-derived
earlier meal uses illustrative nutrition explicitly labeled in the UI. It is demo evidence,
not a real-user meal history or research evaluation sample.

## Alternatives

An unauthenticated hardcoded demo user or service-role access for all app records was
rejected because it bypasses ownership guarantees. In-process simulator imports were
rejected because their dependency pins differ. Queues/microservices and semantic
retrieval remain unnecessary at single-demo capstone scale. Client-generated authoritative
nutrition or LLM nutrient guesses were rejected in favor of SQL recomputation/snapshots.

## Consequences and remaining gates

Local migrations and owner-isolation tests are reproducible; no hosted project is changed.
Authentication and provider configuration remain ignored. A physical camera test and
live USDA/recipe checks are outstanding. Persistence outperforms the selected pretrained
model on held-out error and quantiles are under-covered, so do not advertise clinical
accuracy or calibrated confidence. Future serving changes must retain these boundaries.
