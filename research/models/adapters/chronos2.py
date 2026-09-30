"""Pinned Chronos-2 adapter for CPU-first, CGM-only Milestone 1 inference."""

from __future__ import annotations

from collections.abc import Callable
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from time import perf_counter_ns
from typing import Any

from research.models.adapters.base import (
    ForecastModelAdapter,
    ForecastRequest,
    ForecastResult,
    ForecastValidationError,
    ModelInferenceError,
    ModelLoadError,
    ModelNotLoadedError,
    QuantileForecast,
)


CHRONOS2_MODEL_ID = "amazon/chronos-2"
CHRONOS2_MODEL_REVISION = "29ec3766d36d6f73f0696f85560a422f50e8498c"
CHRONOS_FORECASTING_VERSION = "2.3.2"

PipelineLoader = Callable[..., Any]
TensorFactory = Callable[[list[float]], Any]


def _default_pipeline_loader(model_id: str, **kwargs: object) -> object:
    installed_version = _package_version()
    if installed_version != CHRONOS_FORECASTING_VERSION:
        raise ModelLoadError(
            "The installed chronos-forecasting version does not match the Phase 3 pin"
        )
    try:
        from chronos import Chronos2Pipeline
    except (ImportError, OSError) as error:
        raise ModelLoadError(
            "Chronos-2 dependencies are unavailable; install the pinned chronos group"
        ) from error
    return Chronos2Pipeline.from_pretrained(model_id, **kwargs)


def _default_tensor_factory(values: list[float]) -> object:
    try:
        import torch
    except (ImportError, OSError) as error:
        raise ModelLoadError(
            "PyTorch is unavailable; install the pinned chronos dependency group"
        ) from error
    return torch.tensor(values, dtype=torch.float32)


def _package_version() -> str:
    try:
        return version("chronos-forecasting")
    except PackageNotFoundError:
        return "not-installed"


def _to_nested_list(value: object) -> object:
    current = value
    for method_name in ("detach", "cpu"):
        method = getattr(current, method_name, None)
        if callable(method):
            current = method()
    tolist = getattr(current, "tolist", None)
    return tolist() if callable(tolist) else current


def _normalize_quantile_matrix(
    backend_quantiles: object,
    *,
    prediction_length: int,
    quantile_count: int,
) -> tuple[tuple[float, ...], ...]:
    try:
        if len(backend_quantiles) != 1:  # type: ignore[arg-type]
            raise ValueError("expected one forecast task")
        task = _to_nested_list(backend_quantiles[0])  # type: ignore[index]
        if not isinstance(task, (list, tuple)) or len(task) != 1:
            raise ValueError("expected one target variate")
        rows = task[0]
        if not isinstance(rows, (list, tuple)) or len(rows) != prediction_length:
            raise ValueError("unexpected prediction horizon")
        matrix: list[tuple[float, ...]] = []
        for row in rows:
            if not isinstance(row, (list, tuple)) or len(row) != quantile_count:
                raise ValueError("unexpected quantile dimension")
            matrix.append(tuple(float(value) for value in row))
        return tuple(matrix)
    except (IndexError, TypeError, ValueError) as error:
        raise ModelInferenceError(
            "Chronos-2 returned an output that violates the forecast shape contract"
        ) from error


class Chronos2ForecastAdapter(ForecastModelAdapter):
    """Run the exact pinned Chronos-2 checkpoint on one univariate CGM history."""

    model_id = CHRONOS2_MODEL_ID
    model_version = CHRONOS2_MODEL_REVISION

    def __init__(
        self,
        *,
        device_map: str = "cpu",
        cache_dir: Path | str | None = None,
        pipeline_loader: PipelineLoader | None = None,
        tensor_factory: TensorFactory | None = None,
    ) -> None:
        if device_map != "cpu":
            raise ValueError("Milestone 1 Chronos-2 validation is pinned to CPU inference")
        self.device_map = device_map
        self.cache_dir = Path(cache_dir).resolve() if cache_dir is not None else None
        self._pipeline_loader = pipeline_loader or _default_pipeline_loader
        self._tensor_factory = tensor_factory or _default_tensor_factory
        self._pipeline: object | None = None

    @property
    def is_loaded(self) -> bool:
        return self._pipeline is not None

    def load(self) -> None:
        if self.is_loaded:
            return
        kwargs: dict[str, object] = {
            "revision": self.model_version,
            "device_map": self.device_map,
        }
        if self.cache_dir is not None:
            kwargs["cache_dir"] = str(self.cache_dir)
        try:
            self._pipeline = self._pipeline_loader(self.model_id, **kwargs)
        except ModelLoadError:
            raise
        except Exception as error:
            raise ModelLoadError(
                f"Chronos-2 initialization failed ({type(error).__name__})"
            ) from error

    def predict(self, request: ForecastRequest) -> ForecastResult:
        if not self.is_loaded:
            raise ModelNotLoadedError("Chronos-2 adapter must be loaded before prediction")
        if not isinstance(request, ForecastRequest):
            raise TypeError("request must be a ForecastRequest")
        if request.past_covariates or request.known_covariates:
            raise ForecastValidationError(
                "the Phase 3 Chronos-2 adapter supports CGM-only requests"
            )

        try:
            model_input = self._tensor_factory([point.value for point in request.target_history])
        except ModelLoadError:
            raise
        except Exception as error:
            raise ModelInferenceError(
                f"Chronos-2 input conversion failed ({type(error).__name__})"
            ) from error
        started = perf_counter_ns()
        try:
            backend_quantiles, _backend_point_forecast = self._pipeline.predict_quantiles(  # type: ignore[union-attr]
                inputs=[model_input],
                prediction_length=request.prediction_length,
                quantile_levels=list(request.quantiles),
            )
        except Exception as error:
            raise ModelInferenceError(
                f"Chronos-2 inference failed ({type(error).__name__})"
            ) from error
        latency_ms = (perf_counter_ns() - started) / 1_000_000

        matrix = _normalize_quantile_matrix(
            backend_quantiles,
            prediction_length=request.prediction_length,
            quantile_count=len(request.quantiles),
        )
        quantile_forecasts = tuple(
            QuantileForecast(
                level=level,
                values=tuple(row[index] for row in matrix),
            )
            for index, level in enumerate(request.quantiles)
        )
        median = quantile_forecasts[request.quantiles.index(0.5)].values

        try:
            return ForecastResult(
                model_id=self.model_id,
                model_version=self.model_version,
                context_start=request.context_start,
                context_end=request.context_end,
                forecast_timestamps=request.forecast_timestamps,
                median=median,
                quantiles=quantile_forecasts,
                latency_ms=latency_ms,
                metadata=(
                    ("adapter", "chronos2_univariate"),
                    ("chronos_forecasting_version", _package_version()),
                    ("context_configuration", "cgm_only"),
                    ("device", self.device_map),
                    ("target_unit", "mg/dL"),
                ),
            )
        except ForecastValidationError as error:
            raise ModelInferenceError(
                "Chronos-2 output violates the validated forecast result contract"
            ) from error
