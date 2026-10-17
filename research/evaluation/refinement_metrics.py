"""Tolerance/tail evaluation; row-level predictions must remain in ignored artifacts."""

from __future__ import annotations

import math
import statistics
from collections import defaultdict


def percentile(values, fraction):
    ordered = sorted(values)
    if not ordered or not 0 <= fraction <= 1:
        raise ValueError("percentile requires values and a fraction in [0, 1]")
    position = (len(ordered) - 1) * fraction
    left, right = math.floor(position), math.ceil(position)
    return ordered[left] + (ordered[right] - ordered[left]) * (position - left)


def accuracy_metrics(truth, prediction):
    if len(truth) == 0 or len(truth) != len(prediction):
        raise ValueError("truth and predictions must have equal nonempty lengths")
    if any(not math.isfinite(float(v)) for v in (*truth, *prediction)):
        raise ValueError("nonfinite values cannot enter accuracy metrics")
    absolute = [abs(p - y) for p, y in zip(prediction, truth)]
    return {
        "mae": statistics.mean(absolute),
        "rmse": math.sqrt(statistics.mean(e * e for e in absolute)),
        "within_10": statistics.mean(e <= 10 for e in absolute),
        "whole_curve_within_10": float(max(absolute) <= 10),
        "absolute_error_p95": percentile(absolute, 0.95),
        "absolute_error_p99": percentile(absolute, 0.99),
        "max_absolute_error": max(absolute),
    }


def event_metrics(truth, prediction):
    metrics = accuracy_metrics(truth, prediction)
    if len(truth) == 24:
        for horizon, index in ((30, 5), (60, 11), (120, 23)):
            error = abs(truth[index] - prediction[index])
            metrics[f"absolute_error_{horizon}"] = error
            metrics[f"within_10_{horizon}"] = float(error <= 10)
    return metrics


def summarize_records(runs):
    if not runs:
        raise ValueError("at least one run is required")
    sets = [{r["event_id"] for r in rows} for rows in runs.values()]
    if any(s != sets[0] for s in sets[1:]):
        raise ValueError("comparisons require the same requested events")
    if any(len(rows) != len({r["event_id"] for r in rows}) for rows in runs.values()):
        raise ValueError("duplicate events cannot enter a run")
    reference = {
        r["event_id"]: (r["participant_id"], tuple(r["truth"])) for r in next(iter(runs.values()))
    }
    if any(
        reference[r["event_id"]] != (r["participant_id"], tuple(r["truth"]))
        for rows in runs.values()
        for r in rows
    ):
        raise ValueError("paired comparisons require identical participants and targets")
    common = set.intersection(
        *[{r["event_id"] for r in rows if r["error_type"] is None} for rows in runs.values()]
    )
    summary = {
        "requested_event_count": len(sets[0]),
        "common_success_event_count": len(common),
        "contains_row_level_data": False,
        "runs": {},
    }
    for name, rows in runs.items():
        success = [r for r in rows if r["error_type"] is None]
        matched = [r for r in success if r["event_id"] in common]
        by_subject = defaultdict(list)
        for row in matched:
            by_subject[row["participant_id"]].append(event_metrics(row["truth"], row["prediction"]))
        macro = {}
        if matched:
            for key in event_metrics(matched[0]["truth"], matched[0]["prediction"]):
                macro[key] = statistics.mean(
                    statistics.mean(m[key] for m in group) for group in by_subject.values()
                )
        truth = [v for r in matched for v in r["truth"]]
        prediction = [v for r in matched for v in r["prediction"]]
        point_metrics = accuracy_metrics(truth, prediction) if truth else {}
        # Whole-curve pass for the concatenation is not an event-level rate.
        point_metrics.pop("whole_curve_within_10", None)
        summary["runs"][name] = {
            "success_count": len(success),
            "failure_count": len(rows) - len(success),
            "participant_count": len(by_subject),
            "participant_macro": macro,
            "point_metrics": point_metrics,
            "attempted_event_whole_curve_yield": sum(
                accuracy_metrics(r["truth"], r["prediction"])["whole_curve_within_10"]
                for r in success
            )
            / len(rows)
            if rows
            else None,
            "attempted_point_within_10_yield": sum(
                sum(abs(y - p) <= 10 for y, p in zip(r["truth"], r["prediction"])) for r in success
            )
            / sum(len(r["truth"]) for r in rows)
            if rows
            else None,
            "wall_p95_ms": percentile([r["wall_ms"] for r in success], 0.95) if success else None,
        }
    return summary
