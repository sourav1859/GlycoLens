# MetaboNet Phase 6 independent evaluation — October 16, 2026

Phase 6 is complete. The primary research candidate was frozen as original Phase 4 LightGBM before calibration or reserved outcomes. Original Ridge is a diagnostic challenger; persistence is the baseline. No test-based reselection, point-model refitting, Chronos calls, clipping, app switch or clinical validation occurred.

**Average error improved, but tight precision remains poor.** LightGBM's primary trajectory MAE is 29.91 mg/dL, with 28.20% of points within +/-10. PEDAP MAE is 40.92, within-10 19.57%. The nominal 80% marginal band covers 79.05% on the primary cohort but only 63.94% on PEDAP. The average-error gate is confirmed; broad pediatric reliability is not.

## Calibration and execution

There were 1,488 eligible 24-hour calibration meals. One hash-selected meal per participant supplied 48 source-qualified participant representatives; actual independence/exchangeability is unverified. The 80% finite-sample rule uses order statistic 40 out of 48, separately per horizon and for maximum whole-curve error. These are empirical symmetric bands; their q10/q90 labels are not learned conditional quantiles. Calibration does not improve point accuracy.

| Predictor | Marginal radius 30 min | 60 min | 120 min | Whole-curve radius |
|---|---:|---:|---:|---:|
| persistence | 33.00 | 71.00 | 88.00 | 94.00 |
| lightgbm_direct | 27.24 | 56.88 | 64.05 | 80.35 |
| ridge_direct | 24.74 | 53.02 | 64.86 | 75.17 |

Radii and all errors below are mg/dL. Both bands were frozen in a verified calibration completion before raw reserved CGM/event projection. All four loaded numerical pools reported two threads. Point-model state and original bundles were unchanged. Sources, configurations, original inputs, rows and artifacts are checksummed in separate execution snapshots.

## Reserved-cohort eligibility

All 169 reserved identities were screened. Candidate origins were hash-selected before eligibility, at most 100 per participant across permitted file segments. PEDAP histories/targets were never borrowed across publisher-file boundaries. The unchanged isolated-meal rule examines later meal entries retrospectively; these scores do not represent every live meal.

| Cohort | Reserved IDs | Eligible IDs | Candidate origins | Eligible meals |
|---|---:|---:|---:|---:|
| primary_test | 104 | 102 | 10,180 | 3,533 |
| source_test | 65 | 64 | 6,332 | 2,177 |

Partial exact fingerprint screening: 1,474,695 distinct development reference sequences and 2,519,890 distinct sequences overall. 0 reserved IDs were quarantined; 0 development references were flagged. These rounded, hourly-endpoint checks cannot prove global person uniqueness or absence of foundation pretraining overlap.

## Primary: unseen Loop/ReplaceBG identities

Preparation statuses: `{"ready": 104}`. Rejections among ready subjects: `{"clustered_meal": 643, "follow_up_meal": 3311, "incomplete_history": 2357, "incomplete_target": 336}`.

Primary accuracy averages each participant's meal-level metrics equally. Tail errors pool all successful CGM points. All models attempt identical eligible events; failures remain in attempted-event yields. Common-success summaries are diagnostic and do not replace per-model denominators.

| Predictor | MAE | RMSE | Within +/-10 | Whole curve within +/-10 | Pooled p95 | Max | Failed |
|---|---:|---:|---:|---:|---:|---:|---:|
| persistence | 36.81 | 42.32 | 25.96% | 1.08% | 110.00 | 307.00 | 0 |
| lightgbm_direct | 29.91 | 34.68 | 28.20% | 0.94% | 86.42 | 264.87 | 0 |
| ridge_direct | 30.31 | 35.31 | 28.94% | 1.01% | 85.99 | 263.21 | 0 |

Frozen LightGBM confirmation gate **passed**: MAE improvement 18.74%. The rule requires at least 10% lower MAE, within-10 nondecrease, pooled p95 nonincrease and no failed forecasts. LightGBM-minus-persistence macro MAE difference -6.90, descriptive participant-bootstrap 95% interval [-7.94, -5.87] (10,000 draws, seed20261016). No model is selected again using these test scores.

| Predictor | MAE at 30 min | 60 min | 120 min | Within-10 at 120 min | Attempted whole-curve yield |
|---|---:|---:|---:|---:|---:|
| persistence | 25.45 | 42.28 | 50.41 | 13.44% | 1.19% |
| lightgbm_direct | 20.94 | 34.26 | 40.90 | 16.06% | 1.08% |
| ridge_direct | 21.11 | 35.04 | 41.27 | 16.58% | 1.13% |

| Predictor | Marginal point coverage | Marginal whole-curve coverage | Mean marginal width | Curve-band whole-curve coverage | Curve-band width | Negative marginal lower points |
|---|---:|---:|---:|---:|---:|---:|
| persistence | 80.30% | 49.33% | 122.58 | 78.91% | 188.00 | 6,992 |
| lightgbm_direct | 79.05% | 34.21% | 96.73 | 80.57% | 160.70 | 0 |
| ridge_direct | 76.16% | 34.84% | 91.68 | 76.75% | 150.33 | 0 |

Coverage above is participant-macro. Marginal 80% targets individual time points, while the separate curve band targets the complete 24-point trajectory. Broad bands can cover well while point forecasts remain inaccurate. Coverage under study shift is empirical, with no pediatric or individual guarantee.

| Predictor | Marginal coverage 30 min | 60 min | 120 min | Lowest horizon coverage |
|---|---:|---:|---:|---:|
| persistence | 72.22% | 82.43% | 83.64% | 71.44% |
| lightgbm_direct | 71.75% | 82.22% | 80.05% | 70.18% |
| ridge_direct | 66.92% | 77.89% | 79.81% | 64.86% |

An overall coverage average can hide poorly covered horizons. The primary cohort's near-80% average does not establish 80% coverage at every horizon.

| Predeclared subgroup | Meals | IDs with primary success | LightGBM MAE | Within +/-10 | Marginal point coverage |
|---|---:|---:|---:|---:|---:|
| carbs:30to60 | 1,424 | 96 | 33.40 | 25.56% | 74.92% |
| carbs:above60 | 403 | 62 | 35.79 | 25.59% | 72.16% |
| carbs:below30 | 1,706 | 102 | 27.30 | 29.14% | 82.48% |
| insulin_record_masks:at_least90pct | 3,521 | 102 | 29.83 | 28.27% | 79.15% |
| insulin_record_masks:below90pct | 12 | 4 | 29.03 | 18.23% | 75.30% |
| origin_cgm:70to180 | 2,653 | 101 | 29.05 | 28.77% | 80.31% |
| origin_cgm:above180 | 676 | 95 | 35.85 | 25.52% | 71.18% |
| origin_cgm:below70 | 204 | 64 | 26.43 | 25.61% | 82.92% |
| source:Loop | 2,914 | 84 | 29.75 | 28.60% | 79.00% |
| source:ReplaceBG | 619 | 18 | 30.67 | 26.34% | 79.32% |

Participant MAE min / quartile1 / median / quartile3 / max: 15.22 / 24.94 / 29.18 / 33.93 / 52.57. Subgroups may overlap; small groups and incomplete record masks do not establish physiology, logging completeness or causal effects.

## Source shift: pediatric PEDAP

Preparation statuses: `{"ready": 65}`. Rejections among ready subjects: `{"clustered_meal": 357, "follow_up_meal": 2403, "incomplete_history": 1298, "incomplete_target": 97}`.

Primary accuracy averages each participant's meal-level metrics equally. Tail errors pool all successful CGM points. All models attempt identical eligible events; failures remain in attempted-event yields. Common-success summaries are diagnostic and do not replace per-model denominators.

| Predictor | MAE | RMSE | Within +/-10 | Whole curve within +/-10 | Pooled p95 | Max | Failed |
|---|---:|---:|---:|---:|---:|---:|---:|
| persistence | 48.77 | 55.91 | 19.56% | 0.12% | 137.00 | 320.00 | 0 |
| lightgbm_direct | 40.92 | 46.99 | 19.57% | 0.18% | 109.47 | 268.63 | 0 |
| ridge_direct | 41.69 | 48.02 | 21.04% | 0.18% | 112.06 | 276.22 | 0 |

Frozen LightGBM confirmation gate **passed**: MAE improvement 16.10%. The rule requires at least 10% lower MAE, within-10 nondecrease, pooled p95 nonincrease and no failed forecasts. LightGBM-minus-persistence macro MAE difference -7.85, descriptive participant-bootstrap 95% interval [-9.65, -6.24] (10,000 draws, seed20261016). No model is selected again using these test scores.

| Predictor | MAE at 30 min | 60 min | 120 min | Within-10 at 120 min | Attempted whole-curve yield |
|---|---:|---:|---:|---:|---:|
| persistence | 34.82 | 55.49 | 66.17 | 11.26% | 0.09% |
| lightgbm_direct | 32.21 | 47.13 | 52.91 | 11.67% | 0.18% |
| ridge_direct | 32.46 | 48.99 | 52.45 | 12.34% | 0.18% |

| Predictor | Marginal point coverage | Marginal whole-curve coverage | Mean marginal width | Curve-band whole-curve coverage | Curve-band width | Negative marginal lower points |
|---|---:|---:|---:|---:|---:|---:|
| persistence | 67.76% | 23.96% | 122.58 | 62.83% | 188.00 | 1,695 |
| lightgbm_direct | 63.94% | 12.66% | 96.73 | 61.11% | 160.70 | 0 |
| ridge_direct | 59.76% | 12.87% | 91.68 | 54.25% | 150.33 | 0 |

Coverage above is participant-macro. Marginal 80% targets individual time points, while the separate curve band targets the complete 24-point trajectory. Broad bands can cover well while point forecasts remain inaccurate. Coverage under study shift is empirical, with no pediatric or individual guarantee.

| Predictor | Marginal coverage 30 min | 60 min | 120 min | Lowest horizon coverage |
|---|---:|---:|---:|---:|
| persistence | 56.93% | 70.09% | 71.83% | 55.56% |
| lightgbm_direct | 50.32% | 67.64% | 67.14% | 50.25% |
| ridge_direct | 46.94% | 61.10% | 66.94% | 46.70% |

An overall coverage average can hide poorly covered horizons. The primary cohort's near-80% average does not establish 80% coverage at every horizon.

| Predeclared subgroup | Meals | IDs with primary success | LightGBM MAE | Within +/-10 | Marginal point coverage |
|---|---:|---:|---:|---:|---:|
| carbs:30to60 | 790 | 58 | 41.15 | 18.13% | 63.83% |
| carbs:above60 | 54 | 17 | 47.30 | 15.56% | 56.79% |
| carbs:below30 | 1,333 | 64 | 40.22 | 20.13% | 65.10% |
| insulin_record_masks:at_least90pct | 1,181 | 64 | 40.40 | 19.58% | 65.21% |
| insulin_record_masks:below90pct | 996 | 44 | 40.29 | 19.80% | 64.05% |
| origin_cgm:70to180 | 1,508 | 63 | 37.64 | 20.50% | 67.17% |
| origin_cgm:above180 | 624 | 64 | 49.37 | 18.05% | 55.48% |
| origin_cgm:below70 | 45 | 25 | 39.53 | 19.12% | 67.54% |
| source:PEDAP | 2,177 | 64 | 40.92 | 19.57% | 63.94% |

Participant MAE min / quartile1 / median / quartile3 / max: 20.35 / 35.57 / 40.84 / 45.36 / 63.51. Subgroups may overlap; small groups and incomplete record masks do not establish physiology, logging completeness or causal effects.

## Interpretation and next steps

The +/-10 aspiration remains unmet. Neither MAE nor interval coverage is an overall percentage accuracy score. Point errors, whole-curve tolerance, tails and subgroup variation must be considered together. No maximum-error or clinical claim follows from this experiment.

Trajectory MAE averages errors across all 24 future time points; the two-hour endpoint is harder (primary LightGBM MAE 40.90, PEDAP 52.91). Complete-curve within-10 is only 0.94% and 0.18%, respectively. PEDAP's within-10 improvement over persistence is effectively negligible (19.57% versus 19.56%), even though the prespecified nondecrease gate passes. Primary mean marginal width is 96.73 mg/dL; the separate curve band is 160.70 wide. These widths expose uncertainty rather than deliver precise predictions. Only 48 calibration representatives also limit the stability of estimated radii.

Both reserved cohorts are now consumed. Keep this run as confirmation/diagnostic evidence; any new model or feature tuning requires fresh confirmation data. The next research iteration should improve source-appropriate development data, meal/insulin timing and participant adaptation, using development-only grouped validation before another locked evaluation. Application integration and remaining M2 live prerequisites require separate work.

Measured calibration stage 3.35 seconds; test preparation/scoring 217.72 seconds, excluding initial prior-artifact/raw hashing. Logs preserve all warnings. No data upload.

## Reproduction

```powershell
.venv/Scripts/python.exe -m research.pipelines.run_metabonet_independent --stage calibration --verify-only
.venv/Scripts/python.exe -m research.pipelines.run_metabonet_independent --stage test --verify-only
.venv/Scripts/python.exe -m research.pipelines.report_metabonet_independent
```

Original stages used the same commands without `--verify-only`, calibration first. Completed outputs refuse replay. Ignored artifacts: `artifacts/evaluation-results/metabonet-phase6-v1/{calibration,test}/`. The initial protocol is archived in both source ZIPs; later living-document completion notes do not change the execution record.

See [frozen protocol](../planning/GlycoLens_16_MetaboNet_Independent_Evaluation.md), [decision](../decisions/0014-independent-testing-and-participant-calibration.md) and [verification handoff](../tooling/metabonet-phase6-handoff-2026-10-16.md).
