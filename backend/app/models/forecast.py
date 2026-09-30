"""Validated API transport models for chart-ready forecast responses."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class HistoryPoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    minute: int = Field(le=0)
    value_mg_dl: float = Field(ge=20, le=600)


class ForecastBandPoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    minute: int = Field(gt=0)
    q10_mg_dl: float = Field(ge=20, le=600)
    q50_mg_dl: float = Field(ge=20, le=600)
    q90_mg_dl: float = Field(ge=20, le=600)

    @model_validator(mode="after")
    def validate_quantile_order(self) -> ForecastBandPoint:
        if not self.q10_mg_dl <= self.q50_mg_dl <= self.q90_mg_dl:
            raise ValueError("forecast quantiles must be ordered")
        return self


class ForecastSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    minute_30_mg_dl: float
    minute_60_mg_dl: float
    minute_120_mg_dl: float


class ForecastResponse(BaseModel):
    """Relative-time response safe for the synthetic Milestone 1 chart."""

    model_config = ConfigDict(frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    data_mode: Literal["synthetic_demo"]
    model_id: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    context_configuration: Literal["cgm_only"]
    unit: Literal["mg/dL"] = "mg/dL"
    history: tuple[HistoryPoint, ...] = Field(min_length=2)
    forecast: tuple[ForecastBandPoint, ...] = Field(min_length=1)
    summary: ForecastSummary
    notice: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_series(self) -> ForecastResponse:
        history_minutes = tuple(point.minute for point in self.history)
        forecast_minutes = tuple(point.minute for point in self.forecast)
        if any(
            current <= previous for previous, current in zip(history_minutes, history_minutes[1:])
        ):
            raise ValueError("history minutes must be strictly increasing")
        if any(
            current <= previous for previous, current in zip(forecast_minutes, forecast_minutes[1:])
        ):
            raise ValueError("forecast minutes must be strictly increasing")

        lookup = {point.minute: point.q50_mg_dl for point in self.forecast}
        expected_minutes = (30, 60, 120)
        if any(minute not in lookup for minute in expected_minutes):
            raise ValueError("forecast must contain 30, 60, and 120 minute values")
        observed = (
            self.summary.minute_30_mg_dl,
            self.summary.minute_60_mg_dl,
            self.summary.minute_120_mg_dl,
        )
        expected = tuple(lookup[minute] for minute in expected_minutes)
        if observed != expected:
            raise ValueError("summary values must match the forecast median")
        return self


class HealthResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: Literal["ok"] = "ok"
    service: Literal["glycolens-api"] = "glycolens-api"
