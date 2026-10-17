"""MetaboNet-specific origin features and small direct point-forecast adapters."""

from __future__ import annotations

from datetime import timedelta
from time import perf_counter

import numpy as np

from research.models.adapters.base import (
    ForecastModelAdapter,
    ForecastResult,
    ModelInferenceError,
    ModelNotLoadedError,
    QuantileForecast,
)

FEATURE_VERSION = "metabonet_tabular_v1"


def request_features(request, *, history_hours, profile):
    if profile not in ("cgm", "events") or history_hours not in (2, 6, 12, 24):
        raise ValueError("unsupported MetaboNet feature configuration")
    if (
        len(request.target_history) != history_hours * 12
        or request.frequency_minutes != 5
        or request.prediction_length != 24
    ):
        raise ValueError("request history/horizon differs from trained configuration")
    past = {s.name: s for s in request.past_covariates}
    mask = past.get("cgm_record_present")
    if mask is None or mask.unit != "source_record_present":
        raise ValueError("CGM mask unit/schema required")
    if tuple(p.timestamp for p in mask.points) != tuple(
        p.timestamp for p in request.target_history
    ) or any(p.value not in (0, 1) for p in mask.points):
        raise ValueError("CGM history mask does not match source grid")
    values = np.array([p.value for p in request.target_history], dtype=float)
    present = np.array([p.value for p in mask.points], dtype=float)
    features = []
    names = []

    def add(name, value):
        names.append(name)
        features.append(float(value))

    add("current_cgm", values[-1])
    for i, v in enumerate(values[-24:] - values[-1]):
        add(f"cgm_relative_lag_{23 - i}", v)
    for i, v in enumerate(present[-24:]):
        add(f"cgm_present_lag_{23 - i}", v)
    for count in (6, 12, 24, 72, 144, 288):
        segment = values[-count:]
        for name, v in (
            ("mean", segment.mean() - values[-1]),
            ("std", segment.std()),
            ("min", segment.min() - values[-1]),
            ("max", segment.max() - values[-1]),
            ("available_fraction", len(segment) / count),
            ("present_fraction", present[-count:].mean()),
        ):
            add(f"cgm_{name}_{count}", v)
    for count in (3, 6, 12, 24):
        add(f"cgm_slope_{count}", (values[-1] - values[-count]) / ((count - 1) * 5))
    if profile == "events":
        origin = request.context_end
        for channel, label, unit in (
            ("insulin_bolus", "bolus", "IU_per_source_interval"),
            ("insulin_basal", "basal", "IU_per_source_interval"),
            ("previous_meal_carbohydrates", "previous_carbs", "g"),
        ):
            record = past.get(channel)
            indicator = past.get(channel + "_record_present")
            if (
                indicator is None
                or indicator.unit != "source_record_present"
                or (record is not None and record.unit != unit)
            ):
                raise ValueError("recorded channel unit/mask differs from MetaboNet schema")
            if any(p.value not in (0, 1) for p in indicator.points):
                raise ValueError("invalid event mask")
            masks = {p.timestamp: p.value for p in indicator.points}
            amounts = {p.timestamp: p.value for p in record.points} if record else {}
            first = 1 if label == "previous_carbs" else 0
            ages = np.arange(first, 72, dtype=float) * 5
            data = np.array(
                [
                    amounts.get(origin - timedelta(minutes=float(age)), 0)
                    if masks.get(origin - timedelta(minutes=float(age)), 0) == 1
                    else np.nan
                    for age in ages
                ]
            )
            for lookback in (30, 60, 120, 360):
                segment = data[ages < lookback]
                observed = np.isfinite(segment)
                add(
                    f"{label}_recorded_sum_{lookback}m",
                    np.nansum(segment) if observed.any() else np.nan,
                )
                add(f"{label}_present_fraction_{lookback}m", observed.mean())
            for scale in (30, 120):
                add(
                    f"{label}_recency_weighted_{scale}m",
                    np.nansum(data * np.exp(-ages / scale)) if np.isfinite(data).any() else np.nan,
                )
            positive = ages[np.isfinite(data) & (data > 0)]
            add(f"{label}_last_positive_age", positive.min() if len(positive) else 360)
            add(f"{label}_positive_present", bool(len(positive)))
        meals = {s.name: s for s in request.known_covariates}
        meal = meals.get("meal_carbohydrates")
        if meal is not None and (
            meal.unit != "g" or len(meal.points) != 1 or meal.points[0].timestamp != origin
        ):
            raise ValueError("origin meal unit/schema differs")
        add("meal_carbs_g", meal.points[0].value if meal else np.nan)
        add("meal_carbs_present", meal is not None)
    return np.array(features, dtype=float), tuple(names)


def horizon_matrix(x):
    return np.column_stack((np.repeat(x, 24, axis=0), np.tile(np.arange(1, 25) / 24, len(x))))


class MetaboNetTabularAdapter(ForecastModelAdapter):
    model_version = FEATURE_VERSION

    def __init__(self, *, algorithm="ridge", parameter=10, history_hours=2, profile="events"):
        if (
            algorithm not in ("ridge", "lightgbm")
            or parameter <= 0
            or history_hours not in (2, 6, 12, 24)
            or profile not in ("cgm", "events")
        ):
            raise ValueError("unsupported direct model configuration")
        self.algorithm, self.parameter, self.history_hours, self.profile = (
            algorithm,
            parameter,
            history_hours,
            profile,
        )
        self.model_id = f"metabonet_{algorithm}_direct"
        self._regressor = None
        self._imputer = None
        self._scaler = None
        self.feature_count_ = None

    def load(self):
        if self._regressor is None:
            raise ModelNotLoadedError(
                "direct model requires train-only fit or trusted verified reload"
            )

    def fit(self, requests, targets, *, sample_weight=None):
        x = np.stack(
            [
                request_features(r, history_hours=self.history_hours, profile=self.profile)[0]
                for r in requests
            ]
        )
        return self.fit_arrays(
            x,
            np.asarray(targets),
            np.array([r.target_history[-1].value for r in requests]),
            sample_weight=sample_weight,
        )

    def fit_arrays(self, x, targets, current, *, sample_weight=None):

        x, y, current = (
            np.asarray(x, dtype=float),
            np.asarray(targets, dtype=float),
            np.asarray(current, dtype=float),
        )
        if (
            x.ndim != 2
            or len(x) < 2
            or y.shape != (len(x), 24)
            or current.shape != (len(x),)
            or np.isinf(x).any()
            or not np.isfinite(y).all()
            or not np.isfinite(current).all()
            or np.any(y <= 0)
            or np.any(current <= 0)
        ):
            raise ValueError("invalid aligned training arrays")
        return self._fit_changes(x, y - current[:, None], sample_weight=sample_weight)

    def _fit_changes(self, x, delta, *, sample_weight=None):
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import Ridge
        from sklearn.preprocessing import StandardScaler

        weights = (
            np.ones(len(x)) if sample_weight is None else np.asarray(sample_weight, dtype=float)
        )
        if weights.shape != (len(x),) or not np.isfinite(weights).all() or np.any(weights <= 0):
            raise ValueError("invalid participant weights")
        self.feature_count_ = x.shape[1]
        if self.algorithm == "ridge":
            self._imputer = SimpleImputer(strategy="median", keep_empty_features=True).fit(x)
            imputed = self._imputer.transform(x)
            self._scaler = StandardScaler().fit(imputed, sample_weight=weights)
            self._regressor = Ridge(alpha=float(self.parameter)).fit(
                self._scaler.transform(imputed), delta, sample_weight=weights
            )
        else:
            from lightgbm import LGBMRegressor

            self._regressor = LGBMRegressor(
                n_estimators=160,
                num_leaves=int(self.parameter),
                learning_rate=0.04,
                min_child_samples=100,
                max_bin=63,
                reg_lambda=1,
                random_state=20261016,
                n_jobs=2,
                deterministic=True,
                force_col_wise=True,
                verbosity=-1,
            ).fit(horizon_matrix(x), delta.reshape(-1), sample_weight=np.repeat(weights, 24))
        return self

    def predict_array(self, x, current):
        self.load()
        x, current = np.asarray(x, dtype=float), np.asarray(current, dtype=float)
        if (
            x.ndim != 2
            or x.shape[1] != self.feature_count_
            or current.shape != (len(x),)
            or np.isinf(x).any()
            or not np.isfinite(current).all()
        ):
            raise ValueError("prediction features differ from trained schema")
        delta = self._predict_changes(x)
        prediction = delta + current[:, None]
        if prediction.shape != (len(x), 24) or not np.isfinite(prediction).all():
            raise ModelInferenceError("direct model returned invalid point forecast")
        return prediction

    def _predict_changes(self, x):
        if self.algorithm == "ridge":
            return self._regressor.predict(self._scaler.transform(self._imputer.transform(x)))
        return self._regressor.booster_.predict(horizon_matrix(x), num_threads=2).reshape(-1, 24)

    def predict(self, request):
        self.load()
        if request.quantiles != (0.1, 0.5, 0.9):
            raise ValueError("direct placeholder contract supports only 0.1/0.5/0.9")
        started = perf_counter()
        x, _ = request_features(request, history_hours=self.history_hours, profile=self.profile)
        point = tuple(
            float(v)
            for v in self.predict_array(x[None, :], np.array([request.target_history[-1].value]))[0]
        )
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
                ("feature_representation", FEATURE_VERSION),
                ("interval", "none"),
                ("deterministic", "true"),
                ("history_hours", str(self.history_hours)),
                ("profile", self.profile),
            ),
        )
