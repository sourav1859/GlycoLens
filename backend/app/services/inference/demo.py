"""Deterministic synthetic forecast used only for the Milestone 1 API/UI slice."""

from __future__ import annotations

from datetime import datetime, timedelta

from backend.app.models.forecast import (
    ForecastBandPoint,
    ForecastResponse,
    ForecastSummary,
    HistoryPoint,
)
from research.models.adapters import (
    ForecastRequest,
    ForecastResult,
    QuantileForecast,
    TimePoint,
)


DEMO_NOTICE = (
    "Synthetic demonstration only. This forecast is uncertain, is not clinical guidance, "
    "and must not be used for insulin dosing or treatment decisions."
)


def forecast_to_response(
    request: ForecastRequest,
    result: ForecastResult,
    *,
    data_mode: str = "synthetic_demo",
) -> ForecastResponse:
    """Map the canonical model contract to relative-time chart transport data."""

    if data_mode != "synthetic_demo":
        raise ValueError("Phase 4 supports synthetic_demo transport only")
    q10 = result.quantile_values(0.1)
    q50 = result.quantile_values(0.5)
    q90 = result.quantile_values(0.9)
    history = tuple(
        HistoryPoint(
            minute=round((point.timestamp - request.context_end).total_seconds() / 60),
            value_mg_dl=point.value,
        )
        for point in request.target_history
    )
    forecast = tuple(
        ForecastBandPoint(
            minute=round((timestamp - request.context_end).total_seconds() / 60),
            q10_mg_dl=q10[index],
            q50_mg_dl=q50[index],
            q90_mg_dl=q90[index],
        )
        for index, timestamp in enumerate(result.forecast_timestamps)
    )
    lookup = {point.minute: point.q50_mg_dl for point in forecast}
    return ForecastResponse(
        data_mode="synthetic_demo",
        model_id=result.model_id,
        model_version=result.model_version,
        context_configuration="cgm_only",
        history=history,
        forecast=forecast,
        summary=ForecastSummary(
            minute_30_mg_dl=lookup[30],
            minute_60_mg_dl=lookup[60],
            minute_120_mg_dl=lookup[120],
        ),
        notice=DEMO_NOTICE,
    )


def build_demo_forecast() -> ForecastResponse:
    """Create a deterministic non-patient fixture through the real forecast contracts."""

    context_end = datetime(2026, 1, 1, 12, 0)
    history_values = (
        108,
        109,
        108,
        110,
        111,
        112,
        111,
        113,
        114,
        113,
        115,
        116,
        118,
        117,
        119,
        120,
        119,
        121,
        122,
        121,
        123,
        124,
        123,
        125,
    )
    request = ForecastRequest(
        target_history=tuple(
            TimePoint(
                timestamp=context_end - timedelta(minutes=5 * (23 - index)),
                value=value,
            )
            for index, value in enumerate(history_values)
        )
    )
    median = (
        128,
        132,
        137,
        143,
        149,
        155,
        161,
        166,
        170,
        173,
        175,
        176,
        175,
        173,
        170,
        167,
        163,
        159,
        155,
        151,
        147,
        143,
        139,
        136,
    )
    result = ForecastResult(
        model_id="synthetic-demo",
        model_version="1.0",
        context_start=request.context_start,
        context_end=request.context_end,
        forecast_timestamps=request.forecast_timestamps,
        median=median,
        quantiles=(
            QuantileForecast(0.1, tuple(value - 13 for value in median)),
            QuantileForecast(0.5, median),
            QuantileForecast(0.9, tuple(value + 16 for value in median)),
        ),
        latency_ms=0,
        metadata=(
            ("data_mode", "synthetic_demo"),
            ("target_unit", "mg/dL"),
        ),
    )
    return forecast_to_response(request, result)
