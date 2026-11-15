"""Forecast transport routes."""

from fastapi import APIRouter, Query
from fastapi import Depends
from pydantic import BaseModel, ConfigDict
from pydantic import Field
from uuid import UUID
from typing import Literal

from backend.app.db.client import UserSession, user_session
from backend.app.services.inference.application import forecast_meal
from backend.app.db.client import database_call
from fastapi import HTTPException

from backend.app.models.forecast import ForecastResponse
from backend.app.services.inference.demo import build_demo_forecast
from backend.app.services.inference.scenarios import scenario, actuals


router = APIRouter(prefix="/api/v1/forecasts", tags=["forecasts"])


@router.get("/models")
def available_models(session: UserSession = Depends(user_session)):
    from backend.app.services.inference.registry import model_capabilities

    return {"models": model_capabilities(), "default": "chronos"}


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
    model_key: Literal["chronos", "lightgbm"] = "chronos"


@router.post("")
def create_forecast(body: ForecastCreate, session: UserSession = Depends(user_session)):
    return forecast_meal(session, body.meal_id, body.idempotency_key, body.model_key)


@router.get("")
def list_forecasts(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0, le=10000),
    workspace: Literal["personal", "simulation"] = "personal",
    source_session_id: UUID | None = None,
    session: UserSession = Depends(user_session),
):
    from backend.app.services.workspaces import owned_source

    if workspace == "personal":
        if source_session_id:
            raise HTTPException(422, "Personal forecasts cannot use a virtual source")
        return {
            "forecasts": [],
            "source_session_id": None,
            "workspace": workspace,
            "has_more": False,
        }
    source = owned_source(session, source_session_id)["id"] if source_session_id else None
    partition = "eq." + str(source) if source else "not.is.null"
    rows = database_call(
        session,
        f"forecasts?source_session_id={partition}&select=id,meal_id,meal_revision,model_id,context_config,forecast_origin,created_at,source_session_id&order=created_at.desc,id.desc&limit={limit + 1}&offset={offset}",
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
        "workspace": "simulation" if record["source_session_id"] else "legacy_unclassified",
        "forecast_origin": record["forecast_origin"],
        "forecast": forecast.model_dump(mode="json"),
    }
