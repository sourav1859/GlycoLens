# MetaboNet Phase 3: frozen inference protocol

Approved October 16, 2026. Version `metabonet_phase3_v1`. Settings below are fixed
before new inference. This phase does not fit weights, calibrate intervals, access
reserved test values or replace the application model.

## Acceptance and comparison design

- Verify the completed Phase 2 artifacts and consume validation only, primary
  five-minute meal availability. No raw Parquet access or training/calibration iteration.
- Compare the same 1,509 events eligible at all 2/6/12/24-hour histories. Verify
  participant, origin, targets and current glucose agree across variants. Report the
  original eligibility counts and matched-cohort loss, not only successful forecasts.
- Frozen CPU `amazon/chronos-2` revision
  `29ec3766d36d6f73f0696f85560a422f50e8498c`, package 2.3.2; two Torch threads,
  seed 20261016; q10/q50/q90, 24 five-minute future points. Use the existing common
  adapter unchanged, local cached weights and offline mode. One request per call.
- Seven predeclared runs: persistence; four CGM-only histories; six-hour recorded
  insulin context (C1); six-hour insulin plus logged carbohydrates (C2). Six hours
  for context comparisons is fixed from the prior pilot, not chosen after these
  scores. This does not search every history/context combination.
- C1 includes bolus/basal IU amounts, their source-present masks and the CGM mask.
  C2 adds previous logged carbs and their mask plus origin-known current carbs.
  Omit total insulin when components are used. No full nutrients, source/identity
  predictors, future insulin, invented physiological activity or known future CGM.
  Reuse `recorded_events_v1` alignment explicitly, including its observation channels;
  masks do not establish complete logging. Future meal impulses are zero under the
  already conditional no-follow-up-meal benchmark, not knowledge of unrestricted intake.
- Validate native quantiles. Count crossing/nonfinite/shape failures; do not sort,
  clip, retry failed model outputs or silently keep only good predictions. Persist
  every attempt, including failures. Resume only matching source/input/configuration
  fingerprints and request hashes; reject corrupted/mismatched progress. Completed
  runs refuse replay. Record execution sources, package versions and input hashes
  before inference, including local checkpoint-file hashes, and hash all completed artifacts.
- Primary comparable selection table uses the complete matched cohort and only
  failure-free candidates. Rank participant-average trajectory MAE, tie higher
  participant-average within +/-10, then stable name. Persistence can win. Also
  report all-run common-success metrics and per-candidate paired-baseline metrics,
  failures and attempted-point yields so failed candidates remain visible.
- Select the best failure-free CGM-only history for Phase 4; if none qualify, retain
  the predeclared six-hour fallback and disclose why. Freeze this history decision
  separately from the best overall frozen option. Do not claim a trained-model or
  final-test winner. Improvement gate remains >=10% macro MAE reduction, within-10
  nondecrease and pooled p95 nonincrease against matched persistence.
- Report within-10 point/whole-curve measures, 30/60/120-minute errors, pooled
  p95/p99/max, failures, native q10-q90 coverage/width, negative forecasts and source
  subgroups. Participant-cluster paired bootstrap uses 10,000 draws/seed20261016.
  Validation-selected intervals are descriptive, not selection-adjusted or external
  confirmation. Native 80% bands are not calibrated in this phase.

## Artifacts and next phase

Ignored output: `artifacts/evaluation-results/metabonet-phase3-v1/`. No row-level
records, IDs, dates or weights enter Git/Graphify. Public reports contain aggregates
only. Preserve Phase 2, original M2 and consumed UOM/AZT1D experiments unchanged.

Close this phase only after synthetic failure/leakage/resume checks, actual inference,
frozen history decision, artifact verification and documented results/limitations.
Phase 4 then trains modest direct Ridge/LightGBM candidates on training only using
the new masks deliberately; calibration and reserved tests remain separate.

## Execution ledger

**Complete, October 16, 2026.** Settings above
were archived before inference; this outcome ledger was updated afterwards. No
frozen output or original protocol snapshot was changed.

Seven runs attempted 1,509 events each (48 identities), totaling 10,563 attempts;
inference/aggregation took 28.86 minutes. All-option common-success set: 1,487 events.

| Failure-free option | Macro MAE mg/dL | Macro within +/-10 |
|---|---:|---:|
| Persistence | 37.12 | 25.47% |
| C2, six hours | 37.61 | 25.98% |
| C0, two hours | 42.52 | 23.52% |

Persistence won; the improvement gate failed. C0 six/twelve/24 hours failed 2/11/15
native contracts, C1 failed once, C2 none. The frozen history choice is two hours,
the only failure-free C0. **This is not the point-accuracy optimum:** on common-success
events, 24-hour C0 MAE is 33.50 versus persistence 36.84. Later trained-model history
features should be assessed with predeclared training-only CV, not inferred solely
from native-quantile reliability or changed retrospectively in this experiment.

Native nominal 80% interval coverage was 49.42-64.08% across Chronos options; negative
medians occurred. The frozen approach remains weak relative to +/-10. Larger data
evaluated frozen weights; it did not train them. Source/row hashes, paired truth,
macro metrics, unchanged prepared input and unchanged cached checkpoint files were
independently verified. Five focused tests, 97 research tests and 122 full Python
tests pass; the opt-in simulator test remains skipped. No calibration/test data used.

See [full results](../reports/metabonet-phase3-inference-2026-10-16.md) and
[verification handoff](../tooling/metabonet-phase3-handoff-2026-10-16.md). If Phase 4
expands to all events eligible at its chosen history, compare baselines on exactly
that population and use a separate output; retain the Phase 3 decision/evidence.

Subsequent Phase 4 is complete under [protocol 14](GlycoLens_14_MetaboNet_Direct_Models.md),
retaining this1,509-event population and reusing its verified predictions. Training-only
CV chose 24-hour event features for both small models; LightGBM reduced macro MAE
to 31.17 mg/dL (16.03% below persistence), passing the gate. Tight-tolerance accuracy
remains poor. The original frozen history decision/artifacts are unchanged. At Phase 4 completion calibration/reserved outcomes were untouched; Phase 6 below now records their use. See
[the new report](../reports/metabonet-phase4-training-2026-10-16.md).


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

The frozen-inference findings remain unchanged. Phase 6 did not run Chronos again or silently add failed Phase 3 options to test selection. Its primary model was the validated small direct incumbent.

See [protocol 16](GlycoLens_16_MetaboNet_Independent_Evaluation.md), [independent results](../reports/metabonet-phase6-independent-2026-10-16.md) and [verification handoff](../tooling/metabonet-phase6-handoff-2026-10-16.md).
