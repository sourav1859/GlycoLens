"""Frozen-input portion comparisons and genuinely available virtual observations."""

from datetime import datetime, timedelta
import math
from urllib.parse import quote
from uuid import UUID
from fastapi import HTTPException
from backend.app.db.client import database_call
from backend.app.db.trusted import trusted_call
from backend.app.services.inference import application as inference
from backend.app.services.inference.demo import forecast_to_response
from backend.app.services.inference.registry import resolve_model

FIELDS = ("calories", "carbs_g", "protein_g", "fat_g", "fiber_g")


def scaled_meal(meal, multiplier):
    if not math.isfinite(multiplier) or not 0.1 <= multiplier <= 2:
        raise ValueError("Choose a portion between 10% and 200%")
    return {
        **meal,
        **{f: None if meal.get(f) is None else float(meal[f]) * multiplier for f in FIELDS},
    }


def actual_metrics(points, actual):
    if (
        len(points) != 24
        or len(actual) != 24
        or any(not math.isfinite(v) or not 20 <= v <= 600 for v in actual)
    ):
        raise ValueError("24 valid actual samples required")
    return {
        "mae_mg_dl": sum(abs(p["q50_mg_dl"] - v) for p, v in zip(points, actual)) / 24,
        "interval_coverage": sum(
            p["q10_mg_dl"] <= v <= p["q90_mg_dl"] for p, v in zip(points, actual)
        )
        / 24,
        "sample_count": 24,
    }


def owned_forecast(session, forecast_id):
    rows = database_call(session, f"forecasts?id=eq.{forecast_id}&select=*")
    if not rows:
        raise HTTPException(404, "Forecast not found")
    if not rows[0].get("input_snapshot"):
        raise HTTPException(409, "Frozen input required")
    return rows[0]


def scenario(session, forecast_id, multiplier, key):
    if not inference.MODEL_LOCK.acquire(blocking=False):
        raise HTTPException(429, "Model is busy; retry shortly")
    try:
        original = owned_forecast(session, forecast_id)
        prior = database_call(session, f"portion_scenarios?idempotency_key=eq.{key}&select=*")
        if prior:
            if (
                prior[0]["forecast_id"] != str(forecast_id)
                or float(prior[0]["multiplier"]) != multiplier
            ):
                raise HTTPException(409, "Request key reused")
            return prior[0]
        prior_count = database_call(
            session, f"portion_scenarios?forecast_id=eq.{forecast_id}&select=id&limit=11"
        )
        if len(prior_count) >= 10:
            raise HTTPException(429, "Scenario limit reached for this forecast")
        frozen = original["input_snapshot"]
        identity = frozen.get("model_identity")
        spec = resolve_model(identity["model_key"] if identity else "chronos", expected=identity)
        request = inference.build_model_request(
            spec,
            scaled_meal(frozen["meal"], multiplier),
            frozen["history"],
            frozen["insulin"],
            frozen.get("source_metadata", {}),
        )
        result = spec.predict(request)
        if (
            result.model_id != original["model_id"]
            or result.model_version != original["model_version"]
        ):
            raise HTTPException(
                409,
                "The saved forecast uses a different model version; comparisons require identical models",
            )
        response = forecast_to_response(
            request,
            result,
            data_mode="simulated",
            context_configuration=original["context_config"],
            provenance=spec.identity,
        )
        saved = trusted_call(
            session,
            "rpc/app_save_scenario",
            payload={
                "p_forecast": str(forecast_id),
                "p_multiplier": multiplier,
                "p_key": str(key),
                "p_response": response.model_dump(mode="json"),
            },
        )
        return {
            "id": saved,
            "forecast_id": str(forecast_id),
            "multiplier": multiplier,
            "response": response.model_dump(mode="json"),
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            503, "Scenario unavailable; no substitute prediction was produced"
        ) from None
    finally:
        inference.MODEL_LOCK.release()


def actuals(session, forecast_id, *, save=False):
    original = owned_forecast(session, forecast_id)
    source = UUID(original["source_session_id"])
    origin = datetime.fromisoformat(original["forecast_origin"].replace("Z", "+00:00"))
    end = origin + timedelta(hours=2)
    sources = database_call(session, f"source_sessions?id=eq.{source}&select=clock_at")
    if not sources or datetime.fromisoformat(sources[0]["clock_at"].replace("Z", "+00:00")) < end:
        return {
            "available": False,
            "reason": "Two hours of genuine source observations are not available yet",
        }
    readings = database_call(
        session,
        f"cgm_readings?source_session_id=eq.{source}&recorded_at=gt.{quote(origin.isoformat(), safe='')}&recorded_at=lte.{quote(end.isoformat(), safe='')}&order=recorded_at&select=recorded_at,glucose_mg_dl&limit=25",
    )
    expected = [origin + timedelta(minutes=m) for m in range(5, 121, 5)]
    if [
        datetime.fromisoformat(r["recorded_at"].replace("Z", "+00:00")) for r in readings
    ] != expected:
        return {"available": False, "reason": "The source has incomplete post-origin coverage"}
    values = [float(r["glucose_mg_dl"]) for r in readings]
    metrics = actual_metrics(original["input_snapshot"]["response"]["forecast"], values)
    result = {
        "available": True,
        "values_mg_dl": values,
        "metrics": metrics,
        "available_at": end.isoformat(),
    }
    if save:
        trusted_call(
            session,
            "rpc/app_store_actuals",
            payload={
                "p_forecast": str(forecast_id),
                "p_values": {
                    "actual_30": values[5],
                    "actual_60": values[11],
                    "actual_120": values[23],
                    "available_at": end.isoformat(),
                    "metrics": metrics,
                },
            },
        )
    return result
