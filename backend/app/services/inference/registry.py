"""Server-owned allowlist and immutable identities shared by both inference paths."""

from dataclasses import dataclass
import os
from pathlib import Path
from threading import Lock
from fastapi import HTTPException
from research.models.adapters import Chronos2ForecastAdapter
from research.models.adapters.covariates import FEATURE_VERSION

ROOT = Path(__file__).resolve().parents[4]
_CACHE = {}
_LOCK = Lock()


@dataclass(frozen=True)
class ModelSpec:
    key: str
    identity: dict

    @property
    def history_samples(self):
        return self.identity["history_samples"]

    def adapter(self):
        cache_key = (self.key, self.identity["model_version"], self.identity["calibration_sha256"])
        with _LOCK:
            if cache_key not in _CACHE:
                if self.key == "chronos":
                    adapter = Chronos2ForecastAdapter(
                        cache_dir=ROOT / "artifacts/models/huggingface"
                    )
                    adapter.load()
                else:
                    from .lightgbm_bundle import load_bundle

                    adapter = load_bundle(
                        Path(
                            os.environ.get(
                                "GLYCOLENS_LIGHTGBM_BUNDLE_DIR",
                                str(ROOT / "artifacts/models/lightgbm"),
                            )
                        ),
                        self.identity["bundle_sha256"],
                    )
                    if adapter.calibration_sha256 != self.identity["calibration_sha256"]:
                        raise ValueError("calibration identity changed")
                _CACHE[cache_key] = adapter
            return _CACHE[cache_key]

    def predict(self, request):
        result = self.adapter().predict(request)
        if (result.model_id, result.model_version) != (
            self.identity["model_id"],
            self.identity["model_version"],
        ):
            raise ValueError("resolved model output identity differs")
        return result


def resolve_model(key="chronos", *, expected=None):
    if key not in {"chronos", "lightgbm"}:
        raise HTTPException(422, "Choose an available forecasting model")
    identity = dict(
        model_key=key,
        model_id=Chronos2ForecastAdapter.model_id,
        model_version=Chronos2ForecastAdapter.model_version,
        feature_version=FEATURE_VERSION,
        bundle_sha256=None,
        calibration_sha256=None,
        history_samples=24,
        interval_kind="model_quantiles",
        inputs=["glucose history", "recorded insulin", "carbohydrates", "protein", "fat", "fiber"],
    )
    if key == "lightgbm":
        if os.environ.get("GLYCOLENS_LIGHTGBM_ENABLED", "false").lower() != "true":
            raise HTTPException(
                503, "LightGBM research option is not enabled; Chronos remains available"
            )
        try:
            from .lightgbm_bundle import load_bundle

            digest = os.environ.get("GLYCOLENS_LIGHTGBM_MANIFEST_SHA256", "")
            # Load only verified native bytes, cached by their complete immutable identity.
            cache_key = ("verified_bundle", digest)
            with _LOCK:
                if cache_key not in _CACHE:
                    _CACHE[cache_key] = load_bundle(
                        Path(
                            os.environ.get(
                                "GLYCOLENS_LIGHTGBM_BUNDLE_DIR",
                                str(ROOT / "artifacts/models/lightgbm"),
                            )
                        ),
                        digest,
                    )
                adapter = _CACHE[cache_key]
            identity.update(
                model_id=adapter.model_id,
                model_version=adapter.model_version,
                feature_version="metabonet_tabular_v1",
                bundle_sha256=adapter.bundle_sha256,
                calibration_sha256=adapter.calibration_sha256,
                history_samples=288,
                interval_kind="calibrated_marginal_80",
                inputs=[
                    "24-hour glucose history and observation masks",
                    "recorded five-minute insulin amounts",
                    "previous carbohydrates",
                    "current carbohydrates",
                ],
            )
            _CACHE[(key, identity["model_version"], identity["calibration_sha256"])] = adapter
        except Exception:
            raise HTTPException(
                503,
                "Verified LightGBM bundle/calibration is unavailable; no substitute model was run",
            ) from None
    if expected is not None and identity != expected:
        raise HTTPException(
            409, "Saved model, feature or calibration identity differs; start a separate forecast"
        )
    return ModelSpec(key, identity)


def model_capabilities():
    result = []
    for key, label, count in (
        ("chronos", "Chronos · default", 24),
        ("lightgbm", "LightGBM · research option", 288),
    ):
        try:
            resolve_model(key)
            available, reason = True, None
        except HTTPException as exc:
            available, reason = False, exc.detail
        result.append(
            dict(
                key=key,
                label=label,
                default=key == "chronos",
                history_samples=count,
                available=available,
                reason=reason,
                required_protocol="lightgbm_warmup_48h_v1" if key == "lightgbm" else None,
            )
        )
    return result
