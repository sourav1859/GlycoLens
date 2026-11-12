"""GlycoLens FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.forecasts import router as forecasts_router
from backend.app.api.meals import router as meals_router
from backend.app.api.foods import router as foods_router
from backend.app.api.simulation import router as simulation_router
from backend.app.api.account import router as account_router
from backend.app.api.nutrition import router as nutrition_router
from backend.app.api.notifications import router as notifications_router
from backend.app.api.privacy import router as privacy_router
from backend.app.core.settings import load_local_configuration
from backend.app.core.config import cors_origins
from backend.app.models.forecast import HealthResponse
from backend.app.services.account_deletion import deletion_cleanup_lifespan


load_local_configuration()
app = FastAPI(
    lifespan=deletion_cleanup_lifespan,
    title="GlycoLens API",
    version="0.1.0",
    description="Research and education API; not for treatment or insulin-dosing decisions.",
)


@app.exception_handler(RequestValidationError)
async def redact_deletion_validation(request, exc):
    if request.method == "DELETE" and request.url.path == "/api/v1/me":
        return JSONResponse(status_code=422, content={"detail": "Review the password and deletion confirmation fields"})
    return await request_validation_exception_handler(request, exc)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(cors_origins()),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Accept", "Content-Type", "Authorization"],
)
app.include_router(forecasts_router)
app.include_router(meals_router)
app.include_router(foods_router)
app.include_router(simulation_router)
app.include_router(account_router)
app.include_router(nutrition_router)
app.include_router(notifications_router)
app.include_router(privacy_router)


@app.middleware("http")
async def private_application_responses(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/v1/"):
        response.headers["Cache-Control"] = "private, no-store"
        response.headers["Vary"] = "Authorization, Origin"
    return response


@app.get("/health", response_model=HealthResponse, tags=["operations"])
def health() -> HealthResponse:
    return HealthResponse()
