# GlycoLens Milestones and Course-Aligned Schedule

## November 12: explicit P09 validation and local runtime work

- [x] Specify the controlled meal/portion response and separate outcome-accuracy
  gates in [the protocol](../testing/meal-response-validation-protocol.md).
- [ ] Execute GL-P09-011 with frozen context, labeled nutrient fixtures, repeated
  baselines, portion/composition contrasts and full failure/sensitivity reporting.
- [ ] Execute GL-P09-012 only with an approved untouched matching-outcome target;
  current fixed simulator replay and consumed research test cohorts are unsuitable.
- [x] Implement clearer demo labels, shared discoverable logout and a root local
  Compose configuration with managed cloud Supabase; validation is tracked in the
  [November 12 report](../reports/demo-logout-compose-review-2026-11-12.md).
- [ ] Complete hosted readiness, physical-device/manual UAT, recovery and release
  acceptance. Local container evidence does not close P10 or deployment.

The current catalog has 146 cases. Course dates, model selection, independent
research results and the user's deferred scratch replay decision are unchanged.

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

## 1. Source-of-truth dates

This plan uses the **current CSCI-788 schedule PDF** for Fall 2026 dates. Older class slides are used only for the **meaning/content of Milestones 1-3**, not for their historical dates.

The course schedule is provisional and the advisor may set earlier deadlines.

November 3 presentation revision: after the earlier November 3 date/shorter-slot
confirmation, the user requested an extended 7–8 minute suggested speech in plain
language. The [revised PowerPoint](../presentations/GlycoLens_Milestone_2_Presentation_2026-11-03_v4.pptx)
and [matching notes](../reports/GlycoLens_Milestone_2_Presentation_Notes.md) now target
7:30 across ten main slides, with four hidden backups. This replaces the earlier
5:30 script and records the requested speaking material, not a change to course policy.
Preparation does not change official deadlines, establish that the talk was delivered,
or close remaining live verification and acceptance gates.

### Current course dates

| Item | Current schedule |
|---|---|
| Week 3 - Scientific methods | Sep 8 |
| Project Spec A | Sep 15 |
| Milestone 1 work deadline | **Sep 18** |
| Project Spec B | Sep 22 |
| Milestone 1 A presentation | Sep 29 |
| Milestone 1 B presentation | Oct 6 |
| Milestone 2 work deadline | **Oct 16** |
| Report/poster preparation class | Oct 20 |
| Milestone 2 A | Oct 27 |
| Milestone 2 B | Nov 3 |
| Milestone 3 A | Nov 10 |
| Milestone 3 work deadline | **Nov 13** |
| Milestone 3 B | Nov 17 |
| Poster A | Nov 24 |
| Poster B | Dec 1 |
| Poster final submission | **Dec 6** |
| Final report | **Dec 11** |
| Project defense | **Dec 11, 9:30-11:00 AM** |

## 2. Course meaning of milestones

The course material defines:

### Milestone 1
**Understanding and planning how to solve the problem**
- project specification
- literature review
- current state
- choose and learn methods/tools
- feasibility study
- simulation

### Milestone 2
**Solving the problem**
- algorithms/data structures
- feasibility work
- simulation
- system/code prototyping

### Milestone 3
**Implementing and analyzing the solution**
- system execution
- debugging
- testing
- documentation
- data collection
- verification against specification

The GlycoLens plan below follows this structure.

---

# Milestone 0 - Project Specification
## Sep 7 - Sep 15/22

### Goal
Lock a defensible project scope before heavy development.

### Work

- finalize inference-first scope
- literature survey
- model shortlist:
  - Chronos-2
  - TimesFM-3
  - CGMformer exploratory
- confirm T1D-UOM schema
- download/test public data
- define app MVP
- choose mobile-first PWA
- draft system architecture
- define scientific questions
- define safety boundary
- build repo structure

### Project-spec deliverables

- title
- rationale/problem
- goal
- background
- attack plan
- work plan
- deliverables

### Internal target
Have the project spec substantially ready by **Sep 13**, before the Sep 15 presentation.

---

# Milestone 1 - Understanding, Feasibility, and Planning
## Work deadline: Sep 18
## Presentations: Sep 29 / Oct 6

### Goal
Prove that the proposed architecture is technically feasible.

### Required deliverables

#### Research
- categorized literature survey
- model-selection matrix
- dataset audit
- evaluation protocol

#### Model feasibility
- one Chronos-2 smoke test on CGM
- one TimesFM smoke test if possible
- define common `ForecastModelAdapter`
- verify 2-hour output/quantiles
- record runtime/memory

#### Data
- ingest T1D-UOM
- align at least:
  - CGM
  - meals
  - insulin
- generate first meal-centered windows

#### App/system
- Next.js PWA skeleton
- FastAPI skeleton
- PostgreSQL/Supabase schema
- architecture diagram
- one dummy end-to-end API call

#### Simulation
- py-mgipsim installed and one virtual scenario executed

### Milestone 1 success criteria

- at least one pretrained model runs end to end
- T1D-UOM meal event can be converted into model-ready context
- app can call backend
- scope and model selection criteria are fixed

### Progress snapshot - September 29, 2026

Completed:

- pinned and verified T1D-UOM V1.0.4 provenance
- implemented an aggregate audit for CGM, nutrition, basal insulin, and bolus insulin
- implemented and tested leakage-safe five-minute meal-window generation
- demonstrated 927 eligible windows with 24 pre-meal CGM points, prior insulin context, full meal nutrition, and 24 held-out future CGM points
- established reproducible Python 3.12/uv and Node.js 22/pnpm toolchains with project manifests
  and lockfiles
- added a buildable Next.js/TypeScript PWA with an accessible synthetic forecast chart, loading,
  failure, and retry states
- implemented and tested the common immutable forecast adapter contract with future truth kept
  outside model requests
- implemented the persistence baseline and verified a 24-point forecast with q10/q50/q90 on one
  real eligible T1D-UOM V1.0.4 window
- implemented C0, C1, and available C3 meal-window conversion for later context ablation
- pinned `chronos-forecasting==2.3.2` and the exact `amazon/chronos-2` checkpoint revision
- ran Chronos-2 end to end on a real eligible C0 window with 24 q10/q50/q90 output points,
  finite/non-crossing validation, cached-load and repeated latency evidence, and memory evidence
- implemented a typed FastAPI health route and synthetic forecast endpoint mapped from the common
  contract, with explicit local CORS allowlisting and no identifiers or absolute timestamps
- validated the running Next.js and FastAPI endpoints plus the browser fetch/component contract,
  and added a separate ignored real Chronos-2 research graph with observed history, median
  forecast, and q10-q90 interval
- implemented the executable local Supabase migration with ten application tables, pgvector,
  constraints, indexes, synthetic seed data, and denial-by-default RLS
- passed a clean database reset, schema lint, 20 pgTAP database tests, and static checks preventing
  committed connection details or credentials
- pinned the official py-mgipsim source and its isolated dependency set, executed one fixed
  ExtHovorka/OpenLoop synthetic day, validated 288 five-minute samples, and reproduced the exact
  result across two real runs
- created and validated a seven-slide RIT-branded milestone presentation with speaker notes, two
  editable charts, an editable closure table, and explicit research/safety boundaries
- completed the final closure audit: 73 Python tests passed with one explicit simulator opt-in
  skip, the real simulator suite passed all 11 tests, all five frontend tests plus lint/type/build
  passed, a clean database reset and all 20 pgTAP tests passed, and privacy scans found no private
  academic-address domains or absolute local paths

**Closure status:** Milestone 1 is complete. The pretrained-model, model-ready context, dummy
app-to-backend, simulator, documentation, validation, and presentation criteria are satisfied.
TimesFM remains a desirable comparison if time permits, not a blocker for Milestone 1 closure.

### What to present

Course presentation guidance suggests:
- problem reminder
- solution reminder
- work completed
- obstacles
- insights
- next milestone
- schedule problems/help needed

---

# Milestone 2 - Solve the Core Problem / Working Prototype
## Work deadline: Oct 16
## Presentations: Oct 27 / Nov 3

### Approved implementation sequence - October 14, 2026

Full scope was approved with py-mgipsim first and API-backed editable recipe parsing.
The implementation estimate is 13-22 focused working days, subject to re-estimation
after covariate validation. This does not revise official course deadlines or imply
an advisor extension. Overlap with the November 13 M3 deadline is an explicit risk.
Track actual phases and evidence in [the M2 ledger](GlycoLens_10_Milestone_2_Implementation.md).

November 6 carry-forward: the read-only Azure catalog audit and
[Azure to Supabase migration strategy](../reports/azure-to-supabase-catalog-migration-strategy-2026-11-06.md)
provide M2 feasibility/planning evidence. Executing the corrected-data migration and
verifying its application integration are tracked under M3 below. This does not close
the outstanding M2 live-nutrition requirements or revise course deadlines.

### Goal
Have a usable model pipeline and a working application prototype.

### Additional approved research - October 16

The user approved the refinement phases in [planning document 11](GlycoLens_11_Model_Refinement.md):
protocol/error audit, external-data preparation, frozen history comparison, small direct
models, frozen-Chronos residual heads and independent verification. Local data comes
first; larger MetaboNet training is deferred. Files were subsequently received and
audited on October 16 (metadata-only test access); data preparation/split repair and
terms confirmation precede a new CPU pilot. Report execution evidence in the dated
refinement report and preserve original M2 results. This work does not close live
nutrition/camera/presentation gates, revise the October 16 deadline, imply an advisor
extension, or authorize deployment. Schedule remaining work from measured outcomes;
foundation-model training is a separate later decision.

**Historical development results through Phase 5; Phase 6 completion is recorded below.**
The real Loop/ReplaceBG pilot produced 8,973 training / 2,000 validation /
1,948 calibration six-hour windows. Frozen protocol, metadata-only test reservations,
integrity checks and six new synthetic tests are recorded in
[document 12](GlycoLens_12_MetaboNet_Experiment.md) and the
[preparation report](../reports/metabonet-phase2-preparation-2026-10-16.md).
At Phase 2 completion the 104 primary-test and 65 PEDAP reservations were unscored, with test eligibility deferred; Phase 6 below now records their use. Preparation took 4.69 minutes locally;
this does not predict inference/training effort or revise official deadlines.
Initial UOM phases 3-6 and their failed external improvement gate remain historical
evidence. The subsequent Phase 6 completed the broader sequence, while the +/-10 precision objective remains unmet. Phase 3 ran seven comparisons on 1,509 matched events in 28.86 minutes
of inference/aggregation. Persistence beat eligible Chronos options; the improvement
gate failed. Two-hour C0 is the sole failure-free C0; longer histories have better
conditional accuracy but output failures. No training/test access or official deadline
change. See [protocol 13 and ledger](GlycoLens_13_MetaboNet_Frozen_Inference.md).

Phase 4 trained 32 candidates / 96 fold fits, then two 24-hour-event refits on
6,794 meals / 197 identities. LightGBM reached validation MAE 31.17 versus 37.12
persistence (16.03% lower; gate passes). Within +/-10 remains poor at 26.84%.
Measured wall time was 9.26 minutes from execution freeze through completion,
including an audited scoring-only repair, not a later-phase estimate. Calibration
and the 104 primary-test / 65 PEDAP reservations were untouched at Phase 4 completion;
Phase 6 below now records their use. Phase 4 did not close all M2 gates, change a
deadline or demonstrate independently tested accuracy.
See [protocol 14](GlycoLens_14_MetaboNet_Direct_Models.md) and
[results](../reports/metabonet-phase4-training-2026-10-16.md).

### Model/inference deliverables

- Chronos-2 benchmark on core event set
- TimesFM benchmark on same event set
- persistence baseline
- choose top 1-2 models
- context ablation:
  - CGM
  - + insulin
  - + carbs
  - + full nutrition
- first accuracy/latency results

### Data deliverables

- robust T1D-UOM meal-window generator
- leakage checks
- chronological and/or subject-aware test definitions
- data-quality report

### App deliverables

Required screens:
- home CGM timeline
- add meal
- barcode/search
- recipe parser
- nutrition review
- forecast screen

Backend:
- food lookup
- meal save
- forecast endpoint
- model adapter
- timeline endpoint

### Personalization deliverable

- first similar-meal query using SQL + numeric similarity
- pgvector semantic similarity optional but preferred by end of M2

### Integration

At least one:
- Dexcom Sandbox retrieval **or**
- py-mgipsim live scenario inside app

Ideally both by the end of the milestone.

### Milestone 2 success criteria

October 14 progress: phases 0-4 and 6-7 have executable evidence; the core browser
flow and numeric retrieval are implemented and verified using a confirmed fixture
food, actual local Auth, live simulator and pretrained model. Both pretrained
benchmarks and C0-C3 validation/test comparisons are complete. Phase 5 live nutrition
checks await API configuration, and Phase 8 live nutrition input verification follows.
Phase 9 has model results and core checks but full closure/presentation is pending.
Do not present fixture recipe/barcode responses as live provider evidence.

A user can:

```text
open app
-> choose demo patient
-> enter meal
-> see nutrition
-> run selected pretrained model
-> see forecast
```

---

# Milestone 3 - Integration, Analysis, and Verification
## Work deadline: Nov 13
## Presentations: Nov 10 / Nov 17

Because Milestone 3 A is Nov 10 and the work deadline is Nov 13, aim for an **internal feature freeze by Nov 7**.

### Goal
Turn the prototype into the final evaluated capstone system.

### Responsive UI architecture and page extraction - November 10

The user subsequently confirmed the full phased implementation in
[plan 17](GlycoLens_17_Webapp_Implementation_Plan.md) and dedicated **cloud Supabase
development from now on**, with email/password verification/reset. Its P00-P10
phases refine the A-D checklist below; [ADR 0018](../decisions/0018-cloud-supabase-and-staged-webapp-delivery.md)
records the environment decision. The 27-46 focused-day estimate excludes external
waits and is not a revision of course dates or a promise to finish the expanded
scope by November 13. The linked 146 cases begin NOT_RUN. No phase/migration/cloud
acceptance is complete merely because its plan is drafted.

The user requested a Figma-informed documentation and architecture update. The
[44-node audit](../reports/figma-reference-review-2026-11-10.md),
[ADR 0017](../decisions/0017-responsive-webapp-and-figma-reference-boundary.md) and
[UI architecture](../architecture/responsive-webapp-ui.md) are the design baseline.
No runtime UI change, migration, hosted verification or M2 closure follows from
this documentation. Official dates and the November 7 internal freeze are unchanged;
the expanded page inventory requires staged delivery rather than a new deadline promise.

- [x] Inspect all supplied Figma nodes and record source/adaptation boundaries.
- [x] Define shared routes/components, minimal onboarding, responsive behavior,
  schema/API proposals and acceptance requirements in living documentation.
- [ ] A: implement shared tokens/navigation, permanent Auth and minimal persisted
  onboarding/preferences, basic account/source/help/privacy controls; retain demo fallback.
- [ ] B: extract existing meal/scan/text-analysis/forecast workflows into routes;
  add daily meal history, shared consumed-nutrition aggregate, Home and Nutrition.
- [ ] C: after corrected-catalog acceptance, add catalog search/details and typed
  favorites; add owned nonclinical in-app notifications with verified events.
- [ ] D: complete original planned portion comparison and actual-vs-predicted
  follow-up with immutable inputs/availability; keep deferred integrations explicit.
- [ ] Verify each implemented slice at mobile/tablet/desktop widths, keyboard,
  zoom, safe areas, source/account switching and two-user isolation. Preserve the
  live-provider/camera gates; do not count mock screens as integration acceptance.

If prerequisites or remaining course time prevent a slice, record it as pending
and keep the reliable local meal-to-forecast demonstration. Household, shopping,
AI planning, guided cooking and photo/URL inference are not added to this plan.

### Initial Hostinger KVM 2 deployment

On November 7, the user selected **Hostinger KVM 2 with managed Supabase** for the
initial application deployment. [ADR 0016](../decisions/0016-initial-hostinger-kvm2-managed-supabase.md)
and [architecture section 13](GlycoLens_04_Tech_Stack_and_System_Architecture.md#13-deployment)
define the target and acceptance requirements. This is M3 integration/verification
work; provider selection does not close M2's live-provider/camera acceptance gates.

- [x] Select KVM 2 for the PWA, FastAPI, CPU model and simulator, retaining managed Supabase.
- [ ] Provision the selected host/project and record private DNS, region, subscription
  and capacity settings when execution is authorized; no purchase or deployment is recorded yet.
- [ ] Add pinned Linux containers, portable simulator configuration, CPU thread
  limits, persistent caches/replays and model/simulator readiness checks.
- [ ] Configure HTTPS, frontend/API origins, private secrets and managed Supabase
  migrations/Auth/RLS; verify cross-user isolation and recovery before publication.
- [ ] Verify overlap/busy handling and the complete desktop/mobile meal-to-forecast
  workflow, measuring cold/warm/p95 latency, full-stack memory, CPU credits and quotas.
- [ ] Verify restart recovery, database backup/restore and the local demo fallback;
  retain the previous compatible application release and record hosted acceptance.

Start with Supabase Free only while measured requirements fit. Upgrade the VPS or
database independently when evidence requires it. Keep bulk research and Graphify
local; retain the current application model and deferred catalog-correction gates.
The November 7 internal feature freeze and official course deadlines are unchanged.

### Corrected nutrition catalog migration from Milestone 2

Track the [migration strategy and measured storage budget](../reports/azure-to-supabase-catalog-migration-strategy-2026-11-06.md)
and [ADR 0015](../decisions/0015-corrected-nutrition-catalog-migration.md) as M3
integration and verification work. The Azure audit and strategy are complete;
recipe use, full export, cloud import and application integration remain pending.
Upstream recipe corrections are a dependency, not evidence that the data is ready.

- [ ] Receive a corrected release/manifest and verify food mappings, energy units,
  recipe yields, ingredient quantities, missing values and source provenance.
- [ ] Export the approved catalog and dependency closure from a consistent
  read-only Azure snapshot, preserving stable IDs, checksums and a release manifest.
- [ ] Stage the compact schema in the dedicated cloud development project after
  reviewed target/migration preview; verify counts, relationships, nutrition
  calculations and actual size with required indexes. Check the target baseline and
  the strategy's Free plan operating budget before a cloud import.
- [ ] Import the validated compact catalog into Supabase with appropriate access
  controls, bounded staging and a retained rollback package.
- [ ] Connect the application food adapter, resolve gram/serving compatibility and
  preserve source snapshots without changing the forecasting model.
- [ ] Pass desktop/mobile search, barcode and recipe-review meal-to-forecast
  acceptance, including safe failures, persistence and rollback evidence.

If a corrected release is unavailable before the feature freeze, keep migration
deferred and record the dependency explicitly. Preserve a reliable local demo with
reviewed food facts; do not claim live provider or catalog acceptance from fixtures.
The existing November 7 internal freeze and November 13 course deadline are unchanged.

### Required features

- final selected model(s)
- uncertainty visualization
- similar meals / Meal Passport
- what-if portion comparison
- actual-vs-predicted result view
- simulation integration
- Dexcom Sandbox integration if feasible
- error handling/loading states
- provenance labels

### Final analysis

- model comparison
- context ablation
- latency
- uncertainty
- representative forecasts
- limitations

### Testing

- unit tests for data transforms
- model adapter tests
- nutrition calculation tests
- critical Playwright UI flows
- deterministic demo scenario

### Milestone 3 success criteria

- end-to-end app works
- final experiment set is complete or nearly complete
- results are reproducible
- no core feature depends on future development
- demo is reliable offline/local if cloud fails

---

# Poster / Final Stage
## Nov 18 - Dec 11

### Nov 18-23
- freeze main results
- create poster structure
- choose figures

### Nov 24 / Dec 1 poster sessions
- present draft
- collect feedback
- reduce text
- improve visual flow

Course poster guidance emphasizes:
- visual abstract
- readable in about 5 minutes
- title
- introduction
- background
- system/experiment
- results
- conclusions
- references

### By Dec 6
- submit final poster

### Dec 1-10
- final report
- final screenshots
- architecture figure
- results tables
- proofreading
- reproducibility appendix / repo instructions

### Dec 11
- submit report
- defense/demo

---

# 3. Weekly rough plan

| Week | Date | GlycoLens target |
|---|---|---|
| 3 | Sep 8 | Scope + literature + architecture |
| 4 | Sep 15 | Project-spec presentation; model smoke test |
| 5 | Sep 22 | Project-spec refinement; M1 cleanup |
| 6 | Sep 29 | M1 presentation; begin benchmark pipeline |
| 7 | Oct 6 | M1 B; app nutrition flow |
| 8 | Oct 20 | M2 complete; begin full integration |
| 9 | Oct 27 | M2 A; forecast UI + retrieval |
| 10 | Nov 3 | M2 B; complete main features |
| 11 | Nov 10 | M3 A; feature freeze |
| 12 | Nov 17 | M3 B; results freeze |
| 13 | Nov 24 | Poster draft |
| 14 | Dec 1 | Poster final revisions |
| Final | Dec 6-11 | poster/report/defense |

## 4. Scope-cut order if behind

Cut in this order:

1. meal-image recognition
2. GraphRAG/Neo4j
3. real Dexcom users
4. clinician report
5. CGMformer downstream training
6. personal learned calibration
7. activity-context experiment
8. extra model candidates

Do **not** cut:
- working app
- T1D-UOM event pipeline
- at least two pretrained model evaluations
- persistence baseline
- forecast visualization
- meal nutrition
- core results

## 5. Milestone presentation template

Each milestone deck can follow:

1. Problem - 1 slide
2. Current solution/system - 1 slide
3. Previous milestone reminder - 1 slide
4. Progress:
   - completed
   - obstacles
   - insights
5. Results/demo
6. Next milestone
7. Schedule/risks/help needed

The course materials specify a roughly 5-6 minute milestone presentation, so the slides should remain concise.


## MetaboNet Phase 5 completion

**Phase 5 was complete before the Phase 6 evaluation recorded below.** Frozen C2
generated 6,756 training forecasts; 6,756 usable meals / 196 identities supported six CV
configurations / 18 fold fits and four final refits, with exactly matched direct
controls. Neither correction passed the predeclared incremental gate; retain Phase 4
LightGBM. Lowest-MAE eligible option: `ridge_residual_1000`; advancement candidate:
`lightgbm_direct` (macro MAE 31.17 mg/dL, within +/-10 26.84%). These are
reused-validation findings, not independent confirmation. At Phase 5 completion, calibration/reserved outcomes were untouched.
Phase 6 below supersedes that access status; app inference remains unchanged.
See [protocol 15](GlycoLens_15_MetaboNet_Chronos_Correction.md) and [results](../reports/metabonet-phase5-correction-2026-10-16.md).

Measured backbone time: 41.20 minutes; resumed head CV/refit/validation: 1.99 minutes. CPU limit two was requested, but late-loaded numerical libraries were not universally limited. No official deadline revision or M2 closure.

## MetaboNet Phase 6 completion - current status

**The broader-data model-refinement sequence, Phases 1-6, is complete.** Separate calibration used 48 participant representatives from 1,488 eligible meals. Frozen LightGBM scored 29.91 mg/dL macro trajectory MAE / 28.20% within +/-10 on 3,533 primary-test meals (102 IDs), and 40.92 / 19.57% on 2,177 PEDAP meals (64 IDs). Both predeclared point-improvement gates passed, with zero failed forecasts; tight precision remains poor. Nominal 80% marginal coverage was 79.05% primary and 63.94% PEDAP. Both test cohorts are now consumed; no test-based reselection, point refit, app promotion or full-M2 closure.

Actual Phase 6 calibration took 3.35 seconds and reserved preparation/scoring 217.72 seconds, excluding initial prior/raw hashing. No official course deadline was revised. This completes the approved research sequence, not the remaining M2 application deliverables.

See [protocol 16](GlycoLens_16_MetaboNet_Independent_Evaluation.md), [independent results](../reports/metabonet-phase6-independent-2026-10-16.md) and [verification handoff](../tooling/metabonet-phase6-handoff-2026-10-16.md).
