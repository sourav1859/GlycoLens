"""Small train-only predictors behind the same immutable forecast adapter boundary."""

from __future__ import annotations

import math
from time import perf_counter

import numpy as np

from research.models.adapters.base import (
    ForecastModelAdapter,
    ForecastRequest,
    ForecastResult,
    QuantileForecast,
    ModelNotLoadedError,
)

FEATURE_VERSION = "origin_features_v1"


def request_features(request: ForecastRequest, *, full_nutrition=True):
    """Read origin-known inputs only; targets and participant IDs are unavailable."""
    values = np.array([p.value for p in request.target_history], dtype=float)
    origin = request.context_end
    features = list(values[-24:] - values[-1]) + [values[-1]]
    for count in (6, 24, 72, 144, 288):
        segment = values[-count:]
        features.extend(
            [
                float(segment.mean() - values[-1]),
                float(segment.std()),
                float(segment.min() - values[-1]),
                float(segment.max() - values[-1]),
                min(len(values), count) / count,
            ]
        )
    for count in (3, 6, 12):
        features.append(float((values[-1] - values[-count]) / ((count - 1) * 5)))
    angle = 2 * math.pi * (origin.hour + origin.minute / 60) / 24
    features.extend([math.sin(angle), math.cos(angle)])
    past = {s.name: s for s in request.past_covariates}
    for name in ("insulin_bolus", "previous_meal_carbohydrates") + (
        ("previous_meal_protein", "previous_meal_fat", "previous_meal_fiber")
        if full_nutrition
        else ()
    ):
        points = past[name].points if name in past else ()
        for lookback in (120, 360):
            recent = [
                p for p in points if 0 <= (origin - p.timestamp).total_seconds() / 60 <= lookback
            ]
            features.extend([sum(p.value for p in recent), len(recent)])
        features.extend(
            [
                min((origin - points[-1].timestamp).total_seconds() / 60, 360) if points else 360,
                float(bool(points)),
            ]
        )
    known = {s.name: s.points[0].value for s in request.known_covariates}
    for name in ("meal_carbohydrates",) + (
        ("meal_protein", "meal_fat", "meal_fiber") if full_nutrition else ()
    ):
        features.extend([known.get(name, 0), float(name in known)])
    return np.array(features, dtype=float)


class TabularForecastAdapter(ForecastModelAdapter):
    model_version = FEATURE_VERSION

    def __init__(self, *, algorithm="ridge", parameter=10, full_nutrition=True, backbone=None):
        self.algorithm, self.parameter = algorithm, parameter
        self.full_nutrition, self.backbone = full_nutrition, backbone
        self.model_id = f"{algorithm}_{'residual' if backbone else 'direct'}"
        self._regressor = None
        self._scaler = None
        self._interval = None

    def load(self):
        if self._regressor is None:
            raise ModelNotLoadedError(
                "tabular model requires a train-only fit or trusted local load"
            )

    def _base(self, request):
        if self.backbone is None:
            return np.full(request.prediction_length, request.target_history[-1].value)
        # A caller may cache frozen forecasts. The immutable request is the only model input.
        return np.asarray(self.backbone(request), dtype=float)

    def fit(self, requests, targets, *, sample_weight=None):
        from sklearn.preprocessing import StandardScaler
        from sklearn.linear_model import Ridge
        from sklearn.multioutput import MultiOutputRegressor
        from lightgbm import LGBMRegressor

        if len(requests) != len(targets) or len(requests) < 2:
            raise ValueError("training requires aligned finite input/target examples")
        x = np.stack([request_features(r, full_nutrition=self.full_nutrition) for r in requests])
        y = np.stack([np.asarray(t) - self._base(r) for r, t in zip(requests, targets)])
        if len(x) != len(y) or len(x) < 2 or not np.isfinite(y).all():
            raise ValueError("training requires aligned finite input/target examples")
        self._scaler = StandardScaler().fit(x, sample_weight=sample_weight)
        if self.algorithm == "ridge":
            self._regressor = Ridge(alpha=self.parameter)
        elif self.algorithm == "lightgbm":
            self._regressor = MultiOutputRegressor(
                LGBMRegressor(
                    n_estimators=150,
                    num_leaves=int(self.parameter),
                    learning_rate=0.03,
                    min_child_samples=20,
                    random_state=20261016,
                    n_jobs=2,
                    deterministic=True,
                    force_col_wise=True,
                    verbosity=-1,
                )
            )
        else:
            raise ValueError("unsupported small-model algorithm")
        self._regressor.fit(self._scaler.transform(x), y, sample_weight=sample_weight)
        return self

    def predict(self, request):
        self.load()
        if request.quantiles != (0.1, 0.5, 0.9):
            raise ValueError("tabular calibration supports only 0.1/0.5/0.9 quantiles")
        started = perf_counter()
        x = request_features(request, full_nutrition=self.full_nutrition).reshape(1, -1)
        prediction = self._base(request) + self._regressor.predict(self._scaler.transform(x))[0]
        radius = self._interval if self._interval is not None else np.zeros(len(prediction))
        quantiles = tuple(
            QuantileForecast(
                q,
                tuple(
                    float(v)
                    for v in prediction + (-radius if q == 0.1 else radius if q == 0.9 else 0)
                ),
            )
            for q in request.quantiles
        )
        return ForecastResult(
            self.model_id,
            self.model_version,
            request.context_start,
            request.context_end,
            request.forecast_timestamps,
            tuple(float(v) for v in prediction),
            quantiles,
            (perf_counter() - started) * 1000,
            (
                ("deterministic", "true" if self._interval is None else "false"),
                ("interval", "none" if self._interval is None else "calibrated_marginal_80"),
            ),
        )

    def calibrate(self, requests, targets):
        if len(requests) != len(targets) or len(requests) < 5:
            raise ValueError("insufficient separate calibration events")
        errors = np.stack(
            [
                np.abs(np.asarray(t) - np.asarray(self.predict(r).median))
                for r, t in zip(requests, targets)
            ]
        )
        if len(errors) < 5:
            raise ValueError("insufficient separate calibration events")
        level = min(1, math.ceil((len(errors) + 1) * 0.8) / len(errors))
        self._interval = np.quantile(errors, level, axis=0, method="higher")
        return self
