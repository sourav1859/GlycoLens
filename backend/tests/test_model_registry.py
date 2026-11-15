import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from backend.app.services.inference.registry import resolve_model, model_capabilities
from backend.app.models.forecast import ForecastResponse
from backend.app.services.inference.demo import build_demo_forecast


def test_default_and_unknown_model_selection_are_explicit():
    assert resolve_model().key == "chronos"
    with pytest.raises(HTTPException) as error:
        resolve_model("user.module:/tmp/weights")
    assert error.value.status_code == 422


def test_unavailable_lightgbm_has_no_fallback(monkeypatch):
    monkeypatch.setenv("GLYCOLENS_LIGHTGBM_ENABLED", "false")
    with pytest.raises(HTTPException) as error:
        resolve_model("lightgbm")
    assert error.value.status_code == 503
    assert model_capabilities()[1]["available"] is False


def test_v2_signed_interval_roundtrip_but_v1_keeps_its_bounds():
    payload = build_demo_forecast().model_dump(mode="json")
    payload["forecast"][0]["q10_mg_dl"] = -5
    with pytest.raises(ValidationError):
        ForecastResponse.model_validate(payload)
    payload.update(
        schema_version="2.0",
        interval_kind="calibrated_marginal_80",
        provenance=dict(
            model_key="lightgbm",
            model_id="metabonet_lightgbm_direct",
            model_version="metabonet_tabular_v1:" + "a" * 64,
            feature_version="metabonet_tabular_v1",
            bundle_sha256="a" * 64,
            calibration_sha256="b" * 64,
            history_samples=288,
            interval_kind="calibrated_marginal_80",
            inputs=["current carbohydrates"],
        ),
    )
    payload["model_id"] = payload["provenance"]["model_id"]
    payload["model_version"] = payload["provenance"]["model_version"]
    payload["history"] = [dict(minute=-5 * i, value_mg_dl=120) for i in range(287, -1, -1)]
    payload["context_configuration"] = "cgm_insulin_carbohydrates"
    assert ForecastResponse.model_validate(payload).forecast[0].q10_mg_dl == -5
    payload["provenance"]["bundle_sha256"] = None
    with pytest.raises(ValidationError):
        ForecastResponse.model_validate(payload)
