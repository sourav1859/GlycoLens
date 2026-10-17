# MetaboNet Phase 3 frozen-inference results - October 16, 2026

**Executed on validation only. No model weights were fitted, no calibration set was consumed and no reserved test values were accessed.** The selected configuration is a development decision, not independent confirmation or an application model replacement.

Best eligible frozen option: **persistence**. Participant-average two-hour trajectory MAE **37.12 mg/dL**. Participant-average within +/-10: **25.47%**. Research improvement gate: **FAIL**.
Best eligible Chronos option: **chronos_c2_6h**, macro MAE **37.61 mg/dL**.

Phase 4 CGM-history choice: **2 hours** (`chronos_c0_2h`; best failure-free C0 validation macro MAE). This is separate from the overall frozen candidate and does not prove the same history is optimal for every small trained model.

## Population and fixed design

There are **1,509 matched meal events** from **48 source-qualified identities**. Every run uses the same event identities, origins and 24 future targets. The matched population is fixed before model output; failed candidates do not shrink the failure-free selection table.

| Available history | Eligible events | Eligible identities |
|---|---:|---:|
| 2 h | 2,130 | 48 |
| 6 h | 2,000 | 48 |
| 12 h | 1,837 | 48 |
| 24 h | 1,514 | 48 |

Matched events by source: Loop: 857, ReplaceBG: 652.
The matched set excludes 621 otherwise two-hour-eligible events because all four histories must qualify. Results therefore do not cover every eligible validation meal; history completeness can change the evaluated population.

Five-minute delayed logged-carb availability is primary. This is the frozen Phase 2 retrospectively isolated logged-meal task, not unrestricted pre-meal forecasting. Missing histories use only the prescribed short causal fill; targets are never imputed or clipped. No zero-delay sensitivity was selected using these scores.

C0 is CGM-only at 2/6/12/24 h. C1 uses the predeclared six-hour history plus recorded bolus/basal IU amounts and source-present masks. C2 additionally uses previous logged carbs and origin-known current carbs. Total insulin is omitted when components are used. No protein/fat/fibre or physiological insulin activity was invented. The unchanged common adapter uses `recorded_events_v1`, including its observation channels. Masks do not recover unlogged intake/delivery or unknown upstream interpolation. This study does not search all history/context combinations.

## Primary selection: complete matched cohort, failure-free options

Rank participant-average MAE, tie higher participant-average within +/-10, then stable name. Each participant has equal weight within these macro metrics. P95/max below pool all absolute point errors. Persistence can win.
Failure-free means the software contract accepted an output; it does not establish physiological plausibility or clinical accuracy. Negative medians remain visible in the native-output table.

| Option | MAE mg/dL | Within +/-10 | Pooled p95 | Pooled maximum |
|---|---:|---:|---:|---:|
| persistence | 37.12 | 25.47% | 111.00 | 259.50 |
| chronos_c2_6h | 37.61 | 25.98% | 113.33 | 364.72 |
| chronos_c0_2h | 42.52 | 23.52% | 126.91 | 473.69 |

## All attempts and failures

The table retains every predeclared option. Its MAE/within-10 are paired with persistence on that option's successful events, so those rows can have different populations and are not the primary ranking. Attempted-point yield counts failed forecasts as unsuccessful, rather than dropping their denominators.

| Option | Attempts | Failed | Paired events | Paired MAE | Within +/-10 | Attempted-point within-10 yield |
|---|---:|---:|---:|---:|---:|---:|
| chronos_c0_12h | 1509 | 11 | 1498 | 34.73 | 27.46% | 27.43% |
| chronos_c0_24h | 1509 | 15 | 1494 | 33.54 | 27.93% | 27.81% |
| chronos_c0_2h | 1509 | 0 | 1509 | 42.52 | 23.52% | 23.56% |
| chronos_c0_6h | 1509 | 2 | 1507 | 37.13 | 25.81% | 26.21% |
| chronos_c1_6h | 1509 | 1 | 1508 | 37.77 | 26.04% | 26.21% |
| chronos_c2_6h | 1509 | 0 | 1509 | 37.61 | 25.98% | 26.20% |
| persistence | 1509 | 0 | 1509 | 37.12 | 25.47% | 25.83% |

All-seven common-success set: **1,487 events**. Failure counts/types are preserved; quantiles were not repaired, predictions were not clipped and failed model outputs were not retried.

## Common-success diagnostic comparison

Every option below is scored on the same all-option common-success subset. This describes accuracy conditional on all outputs being valid; it excludes failure cases and therefore does not replace the full-cohort eligibility rule.

| Option | MAE mg/dL | Within +/-10 | Pooled p95 |
|---|---:|---:|---:|
| chronos_c0_12h | 34.60 | 27.60% | 105.83 |
| chronos_c0_24h | 33.50 | 27.97% | 102.95 |
| chronos_c0_2h | 42.34 | 23.60% | 126.18 |
| chronos_c0_6h | 36.94 | 25.90% | 110.55 |
| chronos_c1_6h | 37.67 | 26.15% | 113.02 |
| chronos_c2_6h | 37.51 | 26.09% | 112.95 |
| persistence | 36.84 | 25.58% | 110.00 |

## Horizons, whole curves and error tails

All-option paired-success diagnostics (each row retains its own successful population; see the failure table):

| Option | 30 min | 60 min | 120 min | Pooled p95 | Pooled p99 | Pooled max |
|---|---:|---:|---:|---:|---:|---:|
| chronos_c0_12h | 22.97 | 39.13 | 49.00 | 106.15 | 156.66 | 277.10 |
| chronos_c0_24h | 22.35 | 38.34 | 46.35 | 103.01 | 149.66 | 249.80 |
| chronos_c0_2h | 27.78 | 46.59 | 61.57 | 126.91 | 190.42 | 473.69 |
| chronos_c0_6h | 24.38 | 41.85 | 52.24 | 111.21 | 164.45 | 302.03 |
| chronos_c1_6h | 25.03 | 42.65 | 52.48 | 113.55 | 168.91 | 383.12 |
| chronos_c2_6h | 25.01 | 42.39 | 52.22 | 113.33 | 168.18 | 364.72 |
| persistence | 25.33 | 40.86 | 52.62 | 111.00 | 165.00 | 259.50 |

The following uses the selected failure-free option on the full matched cohort. Endpoint errors are participant-average absolute error at that horizon. A within-10 point percentage is not classification accuracy or the probability that an entire two-hour curve stays within 10.

| Measure | Selected | Persistence |
|---|---:|---:|
| 30-minute error mg/dL | 25.33 | 25.33 |
| 60-minute error mg/dL | 40.86 | 40.86 |
| 120-minute error mg/dL | 52.62 | 52.62 |
| Whole curve within +/-10, participant-average | 1.44% | 1.44% |
| Pooled p99 absolute error mg/dL | 165.00 | 165.00 |
| Pooled max absolute error mg/dL | 259.50 | 259.50 |

## Paired uncertainty and native forecast bands

MAE deltas below are option minus persistence on their matched successful events, bootstrapped by participant with 10,000 draws/seed20261016. Negative favours the option. These validation comparisons were used for selection; their intervals are descriptive and not adjusted for candidate selection.

| Option | Delta MAE mg/dL | Descriptive 95% interval |
|---|---:|---|
| chronos_c0_12h | -2.33 | [-3.47, -1.19] |
| chronos_c0_24h | -3.33 | [-4.55, -2.12] |
| chronos_c0_2h | 5.40 | [3.92, 6.99] |
| chronos_c0_6h | 0.02 | [-1.21, 1.33] |
| chronos_c1_6h | 0.65 | [-0.84, 2.26] |
| chronos_c2_6h | 0.49 | [-0.95, 2.03] |
| persistence | 0.00 | [0.00, 0.00] |

Native q10-q90 intervals have nominal 80% coverage. They have **not been calibrated**. Coverage/width below are pooled over successful native-band points; persistence has no probabilistic band here.

| Option | Band events | Coverage | Mean width mg/dL | Negative forecast points | Failure types |
|---|---:|---:|---:|---:|---|
| chronos_c0_12h | 1498 | 61.40% | 75.93 | 8 | {"ModelInferenceError": 11} |
| chronos_c0_24h | 1494 | 64.08% | 75.72 | 0 | {"ModelInferenceError": 15} |
| chronos_c0_2h | 1509 | 49.42% | 75.54 | 259 | {} |
| chronos_c0_6h | 1507 | 57.79% | 75.36 | 10 | {"ModelInferenceError": 2} |
| chronos_c1_6h | 1508 | 59.55% | 84.39 | 42 | {"ModelInferenceError": 1} |
| chronos_c2_6h | 1509 | 59.56% | 83.25 | 38 | {} |
| persistence | 0 | n/a | n/a | 0 | {} |

Underlying failure-cause types: `{"chronos_c0_12h": {"ForecastValidationError": 11}, "chronos_c0_24h": {"ForecastValidationError": 15}, "chronos_c0_2h": {}, "chronos_c0_6h": {"ForecastValidationError": 2}, "chronos_c1_6h": {"ForecastValidationError": 1}, "chronos_c2_6h": {}, "persistence": {}}`. Cause types distinguish contract/backend categories, not the exact invalid numeric output. Failed raw quantiles were not retained or rerun for diagnosis.

## Source subgroups

These descriptive source summaries use the all-option common-success set within each source, rather than pretending failed cases were scored. Source differences are not independent external validation and must not be read as a controlled causal effect of study membership.

| Source | Common events | Option | MAE mg/dL | Within +/-10 |
|---|---:|---|---:|---:|
| Loop | 838 | chronos_c0_12h | 34.08 | 27.29% |
| Loop | 838 | chronos_c0_24h | 32.89 | 27.80% |
| Loop | 838 | chronos_c0_2h | 42.68 | 22.90% |
| Loop | 838 | chronos_c0_6h | 36.74 | 24.93% |
| Loop | 838 | chronos_c1_6h | 37.07 | 25.97% |
| Loop | 838 | chronos_c2_6h | 36.96 | 25.73% |
| Loop | 838 | persistence | 37.87 | 24.44% |
| ReplaceBG | 649 | chronos_c0_12h | 35.17 | 27.94% |
| ReplaceBG | 649 | chronos_c0_24h | 34.17 | 28.16% |
| ReplaceBG | 649 | chronos_c0_2h | 41.98 | 24.36% |
| ReplaceBG | 649 | chronos_c0_6h | 37.16 | 26.96% |
| ReplaceBG | 649 | chronos_c1_6h | 38.34 | 26.35% |
| ReplaceBG | 649 | chronos_c2_6h | 38.10 | 26.48% |
| ReplaceBG | 649 | persistence | 35.73 | 26.81% |

## Interpretation and next phase

The selected option changes macro MAE by **0.00%** relative to persistence. The gate requires at least 10% lower macro MAE, no lower macro within-10 and no worse pooled p95. Passing it on validation would still need independent testing; failing it is evidence to continue with small trained competitors, not a reason to hide the baseline.

The selected option's within-10 rate is 25.47%, while its observed maximum point error is 259.50 mg/dL. Neither an average improvement nor any point percentage establishes a +/-10 maximum-error guarantee. More input history or recorded events are useful only if these held-out development comparisons support them.
The average absolute error still exceeds 10 mg/dL; the frozen approach remains weak against the +/-10 aspiration.
The broader dataset has evaluated the same frozen weights. It has not yet trained them or automatically improved their accuracy.
These scores are not paired before/after comparisons with the earlier UOM or AZT1D cohorts, which contain different participants and events.
A C1/C2 forecast difference is not evidence of a causal insulin or nutrient effect.

The frozen rule selected two hours because it was the only failure-free C0 candidate, **not because it had the lowest point error**. Longer histories improved conditional point accuracy but incurred native-output validation failures. Their useful history signal should not be discarded merely because the native quantile path failed. Phase 4 should retain the frozen baseline and consider longer-history features through predeclared training-only subject-level cross-validation, not relabel this decision after seeing outcomes.
This experiment evaluates a specific recorded-event encoding; it cannot establish that insulin/carbohydrate context is generally uninformative.

Next is Phase 4: train modest direct Ridge/LightGBM candidates on training only, preserve masks and units deliberately, and compare against the frozen baselines. Chronos corrections follow separately. Calibration remains for interval calibration; all 104 primary-test and 65 PEDAP source-test identity reservations remain untouched pending final configuration selection. No app model switch follows from these validation results.
If Phase 4 uses all events eligible at its chosen history, rerun/reuse frozen baselines on exactly those IDs and targets; do not compare different cohorts or overwrite Phase 3 artifacts.

## Reproduction and provenance

```powershell
uv sync --all-groups
uv run --no-sync python -m research.pipelines.run_metabonet_inference
uv run --no-sync python -m research.pipelines.run_metabonet_inference --verify-only
uv run --no-sync python -m research.pipelines.report_metabonet_inference
```

The default output is ignored `artifacts/evaluation-results/metabonet-phase3-v1/`. An interrupted run resumes only matching frozen input/configuration/source fingerprints and checksummed rows. A completed run refuses replay; use verify-only. Corrupt progress requires review, not silent deletion or retry. Source ZIP, package versions, checkpoint-file hashes, protocol, row attempts, summary and the history decision are protected by completion hashes. All rows/identities remain ignored and outside Graphify.

Inference/aggregation stage elapsed: 28.86 minutes (excludes validation loading and model initialization). Two Torch threads, one request per call, offline cached checkpoint. No model-batch speedup or end-to-end application latency claim. Success-wall p95 includes prediction and metric scoring, not initialization/request construction.

| Option | Successful-call wall p95 ms |
|---|---:|
| chronos_c0_12h | 104.64 |
| chronos_c0_24h | 115.26 |
| chronos_c0_2h | 79.92 |
| chronos_c0_6h | 127.44 |
| chronos_c1_6h | 431.35 |
| chronos_c2_6h | 606.96 |
| persistence | 0.07 |

Python 3.12.5; packages: chronos-forecasting 2.3.2, duckdb 1.4.4, numpy 2.5.3, torch 2.14.0.

Protocol: [planning document 13](../planning/GlycoLens_13_MetaboNet_Frozen_Inference.md). Input preparation: [Phase 2 report](metabonet-phase2-preparation-2026-10-16.md). Verification and remaining risks: [Phase 3 handoff](../tooling/metabonet-phase3-handoff-2026-10-16.md).
