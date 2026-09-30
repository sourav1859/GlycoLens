from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from research.models.adapters import (
    ForecastExample,
    ForecastRequest,
    ForecastResult,
    ForecastTarget,
    QuantileForecast,
    TimePoint,
)
from research.pipelines.render_chronos2_forecast import (
    DEFAULT_OUTPUT,
    FORECAST_ARTIFACT_ROOT,
    _output_path,
)
from research.visualization import save_forecast_plot


def _example_and_result() -> tuple[ForecastExample, ForecastResult]:
    context_end = datetime(2026, 1, 1, 12, 0)
    request = ForecastRequest(
        target_history=tuple(
            TimePoint(context_end - timedelta(minutes=5 * (23 - index)), 100 + index)
            for index in range(24)
        )
    )
    target = ForecastTarget(
        tuple(
            TimePoint(context_end + timedelta(minutes=5 * (index + 1)), 130 + index)
            for index in range(24)
        )
    )
    median = tuple(125 + index for index in range(24))
    result = ForecastResult(
        model_id="synthetic-test",
        model_version="1",
        context_start=request.context_start,
        context_end=request.context_end,
        forecast_timestamps=request.forecast_timestamps,
        median=median,
        quantiles=(
            QuantileForecast(0.1, tuple(value - 10 for value in median)),
            QuantileForecast(0.5, median),
            QuantileForecast(0.9, tuple(value + 10 for value in median)),
        ),
        latency_ms=1,
    )
    return ForecastExample(request, target), result


def test_plot_writes_nonempty_png_and_returns_privacy_summary(tmp_path: Path) -> None:
    example, result = _example_and_result()
    output = tmp_path / "forecast.png"

    summary = save_forecast_plot(example, result, output, include_held_out_target=True)

    assert output.read_bytes().startswith(b"\x89PNG")
    assert output.stat().st_size > 10_000
    assert summary == {
        "history_points": 24,
        "forecast_points": 24,
        "held_out_target_included": True,
        "uses_relative_minutes": True,
        "contains_participant_identifier": False,
        "contains_absolute_timestamp": False,
    }


def test_plot_rejects_a_result_on_a_different_time_grid(tmp_path: Path) -> None:
    example, result = _example_and_result()
    shifted = ForecastResult(
        model_id=result.model_id,
        model_version=result.model_version,
        context_start=result.context_start,
        context_end=result.context_end,
        forecast_timestamps=tuple(
            timestamp + timedelta(minutes=5) for timestamp in result.forecast_timestamps
        ),
        median=result.median,
        quantiles=result.quantiles,
        latency_ms=result.latency_ms,
    )

    with pytest.raises(ValueError, match="does not match"):
        save_forecast_plot(example, shifted, tmp_path / "bad.png")


def test_cli_output_is_constrained_to_ignored_forecast_artifacts(tmp_path: Path) -> None:
    assert _output_path(None) == DEFAULT_OUTPUT.resolve()
    assert DEFAULT_OUTPUT.resolve().is_relative_to(FORECAST_ARTIFACT_ROOT.resolve())

    with pytest.raises(SystemExit, match="must remain under"):
        _output_path(str(tmp_path / "outside.png"))
    with pytest.raises(SystemExit, match=".png extension"):
        _output_path(str(FORECAST_ARTIFACT_ROOT / "forecast.svg"))
