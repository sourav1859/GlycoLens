# MetaboNet Phase 6: frozen independent evaluation

Approved October 16, 2026 under the user's instruction to proceed. Version
`metabonet_phase6_v1`. Archive this document and execution sources before calibration
outcomes are accessed, and again before reserved outcome projection. A negative
result completes the experiment; it does not establish application readiness.

## Frozen choices and acceptance

- Primary candidate: the original Phase 4 `lightgbm_24h_events_31` bundle. Diagnostic
  challenger: original `ridge_24h_events_1000`. Baseline: persistence. No refitting,
  grid search, Chronos inference, correction-head advancement, clipping or test-based
  reselection. Phase 5's corrections failed their incremental advancement gate.
- Preserve prior artifacts and pinned raw input hashes. Use the unchanged 127 origin
  features, native units, 24-hour CGM history, six-hour event masks, five-minute carb
  availability and 24 five-minute targets. All models attempt identical eligible meals.
- Primary role: the 104 reserved Loop/ReplaceBG publisher-test identities absent
  from all publisher training. Separately report all 65 reserved PEDAP identities
  from their original train/test files. Do not join their histories/targets across
  publisher-file boundaries. No AZT1D, Ohio, other sources or shared development IDs.
- Before eligibility, cap each reserved participant at 100 positive-carb candidate
  origins, globally hash-ordered across that participant's permitted files. Reject
  duplicate timestamps within/between its file segments, rather than merge records.
  Keep the existing retrospective isolated-meal and history/target completeness rules;
  no replacement participants or candidates. Report every exclusion and zero-event ID.
- Compare the existing varied exact six-hour fingerprints at hourly endpoints across
  selected development references and all reserved segments. Quarantine reserved IDs
  that match a development ID or another reserved ID before scoring, irrespective of
  error. Do not alter trained models or recalibrate after this screening. Report any
  contaminated references. These rounded, partial trajectory checks cannot prove
  globally unique people or independence from foundation-model pretraining.

## Calibration locked before reserved-value access

Use only prepared **calibration** windows at 24 hours/delay five. Select exactly one
eligible event per participant by ascending SHA-256 of `phase6-calibration|event_id`;
this rule never considers glucose values or model errors. Fail closed on insufficient
participants, role leakage or any calibration prediction failure. Save selected IDs,
all attempted predictions and the immutable interval state before opening reserved CGM.
Point models and their imputers/scalers remain unchanged.

For each of the three frozen predictors, compute absolute errors on these participant
representatives. Target coverage is 80%; with m participants take the kth smallest
score, k = ceil((m+1)*0.8), without interpolation. Refuse a finite band if k exceeds m.
One score per horizon yields 24 symmetric **marginal** radii. Separately calibrate the
maximum absolute error across 24 horizons to obtain a constant-radius **whole-curve**
band. Do not label marginal coverage as simultaneous coverage. Do not retune coverage,
radii, participant sampling, features or model choice using test results.

The common adapter may expose the marginal band at q10/q90 and the unchanged point
forecast at q50, explicitly labeled symmetric calibrated bands rather than estimated
conditional quantiles. No positive clipping of lower bands. Report negative endpoints.
The finite-sample rank is motivated by split conformal prediction, but exchangeability
of these studies, hash-selected eligible meals and new participants is unverified.
There is no unconditional, patient-specific, pediatric or clinical coverage guarantee.
See [Angelopoulos and Bates](https://arxiv.org/abs/2107.07511). PEDAP is an explicit
distribution shift; retain its failures of coverage rather than recalibrate on it.

## Independent evidence and immutable execution

Archive sources/configuration, candidate/model/input hashes, dependencies and actual
threadpool state. Preload numerical estimator libraries before enforcing two threads.
Separate calibration and test completion manifests form a hash chain. Test preparation
requires a verified calibration completion and the same predeclared configuration.
The development iterator continues to reject reserved roles. Keep all raw/projection/
window/prediction/model/runtime artifacts under ignored local paths; no upload/app DB.
Completed stages refuse replay. Preserve partial output and failures for diagnosis;
do not retry a failed forecast or overwrite completed results to improve metrics.

Report primary and PEDAP separately: requested/eligible identities and events,
attrition, all-attempt failure and tolerance yields, per-model success-only metrics,
matched common-success diagnostics, participant-macro MAE/RMSE/within-10/whole-curve
tolerance, pooled p95/p99/max error, and 30/60/120-minute accuracy. Primary comparison
is the frozen LightGBM against persistence, with a descriptive paired participant
bootstrap (10,000 draws, seed20261016). Reuse the >=10% MAE reduction, within-10
nondecrease, p95 nonincrease and zero-failure gate to assess confirmation; failure
does not authorize switching to a test winner. Ridge comparisons are diagnostic.

For both calibrated bands report participant-macro and pooled point/whole-curve
coverage, widths, 30/60/120-minute coverage and negative endpoints. In-sample
calibration coverage is descriptive only. Predeclared subgroups: study; origin CGM
<70/70-180/>180 mg/dL; logged carbs <30/30-60/>60 g; basal+bolus record-mask completeness
<90% versus >=90%. Report counts and participant-performance distributions without
identities; small subgroups do not support strong claims. No subgroup tuning.

Completion requires synthetic role/leakage/quantile/failure/immutability/artifact
checks, actual separately frozen calibration and reserved evaluation, independent
metric/state/hash verification, aggregate results and synchronized living documents.
Tests become consumed after this run; later model tuning needs fresh confirmation.
The +/-10 goal remains aspirational. No M2 closure, clinical validation, application
model switch or deployment follows automatically.

## Execution ledger

**The broader-data model-refinement sequence, Phases 1-6, is complete.** Separate calibration used 48 participant representatives from 1,488 eligible meals. Frozen LightGBM scored 29.91 mg/dL macro trajectory MAE / 28.20% within +/-10 on 3,533 primary-test meals (102 IDs), and 40.92 / 19.57% on 2,177 PEDAP meals (64 IDs). Both predeclared point-improvement gates passed, with zero failed forecasts; tight precision remains poor. Nominal 80% marginal coverage was 79.05% primary and 63.94% PEDAP. Both test cohorts are now consumed; no test-based reselection, point refit, app promotion or full-M2 closure.

The fixed calibration rank was 40/48. LightGBM marginal radii at 30/60/120 minutes were 27.24/56.88/64.05 mg/dL; curve radius 80.35. Partial fingerprint screening flagged no reserved or development IDs. Eligible counts: 3,533 meals / 102 IDs primary, 2,177 / 64 PEDAP. All 17,130 test attempts succeeded. Original point states and prior artifacts remained unchanged. Actual loaded numerical pools all reported two threads.

Independent verification reproduced point/tail/coverage/subgroup results, calibration ranks and 18 public/batch/wrapper samples; checked source/row/model/input/checkpoint hashes and the calibration-before-test chain. Full Python preflight: 155 passed, one opt-in simulator skip and one existing dependency warning. No point training or test-based model selection occurred. These living notes were added after both stages completed; pre-outcome protocol/source snapshots remain in their ZIPs.

See [results](../reports/metabonet-phase6-independent-2026-10-16.md) and [handoff](../tooling/metabonet-phase6-handoff-2026-10-16.md).
