"""Versioned recorded-event representation, not a physiological insulin model.

Values are binned at the first grid point at/after a past event. Basal source
observations retain kind and an observation mask; no rate-to-dose conversion or
invented basal continuation is performed. Older context is retained in explicit
origin-known summaries. Meal composition is an origin impulse, with future zero
meal impulses under the core no-follow-up-meal assumption.
"""

from __future__ import annotations

import bisect

from research.models.adapters.base import ForecastRequest, ForecastValidationError


FEATURE_VERSION = "recorded_events_v1"


def aligned_covariates(
    request: ForecastRequest,
) -> tuple[dict[str, list[float]], dict[str, list[float]]]:
    history_times = [point.timestamp for point in request.target_history]
    size = len(history_times)
    past: dict[str, list[float]] = {}
    future: dict[str, list[float]] = {}
    for series in request.past_covariates:
        values = [0.0] * size
        observed = [0.0] * size
        older = []
        for point in series.points:
            if point.timestamp < history_times[0]:
                older.append(point.value)
                continue
            index = bisect.bisect_left(history_times, point.timestamp)
            if index >= size:
                raise ForecastValidationError("past covariate exceeds forecast origin")
            if series.name.startswith("insulin_basal_kind_"):
                values[index] = point.value
            else:
                values[index] += point.value
            observed[index] += 1.0
        past[series.name] = values
        past[f"{series.name}_observed"] = observed
        # Explicit summaries of older observed context retain the six-hour lookback.
        # Basal last-observed source value is not an inferred active basal rate.
        summary = sum(older) if series.name == "insulin_bolus" else (older[-1] if older else 0.0)
        past[f"{series.name}_older_summary"] = [summary] * size
        past[f"{series.name}_older_present"] = [float(bool(older))] * size
    for series in request.known_covariates:
        if not series.name.startswith("meal_") or len(series.points) != 1:
            raise ForecastValidationError(
                "recorded_events_v1 supports only origin-known meal descriptors"
            )
        point = series.points[0]
        if point.timestamp != request.context_end:
            raise ForecastValidationError("meal descriptors must occur at forecast origin")
        past[series.name] = [0.0] * (size - 1) + [point.value]
        future[series.name] = [0.0] * request.prediction_length
    return past, future
