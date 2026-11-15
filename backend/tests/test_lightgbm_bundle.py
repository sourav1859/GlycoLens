"""Serving must reject untrusted bytes before any native model is constructed."""

import hashlib
import json

import pytest

from backend.app.services.inference.lightgbm_bundle import load_bundle, feature_names


def bundle(tmp_path):
    files = {
        "booster.txt": b"native-model",
        "bands.json": json.dumps(
            dict(
                radii=[10] * 24,
                curve_radius=20,
                coverage=0.8,
                participant_count=48,
            )
        ).encode(),
    }
    manifest = dict(
        format_version="1.0",
        model_id="metabonet_lightgbm_direct",
        feature_version="metabonet_tabular_v1",
        feature_names=list(feature_names()),
        history_hours=24,
        profile="events",
        num_leaves=31,
        lightgbm_version="4.6.0",
        files={name: hashlib.sha256(content).hexdigest() for name, content in files.items()},
    )
    for name, content in files.items():
        (tmp_path / name).write_bytes(content)
    raw = json.dumps(manifest, sort_keys=True).encode()
    (tmp_path / "manifest.json").write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def test_tampered_model_rejected_before_native_load(tmp_path, monkeypatch):
    digest = bundle(tmp_path)
    (tmp_path / "booster.txt").write_text("tampered")
    calls = []
    monkeypatch.setattr("lightgbm.Booster", lambda **kw: calls.append(kw))
    with pytest.raises(ValueError, match="digest"):
        load_bundle(tmp_path, digest)
    assert calls == []


def test_manifest_requires_out_of_band_trust_and_fixed_features(tmp_path):
    digest = bundle(tmp_path)
    with pytest.raises(ValueError, match="manifest"):
        load_bundle(tmp_path, "0" * 64)
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    manifest["feature_names"] = list(reversed(manifest["feature_names"]))
    raw = json.dumps(manifest).encode()
    (tmp_path / "manifest.json").write_bytes(raw)
    with pytest.raises(ValueError, match="feature"):
        load_bundle(tmp_path, hashlib.sha256(raw).hexdigest())
    assert digest != hashlib.sha256(raw).hexdigest()


def test_valid_native_load_retains_signed_calibrated_endpoints(tmp_path, monkeypatch):
    import numpy as np
    from backend.app.services.inference.lightgbm_bundle import synthetic_request

    class Booster:
        def __init__(self, **kw):
            assert kw == {"model_str": "native-model"}

        def num_feature(self):
            return 128

        def predict(self, x, **kw):
            return np.full(len(x), -115.0)

    monkeypatch.setattr("lightgbm.Booster", Booster)
    loaded = load_bundle(tmp_path, bundle(tmp_path))
    result = loaded.predict(synthetic_request())
    assert result.median == (5.0,) * 24
    assert result.quantile_values(0.1) == (-5.0,) * 24
    assert dict(result.metadata)["interval"] == "participant_representative_marginal_80"
    assert result.model_version.endswith(loaded.bundle_sha256)


@pytest.mark.parametrize("name", ["booster.txt", "bands.json", "manifest.json"])
def test_missing_or_corrupt_bundle_files_never_construct_a_model(tmp_path, monkeypatch, name):
    digest = bundle(tmp_path)
    (tmp_path / name).unlink()
    calls = []
    monkeypatch.setattr("lightgbm.Booster", lambda **kw: calls.append(kw))
    with pytest.raises((ValueError, OSError)):
        load_bundle(tmp_path, digest)
    assert not calls


@pytest.mark.parametrize(
    "change",
    [dict(coverage=0.7), dict(participant_count=0), dict(radii=[1] * 23), dict(curve_radius=-1)],
)
def test_invalid_calibration_is_rejected_even_with_matching_file_digests(
    tmp_path, monkeypatch, change
):
    bundle(tmp_path)
    path = tmp_path / "bands.json"
    values = json.loads(path.read_text())
    values.update(change)
    raw = json.dumps(values).encode()
    path.write_bytes(raw)
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    manifest["files"]["bands.json"] = hashlib.sha256(raw).hexdigest()
    raw_manifest = json.dumps(manifest).encode()
    (tmp_path / "manifest.json").write_bytes(raw_manifest)
    calls = []
    monkeypatch.setattr("lightgbm.Booster", lambda **kw: calls.append(kw))
    with pytest.raises(ValueError):
        load_bundle(tmp_path, hashlib.sha256(raw_manifest).hexdigest())
    assert not calls
