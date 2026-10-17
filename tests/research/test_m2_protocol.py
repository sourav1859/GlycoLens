from dataclasses import replace
from datetime import timedelta

import pytest

from research.datasets.t1d_uom import InsulinEvent
from research.evaluation.protocol import (
    SplitPolicy,
    event_id,
    manifest_summary,
    subject_manifest,
    temporal_manifest,
)
from research.models.adapters import ContextConfiguration, ForecastValidationError
from research.models.adapters.converters import meal_window_to_forecast_example
from tests.research.models.test_forecast_adapters import _meal_window


def shifted_window(index: int, subject: str = "synthetic-A", *, minutes: bool = False):
    window = _meal_window()
    shift = timedelta(minutes=index * 130) if minutes else timedelta(days=index)
    return replace(
        window,
        participant_id=subject,
        meal=replace(window.meal, timestamp=window.meal.timestamp + shift),
        cgm_history=tuple(replace(p, timestamp=p.timestamp + shift) for p in window.cgm_history),
        target_cgm=tuple(replace(p, timestamp=p.timestamp + shift) for p in window.target_cgm),
        insulin_history=tuple(
            replace(p, timestamp=p.timestamp + shift) for p in window.insulin_history
        ),
    )


def test_temporal_splits_are_deterministic_target_purged_and_order_independent():
    windows = tuple(shifted_window(i, minutes=True) for i in range(10))
    policy = SplitPolicy(0.61, 0.19)
    entries = temporal_manifest(windows, policy)
    assert entries == temporal_manifest(tuple(reversed(windows)), policy)
    assert manifest_summary(entries)["split_counts"]["purged_boundary"] > 0
    assert "test" in {entry.split for entry in entries}
    assert "validation" in {entry.split for entry in entries}
    by_split = {s: [e for e in entries if e.split == s] for s in ("train", "validation", "test")}
    assert max(e.target_end for e in by_split["train"]) <= min(
        e.meal_at for e in by_split["validation"]
    )
    assert max(e.target_end for e in by_split["validation"]) <= min(
        e.meal_at for e in by_split["test"]
    )


def test_split_assignment_and_identity_do_not_depend_on_outcomes():
    windows = tuple(shifted_window(i) for i in range(10))
    changed = tuple(
        replace(w, target_cgm=tuple(replace(p, glucose_mmol_l=99) for p in w.target_cgm))
        for w in windows
    )
    assert temporal_manifest(windows) == temporal_manifest(changed)
    assert event_id(windows[0]) != event_id(windows[1])
    with pytest.raises(ValueError, match="duplicate"):
        temporal_manifest((windows[0], windows[0]))


def test_subject_holdouts_cannot_overlap_or_reference_unknown_subjects():
    windows = tuple(shifted_window(i, subject) for subject in ("a", "b", "c") for i in range(3))
    entries = subject_manifest(
        windows, validation_subjects=frozenset({"b"}), test_subjects=frozenset({"c"})
    )
    assert all(
        e.split == {"a": "train", "b": "validation", "c": "test"}[e.participant_id] for e in entries
    )
    with pytest.raises(ValueError, match="disjoint"):
        subject_manifest(
            windows, validation_subjects=frozenset({"b"}), test_subjects=frozenset({"b"})
        )
    with pytest.raises(ValueError):
        subject_manifest(
            windows, validation_subjects=frozenset({"missing"}), test_subjects=frozenset({"c"})
        )
    with pytest.raises(ValueError):
        SplitPolicy(0.8, 0.3)


def test_c2_has_only_carbohydrate_and_retains_insulin():
    request = meal_window_to_forecast_example(
        _meal_window(), context=ContextConfiguration.CGM_INSULIN_CARBOHYDRATES
    ).request
    assert {s.name for s in request.known_covariates} == {"meal_carbohydrates"}
    assert request.past_covariates


def test_basal_kinds_do_not_mix_or_sum_rates_and_conflicts_fail_closed():
    window = _meal_window()
    at = window.meal.timestamp - timedelta(minutes=30)
    basal = (InsulinEvent(at, "basal", 0.8, "R"), InsulinEvent(at, "basal", 15, "L"))
    request = meal_window_to_forecast_example(
        replace(window, insulin_history=basal + (basal[0],))
    ).request
    assert {s.name: s.points[0].value for s in request.past_covariates} == {
        "insulin_basal_kind_R": 0.8,
        "insulin_basal_kind_L": 15,
    }
    assert all(s.unit == "source_U_or_U_per_hour" for s in request.past_covariates)
    with pytest.raises(ForecastValidationError, match="conflicting"):
        meal_window_to_forecast_example(
            replace(window, insulin_history=basal + (replace(basal[0], dose=1.2),))
        )
