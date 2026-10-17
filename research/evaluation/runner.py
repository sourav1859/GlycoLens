"""Matched evaluation and explicit failures; raw rows remain ignored research artifacts."""

from __future__ import annotations

import statistics
from collections import defaultdict
from dataclasses import dataclass
from time import perf_counter

from research.evaluation.metrics import score_forecast
from research.evaluation.protocol import event_id
from research.datasets.t1d_uom import MealWindow
from research.models.adapters import ForecastModelAdapter, ContextConfiguration
from research.models.adapters.converters import meal_window_to_forecast_example


@dataclass(frozen=True)
class EvaluationRow:
    event_id: str
    participant_id: str
    model_id: str
    context: str
    metrics: dict[str, float]
    wall_ms: float | None
    error_type: str | None


def evaluate(
    windows: tuple[MealWindow, ...],
    adapter: ForecastModelAdapter,
    context: ContextConfiguration,
) -> tuple[EvaluationRow, ...]:
    rows = []
    for window in windows:
        started = perf_counter()
        try:
            example = meal_window_to_forecast_example(window, context=context)
            result = adapter.predict(example.request)
            scores = score_forecast(example, result)
            rows.append(
                EvaluationRow(
                    event_id(window),
                    window.participant_id,
                    adapter.model_id,
                    context.value,
                    scores,
                    (perf_counter() - started) * 1000,
                    None,
                )
            )
        except Exception as error:
            # Never include exception text: upstream messages may disclose data/paths.
            rows.append(
                EvaluationRow(
                    event_id(window),
                    window.participant_id,
                    adapter.model_id,
                    context.value,
                    {},
                    None,
                    type(error).__name__,
                )
            )
    return tuple(rows)


def comparison_summary(runs: dict[str, tuple[EvaluationRow, ...]]) -> dict[str, object]:
    if not runs:
        raise ValueError("at least one evaluation run is required")
    event_sets = [{row.event_id for row in rows} for rows in runs.values()]
    if any(events != event_sets[0] for events in event_sets[1:]):
        raise ValueError("models must be evaluated on exactly the same requested events")
    if any(len({r.event_id for r in rows}) != len(rows) for rows in runs.values()):
        raise ValueError("duplicate evaluation events")
    common = set.intersection(
        *[{r.event_id for r in rows if r.error_type is None} for rows in runs.values()]
    )
    summary: dict[str, object] = {
        "requested_event_count": len(event_sets[0]),
        "common_success_event_count": len(common),
        "contains_row_level_data": False,
        "runs": {},
    }
    for name, rows in runs.items():
        successful = [r for r in rows if r.error_type is None]
        matched = [r for r in successful if r.event_id in common]
        metrics: dict[str, object] = {}
        names = set.intersection(*[set(r.metrics) for r in matched]) if matched else set()
        for metric in sorted(names):
            by_subject: dict[str, list[float]] = defaultdict(list)
            for row in matched:
                by_subject[row.participant_id].append(row.metrics[metric])
            metrics[metric] = {
                "event_mean": statistics.mean(r.metrics[metric] for r in matched),
                "event_median": statistics.median(r.metrics[metric] for r in matched),
                "participant_macro_mean": statistics.mean(
                    statistics.mean(values) for values in by_subject.values()
                ),
            }
        latencies = sorted(r.wall_ms for r in successful if r.wall_ms is not None)
        summary["runs"][name] = {  # type: ignore[index]
            "success_count": len(successful),
            "failure_count": len(rows) - len(successful),
            "failure_rate": (len(rows) - len(successful)) / len(rows) if rows else None,
            "matched_metrics": metrics,
            "wall_ms_p50": statistics.median(latencies) if latencies else None,
            "wall_ms_p95": latencies[max(0, math_ceil_rank(len(latencies), 0.95) - 1)]
            if latencies
            else None,
        }
    return summary


def math_ceil_rank(count: int, fraction: float) -> int:
    import math

    return math.ceil(count * fraction)
