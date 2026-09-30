from __future__ import annotations

import asyncio
from collections.abc import Mapping, Sequence

import httpx

from backend.app.main import app


def _request(method: str, path: str, *, headers: dict[str, str] | None = None) -> httpx.Response:
    async def send() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.request(method, path, headers=headers)

    return asyncio.run(send())


def _all_keys(value: object) -> set[str]:
    if isinstance(value, Mapping):
        return set(value) | {key for item in value.values() for key in _all_keys(item)}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return {key for item in value for key in _all_keys(item)}
    return set()


def test_health_endpoint() -> None:
    response = _request("GET", "/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "glycolens-api"}


def test_demo_forecast_is_chart_ready_and_explicitly_synthetic() -> None:
    response = _request("GET", "/api/v1/forecasts/demo")

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema_version"] == "1.0"
    assert payload["data_mode"] == "synthetic_demo"
    assert payload["context_configuration"] == "cgm_only"
    assert payload["unit"] == "mg/dL"
    assert len(payload["history"]) == 24
    assert len(payload["forecast"]) == 24
    assert payload["history"][-1]["minute"] == 0
    assert payload["forecast"][0]["minute"] == 5
    assert payload["forecast"][-1]["minute"] == 120
    assert payload["summary"]["minute_30_mg_dl"] == payload["forecast"][5]["q50_mg_dl"]
    assert payload["summary"]["minute_60_mg_dl"] == payload["forecast"][11]["q50_mg_dl"]
    assert payload["summary"]["minute_120_mg_dl"] == payload["forecast"][23]["q50_mg_dl"]
    assert all(
        point["q10_mg_dl"] <= point["q50_mg_dl"] <= point["q90_mg_dl"]
        for point in payload["forecast"]
    )
    assert "Synthetic demonstration only" in payload["notice"]
    assert "insulin dosing" in payload["notice"]


def test_demo_response_excludes_identifiers_and_absolute_times() -> None:
    payload = _request("GET", "/api/v1/forecasts/demo").json()
    keys = _all_keys(payload)

    assert keys.isdisjoint(
        {
            "participant_id",
            "user_id",
            "meal_id",
            "timestamp",
            "context_start",
            "context_end",
            "dataset_root",
        }
    )
    assert not any("2026-" in str(value) for value in payload.values())


def test_openapi_documents_demo_contract() -> None:
    response = _request("GET", "/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert "/api/v1/forecasts/demo" in schema["paths"]
    assert "ForecastResponse" in schema["components"]["schemas"]


def test_cors_allows_local_frontend_and_rejects_unknown_origin() -> None:
    allowed = _request(
        "OPTIONS",
        "/api/v1/forecasts/demo",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:3000"

    denied = _request(
        "OPTIONS",
        "/api/v1/forecasts/demo",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert denied.status_code == 400
    assert "access-control-allow-origin" not in denied.headers
