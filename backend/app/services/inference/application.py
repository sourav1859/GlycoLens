"""Validated past-only application context and process-cached selected model."""

from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock
from urllib.parse import quote
from uuid import UUID

from fastapi import HTTPException

from backend.app.db.client import UserSession, database_call
from backend.app.db.trusted import trusted_call
from backend.app.services.inference.demo import forecast_to_response
from research.models.adapters import (
    Chronos2ForecastAdapter,
    ContextConfiguration,
    ForecastRequest,
    TimePoint,
)
from research.models.adapters.base import CovariateSeries
from research.models.adapters.covariates import FEATURE_VERSION


ROOT = Path(__file__).resolve().parents[4]
MODEL_LOCK = Lock()
MODEL = None
SELECTED_CONTEXT = ContextConfiguration.CGM_INSULIN_NUTRITION


def build_request(meal: dict, cgm: list[dict], insulin: list[dict]) -> ForecastRequest:
    origin = datetime.fromisoformat(meal["recorded_at"].replace("Z", "+00:00"))
    if origin.tzinfo is None:
        raise HTTPException(422, "Forecast origin must be timezone-aware")
    by_time = {datetime.fromisoformat(p["recorded_at"].replace("Z", "+00:00")): p for p in cgm}
    grid = tuple(origin - timedelta(minutes=5 * index) for index in range(23, -1, -1))
    if any(at not in by_time for at in grid):
        raise HTTPException(422, "24 regular CGM samples are required at the simulated origin")
    history = tuple(TimePoint(at, float(by_time[at]["glucose_mg_dl"])) for at in grid)
    if any(by_time[at].get("source") != "simulation" for at in grid):
        raise HTTPException(422, "This prototype accepts reviewed simulated context only")
    groups = {}
    for event in insulin:
        at = datetime.fromisoformat(event["recorded_at"].replace("Z", "+00:00"))
        if not origin - timedelta(hours=6) <= at <= origin:
            continue
        name = (
            "insulin_bolus"
            if event["event_type"] == "bolus"
            else "insulin_basal_kind_" + (event.get("insulin_kind") or "unknown")
        )
        values = groups.setdefault(name, {})
        amount = float(event["units"])
        if name == "insulin_bolus":
            values[at] = values.get(at, 0.0) + amount
        elif at in values and values[at] != amount:
            raise HTTPException(422, "Conflicting simulated basal context")
        else:
            values[at] = amount
    if not groups:
        raise HTTPException(422, "Recent simulated insulin context is unavailable")
    covariates = tuple(
        CovariateSeries(
            name,
            tuple(TimePoint(at, amount) for at, amount in sorted(points.items())),
            "U" if name == "insulin_bolus" else "source_U_or_U_per_hour",
        )
        for name, points in sorted(groups.items())
    )
    nutrients = []
    for field, channel in (
        ("carbs_g", "carbohydrates"),
        ("protein_g", "protein"),
        ("fat_g", "fat"),
        ("fiber_g", "fiber"),
    ):
        if meal.get(field) is None:
            raise HTTPException(422, "Confirm complete meal nutrition before forecasting")
        nutrients.append(
            CovariateSeries("meal_" + channel, (TimePoint(origin, float(meal[field])),), "g")
        )
    return ForecastRequest(history, past_covariates=covariates, known_covariates=tuple(nutrients))


def forecast_meal(session: UserSession, meal_id: UUID, key: UUID):
    global MODEL
    if not MODEL_LOCK.acquire(blocking=False):
        raise HTTPException(429, "Model is busy; retry shortly")
    try:
        rows = database_call(session, f"meals?id=eq.{meal_id}&select=*")
        if not rows:
            raise HTTPException(404, "Meal not found in your demo session")
        meal = rows[0]
        if not meal.get("source_session_id") or meal.get("state") == "cancelled":
            raise HTTPException(422, "Choose a source context and a reviewed active meal")
        source = str(UUID(meal["source_session_id"]))
        origin = meal["recorded_at"]
        sources = database_call(session, f"source_sessions?id=eq.{source}&select=metadata")
        coverage = sources[0]["metadata"].get("inference_context_end") if sources else None
        if not coverage or datetime.fromisoformat(
            origin.replace("Z", "+00:00")
        ) > datetime.fromisoformat(coverage.replace("Z", "+00:00")):
            raise HTTPException(
                422, "Insulin context does not cover this origin; prepare a new reviewed source"
            )
        existing = database_call(
            session, f"forecasts?idempotency_key=eq.{key}&select=id,meal_id,meal_revision"
        )
        if existing:
            if (
                existing[0]["meal_id"] != str(meal_id)
                or existing[0]["meal_revision"] != meal["revision"]
            ):
                raise HTTPException(409, "This request key belongs to another meal")
            return {"forecast_id": existing[0]["id"], "reused": True}
        cgm = database_call(
            session,
            "cgm_readings?recorded_at=lte."
            + quote(origin, safe="")
            + f"&source=eq.simulation&source_session_id=eq.{source}&order=recorded_at.desc&limit=24",
        )
        insulin = database_call(
            session,
            "insulin_events?recorded_at=lte."
            + quote(origin, safe="")
            + f"&source=eq.simulation&source_session_id=eq.{source}&order=recorded_at&limit=600",
        )
        request = build_request(meal, cgm, insulin)
        if MODEL is None:
            model = Chronos2ForecastAdapter(cache_dir=ROOT / "artifacts/models/huggingface")
            model.load()
            MODEL = model
        result = MODEL.predict(request)
        response = forecast_to_response(
            request, result, data_mode="simulated", context_configuration=SELECTED_CONTEXT.value
        )
        forecast_id = trusted_call(
            session,
            "rpc/app_commit_forecast",
            method="POST",
            payload={
                "p_meal": str(meal_id),
                "p_revision": meal["revision"],
                "p_key": str(key),
                "p_model": result.model_id,
                "p_version": result.model_version,
                "p_context": SELECTED_CONTEXT.value,
                "p_origin": origin,
                "p_latency": result.latency_ms,
                "p_provenance": {"source": "simulated", "feature_version": FEATURE_VERSION},
                "p_points": [p.model_dump() for p in response.forecast],
                "p_input": {
                    "meal": meal,
                    "history": cgm,
                    "insulin": insulin,
                    "source_session_id": source,
                    "response": response.model_dump(mode="json"),
                },
            },
        )
        return {
            "forecast_id": forecast_id,
            "reused": False,
            "forecast": response.model_dump(mode="json"),
        }
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            503, "Forecast unavailable; validated model output is required"
        ) from None
    finally:
        MODEL_LOCK.release()
