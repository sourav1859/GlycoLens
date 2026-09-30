"""Forecast transport routes."""

from fastapi import APIRouter

from backend.app.models.forecast import ForecastResponse
from backend.app.services.inference.demo import build_demo_forecast


router = APIRouter(prefix="/api/v1/forecasts", tags=["forecasts"])


@router.get("/demo", response_model=ForecastResponse)
def demo_forecast() -> ForecastResponse:
    """Return a deterministic synthetic chart fixture; no dataset or model load occurs."""

    return build_demo_forecast()
