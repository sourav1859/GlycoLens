# Milestone 1 Phase 2: Forecast Contract and Persistence Baseline

**Date:** September 29, 2026
**Status:** Implemented and validated
**Scope:** Common forecast contract, leakage boundary, T1D-UOM conversion, and persistence baseline

## Outcome

GlycoLens now has one model-independent forecast interface for baselines and pretrained models.
Held-out future CGM is stored in a separate evaluation target and cannot be passed to
`ForecastModelAdapter.predict()`. The deterministic persistence baseline runs through this
contract on a real eligible T1D-UOM V1.0.4 meal window.

This phase does not evaluate forecast accuracy or provide model uncertainty. Equal persistence
quantiles are contract-compatible placeholders for a deterministic baseline.

## Implemented components

| Component | Responsibility |
|---|---|
| `TimePoint` | Finite value and timestamp |
| `CovariateSeries` | Named immutable past or known covariate |
| `ForecastRequest` | Model-visible history, context, horizon, frequency, and quantiles only |
| `ForecastTarget` | Held-out future truth, unavailable to adapters |
| `ForecastExample` | Evaluation-only request/target pairing with exact-grid validation |
| `QuantileForecast` | One finite quantile trajectory |
| `ForecastResult` | Validated model identity, timestamps, median, quantiles, latency, and metadata |
| `ForecastModelAdapter` | Common `load()` and `predict(request)` interface |
| `PersistenceForecastAdapter` | Last-observation-carried-forward baseline |
| T1D-UOM converter | CGM-only, CGM+insulin, and CGM+insulin+nutrition request construction |

## Test traceability

| Requirement or risk | Scenario | Layer | Evidence | Result |
|---|---|---|---|---|
| Adapter lifecycle | Predict before load fails; repeated load succeeds | Unit | `test_persistence_requires_explicit_load_and_load_is_idempotent` | Pass |
| Forecast shape | Persistence returns 24 points and requested quantiles | Unit | `test_persistence_returns_24_ordered_future_points_and_requested_quantiles` | Pass |
| Baseline definition | Every horizon and quantile repeats last CGM | Unit | `test_persistence_repeats_last_value_with_equal_non_crossing_quantiles` | Pass |
| Numeric safety | NaN and positive/negative infinity are rejected | Unit | `test_non_finite_history_values_are_rejected` | Pass |
| Time-grid safety | Empty, irregular, and mixed-awareness histories fail | Unit | `test_empty_irregular_and_mixed_awareness_histories_are_rejected` | Pass |
| Request boundaries | Invalid horizon, frequency, and quantiles fail | Unit | `test_invalid_request_configuration_is_rejected` | Pass |
| Covariate leakage | Future past-covariates and invalid known times fail | Unit | `test_covariate_temporal_boundaries_and_names_are_enforced` | Pass |
| Mutation safety | Mutable caller sequences are defensively copied | Unit | `test_request_defensively_copies_mutable_sequences` | Pass |
| Output validity | Shape, finite values, frequency, and quantile crossing fail closed | Contract | `test_result_rejects_shape_errors_non_finite_values_and_crossing_quantiles` | Pass |
| Target leakage | Request has no target, target CGM, or participant field | Contract | `test_converter_keeps_future_truth_out_of_model_request` | Pass |
| Adapter leakage | Spy receives only `ForecastRequest` | Contract | `test_spy_adapter_receives_only_request_not_held_out_target` | Pass |
| Context ablation | Three contexts differ only by intended covariates | Unit | `test_converter_supports_context_ablation_and_aggregates_same_time_insulin` | Pass |
| Malformed source window | Wrong shape, future insulin, and absent required insulin fail | Unit | `test_converter_rejects_wrong_window_shape_and_future_insulin` | Pass |
| Source integrity | Conversion does not mutate `MealWindow` | Unit | `test_converter_does_not_mutate_source_window` | Pass |
| Privacy-safe evidence | Smoke summary omits IDs, glucose values, and timestamps | Security/unit | `test_public_smoke_summary_excludes_identifiers_and_row_values` | Pass |

Parameterized boundary cases produce 22 passing Phase 2 tests. The complete repository suite has
34 tests after this phase.

The final code-only Graphify refresh passed its exclusion checks and rebuilt the local graph with
929 nodes, about 1,200 edges, and 125 communities. Semantic documentation extraction remained
disabled.

## Real-data smoke validation

Command:

```powershell
uv run python -m research.pipelines.run_persistence_baseline
```

Aggregate result on the verified local T1D-UOM V1.0.4 extraction:

| Field | Result |
|---|---:|
| Eligible window found | Yes |
| Context configuration | CGM + insulin + nutrition |
| History points | 24 |
| Forecast points | 24 |
| Held-out target points | 24 |
| Frequency | 5 minutes |
| Quantiles | 0.1, 0.5, 0.9 |
| Finite forecasts | Yes |
| Non-crossing quantiles | Yes |
| Target withheld from request | Yes |
| Single smoke-call adapter latency | 0.0783 ms |

The latency value is environment-specific, excludes dataset scanning, and is not a benchmark.
No participant ID, timestamp, glucose value, or target value was printed or committed.

## Safety findings

Blocking findings: none.

Defense-in-depth controls implemented:

- future truth is structurally separated from model requests;
- past covariates cannot extend beyond the forecast context boundary;
- participant identifiers are not part of the model request;
- result quantiles must be ordered and finite;
- persistence quantiles are explicitly documented as deterministic rather than calibrated;
- real-data command output is aggregate only.

## Phase 3 follow-up

Phase 3 completed the pinned Chronos-2 adapter and real-data CPU smoke test using this contract.
Model weights remain ignored, output shapes and quantiles are validated, and cold/warm latency and
memory are recorded in `milestone-1-phase-3-chronos2-smoke.md`.
