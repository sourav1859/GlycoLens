from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from backend.app.db.client import UserSession, user_session
from backend.app.main import app


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/nutrition?day=0001-01-01",
        "/api/v1/home?day=9999-12-31",
        "/api/v1/meals?day=0001-01-01",
        "/api/v1/meals?slot=unsafe",
        "/api/v1/forecasts?limit=101",
    ],
)
def test_invalid_ranges_never_reach_storage(path):
    app.dependency_overrides[user_session] = lambda: UserSession(
        "synthetic", "10000000-0000-4000-8000-000000000001"
    )
    try:
        with (
            TestClient(app) as client,
            patch(
                "backend.app.db.client.httpx.request",
                side_effect=AssertionError("must not reach storage"),
            ),
        ):
            assert client.get(path).status_code == 422
    finally:
        app.dependency_overrides.clear()
