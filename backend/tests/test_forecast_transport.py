from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.app.core.config import DEFAULT_CORS_ORIGINS, cors_origins
from backend.app.models.forecast import ForecastBandPoint, ForecastResponse
from backend.app.services.inference.demo import build_demo_forecast


def test_demo_builder_maps_canonical_contract_to_relative_time() -> None:
    response = build_demo_forecast()

    assert isinstance(response, ForecastResponse)
    assert tuple(point.minute for point in response.history) == tuple(range(-115, 1, 5))
    assert tuple(point.minute for point in response.forecast) == tuple(range(5, 121, 5))
    assert response.model_id == "synthetic-demo"


def test_forecast_band_rejects_crossing_quantiles() -> None:
    with pytest.raises(ValidationError, match="quantiles must be ordered"):
        ForecastBandPoint(minute=5, q10_mg_dl=130, q50_mg_dl=120, q90_mg_dl=140)


def test_cors_configuration_is_explicit_and_rejects_wildcard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GLYCOLENS_CORS_ORIGINS", raising=False)
    assert cors_origins() == DEFAULT_CORS_ORIGINS

    monkeypatch.setenv(
        "GLYCOLENS_CORS_ORIGINS",
        "https://demo.example, http://localhost:3000/",
    )
    assert cors_origins() == ("https://demo.example", "http://localhost:3000")

    monkeypatch.setenv("GLYCOLENS_CORS_ORIGINS", "*")
    with pytest.raises(ValueError, match="explicit origins"):
        cors_origins()
