"""Common forecasting adapter contract and implementations."""

from research.models.adapters.base import (
    CovariateSeries,
    ForecastExample,
    ForecastModelAdapter,
    ForecastRequest,
    ForecastResult,
    ForecastTarget,
    ForecastValidationError,
    ModelInferenceError,
    ModelLoadError,
    ModelNotLoadedError,
    QuantileForecast,
    TimePoint,
)
from research.models.adapters.chronos2 import (
    CHRONOS2_MODEL_ID,
    CHRONOS2_MODEL_REVISION,
    CHRONOS_FORECASTING_VERSION,
    Chronos2ForecastAdapter,
)
from research.models.adapters.converters import (
    ContextConfiguration,
    meal_window_to_forecast_example,
)
from research.models.adapters.persistence import PersistenceForecastAdapter

__all__ = [
    "CHRONOS2_MODEL_ID",
    "CHRONOS2_MODEL_REVISION",
    "CHRONOS_FORECASTING_VERSION",
    "Chronos2ForecastAdapter",
    "ContextConfiguration",
    "CovariateSeries",
    "ForecastExample",
    "ForecastModelAdapter",
    "ForecastRequest",
    "ForecastResult",
    "ForecastTarget",
    "ForecastValidationError",
    "ModelInferenceError",
    "ModelLoadError",
    "ModelNotLoadedError",
    "PersistenceForecastAdapter",
    "QuantileForecast",
    "TimePoint",
    "meal_window_to_forecast_example",
]
