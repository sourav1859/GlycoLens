from dataclasses import replace
from datetime import timedelta

import pytest

from research.evaluation.metrics import score_forecast
from research.evaluation.runner import comparison_summary, evaluate
from research.models.adapters import ContextConfiguration, PersistenceForecastAdapter
from research.models.adapters.converters import meal_window_to_forecast_example
from tests.research.test_m2_protocol import shifted_window


def test_metrics_use_held_out_truth_and_deterministic_baseline_has_no_fake_interval():
    window = shifted_window(0)
    example = meal_window_to_forecast_example(window, context=ContextConfiguration.CGM_ONLY)
    model = PersistenceForecastAdapter()
    model.load()
    result = model.predict(example.request)
    scores = score_forecast(example, result)
    expected = sum(abs(p.value - result.median[0]) for p in example.target.points) / 24
    assert scores["mae"] == pytest.approx(expected)
    assert "interval_coverage" not in scores
    assert scores["absolute_error_120"] == pytest.approx(
        abs(example.target.points[-1].value - result.median[-1])
    )
    with pytest.raises(ValueError, match="grid"):
        score_forecast(
            example,
            replace(
                result,
                forecast_timestamps=tuple(
                    t + timedelta(minutes=5) for t in result.forecast_timestamps
                ),
            ),
        )


def test_failed_events_are_counted_and_comparisons_use_common_successes():
    windows = tuple(shifted_window(i) for i in range(3))
    model = PersistenceForecastAdapter()
    model.load()
    rows = evaluate(windows, model, ContextConfiguration.CGM_ONLY)
    failed = (replace(rows[0], metrics={}, error_type="ModelInferenceError", wall_ms=None),) + rows[
        1:
    ]
    summary = comparison_summary({"a": rows, "b": failed})
    assert summary["common_success_event_count"] == 2
    assert summary["runs"]["b"]["failure_rate"] == pytest.approx(1 / 3)
    with pytest.raises(ValueError, match="same requested"):
        comparison_summary({"a": rows, "b": rows[1:]})
