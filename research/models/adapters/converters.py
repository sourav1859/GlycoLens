"""Convert audited dataset windows into leakage-resistant forecast examples."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from enum import Enum

from research.datasets.t1d_uom import MealWindow
from research.models.adapters.base import (
    CovariateSeries,
    ForecastExample,
    ForecastRequest,
    ForecastTarget,
    ForecastValidationError,
    TimePoint,
)


class ContextConfiguration(str, Enum):
    """Implemented Milestone 1 input ablations."""

    CGM_ONLY = "cgm_only"
    CGM_INSULIN = "cgm_insulin"
    CGM_INSULIN_NUTRITION = "cgm_insulin_nutrition"


def _insulin_covariates(window: MealWindow) -> tuple[CovariateSeries, ...]:
    grouped: dict[str, dict[datetime, float]] = defaultdict(lambda: defaultdict(float))
    for event in window.insulin_history:
        grouped[event.event_type][event.timestamp] += event.dose

    series: list[CovariateSeries] = []
    for event_type in sorted(grouped):
        points = tuple(
            TimePoint(timestamp=timestamp, value=value)
            for timestamp, value in sorted(grouped[event_type].items())
        )
        series.append(
            CovariateSeries(
                name=f"insulin_{event_type}",
                points=points,
                unit="dataset_source_value",
            )
        )
    return tuple(series)


def _nutrition_covariates(window: MealWindow) -> tuple[CovariateSeries, ...]:
    meal = window.meal
    return tuple(
        CovariateSeries(
            name=name,
            points=(TimePoint(timestamp=meal.timestamp, value=value),),
            unit="g",
        )
        for name, value in (
            ("meal_carbohydrates", meal.carbs_g),
            ("meal_protein", meal.protein_g),
            ("meal_fat", meal.fat_g),
            ("meal_fiber", meal.fiber_g),
        )
    )


def meal_window_to_forecast_example(
    window: MealWindow,
    *,
    context: ContextConfiguration = ContextConfiguration.CGM_INSULIN_NUTRITION,
    quantiles: tuple[float, ...] = (0.1, 0.5, 0.9),
) -> ForecastExample:
    """Build model input and held-out truth as separate immutable objects."""

    if not isinstance(window, MealWindow):
        raise TypeError("window must be a MealWindow")
    try:
        context_configuration = ContextConfiguration(context)
    except ValueError as error:
        raise ForecastValidationError(f"unsupported context configuration: {context}") from error

    expected_history = window.config.history_minutes // window.config.frequency_minutes
    expected_target = window.config.horizon_minutes // window.config.frequency_minutes
    if len(window.cgm_history) != expected_history:
        raise ForecastValidationError("meal window history length does not match its configuration")
    if len(window.target_cgm) != expected_target:
        raise ForecastValidationError("meal window target length does not match its configuration")

    history = tuple(
        TimePoint(timestamp=point.timestamp, value=point.glucose_mg_dl)
        for point in window.cgm_history
    )
    target = ForecastTarget(
        points=tuple(
            TimePoint(timestamp=point.timestamp, value=point.glucose_mg_dl)
            for point in window.target_cgm
        )
    )

    past_covariates: tuple[CovariateSeries, ...] = ()
    known_covariates: tuple[CovariateSeries, ...] = ()
    if context_configuration in (
        ContextConfiguration.CGM_INSULIN,
        ContextConfiguration.CGM_INSULIN_NUTRITION,
    ):
        if not window.insulin_history:
            raise ForecastValidationError(
                "insulin context was requested but the meal window contains no insulin events"
            )
        past_covariates = _insulin_covariates(window)
    if context_configuration is ContextConfiguration.CGM_INSULIN_NUTRITION:
        known_covariates = _nutrition_covariates(window)

    request = ForecastRequest(
        target_history=history,
        prediction_length=expected_target,
        frequency_minutes=window.config.frequency_minutes,
        quantiles=quantiles,
        past_covariates=past_covariates,
        known_covariates=known_covariates,
    )
    return ForecastExample(request=request, target=target)
