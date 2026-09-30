from __future__ import annotations

from dataclasses import fields
from datetime import datetime, timedelta, timezone
from math import inf, nan

import pytest

from research.datasets.t1d_uom import (
    GlucosePoint,
    InsulinEvent,
    MealEvent,
    MealWindow,
    WindowConfig,
)
from research.models.adapters import (
    ContextConfiguration,
    CovariateSeries,
    ForecastModelAdapter,
    ForecastRequest,
    ForecastResult,
    ForecastValidationError,
    ModelNotLoadedError,
    PersistenceForecastAdapter,
    QuantileForecast,
    TimePoint,
    meal_window_to_forecast_example,
)
from research.pipelines.run_persistence_baseline import public_summary


MEAL_TIME = datetime(2026, 1, 15, 12, 0)


def _history(*, count: int = 24, aware: bool = False) -> list[TimePoint]:
    context_end = MEAL_TIME.replace(tzinfo=timezone.utc) if aware else MEAL_TIME
    return [
        TimePoint(
            timestamp=context_end - timedelta(minutes=5 * (count - index - 1)),
            value=100.0 + index,
        )
        for index in range(count)
    ]


def _request(**overrides: object) -> ForecastRequest:
    values: dict[str, object] = {
        "target_history": tuple(_history()),
        "prediction_length": 24,
        "frequency_minutes": 5,
        "quantiles": (0.1, 0.5, 0.9),
    }
    values.update(overrides)
    return ForecastRequest(**values)  # type: ignore[arg-type]


def _meal_window(
    *,
    future_insulin: bool = False,
    history_count: int = 24,
    include_insulin: bool = True,
) -> MealWindow:
    history = tuple(
        GlucosePoint(
            timestamp=MEAL_TIME - timedelta(minutes=5 * (history_count - index - 1)),
            glucose_mmol_l=5.5 + index * 0.05,
        )
        for index in range(history_count)
    )
    target = tuple(
        GlucosePoint(
            timestamp=MEAL_TIME + timedelta(minutes=5 * (index + 1)),
            glucose_mmol_l=6.7 + index * 0.05,
        )
        for index in range(24)
    )
    insulin = ()
    if include_insulin:
        insulin = (
            InsulinEvent(MEAL_TIME - timedelta(minutes=60), "basal", 0.8, "synthetic"),
            InsulinEvent(MEAL_TIME - timedelta(minutes=20), "bolus", 2.0, "synthetic"),
            InsulinEvent(MEAL_TIME - timedelta(minutes=20), "bolus", 1.0, "synthetic"),
        )
    if future_insulin:
        insulin += (InsulinEvent(MEAL_TIME + timedelta(minutes=5), "bolus", 1.0),)
    return MealWindow(
        participant_id="SYNTHETIC-001",
        meal=MealEvent(
            timestamp=MEAL_TIME,
            meal_type="Lunch",
            meal_tag="synthetic meal",
            carbs_g=45.0,
            protein_g=20.0,
            fat_g=15.0,
            fiber_g=7.0,
        ),
        cgm_history=history,
        insulin_history=insulin,
        target_cgm=target,
        config=WindowConfig(),
    )


def _valid_result(**overrides: object) -> ForecastResult:
    request = _request(prediction_length=3)
    median = (120.0, 121.0, 122.0)
    values: dict[str, object] = {
        "model_id": "test-model",
        "model_version": "1",
        "context_start": request.context_start,
        "context_end": request.context_end,
        "forecast_timestamps": request.forecast_timestamps,
        "median": median,
        "quantiles": (
            QuantileForecast(0.1, (110.0, 111.0, 112.0)),
            QuantileForecast(0.5, median),
            QuantileForecast(0.9, (130.0, 131.0, 132.0)),
        ),
        "latency_ms": 1.0,
    }
    values.update(overrides)
    return ForecastResult(**values)  # type: ignore[arg-type]


def test_persistence_requires_explicit_load_and_load_is_idempotent() -> None:
    adapter = PersistenceForecastAdapter()

    with pytest.raises(ModelNotLoadedError, match="loaded before prediction"):
        adapter.predict(_request())

    adapter.load()
    adapter.load()
    assert adapter.is_loaded


def test_persistence_returns_24_ordered_future_points_and_requested_quantiles() -> None:
    request = _request()
    adapter = PersistenceForecastAdapter()
    adapter.load()

    result = adapter.predict(request)

    assert len(result.forecast_timestamps) == 24
    assert result.forecast_timestamps == request.forecast_timestamps
    assert result.forecast_timestamps[0] == request.context_end + timedelta(minutes=5)
    assert result.forecast_timestamps[-1] == request.context_end + timedelta(minutes=120)
    assert tuple(item.level for item in result.quantiles) == request.quantiles
    assert result.latency_ms >= 0


def test_persistence_repeats_last_value_with_equal_non_crossing_quantiles() -> None:
    request = _request()
    adapter = PersistenceForecastAdapter()
    adapter.load()

    first = adapter.predict(request)
    second = adapter.predict(request)
    expected = (request.target_history[-1].value,) * request.prediction_length

    assert first.median == expected == second.median
    assert first.metadata == second.metadata
    assert all(quantile.values == expected for quantile in first.quantiles)
    assert first.quantile_values(0.1) == first.quantile_values(0.5) == first.quantile_values(0.9)


@pytest.mark.parametrize("value", [nan, inf, -inf])
def test_non_finite_history_values_are_rejected(value: float) -> None:
    with pytest.raises(ForecastValidationError, match="finite"):
        TimePoint(timestamp=MEAL_TIME, value=value)


def test_empty_irregular_and_mixed_awareness_histories_are_rejected() -> None:
    with pytest.raises(ForecastValidationError, match="must not be empty"):
        _request(target_history=())

    irregular = _history()
    irregular[-1] = TimePoint(timestamp=MEAL_TIME + timedelta(minutes=1), value=123.0)
    with pytest.raises(ForecastValidationError, match="configured 5-minute frequency"):
        _request(target_history=irregular)

    mixed = _history()
    mixed[-1] = TimePoint(timestamp=MEAL_TIME.replace(tzinfo=timezone.utc), value=123.0)
    with pytest.raises(ForecastValidationError, match="cannot mix"):
        _request(target_history=mixed)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"prediction_length": 0}, "positive integer"),
        ({"frequency_minutes": -5}, "positive integer"),
        ({"quantiles": ()}, "must not be empty"),
        ({"quantiles": (0.5, 0.1, 0.9)}, "strictly increasing"),
        ({"quantiles": (0.1, 0.9)}, "include 0.5"),
        ({"quantiles": (0.1, 0.5, 1.0)}, "between 0 and 1"),
    ],
)
def test_invalid_request_configuration_is_rejected(
    overrides: dict[str, object], message: str
) -> None:
    with pytest.raises(ForecastValidationError, match=message):
        _request(**overrides)


def test_covariate_temporal_boundaries_and_names_are_enforced() -> None:
    future_past = CovariateSeries(
        "insulin_bolus",
        (TimePoint(MEAL_TIME + timedelta(minutes=5), 1.0),),
    )
    with pytest.raises(ForecastValidationError, match="past covariates cannot contain future"):
        _request(past_covariates=(future_past,))

    historical_known = CovariateSeries(
        "meal_carbohydrates",
        (TimePoint(MEAL_TIME - timedelta(minutes=5), 45.0),),
    )
    with pytest.raises(ForecastValidationError, match="known covariates must fall"):
        _request(known_covariates=(historical_known,))

    duplicate_a = CovariateSeries("duplicate", (TimePoint(MEAL_TIME, 1.0),))
    duplicate_b = CovariateSeries("duplicate", (TimePoint(MEAL_TIME, 2.0),))
    with pytest.raises(ForecastValidationError, match="names must be unique"):
        _request(past_covariates=(duplicate_a,), known_covariates=(duplicate_b,))

    aware_covariate = CovariateSeries(
        "aware_covariate",
        (TimePoint(MEAL_TIME.replace(tzinfo=timezone.utc), 1.0),),
    )
    with pytest.raises(ForecastValidationError, match="timestamp awareness"):
        _request(past_covariates=(aware_covariate,))


def test_request_defensively_copies_mutable_sequences() -> None:
    mutable_history = _history()
    mutable_quantiles = [0.1, 0.5, 0.9]
    request = ForecastRequest(
        target_history=mutable_history,  # type: ignore[arg-type]
        quantiles=mutable_quantiles,  # type: ignore[arg-type]
    )

    mutable_history.append(TimePoint(MEAL_TIME + timedelta(minutes=5), 200.0))
    mutable_quantiles.append(0.95)

    assert len(request.target_history) == 24
    assert request.quantiles == (0.1, 0.5, 0.9)


def test_result_rejects_shape_errors_non_finite_values_and_crossing_quantiles() -> None:
    with pytest.raises(ForecastValidationError, match="one finite value"):
        _valid_result(median=(120.0, 121.0))

    with pytest.raises(ForecastValidationError, match="finite"):
        QuantileForecast(0.1, (100.0, nan, 102.0))

    crossing = (
        QuantileForecast(0.1, (125.0, 111.0, 112.0)),
        QuantileForecast(0.5, (120.0, 121.0, 122.0)),
        QuantileForecast(0.9, (130.0, 131.0, 132.0)),
    )
    with pytest.raises(ForecastValidationError, match="must not cross"):
        _valid_result(quantiles=crossing)

    irregular_timestamps = (
        MEAL_TIME + timedelta(minutes=5),
        MEAL_TIME + timedelta(minutes=10),
        MEAL_TIME + timedelta(minutes=20),
    )
    with pytest.raises(ForecastValidationError, match="regular frequency"):
        _valid_result(forecast_timestamps=irregular_timestamps)


def test_converter_keeps_future_truth_out_of_model_request() -> None:
    example = meal_window_to_forecast_example(_meal_window())

    request_field_names = {field.name for field in fields(example.request)}
    assert "target" not in request_field_names
    assert "target_cgm" not in request_field_names
    assert "participant_id" not in request_field_names
    assert len(example.request.target_history) == 24
    assert len(example.target.points) == 24
    assert all(
        point.timestamp <= example.request.context_end for point in example.request.target_history
    )
    assert all(point.timestamp > example.request.context_end for point in example.target.points)


class _SpyAdapter(ForecastModelAdapter):
    model_id = "spy"
    model_version = "1"

    def __init__(self) -> None:
        self.seen_request: ForecastRequest | None = None

    def load(self) -> None:
        return None

    def predict(self, request: ForecastRequest) -> ForecastResult:
        self.seen_request = request
        baseline = PersistenceForecastAdapter()
        baseline.load()
        return baseline.predict(request)


def test_spy_adapter_receives_only_request_not_held_out_target() -> None:
    example = meal_window_to_forecast_example(_meal_window())
    adapter = _SpyAdapter()

    adapter.predict(example.request)

    assert adapter.seen_request is example.request
    assert not hasattr(adapter.seen_request, "target")
    assert not hasattr(adapter.seen_request, "target_cgm")


def test_converter_supports_context_ablation_and_aggregates_same_time_insulin() -> None:
    window = _meal_window()

    cgm_only = meal_window_to_forecast_example(
        window, context=ContextConfiguration.CGM_ONLY
    ).request
    insulin = meal_window_to_forecast_example(
        window, context=ContextConfiguration.CGM_INSULIN
    ).request
    full = meal_window_to_forecast_example(
        window, context=ContextConfiguration.CGM_INSULIN_NUTRITION
    ).request

    assert cgm_only.past_covariates == ()
    assert cgm_only.known_covariates == ()
    assert {series.name for series in insulin.past_covariates} == {
        "insulin_basal",
        "insulin_bolus",
    }
    bolus = next(series for series in insulin.past_covariates if series.name == "insulin_bolus")
    assert len(bolus.points) == 1
    assert bolus.points[0].value == 3.0
    assert {series.name for series in full.known_covariates} == {
        "meal_carbohydrates",
        "meal_protein",
        "meal_fat",
        "meal_fiber",
    }


def test_converter_rejects_wrong_window_shape_and_future_insulin() -> None:
    with pytest.raises(ForecastValidationError, match="history length"):
        meal_window_to_forecast_example(_meal_window(history_count=23))

    with pytest.raises(ForecastValidationError, match="past covariates cannot contain future"):
        meal_window_to_forecast_example(_meal_window(future_insulin=True))

    with pytest.raises(ForecastValidationError, match="contains no insulin"):
        meal_window_to_forecast_example(_meal_window(include_insulin=False))

    cgm_only = meal_window_to_forecast_example(
        _meal_window(include_insulin=False), context=ContextConfiguration.CGM_ONLY
    )
    assert cgm_only.request.past_covariates == ()


def test_converter_does_not_mutate_source_window() -> None:
    window = _meal_window()
    original_history = window.cgm_history
    original_insulin = window.insulin_history
    original_target = window.target_cgm

    meal_window_to_forecast_example(window)

    assert window.cgm_history is original_history
    assert window.insulin_history is original_insulin
    assert window.target_cgm is original_target


def test_public_smoke_summary_excludes_identifiers_and_row_values() -> None:
    context = ContextConfiguration.CGM_INSULIN_NUTRITION
    example = meal_window_to_forecast_example(_meal_window(), context=context)
    adapter = PersistenceForecastAdapter()
    adapter.load()

    summary = public_summary(example, adapter.predict(example.request), context)

    assert summary["history_points"] == 24
    assert summary["forecast_points"] == 24
    assert summary["held_out_target_points"] == 24
    assert summary["target_withheld_from_request"] is True
    assert not any(
        forbidden in key
        for key in summary
        for forbidden in ("participant", "glucose", "value", "timestamp")
    )
