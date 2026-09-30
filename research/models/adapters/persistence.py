"""Deterministic last-observation-carried-forward baseline."""

from __future__ import annotations

from time import perf_counter_ns

from research.models.adapters.base import (
    ForecastModelAdapter,
    ForecastRequest,
    ForecastResult,
    ModelNotLoadedError,
    QuantileForecast,
)


class PersistenceForecastAdapter(ForecastModelAdapter):
    """Repeat the final observed CGM value over the requested horizon."""

    model_id = "persistence"
    model_version = "1.0"

    def __init__(self) -> None:
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load(self) -> None:
        self._loaded = True

    def predict(self, request: ForecastRequest) -> ForecastResult:
        if not self._loaded:
            raise ModelNotLoadedError("persistence adapter must be loaded before prediction")
        if not isinstance(request, ForecastRequest):
            raise TypeError("request must be a ForecastRequest")

        started = perf_counter_ns()
        last_value = request.target_history[-1].value
        values = (last_value,) * request.prediction_length
        quantiles = tuple(
            QuantileForecast(level=level, values=values) for level in request.quantiles
        )
        latency_ms = (perf_counter_ns() - started) / 1_000_000

        return ForecastResult(
            model_id=self.model_id,
            model_version=self.model_version,
            context_start=request.context_start,
            context_end=request.context_end,
            forecast_timestamps=request.forecast_timestamps,
            median=values,
            quantiles=quantiles,
            latency_ms=latency_ms,
            metadata=(
                ("baseline", "last_observation_carried_forward"),
                ("deterministic", "true"),
                ("target_unit", "mg/dL"),
            ),
        )
