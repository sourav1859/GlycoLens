"""Pinned CPU TimesFM-3 adapter using the official PyTorch package."""

from __future__ import annotations

from importlib.metadata import version
from pathlib import Path
from time import perf_counter
from typing import Callable

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
from research.models.adapters.covariates import FEATURE_VERSION, aligned_covariates


TIMESFM3_MODEL_ID = "google/timesfm-3.0-pytorch"
TIMESFM3_REVISION = "43046b85ec22d584a13f8098c2ed39c889e129c2"
TIMESFM_VERSION = "3.0.2"


def _loader(**kwargs):
    if version("timesfm") != TIMESFM_VERSION:
        raise ModelLoadError("installed TimesFM does not match the pinned research version")
    from timesfm3 import TimesFM3Forecaster

    return TimesFM3Forecaster.from_pretrained(TIMESFM3_MODEL_ID, device="cpu", **kwargs)


class TimesFM3ForecastAdapter(ForecastModelAdapter):
    model_id = TIMESFM3_MODEL_ID
    model_version = TIMESFM3_REVISION

    def __init__(
        self,
        *,
        cache_dir: Path | str | None = None,
        local_files_only: bool = True,
        loader: Callable | None = None,
    ):
        self.cache_dir = str(cache_dir) if cache_dir else None
        self.local_files_only = local_files_only
        self._loader = loader or _loader
        self._model = None

    @property
    def is_loaded(self):
        return self._model is not None

    def load(self):
        if self.is_loaded:
            return
        try:
            self._model = self._loader(
                revision=self.model_version,
                cache_dir=self.cache_dir,
                local_files_only=self.local_files_only,
            )
        except Exception as error:
            raise ModelLoadError(
                f"TimesFM initialization failed ({type(error).__name__})"
            ) from error

    def predict(self, request: ForecastRequest) -> ForecastResult:
        if not self.is_loaded:
            raise ModelNotLoadedError("TimesFM adapter must be loaded before prediction")
        if not isinstance(request, ForecastRequest):
            raise TypeError("request must be a ForecastRequest")
        if any(q not in (0.1, 0.5, 0.9) for q in request.quantiles):
            raise ForecastValidationError("TimesFM adapter supports q10/q50/q90")
        import numpy as np

        past, future = aligned_covariates(request)
        past_only = [values for name, values in sorted(past.items()) if name not in future]
        known = [past[name] + future[name] for name in sorted(future)]
        started = perf_counter()
        try:
            output = self._model.predict(
                np.asarray([p.value for p in request.target_history], dtype=np.float32),
                horizon=request.prediction_length,
                past_only_covariates=np.asarray(past_only, dtype=np.float32) if past_only else None,
                past_future_covariates=np.asarray(known, dtype=np.float32) if known else None,
                return_quantiles=True,
                sort_quantiles=False,
                use_symmetric_averaging=False,
            )
            matrix = np.asarray(output.quantiles)
            if matrix.shape != (request.prediction_length, 9):
                raise ValueError("unexpected quantile output shape")
            quantiles = tuple(
                QuantileForecast(q, tuple(float(v) for v in matrix[:, round(q * 10) - 1]))
                for q in request.quantiles
            )
            median = quantiles[request.quantiles.index(0.5)].values
            return ForecastResult(
                self.model_id,
                self.model_version,
                request.context_start,
                request.context_end,
                request.forecast_timestamps,
                median,
                quantiles,
                (perf_counter() - started) * 1000,
                (
                    ("feature_representation", FEATURE_VERSION),
                    ("device", "cpu"),
                    ("license", "timesfm-non-commercial-license-v1.0"),
                ),
            )
        except Exception as error:
            raise ModelInferenceError(
                f"TimesFM prediction failed ({type(error).__name__})"
            ) from error
