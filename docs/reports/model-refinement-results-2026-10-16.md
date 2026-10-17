# Model refinement results — October 16, 2026

Executed locally after user approval. **Research only; ±10 mg/dL is an aspiration, not a maximum-error guarantee.** The application model was not switched.

## Decision and interpretation

**The proposed improvement did not generalize to AZT1D. Do not promote the new model into the application.** It improved selected UOM validation, but its external MAE, ±10 rate and error tail were slightly worse than persistence. The external paired interval includes zero, so this establishes no reliable advantage in either direction. Performance is far from an 80% within-±10 objective.

The frozen shared-feature choice is **ridge_residual_shared_100**, with **6 hours** of CGM history. The full-nutrition choice is **ridge_residual_full_100**. Persistence was eligible to win either comparison.

MAE is the average size of an error, in the same units as glucose. The ±10 rate counts individual readings close to the recorded value. A whole-curve pass requires all 24 predictions for a meal to stay within ±10. None of these is an overall classification accuracy percentage. The p95 error means 95% of evaluated point errors are at or below that value; it is not a maximum guarantee.

Model selection uses participant-average full-trajectory MAE, then higher ±10 rate for ties. Each participant has equal weight. Tail errors are pooled across matched points. All candidate selection used UOM validation; external predictions were computed only after writing the immutable selection artifact.

## Data and exclusions

The original 927-event M2 manifest and validation/test artifacts remain read-only. The previously inspected original test is diagnostic in this study. Calibration uses the final 20% of each participant's original development time interval, with target-boundary purging. Longer-history survivors retain original split assignments.

| History | Training | Calibration | Validation | Old test, diagnostic |
|---|---:|---:|---:|---:|
| 2 h | 432 | 101 | 177 | 211 |
| 6 h | 391 | 93 | 162 | 183 |
| 12 h | 360 | 85 | 147 | 157 |
| 24 h | 306 | 80 | 130 | 135 |

Longer histories lose meals with insufficient/gapped CGM. These meals were not removed after seeing prediction errors. Future meals/CGM/insulin are unavailable to every model request. No glucose clipping or hard-case deletion was used.

## Frozen Chronos history comparison

All-history eligibility: **130 events**; common successful validation: **129 events**. One 24-hour request failed the forecast contract. Failures stay in attempted yields; metrics use common successes. The implemented ranking admits failure-free candidates only. Six hours also has the lowest matched MAE irrespective of that eligibility rule.

| Model | MAE mg/dL | Points within ±10 | Whole curves within ±10 | Point p95 error | Point p99 error | Worst error | Failures |
|---|---:|---:|---:|---:|---:|---:|---:|
| chronos_12h | 38.511 | 26.73% | 1.76% | 106.31 | 148.38 | 241.57 | 0 |
| chronos_24h | 37.765 | 25.57% | 0.00% | 102.57 | 131.26 | 240.77 | 1 |
| chronos_2h | 43.035 | 24.20% | 0.69% | 120.27 | 186.56 | 279.58 | 0 |
| chronos_6h | 37.489 | 26.76% | 0.00% | 101.40 | 148.54 | 244.38 | 0 |
| persistence | 42.724 | 19.00% | 0.69% | 113.51 | 166.18 | 242.89 | 0 |

Available-event sensitivity (different survivor sets; unsuitable for a direct ranking):

| History | Available events | MAE mg/dL | Points within ±10 |
|---|---:|---:|---:|
| chronos_12h | 147 | 40.216 | 24.06% |
| chronos_24h | 130 | 37.765 | 25.57% |
| chronos_2h | 177 | 47.151 | 16.78% |
| chronos_6h | 162 | 40.343 | 19.95% |

## Small-model and residual validation

Selected-history cohort: 391 training, 93 separate calibration, 162 validation meals. Validation was used to choose candidates across 10 participants, so selected validation improvements are optimistic. Full-nutrient and shared residual heads are separate selections; additional nutrient features did not improve the best validation MAE over the shared head. This is not a controlled causal nutrient ablation.

Ridge alphas 1/10/100; LightGBM leaves 7/15, 150 trees, learning rate .03, min_child_samples 20. Standardization and patient-equal fitting weights use training only. Direct models predict change from the latest glucose; residual models correct a frozen CGM-only Chronos forecast. The foundation model was never trained. Shared features use CGM, local clock, recorded bolus and current/earlier carbohydrates. Full features additionally use recorded protein/fat/fibre. Basal values are omitted because their units are ambiguous. No participant ID or invented insulin-action estimate is used.

| Model | MAE mg/dL | Points within ±10 | Whole curves within ±10 | Point p95 error | Point p99 error | Worst error | Failures |
|---|---:|---:|---:|---:|---:|---:|---:|
| chronos_c0 | 40.343 | 19.95% | 0.00% | 107.26 | 158.37 | 244.38 | 0 |
| lightgbm_direct_full_15 | 38.392 | 19.60% | 0.00% | 95.60 | 124.70 | 193.09 | 0 |
| lightgbm_direct_full_7 | 38.391 | 21.00% | 0.00% | 96.89 | 126.90 | 194.70 | 0 |
| lightgbm_direct_shared_15 | 38.052 | 20.03% | 0.00% | 94.03 | 128.50 | 206.42 | 0 |
| lightgbm_direct_shared_7 | 38.688 | 19.61% | 0.00% | 96.17 | 125.95 | 214.54 | 0 |
| lightgbm_residual_full_15 | 36.185 | 21.32% | 0.00% | 95.23 | 132.11 | 199.85 | 0 |
| lightgbm_residual_full_7 | 35.978 | 21.15% | 0.00% | 93.16 | 132.78 | 198.54 | 0 |
| lightgbm_residual_shared_15 | 36.687 | 19.73% | 0.00% | 93.73 | 130.26 | 216.39 | 0 |
| lightgbm_residual_shared_7 | 36.510 | 19.62% | 0.00% | 93.61 | 130.70 | 215.09 | 0 |
| persistence | 43.455 | 19.88% | 0.48% | 117.12 | 168.29 | 242.89 | 0 |
| ridge_direct_full_1 | 43.553 | 20.18% | 0.00% | 110.00 | 149.41 | 215.16 | 0 |
| ridge_direct_full_10 | 41.184 | 20.25% | 0.00% | 103.75 | 144.18 | 214.92 | 0 |
| ridge_direct_full_100 | 36.759 | 24.77% | 0.53% | 98.43 | 140.78 | 219.59 | 0 |
| ridge_direct_shared_1 | 41.719 | 20.27% | 0.42% | 107.25 | 145.55 | 228.72 | 0 |
| ridge_direct_shared_10 | 39.782 | 20.29% | 0.00% | 102.34 | 137.76 | 227.00 | 0 |
| ridge_direct_shared_100 | 35.943 | 23.51% | 0.00% | 99.92 | 134.72 | 227.76 | 0 |
| ridge_residual_full_1 | 41.846 | 22.30% | 0.53% | 116.70 | 158.06 | 256.03 | 0 |
| ridge_residual_full_10 | 39.581 | 23.57% | 0.94% | 110.86 | 150.98 | 247.80 | 0 |
| ridge_residual_full_100 | 34.922 | 28.22% | 0.76% | 100.33 | 147.49 | 236.87 | 0 |
| ridge_residual_shared_1 | 40.147 | 22.85% | 0.76% | 108.22 | 158.02 | 259.24 | 0 |
| ridge_residual_shared_10 | 38.290 | 23.71% | 0.42% | 104.34 | 146.52 | 252.70 | 0 |
| ridge_residual_shared_100 | 34.246 | 27.99% | 0.24% | 98.41 | 142.39 | 243.54 | 0 |

| Model | Within ±10 at 30 min | At 60 min | At 120 min | Attempted-point ±10 yield | Attempted-event whole-curve yield |
|---|---:|---:|---:|---:|---:|
| chronos_c0 | 27.66% | 12.68% | 7.34% | 24.92% | 0.00% |
| persistence | 23.67% | 13.43% | 9.47% | 23.89% | 0.62% |
| ridge_residual_full_100 | 21.58% | 24.21% | 21.14% | 26.21% | 1.23% |
| ridge_residual_shared_100 | 17.93% | 24.75% | 21.45% | 25.05% | 0.62% |

Endpoint rates are participant-average. Attempted yields use all requested points/events, with failures counting as unsuccessful, so they have a different weighting from macro rates.

Proposed gate: ≥10% lower MAE than matched persistence, no lower ±10 rate, and no higher pooled p95 error. This is a research improvement gate, not clinical acceptance.

- full: MAE improvement 19.64%; gate **passed**. Paired MAE delta -8.533, participant-bootstrap 95% interval [-12.998, -4.059] mg/dL.
- shared: MAE improvement 21.19%; gate **passed**. Paired MAE delta -9.209, participant-bootstrap 95% interval [-13.933, -4.532] mg/dL.

Bootstrap: 10,000 participant-cluster draws, seed 20261016. These intervals are descriptive and do not adjust for candidate selection.

## Separate calibration

Symmetric horizon-specific bands use held-out calibration absolute residuals and a finite-sample corrected empirical 80% quantile. Calibration changes bands, not point forecasts. Temporal dependence and cohort shift prevent a formal conditional or clinical coverage claim.

| Model | Calibration events | Validation coverage | Mean width mg/dL |
|---|---:|---:|---:|
| chronos_c0 | 93 | 71.39% | 110.33 |
| persistence | 93 | 69.14% | 114.66 |
| ridge_residual_full_100 | 93 | 74.96% | 105.85 |
| ridge_residual_shared_100 | 93 | 75.42% | 103.80 |

## Independent AZT1D test

**2610 eligible meals, 24 participants**. The public V1 archive passed SHA-256 and byte-size checks. Only canonical CGM Records files were loaded; Visual Statistics exports were excluded. Missing detailed nutrients were never treated as observed zero inputs. The shared model was not refitted or retuned on AZT1D. Exact duplicate rows collapse; conflicting same-time glucose values and nonpositive/nonfinite glucose are removed before windowing. Same CGM gap and follow-up-meal rules apply. Total bolus is used once; correction dose is not added again.

| Model | MAE mg/dL | Points within ±10 | Whole curves within ±10 | Point p95 error | Point p99 error | Worst error | Failures |
|---|---:|---:|---:|---:|---:|---:|---:|
| persistence | 33.865 | 26.80% | 0.60% | 97.00 | 141.00 | 257.00 | 0 |
| ridge_residual_shared_100 | 34.874 | 24.98% | 0.23% | 97.97 | 141.53 | 269.45 | 2 |

| Model | Within ±10 at 30 min | At 60 min | At 120 min | Attempted-point ±10 yield | Attempted-event whole-curve yield |
|---|---:|---:|---:|---:|---:|
| persistence | 32.70% | 17.95% | 13.88% | 27.15% | 0.65% |
| ridge_residual_shared_100 | 27.30% | 17.78% | 12.55% | 25.21% | 0.23% |

External MAE improvement: -2.98%; proposed gate **failed**. Paired MAE delta 1.009 mg/dL, 95% participant-bootstrap interval [-0.353, 2.329].

| Exclusion reason | Events |
|---|---:|
| follow_up_meal | 1343 |
| incomplete_history | 185 |
| incomplete_target | 85 |
| missing_insulin_context | 1 |

External coverage using UOM calibration, without external recalibration:

- persistence: 82.31% coverage, 114.66 mg/dL mean width.
- ridge_residual_shared_100: 75.78% coverage, 103.80 mg/dL mean width.

Two external backbone requests returned crossing quantiles and were rejected by the existing forecast contract (ModelInferenceError caused by ForecastValidationError). Both failures reproduced in a separate diagnostic. They remain failed requests; no quantile sorting, output clipping, replacement prediction or test-based retuning was used. Matched accuracy uses 2,608 successes; attempted yields use all 2,610 requests.

Source audit (aggregate):

```json
{
  "CarbSize_missing": 283162,
  "TotalBolusInsulinDelivered_missing": 283162,
  "bolus_events": 10518,
  "carbohydrate_events": 4224,
  "conflicting_glucose_timestamps": 185,
  "duplicate_rows": 5189,
  "glucose_points": 300738,
  "participants": 25,
  "rows": 306712
}
```

No exact rounded aligned history-plus-target trajectories overlapped with the UOM cohort or another eligible external event. This cannot prove the absence of shared people across sources. AZT1D's AID cohort/device modes differ from UOM; mode is not a shared predictor. The schema of one canonical file is labelled CGM/BGM, which remains a source modality limitation. The tested AZT1D set is now consumed: later tuning requires a new untouched test or a declared exploratory analysis.

## Original-result reproduction and large-error audit

Re-ran original Chronos C3 on the 211 diagnostic requests. Matched original successful results: 211; failures: 0. Largest per-event MAE reproduction difference: 0.000000 mg/dL.

Forecast values span -140.82–399.29 mg/dL; recorded targets span 41.44–398.20 mg/dL. Worst point error: 349.11 mg/dL. That event's trajectory MAE is 180.11, recorded range 121.80, forecast range 236.87 mg/dL. This is a numeric/source/forecast audit, not a clinical adjudication of the underlying trace. No outlier was removed.
A negative glucose forecast is physically impossible: this is an observed model failure, not an acceptable glucose estimate. Clipping would conceal it without proving predictive skill. The all-211 legacy macro MAE below differs from the original all-model-matched 208-event MAE (37.920); this is a denominator difference, not a replacement of the original result.

| Model | MAE mg/dL | Points within ±10 | Whole curves within ±10 | Point p95 error | Point p99 error | Worst error | Failures |
|---|---:|---:|---:|---:|---:|---:|---:|
| legacy_chronos_c3 | 38.556 | 24.99% | 0.33% | 111.23 | 182.34 | 349.11 | 0 |

## Reproduction and retained evidence

See `research/README.md` for commands. Private artifacts under `artifacts/evaluation-results/refinement-v1/` include source/package/protocol hashes, immutable selection, model state, all attempted row-level predictions/failure types, calibration residuals and summaries. Never commit those files. Serialized estimators are trusted-local artifacts only; residual models require the pinned C0 backbone to be explicitly reattached. Timing includes original cache misses and study work; cache-hit timings in comparisons are inherited inference measurements, not fresh serving benchmarks.
The post-run integrity check verified every retained result hash, unchanged original artifacts/selection, and exact saved-head reload predictions on all 162 validation events for both heads (maximum difference 0). The protocol hash records the initial execution snapshot; later ledger status/documentation updates do not change its frozen research rules.
The exact executed research sources and initial protocol are retained in an ignored 39-file ZIP and verified against these hashes. Reporting/verification helpers and a guard preventing writes into a frozen run were added afterwards; they do not change the executed prediction code. Use the verification command on this completed run.

Execution: 7.24 minutes, CPU, two Torch threads, Python 3.12.5; package versions: chronos-forecasting 2.3.2, lightgbm 4.6.0, numpy 2.5.3, scikit-learn 1.7.2, torch 2.14.0.

Frozen selection UTC: 2026-10-16T04:16:19.395392+00:00. Original validation SHA-256: `75be5cfce21323cb3bd965c12e7f5a21a9147cdbb02aabe74717c65b6e234401`; original test SHA-256: `ea35be62eb658a0802d2388c8ebc06c552027e32043a655fda9136ab3f2c55f6`.

## Next decision

The local sequence is executed; the external improvement gate failed. Do not promise ±10 or 80% within tolerance or promote this head. The user chose local data first; MetaboNet acquisition/training is deferred. A larger genuinely separate development cohort, retained source/subject provenance, and a new independent test are the next prerequisites for further tuning. Optional LoRA/TCN work is a later experiment, not evidence of improvement. Keep the two-hour target and report shorter horizons separately. M2 live nutrition, physical camera and presentation gates remain separate.
Before more model training, audit event timing/bolus/meal missingness and cohort shifts using development data. Add a larger source-distinct development cohort; keep a new independent cohort untouched. Then predeclare a small temporal/subject-validation study for direct models, a compact glucose-specific network or supported LoRA, with the same persistence and failure controls. No particular architecture can be promised to reach ±10.

AZT1D attribution: Saman Khamesian, Asiful Arefeen, Bithika M. Thompson, Adela Grando and Hassan Ghasemzadeh (2025), V1, DOI 10.17632/gk9m674wcx.1, CC BY 4.0.

Sources: [AZT1D V1 and CC BY 4.0 licence](https://data.mendeley.com/datasets/gk9m674wcx/1), [Ridge documentation](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html), [LightGBM API](https://lightgbm.readthedocs.io/en/stable/Python-API.html).
