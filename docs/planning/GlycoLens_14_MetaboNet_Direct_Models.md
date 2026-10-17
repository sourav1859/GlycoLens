# MetaboNet Phase 4: direct small-model protocol

Approved October 16, 2026. Version `metabonet_phase4_v1`. Freeze this protocol,
sources, environment and input hashes before fitting. No foundation-model training,
calibration/test-outcome access, app model replacement or external data upload.

## Acceptance and fixed design

- Verify Phase 2 preparation and completed Phase 3. Consume training for all model
  choices; validation only after per-family CV choices are frozen. Never iterate
  calibration, primary test or PEDAP. Preserve earlier artifacts.
- Compare histories 2/6/12/24 h and two feature profiles, CGM/masks or CGM plus
  recorded events. Use the common training-event intersection for fair history CV.
  Source-stratified stable-hash subject assignment creates three folds; each entire
  source-qualified identity stays in one fold, before target inspection. No source,
  participant identity, absolute date or clock-time predictor.
- Features read immutable ForecastRequest only. Preserve current glucose, last
  two-hour relative lags/masks, causal history summaries, availability fractions and
  short slopes. Event profile uses current known carbs, separate recorded bolus/
  basal/previous-carb amounts, source-present fractions, last-positive recency and
  mathematical exponential recency summaries (30/120-minute scales). These are
  descriptive features, not physiological IOB/COB or dosing recommendations.
- Keep native mg/dL/g/five-minute IU; ignore merged total insulin when components
  are supplied. Unknown event aggregates remain missing when nothing is recorded;
  true recorded zero remains distinct via masks. Do not invent full nutrients.
- Ridge grid: alpha 10/1000. LightGBM grid: 15/31 leaves, 160 trees, learning rate
  0.04, min_child_samples100, max_bin63, reg_lambda1, deterministic seed20261016,
  two threads. Eight history/profile choices times two parameters times two families
  = 32 candidates, each with three subject folds. No adaptive search or early stopping
  using validation outcomes.
- Ridge predicts all 24 glucose deltas from current glucose jointly. Median imputation
  and weighted StandardScaler fit on each training fold only. LightGBM handles NaN
  natively and fits one pooled-horizon delta regressor with horizon fraction as a
  feature; expand horizons only after subject splitting. Each event contributes
  equally at each horizon; inverse event counts give participants equal total weight.
  This pooled-horizon strategy is different from 24 independent boosted regressors.
- Rank out-of-fold participant-average MAE, tie higher participant-average within-10,
  then stable candidate name. Any failed/nonfinite fold makes a candidate ineligible.
  Freeze one candidate per family before reading validation windows/outcomes. Refit
  each on all training events eligible at its chosen history; report any extra events
  beyond the common CV pool. Refit transforms on training only, not fold holdouts or
  validation. Save trusted local models and verify reload prediction equivalence.
- Primary evaluation is the same 1,509 matched validation events/48 identities as
  Phase 3. Reuse verified saved forecasts only for exactly equal identities/targets;
  no new Chronos inference. Keep every old candidate/failure visible diagnostically.
  This conditional cohort excludes 621 otherwise two-hour-eligible meals; do not
  generalize its scores to all eligible/live meals or compare different populations.
- Select across the two fitted candidates and existing failure-free baselines on the
  complete cohort. Use macro MAE, tie higher within-10 then name. Retain the >=10%
  MAE reduction, within-10 nondecrease and pooled-p95 nonincrease gate versus persistence.
  Report all attempts, tails, 30/60/120-minute errors, negatives, source subgroups and
  participant-cluster 10,000-draw/seed20261016 descriptive intervals. Validation has
  been reused for selection; the reserved tests remain the independent check.
- Direct-model quantile fields are explicit deterministic placeholders, not calibrated
  80% bands. Do not report placeholder coverage as probabilistic accuracy. No clipping,
  error-based exclusion or retrying a failed candidate to improve its score.
- Freeze execution/source ZIP before fitting. Save checksummed CV outputs, per-family
  choices, models, validation predictions, decision and completion hashes only under
  ignored `artifacts/evaluation-results/metabonet-phase4-v1/`. Resume only matching
  execution and intact completed work; refuse completed replay and corrupt models.

## Phase gate and next work

Close Phase 4 after synthetic leakage/group/mask/weight/reload tests, real CV/refits,
paired validation, saved-model integrity/reload verification and documented findings.
Completion does not imply the accuracy gate passed. Two hours in Phase 3 was a
native-output reliability decision; this train-only CV deliberately tests longer
histories for small models without changing that earlier artifact.

Phase 5 subsequently compares frozen-Chronos corrections against the direct winner.
Phase 6 calibrates separately and evaluates frozen choices on reserved tests. No
clinical or +/-10 guarantee follows from validation gains.

## Execution ledger

**Complete, October 16, 2026. Phases 5 and 6 subsequently completed; see their ledgers/results below.** The design
above was archived before fitting; this ledger was updated after completion. The
original execution archive and scoring-repair archive remain immutable locally.

- Common CV pool: 6,756 meals / 196 identities, Loop 3,542 / ReplaceBG 3,214.
  All 32 candidates / 96 fold fits succeeded. Both families chose 24-hour event
  features: Ridge alpha 1000, LightGBM 31 leaves. Their OOF macro MAEs were 31.02
  and 30.94 mg/dL. Final refits used 6,794 meals / 197 identities (38 more meals
  and one more identity than CV), with 127 origin-only features.
  The selected 24-hour setting refers to glucose history; event summaries use the
  preceding six hours plus origin-known current carbs.
- Same 1,509 validation meals / 48 identities as Phase 3; no new Chronos calls.
  LightGBM wins the frozen MAE-first rule: macro MAE 31.17 versus 37.12 persistence,
  16.03% lower; within-10 26.84% versus 25.47%; pooled p95 91.16 versus 111.00.
  All three gate conditions pass. Ridge has MAE 31.36 and higher within-10 28.85%.
  Both fitted models had zero failed events and zero negative predicted points.
- Selected endpoint MAEs at 30/60/120 minutes: 20.71/34.10/44.92 mg/dL. Maximum
  error 235.38 mg/dL; whole-curve within-10 only 0.52%, below persistence 1.44%.
  This is better average error but still poor tight-tolerance accuracy. Descriptive
  selected-minus-persistence MAE delta -5.95, 95% interval [-7.60,-4.33]. Reused
  validation is not independent confirmation. No calibrated bands yet.
- The original run completed all fitting and froze choices, then failed before its
  first persisted scored validation row because NumPy booleans cannot enter
  statistics.mean. A synthetic regression reproduced it. A separately archived
  completion step verified CV/model hashes and allowed only the native-float
  conversion line to differ from the frozen runner. No choice/feature/parameter
  changed and no fit was repeated. The original empty prediction file is retained.
- Independent checks reproduced every CV/validation macro score, all row/input/
  model hashes and saved/public prediction equivalence, including unchanged model
  state, original Phase 2/3 outputs and Chronos files. Scaling warnings were logged;
  all OOF predictions and saved scaler/coefficients are finite. Twelve new focused
  tests pass; full Python suite: 134 passed, one opt-in simulator skip, one existing
  TestClient dependency warning. Ruff passed. No calibration/test outcomes or app
  model promotion; all private artifacts remain ignored.

Wall time from execution freeze through completed scoring was 9.26 minutes including
the scoring repair. This is not a later-phase estimate. Phase 5 should predeclare
train-only correction choices and compare with frozen direct models, retaining Ridge
as a tolerance challenger. Phase 6 handles calibration and reserved tests only after
selection. See [results](../reports/metabonet-phase4-training-2026-10-16.md) and
[verification handoff](../tooling/metabonet-phase4-handoff-2026-10-16.md).


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

Original model bundles, train-only transforms and 6,794-meal refits were reused unchanged. Independent testing confirms LightGBM's average-error benefit, while the tolerance objective remains unmet. Calibration modifies only interval state, not point predictions.

See [protocol 16](GlycoLens_16_MetaboNet_Independent_Evaluation.md), [independent results](../reports/metabonet-phase6-independent-2026-10-16.md) and [verification handoff](../tooling/metabonet-phase6-handoff-2026-10-16.md).
