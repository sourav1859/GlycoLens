"""Forecast transport routes."""

from fastapi import APIRouter, Query
from fastapi import Depends
from pydantic import BaseModel, ConfigDict
from pydantic import Field
from uuid import UUID

from backend.app.db.client import UserSession, user_session
from backend.app.services.inference.application import forecast_meal
from backend.app.db.client import database_call
from fastapi import HTTPException

from backend.app.models.forecast import ForecastResponse
from backend.app.services.inference.demo import build_demo_forecast
from backend.app.services.inference.scenarios import scenario, actuals


router = APIRouter(prefix="/api/v1/forecasts", tags=["forecasts"])


class ScenarioCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    multiplier: float = Field(ge=0.1, le=2, allow_inf_nan=False)
    idempotency_key: UUID


@router.post("/{forecast_id}/scenarios")
def create_scenario(
    forecast_id: UUID, body: ScenarioCreate, session: UserSession = Depends(user_session)
):
    return scenario(session, forecast_id, body.multiplier, body.idempotency_key)


@router.get("/{forecast_id}/scenarios")
def list_scenarios(forecast_id: UUID, session: UserSession = Depends(user_session)):
    return {
        "scenarios": database_call(
            session,
            f"portion_scenarios?forecast_id=eq.{forecast_id}&select=id,multiplier,response,created_at&order=created_at&limit=10",
        )
    }


@router.get("/{forecast_id}/actuals")
def get_actuals(forecast_id: UUID, session: UserSession = Depends(user_session)):
    return actuals(session, forecast_id)


@router.post("/{forecast_id}/actuals")
def save_actuals(forecast_id: UUID, session: UserSession = Depends(user_session)):
    return actuals(session, forecast_id, save=True)


@router.get("/demo", response_model=ForecastResponse)
def demo_forecast() -> ForecastResponse:
    """Return a deterministic synthetic chart fixture; no dataset or model load occurs."""

    return build_demo_forecast()


class ForecastCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    meal_id: UUID
    idempotency_key: UUID


@router.post("")
def create_forecast(body: ForecastCreate, session: UserSession = Depends(user_session)):
    return forecast_meal(session, body.meal_id, body.idempotency_key)


@router.get("")
def list_forecasts(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0, le=10000),
    session: UserSession = Depends(user_session),
):
    prefs = database_call(session, "user_preferences?select=source_session_id&limit=1")
    source = prefs[0].get("source_session_id") if prefs else None
    if not source:
        return {"forecasts": [], "source_session_id": None, "has_more": False}
    rows = database_call(
        session,
        f"forecasts?source_session_id=eq.{UUID(source)}&select=id,meal_id,meal_revision,model_id,context_config,forecast_origin,created_at&order=created_at.desc,id.desc&limit={limit + 1}&offset={offset}",
    )
    return {"forecasts": rows[:limit], "source_session_id": source, "has_more": len(rows) > limit}


@router.get("/{forecast_id}")
def saved_forecast(forecast_id: UUID, session: UserSession = Depends(user_session)):
    records = database_call(session, f"forecasts?id=eq.{forecast_id}&select=*")
    if not records:
        raise HTTPException(404, "Forecast not found")
    record = records[0]
    snapshot = record.get("input_snapshot")
    if not isinstance(snapshot, dict) or not snapshot.get("response"):
        raise HTTPException(
            409, "This legacy forecast has no frozen context; create a new forecast"
        )
    try:
        forecast = ForecastResponse.model_validate(snapshot["response"])
    except ValueError:
        raise HTTPException(503, "Saved forecast failed validation") from None
    return {
        "forecast_id": str(forecast_id),
        "meal_id": record["meal_id"],
        "meal_revision": record["meal_revision"],
        "source_session_id": record["source_session_id"],
        "forecast_origin": record["forecast_origin"],
        "forecast": forecast.model_dump(mode="json"),
    }
