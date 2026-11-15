"""Export the trusted frozen local candidate to an ignored native serving bundle.

No fitting, calibration recomputation, reserved-cohort rows or external calls.
Only known paths in the ignored local training/calibration directories are loaded.
"""

import hashlib
import json
from pathlib import Path

from backend.app.services.inference.lightgbm_bundle import (
    feature_names,
    load_bundle,
    synthetic_request,
)

ROOT = Path(__file__).resolve().parents[2]


def checked_artifact(directory, name):
    manifest_bytes = (directory / "complete.json").read_bytes()
    digest = hashlib.sha256(manifest_bytes).hexdigest()
    if digest != (directory / "complete.sha256").read_text().strip():
        raise ValueError("untrusted completion manifest")
    hashes = json.loads(manifest_bytes)["artifact_hashes"]
    raw = (directory / name).read_bytes()
    if hashlib.sha256(raw).hexdigest() != hashes[name]:
        raise ValueError("untrusted selected artifact")
    return raw, digest


def main():
    import io
    import joblib
    import numpy as np
    import lightgbm
    from research.evaluation.metabonet_uncertainty import CalibratedForecastAdapter, SymmetricBands

    trained = ROOT / "artifacts/evaluation-results/metabonet-phase4-v1"
    calibrated = ROOT / "artifacts/evaluation-results/metabonet-phase6-v1/calibration"
    bundle_bytes, training_hash = checked_artifact(trained, "model-lightgbm.joblib")
    bands_bytes, calibration_hash = checked_artifact(calibrated, "bands.json")
    bands = json.loads(bands_bytes)
    checked = {k: v for k, v in bands.items() if k != "row_sha256"}
    if (
        hashlib.sha256(json.dumps(checked, sort_keys=True, allow_nan=False).encode()).hexdigest()
        != bands["row_sha256"]
        or bands["primary_candidate"] != "lightgbm_direct"
    ):
        raise ValueError("frozen calibration identity differs")
    saved = joblib.load(io.BytesIO(bundle_bytes))  # Only after trusted manifest verification.
    # Frozen training pipeline saves configuration and adapter together.
    model = saved["adapter"] if isinstance(saved, dict) and "adapter" in saved else saved
    if not all(
        getattr(model, k, None) == v
        for k, v in dict(
            algorithm="lightgbm",
            parameter=31,
            history_hours=24,
            profile="events",
            feature_count_=127,
        ).items()
    ):
        raise ValueError("frozen winning adapter configuration differs")
    state = SymmetricBands.from_dict(bands["models"]["lightgbm_direct"])
    out = ROOT / "artifacts/models/lightgbm"
    out.mkdir(parents=True, exist_ok=True)
    data = {
        "booster.txt": model._regressor.booster_.model_to_string().encode(),
        "bands.json": json.dumps(state.to_dict(), sort_keys=True).encode(),
    }
    manifest = dict(
        format_version="1.0",
        model_id=model.model_id,
        feature_version="metabonet_tabular_v1",
        feature_names=list(feature_names()),
        history_hours=24,
        profile="events",
        num_leaves=31,
        lightgbm_version=lightgbm.__version__,
        source_training_sha256=training_hash,
        source_calibration_sha256=calibration_hash,
        files={name: hashlib.sha256(raw).hexdigest() for name, raw in data.items()},
    )
    raw = json.dumps(manifest, sort_keys=True, indent=2).encode() + b"\n"
    digest = hashlib.sha256(raw).hexdigest()
    for name, content in data.items():
        (out / name).write_bytes(content)
    (out / "manifest.json").write_bytes(raw)
    loaded = load_bundle(out, digest)
    reference = CalibratedForecastAdapter(model, state)
    max_error = 0.0
    for carbs in (0, 10.7, 40, 120):
        request = synthetic_request(carbs)
        old, new = reference.predict(request), loaded.predict(request)
        for q in (0.1, 0.5, 0.9):
            error = float(
                np.max(np.abs(np.asarray(old.quantile_values(q)) - new.quantile_values(q)))
            )
            max_error = max(max_error, error)
    if max_error > 1e-6:
        raise ValueError("native export parity failed")
    (out / "manifest.sha256").write_text(digest + "\n")
    result = dict(
        native_export_verified=True,
        synthetic_requests=4,
        max_endpoint_error_mg_dl=max_error,
        feature_count=127,
        estimator_feature_count=128,
        manifest_sha256=digest,
        model_fitted=False,
        calibration_refitted=False,
        research_rows_projected=False,
    )
    (ROOT / ".cache/lightgbm-export-validation.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    print(json.dumps(result))


if __name__ == "__main__":
    main()
