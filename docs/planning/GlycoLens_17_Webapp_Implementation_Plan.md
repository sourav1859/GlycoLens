# GlycoLens phased web application implementation plan

## November 14: personal and simulation workspaces implemented

Plan 19 corrections to P01/P03/P04/P06/P07/P08/P09 are implemented: explicit workspace/source writes, current personal clock, independent totals/history, scoped drafts/requests and context-aware links/export. Earlier account-global source descriptions are historical where they control ordinary data; old result ledgers do not automatically pass this new contract. [Actual validation](../reports/workspace-separation-validation-2026-11-14.md) and [44-case ledger](../testing/workspace-separation-results.json): **28 PASS, 16 PARTIAL**. Changes remain local; human Chrome and other qualified gates are not claimed complete.

## November 14: local LightGBM selection enabled for user review

At the user's request, the existing local development runtime now exposes **LightGBM · research option** alongside default Chronos. The ignored local enablement flag is true; the running API's native bundle/digest/read-only mount were verified and real synthetic inference returned 24 ordered points. The shipped environment template remains disabled by default. This is a user-authorized local research exposure for manual testing, not completed L0–L4 acceptance, production enablement or a model default change. All existing history/artifact/owner checks remain enforced.

An existing meal attached to the short one-day source remains ineligible for native inference. Explicitly prepare the 48-hour research source and save a new reviewed meal at that source's clock; existing meal/source snapshots are unchanged. Current carbohydrates are the native meal predictor; matching-outcome accuracy and transferred interval coverage remain unvalidated. [Enablement and verification](../reports/local-lightgbm-enablement-2026-11-14.md). November 12 off-state descriptions below are historical checkpoints; their outstanding acceptance results remain valid.

## November 12 implementation outcome — current status

The supplemental C/L implementation is now present and tested through actual provider/API/cloud/CPU paths; [the 58-case ledger](../testing/m2-closure-lightgbm-results.json) records passes, partial evidence, failures and human blockers. Default Chronos is unchanged; native LightGBM/48h context/v2 signed bands/UI/export and disable/restart recovery are implemented. **GL-P09-011 completed but Chronos capability failed**; GL-P09-012 remains NOT_RUN. The 146-case ledger records that failure without importing supplemental passes or erasing prior publication history. [Actual report](../reports/m2-closure-validation-2026-11-12.md). Chrome/manual UAT, native presentation rehearsal/sign-off, normal native enablement and separate public-release dependencies remain open. Current changes stay local for review.

The dated planning/checkpoint entries below remain historical where they describe unexecuted work.

## November 12: supplemental closure/model plan and device scope

[Plan 18](GlycoLens_18_M2_Closure_and_LightGBM_Integration.md) supplies a detailed current-revision M2 closure track and separate
gated LightGBM integration track, with [58 designed tests](../testing/m2-closure-lightgbm-test-cases.md)
and a separate ledger (initially all NOT_RUN at planning time). It retains Chronos as default and requires a distinct
longer scenario, verified training-compatible inputs and versioned calibrated-band
contracts before opt-in enablement. No implementation/model promotion follows from
the plan. The user selected Chrome acceptance and explicitly deferred physical
camera; GL-P04-003/004 retain future acceptance with DEFERRED_BY_USER disposition,
not PASS. Browser fallback/manual barcode stays in current scope. Existing private
credentials and newly configured OFF contact are available; do not request keys
again. Broader P00-P10 acceptance and release gates remain distinct from M2.

November 12 source publication: [GitHub delivery authorization](../reports/github-checkpoint-delivery-2026-11-12.md) supersedes the earlier local-review hold for this checkpoint. No hosted deployment or phase acceptance is implied.

November 12: shared demo/header logout and clearer simulation names are implemented; root local Compose and Linux runtime are validated. P09 now includes the separate [meal-response sensitivity and matching-outcome gates](../testing/meal-response-validation-protocol.md), originally both NOT_RUN; current sensitivity failure is recorded above. The current 146-case ledger and [follow-up evidence](../reports/demo-logout-compose-review-2026-11-12.md) retain partial phase acceptance.

## Implementation checkpoint - November 11, 2026

Cloud schema, trusted writes, permanent-account development Auth/onboarding and
the responsive application shell are implemented. Common meal capture/history/
edit/cancel, immutable Chronos forecasts, Home/daily/seven-day consumed nutrition,
owned notifications/export, portion comparisons and genuinely later virtual
observations now have code and scoped test evidence. The original demo moved to
`/demo`; `/` is a public entry and private routes require account/onboarding.

This is a **partial validation checkpoint**, not full phase/release acceptance.
Corrected catalog/search/details/favorites, real email verification/recovery,
verified anonymous upgrade, provider retention/restore, physical-device/manual accessibility,
scratch replay/restore and hosted acceptance remain open. Keep these changes local
for review; scratch replay is explicitly deferred. See the
[implementation report](../reports/webapp-implementation-checkpoint-2026-11-11.md),
[ADR 0019](../decisions/0019-trusted-cloud-writes-and-frozen-source-context.md) and
[actual case ledger](../testing/webapp-validation-results.json). Earlier dated
prototype/preparation evidence below remains historical.

The user confirmed **immediate account deletion after explicit confirmation,
with no recovery window**. Password reauthentication, hard Auth deletion, owned
row cascades and retryable private-file cleanup are implemented and validated with
synthetic accounts. See [ADR 0020](../decisions/0020-immediate-account-deletion.md)
and [deletion evidence](../reports/account-deletion-validation-2026-11-11.md).
Provider backup/log retention, restore reconciliation and a support contact remain
public-release gates; there is no application undo snapshot.

**Version:** November 11, 2026. **Status:** staged implementation executed in cloud development; acceptance is PARTIAL and tracked per case.

Initial November 11 preparation verified the Glycolens cloud project through MCP, saved
URL/public/private provider configuration in ignored environment files, and added
modern server-key header support with legacy fallback. Eight focused offline
tests passed. No hosted schema, real Auth email or live food-provider test was executed.
A later user-approved USD 5 cap covered 16 live recipe-model comparison calls;
see [recipe validation](../reports/recipe-model-validation-2026-11-11.md).
The 146-case ledger now distinguishes actual implemented-checkpoint observations from pending full-phase acceptance. See [setup evidence](../reports/cloud-env-and-email-setup-2026-11-11.md).

## 1. Confirmed decisions and implementation boundary

The user confirmed:

- One Git repository for frontend, backend and forecasting code.
- **Cloud Supabase from now on**, using a **dedicated GlycoLens cloud development project** for application PostgreSQL, Auth, PostgREST and integration testing.
- First-release **email/password authentication with email verification and password reset**.
- Temporary development exception confirmed November 11: email/password signup uses automatic email confirmation in the dedicated cloud project, so development can proceed without SMTP. Live Auth settings were read and verified; synthetic confirmed-user password/login/RLS/onboarding checks now pass; real signup email ownership remains unproven. Verification/recovery email delivery remains a public-release requirement.
- Delivery of the **full agreed feature set in staged releases**, rather than a silent scope reduction.

[ADR 0018](../decisions/0018-cloud-supabase-and-staged-webapp-delivery.md) records these decisions. They are also in repository AGENTS.md for future sessions. Local web/API processes and offline fixture/unit tests remain useful; a local Supabase stack is no longer the application or required integration-test target. Historical local results remain historical.

Keep Next.js/TypeScript, plain CSS/reusable components, FastAPI modular monolith, canonical forecasting adapters and managed Supabase. Preserve the current Chronos C3 application model, research-only/simulated-data boundary, source provenance, no dosing/pump/clinical-safe claims, and corrected-catalog admission gate. Figma is a reference, not copied product scope. No hosted resources, migrations, Auth emails, paid calls or runtime changes have been executed by drafting this plan.

The [UI architecture](../architecture/responsive-webapp-ui.md) defines routes and component contracts. The [readiness review](../reports/repository-strategy-and-development-readiness-2026-11-10.md) identifies the existing code gaps. This plan owns implementation order, prerequisite tracking, tests and evidence gates.

## 2. Prerequisites and information needed from the user

Keep secret values in ignored server `.env`, `frontend/.env.local`, a password manager or the deployment/CI secret store. Share only non-secret identifiers/status in chat. Do not commit credentials, paste private keys/passwords into documentation, or expose privileged keys in a browser. Access should be scoped to the development project.

| Needed information/access | Required for | How it is used and handled |
|---|---|---|
| Dedicated cloud development project created or identified; project name/ref, region, URL and plan/quota status | P00-P01 | Non-secret identity establishes the exact allowed target. Confirm it contains no unrelated application data before migrations. No automatic paid project/plan purchase |
| Public Supabase project URL and publishable API key, or compatible legacy anon key | P01-P03 | Browser and user-scoped backend calls. Current code uses `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`; standardize names/key types in P00-P01 |
| Backend secret API key or compatible legacy service-role key | P01/P04 and controlled test administration | `SUPABASE_SECRET_KEY` is now supported for trusted food caching using the API-key header; legacy `SUPABASE_SERVICE_ROLE_KEY` is a fallback. Never use privileged keys for ordinary user reads or in `NEXT_PUBLIC_*`. Other admin paths need their own validation |
| One controlled migration access method: authenticated MCP with migration capability, CLI linking with DB password, or an appropriate TLS database connection | P01 | MCP is connected; retain every applied SQL change under versioned migrations and preview the exact target/diff before application. CLI/connection credentials are needed only if that path is selected; API keys are not database passwords |
| Supabase CLI login/organization access; CI access token only if automated CLI operations require it | P00-P01/P10 | Prefer user-controlled CLI login; a personal access token is not required in browser/backend app configuration. CI token stays in protected secrets |
| Local frontend/API origins, planned HTTPS domain and allowed verification/recovery callback URLs | P01-P03/P10 | Auth Site URL/redirect configuration, client build settings, explicit CORS and same-origin proxy plan |
| SMTP readiness: chosen provider, sender domain/address and verified DNS; SMTP host/port/user/password configured privately in Supabase | P03 email acceptance; before public release | Development Auth can proceed with the approved automatic-confirmation exception. Real verification/recovery delivery and actual inbox testing remain required; default restricted mail or automatic confirmation cannot pass these gates |
| Two dedicated synthetic test inboxes/accounts controlled by the user, and permission for bounded verification/reset test emails | P01/P03/P10 | A/B ownership checks and real email flows. Addresses/passwords stay private; reports use synthetic aliases |
| `LLM_API_KEY`, `LLM_MODEL`, provider/model access and a live-test request/spending cap | P04 | Existing parser uses OpenAI Responses structured extraction. Only recipe text/quantities go to the provider; no patient context. Credentials and paid-call permission are separate prerequisites |
| `USDA_FDC_API_KEY`; `OPEN_FOOD_FACTS_USER_AGENT` with appropriate project/contact identification and agreed call limits | P04 | Real food/barcode facts and source attribution. Private contact details stay in ignored config |
| Corrected recipe/product catalog release and manifest, authorized compact export or read-only source access, units/yields/IDs/mappings and source/license permissions | P07 | Validate before importing/publishing database search/detail data. Do not request source write access, customer records or an unbounded full database copy |
| Selected Hostinger provisioning status, approved SSH/access method, domain/DNS access, region and recovery destination | P10; packaging begins earlier | Private deploy access stays outside Git/chat. No plan purchase, server change or publication occurs merely from this draft |
| Separately authorized cloud scratch project/branch for fresh migration replay and restore; production project/target before public release | P01/P10 | These tests must not reset the main development project. Budget/plan eligibility must be confirmed; absent scratch/production access is a visible gate |
| Existing pinned model/checkpoint cache and reviewed simulator source/runtime availability | P05/P10 | Reuse approved artifacts through ignored caches/volumes. No research retraining, reserved-cohort reuse or automatic model download in ordinary CI |
| Preferred delivery date, intended demo usage/concurrency, supported real phone/browser for camera tests, and privacy/retention/support wording | P00/P08/P10 | Refines engineering budgets, UAT and account export/deletion policy. Course dates are not automatically extended |

The first credentials needed are the cloud project URL/ref, public client key, backend key and migration-access method. LLM/nutrition credentials are not blockers for shell/Auth work; provider fixtures support development but cannot pass live-provider acceptance.

Exact-target/run-intent guards are implemented in `scripts/dev/cloud_preflight.py` and the bounded cloud harness. Paid recipe calls use a conservative cloud reservation guard. Historical local helpers do not implement the new cloud workflow and must not be used as replacements.

### Decisions and open inputs

| Topic | State |
|---|---|
| Repository, cloud development target, initial Auth method, full staged delivery | Confirmed by the user |
| Exact cloud project/ref/region, API-key type and migration connection method | Glycolens cloud project/MCP access and ignored URL/publishable/secret-key configuration verified November 11. 14 canonical migrations applied and normalized SQL hashes verified; scratch replay deferred by user; hosted CI remains pending |
| Keep existing OpenAI parser; model and live-test budget | User selected `gpt-6-luna`, replacing `gpt-5-mini`; private model configuration/template updated and Responses/strict-schema contract retained. USD 5 total live-test cap approved. The 16-call synthetic comparison verified access and used estimated USD 0.00763580; representative accuracy/full P04 acceptance remain pending. Prior spend counts against subsequent tests; see the recipe validation report |
| Corrected catalog readiness/access | User confirmed not ready; use labeled fixtures/providers for development and activate only after validation |
| Hostinger/domain provisioning and target date | User confirmed VPS/domain are pending; no new fixed delivery date supplied |
| Application namespace | Recommendation: reuse existing `public` application migrations in the dedicated project, leave managed `auth` intact, and keep the future catalog in its separately reviewed schema. If a named `glycolens` schema is preferred, decide before migration because exposure/headers/grants/client paths must change |
| Production and scratch environment budget | Confirm before provisioning or enabling reset/restore-style acceptance; do not silently reuse production |
| Account deletion | Confirmed: immediate after password reauthentication and explicit confirmation; no recovery window. ADR 0020 implements hard deletion and retryable private-file cleanup; provider retention/restore remain release gates |
| Demo mode | Retain labeled synthetic/anonymous demo compatibility; permanent accounts are the primary new account path. Real patient data/Dexcom remain outside this implementation unless separately approved |

API keys are not all JWTs: modern publishable/secret keys belong on the supported API-key header, while user sessions use bearer JWTs. P01 must correct any raw REST assumption that a server secret itself is a bearer JWT. [Supabase API-key guidance](https://supabase.com/docs/guides/getting-started/api-keys).
Real email verification/reset requires suitable SMTP/delivery configuration and tests. [Supabase SMTP guidance](https://supabase.com/docs/guides/auth/auth-smtp).

## 3. Phase sequence, dependencies and effort

Estimates are **27-46 focused development days** for one developer including implementation, scoped test/repair and documentation, excluding external waits. They are planning judgments, not a commitment or a revision of official course dates. The full expanded application does not fit the remaining interval to the recorded November 13 M3 deadline; preserve a demonstrable core release and explicitly schedule later releases.

| Phase | Deliverable | Dependencies | Effort | Test cases |
|---|---|---|---|---|
| P00 | Baseline, cloud-safe configuration and executable CI | Non-secret project identification; current repository | 1-2 days | 8 |
| P01 | Cloud connection, migration baseline, RLS and trusted-write boundary | P00; cloud credentials/access | 2-3 days | 12 |
| P02 | Responsive shell and shared UI foundations | P00; frozen route/token contracts | 2-3 days | 10 |
| P03 | Permanent Auth and resumable minimal onboarding | P01/P02; SMTP/inboxes required for email acceptance, deferred during development | 3-5 days | 17 |
| P04 | Common meal capture/logging, scan and recipe analysis | P01-P03; provider credentials for live gates | 3-5 days | 19 |
| P05 | Cloud-backed simulation, forecast/retrieval/history extraction | P04; model/simulator readiness | 2-4 days | 15 |
| P06 | Home and shared daily/seven-day nutrition aggregation | P04/P05 and approved meal/time semantics | 2-4 days | 12 |
| P07 | Validated catalog search/detail and favorites | P04; corrected release admission | 3-5 days | 15 |
| P08 | Profile/settings/privacy and owned in-app notifications | P03/P04; event contracts; some links use P05/P07 | 3-5 days | 13 |
| P09 | Portion scenarios and actual-vs-predicted follow-up | P04/P05/P06; actual availability rules | 3-5 days | 10 |
| P10 | Hosted release, resilience, UAT and recovery proof | Packaging starts early; full release depends on all required phases | 3-5 days | 13 |

P02 can proceed alongside the cloud foundation once contracts are fixed. P08/P09 need not wait for an unavailable catalog. Packaging work starts early; hosted acceptance remains a final gate. A dependency delay is recorded, not hidden by replacing catalog/provider/model facts with fixtures.

Staged releases:

- **R1:** P00-P03, cloud-backed accounts/onboarding and responsive shell.
- **R2:** P04-P06, durable meal-to-forecast, history and Home/Nutrition.
- **R3:** P07-P08, validated catalog, favorites and complete account/event experience.
- **R4:** P09-P10, comparisons/follow-up and fully validated hosted release.

Each release declares which features/tests passed. R1/R2 delivery does not imply the full feature set is complete.

## 4. Phase work packages and gates

### P00 - Baseline, configuration and CI

**Work**
1. Review the accepted documentation and current working tree; preserve existing changes and establish a reproducible revision baseline through the normal delivery workflow.
2. Verify supported Python/uv, Node/pnpm and CLI in the normal shell; verify Docker as packaging work begins, without requiring a local Supabase stack. The review session's Python/uv visibility was limited; resolve availability before claiming test execution.
3. Define cloud-only project identity checks, protected secret loading, run IDs, synthetic fixture ownership and bounded email/provider/load budgets. No helper may overwrite cloud env with local keys.
4. Add missing client environment templates and document which values are public at build time versus private at runtime. Select SDK/raw REST key compatibility and CLI version deliberately.
5. Freeze API/error/versioning and route contracts. Start lightweight schema/client compatibility checks and independent numerical fixtures.
6. Wire executable offline Python/frontend/contract CI using commands proven locally; protected opt-in cloud jobs are separate. Do not add routine weight downloads, research datasets, paid calls or production secrets.
7. Record engineering budgets before evaluation. Proposed initial targets: ordinary API p95 <= 1.5s, warm single-flight forecast p95 <= 30s, cold readiness <= 120s and peak host memory <= 80% of allocated RAM under the approved small synthetic workload. These are unmeasured targets, revised only with an explicit documented decision; no user-count or clinical guarantee follows.

**Validation:** GL-P00-001 through GL-P00-008. Record actual command versions, sanitized reports, failed checks and remediation in the result ledger. No baseline check passes from historical evidence alone.

**Exit:** reproducible relevant baseline, functioning CI, accepted contracts/measurement budgets and cloud-safe configuration controls. Cloud connection can remain gated on credentials while UI foundation work proceeds.

### P01 - Create and connect the cloud application schema

**Work**
1. Read-only verify the exact development project, region, existing schema/history/exposed schemas, extensions and capacity. Review current four migrations for hosted compatibility; do not blindly apply to an unknown populated project.
2. Keep committed `supabase/migrations/` as the only application migration history. Preview reviewed migrations with an explicit cloud target and the pinned CLI's supported flags; apply through one controlled migration owner. Current CLI documentation/flags differ between major versions, so check the installed version/help rather than copying a command whose default target is ambiguous.
3. Reuse the existing entities, then add forward migrations for preferences, versioned onboarding/acknowledgements and optional goals. Prepare meal state/revision and immutable forecast-input changes for P04/P05; add later modules through their own migrations.
4. Keep Supabase Auth identity canonical. Do not create an application password store or replace managed Auth schema. Use timezone-aware instants and canonical nutrient/glucose units.
5. Write a table/RPC permission matrix: browser-managed preferences/drafts versus authoritative calculated totals, catalog facts, forecasts, outcomes and system events. Implement owner checks and narrowly trusted writes together; retain atomic saves while redesigning grants/RPC execution safely.
6. Update backend and frontend configuration to cloud dev. Handle the selected API-key type correctly; private server keys never enter client bundles. Add explicit CORS methods/preflight for actual new endpoints.
7. Build a cloud-safe DB/integration harness with exact-project allowlist, explicit opt-in, run-scoped synthetic users/fixtures and cleanup. Adapt existing assertions without invoking local start/reset scripts.
8. Verify schema/constraints/grants/RLS and cloud Auth/Data API access. Where hosted pgTAP/SQL testing is available, use transaction-scoped tests against an approved development/scratch target; retain REST/JWT tests because a DB-admin connection alone cannot prove user isolation.
9. Rehearse fresh migration replay in a separately authorized empty cloud scratch environment. If unavailable, record this acceptance as blocked; do not reset the main development project to simulate it.

**Validation:** GL-P01-001 through GL-P01-012, including A/B/unauthenticated and child ownership, trusted-write fabrication attempts, RPC compatibility, migration history and unrelated-data cleanup sentinels.

**Exit:** cloud project/schema verified, reviewed baseline applied with evidence, functional permitted transactions, denied unauthorized writes and no local Supabase dependency. Hosted schema is now applied; full exit remains open until remaining case coverage, including deferred scratch replay, is satisfied.

### P02 - Responsive design system and application shell

**Work**
1. Define GlycoLens tokens, typography, focus/touch states, spacing, cards, inputs, async states and adaptive dialog/sheet primitives.
2. Implement one route/navigation source: Home, Search, Meal log, Forecasts and Nutrition; account destinations expose Favorites, Profile, Settings, Notifications and Help.
3. Create public/Auth/app layouts, route loading/error/not-found boundaries and safe deep-link/return navigation. Hide unavailable actions or show honest dependency states.
4. Build fluid mobile single column, tablet rail/adaptive columns and desktop sidebar/grids. Design the missing tablet/reference counterparts explicitly.
5. Extract chart summary/table semantics and safe keyboard/safe-area behavior. Use viewport matrix 320/360/390/430, 768/820/1024 and 1280/1440/1920, including landscape/short height and long content.

**Validation:** GL-P02-001 through GL-P02-010. Browser checks plus manual screen-reader, zoom, keyboard, contrast and physical-device review. Do not equate a screenshot or accessibility scanner alone with full acceptance.

**Exit:** reusable shell/components and accessible representative layouts pass, without fake live metrics or copied Nutri-App branding/data.

### P03 - Permanent Auth and minimal resumable onboarding

**Work**
1. Configure real cloud email/password, confirmation/recovery templates, Site URL and exact redirects. Verify SMTP sender and designated inboxes before live emails.
2. Build signup, sign-in, check-email, callback, forgot/reset-password and logout with Supabase session refresh and neutral errors. Retain independently verified API authorization.
3. Persist minimal onboarding: confirmed IANA timezone, display unit, available data source and notice acknowledgement; nickname/food preferences/goals optional. No required body, diagnosis, insulin-regimen or child/family questionnaire.
4. Add step validation, resume/skip/review/edit, server-side versioned completion and concurrent-tab conflicts.
5. Implement deliberate anonymous-demo continuity/upgrade without email-based record transfer. Clear private caches on logout/source/account change.
6. Implement a minimal profile/settings surface needed for these preferences; complete its broader lifecycle in P08.

**Validation:** GL-P03-001 through GL-P03-017. Real inbox verification/reset evidence is separate from admin-confirmed synthetic user fixtures and mocked Auth responses.

**Exit:** sign up -> verify -> sign in -> onboard -> Home persists across refresh/session changes; A/B isolation, recovery and safe redirects pass.

### P04 - Common meal capture, logging, scan and recipe analysis

**Work**
1. Extract the current workflow into common composer/detail/history features and routes: meal new/detail/edit, scan and recipe analyzer.
2. Implement validated search/barcode/manual-code entry and bounded provider adapters. Stop camera streams on finish/navigation; retain manual fallback.
3. Keep structured recipe extraction editable and limited to ingredient/quantity/serving drafts. Ground food facts and quantities before deterministic calculations; allow manual ingredient entry during provider failure.
4. Add cloud migrations/API contracts for planned/logged/cancelled state, consumed timestamp/slot, revisions, optimistic conflicts, immutable food facts and idempotent atomic saves.
5. Implement daily/paginated meal history, edit/cancel/remove confirmation and copy-as-new-draft semantics. Keep source/session ownership and unknown nutrients explicit.
6. Activate only reviewed live provider paths after key/configuration/unit/provenance tests. Enforce approved LLM request/spend caps and no patient context in provider requests.

**Validation:** GL-P04-001 through GL-P04-019. Independently calculated gram/yield/fraction/repeated-ingredient oracles, failure atomicity, bounded real USDA/LLM evidence and Chrome/manual-barcode coverage are required. Physical-camera evidence is deferred by the November 12 user scope decision, retained for future full-device acceptance.

**Exit:** every entry path leads to the same durable reviewed meal contract; consumption/history/edit/retry semantics pass. Fixtures cannot close live-provider gates; physical-camera acceptance remains explicitly deferred and unpassed.

### P05 - Cloud-backed source context, forecast and personal history

**Work**
1. Run the reviewed simulator/replay with cloud-owned app persistence and explicit simulated clock; make interpreter/source paths portable without importing incompatible simulator dependencies into the API.
2. Preserve 24 regular pre-origin history samples, C3 unit semantics and origin-known meal facts. Keep future glucose/outcomes outside inference.
3. Retain the pinned model/common adapter, bounded single-flight execution, safe unavailable/busy/retry behavior and model identity.
4. Add immutable meal revision/context/input snapshot or verifiable references/hash before exposing editable historical evidence. Existing reads must not rebuild an old result's history from unrelated replacement rows.
5. Extract forecast list/detail and numeric historical retrieval into dedicated routes, with source/date/owner pagination and no future-outcome contamination.
6. Present median/interval, source/freshness, 30/60/120-minute values, display-unit conversion and chart table. Do not introduce clinical confidence grades or automatically promote research results. Plan 18 separately gates the user-approved opt-in LightGBM option; Chronos stays default.

**Validation:** GL-P05-001 through GL-P05-015. Offline contract/leakage/invalid-grid tests plus real cloud save/read/retry and actual approved model/simulator runs; no training/reselection.

**Exit:** confirmed cloud meal -> validated real model -> persisted immutable result/history passes, with safe failures and evidence labeling.

### P06 - Home feed and Nutrition

**Work**
1. Implement one server consumed-meal aggregate for Home, Meal log and Nutrition, scoped by identity, source/session, selected local day/timezone and nutrient completeness.
2. Handle midnight/DST, timezone changes, pagination-independent totals, edits/cancellation and cache invalidation.
3. Show glucose/source/clock and eligible forecast first, meal action, consumed nutrition/daily meals, then catalog discovery when available.
4. Build daily/seven-day nutrition views and accessible charts/tables. Optional goals have units/effective dates; no default calorie prescription or deficiency/medical safety advice.

**Validation:** GL-P06-001 through GL-P06-012 with independently known totals, 23/24/25-hour day boundaries, missing values, goal changes and account/source in-flight request switching.

**Exit:** all three pages agree on trustworthy totals/history and remain usable across target layouts; known empty and unavailable are distinct.

### P07 - Corrected catalog, database search/details and Favorites

**Work**
1. Admit only an approved corrected release: IDs/mappings, quantity/yield/energy bases, dependency closure, attribution/license and missingness checks.
2. Preview and stage bounded import into the reviewed cloud catalog schema. Verify actual indexed size, target budget, counts/FKs/checksums and rollback package before publication.
3. Build product/recipe tabs, query/filter/sort/pagination URL state, autocomplete and genuine empty/unavailable recovery. Offer supported data filters only.
4. Build recipe and product detail with correct whole/serving/per-100-g/pack semantics, ingredient/provenance sections and common composer actions.
5. Add typed owner-scoped recipe/product favorites with FK/uniqueness and idempotent toggle; favorites are not consumed meals.
6. Separate catalog updates from saved meal/forecast snapshots. No retail inventory/price/geolocation or family/condition-safe claims.

**Validation:** GL-P07-001 through GL-P07-015. Publishing is blocked by bad units/mappings/yields, missing permission or insufficient capacity; UI fixtures can advance design but not release admission.

**Exit:** actual validated cloud database search/detail/favorites pass. If correction is pending, the phase remains pending while independent phases continue.

### P08 - Profile, settings, privacy and Notifications

**Work**
1. Complete profile/settings/preferences/connections with consistent unit/timezone/source behavior and safe sensitive-account flows.
2. Define and implement account export/deletion/retention behavior with verified ownership, reauthentication and FK-safe cleanup. Help/privacy/terms must accurately reflect real capabilities and providers.
3. Add owner-scoped, trusted in-app notification events, safe entity links, deduplication, read/unread counts and bounded pagination/mark-all-read.
4. Support only nonclinical application events. Email/push delivery, scheduled meal reminders and medical alarms are not automatically added; separate opt-in/infrastructure work is required if later requested.
5. Ensure account lifecycle and logout clear private route/query/service-worker state.

**Validation:** GL-P08-001 through GL-P08-013, including no cross-user export/deletion/event effects and no browser-fabricated system events.

**Exit:** persistent account/settings and data controls, accurate public notices and real event-backed notification center pass.

### P09 - Portion scenarios and later actual response

**Work**
1. Recalculate 50/75/100/custom portions from grounded facts, using the same frozen origin/context/model for comparable scenarios.
2. Store scenarios separately from consumption; bound requests and avoid inference on every slider movement.
3. Attach actual post-meal observations only after genuine source/session availability, preserving coverage and chronology.
4. Compute validated error/coverage summaries, persist actual outcomes with available_at and expose eligible later personal evidence.
5. Keep units/quantiles/source/research limitations accessible in graph/table/comparison layouts.
6. Execute the [meal-response validation protocol](../testing/meal-response-validation-protocol.md): controlled frozen-context meal/portion sensitivity and reproducibility first, then separately approved matching-outcome accuracy. Input wiring or different output alone is insufficient evidence. Current fixed simulator outcomes are not matched to arbitrary user meals; consumed primary/PEDAP cohorts remain unavailable for new independent claims.

**Validation:** GL-P09-001 through GL-P09-012, with the separate sensitivity/outcome protocol, hand-computed scaling/error arrays, missing actuals, cross-source collisions and early-future retrieval rejection.

**Exit:** comparable scenarios and genuine follow-up work without inflating nutrition totals, leaking future data or recommending a dose/safe portion.

### P10 - Hosted delivery, resilience and release acceptance

**Work**
1. Use root `compose.yaml` for one-command local startup (ADR 0021), with `infra/compose.yml` retained as a separate hosting template. Begin packaging earlier: pinned Linux web/API images, isolated simulator, explicit Docker build exclusions and persistent model/replay volumes. Keep application DB/Auth managed in cloud Supabase.
2. Configure the selected host, HTTPS reverse proxy, environment-specific public build settings, private runtime keys and exact Auth/CORS origins.
3. Add liveness versus model/simulator/dependency readiness, bounded concurrency, CPU/thread limits and redacted monitoring. Begin with one model/API worker; process-local locks do not coordinate replicas.
4. Run bounded cold/warm/overlap measurements against P00 budgets, reporting sample sizes and actual errors/memory/latency. No unsupported concurrency guarantee.
5. Rehearse migration release, compatible app rollback, host restart and managed-database backup/restore into a separately authorized cloud scratch target. VPS backup alone does not cover managed Supabase.
6. Complete physical phone/cross-browser UAT and full cloud journeys using synthetic accounts and real approved provider/model paths.
7. Reconcile every mandatory case, unresolved defect and release manifest. Publish only after the separate concrete deployment authorization/target configuration; execute a small non-destructive production smoke, never the full mutation/load suite against production.

**Validation:** GL-P10-001 through GL-P10-013. Missing production/scratch/SMTP/catalog/provider evidence remains a visible gate; no "all passed" from fixture success.

**Exit:** release evidence, recovery and UAT pass at the exact artifact/schema/model versions; no unresolved security/data-integrity or release-blocking defects.

## 5. Test execution, validation and result recording

The [test-case catalog](../testing/webapp-cloud-test-cases.md) contains **146 named cases across 11 phases**, with layer, setup/action, expected result and priority. The [result ledger](../testing/webapp-validation-results.json) now contains actual observations and remaining PARTIAL/BLOCKED/NOT_RUN coverage. The catalog remains the acceptance contract; executable unit/browser/cloud checks cover stated subsets without claiming every catalog case is closed.

### Feature-to-test traceability

All cases in the catalog remain required for full acceptance; these mappings identify
the main cases for each user-facing capability and shared engineering change.

| Feature/change | Owning phases | Main case references |
|---|---|---|
| Cloud schema, Auth/Data API connection and isolation | P00/P01 | GL-P00-003, GL-P01-001, GL-P01-003, GL-P01-006, GL-P01-007 |
| Signup/login, verification/reset and account sessions | P03 | GL-P03-001, GL-P03-003, GL-P03-005, GL-P03-006, GL-P03-007 |
| Resumable optional/minimal onboarding | P03 | GL-P03-010, GL-P03-011, GL-P03-012, GL-P03-013, GL-P03-016 |
| Responsive navigation, shared dialogs and accessible charts | P02 | GL-P02-001, GL-P02-002, GL-P02-003, GL-P02-004, GL-P02-009 |
| Meal capture/log/history/edit/cancel/copy | P04 | GL-P04-008, GL-P04-011, GL-P04-012, GL-P04-014, GL-P04-015, GL-P04-016, GL-P04-017 |
| Product scan and fallback | P04 | GL-P04-002, GL-P04-003, GL-P04-004 |
| Recipe analyzer/LLM validation | P04 | GL-P04-005, GL-P04-006, GL-P04-007, GL-P04-008 |
| Glucose data/forecasts, summaries, history and similar meals | P05 | GL-P05-001, GL-P05-003, GL-P05-006, GL-P05-008, GL-P05-012, GL-P05-013, GL-P05-014 |
| Home daily feed and nutrition totals/trends/goals | P06 | GL-P06-001, GL-P06-002, GL-P06-004, GL-P06-007, GL-P06-008, GL-P06-009 |
| Database recipe/product search and filters | P07 | GL-P07-001, GL-P07-004, GL-P07-005, GL-P07-006, GL-P07-007 |
| Recipe detail and product detail | P07 | GL-P07-009, GL-P07-010, GL-P07-011, GL-P07-015 |
| Favorites page and add/remove/reuse | P07 | GL-P07-012, GL-P07-013, GL-P07-014 |
| Profile/settings/connections and privacy/help | P08 | GL-P08-001, GL-P08-002, GL-P08-004, GL-P08-005, GL-P08-006, GL-P08-007 |
| Owned in-app notifications | P08 | GL-P08-008, GL-P08-009, GL-P08-010, GL-P08-011 |
| Portion comparison and actual follow-up | P09 | GL-P09-001, GL-P09-002, GL-P09-003, GL-P09-006, GL-P09-008, GL-P09-009 |
| CI, deployment, performance, recovery and full UAT | P00/P10 | GL-P00-004, GL-P00-005, GL-P10-001, GL-P10-005, GL-P10-009, GL-P10-010, GL-P10-012 |

For every implemented change:

1. Add meaningful tests at the lowest layer that proves its behavior before calling the change complete. Update an existing relevant test rather than duplicating the same assertion at every layer.
2. Run the narrow changed calculation/API/component tests, then dependent database/cloud or browser checks, and the relevant release journey. Broaden only for changed boundaries, failures or unresolved concerns.
3. Record expected and actual values, run/revision/environment, evidence locations and defects. A fixture test cannot satisfy a cloud, physical camera, real mail/provider or model requirement.
4. Repair failures and rerun affected cases; retain the original failed run and distinguish it from the successful recheck. A skipped test is not passed.
5. Update affected living docs, phase status and implementation handoff in the same work cycle.

Result states: NOT_RUN, RUNNING, PASS, FAIL, BLOCKED or WAIVED. PASS requires actual observations, execution time, run/revision and redacted evidence; BLOCKED requires a specific unmet prerequisite. Any waiver is an explicit scope decision with owner/reason and cannot silently waive authorization, data-integrity, future-leakage or secret-exposure gates. All listed P0/P1 cases are required for full-feature acceptance.

Evidence package per phase:

- Exact code revision, migration IDs/checksums, app/config/model/release identities and cloud target alias.
- Redacted unit/contract reports, SQL/schema/RLS assertions and synthetic API traces as appropriate.
- Browser traces/screenshots for representative viewports, manual accessibility/device/email protocols and approved live-provider request counts.
- Numerical oracle comparison, cloud fixture cleanup proof, performance metrics/sample sizes when applicable, and defect/retest record.
- A short phase report with delivery status, expected-versus-actual results, blockers, risks and next action.

Raw logs/screenshots that could contain private configuration stay ignored/redacted; checked-in reports contain only sanitized evidence summaries. Do not store patient data or private test inboxes in the ledger.

### Where the cases become executable

| Layer/tool | Implementation location and execution contract |
|---|---|
| Python calculations/API/contract checks | Existing `backend/tests/` and relevant `tests/` modules; add/change focused pytest cases. Existing command family: `uv run pytest -q <affected-test-path>` after P00 verifies the normal-shell toolchain |
| Frontend components/clients | Existing feature/component test files under `frontend/src/`; Vitest/Testing Library. Existing root `pnpm frontend:check` runs lint, tests, typecheck and build; use narrow tests during edits |
| Cloud DB/Auth/RLS integration | Planned guarded `tests/cloud/` and cloud runner under `scripts/dev/` or `scripts/database/`; adapt existing `supabase/tests/` SQL assertions to an approved remote execution method. Implement target/run/cleanup guards before execution |
| Browser journeys | Existing `frontend/e2e/` and Playwright; separate deterministic fixture journeys from explicit cloud-dev real Auth/API runs. Adapt the current Windows/live-local server launch contract before claiming cloud portability |
| Model/simulator boundaries | Existing adapter/context tests plus explicit real-model/simulator opt-in; run only needed contract regressions and approved real acceptance, without retraining/reserved-cohort access |
| Device/accessibility/email/restore | Named manual protocols in phase reports, with device/browser/target identities and expected/observed evidence; automation supplements rather than replaces these checks |

New cloud runner paths/flags are proposed deliverables, not executable commands in
the current repo. Preserve redacted per-run artifacts under ignored
`.cache/webapp-validation/<run-id>/`; commit sanitized phase summaries and update
the result ledger with actual observations. Retain failed and retest runs instead
of overwriting their history.

### Validation gates

| Gate | Required result |
|---|---|
| Per change | Relevant behavior tests and contracts pass; reviewed source/docs consistent |
| Cloud schema | Correct project, migration history/schema/constraints, owner + trusted-write matrix and safe cleanup pass |
| Per phase | Every required phase case passes with evidence, or phase remains visibly incomplete |
| Per staged release | Implemented subset and regression journey pass; unimplemented features are explicitly disclosed |
| Full feature acceptance | All required cases pass, real integration/device evidence exists, no unresolved P0/data-integrity/security defect |
| Public release | Full applicable release evidence plus authorized production configuration, recovery proof and bounded smoke pass |

## 6. Cloud migration and operational safeguards

- Never run `supabase db reset`, local stack start/restart, legacy `Configure-LocalDemo.ps1` or local-reset wrappers as the new application setup/test path. Do not wipe a hosted project to recreate the old local test workflow.
- All migrations remain Git-reviewed and reproducible; use explicit, version-verified cloud target selection, preview and one controlled apply path. [Supabase local/hosted target guidance](https://supabase.com/docs/guides/local-development/local-and-hosted-projects) and [CLI reference](https://supabase.com/docs/reference/cli/introduction).
- Use only run-scoped synthetic fixtures in cloud integration tests; clean up recorded resources from that run. Verify JWT-level APIs and database grants in addition to admin SQL checks. [Database testing guidance](https://supabase.com/docs/guides/database/testing).
- Do not copy anonymous local users or local health timelines into cloud by default. Fresh synthetic cloud users/data are the default. Any local record migration needs a separate reviewed inventory and owner-mapping plan.
- Keep development and production targets/keys distinct. Scratch replay/restore tests require a disposable approved cloud target, not a destructive operation on shared development data.
- Private research cohorts, raw CGM exports, training/batch workloads and Graphify stay outside hosted application data/runtime. Current source/model scientific boundaries remain unchanged.

## 7. Current status and next action

This cycle drafts the plan, test cases, result ledger and durable cloud-first project memory. No phase implementation or listed cloud/application test has run. Documentation consistency/traceability checks are recorded in the [planning handoff](../tooling/cloud-webapp-plan-handoff-2026-11-10.md).

First next action: complete P00 toolchain/CI/cloud-guard readiness using the verified MCP target and private environment configuration, then present the concrete P01 migration diff/target summary before controlled application. Carry forward the USD 5 total LLM test cap and recorded usage; prepare release SMTP/domain delivery independently. Catalog and hosting remain separate gates and do not block shared UI foundation work.
