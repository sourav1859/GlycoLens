"""Model-independent, leakage-resistant forecasting contracts."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from math import isclose, isfinite
from typing import Iterable


DEFAULT_QUANTILES = (0.1, 0.5, 0.9)


class ForecastValidationError(ValueError):
    """Raised when a forecast request, target, or result violates the contract."""


class ModelNotLoadedError(RuntimeError):
    """Raised when prediction is attempted before adapter initialization."""


class ModelLoadError(RuntimeError):
    """Raised when a forecasting backend cannot be initialized safely."""


class ModelInferenceError(RuntimeError):
    """Raised when a forecasting backend fails or returns an invalid payload."""


def _tuple_copy(values: Iterable[object], field_name: str) -> tuple[object, ...]:
    if isinstance(values, (str, bytes)):
        raise ForecastValidationError(f"{field_name} must be a sequence, not text")
    try:
        return tuple(values)
    except TypeError as error:
        raise ForecastValidationError(f"{field_name} must be iterable") from error


def _require_positive_integer(value: object, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ForecastValidationError(f"{field_name} must be a positive integer")
    return value


def _timestamp_awareness(timestamp: datetime) -> bool:
    return timestamp.tzinfo is not None and timestamp.utcoffset() is not None


def _validate_timestamps(
    timestamps: tuple[datetime, ...],
    field_name: str,
    *,
    allow_single: bool = True,
) -> None:
    if not timestamps:
        raise ForecastValidationError(f"{field_name} must not be empty")
    if not allow_single and len(timestamps) < 2:
        raise ForecastValidationError(f"{field_name} must contain at least two timestamps")
    if any(not isinstance(timestamp, datetime) for timestamp in timestamps):
        raise ForecastValidationError(f"{field_name} must contain datetime values")
    awareness = _timestamp_awareness(timestamps[0])
    if any(_timestamp_awareness(timestamp) != awareness for timestamp in timestamps[1:]):
        raise ForecastValidationError(f"{field_name} cannot mix naive and timezone-aware values")
    if any(current <= previous for previous, current in zip(timestamps, timestamps[1:])):
        raise ForecastValidationError(f"{field_name} must be strictly increasing")


def _validate_regular_frequency(
    timestamps: tuple[datetime, ...], frequency_minutes: int, field_name: str
) -> None:
    expected = timedelta(minutes=frequency_minutes)
    if any(current - previous != expected for previous, current in zip(timestamps, timestamps[1:])):
        raise ForecastValidationError(
            f"{field_name} must use the configured {frequency_minutes}-minute frequency"
        )


@dataclass(frozen=True)
class TimePoint:
    """One finite numeric observation at a specific time."""

    timestamp: datetime
    value: float

    def __post_init__(self) -> None:
        if not isinstance(self.timestamp, datetime):
            raise ForecastValidationError("time-point timestamp must be a datetime")
        if isinstance(self.value, bool):
            raise ForecastValidationError("time-point value must be numeric")
        try:
            normalized = float(self.value)
        except (TypeError, ValueError) as error:
            raise ForecastValidationError("time-point value must be numeric") from error
        if not isfinite(normalized):
            raise ForecastValidationError("time-point value must be finite")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True)
class CovariateSeries:
    """A named numeric covariate series with immutable timestamped points."""

    name: str
    points: tuple[TimePoint, ...]
    unit: str = ""

    def __post_init__(self) -> None:
        normalized_name = self.name.strip() if isinstance(self.name, str) else ""
        if not normalized_name:
            raise ForecastValidationError("covariate name must not be blank")
        normalized_points = _tuple_copy(self.points, "covariate points")
        if any(not isinstance(point, TimePoint) for point in normalized_points):
            raise ForecastValidationError("covariate points must contain TimePoint values")
        _validate_timestamps(
            tuple(point.timestamp for point in normalized_points), "covariate points"
        )
        normalized_unit = self.unit.strip() if isinstance(self.unit, str) else ""
        object.__setattr__(self, "name", normalized_name)
        object.__setattr__(self, "points", normalized_points)
        object.__setattr__(self, "unit", normalized_unit)


@dataclass(frozen=True)
class ForecastRequest:
    """Only information available to a model at forecast creation time."""

    target_history: tuple[TimePoint, ...]
    prediction_length: int = 24
    frequency_minutes: int = 5
    quantiles: tuple[float, ...] = DEFAULT_QUANTILES
    past_covariates: tuple[CovariateSeries, ...] = field(default_factory=tuple)
    known_covariates: tuple[CovariateSeries, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        history = _tuple_copy(self.target_history, "target_history")
        if any(not isinstance(point, TimePoint) for point in history):
            raise ForecastValidationError("target_history must contain TimePoint values")
        timestamps = tuple(point.timestamp for point in history)
        _validate_timestamps(timestamps, "target_history")

        prediction_length = _require_positive_integer(self.prediction_length, "prediction_length")
        frequency_minutes = _require_positive_integer(self.frequency_minutes, "frequency_minutes")
        _validate_regular_frequency(timestamps, frequency_minutes, "target_history")

        quantiles = _tuple_copy(self.quantiles, "quantiles")
        try:
            normalized_quantiles = tuple(float(quantile) for quantile in quantiles)
        except (TypeError, ValueError) as error:
            raise ForecastValidationError("quantiles must be numeric") from error
        if not normalized_quantiles:
            raise ForecastValidationError("quantiles must not be empty")
        if any(not isfinite(quantile) or not 0 < quantile < 1 for quantile in normalized_quantiles):
            raise ForecastValidationError(
                "quantiles must be finite values strictly between 0 and 1"
            )
        if tuple(sorted(set(normalized_quantiles))) != normalized_quantiles:
            raise ForecastValidationError("quantiles must be unique and strictly increasing")
        if 0.5 not in normalized_quantiles:
            raise ForecastValidationError("quantiles must include 0.5 for the median")

        past_covariates = _tuple_copy(self.past_covariates, "past_covariates")
        known_covariates = _tuple_copy(self.known_covariates, "known_covariates")
        all_covariates = past_covariates + known_covariates
        if any(not isinstance(series, CovariateSeries) for series in all_covariates):
            raise ForecastValidationError("covariates must contain CovariateSeries values")
        names = tuple(series.name for series in all_covariates)
        if len(names) != len(set(names)):
            raise ForecastValidationError("covariate names must be unique across the request")

        context_end = timestamps[-1]
        forecast_end = context_end + timedelta(minutes=frequency_minutes * prediction_length)
        context_awareness = _timestamp_awareness(context_end)
        if any(
            _timestamp_awareness(point.timestamp) != context_awareness
            for series in all_covariates
            for point in series.points
        ):
            raise ForecastValidationError(
                "covariate timestamps must match target_history timestamp awareness"
            )
        if any(
            point.timestamp > context_end for series in past_covariates for point in series.points
        ):
            raise ForecastValidationError("past covariates cannot contain future values")
        if any(
            point.timestamp < context_end or point.timestamp > forecast_end
            for series in known_covariates
            for point in series.points
        ):
            raise ForecastValidationError(
                "known covariates must fall between context end and forecast end"
            )

        object.__setattr__(self, "target_history", history)
        object.__setattr__(self, "prediction_length", prediction_length)
        object.__setattr__(self, "frequency_minutes", frequency_minutes)
        object.__setattr__(self, "quantiles", normalized_quantiles)
        object.__setattr__(self, "past_covariates", past_covariates)
        object.__setattr__(self, "known_covariates", known_covariates)

    @property
    def context_start(self) -> datetime:
        return self.target_history[0].timestamp

    @property
    def context_end(self) -> datetime:
        return self.target_history[-1].timestamp

    @property
    def forecast_timestamps(self) -> tuple[datetime, ...]:
        step = timedelta(minutes=self.frequency_minutes)
        return tuple(
            self.context_end + step * offset for offset in range(1, self.prediction_length + 1)
        )


@dataclass(frozen=True)
class ForecastTarget:
    """Held-out truth used only after model prediction for evaluation."""

    points: tuple[TimePoint, ...]

    def __post_init__(self) -> None:
        points = _tuple_copy(self.points, "forecast target")
        if any(not isinstance(point, TimePoint) for point in points):
            raise ForecastValidationError("forecast target must contain TimePoint values")
        _validate_timestamps(tuple(point.timestamp for point in points), "forecast target")
        object.__setattr__(self, "points", points)


@dataclass(frozen=True)
class ForecastExample:
    """Evaluation-only pairing that keeps model input and future truth separate."""

    request: ForecastRequest
    target: ForecastTarget

    def __post_init__(self) -> None:
        if not isinstance(self.request, ForecastRequest):
            raise ForecastValidationError("example request must be a ForecastRequest")
        if not isinstance(self.target, ForecastTarget):
            raise ForecastValidationError("example target must be a ForecastTarget")
        if len(self.target.points) != self.request.prediction_length:
            raise ForecastValidationError("target length must equal request prediction_length")
        target_timestamps = tuple(point.timestamp for point in self.target.points)
        if target_timestamps != self.request.forecast_timestamps:
            raise ForecastValidationError(
                "target timestamps must match the request forecast grid exactly"
            )


@dataclass(frozen=True)
class QuantileForecast:
    """Forecast values for one requested probability level."""

    level: float
    values: tuple[float, ...]

    def __post_init__(self) -> None:
        if isinstance(self.level, bool):
            raise ForecastValidationError("quantile level must be numeric")
        try:
            level = float(self.level)
        except (TypeError, ValueError) as error:
            raise ForecastValidationError("quantile level must be numeric") from error
        if not isfinite(level) or not 0 < level < 1:
            raise ForecastValidationError("quantile level must be strictly between 0 and 1")
        try:
            values = tuple(float(value) for value in _tuple_copy(self.values, "quantile values"))
        except (TypeError, ValueError) as error:
            raise ForecastValidationError("quantile values must be numeric") from error
        if not values or any(not isfinite(value) for value in values):
            raise ForecastValidationError("quantile values must be non-empty and finite")
        object.__setattr__(self, "level", level)
        object.__setattr__(self, "values", values)


@dataclass(frozen=True)
class ForecastResult:
    """Validated, model-independent probabilistic forecast output."""

    model_id: str
    model_version: str
    context_start: datetime
    context_end: datetime
    forecast_timestamps: tuple[datetime, ...]
    median: tuple[float, ...]
    quantiles: tuple[QuantileForecast, ...]
    latency_ms: float
    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        model_id = self.model_id.strip() if isinstance(self.model_id, str) else ""
        model_version = self.model_version.strip() if isinstance(self.model_version, str) else ""
        if not model_id or not model_version:
            raise ForecastValidationError("model_id and model_version must not be blank")
        if not isinstance(self.context_start, datetime) or not isinstance(
            self.context_end, datetime
        ):
            raise ForecastValidationError("forecast context bounds must be datetimes")
        if _timestamp_awareness(self.context_start) != _timestamp_awareness(self.context_end):
            raise ForecastValidationError("forecast context cannot mix timestamp awareness")
        if self.context_end < self.context_start:
            raise ForecastValidationError("context_end cannot precede context_start")

        timestamps = _tuple_copy(self.forecast_timestamps, "forecast_timestamps")
        if any(not isinstance(timestamp, datetime) for timestamp in timestamps):
            raise ForecastValidationError("forecast_timestamps must contain datetime values")
        _validate_timestamps(timestamps, "forecast_timestamps")
        if _timestamp_awareness(timestamps[0]) != _timestamp_awareness(self.context_end):
            raise ForecastValidationError(
                "forecast timestamps must match context timestamp awareness"
            )
        if timestamps[0] <= self.context_end:
            raise ForecastValidationError("forecast timestamps must be strictly after context_end")
        if len(timestamps) > 2:
            forecast_step = timestamps[1] - timestamps[0]
            if any(
                current - previous != forecast_step
                for previous, current in zip(timestamps[1:], timestamps[2:])
            ):
                raise ForecastValidationError("forecast timestamps must use a regular frequency")

        try:
            median = tuple(float(value) for value in _tuple_copy(self.median, "median"))
        except (TypeError, ValueError) as error:
            raise ForecastValidationError("median values must be numeric") from error
        if len(median) != len(timestamps) or any(not isfinite(value) for value in median):
            raise ForecastValidationError(
                "median must contain one finite value per forecast timestamp"
            )

        quantiles = _tuple_copy(self.quantiles, "result quantiles")
        if not quantiles or any(not isinstance(item, QuantileForecast) for item in quantiles):
            raise ForecastValidationError("result quantiles must contain QuantileForecast values")
        levels = tuple(item.level for item in quantiles)
        if tuple(sorted(set(levels))) != levels:
            raise ForecastValidationError("result quantiles must be unique and strictly increasing")
        if any(len(item.values) != len(timestamps) for item in quantiles):
            raise ForecastValidationError("each quantile must match the forecast timestamp length")
        for index in range(len(timestamps)):
            values_at_time = tuple(item.values[index] for item in quantiles)
            if any(
                current < previous for previous, current in zip(values_at_time, values_at_time[1:])
            ):
                raise ForecastValidationError("quantile forecasts must not cross")
        if 0.5 in levels:
            median_quantile = quantiles[levels.index(0.5)].values
            if any(
                not isclose(expected, observed, rel_tol=1e-9, abs_tol=1e-9)
                for expected, observed in zip(median, median_quantile)
            ):
                raise ForecastValidationError("median must match the 0.5 quantile")

        if isinstance(self.latency_ms, bool):
            raise ForecastValidationError("latency_ms must be numeric")
        try:
            latency_ms = float(self.latency_ms)
        except (TypeError, ValueError) as error:
            raise ForecastValidationError("latency_ms must be numeric") from error
        if not isfinite(latency_ms) or latency_ms < 0:
            raise ForecastValidationError("latency_ms must be finite and non-negative")

        metadata = _tuple_copy(self.metadata, "metadata")
        normalized_metadata: list[tuple[str, str]] = []
        for item in metadata:
            if not isinstance(item, tuple) or len(item) != 2:
                raise ForecastValidationError("metadata entries must be key/value tuples")
            key, value = item
            normalized_key = key.strip() if isinstance(key, str) else ""
            if not normalized_key or not isinstance(value, str):
                raise ForecastValidationError(
                    "metadata keys must be non-blank and values must be text"
                )
            normalized_metadata.append((normalized_key, value))
        metadata_keys = tuple(key for key, _ in normalized_metadata)
        if len(metadata_keys) != len(set(metadata_keys)):
            raise ForecastValidationError("metadata keys must be unique")

        object.__setattr__(self, "model_id", model_id)
        object.__setattr__(self, "model_version", model_version)
        object.__setattr__(self, "forecast_timestamps", timestamps)
        object.__setattr__(self, "median", median)
        object.__setattr__(self, "quantiles", quantiles)
        object.__setattr__(self, "latency_ms", latency_ms)
        object.__setattr__(self, "metadata", tuple(normalized_metadata))

    def quantile_values(self, level: float) -> tuple[float, ...]:
        for forecast in self.quantiles:
            if forecast.level == level:
                return forecast.values
        raise KeyError(f"quantile not present: {level}")


class ForecastModelAdapter(ABC):
    """Common boundary implemented by every GlycoLens forecasting model."""

    model_id: str
    model_version: str

    @abstractmethod
    def load(self) -> None:
        """Initialize model resources. Implementations must be idempotent."""

    @abstractmethod
    def predict(self, request: ForecastRequest) -> ForecastResult:
        """Return a validated forecast using only the supplied request."""
