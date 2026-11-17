# Milestone 3 status and critical audit

**Audit date:** November 16, 2026, America/New_York.  
**Inspected code baseline:** 7ce5f608b6dcd93684d59e8ae48a8630659c84df, plus the existing uncommitted November 14 catalog documentation updates.  
**Overall finding:** substantial research and prototype engineering are delivered; Milestone 3 is not ready for unqualified closure.

The recorded work deadline was November 13; M3 A was November 10 and M3 B is November 17. No revised course deadline was found. The expanded web application plan explicitly estimates 27–46 focused development days and says it does not fit the original remaining interval. The work after November 13 is useful progress, but cannot establish completion by the recorded deadline.

## Basis and interpretation

The maintained [milestone schedule](../planning/GlycoLens_06_Milestones_and_Schedule.md#milestone-3---integration-analysis-and-verification) is the task authority, together with Plans 17–19 and their actual-result ledgers. The older planning pack outside the repository is historical; it lacks the later cloud, catalog and responsive application work.

This audit maps every bullet/checklist item in the M3 section into **39 review rows**. These are the plan's overlapping work items, not 39 independent features:

| Assessment | Rows |
|---|---:|
| Completed within the stated task scope | 11 |
| Partial | 21 |
| Pending, dependent on catalog admission | 6 |
| Explicitly deferred / conditional | 1 |
| Total | 39 |

These counts are an audit classification, not a project completion percentage. A small planning decision and a multiweek deployment package have different effort and risk. A completed experiment may have an unfavorable result. A partial feature can contain implemented code, passing tests and a failed capability gate.

Completed means the bounded task has supporting implementation or recorded research evidence. Partial means some implementation/evidence exists but its combined acceptance is open. Pending means the required delivered outcome has not occurred. Deferred is an intentional scope decision rather than a failed test.

Important evidence is source-verified below. Previously executed cloud/provider/model results are identified as recorded evidence; this audit did not repeat paid calls, cloud writes, research inference, clinical-data access, deployment or manual browser acceptance.

## Full Milestone 3 task inventory

### Responsive UI and page extraction

Source: [M3 UI checklist](../planning/GlycoLens_06_Milestones_and_Schedule.md#responsive-ui-architecture-and-page-extraction---november-10), [Plan 17](../planning/GlycoLens_17_Webapp_Implementation_Plan.md), [workspace validation](workspace-separation-validation-2026-11-14.md).

| ID | Planned task | Assessment | What exists / what remains |
|---|---|---|---|
| U01 | Inspect supplied Figma nodes and document adaptation boundaries | Completed | Recorded 44 unique nodes / 45 references, audit and ADR 0017. This is completed design evidence. |
| U02 | Define routes, shared components, onboarding, responsive rules, schema/API proposals and acceptance | Completed | Product specification, responsive architecture, Plan 17 and test catalogs exist. |
| U03 | Slice A: tokens/navigation, permanent Auth, persisted onboarding/preferences, basic account/source/help/privacy, demo fallback | Partial | Shell, password sign-in, onboarding, settings, export/deletion and separate demo are implemented. Real verification/recovery delivery, anonymous continuity and complete manual acceptance remain open. |
| U04 | Slice B: route-based meal/scan/text/forecast workflows, history, consumed totals, Home and Nutrition | Partial | Common composer/detail/history, provider adapters, immutable forecasts and daily/seven-day totals exist. Real API/cloud and browser evidence covers a subset; all input/failure/manual variants are not accepted. |
| U05 | Slice C: corrected-catalog search/details/favorites and owned notifications | Partial | Owned notifications are implemented. Catalog admission, search/detail data and favorites are pending; route placeholders are not functioning catalog features. |
| U06 | Slice D: portion comparison and actual-versus-predicted follow-up with frozen inputs | Partial | Frozen-model scenarios, later-observation gating, persistence and metrics exist. Chronos meal-response capability failed; matching-meal accuracy and combined browser acceptance remain open. |
| U07 | Verify mobile/tablet/desktop, keyboard/zoom/safe areas, account/source switching and isolation | Partial | Automated viewport, request-boundary, two-tab and owner-isolation evidence exists. Human Chrome/assistive/zoom checks and full live-provider/browser paths are incomplete; physical camera remains deferred. |

### Initial Hostinger KVM 2 deployment

Source: [deployment checklist](../planning/GlycoLens_06_Milestones_and_Schedule.md#initial-hostinger-kvm-2-deployment), [container guidance](../../infra/README.md), [local Linux evidence](lightgbm-app-validation-2026-11-12.md).

| ID | Planned task | Assessment | What exists / what remains |
|---|---|---|---|
| H01 | Select KVM 2 with managed Supabase | Completed | ADR 0016 records the decision. Provider selection is distinct from an operating deployment. |
| H02 | Provision host/project; record DNS, region, subscription and capacity | Partial | Dedicated managed cloud development is implemented. VPS/domain provisioning and hosted configuration are still pending in the available evidence. |
| H03 | Pinned Linux containers, portable simulator, CPU limits, persistent caches/replays, readiness | Partial | Digest-pinned images, isolated Linux simulator, root Compose, read-only model mounts, thread limits and runtime checks exist. Actual-host resource/readiness acceptance is open. |
| H04 | HTTPS, origins, private secrets, managed migrations/Auth/RLS, isolation and recovery | Partial | Development schema, trusted writes, owner checks and guarded migrations have evidence; Caddy/hosting templates exist. Live DNS/TLS, production origins, email delivery and recovery acceptance are pending. |
| H05 | Overlap/busy handling, desktop/mobile full flow, cold/warm/p95, memory, credits and quotas | Partial | Single-flight locking, 429 handling, model-only timings and local journeys exist. Full HTTP p95, target-host peak memory/concurrency, credits/quotas and combined live browser workflow are unproven. |
| H06 | Restart recovery, database backup/restore, local fallback, retained prior release and hosted sign-off | Partial | Local API/container restart and saved-result preservation have scoped evidence. Host reboot, independent managed-DB restore, compatible-release rehearsal and cloud-outage fallback proof are missing/deferred. |

### Corrected nutrition catalog migration

Source: [M3 migration checklist](../planning/GlycoLens_06_Milestones_and_Schedule.md#corrected-nutrition-catalog-migration-from-milestone-2), [November 14 audit](azure-nutrition-catalog-assessment-2026-11-06.md), [migration strategy](azure-to-supabase-catalog-migration-strategy-2026-11-06.md).

| ID | Planned task | Assessment | What exists / what remains |
|---|---|---|---|
| C01 | Receive approved corrected release/manifest; verify mappings, energy, yields, quantities, missingness and provenance | Pending | Read-only assessment/strategy are complete. No admitted release exists; substantive quality/basis/rights gates remain. |
| C02 | Export approved dependency closure from consistent snapshot with IDs/checksums/manifest | Pending | Sample sizing is not a complete export. No approved full private release export is recorded. |
| C03 | Stage compact schema in guarded cloud target; verify counts, FKs, calculations and actual indexed size/budget | Pending | Measured target baseline and estimated transfer sizes exist. No staged restored release/index-size validation is recorded. |
| C04 | Import validated catalog with access controls, bounded staging and rollback package | Pending | No cloud catalog schema/data import or publication was recorded. |
| C05 | Connect food adapter; resolve grams/servings and preserve source snapshots | Pending | Existing food APIs support provider/cache facts. The corrected Azure catalog adapter and recipe serving contract are not delivered. |
| C06 | Pass desktop/mobile catalog search, barcode and recipe-review meal-to-forecast, failures/persistence/rollback | Pending | All 15 P07 acceptance cases are blocked. Provider smoke/fixture tests cannot substitute for this release's acceptance. |

### Required product features

Source: [required M3 features](../planning/GlycoLens_06_Milestones_and_Schedule.md#required-features), [Plan 18](../planning/GlycoLens_18_M2_Closure_and_LightGBM_Integration.md), [Plan 19](../planning/GlycoLens_19_Personal_and_Simulation_Workspaces.md).

| ID | Planned task | Assessment | What exists / what remains |
|---|---|---|---|
| F01 | Final selected model(s) | Partial | Chronos is the explicit default; frozen LightGBM has a verified native adapter and local opt-in. Selection/integration exist, but acceptance is incomplete and meal usefulness is not established. |
| F02 | Uncertainty visualization | Partial | Chart, table, display conversion, interval kind, frozen calibration identity and signed v2 bands are implemented. Manual acceptance and application-transfer coverage are unverified. |
| F03 | Similar meals / Meal Passport | Partial | SQL chronological candidate filtering, numeric nutrient-distance ranking and demo UI exist. It is same-session simulated history; personal longitudinal Meal Passport and dedicated route integration are not complete. |
| F04 | What-if portion comparison | Partial | 10–200% scenarios freeze original context/model, preserve totals and reproduce the 100% baseline. Default Chronos failed the synthetic meal/portion-response capability test. LightGBM has only limited synthetic carbohydrate sensitivity. |
| F05 | Actual-versus-predicted result view | Partial | 24 later samples, exact clock/grid checks, error/coverage metrics and saved outcomes exist. The UI shows numerical follow-up, not an actual-curve overlay. Preset simulator outcomes do not validate arbitrary entered meals. |
| F06 | Simulation integration | Partial | Short and separate 48h protocols, live/replay, owned sessions, virtual clocks, withheld future and both real model paths have recorded evidence. Full lifecycle/recovery/manual acceptance remains partial. |
| F07 | Dexcom Sandbox if feasible | Deferred | Explicitly deferred in the approved direction. No personal glucose connector is enabled; do not count missing personal forecasting as implemented Dexcom support. |
| F08 | Loading and error handling | Partial | Async/loading/error/not-found states, retry, busy/unavailable and no silent model fallback are implemented. Complete provider/session/revocation/browser failure permutations remain unaccepted. |
| F09 | Provenance labels | Partial | Provider nutrient basis, frozen facts, model/version/calibration identity, workspace/source labels and exports exist. Catalog field authority/rights and comprehensive display/manual review remain open. |

### Final analysis

Source: [original model comparison](milestone-2-model-results.md), [refinement](model-refinement-results-2026-10-16.md), [independent evaluation](metabonet-phase6-independent-2026-10-16.md), [application sensitivity](meal-response-sensitivity-2026-11-12.md).

| ID | Planned task | Assessment | What exists / what remains |
|---|---|---|---|
| A01 | Model comparison | Completed | Chronos/TimesFM/persistence C0–C3 comparison, train-only refinement and frozen LightGBM independent confirmation are reported. Different cohorts/protocols must not be merged into a single direct ranking. |
| A02 | Context ablation | Completed | Original C0–C3 context experiment, history-window and later common/events/full-feature comparisons exist. Mixed or negative results are completed experimental evidence. |
| A03 | Latency analysis | Partial | Research runtime and local Linux cold/warm model-only timings exist. Full endpoint/provider latency, p95 concurrency and target-host resource/cost acceptance remain missing. |
| A04 | Uncertainty analysis | Completed | Original undercoverage, separately calibrated marginal/curve bands, subgroup/horizon and shifted-cohort coverage are documented. Failed coverage under shift is a finding, not a missing experiment. |
| A05 | Representative forecasts | Partial | Chart/UI and synthetic cases exist; reports expose aggregate tails and difficult cases. A consolidated checked-in M3 representative forecast set tied to the final demo/results was not found in the reviewed reports/presentation inventory. Ignored raw artifacts were not inspected. |
| A06 | Limitations | Completed | Baseline failure, poor tight precision, shift, small calibration sample, missingness, physiological mismatch, consumed test cohorts and simulation limitations are explicitly recorded. |

### Testing

Source: [test strategy](../testing/test-strategy.md), [actual webapp ledger](../testing/webapp-validation-results.json), [workspace ledger](../testing/workspace-separation-results.json), tests and runners in the source tree.

| ID | Planned task | Assessment | What exists / what remains |
|---|---|---|---|
| T01 | Unit tests for data transforms | Completed | Checked-in preparation, chronology, units, workspace/date/DST and transform tests exist. The fresh offline selection passed; research-suite outcomes outside that selection are recorded historical evidence. |
| T02 | Model adapter tests | Completed | Shared contracts, shape/quantiles, registry, native bundle integrity/parity and context guards have tests. Passing contracts do not prove predictive skill. |
| T03 | Nutrition calculation tests | Completed | Gram scaling, repeated ingredients, unknown facts, reviewed-fact conflicts, lifecycle and aggregate tests exist; current selected tests passed. |
| T04 | Critical Playwright flows | Partial | Multiple desktop/mobile fixture runs and a recorded real password/cloud/local-browser journey exist. Full real-provider Chrome flow, human keyboard/zoom and applicable failure variants remain open; historical live-application spec is unconditionally skipped. |
| T05 | Deterministic demo scenario | Completed | Versioned fixed short/48h protocols, seeds/replay identities and prior two-run hash equivalence have evidence. This audit's explicit real-simulator test remained skipped; cloud-independent availability is a separate recovery criterion. |

## Recorded acceptance ledgers

Counts below were recomputed directly from each file's individual case statuses.

| Ledger | Cases | PASS | PARTIAL | BLOCKED | NOT_RUN | FAIL |
|---|---:|---:|---:|---:|---:|---:|
| [Plan 17 webapp](../testing/webapp-validation-results.json) | 146 | 22 | 87 | 32 | 4 | 1 |
| [Plan 18 closure / native model](../testing/m2-closure-lightgbm-results.json) | 58 | 22 | 29 | 6 | 0 | 1 |
| [Plan 19 workspace separation](../testing/workspace-separation-results.json) | 44 | 28 | 16 | 0 | 0 | 0 |

Do not add these totals: the catalogs overlap and describe different requirements/versions. In particular, GL-P09-011 and M2C-C2-008 refer to the same Chronos sensitivity failure. Main-ledger counts are recorded acceptance, not a complete current implementation inventory; stale explanatory rows are identified below.

| Expanded implementation phase | Current audit judgment | Main-ledger PASS / PARTIAL / BLOCKED / NOT_RUN / FAIL |
|---|---|---|
| P00 Baseline/configuration/CI | Partial: executable checks exist and current local checks pass; protected hosted CI acceptance not verified here | 5 / 2 / 1 / 0 / 0 |
| P01 Cloud schema/trusted boundary | Partial: applied development migrations and scoped isolation evidence; scratch replay/restore deferred | 6 / 5 / 1 / 0 / 0 |
| P02 Responsive shell | Partial: implemented, fixture tested; manual accessibility/zoom/device checks open | 0 / 7 / 3 / 0 / 0 |
| P03 Auth/onboarding | Partial: password/development Auth works; verified email/recovery and anonymous upgrade open | 7 / 4 / 6 / 0 / 0 |
| P04 Capture/scan/recipe/meal lifecycle | Partial: code and live API/provider evidence; representative extraction and full Chrome/failure acceptance incomplete | 0 / 17 / 0 / 2 / 0 |
| P05 Simulation/forecast/history | Partial: real inference, frozen storage/history and retrieval exist; combined variants remain open | 0 / 15 / 0 / 0 / 0 |
| P06 Home/Nutrition | Partial: real aggregation and DST/pagination evidence; optional goal entry/history not implemented/accepted | 0 / 11 / 0 / 1 / 0 |
| P07 Catalog/search/details/favorites | Pending: dependency-gated, all 15 cases blocked | 0 / 0 / 15 / 0 / 0 |
| P08 Settings/privacy/notifications | Partial: export, immediate deletion and notifications exist; verified credential recovery/retention/release checks remain | 2 / 10 / 1 / 0 / 0 |
| P09 Scenarios/actual follow-up | Partial with failed capability: default meal-response FAIL; matching-outcome accuracy NOT_RUN | 2 / 8 / 0 / 1 / 1 |
| P10 Hosting/resilience/release | Partial preparation: local packaging works; hosted/full recovery/UAT gates remain | 0 / 8 / 5 / 0 / 0 |

No P00–P10 phase is fully accepted in the main ledger. Plan 18's bounded L0 native artifact/parity phase is PASS with six cases; that does not close L1–L4 or the release. Plan 19 demonstrates real engineering progress while retaining 16 partial combined cases.

## Critical findings, ordered by closure impact

### 1. The default model failed the capability central to meal/portion claims

The [sensitivity report](meal-response-sensitivity-2026-11-12.md) records 236/236 completed synthetic predictions, 118 per model. All **60/60 eligible Chronos changed-input contrasts** were indistinguishable at the predeclared 0.001 mg/dL tolerance. Its largest endpoint change was approximately 0.0000076294 mg/dL; the illustrative 100g versus 250g palak-paneer contrast changed by zero.

This is not an unexecuted test or a request-plumbing failure. The capability experiment was executed and failed despite successful input delivery, finite outputs and repeatability. Portion UI and inference transport can work while the default model provides no demonstrated meal contrast. The current model notice discloses the result in [response conversion](../../backend/app/services/inference/demo.py).

LightGBM changed in many carbohydrate contrasts, with a largest endpoint difference of 13.9066 mg/dL, but its current-meal predictor is carbohydrates only. Equal-carbohydrate protein/fat/fiber changes do not affect that candidate. Sensitivity is neither matched-outcome accuracy nor evidence of a safe or beneficial portion.

**Closure implication:** describe this as a failed research capability with an operational scenario tool. Any proposed remediation needs a declared evaluation protocol and appropriate fresh confirmation; do not switch defaults, tune against consumed tests or relabel inference completion as success.

### 2. Personal forecasting and matching-meal outcome validation are absent

[Application inference](../../backend/app/services/inference/application.py) explicitly rejects personal meals with 422 because no personal glucose connector is enabled. [Meal detail](../../frontend/src/features/meal/MealDetail.tsx) correctly explains that personal meals contribute to the log and research forecasts belong to the separate virtual workspace. This is an honest boundary, but limits the delivered product claim.

[Scenario actuals](../../backend/app/services/inference/scenarios.py) waits for the owned source clock and requires the exact 24 later five-minute samples. These chronology guards are useful. However, the simulator's preset meals are not replaced by the proposed user meal. Its later glucose is not matched ground truth for that arbitrary meal.

[ScenarioPanel](../../frontend/src/features/forecast/ScenarioPanel.tsx) displays later-observation error/coverage and supports saving outcomes, but does not overlay an observed trajectory on the prediction. GL-P09-012 remains NOT_RUN. This is a partial follow-up feature with numeric diagnostics, not demonstrated personalized prediction accuracy.

### 3. Catalog admission blocks an entire user-facing feature family

The [current catalog assessment](azure-nutrition-catalog-assessment-2026-11-06.md) reports 33,194 ready-labeled recipes, 5,429 ingredients and 11,397 active products. These are candidates, not approved nutrition:

- 19,111 recipe profiles are per-recipe and 14,083 per-serving; assuming one common basis is wrong.
- 1,343 recipe profiles lack a complete nonnegative core set; 299 recipe/profile yield conflicts remain.
- Of the 3,374 dependency ingredients, 475 lack carbohydrate and 1,470 lack fiber.
- 1,706 selected product GTINs fail their check digit.
- Estimated/generated facts, field disagreements, cooked-yield uncertainty and reuse rights still need policy and validation.

The estimated 151.90 MiB CSV / 50.61 MiB gzip is transfer sizing, not measured indexed PostgreSQL storage.

Source inspection confirms [Search](../../frontend/src/app/(app)/search/page.tsx) and [Favorites](../../frontend/src/app/(app)/favorites/page.tsx) render UnavailableFeature. Recipe/product detail routes explicitly say the corrected catalog is pending. Existing USDA/OFF ingredient paths and API food search are separate, partially verified capabilities.

**Closure implication:** prioritize an approved bounded release and serving/authority rules before treating source status labels as delivery. The code currently has honest placeholders; the release feature remains missing.

### 4. Local packaging is delivered; hosted release and outage resilience are unproven

[Root Compose](../../compose.yaml) provides web/API, isolated simulator, model mounts, CPU limits and managed cloud Supabase. [Dockerfile.api](../../infra/Dockerfile.api) pins image digests and simulator commit. These are substantial delivered tasks.

Nevertheless, local Auth/database continue to depend on managed Supabase. A local model cache or simulator replay does not make the authenticated meal-to-forecast workflow independent of cloud Auth/Data API availability. [User-session validation](../../backend/app/db/client.py) calls Auth and the session-active RPC.

The historical ForecastDemo component still exists and uses the unauthenticated synthetic demo endpoint, but source search found no current page importing that component. Its existence alone is not a demonstrated reachable offline defense workflow. No service-worker/offline workflow was found in the inspected frontend source; a manifest by itself does not establish offline operation.

Local Linux model-only warm p95 is recorded as 0.467s Chronos and 0.0035s LightGBM over 20 sequential warm samples each. Sampled process RSS reached about 951 MiB. These are not full HTTP p95, target-host peak memory, multiuser capacity, CPU-credit or backup/restore results.

**Closure implication:** qualify the local-demo claim precisely and rehearse the actual cloud-unavailable defense path. Public release still needs VPS/domain/TLS/SMTP, target-host measurements, rollback, restart and independent database restore evidence.

### 5. Research is substantially complete, with unfavorable usefulness and transfer findings

The original [T1D-UOM comparison](milestone-2-model-results.md) selected Chronos C3 on validation among pretrained choices, but its test macro MAE was 37.920 mg/dL versus 33.957 for persistence on the common-success comparison. It did not establish superiority to the baseline.

The separate [frozen LightGBM confirmation](metabonet-phase6-independent-2026-10-16.md) is a completed research contribution:

| Measure | Primary test | PEDAP |
|---|---:|---:|
| Eligible meals / participants | 3,533 / 102 | 2,177 / 64 |
| Trajectory MAE, mg/dL | 29.91 | 40.92 |
| Relative MAE improvement over its paired persistence baseline | 18.74% | 16.10% |
| Points within ±10 mg/dL | 28.20% | 19.57% |
| Nominal 80% marginal band coverage | 79.05% | 63.94% |
| Two-hour endpoint MAE, mg/dL | 40.90 | 52.91 |

Average error passed the predeclared confirmation gates. Tight precision remains poor, pediatric interval transfer undercovers and the 48-participant calibration sample limits stability. These research scores are from a different cohort/protocol than the Chronos comparison and cannot be used as a direct same-cohort superiority calculation.

Both reserved cohorts are consumed. Existing analysis is complete evidence; new tuning cannot reuse them as untouched confirmation. No new matching-meal application accuracy was established by serving the frozen candidate.

### 6. Acceptance evidence is fragmented and some current-looking explanations are stale

The exact ledger statuses must be reconciled with newer scoped evidence before closure:

- Main ledger GL-P08-004 says deletion is explicitly disabled. [Immediate deletion validation](account-deletion-validation-2026-11-11.md), the implemented endpoint/service and PrivacyControls demonstrate password-confirmed hard deletion. Verified credential recovery remains open; the deletion explanation is stale.
- Main ledger GL-P00-005 says hosted execution is not enabled while changes stay local. HEAD contains the later implementation checkpoint and publication documentation. GitHub protected-environment/actual-run acceptance was not checked by this audit, so do not infer either pass or failure from that old wording.
- Main ledger GL-P10-010 still lists a complete Linux API/simulator as required; later local Linux/Compose evidence delivers that part. Hosted combined acceptance is still missing.
- Architecture section 13 still says no Compose file exists and the simulator path is Windows-specific. Later code and local-runtime sections contradict those statements.
- Plan 06 retains unchecked coarse A–D/container items despite later engineering reports, and prose that the 146 cases begin NOT_RUN. Those describe planning history, not current item-by-item delivery.
- The test strategy link text still says 144 cases; the current catalog/ledger contain 146.
- Plan 17's phase-sequence row still lists P09 as 10 cases, while its current P09 section/ledger contain 12.
- Main-ledger latest_checkpoint contains older counts, distinct from the later implementation_checkpoint counts and current case rows. Consumers must aggregate actual rows rather than trust the first summary object.

Some older entries are explicitly dated historical checkpoints and should be preserved. The problem is the absence of one reconciled current M3 closure view, not a reason to erase history or convert qualified cases to PASS.

Several broad PARTIAL rows repeat generic explanations across different requirements; a release reviewer cannot easily tell which exact subvariant is missing. Earlier cloud runs also did not always capture the exact execution-time dirty-tree digest. A final reviewed manifest cannot retroactively establish every earlier run's revision.

**Closure implication:** produce one requirement → implementation → exact test/run/revision → remaining condition map, retaining the historic observations. This audit does not rewrite those ledgers or grant acceptance.

### 7. Final milestone packaging and manual acceptance still need work

No dedicated M3 report/deck was found in the checked-in report/presentation filename inventory before this audit. The existing M2 v4 deck and updated Markdown claims are not a recorded M3 presentation, rendered-deck review or timed presenter rehearsal.

The November 14 workspace report records an actual browser/cloud journey using genuine Auth, and meaningful automated fixture coverage. Therefore “there has been no real browser evidence” would be wrong. It also explicitly leaves human Chrome keyboard/zoom review, representative resource gates, transition-failure rehearsal and owner sign-off open. Physical camera and independent scratch restore/replay are deliberate deferrals.

**Closure implication:** preserve the useful automated evidence, then finish the specific remaining manual/rehearsal and failure checks for the declared demonstration scope. Do not label every browser gap as an infrastructure failure or every automated viewport test as human acceptance.

## Fresh verification performed by this audit

| Check | Observed result |
|---|---|
| Existing network-denied offline Python CI selection | **210 passed, 1 skipped**, 12.74s |
| Existing frontend Vitest suite | **36 passed**, 11 files |
| Frontend ESLint with zero-warning threshold | Passed |
| Frontend TypeScript check, without emit | Passed |
| API contract vs reviewed OpenAPI snapshot | Matched |
| Public-file exclusion scan | 623 files checked; zero findings; zero missing image exclusions |
| Repository skill validation | Nine skills passed; zero failures |
| Graphify status/query before report creation | ACTIVE, version 0.9.69; local query located M3, deployment, catalog and comparison relationships; claims checked against source |

Python command: .venv/Scripts/python.exe -m pytest -p scripts.quality.offline_pytest backend/tests tests/quality tests/contract tests/database tests/research/models/test_forecast_adapters.py tests/research/test_pymgipsim.py -q.

Frontend command: frontend/node_modules/.bin/vitest.cmd run, executed from frontend. API/public/skill checks used the existing scripts.quality modules.

The skipped test explicitly requires GLYCOLENS_RUN_PYMGIPSIM=1 and the isolated installer. It is not a simulator pass in this audit. One existing Starlette/httpx deprecation warning was reported; it did not fail the suite. Initial sandbox runtime/dependency access restrictions were resolved through approved tool execution, without changing toolchains or installing packages.

Current test success supports the inspected contracts and unit behavior. It does not close historical combined browser/cloud/manual cases, prove nutrition accuracy, repeat independent research results or establish a hosted release. Older overlapping test totals were not added to these fresh counts.

## Milestone success criteria

| Original criterion | Finding |
|---|---|
| End-to-end app works | Partial: local/cloud-development virtual workflow is demonstrated; personal forecasting, corrected catalog and full agreed Auth/recovery/browser paths are incomplete. |
| Final experiment set complete or nearly complete | Approved original comparison/refinement/independent evaluation is complete. New application sensitivity completed with a failure; matching-outcome application accuracy remains unexecuted. |
| Results reproducible | Partial: source/locks/configuration/digests/runners and deterministic scenario evidence exist. Full independent research reproduction, some historical execution-revision certainty and scratch replay/restore remain open. |
| No core feature depends on future development | Not met for the expanded feature contract: catalog/search/details/favorites, personal connector and public-release dependencies remain. |
| Demo reliable offline/local if cloud fails | Partial: local model/simulator/runtime exist, but current authenticated app still requires managed cloud services; an actually reachable cloud-independent defense workflow has not been demonstrated. |

## Recommended closure order

1. **Freeze and state the demonstration scope.** Present current local/cloud-development meal logging, truthful nutrition review, immutable simulated forecasts and explicit limitations. Declare catalog/Dexcom/device/restore deferrals accurately. Do not silently remove agreed requirements or change course dates.
2. **Reconcile acceptance and current claims.** Update the stale explanations, attach later Plan 18/19 evidence to exact requirements and keep pending variants visible. Preserve the Chronos capability FAIL and matching-outcome NOT_RUN.
3. **Resolve the meal-forecast claim.** Keep the negative Chronos result visible. If further work is approved, predeclare a suitable development/evaluation protocol and fresh matching outcomes; do not tune on consumed test groups.
4. **Rehearse the actual defense workflow.** Record Chrome/provider/cloud/model paths, refresh/logout/owner isolation, keyboard/zoom and a tested cloud-outage fallback; prepare a current M3 deck/report and timed rehearsal.
5. **Admit a bounded corrected catalog release.** Set nutrient basis, field authority, provenance/rights and yield rules; export, restore/index-measure, import under guards, then deliver and accept search/details/favorites.
6. **Finish release operations separately.** Provision authorized hosting/email/DNS/TLS, measure full-stack resources and latency, rehearse compatible rollback and independent restore, then record applicable UAT and sign-off.

This order prioritizes closure evidence and truthful claims. It is not an instruction to change the approved model, activate questionable food data or launch a public service.

## Review scope and preserved state

Reviewed the repository instructions, current planning 00/01 and relevant product/architecture/scientific/milestone/risk/specification sections; Plans 10, 16–19; current test catalogs/three ledgers; M2, research, catalog, workspace, deletion, model-enablement and local-runtime reports; frontend routes/features; backend Auth/meal/nutrition/retrieval/inference/scenario/source code; relevant migrations; test/CI definitions; manifests/configuration and container/Compose guidance.

The local Graphify status/query was navigation support, not scientific or integration proof. Its optional SQL extraction limits were handled by inspecting relevant migration source directly. No external semantic backend was used.

Existing user modifications were preserved. This audit adds only this report; it changes no product behavior, scientific choice, schema, milestone date, acceptance result or external service. Accordingly, planning source-of-truth files and the root README were reviewed where relevant but not rewritten to imply implementation or closure.
