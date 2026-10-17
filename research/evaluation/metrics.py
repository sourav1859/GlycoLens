"""Event-level metrics with strict request/result/held-out grid agreement."""

from __future__ import annotations

import math

from research.models.adapters.base import ForecastExample, ForecastResult


def score_forecast(example: ForecastExample, result: ForecastResult) -> dict[str, float]:
    if result.forecast_timestamps != example.request.forecast_timestamps:
        raise ValueError("result grid differs from the held-out evaluation grid")
    if result.context_end != example.request.context_end:
        raise ValueError("result forecast origin differs from the request")
    truth = tuple(point.value for point in example.target.points)
    errors = tuple(predicted - actual for predicted, actual in zip(result.median, truth))
    scores = {
        "mae": sum(abs(error) for error in errors) / len(errors),
        "rmse": math.sqrt(sum(error * error for error in errors) / len(errors)),
    }
    minutes = tuple(
        int((timestamp - result.context_end).total_seconds() / 60)
        for timestamp in result.forecast_timestamps
    )
    for horizon in (30, 60, 120):
        if horizon in minutes:
            scores[f"absolute_error_{horizon}"] = abs(errors[minutes.index(horizon)])
    if dict(result.metadata).get("deterministic") != "true":
        lower, upper = result.quantile_values(0.1), result.quantile_values(0.9)
        scores["interval_coverage"] = sum(
            low <= actual <= high for low, actual, high in zip(lower, truth, upper)
        ) / len(truth)
        scores["interval_width"] = sum(high - low for low, high in zip(lower, upper)) / len(truth)
        for forecast in result.quantiles:
            scores[f"pinball_{forecast.level:g}"] = sum(
                max(
                    forecast.level * (actual - predicted),
                    (forecast.level - 1) * (actual - predicted),
                )
                for actual, predicted in zip(truth, forecast.values)
            ) / len(truth)
    return scores
