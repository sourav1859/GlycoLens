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

Phase 3 intentionally rejects C1/C3 requests in the Chronos-2 adapter. Covariate support must be
implemented as an explicit model-specific path; it must never be silently ignored.
