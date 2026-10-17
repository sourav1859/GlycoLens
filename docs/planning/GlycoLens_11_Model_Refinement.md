# Approved model refinement protocol and execution ledger

Execution started October 16, 2026 following user approval in this conversation.
The user clarified that +/-10 mg/dL is an aspirational error tolerance, not a
maximum-error acceptance guarantee. The forecast remains 24 five-minute readings
over two hours. No dosing, pump control, real-user study or hosted deployment.

## Frozen research rules, version refinement_v1

- Preserve the M2 artifacts, original 927-event manifest and published results.
  The original test has been inspected and is now diagnostic, not a fresh final test.
- Inherit original event/split assignments for history-length comparisons; never
  rebuild temporal cuts separately for each history's eligible survivors.
- Within each participant's original development interval, reserve the final 20%
  of its time span for calibration and purge targets crossing this new cut.
  Fit transforms/models only on the remaining earlier training events. Original
  validation events select configurations; calibration outcomes do not fit point models.
- Reserve AZT1D as an independent external common-feature cohort. Audit schema and
  eligibility before selection, but do not compute predictive test scores until a
  model/configuration is frozen. MetaboNet development must exclude AZT1D and all
  copies of T1D-UOM; preserve cohort and subject provenance and check duplicates.
- Primary selection: participant-average trajectory MAE, then higher participant-
  average fraction within +/-10 for ties. Report +/-10 rates prominently, endpoints,
  whole-curve pass rates, pooled p95/p99 and maximum errors, missingness and failures.
  A proposed improvement gate is >=10% lower validation MAE than matched persistence,
  no lower +/-10 rate, and no higher pooled p95 error. Report failure of this gate.
  Failure rates and attempted-event tolerance yields accompany successful-set metrics.
- No output clipping, future CGM/events, test-fitted normalization, or retrospective
  removal of hard cases to improve a score. Source-quality exclusions require
  predeclared rules and sensitivity reporting. No synthetic data in real-data metrics.
- Compare 2/6/12/24-hour histories on matched events and report survivor counts.
  Keep the full available history-specific validation results as secondary analyses.
- Small-model grid: Ridge alpha {1,10,100}; LightGBM leaves {7,15}, 150 trees,
  learning rate .03, min_child_samples 20, seed 20261016, deterministic CPU execution.
  Patient-equal training weights; no subject ID as a predictor. Predict glucose change
  relative to origin. Full-nutrient and shared-feature models are separate experiments.
- Use recorded bolus units and missingness; do not turn ambiguous T1D-UOM basal values
  into doses/rates or invent insulin-on-board. Earlier meals and time since recorded
  events may be features. Clock features retain source-local/unknown-timezone semantics.
- Frozen Chronos corrections learn residuals on training outcomes only. Compare with
  direct small models and persistence; allow the baseline to win. Backbone weights stay
  unchanged. Large-model training and optional extra candidates are not required here.
- Calibrate symmetric marginal 80% bands on separate calibration residuals, assess
  coverage and width on validation/external data. No conditional/clinical coverage
  guarantee; correlated observations and cohort shift limit interpretation.
- A validated research winner does not automatically replace the application's M2
  model. Shared-feature external results do not validate full protein/fat/fiber effects.

## Phase ledger

**Current position in the broader-data plan: Phases 1-6 complete; tight-precision objective unmet.**
The approved streaming preparation is executed under
[document 12](GlycoLens_12_MetaboNet_Experiment.md). Primary six-hour data comprises
8,973 training / 2,000 validation / 1,948 calibration windows across 197/48/48 eligible
source-qualified IDs. Metadata-only reservations contain 104 unseen publisher-test
and 65 PEDAP identities. Frozen artifacts and leakage/integrity tests are verified.
No model fitting or test-value projection occurred in Phase 2. The subsequent
[Phase 3 comparison](GlycoLens_13_MetaboNet_Frozen_Inference.md) generated seven sets
of validation forecasts on 1,509 matched events. Persistence won among failure-free
options (macro MAE 37.12 mg/dL; C2 37.61); the improvement gate failed. Two-hour C0
is the sole failure-free C0, not the point-accuracy optimum. Longer-history signal
is useful among valid outputs, but their native contracts failed on some requests.
Phase 4 trained 32 fixed candidates with three subject folds, then two final refits;
LightGBM achieved macro MAE 31.17 versus 37.12 persistence on the same 1,509 validation
meals, passing the 16.03% improvement gate. Within +/-10 remains poor at 26.84%; Ridge
reaches 28.85% with MAE 31.36. At Phase 4 completion calibration/reserved outcomes were untouched; Phase 6 below now records their use.

| Broader-data phase | Current status |
|---|---|
| 1. Evaluation protocol | Established; tolerance/tail/failure rules remain active |
| 2. Broader development data | Complete; fixed pilot and metadata-only test reservations |
| 3. Frozen inference | Complete; failed improvement gate |
| 4. Small direct models | Complete; validation MAE gate passes, tight-tolerance objective unmet |
| 5. Frozen-Chronos correction | Complete; see incremental gate and retained candidate below |
| 6. Calibration / independent testing | Complete; point gate confirmed, pediatric undercoverage; tests consumed |

The table records the **initial local-data pilot**, executed while the user deferred
MetaboNet. Executing phases 3-6 in that pilot did not complete the broader-data plan
or pass its improvement gate. The subsequent MetaboNet experiment reuses tested
components on its own fixed development protocol. Six hours was the UOM reference
candidate, not a proven optimum; the new history decision is recorded in document 13.

| Phase | Acceptance evidence | Status |
|---|---|---|
| 1 Protocol and error audit | Frozen protocol, tolerance/tail tests, all 211 legacy results reproduced, negative-output/outlier audit | Executed |
| 2 Broader data | AZT1D checksum/loader/test; subsequent MetaboNet intake and executed preparation | Early pilot entry; subsequent MetaboNet Phases 2-6 complete below |
| 3 Frozen inference | 130 common eligible / 129 successful events across 2/6/12/24-hour validation; six hours selected | Executed |
| 4 Small models | 20 total direct/residual configurations; train-only transforms and saved-head reload verification | Executed on local cohort |
| 5 Chronos correction | Shared/full Ridge alpha 100 residual heads selected on validation; frozen foundation weights | Executed |
| 6 Independent verification | Selection frozen before external scoring; calibrated bands, failure accounting, bootstrap | Executed; external improvement gate failed |

### Results and decision

The local sequence completed in 7.24 minutes on CPU. Six-hour data: 391 training,
93 calibration, 162 validation events (10 validation participants). The shared residual
head improved selected validation MAE from 43.455 to 34.246 mg/dL and within-10 from
19.88% to 27.99%. Full-nutrient MAE was 34.922; adding nutrients did not improve
the best validation result, but this was not a controlled causal ablation.

On the independent AZT1D matched 2,608 successes, the shared head MAE was 34.874
versus persistence 33.865; within-10 was 24.98% versus 26.80%. Two additional attempted
requests failed because the frozen backbone returned crossing quantiles. The paired
MAE difference was +1.009, 95% participant-bootstrap [-0.353, 2.329] mg/dL: no reliable
advantage. Its calibrated coverage was 75.78% with 103.80 mg/dL mean width, not
80% within +/-10. Worst external point error was 269.45 mg/dL. The proposed gate failed.

Do not promote this research head. The local training improvement did not generalize.
The original C3 audit also found negative predictions (minimum -140.82) and worst
error 349.11 mg/dL. No score-changing clipping/removal was performed. Original
all-model matched and new all-C3 diagnostic denominators differ; preserve both.
See [the complete aggregate report](../reports/model-refinement-results-2026-10-16.md).

## Prerequisites and current findings

Existing Python 3.12.5/Chronos environment and approximately 360 GiB disk are available.
Python execution needs the existing local launcher outside the restricted tool sandbox;
this is not a broken installation. The local T1D-UOM release is present in the workspace
parent; the environment variable is absent, so research commands must use an explicit
dataset path or a private environment setting. No key is needed for local forecasting.
Scikit-learn 1.7.2 and LightGBM 4.6.0 were installed through the pinned `refinement`
dependency group with the original Chronos/TimesFM/plotting groups retained.

AZT1D V1 download, checksum, schema and source-local timestamp formats were verified.
Its external test is now consumed. At completion of the initial local run, MetaboNet
acquisition/development was deferred because the user chose local data first (later
intake is recorded below). Nothing further was required
from the user for the completed local run. Larger source-distinct training data and
a new untouched test are prerequisites for further tuning, not a reason to reuse
AZT1D as an untouched holdout. No registration, credentials, paid compute or external
service mutation was performed.
Nutrition API credentials remain a separate M2 application prerequisite.

## Traceability and records

| Risk/requirement | Verification |
|---|---|
| +/-10 boundary and complete-curve meaning | Synthetic metric tests including exactly +/-10 and isolated outliers |
| Large errors hidden by averaging | Pooled point p95/p99/max plus participant-macro accuracy |
| Target/subject leakage | Immutable requests; source/split checks; train-only fits; synthetic cutoff tests |
| Survivor bias/failures | Matched event sets, available-event counts, attempted-event success yields |
| Irreproducible selection | Protocol/configuration/source hashes, fixed seeds, frozen selection artifact |
| Health data/weights/secrets | Ignored data/artifact directories; sanitized aggregate reports only |

Commands, package versions, timings, exclusions, failures, model identities and result
hashes must accompany the results report and session handoff. Update this ledger after
real execution; do not mark a phase complete from unit tests alone. Course dates are
unchanged; this refinement must not erase outstanding M2 nutrition/presentation gates.

The ignored execution-source ZIP preserves all 38 original research source files and
the pre-run protocol document, each checked against execution provenance. Current
reporting/verification helpers and a pre-write replay guard were added after the
experiment; they did not alter forecasts/selection. A completed run refuses replay
into its frozen output directory. Use `verify_refinement` for integrity/saved-head
checks. Public documentation contains only aggregates; data, predictions and model
state remain ignored. The application remains on its existing M2 path.

## Subsequent MetaboNet intake - October 16, 2026

The user later supplied `train.parquet` and `test.parquet`, plus portal release-note
evidence for v1.2 (October 5). Both files are readable, with 132,811,004 / 22,069,548
rows and identical 37-column schemas. Exact hashes are in the
[intake report](../reports/metabonet-intake-audit-2026-10-16.md). The earlier deferral
remains the history of refinement_v1; this new intake does not change its frozen rules,
selection or consumed external test. No MetaboNet training or test prediction occurred.

The final source-aware audit finds 1,730 training / 351 test study-participant IDs,
169 shared combinations and 182 test-only before exclusions. Bare IDs repeat across
studies; a preliminary unresolved-source overlap count of 172 was superseded by 169.
166 shared combinations have the shared flag in both files. 164 have only a five-minute
boundary gap; five have interleaved/reversed ranges; no exact cross-file keys repeat.
Metadata-only access selected source, ID, timestamps and flags; no test outcome values.

Both previously evaluated cohorts occur in training (AZT1D 21 IDs, UOM 13), so exclude
their copies from new development. Missing carbohydrates in several studies prevent
direct meal-window use there; Loop/ReplaceBG/PEDAP/CTR3 are candidate meal-bearing
sources; BrisT1D and CTR3 lack separate bolus/basal. SIESTA's five IDs have five-minute cadence
with fixed subject-specific offsets, and no carb entries. Preserve relative cadence.
OhioT1DM's 12 IDs need current release terms confirmation; prepare other documented sources
while leaving it out of training. No blanket CC BY licence is assumed for all sources.

Next: finish source/terms/bin-semantics mapping; build streaming origin-safe shared
meal windows; freeze a new subject/source-aware validation/calibration/test protocol;
then run a balanced CPU pilot before scaling. Genuine supplied test-only participants
must be separated from shared-subject temporal diagnostics, and all two-hour targets
purged across cuts. No new model score, clinical promise, app promotion or training
has been produced by this audit. No additional data download, GPU or API key is
needed for preparation. The subsequent saved dictionary covers all 37 fields and
confirms all 15 training source labels. Units, trailing-five-minute insulin amounts,
IOBP2's all-insulin-as-bolus exception and split-flag definitions are now documented.
Carb availability/bin endpoints, source missingness and current use rights remain
open; README/terms would help. See the
[dictionary review](../reports/metabonet-dictionary-review-2026-10-16.md). No training
or test outcome access occurred in this follow-up.

## Phase 2 exit evidence and next work

The following checklist is implemented and verified. Source-balanced quotas selected
200 training / 50 validation / 50 calibration IDs before quality inspection, with at
most 100 hash-selected candidate origins each. The 28,852 sampled candidates yielded
the six-hour counts above, without replacement. No duplicate candidates were found
in 1,474,695 partial exact varied CGM fingerprints; this does not prove global identity.
Full counts, exclusions and reproduction commands are in the
[preparation report](../reports/metabonet-phase2-preparation-2026-10-16.md).

1. Implemented streaming, source-qualified shared-feature ingestion. AZT1D/UOM
   copies and OhioT1DM are excluded. Native amount units, missingness and source-specific
   insulin exceptions are preserved; no merged-insulin bolus or full nutrients invented.
2. Constructed origin-safe two-hour/24-point targets and four supported histories.
   Five-minute delayed carb availability and zero-minute development sensitivity are
   fixed. CGM gaps, clustered/future meals and source-present targets have explicit
   checks and aggregate exclusions. Eligible events/IDs are reported by study.
3. Froze provenance and a versioned protocol with disjoint training, validation and
   calibration subjects; targets stay inside their publisher-training source. Reserve
   104 primary test identities absent from all publisher training and 65 PEDAP source
   test identities. The earlier 182 test-only combinations were pre-exclusion candidates,
   not guaranteed usable independent people. Test-event eligibility remains deferred.
4. Recorded hashes, masks/exclusions, per-split eligible counts, executed source and
   successful synthetic leakage/identity/unit checks plus real artifact verification.
   These artifacts close Phase 2; a download alone does not.

Phase 3 compared frozen inference histories/representations on matched validation
events; Phase 4 subsequently completed the balanced CPU Ridge/LightGBM pilot on
197 eligible training identities; Phase 5 subsequently compared frozen-Chronos residual
heads against the direct models; Phase 6 scores the frozen choices once on reserved
test data and evaluates uncertainty, tails, failures and study/participant subgroups.
Do not assume the correction head must win or reuse AZT1D as an untouched final test.
No new large-model training, app promotion, deadline change or prediction result is implied.

The files/dictionary sufficed for preparation. Additional terms/README can be
reviewed in parallel; the unresolved OhioT1DM question need not block other cohorts.
The completed broader-data stage preserves frozen refinement_v1 rules and original results.

### Broader-data Phase 3 result

Completed seven validation runs / 10,563 attempts in 28.86 inference/aggregation minutes.
The only failure-free C0 was two hours (MAE 42.52); C2 six hours had MAE 37.61 versus
persistence 37.12. C0 six/twelve/24 hours failed 2/11/15 times; C1 failed once, C2 zero.
The frozen history artifact records two hours for the eligible C0 baseline. On the
1,487 all-option common-success events, 24-hour C0 improved MAE to 33.50 versus 36.84
persistence; do not confuse reliability selection with best conditional point accuracy.
Use train-only CV to examine longer-history small-model features in a new protocol.
Native bands undercovered, negative forecasts occurred, and no +/-10 objective was met.
Full metrics, failure populations and independent checks:
[report](../reports/metabonet-phase3-inference-2026-10-16.md),
[handoff](../tooling/metabonet-phase3-handoff-2026-10-16.md).

### Broader-data Phase 4 result

Training-only three-fold subject CV compared 32 candidates on 6,756 common training
meals/196 identities. Both families chose 24-hour event features; refits used 6,794
training meals/197 identities. LightGBM (31 leaves/160 trees) wins the predeclared
MAE-first rule:31.17 mg/dL versus 37.12 persistence, within-10 26.84% versus 25.47%,
pooled p95 91.16 versus 111.00. Descriptive MAE delta -5.95, interval[-7.60,-4.33].
Ridge alpha 1000 has MAE 31.36 and higher within-10 28.85%. Preserve it as a tolerance
challenger. Whole-curve within-10 worsens (LightGBM 0.52%, Ridge 0.76%, persistence 1.44%);
maximum LightGBM error 235.38. A passed average-error gate is not a +/-10 achievement.

All 96 CV fits and both final refits succeeded. A scoring-only native-float conversion
repair was archived separately, with original models/choices unchanged and no refits.
Independent checks reproduced CV/validation metrics and saved/public predictions;
134 Python tests pass with one opt-in simulator skip. Calibration/test outcomes and
foundation weights remain untouched; no app model switch. The Phase 5 comparison was predeclared before fitting and is now complete. See
[protocol 14](GlycoLens_14_MetaboNet_Direct_Models.md),
[report](../reports/metabonet-phase4-training-2026-10-16.md) and
[handoff](../tooling/metabonet-phase4-handoff-2026-10-16.md).


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

The next research iteration needs a new development-only plan: expand suitable development cohorts and timing-aware context, then assess participant adaptation with grouped validation. Do not tune on these consumed tests or describe AZT1D as untouched. More test records alone do not improve a frozen model's accuracy.

See [protocol 16](GlycoLens_16_MetaboNet_Independent_Evaluation.md), [independent results](../reports/metabonet-phase6-independent-2026-10-16.md) and [verification handoff](../tooling/metabonet-phase6-handoff-2026-10-16.md).
