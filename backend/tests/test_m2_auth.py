from fastapi.testclient import TestClient

from backend.app.db.client import UserSession, user_session
from backend.app.main import app


def test_meals_and_timeline_reject_requests_without_session():
    with TestClient(app) as client:
        assert client.get("/api/v1/timeline").status_code == 401
        assert client.post("/api/v1/demo/session").status_code == 401


def test_meal_rejects_forged_owner_and_naive_time_before_persistence():
    app.dependency_overrides[user_session] = lambda: UserSession("test-only", "synthetic-user")
    body = {
        "name": "synthetic",
        "recorded_at": "2026-01-01T12:00:00",
        "idempotency_key": "40000000-0000-4000-8000-000000000001",
        "items": [{"food_id": "00000000-0000-4000-8000-000000000001", "grams": 100}],
    }
    try:
        with TestClient(app) as client:
            assert (
                client.post("/api/v1/meals", json={**body, "user_id": "another-user"}).status_code
                == 422
            )
            assert client.post("/api/v1/meals", json=body).status_code == 422
    finally:
        app.dependency_overrides.clear()
