"""Forecast transport routes."""

from fastapi import APIRouter
from fastapi import Depends
from pydantic import BaseModel
from uuid import UUID

from backend.app.db.client import UserSession, user_session
from backend.app.services.inference.application import forecast_meal
from backend.app.db.client import database_call
from backend.app.models.forecast import ForecastBandPoint, ForecastSummary, HistoryPoint
from datetime import datetime
from urllib.parse import quote
from fastapi import HTTPException

from backend.app.models.forecast import ForecastResponse
from backend.app.services.inference.demo import build_demo_forecast


router = APIRouter(prefix="/api/v1/forecasts", tags=["forecasts"])


@router.get("/demo", response_model=ForecastResponse)
def demo_forecast() -> ForecastResponse:
    """Return a deterministic synthetic chart fixture; no dataset or model load occurs."""

    return build_demo_forecast()


class ForecastCreate(BaseModel):
    meal_id: UUID
    idempotency_key: UUID


@router.post("")
def create_forecast(body: ForecastCreate, session: UserSession = Depends(user_session)):
    return forecast_meal(session, body.meal_id, body.idempotency_key)


@router.get("/{forecast_id}")
def saved_forecast(forecast_id: UUID, session: UserSession = Depends(user_session)):
    records = database_call(session, f"forecasts?id=eq.{forecast_id}&select=*")
    if not records:
        raise HTTPException(404, "Forecast not found")
    record = records[0]
    origin = datetime.fromisoformat(record["forecast_origin"].replace("Z", "+00:00"))
    rows = database_call(session, f"forecast_points?forecast_id=eq.{forecast_id}&order=forecast_at")
    points = tuple(
        ForecastBandPoint(
            minute=round(
                (
                    datetime.fromisoformat(p["forecast_at"].replace("Z", "+00:00")) - origin
                ).total_seconds()
                / 60
            ),
            q10_mg_dl=p["q10"],
            q50_mg_dl=p["q50"],
            q90_mg_dl=p["q90"],
        )
        for p in rows
    )
    history_rows = database_call(
        session,
        "cgm_readings?source=eq.simulation&recorded_at=lte."
        + quote(record["forecast_origin"], safe="")
        + "&order=recorded_at.desc&limit=24",
    )
    history = tuple(
        HistoryPoint(
            minute=round(
                (
                    datetime.fromisoformat(p["recorded_at"].replace("Z", "+00:00")) - origin
                ).total_seconds()
                / 60
            ),
            value_mg_dl=p["glucose_mg_dl"],
        )
        for p in reversed(history_rows)
    )
    median = {point.minute: point.q50_mg_dl for point in points}
    forecast = ForecastResponse(
        data_mode="simulated",
        model_id=record["model_id"],
        model_version=record["model_version"],
        context_configuration=record["context_config"],
        history=history,
        forecast=points,
        summary=ForecastSummary(
            minute_30_mg_dl=median[30], minute_60_mg_dl=median[60], minute_120_mg_dl=median[120]
        ),
        notice="Simulated research context. Forecasts are uncertain, not clinical guidance or insulin-dosing advice.",
    )
    return {"forecast_id": str(forecast_id), "forecast": forecast.model_dump(mode="json")}
