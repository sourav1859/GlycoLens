# Milestone 2 model comparison and context ablation

Generated October 14, 2026 from pinned local T1D-UOM V1.0.4 artifacts.
Research estimates only; no clinical validity or dosing use. The application selection
was frozen as Chronos-2 C3 on validation before held-out test execution.

## Protocol

927 windows; per-participant temporal time cuts 60/20/20, crossing targets purged.
536 development, 177 validation, 211 test, three purged. Twelve of fifteen
participants have both validation and test events. Subject-disjoint definitions
are implemented but a subject-disjoint benchmark has not yet been run.
The same requested events enter every model/context; tables use the intersection
of successful events. Failures are not removed from the denominator. Representation:
recorded_events_v1 (ADR 0008). No weights are trained or calibrated.

## Validation

Requested 177 events; 171 common successful events.

| Model/context | Failed | Participant macro MAE (mg/dL) | Event MAE | Event RMSE | Coverage q10-q90 | Width | Wall p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| chronos2:cgm_insulin | 6 | 47.573 | 46.003 | 53.392 | 0.468 | 130.232 | 88.09 |
| chronos2:cgm_insulin_carbohydrates | 6 | 45.707 | 43.729 | 50.813 | 0.459 | 83.461 | 86.63 |
| chronos2:cgm_insulin_nutrition | 6 | 44.088 | 42.291 | 49.167 | 0.458 | 70.696 | 89.97 |
| chronos2:cgm_only | 0 | 47.243 | 45.160 | 52.340 | 0.411 | 71.330 | 63.86 |
| persistence:cgm_insulin | 6 | 44.080 | 41.555 | 47.855 | N/A | N/A | 0.24 |
| persistence:cgm_insulin_carbohydrates | 6 | 44.080 | 41.555 | 47.855 | N/A | N/A | 0.25 |
| persistence:cgm_insulin_nutrition | 6 | 44.080 | 41.555 | 47.855 | N/A | N/A | 0.25 |
| persistence:cgm_only | 0 | 44.080 | 41.555 | 47.855 | N/A | N/A | 0.25 |
| timesfm3:cgm_insulin | 6 | 55.216 | 52.422 | 60.741 | 0.419 | 73.794 | 300.84 |
| timesfm3:cgm_insulin_carbohydrates | 6 | 54.950 | 52.419 | 60.663 | 0.430 | 74.807 | 306.96 |
| timesfm3:cgm_insulin_nutrition | 6 | 54.485 | 52.569 | 60.794 | 0.426 | 73.036 | 386.92 |
| timesfm3:cgm_only | 0 | 55.491 | 52.956 | 61.488 | 0.390 | 69.640 | 246.67 |

Selected Chronos C3 minus persistence, paired participant-average MAE:
0.008 mg/dL; bootstrap 95% interval
[-2.160, 2.318],
12 participants / 171 matched events.
This interval uses the pairwise successful set, which can differ from the all-run table intersection.
Negative differences favor Chronos. Participant resampling uses seed 20261014,
2,000 draws; small-cohort intervals are descriptive, not clinical evidence.

## Test

Requested 211 events; 208 common successful events.

| Model/context | Failed | Participant macro MAE (mg/dL) | Event MAE | Event RMSE | Coverage q10-q90 | Width | Wall p95 ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| chronos2:cgm_insulin | 0 | 39.301 | 39.140 | 45.290 | 0.532 | 81.805 | 78.36 |
| chronos2:cgm_insulin_carbohydrates | 0 | 38.539 | 38.498 | 44.761 | 0.535 | 77.212 | 101.83 |
| chronos2:cgm_insulin_nutrition | 0 | 37.920 | 37.923 | 44.154 | 0.539 | 74.838 | 100.19 |
| chronos2:cgm_only | 0 | 39.348 | 38.234 | 44.401 | 0.516 | 69.373 | 49.43 |
| persistence:cgm_insulin | 0 | 33.957 | 33.533 | 38.776 | N/A | N/A | 0.26 |
| persistence:cgm_insulin_carbohydrates | 0 | 33.957 | 33.533 | 38.776 | N/A | N/A | 0.26 |
| persistence:cgm_insulin_nutrition | 0 | 33.957 | 33.533 | 38.776 | N/A | N/A | 0.27 |
| persistence:cgm_only | 0 | 33.957 | 33.533 | 38.776 | N/A | N/A | 0.15 |
| timesfm3:cgm_insulin | 1 | 39.903 | 42.127 | 48.958 | 0.480 | 75.627 | 345.64 |
| timesfm3:cgm_insulin_carbohydrates | 1 | 38.488 | 41.722 | 48.577 | 0.517 | 79.767 | 287.32 |
| timesfm3:cgm_insulin_nutrition | 1 | 38.269 | 42.235 | 49.088 | 0.504 | 76.673 | 337.25 |
| timesfm3:cgm_only | 1 | 41.858 | 42.936 | 49.975 | 0.449 | 69.471 | 237.95 |

Selected Chronos C3 minus persistence, paired participant-average MAE:
4.197 mg/dL; bootstrap 95% interval
[1.894, 6.884],
15 participants / 211 matched events.
This interval uses the pairwise successful set, which can differ from the all-run table intersection.
Negative differences favor Chronos. Participant resampling uses seed 20261014,
2,000 draws; small-cohort intervals are descriptive, not clinical evidence.

## Interpretation and limitations

Chronos C3 was the strongest pretrained validation configuration and practical CPU choice.
It did not beat persistence on validation participant-average MAE; input support alone
does not prove meal-aware benefit. Held-out results above must be assessed without reselection.
Filtering retains approximately 24% of loaded meal events. Self-report quality, unknown
source timezone/DST, sparse/missing insulin logs and ambiguous basal source units limit transfer.
Conflicting same-time basal observations fail closed and appear in failure counts.
Recorded-event masks and raw-kind descriptors are not insulin-on-board or physiological models.
Mean event RMSE is the average of per-event RMSE, not a globally pooled RMSE.
Persistence has no calibrated interval. Coverage/width and pinball metrics are available;
exact CRPS is not inferred from only three quantiles. RSS is post-run process RSS, not peak
memory; wall percentiles include adapter conversion/scoring and use the actual event samples.
Live nutrition and recipe-provider checks remain prerequisites until API configuration exists.

## Reproduction

Use the locked optional Chronos/TimesFM groups. Build the ignored manifest, run the
full validation benchmark, freeze the explicit selection, then run the test benchmark
with --frozen-selection. Run `python -m research.pipelines.report_m2_results` to
export these aggregates. Raw event rows, timestamps and IDs stay ignored.
