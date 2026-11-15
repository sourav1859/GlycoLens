"""Verified native LightGBM serving; no pickle deserialization or model fitting."""

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re

from research.models.adapters.base import CovariateSeries, ForecastRequest, TimePoint
from research.models.adapters.metabonet_tabular import (
    FEATURE_VERSION,
    MetaboNetTabularAdapter,
    horizon_matrix,
    request_features,
)
from research.evaluation.metabonet_uncertainty import CalibratedForecastAdapter, SymmetricBands


def synthetic_request(carbs=40.0):
    """Handcrafted parity fixture, independent of all research cohort rows."""
    origin = datetime(2026, 1, 2, 12, tzinfo=timezone.utc)
    history = tuple(TimePoint(origin - timedelta(minutes=5 * i), 120) for i in range(287, -1, -1))
    covariates = [
        CovariateSeries(
            "cgm_record_present",
            tuple(TimePoint(p.timestamp, 1) for p in history),
            "source_record_present",
        )
    ]
    times = [origin - timedelta(minutes=5 * i) for i in range(71, -1, -1)]
    for name, unit in (
        ("insulin_bolus", "IU_per_source_interval"),
        ("insulin_basal", "IU_per_source_interval"),
        ("previous_meal_carbohydrates", "g"),
    ):
        covariates += [
            CovariateSeries(name, tuple(TimePoint(at, 0) for at in times), unit),
            CovariateSeries(
                name + "_record_present",
                tuple(TimePoint(at, 1) for at in times),
                "source_record_present",
            ),
        ]
    return ForecastRequest(
        history,
        past_covariates=tuple(covariates),
        known_covariates=(CovariateSeries("meal_carbohydrates", (TimePoint(origin, carbs),), "g"),),
    )


def feature_names():
    return request_features(synthetic_request(), history_hours=24, profile="events")[1]


class NativeTabularAdapter(MetaboNetTabularAdapter):
    def __init__(self, booster, bundle_sha256, calibration_sha256):
        super().__init__(algorithm="lightgbm", parameter=31, history_hours=24, profile="events")
        self._booster = booster
        self.feature_count_ = 127
        self.model_version = FEATURE_VERSION + ":" + bundle_sha256
        self.bundle_sha256 = bundle_sha256
        self.calibration_sha256 = calibration_sha256

    def load(self):
        if self._booster.num_feature() != 128:
            raise ValueError("native model feature dimension differs")

    def fit(self, *args, **kwargs):
        raise ValueError("serving cannot fit weights")

    def fit_arrays(self, *args, **kwargs):
        raise ValueError("serving cannot fit weights")

    def _predict_changes(self, x):
        return self._booster.predict(horizon_matrix(x), num_threads=2).reshape(-1, 24)


def _checked_bytes(directory, name, expected, maximum):
    path = (directory / name).resolve(strict=True)
    if not path.is_relative_to(directory) or path.stat().st_size > maximum:
        raise ValueError("bundle path or size is invalid")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError(f"{name} digest differs")
    return raw


def load_bundle(directory: Path, manifest_sha256: str):
    """Require a server-configured trust anchor and hash bytes before native loading."""
    if not re.fullmatch(r"[a-f0-9]{64}", manifest_sha256 or ""):
        raise ValueError("trusted manifest digest is required")
    directory = Path(directory).resolve(strict=True)
    raw = _checked_bytes(directory, "manifest.json", manifest_sha256, 32768)
    manifest = json.loads(raw)
    expected = dict(
        format_version="1.0",
        model_id="metabonet_lightgbm_direct",
        feature_version=FEATURE_VERSION,
        history_hours=24,
        profile="events",
        num_leaves=31,
        lightgbm_version="4.6.0",
    )
    if any(manifest.get(k) != v for k, v in expected.items()):
        raise ValueError("bundle configuration differs from frozen feature recipe")
    if manifest.get("feature_names") != list(feature_names()):
        raise ValueError("bundle feature order differs")
    if set(manifest.get("files", {})) != {"booster.txt", "bands.json"}:
        raise ValueError("bundle file allowlist differs")
    model_bytes = _checked_bytes(
        directory, "booster.txt", manifest["files"]["booster.txt"], 32_000_000
    )
    band_bytes = _checked_bytes(directory, "bands.json", manifest["files"]["bands.json"], 32768)
    bands = SymmetricBands.from_dict(json.loads(band_bytes))
    import lightgbm

    if lightgbm.__version__ != "4.6.0":
        raise ValueError("serving LightGBM dependency differs")
    native = NativeTabularAdapter(
        lightgbm.Booster(model_str=model_bytes.decode("utf-8")),
        manifest_sha256,
        manifest["files"]["bands.json"],
    )
    native.load()
    adapter = CalibratedForecastAdapter(native, bands)
    adapter.bundle_sha256 = manifest_sha256
    adapter.calibration_sha256 = native.calibration_sha256
    return adapter
