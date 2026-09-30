"""GlycoLens FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.forecasts import router as forecasts_router
from backend.app.core.config import cors_origins
from backend.app.models.forecast import HealthResponse


app = FastAPI(
    title="GlycoLens API",
    version="0.1.0",
    description="Research and education API; not for treatment or insulin-dosing decisions.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(cors_origins()),
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Accept", "Content-Type"],
)
app.include_router(forecasts_router)


@app.get("/health", response_model=HealthResponse, tags=["operations"])
def health() -> HealthResponse:
    return HealthResponse()
