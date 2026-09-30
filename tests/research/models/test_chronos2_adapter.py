from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from research.models.adapters import chronos2
from research.models.adapters import (
    CHRONOS2_MODEL_ID,
    CHRONOS2_MODEL_REVISION,
    Chronos2ForecastAdapter,
    CovariateSeries,
    ForecastRequest,
    ForecastValidationError,
    ModelInferenceError,
    ModelLoadError,
    ModelNotLoadedError,
    TimePoint,
)


CONTEXT_END = datetime(2026, 1, 15, 12, 0)


def _request(**overrides: object) -> ForecastRequest:
    values: dict[str, object] = {
        "target_history": tuple(
            TimePoint(
                timestamp=CONTEXT_END - timedelta(minutes=5 * (23 - index)),
                value=100.0 + index,
            )
            for index in range(24)
        ),
        "prediction_length": 24,
        "frequency_minutes": 5,
        "quantiles": (0.1, 0.5, 0.9),
    }
    values.update(overrides)
    return ForecastRequest(**values)  # type: ignore[arg-type]


def _ordered_rows(horizon: int = 24) -> list[list[float]]:
    return [[90.0 + index, 100.0 + index, 110.0 + index] for index in range(horizon)]


class _FakePipeline:
    def __init__(self, rows: list[list[float]] | None = None) -> None:
        self.rows = rows if rows is not None else _ordered_rows()
        self.calls: list[dict[str, object]] = []

    def predict_quantiles(self, **kwargs: object) -> tuple[list[object], list[object]]:
        self.calls.append(kwargs)
        return [[self.rows]], [[[row[1] for row in self.rows]]]


def _adapter(pipeline: object) -> Chronos2ForecastAdapter:
    return Chronos2ForecastAdapter(
        pipeline_loader=lambda _model_id, **_kwargs: pipeline,
        tensor_factory=lambda values: tuple(values),
    )


def test_load_is_idempotent_and_pins_checkpoint_device_and_cache(tmp_path: Path) -> None:
    calls: list[tuple[str, dict[str, object]]] = []

    def loader(model_id: str, **kwargs: object) -> _FakePipeline:
        calls.append((model_id, kwargs))
        return _FakePipeline()

    cache_dir = tmp_path / "models"
    adapter = Chronos2ForecastAdapter(
        cache_dir=cache_dir,
        pipeline_loader=loader,
        tensor_factory=lambda values: tuple(values),
    )

    adapter.load()
    adapter.load()

    assert adapter.is_loaded
    assert calls == [
        (
            CHRONOS2_MODEL_ID,
            {
                "revision": CHRONOS2_MODEL_REVISION,
                "device_map": "cpu",
                "cache_dir": str(cache_dir.resolve()),
            },
        )
    ]


def test_predict_requires_load_and_rejects_non_cpu_configuration() -> None:
    adapter = _adapter(_FakePipeline())
    with pytest.raises(ModelNotLoadedError, match="loaded before prediction"):
        adapter.predict(_request())
    with pytest.raises(ValueError, match="pinned to CPU"):
        Chronos2ForecastAdapter(device_map="cuda")


def test_predict_passes_only_history_horizon_and_quantiles_to_backend() -> None:
    pipeline = _FakePipeline()
    adapter = _adapter(pipeline)
    request = _request()
    adapter.load()

    result = adapter.predict(request)

    assert pipeline.calls == [
        {
            "inputs": [tuple(point.value for point in request.target_history)],
            "prediction_length": 24,
            "quantile_levels": [0.1, 0.5, 0.9],
        }
    ]
    assert result.model_id == CHRONOS2_MODEL_ID
    assert result.model_version == CHRONOS2_MODEL_REVISION
    assert result.forecast_timestamps == request.forecast_timestamps
    assert result.median == tuple(100.0 + index for index in range(24))
    assert result.quantile_values(0.1) == tuple(90.0 + index for index in range(24))
    assert result.quantile_values(0.9) == tuple(110.0 + index for index in range(24))
    assert dict(result.metadata)["context_configuration"] == "cgm_only"
    assert result.latency_ms >= 0


def test_covariates_are_rejected_instead_of_silently_ignored() -> None:
    covariate = CovariateSeries(
        name="insulin_bolus",
        points=(TimePoint(timestamp=CONTEXT_END, value=2.0),),
    )
    adapter = _adapter(_FakePipeline())
    adapter.load()

    with pytest.raises(ForecastValidationError, match="CGM-only"):
        adapter.predict(_request(past_covariates=(covariate,)))


@pytest.mark.parametrize(
    "backend_quantiles",
    [
        [],
        [[_ordered_rows()], [_ordered_rows()]],
        [[[row[:2] for row in _ordered_rows()]]],
        [[_ordered_rows(horizon=23)]],
    ],
)
def test_malformed_backend_shapes_fail_closed(backend_quantiles: object) -> None:
    class MalformedPipeline:
        def predict_quantiles(self, **_kwargs: object) -> tuple[object, list[object]]:
            return backend_quantiles, []

    adapter = _adapter(MalformedPipeline())
    adapter.load()

    with pytest.raises(ModelInferenceError, match="shape contract"):
        adapter.predict(_request())


def test_crossing_quantiles_and_backend_failures_use_safe_adapter_errors() -> None:
    crossing = _ordered_rows()
    crossing[5] = [120.0, 100.0, 110.0]
    adapter = _adapter(_FakePipeline(crossing))
    adapter.load()
    with pytest.raises(ModelInferenceError, match="result contract"):
        adapter.predict(_request())

    class FailingPipeline:
        def predict_quantiles(self, **_kwargs: object) -> None:
            raise RuntimeError("private backend diagnostic")

    failing = _adapter(FailingPipeline())
    failing.load()
    with pytest.raises(ModelInferenceError, match=r"inference failed \(RuntimeError\)") as caught:
        failing.predict(_request())
    assert "private backend diagnostic" not in str(caught.value)


def test_loader_failures_are_wrapped_without_leaking_backend_message() -> None:
    def failing_loader(_model_id: str, **_kwargs: object) -> object:
        raise OSError("private local cache path")

    adapter = Chronos2ForecastAdapter(pipeline_loader=failing_loader)
    with pytest.raises(ModelLoadError, match=r"initialization failed \(OSError\)") as caught:
        adapter.load()
    assert "private local cache path" not in str(caught.value)


def test_default_loader_rejects_unpinned_package_version(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(chronos2, "_package_version", lambda: "unexpected")

    with pytest.raises(ModelLoadError, match="does not match"):
        chronos2._default_pipeline_loader(CHRONOS2_MODEL_ID)


def test_input_conversion_failure_is_wrapped_without_leaking_values() -> None:
    def failing_tensor_factory(_values: list[float]) -> object:
        raise ValueError("private input diagnostic")

    adapter = Chronos2ForecastAdapter(
        pipeline_loader=lambda _model_id, **_kwargs: _FakePipeline(),
        tensor_factory=failing_tensor_factory,
    )
    adapter.load()

    with pytest.raises(
        ModelInferenceError, match=r"input conversion failed \(ValueError\)"
    ) as caught:
        adapter.predict(_request())
    assert "private input diagnostic" not in str(caught.value)
