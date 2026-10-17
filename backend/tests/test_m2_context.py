from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from backend.app.services.inference.application import build_request


def fixture():
    origin = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
    meal = {
        "recorded_at": origin.isoformat(),
        "carbs_g": 40,
        "protein_g": 20,
        "fat_g": 10,
        "fiber_g": 5,
    }
    cgm = [
        {
            "recorded_at": (origin - timedelta(minutes=5 * i)).isoformat(),
            "glucose_mg_dl": 120,
            "source": "simulation",
        }
        for i in range(24)
    ]
    insulin = [
        {"recorded_at": origin.isoformat(), "event_type": "bolus", "units": 1, "source_unit": "U"}
    ]
    return origin, meal, cgm, insulin


def test_application_never_includes_future_glucose_or_insulin():
    origin, meal, cgm, insulin = fixture()
    cgm.append(
        {
            "recorded_at": (origin + timedelta(minutes=5)).isoformat(),
            "glucose_mg_dl": 999,
            "source": "simulation",
        }
    )
    insulin.append(
        {
            "recorded_at": (origin + timedelta(minutes=5)).isoformat(),
            "event_type": "bolus",
            "units": 99,
        }
    )
    request = build_request(meal, cgm, insulin)
    assert len(request.target_history) == 24
    assert all(p.timestamp <= origin and p.value != 999 for p in request.target_history)
    assert all(
        p.timestamp <= origin and p.value != 99 for s in request.past_covariates for p in s.points
    )


def test_missing_history_and_unverified_sources_fail_closed():
    _, meal, cgm, insulin = fixture()
    with pytest.raises(HTTPException):
        build_request(meal, cgm[:-1], insulin)
    cgm[0]["source"] = "unknown"
    with pytest.raises(HTTPException):
        build_request(meal, cgm, insulin)


def test_same_time_bolus_is_aggregated_before_contract_validation():
    _, meal, cgm, insulin = fixture()
    request = build_request(meal, cgm, insulin + insulin)
    assert request.past_covariates[0].points[0].value == 2
