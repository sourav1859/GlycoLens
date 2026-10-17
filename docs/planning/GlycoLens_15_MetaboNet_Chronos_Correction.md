# MetaboNet Phase 5: frozen-Chronos correction protocol

Approved October 16, 2026 within the user's instruction to proceed. Version
`metabonet_phase5_v1`. Freeze each stage's sources/configuration before execution;
archive this protocol before the first backbone call and before head fitting.

## Fixed design and acceptance

- Preserve completed Phase 2/3/4 artifacts. No calibration or reserved test outcomes,
  raw-data reprocessing, foundation-weight updates, application changes or uploads.
  Five-minute availability, two-hour/24-point targets and isolated-meal limitations
  are inherited. +/-10 remains aspirational, not a maximum-error acceptance condition.
- Backbone is the pinned frozen six-hour C2 Chronos configuration: the best
  failure-free Chronos option in Phase 3. Current/previous carbs, recorded basal/
  bolus and source masks use exactly the saved C2 request schema. No insulin total
  double counting. Forecasts come only from immutable origin-known requests.
- Use the Phase 4 common four-history training pool: 6,756 meals / 196 identities,
  preserving its three stable source-stratified subject folds. Generate one frozen
  C2 forecast per training meal, persist every success/failure, and never retry
  failed predictions or repair native quantiles. Drop failed training backbone
  rows only because a residual target cannot be defined; report this attrition.
  Recompute participant weights within the usable training pool/fold.
- Fixed features: Phase 4's 127 features from 24-hour CGM plus six-hour recorded
  events, augmented by the 24 frozen C2 median changes from current glucose.
  Frozen future predictions are inputs; future observations are labels only.
  No identities, source labels, absolute time, nutrients or physiological estimates.
- Four correction configurations: Ridge alpha 10/1000; pooled-horizon LightGBM
  15/31 leaves. Use Phase 4's unchanged 160-tree/.04 learning rate/min-child100/
  max-bin63/lambda1/seed20261016/two-thread settings. Ridge fits 24 residual outputs;
  LightGBM expands horizons only after subject splitting. Fit imputation/scaling
  only on each training fold. No adaptive search or validation early stopping.
- Rank training OOF participant-average MAE, tie higher within-10 then stable name;
  a failed/nonfinite fold excludes its candidate. Freeze one correction per family
  before reading prepared validation outcomes, then refit on all usable common
  training meals. Do not expand the refit pool in this phase.
- Fit two direct controls with the fixed Phase 4 choices (24-hour events, Ridge
  alpha 1000 / LightGBM 31 leaves) on exactly the same usable training events. Their
  three-fold OOF results and final refits separate training-population changes from
  the added frozen forecasts. These controls are not retuned. Correction-vs-control
  comparisons use identical subjects, labels, weights and fold assignments.
- Validation remains the same 1,509 events / 48 identities. Verify and reuse the
  seven original Phase 3 runs and two original Phase 4 direct runs. Reuse C2
  predictions only for matching request fingerprints, identities, origins and
  targets; no new validation Chronos calls. Keep invalid backbone outputs as failed
  correction attempts. Cached baselines do not justify silently dropping events.
- Report all 13 options: nine original runs, two correction winners and two matched
  direct controls. Primary rank only failure-free options over all 1,509 events,
  using the unchanged MAE-first rule. Report all-attempt yields, pairwise and
  all-option common-success populations, tails/30/60/120-minute errors, whole-curve
  tolerance, negative predictions and source subgroups. No clipping or repair.
- Preserve the overall >=10% MAE reduction / within-10 nondecrease / p95 nonincrease
  gate versus persistence. Separately predeclare an incremental correction gate:
  >=5% lower macro MAE than the original Phase 4 LightGBM incumbent, no lower
  within-10, no worse pooled p95, and zero failed validation attempts. Report
  correction-minus-incumbent and correction-minus-same-family-control descriptive
  participant-bootstrap intervals (10,000 draws, seed20261016). No independence or
  multiplicity-adjusted significance claim follows from reused validation.
- Record the lowest-MAE eligible option separately from the advancement decision.
  If no correction passes the incremental gate, retain the Phase 4 incumbent for
  the later frozen comparison, even if a correction has a tiny point-estimate gain.
  Keep Ridge's tolerance tradeoff visible; do not change the ranking after results.
- Corrected models return deterministic quantile placeholders, not the backbone's
  uncorrected native bands. No interval-coverage claim or calibration in this phase.
  Save head weights without the Chronos model. Verify bytes before trusted local
  deserialization and check reload/prediction equivalence and frozen state.
- Ignored output: `artifacts/evaluation-results/metabonet-phase5-v1/`, with separate
  `backbone/` and `heads/` execution/source snapshots. Freeze checkpoint/input hashes,
  cohort/folds, environment, progress, CV choices, models, validation and completion
  manifests. Resume only intact matching stages; refuse completed replay/corruption.

Close Phase 5 after synthetic leakage/cache/group/reload/failure tests, actual frozen
training forecasts, train-only CV/refits, paired validation and independent metric/
artifact verification. A negative result completes the phase. Next is Phase 6:
predeclare final selection/calibration/test protocol, calibrate separately and score
reserved primary/PEDAP cohorts once. No automatic app promotion or clinical claim.

## Execution ledger

The Ridge correction's 0.03 mg/dL MAE gain over the incumbent has a descriptive
95% delta interval [-0.48,0.43], including no improvement. Its within-10 is 29.12%
versus 26.84% LightGBM direct, but only 0.27 percentage points above original Ridge
direct (28.85%). LightGBM correction is worse at MAE 31.75 / within-10 25.95%.
These bounded heads add little beyond the direct models; they do not establish
that every possible Chronos correction is ineffective.

The first head launcher stopped on a numerical warning during an incomplete CV
candidate, before completed candidates or validation predictions. Corrected stderr
handling resumed identical frozen sources/settings; the lost partial candidate was
recomputed, with no outcome-based retry. Warnings and interrupted logs are retained.
An isolated import-order audit found late-loaded SciPy/OpenMP at 16 threads despite
the requested two-thread context. Strict universal head thread limits were not
established; the head runtime is the resumed attempt, excluding interrupted work.
Future profiling should preload estimator libraries before applying limits. This
operational caveat does not change the independently reproduced accuracy scores.

**Phase 5 was complete before the Phase 6 evaluation recorded below.** Frozen C2
generated 6,756 training forecasts; 6,756 usable meals / 196 identities supported six CV
configurations / 18 fold fits and four final refits, with exactly matched direct
controls. Neither correction passed the predeclared incremental gate; retain Phase 4
LightGBM. Lowest-MAE eligible option: `ridge_residual_1000`; advancement candidate:
`lightgbm_direct` (macro MAE 31.17 mg/dL, within +/-10 26.84%). These are
reused-validation findings, not independent confirmation. At Phase 5 completion, calibration/reserved outcomes were untouched.
Phase 6 below supersedes that access status; app inference remains unchanged.

Backbone failures: {}; causes: {}. No retry/repair or outcome-based exclusion. CV choices: ridge_residual_1000, lightgbm_residual_31. All four final bundles use 6,756 meals. Selected advancement maximum error 235.38 mg/dL; whole-curve within-10 0.52%. No calibrated bands.

Ten focused tests and 144 full Python tests pass, one opt-in simulator skip and one existing dependency warning. Saved/public/batch predictions and model state, all CV/validation macro scores, source/row/model/input hashes, prior outputs and checkpoint files were independently verified. Execution snapshots preserve the pre-outcome protocol; this ledger was updated afterwards. No foundation training or app promotion.

See [results](../reports/metabonet-phase5-correction-2026-10-16.md) and [verification handoff](../tooling/metabonet-phase5-handoff-2026-10-16.md).

## MetaboNet Phase 6 completion - current status

**The broader-data model-refinement sequence, Phases 1-6, is complete.** Separate calibration used 48 participant representatives from 1,488 eligible meals. Frozen LightGBM scored 29.91 mg/dL macro trajectory MAE / 28.20% within +/-10 on 3,533 primary-test meals (102 IDs), and 40.92 / 19.57% on 2,177 PEDAP meals (64 IDs). Both predeclared point-improvement gates passed, with zero failed forecasts; tight precision remains poor. Nominal 80% marginal coverage was 79.05% primary and 63.94% PEDAP. Both test cohorts are now consumed; no test-based reselection, point refit, app promotion or full-M2 closure.

Neither correction was reselected for independent testing. Original direct LightGBM advanced under the predeclared incremental gate; diagnostic Ridge was fixed separately. Phase 5 source archives, forecasts and head bundles remain unchanged.

See [protocol 16](GlycoLens_16_MetaboNet_Independent_Evaluation.md), [independent results](../reports/metabonet-phase6-independent-2026-10-16.md) and [verification handoff](../tooling/metabonet-phase6-handoff-2026-10-16.md).
