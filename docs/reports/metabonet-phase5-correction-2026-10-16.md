# MetaboNet Phase 5 frozen-Chronos correction results - October 16, 2026

**Phase 5 is complete. Small correction heads and matched direct controls were trained; foundation weights remained frozen. Calibration and reserved test outcomes were not accessed. No application model was replaced.**

Lowest-MAE failure-free validation option: **ridge_residual_1000** (31.14 mg/dL). Candidate retained for the later final comparison: **lightgbm_direct**. No correction passed the predeclared incremental gate; retain the Phase 4 incumbent.

The lowest point estimate and the advancement decision are different rules fixed before fitting. Passing a development gate is not independent or clinical confirmation, and a small improvement does not establish dependable +/-10 forecasts.

## Frozen design and actual training population

The backbone is the pinned six-hour recorded-context C2 Chronos model, the best failure-free Chronos variant from Phase 3. Its immutable request contains only origin-known glucose, separate basal/bolus amounts, previous/current carbs and presence masks. No merged total-insulin double counting. Checkpoint files and source/configuration hashes were frozen before calls and verified unchanged.

Training backbone attempts: **6,756**; successes **6,756**. Failure types: `{}`; underlying causes `{}`. Every attempt was persisted and failed forecasts were not retried or repaired. Raw failed quantiles were not retained, so cause types do not identify individual invalid values.

The original common pool was **6,756 meals / 196 identities**; usable head/control training was **6,756 meals / 196 identities**. Backbone failures excluded **0 training meals** because their residual labels cannot be defined, not because of observed errors. All four final models use exactly the same usable events. Original Phase 4 models used 6,794 meals; matched controls isolate that change.

Source counts: Loop: 3,542, ReplaceBG: 3,214.

The same three whole-subject folds from Phase 4 are used. Fit-fold participant weights give each identity equal total weight. Transformations use fit-fold data only. Horizon expansion occurs after splitting. No source, identity or absolute-time predictor. Validation is read only after training-CV choices and final model bundles are frozen; no validation early stopping or new history search.

Correction heads add 24 frozen C2 median changes to the original 127 request features (24-hour glucose / six-hour recorded events). These future predictions are not future observations. Ridge fits 24 residual outputs with median imputation/weighted scaling; LightGBM fits pooled horizons with the unchanged 160-tree/.04-rate/min-child100/max-bin63/lambda1/two-thread budget. Head weights are saved without a live Chronos model. Corrected quantiles are deterministic placeholders, not the uncorrected native bands.

## Training-only cross-validation and refits

Four correction candidates (two parameters per family), plus two fixed Phase 4 direct controls, each have three subject folds. Select one correction per family by OOF macro MAE, tie higher within-10 then stable name. Failed candidates cannot win. Controls are not retuned. Refit the same usable pool.

| Candidate | OOF macro MAE | OOF within +/-10 | Failed folds |
|---|---:|---:|---:|
| ridge_residual_10 | 31.41 | 28.40% | 0 |
| ridge_residual_1000 | 31.04 | 28.48% | 0 |
| lightgbm_residual_15 | 31.66 | 25.82% | 0 |
| lightgbm_residual_31 | 31.55 | 26.38% | 0 |
| ridge_control | 31.02 | 28.52% | 0 |
| lightgbm_control | 30.94 | 27.46% | 0 |

| Final model | Training meals | Identities | Origin features | Reload equivalent |
|---|---:|---:|---:|---|
| lightgbm_control | 6,756 | 196 | 127 | True |
| lightgbm_residual_31 | 6,756 | 196 | 151 | True |
| ridge_control | 6,756 | 196 | 127 | True |
| ridge_residual_1000 | 6,756 | 196 | 151 | True |

## Primary validation: same 1,509 meals / 48 identities

Feature counts above describe origin inputs; pooled LightGBM adds one horizon-fraction column after the subject split.

Seven original Phase 3 runs, two original Phase 4 direct models, two chosen corrections and two matched controls are compared. Cached C2 predictions were reused only after request/identity/target checks; no validation Chronos calls were repeated. Failure-free selection uses all 1,509 events. The all-history intersection excludes 621 otherwise two-hour-eligible validation meals; this remains a retrospectively isolated logged-meal task, not every live meal.

Macro metrics weight participants equally. Tails pool individual point errors. No clipping, silent native-band repair or outcome-based exclusions.

| Eligible option | Macro MAE mg/dL | Within +/-10 | Pooled p95 | Pooled maximum |
|---|---:|---:|---:|---:|
| ridge_residual_1000 | 31.14 | 29.12% | 90.53 | 230.26 |
| lightgbm_direct | 31.17 | 26.84% | 91.16 | 235.38 |
| lightgbm_control | 31.25 | 26.60% | 90.84 | 243.75 |
| ridge_control | 31.30 | 28.72% | 90.98 | 230.15 |
| ridge_direct | 31.36 | 28.85% | 91.18 | 229.53 |
| lightgbm_residual_31 | 31.75 | 25.95% | 92.00 | 265.22 |
| persistence | 37.12 | 25.47% | 111.00 | 259.50 |
| chronos_c2_6h | 37.61 | 25.98% | 113.33 | 364.72 |
| chronos_c0_2h | 42.52 | 23.52% | 126.91 | 473.69 |

## Incremental correction decision

Predeclared correction gate versus original Phase 4 LightGBM: at least 5% lower macro MAE, no lower within-10, no worse pooled p95, and zero failed validation attempts. This guards against advancing a more expensive model for a tiny selected point-estimate gain. It does not prove external benefit.

| Correction | MAE improvement versus incumbent | Gate |
|---|---:|---|
| lightgbm_residual_31 | -1.85% | FAIL |
| ridge_residual_1000 | 0.10% | FAIL |

The best eligible option's overall persistence-improvement gate passes (16.11% lower MAE; also requires nondecreasing within-10 and nonincreasing p95). This overall gate is separate from correction benefit over the stronger incumbent.

Participant-cluster bootstrap, 10,000 draws/seed20261016: differences are correction minus comparator; negative favours correction. Intervals are descriptive after reused-validation selection, without multiplicity correction or independent significance claims.

| Correction | Comparator | Delta MAE | Descriptive 95% interval |
|---|---|---:|---|
| lightgbm_residual_31 | lightgbm_control | 0.50 | [0.08, 0.89] |
| lightgbm_residual_31 | lightgbm_direct | 0.58 | [0.21, 0.93] |
| ridge_residual_1000 | lightgbm_direct | -0.03 | [-0.48, 0.43] |
| ridge_residual_1000 | ridge_control | -0.16 | [-0.31, -0.01] |

## Failure accounting, horizons and tolerance

Pairwise-success scores have distinct populations; all-attempt yields retain failed cases. These rows do not replace full-cohort ranking.

| Option | Attempts | Failures | Paired successes | Paired macro MAE | Attempted-point within-10 yield | Negative predictions |
|---|---:|---:|---:|---:|---:|---:|
| chronos_c0_12h | 1509 | 11 | 1498 | 34.73 | 27.43% | 8 |
| chronos_c0_24h | 1509 | 15 | 1494 | 33.54 | 27.81% | 0 |
| chronos_c0_2h | 1509 | 0 | 1509 | 42.52 | 23.56% | 259 |
| chronos_c0_6h | 1509 | 2 | 1507 | 37.13 | 26.21% | 10 |
| chronos_c1_6h | 1509 | 1 | 1508 | 37.77 | 26.21% | 42 |
| chronos_c2_6h | 1509 | 0 | 1509 | 37.61 | 26.20% | 38 |
| lightgbm_control | 1509 | 0 | 1509 | 31.25 | 26.68% | 0 |
| lightgbm_direct | 1509 | 0 | 1509 | 31.17 | 26.79% | 0 |
| lightgbm_residual_31 | 1509 | 0 | 1509 | 31.75 | 26.19% | 0 |
| persistence | 1509 | 0 | 1509 | 37.12 | 25.83% | 0 |
| ridge_control | 1509 | 0 | 1509 | 31.30 | 27.88% | 0 |
| ridge_direct | 1509 | 0 | 1509 | 31.36 | 28.01% | 0 |
| ridge_residual_1000 | 1509 | 0 | 1509 | 31.14 | 28.23% | 0 |

Endpoint and whole-curve metrics for full-cohort eligible options:

| Option | 30 min MAE | 60 min MAE | 120 min MAE | Whole curve within +/-10 | Pooled p99 |
|---|---:|---:|---:|---:|---:|
| chronos_c0_2h | 27.78 | 46.59 | 61.57 | 0.78% | 190.42 |
| chronos_c2_6h | 25.01 | 42.39 | 52.22 | 1.10% | 168.18 |
| lightgbm_control | 20.70 | 34.17 | 44.94 | 0.62% | 135.40 |
| lightgbm_direct | 20.71 | 34.10 | 44.92 | 0.52% | 134.82 |
| lightgbm_residual_31 | 21.38 | 34.72 | 45.22 | 0.22% | 137.94 |
| persistence | 25.33 | 40.86 | 52.62 | 1.44% | 165.00 |
| ridge_control | 20.99 | 34.37 | 45.32 | 0.65% | 137.63 |
| ridge_direct | 20.94 | 34.46 | 45.44 | 0.76% | 137.93 |
| ridge_residual_1000 | 20.71 | 34.15 | 44.91 | 0.52% | 136.02 |

## Conditional common-success and source diagnostics

All 13 options succeeded on **1,487 meals**. This conditional subset excludes failures and is secondary.

| Option | Common-success macro MAE | Within +/-10 |
|---|---:|---:|
| chronos_c0_12h | 34.60 | 27.60% |
| chronos_c0_24h | 33.50 | 27.97% |
| chronos_c0_2h | 42.34 | 23.60% |
| chronos_c0_6h | 36.94 | 25.90% |
| chronos_c1_6h | 37.67 | 26.15% |
| chronos_c2_6h | 37.51 | 26.09% |
| lightgbm_control | 31.24 | 26.54% |
| lightgbm_direct | 31.17 | 26.75% |
| lightgbm_residual_31 | 31.74 | 25.90% |
| persistence | 36.84 | 25.58% |
| ridge_control | 31.32 | 28.66% |
| ridge_direct | 31.37 | 28.79% |
| ridge_residual_1000 | 31.16 | 29.08% |

Subgroups use all-option common-success meals within each source. They are descriptive, not a causal study effect or external validation.

| Source | Common meals | Option | Macro MAE | Within +/-10 |
|---|---:|---|---:|---:|
| Loop | 838 | persistence | 37.87 | 24.44% |
| Loop | 838 | lightgbm_direct | 29.69 | 28.69% |
| Loop | 838 | ridge_direct | 29.92 | 30.81% |
| Loop | 838 | lightgbm_control | 29.76 | 28.26% |
| Loop | 838 | lightgbm_residual_31 | 30.24 | 27.74% |
| Loop | 838 | ridge_control | 29.92 | 30.71% |
| Loop | 838 | ridge_residual_1000 | 29.70 | 30.96% |
| ReplaceBG | 649 | persistence | 35.73 | 26.81% |
| ReplaceBG | 649 | lightgbm_direct | 32.77 | 24.65% |
| ReplaceBG | 649 | ridge_direct | 32.95 | 26.59% |
| ReplaceBG | 649 | lightgbm_control | 32.85 | 24.67% |
| ReplaceBG | 649 | lightgbm_residual_31 | 33.37 | 23.90% |
| ReplaceBG | 649 | ridge_control | 32.84 | 26.44% |
| ReplaceBG | 649 | ridge_residual_1000 | 32.75 | 27.03% |

## Critical interpretation and next phase

The Ridge correction lowers MAE by only 0.03 mg/dL versus original LightGBM (0.10%); its descriptive delta interval [-0.48,0.43] includes no improvement. Within-10 rises from 26.84% to 29.12%, but that is only 0.27 percentage points above the cheaper original Ridge direct model's 28.85%. LightGBM correction worsens MAE to 31.75 and within-10 to 25.95%. These corrections substantially improve the frozen C2 backbone itself (37.61 MAE), but add little or no value beyond the already trained direct models. Retaining the direct incumbent is the predeclared decision, not a claim that it wins every tolerance metric.

The retained option has macro MAE **31.17 mg/dL**, within +/-10 **26.84%**, whole-curve within-10 **0.52%**, maximum error **235.38 mg/dL**. Average error and within-10 percentages are different objectives. A point percentage is not classification accuracy, interval coverage or an entire-curve guarantee. The +/-10 aspiration remains unmet; accuracy is still weak for that goal.

Matched controls remove the training-population difference. The correction adds forecast features and changes the target to a residual, so this comparison does not isolate those two mechanisms individually. The four fixed correction configurations do not exhaust possible models, training budgets or representations. A negative gate is evidence about this bounded design, not proof that all Chronos correction is impossible. A positive gate remains selected development evidence requiring reserved testing.

No protein/fat/fibre or physiological IOB/COB was invented. Recorded context cannot recover missing meals, delivery or unknown latency/upstream processing. Source-qualified identities are not proof of globally independent people. Performance on other studies or earlier UOM/AZT1D cohorts is not a paired before/after improvement. The previously consumed AZT1D set is not untouched.

Next is Phase 6: freeze the final candidate set and separate calibration/test protocol, calibrate intervals on reserved development calibration data, then score the 104 primary-test and 65 PEDAP source-test identity reservations once. Eligible test-event counts are not yet known. Report all failures, tails, subgroups and uncertainty. No further tuning on test outcomes, app promotion or clinical guarantee follows from these scores.

## Reproduction, runtime and verification

```powershell
uv run --no-sync python -m research.pipelines.cache_metabonet_backbone
uv run --no-sync python -m research.pipelines.run_metabonet_correction
uv run --no-sync python -m research.pipelines.run_metabonet_correction --verify-only
uv run --no-sync python -m research.pipelines.report_metabonet_correction
```

Completed stages refuse replay. Matching interrupted stages reuse intact checksummed work; failures are never retried. Distinct backbone/head source snapshots, cohort/folds, checkpoint/input hashes, OOF arrays, fitted heads, predictions and completion manifests remain under ignored local artifacts. No raw health rows, identities, timestamps, weights or secrets enter this report.

Python 3.12.5; head packages: duckdb 1.4.4, joblib 1.6.0, lightgbm 4.6.0, numpy 2.5.3, scikit-learn 1.7.2.
Backbone stage runtime **41.20 minutes**; head CV/refit/validation/summary **1.99 minutes**. The requested CPU limit was two threads. A separate import-order audit found late-loaded SciPy/OpenMP libraries could retain 16 threads despite that request; strict two-thread enforcement was not established for the heads. These measurements exclude preflight/loading and do not predict later-phase effort.

Training-backbone call wall time: median **325.67 ms**, p95 **538.97 ms**. Includes adapter predict but excludes request construction. A correction still needs this backbone work at inference; a direct model does not.

| Model | Head-only batch prediction, 1,509 meals |
|---|---:|
| lightgbm_control | 70.72 ms |
| lightgbm_residual_31 | 76.35 ms |
| ridge_control | 2.41 ms |
| ridge_residual_1000 | 3.66 ms |

Head batch timings exclude feature extraction/backbone generation and are not per-request latency. Zero row timing placeholders are excluded from latency claims. Do not compare them directly with Chronos call p95.

See [protocol 15](../planning/GlycoLens_15_MetaboNet_Chronos_Correction.md) and [verification handoff](../tooling/metabonet-phase5-handoff-2026-10-16.md).

## Launcher interruption and resource-limit audit

The first head-stage PowerShell launcher treated a retained numerical RuntimeWarning as a terminating native-command error. It stopped during the first CV candidate before any completed CV candidate or validation row was saved. The launcher was corrected to retain stderr warnings in the log and honor the Python exit code; the unchanged frozen model sources/configuration resumed. The incomplete candidate was recomputed; no completed candidate, failed prediction or validation result was retried to improve a score. Original interrupted logs and an audit JSON were retained.

The head runtime above is the resumed completion attempt, not cumulative CPU time including interrupted partial folds. An isolated reproduction of the runner import order found NumPy BLAS limited to 2 threads but late-loaded SciPy BLAS/OpenMP at 16. These are requested resource settings, not proof every library was limited to two threads. Future runners should import estimator libraries before applying limits. No model settings or features changed during this run; accuracy was independently reproduced.
