"""Explicit context boundaries; no cloud/network/model needed for these oracles."""

from datetime import date
from uuid import uuid4
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from backend.app.api.meals import MealSave
from backend.app.api.nutrition import nutrition_summary
from backend.app.db.client import UserSession


def payload(**changes):
    return dict(
        name="Synthetic reviewed meal",
        recorded_at="2026-11-14T17:00:00Z",
        confirmed=True,
        idempotency_key=str(uuid4()),
        items=[dict(food_id=str(uuid4()), grams=100)],
        **changes,
    )


def test_ambiguous_old_write_fails_closed():
    with pytest.raises(ValidationError):
        MealSave.model_validate(payload())


@pytest.mark.parametrize(
    "scope",
    [
        dict(workspace="simulation"),
        dict(workspace="personal", source_session_id=str(uuid4())),
        dict(workspace="legacy_unclassified"),
    ],
)
def test_inconsistent_write_scope_rejected(scope):
    with pytest.raises(ValidationError):
        MealSave.model_validate(payload(**scope))


@pytest.mark.parametrize("workspace", ["personal", "simulation"])
def test_explicit_write_contract(workspace):
    values = payload(workspace=workspace)
    if workspace == "simulation":
        values["source_session_id"] = str(uuid4())
    body = MealSave.model_validate(values)
    assert body.workspace == workspace


def test_personal_nutrition_ignores_selected_virtual_source():
    calls = []

    def db(session, path, **kwargs):
        calls.append((path, kwargs))
        if path.startswith("user_preferences?"):
            return [dict(timezone="America/New_York", source_session_id=str(uuid4()))]
        assert not path.startswith("source_sessions"), "Personal time must not read a virtual clock"
        if path.startswith("rpc/"):
            assert kwargs["payload"]["p_workspace"] == "personal"
            assert kwargs["payload"]["p_source"] is None
            return []
        if path.startswith("meals?"):
            assert "workspace=eq.personal" in path
        return []

    with patch("backend.app.api.nutrition.database_call", side_effect=db):
        value = nutrition_summary(UserSession("synthetic", "owner"), date(2026, 11, 14))
    assert value["available"] and value["source"] is None
    assert value["day"] == "2026-11-14"


def test_personal_default_day_is_current_profile_day():
    from datetime import datetime, timezone
    from zoneinfo import ZoneInfo

    def db(session, path, **kwargs):
        if path.startswith("user_preferences?"):
            return [dict(timezone="Pacific/Kiritimati")]
        return []

    with patch("backend.app.api.nutrition.database_call", side_effect=db):
        value = nutrition_summary(UserSession("synthetic", "owner"))
    assert (
        value["day"]
        == datetime.now(timezone.utc).astimezone(ZoneInfo("Pacific/Kiritimati")).date().isoformat()
    )


def test_timeline_is_explicitly_virtual_and_requires_source():
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.db.client import user_session

    app.dependency_overrides[user_session] = lambda: UserSession("synthetic", str(uuid4()))
    try:
        with TestClient(app) as client:
            assert client.get("/api/v1/timeline").status_code == 422
            assert (
                client.get(
                    f"/api/v1/timeline?workspace=personal&source_session_id={uuid4()}"
                ).status_code
                == 422
            )
    finally:
        app.dependency_overrides.pop(user_session, None)
