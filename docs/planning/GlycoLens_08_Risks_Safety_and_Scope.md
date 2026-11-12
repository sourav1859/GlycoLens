# GlycoLens Risks, Safety Boundaries, and Scope Controls

## November 12: meal-response and local runtime boundaries

A forecast changing after a portion change does not establish an accurate or causal
meal response. Use [the separate sensitivity/outcome gates](../testing/meal-response-validation-protocol.md);
the fixed replay is not ground truth for arbitrary user meals. Preserve research
labels, uncertainty and the consumed-cohort boundary. An invariant/unstable model
response must be reported as a limitation, not hidden by successful input wiring.
Local Compose publishes loopback ports only, keeps private credentials in API
runtime configuration and retains source artifacts in the existing shared host directory.
All API deletion workers must see the same complete source store. Liveness
cannot establish model, cloud, provider or restore readiness. Anonymous sign-out
warns about identity loss; account-switch/logout must discard private UI drafts.

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

## Current cloud development and test boundary

[ADR 0018](../decisions/0018-cloud-supabase-and-staged-webapp-delivery.md) and
[plan 17](GlycoLens_17_Webapp_Implementation_Plan.md) set a dedicated cloud Supabase
development project for new app/Auth/schema/integration work. Preserve historical
local evidence without using local reset/key-writing scripts as cloud setup.
Require exact target guards, version-verified migration preview, run-scoped synthetic
owners and cleanup, trusted derived-write checks and separate authorized scratch
restore/replay targets. Never reset production or infer API/RLS safety from admin
SQL access alone. Modern API keys must use compatible headers; private keys remain
server-side. Live email/LLM/provider/load checks need designated test identities and
bounded limits. No real-patient research data is authorized by this cloud choice.
All 144 planned cases start NOT_RUN and require actual evidence before PASS.

## November 10 reference-design and responsive UI risks

The [Figma audit](../reports/figma-reference-review-2026-11-10.md) observed condition-safe,
family/allergen-safe and deficiency-style labels in the source designs. They are
excluded from the [GlycoLens UI architecture](../architecture/responsive-webapp-ui.md).
Use source facts, missingness and model uncertainty; no medical meal grade,
clinical alarm, dosing action or default calorie prescription is introduced.

Minimal onboarding collects account/app preferences and data-source/notice
acknowledgements, with optional food preferences/goals. It does not require body
metrics, diagnosis, medication or family/child records, nor authorize real-patient
research. Optional avoidance preferences are not an allergy-safety guarantee.

Prevent UI-induced data errors: only confirmed eaten meal revisions enter daily
totals; planned/cancelled meals, copies, favorites and scenarios do not. Preserve
unknown nutrients and immutable forecast/context/source snapshots. Respect local
timezone/DST and the explicit simulated clock; source/account switches clear
private caches and cannot mix timelines or expose previous-user content.

Responsive failure can hide quantities, source labels or uncertainty. Require
chart text/tables, keyboard/focus recovery, visible units, safe-area/keyboard
clearance and 320px reflow. A screenshot or limited viewport test is not proof
of accessibility or complete responsive acceptance. New schema/API features need
grants/RLS, server-owned derived writes, idempotency and cross-user tests before use.
Cloud owner/trusted-write, source partition, frozen forecast and eaten-total controls now have scoped runtime evidence. Remaining manual/accessibility/physical-device and complete-case checks are listed in the current ledger.

November 6 catalog boundary: recipe data remains deferred during upstream correction.
The [migration strategy](../reports/azure-to-supabase-catalog-migration-strategy-2026-11-06.md)
requires corrected source mappings, energy/serving semantics, explicit missingness and
provenance before activation. Export/import planning preserves read-only Azure access,
excludes customer/health records, keeps credentials private and requires target capacity
and access checks. These catalog findings do not establish a new nutrition provider,
cloud deployment or clinical claim.

## 1. Core safety boundary

GlycoLens is a research prototype.

It will not:
- calculate a real-user insulin dose
- modify physician settings
- send commands to an insulin pump
- classify a meal as medically safe/unsafe
- diagnose T1D
- claim clinical-grade accuracy
- replace a clinician or regulated diabetes-management system

## 2. Model risk

### Risk
A pretrained general time-series model may not transfer well to T1D postprandial dynamics.

### Mitigation
- persistence baseline
- compare multiple pretrained models
- use real held-out T1D data
- show uncertainty
- keep historical evidence visible
- small calibration fallback rather than large training

## 3. TimesFM-3 maturity risk

### Risk
TimesFM-3 is extremely new as of September 2026.

### Mitigation
- implement Chronos-2 first
- keep TimesFM-2.5 as stable fallback
- do not architect the system around one model

## 4. GlucoFM checkpoint risk

### Risk
GlucoFM is highly relevant, but official weights are not currently public.

### Mitigation
- literature/reference only
- revisit at Milestone 2
- do not use unofficial weights as the main result unless provenance is fully documented

## 5. Dataset size risk

### Risk
T1D-UOM has only 17 participants.

### Mitigation
- no large model training
- inference-first
- subject-aware analysis
- external validation with AZT1D/HUPA-UCM
- make claims about the evaluated dataset, not all people with T1D

## 6. Meal-label quality risk

### Risk
Free-living food logs can be incomplete or inaccurate.

### Mitigation
- data-quality filtering
- sensitivity analysis
- describe source limitations
- do not treat self-reported nutrition as laboratory truth

## 7. Data leakage

### Risk
Future CGM or later events accidentally enter context.

### Mitigation
- strict timestamp boundary at meal time
- event-window tests
- chronological/subject-aware split
- retrieval only from data available prior to the tested event

Implemented Milestone 1 controls:

- CGM history timestamps must be at or before the meal
- target timestamps must be strictly after the meal
- insulin context excludes post-meal events
- another meal inside the two-hour target rejects the window
- deterministic synthetic tests cover each boundary
- model adapters accept `ForecastRequest`, which has no held-out target or participant-ID field
- future truth is stored separately in `ForecastTarget` and paired only for evaluation
- past covariates extending beyond context end fail validation
- non-finite values, irregular grids, and crossing output quantiles fail closed
- Chronos-2 receives only the CGM-only `ForecastRequest`; held-out target data and participant IDs
  are structurally unavailable to the adapter
- Chronos-2 requests containing covariates fail explicitly in Phase 3 instead of silently dropping
  insulin or nutrition
- the package and checkpoint revision are pinned, and downloaded weights/aggregate measurements
  remain in ignored artifact directories
- real-checkpoint execution requires explicit download opt-in; ordinary tests remain offline
- the public Phase 4 demo response is deterministic synthetic data and is labeled
  `synthetic_demo`; it contains relative minutes rather than absolute timestamps and contains no
  participant or user identifiers
- FastAPI CORS is an explicit local-origin allowlist and rejects wildcard configuration
- transport and browser validators reject malformed shapes, non-finite values, unordered time
  grids, and crossing quantiles
- the UI presents uncertainty as a q10-q90 interval and repeats that forecasts are uncertain, are
  not clinical guidance, and must not be used for insulin dosing or treatment decisions
- real-data forecast figures are confined to ignored `artifacts/forecasts/`; held-out future truth
  is excluded by default and requires an explicit local-only flag
- the Phase 5 application schema is reproducible from migrations and stores no research dataset;
  its committed seed is explicitly synthetic and contains no account or health record
- every exposed application table has RLS enabled; anonymous table access is revoked and
  authenticated owner isolation is tested against two synthetic users
- invalid glucose values and crossing forecast quantiles fail database constraints
- generated local Supabase configuration, endpoints, project references, connection strings, and
  credentials remain ignored; Phase 5 does not create or modify a hosted project
- py-mgipsim source and its 68-package environment are isolated under ignored `.cache/` paths and
  verified against exact commit `b985f8c2ea385d1b2b8480957b730866e07772f1`
- the Phase 6 protocol is fixed, synthetic, explicitly opt-in, and reproduced across two runs
- simulator exports use relative minutes and omit real identifiers, absolute timestamps,
  individual insulin values, and dose fields
- simulated glucose is labeled feasibility/demo evidence and is not used as clinical truth or a
  substitute for held-out T1D-UOM evaluation

The implemented persistence q10/q50/q90 trajectories are equal because the baseline is
deterministic. They are not presented as uncertainty estimates or clinical confidence.

## 7A. Dataset timestamp and duplicate risk

### M2 implementation safeguards and observed limitations

The actual app uses verified session identity and owner-token RLS; no client-supplied
owner is trusted. Provider keys and privileged catalog writes stay server-side.
Recipe-model requests contain recipe text only, not CGM/insulin/participant context,
and provider retention is disabled in the prepared Responses request. Structured
extraction requires confirmation and deterministic food-fact calculations.

The public M1 simulator export remains dose-free. M2 adds a separate ignored,
server-internal synthetic context export and privately owned application insulin
history for inference; it is never a dose recommendation. Only pre-origin simulated
CGM is imported. SQL retrieval excludes outcomes unavailable at the query origin.
Future-event leakage, invalid grids, owner isolation, retry behavior and atomicity
have scoped tests. No real-user data, hosted deployment or clinical claims were added.

The observed pretrained errors do not beat persistence, and nominal q10-q90 intervals
are under-covered. These are explicit research limitations, not reasons to change
the frozen test selection or silently clip/repair outputs. Live nutrition credentials,
provider validation and physical camera capture remain unresolved closure evidence.

### Risk
T1D-UOM V1.0.4 uses day-first timestamps despite month-first wording in its README, provides no timezone offsets, and contains repeated timestamps including conflicting CGM values.

### October 16 refinement safeguards

Small Ridge/LightGBM heads may improve average validation errors while still failing
often at +/-10 or producing large errors. The tolerance is aspirational. Original
test results are preserved but reused only diagnostically. Separate calibration
does not ensure conditional/clinical coverage, especially under AZT1D source shift.
Validation selection is optimistic; report independent results before app promotion.
The application model remains unchanged in this research cycle.

AZT1D downloads and row-level forecasts/model states stay ignored. Only canonical
CGM files are ingested; serial-number Visual Statistics exports are excluded. Missing
nutrients are not observed zero predictors. Conflicting CGM timestamps and duplicate
rows have tested rules; ambiguous basal units are not converted. Exact trajectory
checks cannot establish cross-source subject identity. External selection is frozen
before prediction, and the resulting test cannot support subsequent untouched-test
claims. Joblib state is trusted-local only. No patient uploads, paid calls, dosing
or pump control. See ADR 0010 and the refinement report for measured limitations.

### MetaboNet intake safeguards - October 16

The aggregate intake reads test metadata only; no test glucose/insulin/carbohydrate
values, clinical outcomes or forecasts. Raw IDs are reused across sources: namespace
IDs before joins/splitting and check cross-source aliases rather than assuming unique
people. Supplied train/test has 169 overlapping source-qualified IDs, mostly without
a horizon buffer. Freeze a new protocol and purge target boundaries before training.
AZT1D/UOM copies must not return as new development or independent-test evidence.
Preserve event missingness and interval-time semantics; source-local offsets are not
automatically bad cadence. OhioT1DM use rights require current release confirmation;
quarantine that source from training while preparing other documented cohorts.
Parquet/scratch/aggregate JSON remain ignored; only sanitized report aggregates enter
Git. No paid compute, model training, app promotion, patient upload or medical advice.

Saved-dictionary definitions resolve insulin as prior-five-minute IU amounts; avoid
hourly-rate conversion and counting total insulin again with its components. IOBP2
encodes all delivery as bolus, so it cannot silently become a conventional meal-bolus
input. Some timezone/zero-null semantics remain ambiguous. The dictionary is not a
licence grant or proof of unique global IDs. Saved HTML/resources stay under ignored
raw data and are parsed as inert text, never executed, uploaded or included in Graphify.

Phase 2 preparation now enforces metadata-only test reservation, source-qualified
whole-subject roles, capped deterministic candidates, immutable request/target separation
and corruption/replay checks. All subject manifests, projections, windows and source
snapshots stay ignored. The selected pilot uses only Loop/ReplaceBG; 104 unseen test
identities and 65 PEDAP identities are reserved. PEDAP is a separate pediatric shift,
not interchangeable with adult development. There were no partial exact fingerprint
matches among selected development IDs; aliases are still possible. Five-minute
meal availability is an assumption. Missing masks cannot establish complete logging
or undo upstream processing, and retrospective future-meal exclusion narrows the
evaluated population. Retain these limitations with future scores. No accuracy or
clinical guarantee follows from the successful build. See
[the frozen protocol](GlycoLens_12_MetaboNet_Experiment.md).

Phase 3 uses cached weights offline and only validation examples. It preserves every
attempt, including invalid native model outputs, and permits only failure-free options
in full-cohort selection. Resume requires unchanged input/configuration/source hashes
and checksummed records; completed output cannot be replayed. Do not turn a native
quantile-contract failure into an apparently successful median by silently repairing
bands or dropping cases. Raw coverage is not interval calibration, and validation
ranking is not external confirmation. C1/C2 comparisons are predictive, not causal
nutrient/insulin effects. No application promotion or clinical guarantee follows.
See [protocol 13](GlycoLens_13_MetaboNet_Frozen_Inference.md).

Executed evidence reinforces the boundary: persistence beat eligible frozen Chronos
options; Chronos native 80% bands covered only 49.42-64.08%, negative median predictions
occurred, and longer histories had contract failures. Failure-free means a software
contract passed, not physiological plausibility or clinical adequacy. Preserve these
negative outputs for unbiased research metrics; do not present them as acceptable
clinical forecasts. Accuracy remains far from the +/-10 aspiration. Research-only
results authorize neither treatment use nor automatic application promotion.

Phase 4 adds explicit training-only whole-subject CV, train-fold transformations,
participant-balanced weights and origin-only native-unit/mask features. Model bundles
remain ignored and are hash-checked before trusted local deserialization. A numeric
scoring interruption was repaired with a separate archived completion step: original
CV choices/model bytes were verified unchanged, and only the scalar-conversion line
could differ from the frozen runner. No hidden retraining or outcome-based retry.

LightGBM's validation MAE fell 16.03% to 31.17 mg/dL, but within +/-10 is just 26.84%,
whole-curve success 0.52% and maximum error 235.38 mg/dL. Ridge has better within-10;
both learned models have lower whole-curve success than persistence. A passed MAE
gate is not uniform improvement or clinical adequacy. Direct equal quantiles are
deterministic placeholders, not calibrated uncertainty; never report their coverage
as confidence. At Phase 4 completion calibration/reserved tests were untouched; Phase 6 below now records their use. Phase 6 independent evaluation is still required. See
[protocol 14](GlycoLens_14_MetaboNet_Direct_Models.md) and
[results](../reports/metabonet-phase4-training-2026-10-16.md).

### T1D-UOM timestamp mitigation

- pin the exact V1.0.4 DOI and release commit
- parse the observed day-first format before fallback formats
- keep timestamps timezone-naive until a documented DST/cross-source policy exists
- collapse only exact repeated CGM values
- exclude conflicting same-timestamp CGM values rather than silently selecting or averaging them
- report missing and repeated records in aggregate
- keep raw and derived row-level data outside Git

## 8. Counterfactual risk

### Risk
"What-if 50% portion" can sound causal.

### Mitigation
Use wording:
- "model-based scenario"
- "predicted trajectory under changed meal features"

Do not use:
- "this is what would definitely happen"
- "this is safe"
- "you should eat this"

## 9. GraphRAG scope risk

### Risk
GraphRAG consumes time without improving the core goal.

### Decision
Not in MVP.

Use:
- PostgreSQL
- pgvector
- SQL/numeric similarity

Only add graph technology if:
1. all M2 core features work
2. a concrete retrieval question cannot be handled cleanly in Postgres
3. advisor agrees it adds capstone value

Developer note: a local Graphify repository knowledge graph may be used for code and documentation navigation. It is tooling only and must not be presented as the product's GraphRAG architecture or ingest secrets, health datasets, private CGM exports, model weights, or generated artifacts.

## 10. Mobile scope risk

### Risk
Native iOS + Android doubles delivery complexity.

### Decision
Mobile-first PWA.

Native React Native/Expo only if advisor explicitly requests native.

## 11. External API risk

### USDA
API key and rate/access dependence.

Mitigation:
- backend caching
- save resolved foods locally

### Open Food Facts
Community data can be incomplete/inaccurate.

Mitigation:
- display source
- prefer USDA where appropriate
- ask user to verify nutrition label
- do not silently merge conflicting values

### Dexcom
Developer access/sandbox behavior can change.

Mitigation:
- device-agnostic `CGMProvider`
- demo works with historical/simulated providers

## 12. Cloud/inference cost risk

### Accepted initial host and remaining operational risks

The November 7 user decision selects Hostinger KVM 2 with managed Supabase,
initially Free subject to measured capacity. [ADR 0016](../decisions/0016-initial-hostinger-kvm2-managed-supabase.md)
records the prepaid commitment, renewal, separate API/database costs and pending
hosted verification. Resource specifications do not establish smooth concurrent
operation: sustained CPU use can exhaust Hostinger credits, model workers duplicate
memory, and current model/simulator locks return busy responses on overlap.

Keep one backend worker initially, bound simulator work, configure CPU threads,
warm/persist the model and measure the complete deployment. The VPS is self-managed;
patching, HTTPS, firewall, monitoring and recovery need explicit ownership. Supabase
quotas/inactivity and its backup/restore plan remain separate from VPS disk/backups.
Keep research datasets private/off the app host and preserve user-token RLS.
Linux simulator paths and reproducible containers remain deployment prerequisites.
Provider selection does not authorize real-user data or establish clinical readiness.

### Mitigation
- models selected partly for practical inference
- verified local inference/demo fallback for defense
- cache model in process
- do not depend on expensive managed GPU service
- retain the working local app workflow and package a reproducible Docker/Compose fallback

## 13. Privacy risk

For MVP:
- use public de-identified research data
- simulated users
- sandbox data

If real users are ever added:
- advisor/IRB/privacy requirements must be checked
- OAuth tokens and health data require stronger security
- HIPAA/compliance should not be assumed from ordinary cloud configuration

## 14. Schedule risk

### Scope-cut priority

Cut first:
1. image-based meal estimation
2. GraphRAG
3. clinician portal/report
4. native mobile
5. real-user integration
6. CGMformer downstream training
7. learned personalization

Protect:
1. research pipeline
2. pretrained model comparison
3. core context experiment
4. working meal/nutrition flow
5. forecast UI
6. Meal Passport
7. final results

## 15. Go/no-go checkpoints

### By Milestone 1
At least one pretrained model must run on real CGM data.

If not:
- use TimesFM-2.5 / simpler Chronos variant
- keep LightGBM as emergency forecast baseline

### By Milestone 2
End-to-end:
`meal -> context -> forecast -> UI`

If not:
- stop adding integrations
- focus only on core app

### By Milestone 3
No new major features.
Only:
- test
- analyze
- fix
- document
- improve presentation


## MetaboNet Phase 5 completion

The first PowerShell launcher stopped on a retained numerical warning, before
validation or completed CV candidates. Resume preserved the frozen model design;
interruption evidence is retained. Late-loaded numerical libraries were not fully
limited by the requested two-thread context, so runtime claims carry that caveat.

**Phase 5 was complete before the Phase 6 evaluation recorded below.** Frozen C2
generated 6,756 training forecasts; 6,756 usable meals / 196 identities supported six CV
configurations / 18 fold fits and four final refits, with exactly matched direct
controls. Neither correction passed the predeclared incremental gate; retain Phase 4
LightGBM. Lowest-MAE eligible option: `ridge_residual_1000`; advancement candidate:
`lightgbm_direct` (macro MAE 31.17 mg/dL, within +/-10 26.84%). These are
reused-validation findings, not independent confirmation. At Phase 5 completion, calibration/reserved outcomes were untouched.
Phase 6 below supersedes that access status; app inference remains unchanged.
See [protocol 15](GlycoLens_15_MetaboNet_Chronos_Correction.md) and [results](../reports/metabonet-phase5-correction-2026-10-16.md).

Saved heads contain no live foundation model; verify trusted local bytes before deserialization. Frozen baseline outputs are predictions, not future observations. Retain failed attempts and denominator integrity. No calibrated uncertainty or clinical/maximum-error claim; corrections still require backbone computation.

## MetaboNet Phase 6 completion - current status

**The broader-data model-refinement sequence, Phases 1-6, is complete.** Separate calibration used 48 participant representatives from 1,488 eligible meals. Frozen LightGBM scored 29.91 mg/dL macro trajectory MAE / 28.20% within +/-10 on 3,533 primary-test meals (102 IDs), and 40.92 / 19.57% on 2,177 PEDAP meals (64 IDs). Both predeclared point-improvement gates passed, with zero failed forecasts; tight precision remains poor. Nominal 80% marginal coverage was 79.05% primary and 63.94% PEDAP. Both test cohorts are now consumed; no test-based reselection, point refit, app promotion or full-M2 closure.

The +/-10 aspiration is unmet: complete-curve within-10 is 0.94% primary / 0.18% PEDAP, and maximum primary error is 264.87 mg/dL. PEDAP within-10 is essentially unchanged versus persistence (19.57%/19.56%). Primary marginal bands average 96.73 mg/dL wide and under-cover some early horizons; pediatric undercoverage blocks broad reliability claims. No dosing/clinical assurance or automatic app switch.

See [protocol 16](GlycoLens_16_MetaboNet_Independent_Evaluation.md), [independent results](../reports/metabonet-phase6-independent-2026-10-16.md) and [verification handoff](../tooling/metabonet-phase6-handoff-2026-10-16.md).
