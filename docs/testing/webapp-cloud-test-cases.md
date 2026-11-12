# Cloud web application test-case catalog

**Plan version:** 2026-11-10. **Status:** cases remain the acceptance contract; actual checkpoint observations and unexecuted/blocked coverage are recorded in the linked ledger. A passing subset does not close a combined-layer case or phase.

The [implementation plan](../planning/GlycoLens_17_Webapp_Implementation_Plan.md) defines phase work and gates. The machine-readable [validation results](webapp-validation-results.json) records every case. Each case requires actual observations and evidence before its result changes. 146 cases cover 11 phases.

## Execution and evidence rules

- Layers: U = offline unit/contract/static checks; C = controlled cloud development/staging integration; B = browser automation; M = manual/device/accessibility review. Combined labels require the relevant evidence, not a mock substituted for a real integration.
- P0 cases guard security, privacy, data integrity or release-critical behavior; P1 cases are also required for the delivered feature. All listed cases are required for full agreed-feature acceptance. A staged release can cover a declared subset but must not claim full completion.
- Cloud cases use the dedicated approved cloud development project, synthetic users A/B and run-tagged fixtures. No production/local-Supabase target, whole-database reset, arbitrary user cleanup or private research data is allowed. A separately authorized cloud scratch project/branch is required for fresh migration replay and restore tests; absent access is BLOCKED once execution is attempted.
- Fixtures include independently calculated meal/nutrition arrays, valid/invalid forecast grids, DST boundaries, hostile text, unknown nutrients, owner collisions, timeouts and source/session switches. Real provider facts and real model results are recorded separately from fixture contracts.
- Capture a run ID, exact code/migration/model/config revision, target project alias, command or manual protocol, expected/actual result, redacted evidence paths, defect and execution time. Never store raw keys, JWTs, passwords, private health records or full request logs. Actual test email addresses/configuration stay private.
- Use stable operation IDs to verify retries; compare totals/errors with an independent oracle rather than reproducing the implementation. Repeat a passed check only after a relevant change or unresolved concern.
- Do not request real Auth email, paid LLM/provider calls or hosted load without the designated inboxes, confirmed limits and applicable opt-in. Do not use admin-confirmed fixtures to claim real email confirmation/reset delivery passed.
- New harness/runner paths and commands must be implemented in their owning phase. Existing local reset/Configure-LocalDemo tooling is historical and is not a cloud test runner.

## Phase-to-case inventory

| Phase | Area | Cases |
|---|---|---|
| P00 | Baseline, configuration and CI | 8 |
| P01 | Cloud Supabase, schema and trusted data boundaries | 12 |
| P02 | Responsive shell and shared UI | 10 |
| P03 | Permanent Auth and minimal onboarding | 17 |
| P04 | Meal capture, logging, barcode and recipe analysis | 19 |
| P05 | Simulation, forecasts and historical evidence | 15 |
| P06 | Home feed and nutrition aggregation | 12 |
| P07 | Validated catalog, search, detail and favorites | 15 |
| P08 | Profile, settings, privacy and notifications | 13 |
| P09 | Portion comparison and later actual outcomes | 12 |
| P10 | Hosted deployment, resilience and release acceptance | 13 |

## P00 - Baseline, configuration and CI

| Case | Priority | Layer | Setup and action | Expected result / validation oracle |
|---|---|---|---|---|
| GL-P00-001 — Reproduce supported toolchain | P0 | U | Clean checkout; pinned manifests. Run documented version/install/check commands in the normal shell. | Supported Python/Node/pnpm/CLI versions and relevant checks are recorded; unavailable tools block execution rather than producing a pass. |
| GL-P00-002 — Configuration presence without disclosure | P0 | U | Empty and populated synthetic environment maps. Run readiness/config validators with absent, malformed and valid values. | Report names/presence and actionable errors only; no key/token/password values or health content. |
| GL-P00-003 — Reject unintended database target | P0 | C | Approved cloud-dev reference plus local/production/lookalike targets. Invoke cloud harness with each target and missing opt-in. | Only the exact approved development target with explicit run intent can execute writes; local/production/unknown targets are refused. |
| GL-P00-004 — CI ordinary checks are offline | P0 | U | PR workflow without cloud/provider secrets. Run unit/frontend/contract jobs; observe outbound dependencies. | Tests pass with synthetic fixtures and no model download, paid call or cloud mutation; genuine failures fail CI. |
| GL-P00-005 — Protected cloud test job | P0 | C | Trusted and untrusted PR/job contexts. Attempt secret-backed integration job in each context. | Untrusted forks receive no secrets and cannot run cloud writes; eligible protected jobs are explicitly enabled and report status. |
| GL-P00-006 — API schema and client drift | P1 | U | Versioned OpenAPI/types plus deliberate incompatible response. Run schema/client compatibility checks. | Incompatible change fails; reviewed compatible schema regenerates/checks deterministic client types. |
| GL-P00-007 — Secret and image-context inspection | P0 | U | Synthetic secret canaries and excluded data/cache paths. Inspect versioned files and prospective container build context. | Private env, dataset/database/model caches and canaries are excluded from Git/images/public bundles; public keys distinguished from private secrets. |
| GL-P00-008 — Baseline and release manifest | P1 | U | Existing prototype and pinned model metadata. Record commit, lockfiles, migrations, model revision and relevant baseline results. | A reproducible manifest distinguishes existing passes from new work; missing evidence remains pending. |

## P01 - Cloud Supabase, schema and trusted data boundaries

| Case | Priority | Layer | Setup and action | Expected result / validation oracle |
|---|---|---|---|---|
| GL-P01-001 — Cloud project and key compatibility | P0 | C | Dedicated cloud-dev project; selected API key types. Check project identity, API connectivity and modern/legacy key header behavior. | URL/ref belong to the approved project; API keys use supported headers, user JWTs authenticate users, and no non-JWT secret is treated as a bearer JWT. |
| GL-P01-002 — Inventory before first migration | P0 | C | New project with managed schemas/extensions. Read migration history, exposed schemas, tables and baseline capacity. | Existing state is recorded; collisions/drift stop mutation; no managed Auth table is replaced. |
| GL-P01-003 — Migration preview and controlled apply | P0 | C | Reviewed pending migrations and approved target. Preview exact changes, then apply once through the controlled workflow. | Only reviewed migrations apply to cloud dev; history/checksums/schema match; no cloud reset/drop/reseed occurs. |
| GL-P01-004 — Repeated and failed migration handling | P0 | C | Applied baseline; safe isolated migration failure fixture. Repeat history check and test a transactional failure in the test environment. | No duplicate schema/data effects; failed migration leaves a documented consistent state and recovery action. |
| GL-P01-005 — Fresh hosted replay | P1 | C | Separately authorized empty cloud scratch project or branch. Replay committed migration chain and compare schema contract. | Fresh cloud schema matches expected structure without a local Supabase dependency; lack of scratch access is recorded as blocked. |
| GL-P01-006 — Owner and child RLS matrix | P0 | C | Synthetic users A/B, anonymous request, linked parent/child rows, forged/expired/foreign-project tokens. Attempt read/write/RPC access across each identity/resource combination. | A cannot access B; child policies follow owned parents; unauthenticated and invalid token access is denied as specified. |
| GL-P01-007 — Trusted derived-write matrix | P0 | C | Browser A token, spoofed user metadata/role claims and restricted backend writer. Attempt direct/RPC fabrication of totals, forecast points, outcomes, notifications and catalog facts. | Browser cannot forge authoritative derived records or escalate through editable metadata; approved server operations succeed with explicit verified ownership. |
| GL-P01-008 — RPC grants remain functional | P0 | C | Revised grants and transaction functions. Save a meal/forecast through allowed entry points and retry. | Calculated atomic saves still work; revoked table writes do not silently break SECURITY INVOKER dependencies. |
| GL-P01-009 — Schema and numeric invariants | P0 | C | Synthetic invalid timestamps, quantities, units, grids and foreign keys. Submit boundary/invalid records through API and direct permitted interfaces. | Constraints reject invalid/non-finite/negative or inconsistent values; valid boundary inputs persist correctly. |
| GL-P01-010 — New account schema bootstrap | P1 | C | Confirmed synthetic Auth user; preferences/onboarding migrations. Initialize account twice and inspect linked records. | One owner-linked profile; defaults/progress/acknowledgement records are valid and initialization is idempotent. |
| GL-P01-011 — Cloud outage and latency recovery | P1 | C | Network timeout/unavailable-project simulation. Call authenticated read/save and retry after recovery. | Redacted unavailable status, preserved draft and no fabricated empty success or duplicate write. |
| GL-P01-012 — Scoped synthetic cleanup | P0 | C | Run-tagged test users and records plus an unrelated sentinel. Run cloud test teardown and rerun after interrupted teardown. | Only owned recorded test resources are removed; sentinel and other runs survive; no broad delete/reset. |

## P02 - Responsive shell and shared UI

| Case | Priority | Layer | Setup and action | Expected result / validation oracle |
|---|---|---|---|---|
| GL-P02-001 — Navigation and deep links | P1 | B | Mobile, tablet and desktop sessions. Navigate all implemented primary/account routes; reload/back/forward. | Same route identity/order/active state; direct URLs work and unavailable features have honest states. |
| GL-P02-002 — Small-screen reflow | P0 | B | 320/360/390/430px with long names and dense values. Open shell, forms, cards and charts; inspect full content. | No page-wide overflow or lost data/actions; contained scrolling is labeled where needed. |
| GL-P02-003 — Tablet and wide layouts | P1 | B | 768/820/1024/1280/1440/1920px; both tablet orientations. Resize without losing in-progress state. | Rail/sidebar and grids adapt; data, units and controls remain visible; no fixed-frame assumptions. |
| GL-P02-004 — Keyboard and browser chrome | P0 | M | Real mobile keyboard, short viewport and safe-area device. Focus final fields, scroll and activate sticky actions. | Focused inputs/errors/last rows stay visible; navigation/CTAs reserve safe-area space. |
| GL-P02-005 — Accessible dialog behavior | P1 | B | Sheet/dialog with unsaved input. Open using keyboard; tab, Escape/cancel and return. | Focus is constrained/restored correctly, controls named, input preserved as specified and full-page fallback usable. |
| GL-P02-006 — Screen-reader and keyboard journey | P0 | M | Representative page, error and chart states. Complete navigation and primary form without pointer. | Logical focus/reading order, associated labels/errors and meaningful async announcements; no trap. |
| GL-P02-007 — Zoom, text and reduced motion | P1 | M | 200% text, 400% zoom, reduced-motion preference. Use core forms/navigation and chart summaries. | No loss of information/function; readable focus/touch targets; motion respects preference. |
| GL-P02-008 — Async and empty state semantics | P1 | B | Loading, empty, partial, denied and failure fixtures. Exercise each state and retry. | States are distinct; no false zero/success; retry preserves safe state and controls prevent accidental resubmission. |
| GL-P02-009 — Chart accessible representation | P0 | B | Valid history/quantiles with both display units. Inspect plot, legend, summaries, keyboard detail and table at each layout. | Origin/units/source/interval are understandable without color or hover; all required numeric values available. |
| GL-P02-010 — Brand and contrast review | P1 | M | GlycoLens tokens and reference-derived components. Compare core screens and audit focus/text/controls. | Consistent GlycoLens identity and verified contrast/touch sizing; no copied reference branding/assets or clinical-safe labels. |

## P03 - Permanent Auth and minimal onboarding

| Case | Priority | Layer | Setup and action | Expected result / validation oracle |
|---|---|---|---|---|
| GL-P03-001 — Register and verify email | P0 | C+B | Approved test inbox; SMTP and redirects configured. Register, receive verification, verify and return to app. | Account becomes confirmed; credentials remain Supabase-managed; one profile is created and onboarding opens. |
| GL-P03-002 — Unverified and invalid sign-in | P0 | C+B | Unconfirmed user and invalid credentials. Attempt sign-in with each. | Access is denied with neutral useful messaging; no account enumeration or sensitive provider detail. |
| GL-P03-003 — Valid sign-in and routing | P0 | C+B | Confirmed completed and incomplete users. Sign in and directly request protected routes. | Completed user reaches Home; incomplete user resumes setup; API independently authenticates access. |
| GL-P03-004 — Verification-link expiry and resend | P1 | C+B | Expired/reused verification link and rate limits. Open link and request a bounded resend. | Safe recovery; no duplicate profile; real delivery/limit failures are visible rather than reported as sent. |
| GL-P03-005 — Password recovery and reset | P0 | C+B | Confirmed synthetic user and approved inbox. Request reset, follow link, change password and sign in. | Only a valid recovery session permits reset; new password works and invalid/expired/reused links fail safely. |
| GL-P03-006 — Session refresh and expiry | P0 | C+B | Expiring/revoked session. Keep app open, refresh session, then revoke and retry an API call. | Valid refresh works; revoked/expired identity loses access; safe draft/return flow is preserved. |
| GL-P03-007 — Logout and user switching | P0 | C+B | A has private cached data; B signs in next. Logout A and sign in B across routes/tabs. | No A records or cache flashes; private state is cleared and server ownership remains enforced. |
| GL-P03-008 — Safe Auth redirects | P0 | C+B | Allowed callback plus external/malformed return URLs. Complete Auth/recovery with each destination. | Only approved same-origin return paths are used; no open redirect or token leakage through URLs/logs. |
| GL-P03-009 — Password and request validation | P1 | U+B | Weak/overlong input, repeat clicks and safe error fixtures. Submit forms and observe requests/errors. | Approved policy enforced; accessible errors; no password logging or duplicate uncontrolled requests. |
| GL-P03-010 — Onboarding required values | P0 | C+B | New account with invalid/missing timezone/unit/source. Try advancing and completing setup. | Required valid values and notice version enforced server-side; browser flags cannot bypass completion. |
| GL-P03-011 — Resume setup across sessions | P1 | C+B | Partially completed user. Save a step, reload/logout/sign in and resume. | Persisted values and correct next step restore; no duplicated health profile or lost acknowledgement. |
| GL-P03-012 — Skip optional goals/preferences | P0 | C+B | User declines optional fields. Complete setup without nickname/goals/food preferences. | Completion succeeds with safe defaults; no required body/diagnosis data or invented nutrition target. |
| GL-P03-013 — Review and edit consistency | P1 | C+B | Completed steps with saved values. Edit earlier values from review and finish. | Review, database and Home preferences agree; unit/timezone/source validation is reapplied. |
| GL-P03-014 — Onboarding version and concurrency | P1 | C | Two tabs and a changed flow version. Submit stale completion/state updates. | Version conflict or deliberate compatible resume; no false completion or lost newer values. |
| GL-P03-015 — Demo-account continuity | P0 | C+B | Anonymous demo with owned synthetic meals. Use retained demo and approved upgrade path. | Chosen flow preserves UUID/owned records or performs verified migration; no email-based ownership transfer. |
| GL-P03-016 — Ack and consent separation | P0 | C | Required notice plus optional delivery preference. Accept notice, decline delivery and update preferences. | Versioned acknowledgement is auditable; optional choice independent; no real-patient research consent is inferred. |
| GL-P03-017 — Auth abuse and email limits | P1 | C | Bounded approved attempts and provider limit fixtures. Exercise rate-limited sign-in/resend/recovery paths. | Throttling/retry guidance works; tests stay within approved email budget and never conceal undelivered mail. |

## P04 - Meal capture, logging, barcode and recipe analysis

| Case | Priority | Layer | Setup and action | Expected result / validation oracle |
|---|---|---|---|---|
| GL-P04-001 — Search food and resolve facts | P0 | C+B | Known provider fixture and approved live source. Search/select food and inspect stored basis/source. | Canonical item/source ID and per-100-g facts are consistent; live acceptance is labeled separately from fixtures. |
| GL-P04-002 — Barcode manual lookup | P1 | C+B | Known valid, unsupported and malformed codes. Enter barcode and confirm selected product. | Correct product/basis returned or explicit recoverable unsupported/invalid state; no guessed food match. |
| GL-P04-003 — Physical camera capture | P0 | M | HTTPS on a supported real phone; approved barcode. Grant camera, capture once, review result and stop. | Correct code enters normal review; camera stops on completion/navigation and no image is retained unexpectedly. |
| GL-P04-004 — Camera denied or unsupported | P1 | B+M | Denied permission and missing camera/decoder support. Start scan and use fallback. | Clear permission/unsupported recovery and manual code path; no trapped screen or hidden permission loop. |
| GL-P04-005 — Recipe extraction schema | P0 | U+C | Ambiguous recipe text; fixture and approved live LLM run. Parse and inspect editable ingredients/servings. | Output obeys strict schema and limits; ambiguity requires review; model supplies no authoritative nutrient facts. |
| GL-P04-006 — Prompt injection and privacy | P0 | U | Hostile recipe text plus separate synthetic patient-context/secret canaries in surrounding application state. Inspect LLM request and parse result. | Text is treated as untrusted data; surrounding patient/CGM/insulin/context/secrets are not appended to the request; unapproved output fields are rejected. |
| GL-P04-007 — LLM timeout or invalid response | P1 | U+B | Timeout, refusal, malformed, incomplete and over-limit fixtures. Parse and retry/cancel or enter manually. | Honest processing/failure state; draft retained; no invented percent, quantities or silent success. |
| GL-P04-008 — Ingredient grounding and yield | P0 | C+B | Multiple ingredients, ambiguous household units and recipe yield. Resolve food facts and confirm gram/serving conversions. | Every required ingredient is grounded; deterministic totals and per-serving yield math match independent expected values. |
| GL-P04-009 — Missing and invalid nutrient data | P0 | U+C | Unknown fiber, kJ-only energy and invalid quantities. Try reviewing/saving/forecasting each case. | Unknown is not zero; units/conversions follow approved contract; invalid or incomplete required inference inputs fail visibly. |
| GL-P04-010 — Repeated ingredients and fractions | P1 | U+C | Repeated food IDs and fractional gram/serving amounts. Save reviewed composition. | Aggregation and rounding match an independent calculation; no double counting or early rounding drift. |
| GL-P04-011 — Explicit planned versus eaten save | P0 | C+B | Reviewed meal with slot/time/source. Save once as planned and once as eaten. | Distinct states/consumed timestamp; only eaten record contributes to consumption totals. |
| GL-P04-012 — Idempotent durable save | P0 | C+B | Save timeout/retry and double-click. Repeat with the same operation key. | Exactly one durable meal/revision and one success state; changed payload/key misuse returns conflict as specified. |
| GL-P04-013 — Atomic save failure | P0 | C | Invalid child item mixed with valid items. Attempt transactional save. | No partial meal/items/totals remain; error is recoverable and input is retained. |
| GL-P04-014 — Meal edit and version conflict | P0 | C+B | Owned logged meal open in two tabs. Edit grams/time in one tab and submit a stale edit in the other. | New revision/recomputed totals; stale write conflicts; previous forecast inputs remain unchanged. |
| GL-P04-015 — Cancel/remove and ownership | P0 | C+B | Owned and foreign meal IDs. Confirm/cancel removal and attempt foreign edit/delete. | Only owned allowed action succeeds; cancellation updates totals once; foreign record is not disclosed. |
| GL-P04-016 — Copy meal to another date | P1 | C+B | Eaten meal with forecast/outcome. Copy, review and optionally consume new instance. | New draft/planned ID; no copied outcome/forecast association and no consumption until explicit logging. |
| GL-P04-017 — Meal detail and paginated history | P1 | C+B | More records than a page across slots/dates. Navigate, filter and reopen a detail link. | Stable owner/date/source pagination; correct slots and details; totals do not depend on loaded page size. |
| GL-P04-018 — Offline/interrupted draft recovery | P1 | B | Unsaved recipe/portion and network interruption. Navigate/retry according to the approved draft policy. | Safe draft recovery or explicit discard; no private cross-account persistent cache or fake successful save. |
| GL-P04-019 — Provider limits and provenance | P0 | U+C | Provider outage/rate-limit plus changed source facts. Lookup, retry and revisit a saved meal. | Bounded calls and clear source/unavailable state; source updates cannot rewrite the saved nutrition snapshot. |

## P05 - Simulation, forecasts and historical evidence

| Case | Priority | Layer | Setup and action | Expected result / validation oracle |
|---|---|---|---|---|
| GL-P05-001 — Cloud-backed simulator and clock | P0 | C+B | Pinned isolated simulator; cloud-dev user. Run fixed scenario and inspect timeline/source/origin. | Only reviewed synthetic context reaches owned storage; fixture clock is explicit and future glucose is absent. |
| GL-P05-002 — Replay provenance and source switch | P0 | C+B | Reviewed replay plus missing/stale replay fixtures. Switch/run replay and attempt absent replay. | Live versus replay is explicit; missing replay fails clearly; timelines/outcomes do not mix sources/sessions. |
| GL-P05-003 — Regular pre-origin input window | P0 | U+C | Valid 24-point grid plus missing/irregular/future rows. Build forecast requests from each input. | Valid regular past-only inputs succeed; invalid context fails closed with no future leakage. |
| GL-P05-004 — Insulin semantics and meal completeness | P0 | U | Basal/bolus unit kinds and incomplete meal fixtures. Construct C3 request. | Source semantics and past-only timestamps retained; incompatible/missing inputs are rejected instead of fabricated. |
| GL-P05-005 — Model and checkpoint identity | P0 | U+C | Pinned Chronos C3 and missing/corrupt runtime fixtures. Warm/run model and inspect persisted identity. | Only approved model/revision/config executes; unavailable dependencies return readiness/error, not a synthetic replacement. |
| GL-P05-006 — Forecast shape and quantiles | P0 | U | Malformed count, timestamps, non-finite values and crossing quantiles. Validate adapter/transport/database result. | Only 24 future five-minute points with ordered finite quantiles persist; invalid output produces no partial result. |
| GL-P05-007 — Forecast save/read retry | P0 | C+B | Owned confirmed meal and idempotency key. Create, retry, reload and read persisted forecast. | One compatible forecast is reused; wrong meal/key conflicts; read representation matches persisted values. |
| GL-P05-008 — Immutable forecast input/history | P0 | C | Saved forecast followed by meal edit/source context replacement. Reload original result and inspect its input references/hash. | Original meal revision, origin/history/source/model identity remain reproducible; current rows cannot relabel old evidence. |
| GL-P05-009 — Cross-user forecast authorization | P0 | C | A/B meals, results and forecast points. Attempt create/read/list with another owner's IDs. | No unauthorized inference/result access; child points and summaries follow parent ownership. |
| GL-P05-010 — Busy, timeout and cancellation | P1 | C+B | One active bounded inference and overlapping request. Start overlap and trigger timeout/navigation. | Documented 429/bounded behavior, useful retry, released locks and no partial or duplicate results; cancellation policy is honest. |
| GL-P05-011 — Source freshness and unavailable context | P0 | U+B | Missing/stale/implausible glucose and unimplemented source. Open Home and request forecast. | No fabricated forecast/trend; clear freshness/source explanation and recoverable eligible-input path. |
| GL-P05-012 — Forecast chart conversion | P0 | U+B | Known mg/dL values with q10/q50/q90. Switch display units and inspect graph/30/60/120 summaries/table. | Consistent tested conversion/rounding; canonical stored values unchanged; interval is not a clinical confidence grade. |
| GL-P05-013 — Same-user past-outcome retrieval | P0 | U+C | Known numeric distances plus future/unavailable/foreign outcomes. Query similar meals at a fixed origin. | Only eligible owned past outcomes; deterministic rank and provenance; empty history is honest. |
| GL-P05-014 — Forecast history and deep links | P1 | C+B | Multiple owned results, source filters and pagination. Browse history and open direct result URLs. | Stable scoped list/detail; no results lost through pagination or source changes; not-found state safe. |
| GL-P05-015 — No dosing or automatic promotion | P0 | U+M | Core UI, notifications and research model artifacts. Review generated copy/actions and app model configuration. | No dosing, pump/clinical-safe claims or automatic LightGBM promotion; current research limitations remain visible. |

## P06 - Home feed and nutrition aggregation

| Case | Priority | Layer | Setup and action | Expected result / validation oracle |
|---|---|---|---|---|
| GL-P06-001 — Shared consumed-day aggregate | P0 | U+C | Known eaten, planned, cancelled, copied and scenario records. Load Home/Meal log/Nutrition for same day. | All pages agree with independently calculated eaten totals; other states are excluded. |
| GL-P06-002 — Timezone and DST boundaries | P0 | U+C | Records at local midnight, DST transition and UTC boundaries. Query dates in multiple IANA zones. | Correct exclusive day boundaries for 23/24/25-hour days; each eaten meal counted exactly once. |
| GL-P06-003 — Timezone preference changes | P1 | C+B | Historical UTC instants with updated timezone. Change zone and revisit dates. | Grouping recomputes consistently without rewriting stored instants or mixing simulator wall clock. |
| GL-P06-004 — Nutrient coverage and empty state | P0 | U+B | Complete, partial, no-meal and retrieval-failure fixtures. Inspect nutrient totals and coverage. | Unknown/partial/no meals/unavailable remain distinct; no missing-value zero fill or misleading goal ring. |
| GL-P06-005 — Pagination-independent totals | P0 | C | Meal count spanning several pages. Compare summary with all expected records while paging. | Totals use full scoped dataset, not visible cards; bounded server queries stay consistent. |
| GL-P06-006 — Edit/cancel/retry propagation | P0 | C+B | Consumed meal displayed across all three pages. Edit/cancel it, retry and refresh. | All summaries update once, respect revisions and show no stale private cache. |
| GL-P06-007 — Optional goals and history | P1 | U+C | No goal and goals with different effective intervals. View day/week before and after goal changes. | No invented default target; correct units/effective date and goal progress; no clinical deficiency claim. |
| GL-P06-008 — Seven-day nutrition trend | P1 | U+B | Known daily values with missing days. Select date/range and inspect graph/table. | Correct chronology/local dates, units and unknowns; aggregate matches daily values. |
| GL-P06-009 — Glucose-first Home behavior | P1 | B | History only, eligible forecast and unavailable source states. Open Home at mobile/tablet/desktop. | Source/clock and chart lead; forecast only when eligible; nutrition and meal actions remain discoverable. |
| GL-P06-010 — Catalog discovery fallback | P1 | B | Published catalog and unavailable catalog fixtures. Open recommended/browse area. | Source-backed content or useful unavailable/search state; no invented personalized or clinical recommendation. |
| GL-P06-011 — Account/source cache partition | P0 | C+B | A/B identities and two simulation sessions. Switch account/source with stale requests in flight. | No foreign/previous-source data flashes or late response overwrites; keys and invalidation honor context. |
| GL-P06-012 — Date-range and unit validation | P1 | U+C | Invalid zones, ranges and extreme/malformed query values. Request dashboard/nutrition summaries. | Bounded validated requests and clear errors; no unbounded scan or silent unit reinterpretation. |

## P07 - Validated catalog, search, detail and favorites

| Case | Priority | Layer | Setup and action | Expected result / validation oracle |
|---|---|---|---|---|
| GL-P07-001 — Corrected release admission | P0 | C | Approved manifest plus known-bad corrected-release fixtures. Check IDs, mappings, energy, quantities, yield, missingness and attribution. | Only a validated release is published; unresolved defects block activation and are reported. |
| GL-P07-002 — Catalog import and capacity | P0 | C | Approved compact release and dedicated cloud-dev target. Preview/load bounded staging, verify counts/FKs/checksums/indexed size. | Correct release/dependency closure with capacity headroom; no source writes or customer/health records imported. |
| GL-P07-003 — Catalog access and ingestion authority | P0 | C | Browser A/B and approved ingestion identity. Read published facts and attempt browser writes/staging reads. | Only allowed published data readable; ingestion/staging writes restricted; private app rows remain owner-scoped. |
| GL-P07-004 — Recipe/product tabbed search | P1 | C+B | Known catalog items and source IDs. Query both tabs and navigate pages. | Correct type/scoped results, stable IDs/counts and labeled source; explicit external fallback is separate. |
| GL-P07-005 — Query/filter/sort URL state | P1 | U+B | Known text, filters and sort options. Apply/change/reset, reload and use back/forward. | State round-trips safely and supported filters/sorts produce independent expected results. |
| GL-P07-006 — Autocomplete and keyboard | P1 | B | Recent/suggestion fixtures with mobile keyboard. Type, navigate suggestions and submit. | Accessible selection and visible input/actions; no unsupported silent search or private query leak. |
| GL-P07-007 — Empty versus unavailable catalog | P1 | U+B | Zero match, filter exclusion, timeout and unpublished release. Search each and recover/reset. | Correct distinct state and recovery; errors are not reported as zero results. |
| GL-P07-008 — Unsupported and malicious query values | P0 | U+C | Oversized text, encoded delimiters and unsupported filters. Submit search requests. | Input/range limits enforced and safe parameter handling; no server error or invented health/store filter. |
| GL-P07-009 — Recipe detail serving basis | P0 | U+C+B | Known recipe yield and ingredient quantities. Change serving preview and enter common composer. | Ingredient/per-serving/whole-recipe math and source release agree; missing facts stay explicit. |
| GL-P07-010 — Product detail nutrition basis | P0 | U+C+B | Known barcode/pack/serving/per-100-g facts. Inspect detail and choose grams/servings. | Pack and consumption bases stay distinct; composer matches verified source snapshot. |
| GL-P07-011 — Catalog update and old meal snapshot | P0 | C | Saved meal from release A, publish release B. Reopen detail and saved meal. | Detail identifies new release; old consumed revision/forecast nutrition remains unchanged. |
| GL-P07-012 — Favorite add/remove idempotency | P1 | C+B | Owned user plus published recipe/product. Toggle repeatedly, refresh and retry after timeout. | One typed favorite per item/owner; removal is durable; no eaten meal is created. |
| GL-P07-013 — Favorite ownership and FK safety | P0 | C | A/B favorites and invalid/deleted catalog IDs. Attempt cross-user reads/writes and broken references. | Owner isolation and valid typed references; unavailable/deleted item handled without unrelated data exposure. |
| GL-P07-014 — Favorite-to-meal journey | P1 | C+B | Saved recipe and product favorites. Open favorite and review/log a chosen portion. | Uses same composer/source math and consumption semantics as search; no duplicate backend logic. |
| GL-P07-015 — Attribution and safe content | P0 | M | Catalog text/images/allergen metadata and missing assets. Review detail/results at supported layouts. | Attribution and unknowns displayed; safe escaped content/image fallback; no allergy-safe/condition-safe or unsupported retail promise. |

## P08 - Profile, settings, privacy and notifications

| Case | Priority | Layer | Setup and action | Expected result / validation oracle |
|---|---|---|---|---|
| GL-P08-001 — Profile persistence and validation | P1 | C+B | Owned profile with long/invalid nickname. Edit, reload and test invalid values. | Valid data persists once; safe length/escaping and errors; another owner cannot edit. |
| GL-P08-002 — Settings unit/timezone/source changes | P0 | C+B | Owned preferences and open Home/history tabs. Change each setting and reload. | Settings and dependent views agree; source eligibility and canonical units maintained. |
| GL-P08-003 — Notice and optional preference updates | P1 | C | Versioned acknowledgements and food/notification preferences. Update/withdraw optional choice and review audit trail. | Required notice history retained appropriately; optional changes respected; no expanded medical collection. |
| GL-P08-004 — Password change and sensitive actions | P0 | C+B | Signed-in synthetic user with recent-auth requirements. Change password and attempt stale-session sensitive action. | Supabase-approved verification/recovery used; failures safe and passwords never stored in app tables. |
| GL-P08-005 — Privacy export scope | P0 | C | A/B synthetic records and documented export contract. Request A export and inspect sanitized payload/artifact. | Only A's permitted data with defined source/model metadata; no keys, B records or research dataset export. |
| GL-P08-006 — Account deletion lifecycle | P0 | C+B | Synthetic account with linked children and documented retention policy. Verify current password, exact DELETE and acknowledgement; delete immediately with no recovery window and retry safely. Inject private-file failure, test queue retry and A/B isolation, session/refresh denial and browser cleanup. | Approved deletion/retention rules enforced with FK-safe cleanup, revoked access and no cross-user effect; unavailable lifecycle is not falsely advertised. |
| GL-P08-007 — Help/privacy/terms accuracy | P1 | M | Current product scope and configured providers. Review public pages and in-app notices. | Clear research/data-use/retention/source limitations and functioning support links; no unsupported security/medical claims. |
| GL-P08-008 — Owned notification creation | P0 | C | Real app event and a browser fabrication attempt. Complete event and attempt direct custom system event insertion. | One trusted owned nonclinical event; browser cannot forge another owner or authoritative event. |
| GL-P08-009 — Notification read state and pagination | P1 | C+B | Owned read/unread events across pages. Open, mark read, mark all read and retry. | Stable counts/state persist; operations idempotent and apply only to the correct owner/range. |
| GL-P08-010 — Notification deduplication and stale links | P1 | C+B | Duplicate event delivery and removed/unavailable target. Retry event delivery and open notification link. | Deduplicated event, safe scoped deep link and useful stale-target recovery. |
| GL-P08-011 — Delivery preferences and medical boundary | P0 | U+M | In-app notifications plus opt-out delivery preference. Review event types and trigger a permitted event. | No glucose/clinical alarm or unapproved email/push/reminder delivery; optional preferences honored. |
| GL-P08-012 — Logout and lifecycle cache cleanup | P0 | C+B | Private data loaded in multiple routes/tabs. Logout or delete account and revisit cached routes. | Private content removed and protected API access denied; no cache survives into another account. |
| GL-P08-013 — Settings responsive and accessible flow | P1 | B+M | Long settings/privacy forms on mobile/tablet/desktop. Complete edit/error/confirmation journeys with keyboard. | All data/actions and confirmation consequences are readable; focus/keyboard/safe-area rules hold. |

## P09 - Portion comparison and later actual outcomes

| Case | Priority | Layer | Setup and action | Expected result / validation oracle |
|---|---|---|---|---|
| GL-P09-001 — Portion recalculation oracle | P0 | U | Known ingredients at 50/75/100 percent and custom amount. Calculate scenario nutrients. | Deterministic scaled values match independent math with documented rounding; invalid/zero/extreme amounts rejected. |
| GL-P09-002 — Shared-origin scenario requests | P0 | U+C | Confirmed meal and frozen pre-origin context. Request multiple portion forecasts. | Same model/origin/context with only approved meal changes; no later information enters any request. |
| GL-P09-003 — Scenario is not consumption | P0 | C+B | Saved eaten meal and portion comparisons. Compare repeatedly, refresh and inspect daily totals. | No extra eaten meal/outcome or inflated totals; scenarios have explicit separate identity. |
| GL-P09-004 — Comparison busy/partial/error states | P1 | C+B | Multiple scenarios and one invalid/busy result. Run comparison and recover. | Results retain labels/context; partial failures are explicit; no fabricated connecting line or uncontrolled slider requests. |
| GL-P09-005 — Quantiles and unit comparison | P0 | U+B | Known scenario outputs in both glucose units. Inspect plot/table/summary. | Correct comparable units/legend/interval; no recommended safe portion or dose label. |
| GL-P09-006 — Actual availability boundary | P0 | U+C | Future, incomplete and complete post-meal CGM fixtures. Request actual-vs-predicted view at each clock. | Actuals remain pending until genuinely available; incomplete coverage explicit; future values never enter inference/retrieval early. |
| GL-P09-007 — Actual matching and source identity | P0 | U+C | Two sessions/sources with nearby timestamps. Attach later observations to a forecast. | Correct source/session/origin alignment; no other user's or replay's outcome attached. |
| GL-P09-008 — Follow-up error calculation | P0 | U | Small known predicted/actual arrays with gaps. Compute displayed errors and coverage. | Independent expected error calculation; missing points handled by documented policy without overstated completeness. |
| GL-P09-009 — Outcome persistence and history | P0 | C+B | Eligible owned actual outcome. Save/retry/read and query later similar meals. | One durable outcome with available_at and provenance; retrieval includes it only after availability. |
| GL-P09-010 — Scenario and follow-up usability | P1 | B+M | Dense scenarios, small viewport and no-data state. Use keyboard/chart table and read explanatory copy. | All values/comparisons accessible; uncertainty/research boundary explicit; no clinical success claim. |
| GL-P09-011 — Controlled meal-response sensitivity | P0 | U+C | Frozen synthetic contexts, profiles/portions and repeated identical baselines from the [protocol](meal-response-validation-protocol.md). Run the real cached adapter with captured inputs. | Reproducible complete matrix and failure accounting, finite ordered quantiles, input isolation and reviewed sensitivity/invariance/stability; no causal or monotonic guarantee. |
| GL-P09-012 — Matching-outcome meal accuracy | P0 | C | Separately approved untouched matching-outcome windows and predeclared criteria. Compare persistence/CGM-only/full context. | Horizon/trajectory error, interval coverage/width, failure rate and participant uncertainty reported by eligible strata; no reused consumed test cohorts or unmatched replay truth. |

## P10 - Hosted deployment, resilience and release acceptance

| Case | Priority | Layer | Setup and action | Expected result / validation oracle |
|---|---|---|---|---|
| GL-P10-001 — Portable runtime build | P0 | C | Pinned Linux images and simulator source; no local Supabase. Build web/API and isolated simulator, start on test host. | Reproducible runtime without Windows paths, private datasets or development venv copies; managed cloud connection used. |
| GL-P10-002 — Public versus private build configuration | P0 | U+C | Environment-specific API/Auth origins and private secret canaries. Build, inspect browser assets and start configured images. | Correct cloud/origins at build/runtime; no private secret in client/image layers; stale public-config build is detected. |
| GL-P10-003 — HTTPS/proxy and private ports | P0 | C+B | Staging domain, reverse proxy and approved redirects. Exercise direct links/API/Auth/camera and inspect exposed listeners. | HTTPS workflows work; API/database/admin internals are not unintentionally public; exact CORS/redirect rules hold. |
| GL-P10-004 — Readiness versus liveness | P0 | C | Cold/warm model and unavailable simulator/database fixtures. Start/restart and query operational states. | Liveness is distinct from dependency/model readiness; no ready claim before required runtime is usable. |
| GL-P10-005 — Bounded concurrency and budgets | P0 | C | Approved dev/staging load envelope and Phase 0 latency/memory budgets. Measure single/overlapping synthetic requests with bounded warm/cold samples. | Reported p50/p95/sample count/errors/whole-stack memory meet recorded budgets or fail gate; locks/artifacts remain safe without an unsupported user-capacity claim. |
| GL-P10-006 — Restart and cache persistence | P0 | C | Saved meals/results and warmed model/replay caches. Restart web/API/host processes. | Durable records survive; required caches/replays recover; no duplicate jobs or cross-run artifact corruption. |
| GL-P10-007 — Provider/cloud outage recovery | P0 | C+B | Controlled timeout/rate-limit fixtures and restored services. Exercise lookup/Auth/save/forecast failure and retry. | Clear degraded states, bounded retries, preserved data and no fake totals/results or leaked provider errors. |
| GL-P10-008 — Controlled migration release and rollback | P0 | C | Compatible prior/new app artifacts and reviewed schema change. Rehearse deploy/rollback against approved staging target. | One migration owner; compatibility manifest retained; previous app can recover without destructive hosted down-migration. |
| GL-P10-009 — Backup and restore proof | P0 | C | Approved synthetic backup and separate cloud scratch restore target. Restore and verify counts, relationships and access rules. | Recovery evidence and measured recovery time; source/production project untouched; no claim that VPS backup covers managed Supabase. |
| GL-P10-010 — Full cloud end-to-end journey | P0 | C+B | Cloud-dev synthetic user; verified food facts and real model. Register/verify, onboard, log meal, forecast, reload history, inspect nutrition/favorites/settings. | Correct durable identity/data through full workflow; real versus fixture/provider evidence distinguished. |
| GL-P10-011 — Physical-device and cross-browser UAT | P0 | M | Supported desktop/mobile browsers and one real camera device. Run agreed journeys, zoom, keyboard and representative viewport matrix. | Documented support coverage and no blocking data/action/accessibility loss; unsupported capabilities have tested fallbacks. |
| GL-P10-012 — Release evidence and defect gate | P0 | U+M | All mandatory case results and open defects. Reconcile catalog, results, traces and release manifest. | Required cases pass with matching revision/environment/evidence; unresolved security/data-integrity/high-priority defects or missing integrations prevent full acceptance. |
| GL-P10-013 — Safe production smoke and monitoring | P0 | C+M | Separately authorized production release and synthetic smoke account. Run bounded smoke checks and inspect redacted health/error monitoring. | Correct production target/schema/release; no destructive or stress tests, private-content logs or test data pollution; recovery owner identified. |
