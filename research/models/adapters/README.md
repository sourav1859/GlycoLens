# Forecast Model Adapters

Pretrained forecasting models are isolated behind the common `ForecastModelAdapter` interface so
Chronos-2, TimesFM, CGMformer-based methods, and baselines can be compared without changing the
rest of the system.

Implemented through Milestone 1 Phase 3:

- immutable timestamped request, covariate, held-out target, quantile, and result contracts;
- strict finite-value, frequency, temporal-boundary, shape, and non-crossing-quantile validation;
- explicit separation of model input from future evaluation truth;
- T1D-UOM meal-window conversion for CGM-only, CGM+insulin, and
  CGM+insulin+nutrition configurations;
- deterministic last-observation-carried-forward persistence baseline.
- pinned Chronos-2 CPU adapter for C0/CGM-only inference, with safe lifecycle/backend errors and
  strict output normalization.

Example:

```python
from research.models.adapters import PersistenceForecastAdapter, meal_window_to_forecast_example

example = meal_window_to_forecast_example(window)
adapter = PersistenceForecastAdapter()
adapter.load()
result = adapter.predict(example.request)

# Compare result to example.target only after prediction.
```

Never add future CGM or later event outcomes to `ForecastRequest`. Downloaded model weights and
row-level forecast artifacts remain outside Git.

M1 Phase 3 intentionally rejected covariates. M2 now implements explicit C0-C3
Chronos/TimesFM paths with `recorded_events_v1` (see ADR 0008), including basal-kind
separation and masks. TimesFM 3.0.2 and its immutable checkpoint revision are pinned;
ordinary tests inject fake backends, and real downloads require opt-in. Unsupported
representations fail rather than drop features. Accuracy and under-coverage results
are reported in `docs/reports/milestone-2-model-results.md`.

October 16 refinement adds `tabular.py`: train-only standardized Ridge/LightGBM
multi-output glucose-change heads, optional frozen C0 Chronos residual correction,
and separately calibrated symmetric q10/q90 bands. `origin_features_v1` uses only
origin-known CGM, recorded events and meal descriptors; no subject identity, ambiguous
basal conversion, future target or insulin-action estimate. Shared and full-nutrient
feature sets are different experiments. Uncalibrated equal quantiles are explicitly
marked deterministic; only 0.1/0.5/0.9 levels are supported. Saved trusted-local state
does not serialize foundation weights. See ADR 0010 and research/README.md; no new
adapter is wired into the application by this study.

MetaboNet Phase 4 adds `metabonet_tabular.py` with `metabonet_tabular_v1`:
request-only glucose lags/history summaries and native recorded IU/grams/masks.
Ridge fits 24 glucose deltas jointly with train-only imputation/scaling. LightGBM
uses one pooled-horizon delta regressor with horizon fraction; subject splitting
precedes horizon expansion. Both use equal participant training weights. Quantile
fields remain deterministic placeholders until a separate calibration phase.
The dedicated runner freezes training-only subject-CV choices before validation,
checks trusted local bundles before reload and reuses verified Phase 3 forecasts.
See [ADR 0012](../../../docs/decisions/0012-metabonet-direct-model-selection.md) and
[protocol 14](../../../docs/planning/GlycoLens_14_MetaboNet_Direct_Models.md).

MetaboNet Phase 5 adds `metabonet_context.py` (the exact frozen six-hour C2 request)
and `metabonet_residual.py` (151-feature corrections to that frozen median). Small
heads reuse the direct adapter's extracted regression helpers; saved Phase 4 outputs
remain equivalent. Baseline forecasts are inputs, never observed future glucose.
Saved residual heads strip a live backbone; use `attach_backbone` explicitly or
`predict_from_baseline` with verified cached provenance. Native backbone bands are
not inherited as corrected uncertainty. Live public prediction timing includes
backbone plus head; cached/batch head timings are reported separately.
See [ADR 0013](../../../docs/decisions/0013-frozen-chronos-correction-and-matched-controls.md)
and [protocol 15](../../../docs/planning/GlycoLens_15_MetaboNet_Chronos_Correction.md).

Phase 6's `research/evaluation/metabonet_uncertainty.py` adds an immutable `SymmetricBands` state and `CalibratedForecastAdapter` wrapper. It preserves the supplied point forecast and common contract, exposing explicitly labeled symmetric marginal 80% bands at q10/q90 rather than deterministic placeholders or learned conditional quantiles. A separate maximum-error radius serves whole-curve evaluation. It does not mutate or refit the supplied model. Exchangeability/study-shift coverage is unverified; PEDAP undercoverage is reported. This wrapper is research-only and is not wired into the app. See [ADR 0014](../../../docs/decisions/0014-independent-testing-and-participant-calibration.md).
