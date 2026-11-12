# Milestone 2 approved implementation and evidence ledger

## November 12 development update

Demo actions are now **Run new simulation** / **Replay saved simulation**. Existing
Supabase logout is exposed in the app header and demo, with anonymous confirmation
and identity-bound draft cleanup. Root Compose provides a local web/API runtime
with CPU forecasting, isolated simulator and external managed cloud Supabase;
see [ADR 0021](../decisions/0021-local-compose-runtime.md). The explicit
[meal-response protocol](../testing/meal-response-validation-protocol.md) adds
GL-P09-011/012 to the current 146-case plan. Sensitivity and observed accuracy
remain unexecuted; no clinical claim or model/research-test change follows.
See the [review and actual validation](../reports/demo-logout-compose-review-2026-11-12.md).
[GitHub delivery authorization](../reports/github-checkpoint-delivery-2026-11-12.md) supersedes the earlier local-review hold for this checkpoint. No hosted deployment or phase acceptance is implied.

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

Current follow-up: the user selected **cloud Supabase from now on** for new
application work, with a dedicated development project and verified email/password
accounts. [Plan 17](GlycoLens_17_Webapp_Implementation_Plan.md) and
[ADR 0018](../decisions/0018-cloud-supabase-and-staged-webapp-delivery.md) define the
staged implementation and future cloud tests. The local M2 results/commands below
are historical evidence; they are not the new cloud setup path or fresh acceptance.
No recorded phase status, model result, course date or M2 closure changes here.

November 10 documentation follow-up: the [Figma review](../reports/figma-reference-review-2026-11-10.md)
and [responsive UI architecture](../architecture/responsive-webapp-ui.md) define
future account/onboarding and multi-page UI extraction. This is a design update,
not a new executable M2 feature or acceptance result. The existing phase ledger
below remains the evidence boundary; implementation is staged in the M3 checklist,
without changing course dates, model behavior or open provider/camera gates.

Approved by the user on October 14, 2026. Full milestone scope; py-mgipsim first,
Dexcom later; API-backed recipe extraction with editable confirmed ingredients.
Research/education only. No dosing, pump control, real-user study, or hosted deployment.

November 7 deployment follow-up: the user selected Hostinger KVM 2 with managed
Supabase as the initial target in [ADR 0016](../decisions/0016-initial-hostinger-kvm2-managed-supabase.md).
Implementation and hosted acceptance are tracked in the [M3 deployment checklist](GlycoLens_06_Milestones_and_Schedule.md#initial-hostinger-kvm-2-deployment).
The October 14 implementation boundary and recorded local evidence above remain
historical; no hosted deployment has been executed, and M2 live-provider/camera
checks and final acceptance remain open.

The October 26 [advisor report](../reports/GlycoLens_Milestone_2_Advisor_Report_2026-10-26.md)
consolidates prototype verification, all model experiments, current limitations and
proposed next steps. Its [Word copy](../reports/GlycoLens_Milestone_2_Advisor_Report_2026-10-26.docx)
and [email draft](../reports/GlycoLens_Milestone_2_Advisor_Email_Draft_2026-10-26.md) do not
change these acceptance gates or claim full M2 closure.

November 2 update: the user approved ten main presentation slides plus four backups
and confirmed November 3 with 5–6 minutes plus questions. The
[RIT PowerPoint draft](../presentations/GlycoLens_Milestone_2_Presentation_2026-11-03_v4.pptx)
and [matching notes](../reports/GlycoLens_Milestone_2_Presentation_Notes.md) are prepared,
originally targeting 5:30. On November 3 the user requested plain-language speaking
material lasting 7–8 minutes. The current v4 deck and notes target 7:30, with the
requested presentation wording removed. This edits presentation content only.
Application requirements, recorded checks and acceptance gates remain unchanged.
No new application/model runs or full closure are claimed.

## Delivery contract

The required flow is demo patient -> timeline -> meal entry -> nutrition review -> saved
meal -> selected pretrained inference -> probabilistic forecast. Also required: two
pretrained evaluations plus persistence, C0-C3 ablation, data/split/leakage evidence,
SQL numeric similar-meal retrieval, and live app simulator execution.

The approved estimate is 13-22 focused working days, re-estimated after Phase 3.
This is an implementation estimate, not an extension of official course deadlines.
The October 16 M2 and November 13 M3 course dates remain unchanged; overlap is a risk.

## Phases and acceptance gates

| Phase | Scope | Gate | Status |
|---|---|---|---|
| 0 | Baseline and prerequisites | Normal checks executable; readiness and blockers recorded | Complete |
| 1 | Data semantics and protocol | C2, separated insulin semantics, stable manifests, chronological/subject definitions, quality report and leakage tests | Complete; source-unit ambiguity explicitly retained |
| 2 | Batch evaluator and TimesFM | Matched C0 validation for persistence/Chronos/TimesFM, metrics and explicit failure accounting | Complete |
| 3 | Covariate adapters and ablation | Real C0-C3 inputs; matched validation; provisional selection frozen before test | Complete |
| 4 | Demo Auth, persistence, timeline | Session isolation; atomic/idempotent saves; migrations/RLS checks | Complete |
| 5 | Nutrition and recipes | Search/barcode/LLM extraction; confirmation; deterministic totals and provenance | Implemented/offline tested; live provider configuration pending |
| 6 | Live py-mgipsim | Authenticated bounded execution; simulated clock; past-only internal context; labeled replay | Complete |
| 7 | Forecast API | Real selected model, validated and persisted 24-point forecasts; safe failures | Complete |
| 8 | Screens and numeric retrieval | All required input paths, mobile flow, same-user past-outcome retrieval | Implemented; real fixture-food flow and browser input contracts pass; live nutrition paths await Phase 5 |
| 9 | Verification and closure | Held-out results, full acceptance evidence, report and presentation | Held-out evaluation, core checks, report and presentation draft ready; full closure pending live providers, camera and final acceptance |

Each phase updates affected planning documents, tests, ADRs and this ledger. Evidence
must distinguish implemented code, offline tests, real integrations and scientific results.
No phase is marked complete merely because scaffolding exists.

## Prerequisites

Python 3.12/uv, Node 22/pnpm 10, local Docker/Supabase, pinned local dataset,
checkpoint access/storage, existing isolated simulator environment, USDA key,
Open Food Facts User-Agent, and recipe API model/key. Secrets remain ignored/server-side.
Run `python scripts/dev/check_m2_prerequisites.py` for a value-free readiness report.

## Baseline evidence

Normal Python 3.12.5 and pnpm work outside the restricted execution sandbox. The
previous launcher/dependency errors were sandbox permissions, not missing runtimes.
Python: 75 passed, one explicit real-simulator skip; Ruff lint passed.
Frontend behavior: three files/five tests passed, plus lint/type/build.
Two pre-existing Codex-config validation formatting failures were corrected without behavior changes.
Docker daemon reports 28.4.0. Installed Supabase CLI 2.31.4 is older than the previously
validated 2.118.0; database readiness requires a real local check, not version inference.

## October 14 implementation evidence

- 927 real windows reproduced; temporal partitions: 536 development, 177 validation,
  211 test, three purged. Twelve participants have both validation and test events.
- Two pinned pretrained models and persistence ran C0-C3. Validation uses 171 matched
  successes out of 177 requests; test uses 208 common successes out of 211 requests.
- Chronos C3 was frozen on validation as the best pretrained configuration, before
  test execution. It does not beat persistence. The nominal q10-q90 interval is
  under-covered; no efficacy, calibration or clinical claim is made.
- Final local schema/reset/lint and 35 pgTAP tests passed, including owner isolation,
  source snapshots, atomic invalid-grid rollback and outcome-availability chronology.
- The actual local Auth -> live simulator -> saved fixture meal -> Chronos C3 ->
  persisted forecast -> numeric historical retrieval path passed with 24 forecast points.
- Six Playwright desktop/mobile checks pass: two real model/simulator flows and four
  synthetic browser input/confirmation contracts. Page-width checks prevent mobile overflow.
- Five existing frontend component/client tests, lint, TypeScript and build pass.
- 94 offline Python tests pass with one explicit simulator skip; the opted-in real
  simulator suite separately passes all 11 tests.
- The local Docker image exposed a template/postgres collation mismatch on restart.
  Reindexing and refreshing both local databases restored the complete stack. A
  workspace-pinned Supabase CLI 2.118.0 is available; no global CLI was replaced.
- Server and public-client local configuration is generated only in ignored files.
  The recipe model is configurable; no paid recipe call has been made without keys.

See [model results](../reports/milestone-2-model-results.md) and the implementation
verification report. Raw health rows, tokens, weights, simulator-internal observations,
screenshots and research result artifacts remain ignored.

## Remaining prerequisites for full closure

November 6 user direction: Azure recipe data is being corrected and is not yet to be
used. The [catalog migration strategy](../reports/azure-to-supabase-catalog-migration-strategy-2026-11-06.md)
plans a compact corrected copy after validation. No export/import or provider switch
has occurred. Existing live nutrition, recipe-input and final acceptance requirements
remain open until the adopted source is deliberately integrated and verified.

Milestone placement: the catalog audit and strategy are M2 feasibility/planning
evidence. Corrected-release export, local sizing, Supabase import and application
acceptance are listed as M3 carry-forward work in the
[milestone schedule](GlycoLens_06_Milestones_and_Schedule.md#corrected-nutrition-catalog-migration-from-milestone-2).
This placement preserves the unresolved M2 nutrition gates and the correction hold.

The user must privately configure USDA_FDC_API_KEY, LLM_API_KEY and LLM_MODEL and
confirm the recipe provider/model. An OpenAI Responses adapter is prepared; another
provider requires its supported structured-output adapter. Open Food Facts and local
Supabase configuration are prepared. Live USDA search/detail and real recipe extraction
still need execution, provenance checks and browser verification. Camera hardware
capture is implemented but has not been physically exercised; manual barcode entry
and mocked barcode contracts are verified. Presentation material must disclose this
status rather than assert full milestone completion.

## Scope and safeguards

Research manifests, timestamps, participant identifiers and row-level results remain in
ignored research/artifact paths. Only sanitized aggregate reports enter documentation.
Freeze splits and feature representations before comparative selection. Never leak test
targets to adapters, normalization, retrieval or selection. Report unusable runs.
Model quantiles are estimates; persistence quantiles are deterministic placeholders.
Optional after core work: Dexcom, vector embeddings, C4, extra history experiments,
CGMformer. History experiments, modest direct/residual heads and separate interval
calibration were subsequently approved on October 16; their phase ledger/results are
in [planning document 11](GlycoLens_11_Model_Refinement.md). They preserve original M2
results and app behavior. MetaboNet Phase 2 preparation is now executed and verified
under [document 12](GlycoLens_12_MetaboNet_Experiment.md): bounded source-qualified
ingestion, fixed development roles, origin-safe windows and metadata-only test
reservations. No new forecasting/training or test-value projection. The next stage
was Phase 3 inference validation; [preparation evidence](../reports/metabonet-phase2-preparation-2026-10-16.md)
does not establish better accuracy or authorize an application model switch.
This research does
not complete the remaining live nutrition/camera/presentation checks.

Subsequent Phase 3 is complete under [protocol 13](GlycoLens_13_MetaboNet_Frozen_Inference.md):
1,509 matched validation events, seven runs, no training/calibration/test access.
Persistence won among failure-free options; native Chronos accuracy/reliability did
not pass the improvement gate. This supports the next direct-small-model training
stage, not M2 closure or an app model switch. See the
[executed results](../reports/metabonet-phase3-inference-2026-10-16.md).
Subsequent Phase 4 is complete under [protocol 14](GlycoLens_14_MetaboNet_Direct_Models.md):
32 training-only CV candidates, both final refits, then the same 1,509-meal validation
comparison. LightGBM macro MAE 31.17 versus 37.12 persistence passes the research gate
(16.03% improvement), while within +/-10 remains poor at 26.84%. Ridge has higher
within-10 at 28.85%. At Phase 4 completion there had been no calibration/test access or app promotion; Phase 6 below now records independent testing. A scoring-only numeric repair preserved all fits and decisions. See
[Phase 4 results](../reports/metabonet-phase4-training-2026-10-16.md). These research
gains do not close live nutrition/camera/presentation gates or imply clinical accuracy.
Full Meal Passport, portion comparison and later
actual-versus-predicted follow-up remain M3 work.


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

## MetaboNet Phase 6 completion - current status

**The broader-data model-refinement sequence, Phases 1-6, is complete.** Separate calibration used 48 participant representatives from 1,488 eligible meals. Frozen LightGBM scored 29.91 mg/dL macro trajectory MAE / 28.20% within +/-10 on 3,533 primary-test meals (102 IDs), and 40.92 / 19.57% on 2,177 PEDAP meals (64 IDs). Both predeclared point-improvement gates passed, with zero failed forecasts; tight precision remains poor. Nominal 80% marginal coverage was 79.05% primary and 63.94% PEDAP. Both test cohorts are now consumed; no test-based reselection, point refit, app promotion or full-M2 closure.

This is the sixth phase of the additional model-refinement sequence, not the application's Phase 6 or full milestone closure. Remaining live nutrition/recipe configuration and verification plus presentation work remain governed by this implementation ledger.

See [protocol 16](GlycoLens_16_MetaboNet_Independent_Evaluation.md), [independent results](../reports/metabonet-phase6-independent-2026-10-16.md) and [verification handoff](../tooling/metabonet-phase6-handoff-2026-10-16.md).
