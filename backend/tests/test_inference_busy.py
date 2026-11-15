"""Both public inference services must share capacity and release it on failure."""

from concurrent.futures import ThreadPoolExecutor
from threading import Event
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.db.client import UserSession
from backend.app.services.inference import application, scenarios
from backend.app.services.inference.registry import ModelSpec
from backend.tests.test_m2_context import fixture


def test_scenario_is_busy_during_forecast_and_timeout_releases_capacity(monkeypatch):
    origin, meal, cgm, insulin = fixture()
    mid = uuid4()
    meal.update(id=str(mid), revision=1, source_session_id=str(uuid4()), state="planned")

    def rows(session, path):
        if path.startswith("meals?"):
            return [meal]
        if path.startswith("source_sessions?"):
            return [{"metadata": {"inference_context_end": origin.isoformat()}}]
        if path.startswith("cgm_readings?"):
            return cgm
        if path.startswith("insulin_events?"):
            return insulin
        if path.startswith("forecasts?"):
            return []
        raise AssertionError("Unexpected context query")

    monkeypatch.setattr(application, "database_call", rows)
    persisted = Mock()
    monkeypatch.setattr(application, "trusted_call", persisted)
    started, release = Event(), Event()

    def predict(self, request):
        started.set()
        assert release.wait(5)
        raise TimeoutError("controlled inference failure")

    monkeypatch.setattr(ModelSpec, "predict", predict)
    owner = UserSession("synthetic", str(uuid4()))
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(application.forecast_meal, owner, mid, uuid4())
        try:
            assert started.wait(2)
            with pytest.raises(HTTPException) as error:
                scenarios.scenario(owner, uuid4(), 1, uuid4())
            assert error.value.status_code == 429
        finally:
            release.set()
        with pytest.raises(HTTPException) as error:
            future.result(timeout=5)
        assert error.value.status_code == 503
    persisted.assert_not_called()
    assert application.MODEL_LOCK.acquire(blocking=False)
    application.MODEL_LOCK.release()


def test_model_capabilities_require_verified_authentication():
    with TestClient(app) as api:
        assert api.get("/api/v1/forecasts/models").status_code == 401
