"""Stable M2 identities, separate calibration data and origin-only enriched requests."""

from collections import defaultdict
from dataclasses import replace
from datetime import datetime, timedelta

from research.datasets.t1d_uom import MealWindow, ParticipantData
from research.models.adapters import ContextConfiguration
from research.models.adapters.base import CovariateSeries, TimePoint
from research.models.adapters.converters import meal_window_to_forecast_example


def calibration_assignments(manifest):
    groups = defaultdict(list)
    assignments = {
        e["event_id"]: ("diagnostic" if e["split"] == "test" else e["split"]) for e in manifest
    }
    for entry in manifest:
        if entry["split"] == "train":
            groups[entry["participant_id"]].append(entry)
    for entries in groups.values():
        start = min(datetime.fromisoformat(e["meal_at"]) for e in entries)
        end = max(datetime.fromisoformat(e["target_end"]) for e in entries)
        cut = start + (end - start) * 0.8
        for entry in entries:
            assignments[entry["event_id"]] = (
                "train"
                if datetime.fromisoformat(entry["target_end"]) <= cut
                else "calibration"
                if datetime.fromisoformat(entry["meal_at"]) >= cut
                else "purged_boundary"
            )
    return assignments


def enriched_request(window: MealWindow, participant: ParticipantData, *, full_nutrition=True):
    # Start with C0 to avoid any invented basal conversion or source-kind mixing.
    request = meal_window_to_forecast_example(window, context=ContextConfiguration.CGM_ONLY).request
    origin = window.meal.timestamp
    earliest = origin - timedelta(hours=6)
    bolus_values = defaultdict(float)
    for event in window.insulin_history:
        if event.event_type == "bolus":
            bolus_values[event.timestamp] += event.dose
    bolus = [TimePoint(at, value) for at, value in sorted(bolus_values.items())]
    past = [CovariateSeries("insulin_bolus", tuple(bolus), "U")] if bolus else []
    previous = [m for m in participant.meals if earliest <= m.timestamp < origin]
    for suffix, field in [("carbohydrates", "carbs_g")] + (
        [("protein", "protein_g"), ("fat", "fat_g"), ("fiber", "fiber_g")] if full_nutrition else []
    ):
        if previous:
            past.append(
                CovariateSeries(
                    "previous_meal_" + suffix,
                    tuple(TimePoint(m.timestamp, getattr(m, field)) for m in previous),
                    "g",
                )
            )
    known = []
    for suffix, field in [("carbohydrates", "carbs_g")] + (
        [("protein", "protein_g"), ("fat", "fat_g"), ("fiber", "fiber_g")] if full_nutrition else []
    ):
        known.append(
            CovariateSeries(
                "meal_" + suffix, (TimePoint(origin, getattr(window.meal, field)),), "g"
            )
        )
    return replace(request, past_covariates=tuple(past), known_covariates=tuple(known))
