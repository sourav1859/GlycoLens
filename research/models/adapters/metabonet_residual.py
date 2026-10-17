"""Small correction heads; foundation predictions are frozen request-only inputs."""

from dataclasses import replace
from time import perf_counter

import numpy as np

from research.models.adapters.base import ForecastResult, ModelNotLoadedError, QuantileForecast
from research.models.adapters.chronos2 import CHRONOS2_MODEL_ID, CHRONOS2_MODEL_REVISION
from research.models.adapters.metabonet_context import c2_request
from research.models.adapters.metabonet_tabular import MetaboNetTabularAdapter, request_features

FEATURE_VERSION = "metabonet_c2_residual_v1"


def augmented_features(x, current, baseline):
    x, current, baseline = (np.asarray(v, dtype=float) for v in (x, current, baseline))
    if (
        x.ndim != 2
        or current.shape != (len(x),)
        or baseline.shape != (len(x), 24)
        or not np.isfinite(current).all()
        or np.any(current <= 0)
        or not np.isfinite(baseline).all()
        or np.isinf(x).any()
    ):
        raise ValueError("invalid aligned baseline/features")
    return np.column_stack((x, baseline - current[:, None]))


class MetaboNetResidualAdapter(MetaboNetTabularAdapter):
    model_version = FEATURE_VERSION

    def __init__(self, *, algorithm="ridge", parameter=1000, backbone=None):
        super().__init__(
            algorithm=algorithm, parameter=parameter, history_hours=24, profile="events"
        )
        self.model_id = f"metabonet_{algorithm}_residual"
        self._backbone = backbone

    def __getstate__(self):
        return {**self.__dict__, "_backbone": None}  # Never pickle a foundation model/callable.

    def attach_backbone(self, backbone):
        if not callable(getattr(backbone, "predict", None)):
            raise TypeError("frozen backbone must expose predict(request)")
        self._backbone = backbone
        return self

    def fit(self, requests, targets, *, baselines, sample_weight=None):
        x = np.stack([request_features(r, history_hours=24, profile="events")[0] for r in requests])
        current = np.array([r.target_history[-1].value for r in requests])
        return self.fit_arrays(x, targets, current, baselines, sample_weight=sample_weight)

    def fit_arrays(self, x, targets, current, baseline, *, sample_weight=None):
        augmented = augmented_features(x, current, baseline)
        y, baseline = np.asarray(targets, dtype=float), np.asarray(baseline, dtype=float)
        if (
            len(augmented) < 2
            or y.shape != baseline.shape
            or not np.isfinite(y).all()
            or np.any(y <= 0)
        ):
            raise ValueError("invalid residual training labels")
        return self._fit_changes(augmented, y - baseline, sample_weight=sample_weight)

    def predict_array(self, x, current, baseline):
        self.load()
        baseline = np.asarray(baseline, dtype=float)
        augmented = augmented_features(x, current, baseline)
        correction = super().predict_array(augmented, np.zeros(len(augmented)))
        prediction = baseline + correction
        if not np.isfinite(prediction).all():
            raise ValueError("nonfinite corrected forecast")
        return prediction

    def predict(self, request):
        self.load()
        if self._backbone is None:
            raise ModelNotLoadedError(
                "correction head needs an explicitly attached frozen backbone"
            )
        started = perf_counter()
        result = self.predict_from_baseline(request, self._backbone.predict(c2_request(request)))
        return replace(
            result,
            latency_ms=(perf_counter() - started) * 1000,
            metadata=result.metadata + (("timing", "backbone_plus_head"),),
        )

    def predict_from_baseline(self, request, baseline):
        self.load()
        started = perf_counter()
        short = c2_request(request)
        if (
            baseline.model_id != CHRONOS2_MODEL_ID
            or baseline.model_version != CHRONOS2_MODEL_REVISION
            or baseline.context_start != short.context_start
            or baseline.context_end != request.context_end
            or baseline.forecast_timestamps != request.forecast_timestamps
        ):
            raise ValueError("frozen backbone identity/origin/horizon differs")
        if request.quantiles != (0.1, 0.5, 0.9):
            raise ValueError("correction placeholders support only 0.1/0.5/0.9")
        x, _ = request_features(request, history_hours=24, profile="events")
        prediction = self.predict_array(
            x[None, :], np.array([request.target_history[-1].value]), np.array([baseline.median])
        )[0]
        point = tuple(float(v) for v in prediction)
        return ForecastResult(
            self.model_id,
            self.model_version,
            request.context_start,
            request.context_end,
            request.forecast_timestamps,
            point,
            tuple(QuantileForecast(q, point) for q in request.quantiles),
            (perf_counter() - started) * 1000,
            (
                ("interval", "none"),
                ("deterministic", "true"),
                ("feature_representation", FEATURE_VERSION),
                ("backbone", "chronos_c2_6h"),
            ),
        )
