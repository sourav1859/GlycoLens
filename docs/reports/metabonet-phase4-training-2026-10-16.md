# MetaboNet Phase 4 direct-model results - October 16, 2026

**Phase 4 is complete. Small models were trained; Chronos weights stayed frozen. Calibration and reserved test outcomes were not accessed.** These are development validation findings, not independent confirmation or an app model replacement.

Selected failure-free option: **lightgbm_direct**, participant-average MAE **31.17 mg/dL**, within +/-10 **26.84%**. Improvement over persistence: **16.03%**. Predeclared improvement gate: **PASS**.

## Training choices and leakage controls

The common four-history training pool contains **6,756 events / 196 source-qualified identities**. Three source-stratified, stable-hash subject folds keep every identity wholly inside one fold. Participant weights have equal total weight per identity. No participant/source identifier, absolute date or clock time is a predictor.

Histories 2/6/12/24 hours, CGM-only/event profiles and two parameters per family give 32 candidates / 96 fold fits. Rank training out-of-fold participant-average MAE, tie higher within-10 then stable name; failed candidates cannot win. No validation-based early stopping or adaptive search was used. Per-family choices were frozen and refitted before reading prepared validation outcomes.

Ridge jointly predicts 24 glucose deltas from current glucose, with median imputation and weighted scaling fitted only on each training fold/refit. LightGBM fits one pooled-horizon delta regressor, adding horizon fraction and expanding rows only after subject splitting. It is not 24 independent boosters. The fixed tree budget is 160, learning rate 0.04, minimum child size 100, max_bin63, reg_lambda1, seed20261016 and two threads.

Features use current glucose, two-hour relative lags/masks, history summaries and slopes. The selected 24-hour configuration uses 24-hour glucose history; recorded-event summaries cover the preceding six hours. Event profiles add origin-known fractional carbs, separate recorded basal/bolus amounts, prior carbs, presence fractions and mathematical recency summaries. Units remain mg/dL, grams and previous-five-minute IU. Merged insulin total is omitted. Missing event amounts are distinguished from recorded zero; masks cannot recover unlogged meals or delivery. Recency features are not physiological IOB/COB or causal treatment effects.

| History | All eligible training events | Identities |
|---|---:|---:|
| 2 h | 9,540 | 197 |
| 6 h | 8,973 | 197 |
| 12 h | 8,119 | 197 |
| 24 h | 6,794 | 197 |

Training-only CV grid:

| Candidate | OOF macro MAE | OOF within +/-10 | Failed folds |
|---|---:|---:|---:|
| ridge_2h_cgm_10 | 32.26 | 27.25% | 0 |
| ridge_2h_cgm_1000 | 32.17 | 27.47% | 0 |
| ridge_2h_events_10 | 32.22 | 27.69% | 0 |
| ridge_2h_events_1000 | 31.87 | 27.83% | 0 |
| ridge_6h_cgm_10 | 32.16 | 27.45% | 0 |
| ridge_6h_cgm_1000 | 32.03 | 27.56% | 0 |
| ridge_6h_events_10 | 32.19 | 27.68% | 0 |
| ridge_6h_events_1000 | 31.77 | 27.83% | 0 |
| ridge_12h_cgm_10 | 31.88 | 27.72% | 0 |
| ridge_12h_cgm_1000 | 31.74 | 27.71% | 0 |
| ridge_12h_events_10 | 31.94 | 27.95% | 0 |
| ridge_12h_events_1000 | 31.49 | 27.96% | 0 |
| ridge_24h_cgm_10 | 31.35 | 28.58% | 0 |
| ridge_24h_cgm_1000 | 31.21 | 28.51% | 0 |
| ridge_24h_events_10 | 31.41 | 28.35% | 0 |
| ridge_24h_events_1000 | 31.02 | 28.52% | 0 |
| lightgbm_2h_cgm_15 | 32.20 | 26.36% | 0 |
| lightgbm_2h_cgm_31 | 32.29 | 26.53% | 0 |
| lightgbm_2h_events_15 | 31.69 | 26.00% | 0 |
| lightgbm_2h_events_31 | 31.73 | 26.29% | 0 |
| lightgbm_6h_cgm_15 | 32.18 | 26.18% | 0 |
| lightgbm_6h_cgm_31 | 32.21 | 26.56% | 0 |
| lightgbm_6h_events_15 | 31.75 | 25.82% | 0 |
| lightgbm_6h_events_31 | 31.66 | 26.34% | 0 |
| lightgbm_12h_cgm_15 | 31.92 | 26.07% | 0 |
| lightgbm_12h_cgm_31 | 32.00 | 26.28% | 0 |
| lightgbm_12h_events_15 | 31.49 | 26.17% | 0 |
| lightgbm_12h_events_31 | 31.44 | 26.68% | 0 |
| lightgbm_24h_cgm_15 | 31.44 | 26.90% | 0 |
| lightgbm_24h_cgm_31 | 31.49 | 27.47% | 0 |
| lightgbm_24h_events_15 | 30.98 | 26.88% | 0 |
| lightgbm_24h_events_31 | 30.94 | 27.46% | 0 |

Chosen refits (all eligible training events at the selected history):

| Family | Training-CV choice | Refit events | Identities | Features | Reload equivalent |
|---|---|---:|---:|---:|---|
| lightgbm | lightgbm_24h_events_31 | 6,794 | 197 | 127 | True |
| ridge | ridge_24h_events_1000 | 6,794 | 197 | 127 | True |

Refits can include additional training meals outside the common CV pool; the table makes that expansion explicit. All imputation/scaling/model state is frozen before validation. Trusted local bundles are checksummed before resume deserialization; save/reload prediction equivalence was checked.

## Primary validation: same 1,509 meals / 48 identities

Both selected families were compared with the seven verified saved Phase 3 forecasts on exactly equal origins, identities and targets. No Chronos inference was rerun. This cohort has 857 Loop and 652 ReplaceBG meals and excludes 621 otherwise two-hour-eligible validation meals. Five-minute delayed logged-carb availability, retrospective isolated-meal exclusions and causal short filling remain unchanged. These are conditional logged-meal forecasts, not all live meals.

Only failure-free options on the complete cohort enter the primary ranking. Each identity has equal weight in macro metrics. Pooled error tails weight individual points equally. No prediction clipping or error-based exclusion.

| Option | Macro MAE mg/dL | Within +/-10 | Pooled p95 | Pooled maximum |
|---|---:|---:|---:|---:|
| lightgbm_direct | 31.17 | 26.84% | 91.16 | 235.38 |
| ridge_direct | 31.36 | 28.85% | 91.18 | 229.53 |
| persistence | 37.12 | 25.47% | 111.00 | 259.50 |
| chronos_c2_6h | 37.61 | 25.98% | 113.33 | 364.72 |
| chronos_c0_2h | 42.52 | 23.52% | 126.91 | 473.69 |

All attempts, including failure-prone original options:

| Option | Attempts | Failures | Paired successful events | Paired macro MAE | Attempted-point within-10 yield | Negative predictions |
|---|---:|---:|---:|---:|---:|---:|
| chronos_c0_12h | 1509 | 11 | 1498 | 34.73 | 27.43% | 8 |
| chronos_c0_24h | 1509 | 15 | 1494 | 33.54 | 27.81% | 0 |
| chronos_c0_2h | 1509 | 0 | 1509 | 42.52 | 23.56% | 259 |
| chronos_c0_6h | 1509 | 2 | 1507 | 37.13 | 26.21% | 10 |
| chronos_c1_6h | 1509 | 1 | 1508 | 37.77 | 26.21% | 42 |
| chronos_c2_6h | 1509 | 0 | 1509 | 37.61 | 26.20% | 38 |
| lightgbm_direct | 1509 | 0 | 1509 | 31.17 | 26.79% | 0 |
| persistence | 1509 | 0 | 1509 | 37.12 | 25.83% | 0 |
| ridge_direct | 1509 | 0 | 1509 | 31.36 | 28.01% | 0 |

Failed forecasts remain in attempted denominators. Pairwise-success rows can have different populations and do not replace primary selection.

## Horizons, tails and descriptive intervals

Full-cohort eligible options; endpoint errors are participant averages:

| Option | 30 min MAE | 60 min MAE | 120 min MAE | Whole curve within +/-10 | Pooled p99 |
|---|---:|---:|---:|---:|---:|
| chronos_c0_2h | 27.78 | 46.59 | 61.57 | 0.78% | 190.42 |
| chronos_c2_6h | 25.01 | 42.39 | 52.22 | 1.10% | 168.18 |
| lightgbm_direct | 20.71 | 34.10 | 44.92 | 0.52% | 134.82 |
| persistence | 25.33 | 40.86 | 52.62 | 1.44% | 165.00 |
| ridge_direct | 20.94 | 34.46 | 45.44 | 0.76% | 137.93 |

Option-minus-persistence MAE; negative favours the option. Participant-cluster bootstrap uses 10,000 draws and seed20261016. Validation was used for selection, so these are descriptive intervals without multiplicity correction, not independent significance claims.

| Option | Delta MAE mg/dL | Descriptive 95% interval |
|---|---:|---|
| chronos_c0_12h | -2.33 | [-3.47, -1.19] |
| chronos_c0_24h | -3.33 | [-4.55, -2.12] |
| chronos_c0_2h | 5.40 | [3.92, 6.99] |
| chronos_c0_6h | 0.02 | [-1.21, 1.33] |
| chronos_c1_6h | 0.65 | [-0.84, 2.26] |
| chronos_c2_6h | 0.49 | [-0.95, 2.03] |
| lightgbm_direct | -5.95 | [-7.60, -4.33] |
| persistence | 0.00 | [0.00, 0.00] |
| ridge_direct | -5.76 | [-7.45, -4.12] |

## Common-success and source diagnostics

All-nine common-success cohort: **1,487 meals**. This excludes failures and is secondary to full-cohort selection.

| Option | Common-success macro MAE | Within +/-10 |
|---|---:|---:|
| chronos_c0_12h | 34.60 | 27.60% |
| chronos_c0_24h | 33.50 | 27.97% |
| chronos_c0_2h | 42.34 | 23.60% |
| chronos_c0_6h | 36.94 | 25.90% |
| chronos_c1_6h | 37.67 | 26.15% |
| chronos_c2_6h | 37.51 | 26.09% |
| lightgbm_direct | 31.17 | 26.75% |
| persistence | 36.84 | 25.58% |
| ridge_direct | 31.37 | 28.79% |

Source rows use all-nine common-success meals within each source; they are descriptive, not an external test or controlled study effect.

| Source | Common meals | Option | Macro MAE | Within +/-10 |
|---|---:|---|---:|---:|
| Loop | 838 | persistence | 37.87 | 24.44% |
| Loop | 838 | chronos_c2_6h | 36.96 | 25.73% |
| Loop | 838 | ridge_direct | 29.92 | 30.81% |
| Loop | 838 | lightgbm_direct | 29.69 | 28.69% |
| ReplaceBG | 649 | persistence | 35.73 | 26.81% |
| ReplaceBG | 649 | chronos_c2_6h | 38.10 | 26.48% |
| ReplaceBG | 649 | ridge_direct | 32.95 | 26.59% |
| ReplaceBG | 649 | lightgbm_direct | 32.77 | 24.65% |

## Interpretation and next phase

**Blunt assessment: average error improved, but tight-tolerance accuracy is still poor.** The selected model is outside +/-10 for about 73.16% of points under participant averaging. This does not support dependable +/-10 forecasting.

Ridge has higher within-10 than LightGBM despite a slightly higher MAE. LightGBM wins under the predeclared MAE-first rule; it is not best on every metric. Keep Ridge as a tolerance challenger for the later frozen comparison. Both learned models have a lower whole-curve-within-10 rate than persistence. The gate did not require improving whole-curve success, so passing it does not imply that metric improved. Do not change the ranking after seeing scores.

The gate requires at least 10% lower macro MAE than persistence, nondecreasing macro within-10 and nonincreasing pooled p95. A validation pass still requires reserved testing. The selected within-10 rate is a fraction of individual five-minute predictions, not classification accuracy, interval coverage or the probability an entire two-hour curve stays within 10.

The observed selected maximum error is **235.38 mg/dL**. The +/-10 aspiration has not been achieved as a maximum-error guarantee. Training more data or fitting a small model does not guarantee this tolerance. These results do not isolate causal meal/insulin effects or establish global identity independence, complete event logging or clinical safety.

Direct models supply deterministic contract placeholders for quantiles. They have **no calibrated uncertainty interval**, so placeholder coverage is not reported. Phase 3 native Chronos undercoverage is preserved in its report.

Next, Phase 5 compares a small frozen-Chronos correction with the direct winner using training-only choices and the same validation task. Freeze that comparison before Phase 6 interval calibration and one-time reserved primary and PEDAP testing. The 104 primary-test and 65 PEDAP identity reservations remain metadata-only; eligible test-event counts are not yet known. Earlier UOM/AZT1D scores are historical, not paired before/after evidence. No foundation-model fine-tuning or application promotion occurred.

## Reproduction and provenance

```powershell
.venv/Scripts/python.exe -m research.pipelines.run_metabonet_training
.venv/Scripts/python.exe -m research.pipelines.run_metabonet_training --verify-only
.venv/Scripts/python.exe -m research.pipelines.report_metabonet_training
```

The first command refuses completed replay. Matching interrupted work can reuse only intact checksummed CV/model/validation outputs. Execution config, protocol, package versions and sources were archived before fitting; later documentation updates do not rewrite executed source. All IDs, timestamps, windows, predictions, OOF arrays, source ZIPs and trusted model weights remain under ignored local artifacts. This report contains aggregate data only.

Python 3.12.5; packages: duckdb 1.4.4, joblib 1.6.0, lightgbm 4.6.0, numpy 2.5.3, scikit-learn 1.7.2.
Measured wall time from the original execution freeze through completion (including diagnosis/scoring repair when present): 9.26 minutes, CPU two threads. This excludes initial input verification and is not a promise for later phases.

| Direct model | Validation batch prediction time, 1,509 meals |
|---|---:|
| lightgbm | 75.48 ms |
| ridge | 2.33 ms |

Batch timing excludes feature extraction and is not per-request latency. Per-event p95 was not measured; zero row timing placeholders are excluded from aggregate latency claims. Do not compare this batch timing directly with Phase 3 individual Chronos call latency.

See [protocol 14](../planning/GlycoLens_14_MetaboNet_Direct_Models.md) and [verification handoff](../tooling/metabonet-phase4-handoff-2026-10-16.md).

## Scoring interruption and audited completion

The original run completed all 96 CV fits and both final refits, then stopped before its first persisted scored validation row: statistics.mean cannot average NumPy boolean values. A synthetic regression reproduced this failure; converting prediction scalars to native Python floats fixed the metrics/JSON boundary. This was a scoring bug, not a failed fitted model.

The dedicated complete_metabonet_training command verified original CV records, choices, model hashes and source ZIP, and checked that the runner changed only that conversion line. Its own source/configuration snapshot is archived under completion-repair. No CV candidate or model was refitted, no choice/parameter/feature changed, and the original zero-row file was retained as interrupted-validation-ridge.jsonl. Validation was scored again with identical frozen predictions; there was no outcome-based retry or exclusion. The completion manifest covers both execution archives. A completed run still refuses replay.

Ridge CV emitted weighted-scaling RuntimeWarnings during square roots of numerical variances. Every OOF prediction was finite, no fold failed, and the saved scaler/coefficients and predictions were independently checked. The warning is retained in the local log, not silently suppressed.
