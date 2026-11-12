"""Onboarding fields are checked before any cloud write; owner comes from session."""

import pytest
from fastapi.testclient import TestClient

from backend.app.db.client import UserSession, user_session
from backend.app.main import app


@pytest.mark.parametrize(
    "body",
    [
        {"revision": 0, "step": "preferences", "values": {}},
        {
            "revision": 0,
            "step": "preferences",
            "values": {"timezone": "Invalid/Zone", "glucose_unit": "mg/dL"},
        },
        {"revision": 0, "step": "source", "values": {"source_mode": "live_patient"}},
        {"revision": 0, "step": "review", "values": {}},
        {
            "revision": 0,
            "step": "source",
            "values": {"source_mode": "simulation"},
            "user_id": "forged",
        },
    ],
)
def test_invalid_or_owner_supplied_setup_is_rejected_before_write(body):
    app.dependency_overrides[user_session] = lambda: UserSession(
        "synthetic", "10000000-0000-4000-8000-000000000001"
    )
    try:
        with TestClient(app) as client:
            assert client.patch("/api/v1/me/onboarding", json=body).status_code == 422
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize(
    "body",
    [
        {"revision": 0, "notice_version": "research-v1", "acknowledged": False},
        {"revision": 0, "notice_version": "obsolete", "acknowledged": True},
        {"revision": 0, "notice_version": "research-v1", "acknowledged": True, "completed": True},
    ],
)
def test_completion_cannot_bypass_acknowledgement_or_version(body):
    app.dependency_overrides[user_session] = lambda: UserSession(
        "synthetic", "10000000-0000-4000-8000-000000000001"
    )
    try:
        with TestClient(app) as client:
            response = client.post("/api/v1/me/onboarding/complete", json=body)
            assert response.status_code == 422
            assert response.headers["cache-control"] == "private, no-store"
    finally:
        app.dependency_overrides.clear()
