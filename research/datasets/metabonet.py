"""Origin-safe shared-feature windows in native mg/dL and five-minute IU amounts.

Only finite source values are called record-present; this is not proof of complete
event logging or original sensor observation. Missing doses are never forward-filled.
Future labels remain outside immutable ForecastRequest objects.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import cached_property

import numpy as np

from research.datasets.t1d_uom import WindowRejected
from research.models.adapters.base import (
    CovariateSeries,
    ForecastExample,
    ForecastRequest,
    ForecastTarget,
    TimePoint,
)

STEP_NS = 300_000_000_000
SCHEMA_VERSION = "metabonet_windows_v1"
CHANNELS = ("carbs", "bolus", "basal", "insulin")


@dataclass(frozen=True)
class SubjectSeries:
    sid: str
    source: str
    times: np.ndarray
    # CGM, carbs, bolus, basal, insulin. Source units: mg/dL, g, IU, IU, IU.
    values: np.ndarray

    def __post_init__(self):
        if self.values.shape != (len(self.times), 5) or len(self.times) < 2:
            raise ValueError("invalid projected subject shape")
        if np.any(np.diff(self.times) <= 0):
            raise ValueError("duplicate or unsorted subject timestamps")

    @cached_property
    def valid_glucose_indices(self):
        return np.flatnonzero(np.isfinite(self.values[:, 0]) & (self.values[:, 0] > 0))

    @cached_property
    def meal_indices(self):
        return np.flatnonzero(np.isfinite(self.values[:, 1]) & (self.values[:, 1] > 0))

    @cached_property
    def meal_times(self):
        return self.times[self.meal_indices]


def event_identity(sid, meal_ns):
    return hashlib.sha256(f"{SCHEMA_VERSION}|{sid}|{int(meal_ns)}".encode()).hexdigest()


def candidate_indices(series, *, limit=100):
    # Sample origins before inspecting targets; stable across histories and delays.
    return sorted(
        sorted(
            (int(i) for i in series.meal_indices),
            key=lambda i: event_identity(series.sid, series.times[i]),
        )[:limit]
    )


def values_at(series, grid):
    positions = np.searchsorted(series.times, grid)
    clipped = np.minimum(positions, len(series.times) - 1)
    exact = (positions < len(series.times)) & (series.times[clipped] == grid)
    values = np.full((len(grid), 5), np.nan)
    values[exact] = series.values[clipped[exact]]
    return values


def build_window(series, meal_index, *, hours, delay_minutes=5):
    if hours not in (2, 6, 12, 24) or delay_minutes not in (0, 5):
        raise ValueError("unsupported frozen window configuration")
    meal_ns = int(series.times[meal_index])
    carbs = float(series.values[meal_index, 1])
    if not np.isfinite(carbs) or carbs <= 0:
        raise WindowRejected("invalid_meal")
    origin = meal_ns + delay_minutes * 60_000_000_000
    # Retrospective isolated-meal selection, never an input available at forecast time.
    previous = np.searchsorted(series.meal_times, meal_ns, side="left")
    if previous and meal_ns - int(series.meal_times[previous - 1]) <= 3 * STEP_NS:
        raise WindowRejected("clustered_meal")
    following = np.searchsorted(series.meal_times, meal_ns, side="right")
    if following < len(series.meal_times) and series.meal_times[following] <= origin + 24 * STEP_NS:
        raise WindowRejected("follow_up_meal")
    grid = origin - np.arange(hours * 12 - 1, -1, -1, dtype=np.int64) * STEP_NS
    source_history = values_at(series, grid)[:, 0]
    observed = np.isfinite(source_history) & (source_history > 0)
    valid = series.valid_glucose_indices
    if len(valid) == 0:
        raise WindowRejected("incomplete_history")
    times = series.times[valid]
    positions = np.searchsorted(times, grid, side="right") - 1
    last = np.maximum(positions, 0)
    # Last-past-value fill only; never interpolate from a later reading.
    if np.any(positions < 0) or np.any(grid - times[last] > 2 * STEP_NS) or observed.mean() < 0.9:
        raise WindowRejected("incomplete_history")
    history = series.values[valid[last], 0]
    target_grid = origin + np.arange(1, 25, dtype=np.int64) * STEP_NS
    truth = values_at(series, target_grid)[:, 0]
    if not np.all(np.isfinite(truth) & (truth > 0)):
        raise WindowRejected("incomplete_target")
    context_grid = origin - np.arange(71, -1, -1, dtype=np.int64) * STEP_NS
    context = values_at(series, context_grid)
    # Conservative carb availability: raw meal bin + delay. Insulin is trailing-bin.
    context[:, 1] = values_at(series, context_grid - delay_minutes * 60_000_000_000)[:, 1]
    covariates = {
        name: [float(v) if np.isfinite(v) and v >= 0 else None for v in context[:, i + 1]]
        for i, name in enumerate(CHANNELS)
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "sid": series.sid,
        "source": series.source,
        "event_id": event_identity(series.sid, meal_ns),
        "meal_bin_ns": meal_ns,
        "origin_ns": origin,
        "history_hours": hours,
        "carb_delay_minutes": delay_minutes,
        "meal_carbs_g": carbs,
        "history": [float(v) for v in history],
        "history_record_present": [int(v) for v in observed],
        "context": covariates,
        "truth": [float(v) for v in truth],
    }


def timestamp(ns):
    # Keep exact source ns in artifacts. Contract datetimes retain microsecond precision.
    return datetime(1970, 1, 1) + timedelta(microseconds=int(ns) // 1000)


def window_to_example(window, *, with_covariates=False):
    if window["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported prepared-window schema")
    origin = int(window["origin_ns"])
    history = tuple(
        TimePoint(timestamp(origin - (len(window["history"]) - 1 - i) * STEP_NS), float(v))
        for i, v in enumerate(window["history"])
    )
    past = []
    known = []
    if with_covariates:
        for name in CHANNELS:
            values = window["context"][name]
            channel = (
                "previous_meal_carbohydrates"
                if name == "carbs"
                else {
                    "bolus": "insulin_bolus",
                    "basal": "insulin_basal",
                    "insulin": "insulin_total",
                }[name]
            )
            unit = "g" if name == "carbs" else "IU_per_source_interval"
            points = tuple(
                TimePoint(timestamp(origin - (71 - i) * STEP_NS), v)
                for i, v in enumerate(values)
                if v is not None and v > 0 and (name != "carbs" or i < 71)
            )
            if points:
                past.append(CovariateSeries(channel, points, unit))
            past.append(
                CovariateSeries(
                    channel + "_record_present",
                    tuple(
                        TimePoint(timestamp(origin - (71 - i) * STEP_NS), float(v is not None))
                        for i, v in enumerate(values)
                    ),
                    "source_record_present",
                )
            )
        past.append(
            CovariateSeries(
                "cgm_record_present",
                tuple(
                    TimePoint(p.timestamp, float(mask))
                    for p, mask in zip(history, window["history_record_present"])
                ),
                "source_record_present",
            )
        )
        known = [
            CovariateSeries(
                "meal_carbohydrates", (TimePoint(timestamp(origin), window["meal_carbs_g"]),), "g"
            )
        ]
    request = ForecastRequest(history, past_covariates=tuple(past), known_covariates=tuple(known))
    target = ForecastTarget(
        tuple(
            TimePoint(timestamp(origin + (i + 1) * STEP_NS), v)
            for i, v in enumerate(window["truth"])
        )
    )
    return ForecastExample(request, target)


def trajectory_fingerprints(series):
    # Exact six-hour varied CGM segments at hourly endpoints. No timestamp/ID in hash.
    for end in np.flatnonzero(series.times % (12 * STEP_NS) == 0):
        if end < 71:
            continue
        times = series.times[end - 71 : end + 1]
        values = series.values[end - 71 : end + 1, 0]
        if (
            np.any(np.diff(times) != STEP_NS)
            or not np.all(np.isfinite(values) & (values > 0))
            or np.unique(values).size < 20
            or np.ptp(values) < 20
        ):
            continue
        yield hashlib.sha256(np.round(values, 4).astype("<f8").tobytes()).digest()
