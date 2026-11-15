"""Validated API transport models for chart-ready forecast responses."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class HistoryPoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    minute: int = Field(le=0)
    value_mg_dl: float = Field(ge=20, le=600, allow_inf_nan=False)


class ForecastBandPoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    minute: int = Field(gt=0)
    q10_mg_dl: float = Field(ge=-99999, le=99999, allow_inf_nan=False)
    q50_mg_dl: float = Field(gt=0, le=1000, allow_inf_nan=False)
    q90_mg_dl: float = Field(ge=-99999, le=99999, allow_inf_nan=False)

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


class ModelProvenance(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    model_key: Literal["chronos", "lightgbm"]
    model_id: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    feature_version: str = Field(min_length=1)
    bundle_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    calibration_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    history_samples: Literal[24, 288]
    interval_kind: Literal["model_quantiles", "calibrated_marginal_80"]
    inputs: tuple[str, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def identity_is_complete(self):
        if self.model_key == "lightgbm" and (
            not self.bundle_sha256
            or not self.calibration_sha256
            or self.history_samples != 288
            or self.interval_kind != "calibrated_marginal_80"
            or not self.model_version.endswith(self.bundle_sha256)
        ):
            raise ValueError("complete LightGBM bundle/calibration identity required")
        if self.model_key == "chronos" and (
            self.history_samples != 24 or self.interval_kind != "model_quantiles"
        ):
            raise ValueError("Chronos capability identity differs")
        return self


class ForecastResponse(BaseModel):
    """Relative-time response safe for the synthetic Milestone 1 chart."""

    model_config = ConfigDict(frozen=True)

    schema_version: Literal["1.0", "2.0"] = "1.0"
    data_mode: Literal["synthetic_demo", "simulated"]
    model_id: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    context_configuration: Literal[
        "cgm_only", "cgm_insulin", "cgm_insulin_carbohydrates", "cgm_insulin_nutrition"
    ]
    unit: Literal["mg/dL"] = "mg/dL"
    history: tuple[HistoryPoint, ...] = Field(min_length=2)
    forecast: tuple[ForecastBandPoint, ...] = Field(min_length=1)
    summary: ForecastSummary
    notice: str = Field(min_length=1)
    interval_kind: Literal["model_quantiles", "calibrated_marginal_80"] = "model_quantiles"
    provenance: ModelProvenance | None = None

    @model_validator(mode="after")
    def validate_series(self) -> ForecastResponse:
        if self.schema_version == "1.0":
            if (
                any(
                    not 20 <= v <= 600
                    for p in self.forecast
                    for v in (p.q10_mg_dl, p.q50_mg_dl, p.q90_mg_dl)
                )
                or self.interval_kind != "model_quantiles"
            ):
                raise ValueError("legacy forecast bounds must remain within 20–600")
        elif self.provenance is None or (self.model_id, self.model_version, self.interval_kind) != (
            self.provenance.model_id,
            self.provenance.model_version,
            self.provenance.interval_kind,
        ):
            raise ValueError("version 2 requires matching full model provenance")
        elif (
            tuple(p.minute for p in self.forecast) != tuple(range(5, 121, 5))
            or tuple(p.minute for p in self.history)
            != tuple(range(-5 * (self.provenance.history_samples - 1), 1, 5))
            or self.context_configuration
            != (
                "cgm_insulin_carbohydrates"
                if self.provenance.model_key == "lightgbm"
                else "cgm_insulin_nutrition"
            )
        ):
            raise ValueError("version 2 model history, forecast grid or context differs")
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
