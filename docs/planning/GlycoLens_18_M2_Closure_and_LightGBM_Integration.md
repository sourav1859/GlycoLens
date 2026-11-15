# Milestone 2 closure and opt-in LightGBM implementation plan

## November 14: personal and simulation workspaces implemented

Plan 19 now isolates both research model paths in `/demo`. Short/long protocols, deterministic virtual epoch, exact history windows and frozen calibration/results remain unchanged. Personal meals cannot borrow a virtual source for forecasts. Existing local native enablement and unresolved accuracy/manual gates remain as recorded. [Actual validation](../reports/workspace-separation-validation-2026-11-14.md) and [44-case ledger](../testing/workspace-separation-results.json): **28 PASS, 16 PARTIAL**. Changes remain local; human Chrome and other qualified gates are not claimed complete.

## November 14: local LightGBM selection enabled for user review

At the user's request, the existing local development runtime now exposes **LightGBM · research option** alongside default Chronos. The ignored local enablement flag is true; the running API's native bundle/digest/read-only mount were verified and real synthetic inference returned 24 ordered points. The shipped environment template remains disabled by default. This is a user-authorized local research exposure for manual testing, not completed L0–L4 acceptance, production enablement or a model default change. All existing history/artifact/owner checks remain enforced.

An existing meal attached to the short one-day source remains ineligible for native inference. Explicitly prepare the 48-hour research source and save a new reviewed meal at that source's clock; existing meal/source snapshots are unchanged. Current carbohydrates are the native meal predictor; matching-outcome accuracy and transferred interval coverage remain unvalidated. [Enablement and verification](../reports/local-lightgbm-enablement-2026-11-14.md). November 12 off-state descriptions below are historical checkpoints; their outstanding acceptance results remain valid.

## Implementation evidence

[Plan 18 engineering](GlycoLens_18_M2_Closure_and_LightGBM_Integration.md) is delivered locally: grounded live-provider/API journeys, native opt-in connector, separate 48h scenario, versioned cloud intervals, research UI and CPU Compose/recovery. [Actual report](../reports/m2-closure-validation-2026-11-12.md) and [58-case results](../testing/m2-closure-lightgbm-results.json) replace the planning-only status below. **GL-P09-011 executed and failed Chronos meal-response capability**; GL-P09-012 remains NOT_RUN. API successes do not close Chrome-dependent phases 5/8/9 or presenter acceptance. Normal native enablement remains off. No new push authorization or full M2 closure; physical camera and scratch replay stay deferred.

**Date:** November 12, 2026. **Status:** engineering implemented; real API/cloud/CPU evidence recorded, combined acceptance partial, Chronos sensitivity capability FAIL. Ordinary native enablement off. Baseline inspected: `75191e2f654d9e1cbe4a3676d2948131013ec94b`. This plan supplements [M2 ledger 10](GlycoLens_10_Milestone_2_Implementation.md) and [webapp plan 17](GlycoLens_17_Webapp_Implementation_Plan.md); it does not declare either complete.

## 1. Confirmed direction and boundaries

- Retain one repository, FastAPI modular monolith, common forecast adapters and managed **cloud Supabase**. Do not introduce a local Supabase stack, model microservice or new external model API.
- **Chronos remains the application default.** Add LightGBM as an explicitly selected research option only after the integration gates below. User approval of this direction is not evidence of runtime readiness or permission to replace the default.
- Add a **separate versioned longer synthetic scenario** with at least 24 hours of pre-origin history; retain the current fixed one-day demo and replay contract.
- Browser acceptance targets Chrome, with mobile/tablet/desktop viewport coverage. The user explicitly deferred physical-camera testing to future scope. Manual barcode lookup and browser fallback/error contracts remain in scope; emulated camera/viewport tests cannot claim physical-device acceptance.
- Existing corrected-catalog admission, SMTP/domain/hosting, separate scratch restore/replay and prospective accuracy requirements remain their own gates. They do not become new prerequisites for original M2 provider journeys.
- The user subsequently authorized implementation. The work cycle now includes guarded forward cloud migration, tagged synthetic integration fixtures, bounded provider calls and one successful paid recheck plus an unresolved attempted call reserve. No training, consumed-cohort access or model default switch. Changes remain local for review.

## 2. Planning baseline findings (superseded by implementation outcome above)

### Original Milestone 2

The core demo, real simulator execution, grounded nutrition adapters, meal save, Chronos inference, persisted forecasts, numeric historical retrieval and research comparisons exist. The M2 ledger's old statement that USDA/LLM credentials are missing is stale. Cloud keys, USDA, selected OpenAI recipe parser, simulator environment and Chronos cache are present; earlier component smoke tests are evidence of those runs, not complete live browser journeys.

Remaining work that can be implemented/tested now:

1. Establish independent representative nutrition/extraction oracles, reconcile configuration and evidence to the current revision, and verify provider compatibility and bounded failures.
2. Exercise actual Chrome -> provider -> reviewed meal -> cloud save -> real simulator/Chronos -> persisted read journeys for food search, manual barcode and recipe text. Keep source, units, ownership, retries and timestamps observable.
3. Execute the already planned meal-response **sensitivity** assessment with frozen inputs, and report invariant or unstable responses honestly. This is distinct from proving accuracy for arbitrary meals.
4. Reconcile requirements/results, presentation claims and remaining acceptance decisions. Native PowerPoint review and presenter rehearsal need human review; do not fabricate sign-off.

Physical-camera testing is now an accepted future item, not a blocker for this declared Chrome/manual-barcode closure scope. The original full feature/device contract is retained for future acceptance. The remaining 146-case webapp ledger is broader than M2: its pass count is not an M2 completion percentage.

### Current application versus LightGBM research

| Area | Current application | Existing LightGBM candidate / integration consequence |
|---|---|---|
| Model selection | `application.py` and `scenarios.py` construct Chronos; process singleton | Introduce one server-owned registry used by both paths; explicit allowlisted model selection and capability checks |
| Glucose history | 24 five-minute readings, about two hours | Exactly 288 regular five-minute readings, about 24 hours; origin alignment must match training |
| Missingness | No training-style observation masks | Requires CGM/event record-presence masks; unknown, observed zero and absent event are different |
| Insulin | Bolus U and source-kind basal channels, potentially U/hour | Six-hour historical bolus/basal amounts in `IU_per_source_interval`, aligned to five-minute bins; unit/availability conversion is mandatory |
| Previous meals | No equivalent canonical historical carbohydrate channel in the inference builder | Six-hour `previous_meal_carbohydrates` and record-presence channel, excluding the current meal |
| Proposed meal | Chronos C3 receives carbs/protein/fat/fiber | Trained direct model uses **current carbohydrates only**. Protein/fat/fiber-only contrasts should leave its features unchanged |
| Feature vector | Chronos covariates | `metabonet_tabular_v1`: 127 origin features plus horizon fraction in the estimator input, not a generic C3 full-nutrition model |
| Loading | Cached Chronos loader | `MetaboNetTabularAdapter.load()` is not a disk loader. Trusted frozen artifact loading/export and exact version checks must be added |
| Uncertainty | Quantile response and chart | Direct adapter emits equal placeholder bounds. Saved participant calibration wrapper is required for meaningful intervals; symmetric marginal bands must be labeled accurately |
| Transport/storage | v1 forecast bounds 20–600 in API; positive bounds in DB | Calibration may produce bounds outside these limits. Version the contract/storage deliberately; never clip intervals or call placeholders calibrated |
| Packaging | API image installs Chronos group | Add pinned CPU LightGBM dependencies and a narrow read-only verified bundle mount; avoid mounting research datasets |

Relevant sources: [application inference](../../backend/app/services/inference/application.py), [scenario inference](../../backend/app/services/inference/scenarios.py), [tabular adapter](../../research/models/adapters/metabonet_tabular.py), [training-window translation](../../research/datasets/metabonet.py), [calibration wrapper](../../research/evaluation/metabonet_uncertainty.py), [API schema](../../backend/app/models/forecast.py), [frontend schema](../../frontend/src/types/forecast.ts), [simulator contract](../../research/simulation/adapter.py), [API image](../../infra/Dockerfile.api). See [ADR 0022](../decisions/0022-opt-in-lightgbm-research-integration.md).

**Artifact readiness inspected:** the saved LightGBM bundle and calibration bands exist. Their selected-file hashes and completion-manifest hashes match; the calibration record checksum and `lightgbm_direct` identity match. This was metadata/hash inspection only: no deserialization, retraining, predictions or research-row projection. It does not prove serving compatibility, every research artifact's integrity or end-to-end acceptance.

### What the accuracy results mean

The original UOM matched test has Chronos C3 macro MAE 37.920 mg/dL versus persistence 33.957; the pretrained choice did not beat persistence. The later frozen MetaboNet LightGBM scored 29.91 on the primary cohort and 40.92 on PEDAP, passing that study's predeclared point-improvement gates. Tight accuracy remains poor: within +/-10 mg/dL was 28.20% and 19.57%. Nominal 80% marginal interval coverage was 79.05% and 63.94% respectively.

These cohorts, histories and protocols differ. **29.91 versus 37.920 is not a valid head-to-head comparison.** Research success explains why an opt-in candidate is worth integrating, not why the app should automatically switch. Primary/PEDAP test cohorts are consumed: no test-based model reselection, retuning, recalibration or new independent-accuracy claims. Preserve [original M2 results](../reports/milestone-2-model-results.md) and [Phase 6 results](../reports/metabonet-phase6-independent-2026-10-16.md).

## 3. Prerequisites and what is needed from the user

| Item | Current state | Effect |
|---|---|---|
| Approved cloud Supabase development URL/public/server keys and migration access | Existing private configuration; public frontend target matches backend | Reuse with target guards and synthetic users; do not ask for keys again |
| USDA key; OpenAI recipe key/model | Present; selected parser remains `gpt-6-luna` | Recipe parser is independent of glucose model selection |
| Paid-test allowance | USD 5 **total**, earlier estimated USD 0.00763580 already spent | Reconcile available budget, use existing reservations and per-call limits; stop before exceeding cap, including retries |
| Open Food Facts application contact | **User approved; configured in ignored root `.env` November 12**; value-free format check passes | Restart/recreate API to load it before live uncached barcode testing; never publish the address |
| Chronos cache and isolated simulator | Present | Readiness still needs the exact runtime smoke used for acceptance |
| LightGBM frozen bundle and calibration | Present; selected checksums match | L0 must validate metadata, compatible dependencies and serving parity before enablement |
| Longer synthetic protocol | User accepts separate versioned scenario | Implement and validate in L1; current demo stays supported |
| Chrome review | User selected Chrome | Automate desktop/mobile/tablet views; human keyboard/zoom/reading review remains explicit |
| Physical camera | **Deferred by user** | Retain future device cases; do not mark them passed |
| Native deck review/rehearsal and final M2 acceptance | Not recorded | User/presenter input needed at C3; all engineering work can proceed first |
| Corrected catalog, VPS/domain/SMTP, scratch replay target | Pending / scratch explicitly deferred | Separate M3/public-release work; do not use fixtures to claim those pass |

No new LightGBM API key, LLM choice, paid GPU service, model-training budget or repository is required for this design. Existing bundle rights/provenance and packaged dependency compatibility still need checking. Configure private values through ignored files; do not include them in tracked test evidence.

### Open Food Facts explained

Open Food Facts maps a packaged food's barcode/GTIN to community product facts such as name and per-100g calories, carbohydrates, protein, fat and fiber. USDA supports food/ingredient search; the LLM extracts editable ingredient text. None of these alone proves a user's actual portion or a glucose response.

There is no Supabase-style project or secret API key to provision for public product reads. Our `OPEN_FOOD_FACTS_USER_AGENT` identifies **GlycoLens/version and an approved contact email** to the service. Public reads require that identity, while contribution/write operations have separate authentication. The service also asks API users to submit its usage form; that is an application-registration courtesy, not the missing backend key. GlycoLens does not upload user meals/photos or write products in this scope. See [official API requirements](https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/#authentication).

The adapter currently uses v2. Official docs now recommend v3 and retain v2 for compatibility. C1 must review a bounded v3 migration or explicitly retain/test compatible v2 with a recorded deprecation limitation. Respect current product-read limits (official docs currently state 15 requests/minute/IP), caching and bounded retries. Community facts can be incomplete or incorrect: preserve unknown nutrients, review the package label and retain source attribution. See [official overview and limits](https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/). A successful manual barcode test says nothing about real camera capture.

## 4. Execution order and phase gates

Estimates are focused engineering days, conditional on current code/environment; they are not deadline commitments. Start C0, then C1/C2, then C3 closure. LightGBM is an additional application-integration track: start L0 after C0, then L1/L2, then L3/L4. Do not hold original M2 provider closure open solely for the new candidate. Do not change course dates or reset earlier research phase numbers.

| Phase | Work | Dependencies | Estimate | Tests / exit |
|---|---|---|---|---|
| C0 | Current-revision baseline, private config/readiness, declared scope and oracle freeze | Existing repo/config | 0.5–1 day | C0 catalog cases; reproducible manifest, limits, expected facts and scope recorded |
| C1 | Grounded provider/recipe correctness and failure behavior | C0; configured contact | 1–2 days | C1 cases; independent nutrition/extraction oracles, missingness and safe failure evidence |
| C2 | Real Chrome/cloud/model journeys and meal-response sensitivity | C1; cached model and real simulator | 1–2 days | C2 cases; three actual input journeys plus authorization/retry/source evidence and sensitivity report |
| C3 | M2 evidence, presentation claims and acceptance reconciliation | C2 | 0.5–1 day plus presenter review | C3 cases; declared-scope checklist reconciled, no unsupported completion or accuracy claim |
| L0 | Trusted frozen LightGBM bundle loader/export and calibrated adapter parity | C0; existing artifacts | 1–2 days | L0 cases; immutable identity, checksum gate, dependency compatibility and synthetic parity |
| L1 | Separate longer simulator, 24h history and training-compatible event features | L0 feature contract | 2–3 days | L1 cases; warm-up, bins/units/masks/chronology verified without changing old replay |
| L2 | Common registry, capability/readiness and versioned API/storage contracts | L0/L1 | 2–3 days | L2 cases; both forecast paths, safe intervals, owner isolation and old-result compatibility |
| L3 | Opt-in UI, result identity, comparisons and honest input/interval explanation | L2 | 1–2 days | L3 cases; explicit choice, short-history recovery, responsive chart/table and coherent snapshots |
| L4 | CPU Compose acceptance, measured performance, sensitivity and rollback | L0–L3 | 1–2 days | L4 cases; complete synthetic journey, resource report, bounded failures and default preserved |

### C0 — Freeze the acceptance basis

Record commit/worktree hashes, lockfiles, cloud migration identities, model revisions, runtime versions and configured capabilities without values. Reuse previous passing checks unless affected; run the relevant current baseline once when implementation starts. Provision only tagged disposable users/rows under the approved cloud target, with cleanup IDs captured. Define independent expected totals and extraction lists **before** new inference/provider execution. Separate live provider facts from stable offline response fixtures, recording retrieval time and product/food ID.

Exit: reproducible baseline plus test manifest; configuration presence is not a live-access pass. New test ledger entries remain NOT_RUN until executed.

### C1 — Verify grounded nutrition and recipe extraction

Cover representative plain foods, prepared meals (including palak paneer), repeated ingredients, gram/yield/serving scaling, unknown nutrients, units and ambiguous household portions. Use independent hand-calculated nutrient oracles; never use the same implementation to calculate expected results. LLM output supplies ingredient candidates only; require reviewed source matches and measured grams before save. Measure extraction accuracy against frozen expected lists and include ambiguity/refusal/failure cases, rather than treating parseable JSON as accuracy.

Review OFF version compatibility, User-Agent, caching, supported valid/invalid GTIN, not-found, 429, timeout and partial facts. Bound read volume and avoid provider flooding. Use existing recipe spend reservation; record actual tokens/cost estimates and retries. No real health information goes to LLM/provider tests.

Exit: required deterministic cases pass and a bounded real provider sample supports each adopted path. Missing/unstable provider evidence stays PARTIAL/BLOCKED, never relabeled as a mocked live pass.

### C2 — Validate the actual Chrome experience

Run independent actual paths for USDA search, manually entered barcode and recipe text: select/review/grams -> save exactly once -> real source context -> Chronos forecast -> persisted owned detail/reload. Test double-click, retry after an interrupted response, expired/revoked session, owner A/B access and provider unavailability. Keep forecast timestamps tied to the virtual source clock, distinct from wall-clock save time.

Run the existing [meal-response protocol](../testing/meal-response-validation-protocol.md), GL-P09-011, on frozen contexts for at least low/medium/high carbohydrate meals, 50/100/150% portions and equal-carbohydrate composition contrasts, including repeated identical requests. Capture actual model inputs and point/interval deltas; do not require a monotonic glucose response as a universal truth. Document that the fixed simulator's later preset trajectory is not matching ground truth for a newly proposed meal. GL-P09-012 accuracy remains unexecuted until an approved matching-outcome protocol/source exists.

Chrome coverage: 320/390 mobile, 768/1024 tablet and 1440/1920 desktop widths; chart data table, keyboard focus, errors, loading and empty states. Human zoom/keyboard checks complement automation. Physical camera remains deferred.

### C3 — Reconcile closure and presentation

Update original M2 phases 5/8/9 only against their combined evidence. Build requirement -> test -> revision -> actual result -> limitation mapping. Review the existing v4 presentation/notes for the current Chronos/default versus LightGBM/research distinction, provider status and camera deferral. Preserve dated research results and historical local-Supabase evidence. Presenter reviews native PowerPoint and rehearses the current 7–8 minute script; do not overwrite this with an invented timing pass.

Exit: engineering closure for the declared M2 subset may be recommended with explicit deferrals. Full M2 acceptance requires review of the complete delivery checklist and presenter/owner sign-off. No release-wide acceptance follows from this narrower exercise.

### L0 — Package the frozen candidate without retraining

Use the existing winning configuration: LightGBM, 31 leaves, 24h history, events profile; 127 origin features plus one horizon feature. Verify trusted completion/bundle/calibration digests, feature version, training dependency versions, horizon/units and calibration identity. Never deserialize a user-supplied path or an unverified pickle/joblib file. Native Booster export is preferred for narrow serving if exact point parity is demonstrated; retain trusted adapter logic and calibration manifest. [LightGBM supports native model save/load](https://lightgbm.readthedocs.io/en/v4.6.0/pythonapi/lightgbm.Booster.html); [joblib/pickle loading requires trusted artifacts and compatible environments](https://scikit-learn.org/stable/model_persistence.html).

Use handcrafted synthetic compatible requests, not consumed reserved-cohort rows, for feature and prediction parity. Freeze tolerances before execution: origin features equal including NaN masks; median and band endpoints agree within 1e-6 mg/dL before storage, or document a justified tighter serialization-specific alternative before running. Load the saved `lightgbm_direct` symmetric bands; q10=q50=q90 placeholders cannot enable the UI. Do not refit weights/calibration.

### L1 — Create an independent longer synthetic protocol

Prefer a versioned **48-hour** scenario with a forecast origin after 24h and at least two hours of withheld future observations. Validate simulator support first; if upstream cannot produce that contract, stop this phase and report the dependency, rather than stretching/padding the current demo. Keep the original name, fixed seed, 288-sample contract, replay checksums and tests unchanged.

Build a model-specific context translator matching training-window timing: 288 regular CGM readings ending at origin, aligned binary record-presence masks, six-hour past event bins and current known carbohydrate timing. Confirm source observation coverage; no record is not automatically zero. Integrate basal U/hour over each actual five-minute overlap: **1.2 U/hour for 5 minutes = 0.1 U**; a 2 U bolus stays an amount, not a rate. Handle duplicate events, rate changes, interval boundaries and unknown units explicitly. Numeric unit conversion alone does not prove simulator insulin semantics match the training cohort.

Exclude current-meal carbohydrates from previous-meal history; exclude post-origin insulin/meals/CGM and unavailable late records. Store simulator generation/protocol identity separately from source time and wall time. Future data stays private until controlled clock advance; synthetic mismatch/OOD is reported, not repaired by borrowing future observations.

### L2 — Integrate through the existing backend connector

Define an allowlisted registry whose entries declare model/bundle/feature/calibration identities, history requirements, context recipe, supported inputs and interval kind. Both ordinary forecast and portion-scenario services resolve it. Keep Chronos default and its two-hour contract; select a different builder only for an explicit eligible LightGBM request. No arbitrary module, path or download parameter from clients. Cache by immutable full identity, preserve bounded locks and return an explicit readiness/insufficient-history error; never silently fall back to another model.

Design a backward-compatible, versioned response/persistence contract before schema work. A v2 should distinguish model quantiles, calibrated symmetric marginal bands and unavailable intervals, retain finite ordered values and validate glucose histories separately from uncertainty endpoints. Preserve signed lower band values where mathematically produced; do not clip to 20/zero or cast placeholders into intervals. Review SQL constraints/RPC checks, frontend validators, historical reads, exports and numeric retrieval together. Existing v1 Chronos results remain readable and unchanged. Any cloud schema change uses a reviewed forward migration on the exact development target; scratch replay remains a recorded deferred gate.

Persist exact input snapshot, requested/resolved model, bundle digest, feature/calibration versions and scenario protocol. Bind these to idempotency and owner checks. Portion comparisons use the baseline's frozen complete model/input identity, not whatever is now the default. Changing models creates a separate result; no mixed-model portion comparison is implied.

### L3 — Add the research option honestly

Provide a model selector with Chronos selected by default, a clearly marked LightGBM research option and an actionable 24h-history requirement. Short current demo remains usable with Chronos; users can explicitly start the longer scenario for LightGBM. Keep selection/result identity stable across reloads without leaking it across owners/sources. Record selection in the persisted forecast, not only frontend state.

Display LightGBM's actual inputs: glucose, recorded insulin/history masks, previous/current carbohydrates; protein/fat/fiber are nutrition facts but not predictors in this frozen model. Label its bands as calibrated marginal intervals, with synthetic-transfer and coverage limitations, rather than claiming native learned q10/q90 or personal confidence. Keep old Chronos labels accurate. Include accessible chart table, model provenance, selected meal/portion and virtual timestamps on responsive layouts. Preserve owner-scoped export/history and same-model portion comparisons.

### L4 — Validate and conditionally enable

Install pinned compatible CPU LightGBM dependencies in the API image. Mount only a verified narrow serving bundle/calibration manifest read-only; keep research datasets, joblib scratch outputs and secrets outside the browser/image/repo. Run complete Chrome -> long simulator -> save -> LightGBM -> cloud read/reload -> same-model portion comparison in root Compose. Preserve original Chronos/demo/replay/logout regressions.

Measure cold load, warm inference and full end-to-end latency plus peak process/container memory on the actual local machine; do not infer VPS capacity from a single local run. Predeclare benchmark sample counts (at least 20 warm requests per model, sequential, bounded) and report median/p95/failures, CPU threads, image and hardware. Retain existing timeout/concurrency limits; set numerical resource gates from measured baseline/target capacity before enablement, with insufficient evidence explicitly pending. No new performance guarantee is invented by this plan.

Run sensitivity/repeatability per model. For LightGBM, equal carbs with fat/protein-only changes should yield identical features/predictions; describe this limitation. Changed carbohydrates must reach the correct features, but actual output may be flat or nonmonotonic. Report this without claiming reliable meal response or clinical accuracy. Future accuracy needs a new approved matching-outcome protocol; do not rerun consumed cohorts to manufacture independence.

Enable opt-in only when mandatory L0–L4 correctness/security/integration cases pass and limitations are visible. Roll back by disabling the option; Chronos/default and historical LightGBM reads remain available. Do not undo durable results or mutate frozen model artifacts.

## 5. Test execution, evidence and stop conditions

The [detailed traceability catalog](../testing/m2-closure-lightgbm-test-cases.md) maps each phase to fixtures/actions, independent expected results, runner location and evidence. The [results ledger](../testing/m2-closure-lightgbm-results.json) now contains actual scoped outcomes; it initially began with every case NOT_RUN. Existing [146-case results](../testing/webapp-validation-results.json) remain separate; mapped case IDs are not duplicate passes.

For every run record exact commit plus dirty-tree hashes, environment/image, cloud migration versions and target alias, model/bundle/feature/calibration/scenario identities, run-scoped owner IDs, expected/observed numerical outputs, outcome, redacted evidence and defect. Exclude personal email, secrets, health rows, weights and private source files from tracked evidence. Use sanitized aggregates only. A checksum readiness check is not a prediction or live integration pass.

Validation ladder: independent offline feature/provider/unit oracles -> API/DB contract and owner integration -> real provider/model tests under explicit opt-ins -> Chrome journeys -> manual scope/presentation review -> declared-scope acceptance. Execute relevant existing tests after changes; do not repeat whole training, all provider calls or all historical suites merely to inflate counts. Planned runners/test paths in the catalog must be implemented in their owning phase before execution.

Stop/defer the affected gate if provider limits/budget cannot be honored; frozen artifact/unit/mask identity fails; intervals would require silent clipping; matching ground truth is absent; cloud target/ownership is uncertain; or upstream long-scenario semantics cannot be verified. Continue independent work and report the exact dependency. Do not request new keys or change production services to bypass these gates.

## 6. Implementation outcome and next action

Engineering is implemented. See [actual C/L phase disposition](../reports/m2-closure-validation-2026-11-12.md), [native integration](../reports/lightgbm-app-validation-2026-11-12.md), [sensitivity result](../reports/meal-response-sensitivity-2026-11-12.md) and the [case ledger](../testing/m2-closure-lightgbm-results.json). Chronos remains default but failed synthetic meal-response capability. No new matching-outcome accuracy follows. Ordinary native enablement is off; the isolated Compose review stack alone enables it. Cloud fixtures were cleaned up; no repository push or hosted release occurred.

Next user action: review Chrome at `http://127.0.0.1:3102/demo`, including manual barcode, keyboard/zoom and model/interval clarity; review the native v4 presentation and record the actual rehearsal/acceptance decision. Computer Use stopped because the current Windows browser URL could not be verified; no later UI automation was attempted. Physical camera and scratch replay remain deferred. Catalog, real email, hosting and untouched matching-outcome accuracy remain independent gates. Do not promote the option or claim M2 closed from API/unit successes.
