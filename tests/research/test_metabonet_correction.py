from dataclasses import replace
import json

import numpy as np
import pytest

from research.datasets.metabonet import STEP_NS, SubjectSeries, build_window, window_to_example
from research.models.adapters.base import ModelInferenceError
from research.models.adapters.metabonet_context import c2_request
from research.pipelines.cache_metabonet_backbone import cache_training
from research.pipelines.run_metabonet_inference import request_for, request_fingerprint


def window(hours=24):
    values = np.full((720, 5), 0.1)
    values[:, 0] = 120 + 20 * np.sin(np.arange(720) / 15)
    values[:, 1:3] = np.nan
    values[350, 1] = 35.5
    values[349, 2] = 2.25
    series = SubjectSeries("synthetic", "Loop", np.arange(720) * STEP_NS, values)
    return build_window(series, 350, hours=hours)


def test_backbone_request_matches_original_c2_and_cannot_receive_labels():
    long = window_to_example(window(), with_covariates=True).request
    six = {**window(6), "split": "validation"}
    expected = request_for(six, "chronos_c2_6h")
    assert request_fingerprint(c2_request(long)) == request_fingerprint(expected)
    assert len(c2_request(long).target_history) == 72
    assert "insulin_total" not in {s.name for s in c2_request(long).past_covariates}
    changed = {**window(), "truth": [999] * 24, "sid": "other"}
    request = window_to_example(changed, with_covariates=True).request
    assert c2_request(request) == c2_request(long)
    with pytest.raises(ValueError, match="six hours"):
        c2_request(replace(long, target_history=long.target_history[-24:]))


def test_training_cache_retains_failures_without_retry_and_rejects_tampering(tmp_path):
    w = {**window(6), "split": "train"}
    calls = []

    def failing(request):
        calls.append(request)
        assert not hasattr(request, "truth")
        raise ModelInferenceError("synthetic")

    path = tmp_path / "training.jsonl"
    rows = cache_training({w["event_id"]: w}, failing, path)
    assert len(calls) == 1 and rows[0]["error_type"] == "ModelInferenceError"
    assert "truth" not in rows[0]
    assert cache_training({w["event_id"]: w}, failing, path) == rows
    assert len(calls) == 1
    payload = json.loads(path.read_text())
    payload["error_type"] = None
    path.write_text(json.dumps(payload) + "\n")
    with pytest.raises(ValueError, match="cache"):
        cache_training({w["event_id"]: w}, failing, path)


def test_cache_rejects_nontraining_role_before_any_predictor_call(tmp_path):
    w = {**window(6), "split": "calibration"}
    with pytest.raises(ValueError, match="training role"):
        cache_training(
            {w["event_id"]: w}, lambda request: pytest.fail("role leak"), tmp_path / "rows.jsonl"
        )


@pytest.mark.parametrize("algorithm,parameter", [("ridge", 10), ("lightgbm", 15)])
def test_residual_head_uses_frozen_baseline_and_saves_no_backbone(tmp_path, algorithm, parameter):
    import joblib
    from research.models.adapters.base import ForecastResult, QuantileForecast, ModelNotLoadedError
    from research.models.adapters.chronos2 import CHRONOS2_MODEL_ID, CHRONOS2_MODEL_REVISION
    from research.models.adapters.metabonet_residual import MetaboNetResidualAdapter
    from research.models.adapters.metabonet_tabular import request_features

    request = window_to_example(window(), with_covariates=True).request
    x, _ = request_features(request, history_hours=24, profile="events")
    current = request.target_history[-1].value
    baseline = tuple(current + i for i in range(24))
    short = c2_request(request)
    result = ForecastResult(
        CHRONOS2_MODEL_ID,
        CHRONOS2_MODEL_REVISION,
        short.context_start,
        short.context_end,
        short.forecast_timestamps,
        baseline,
        tuple(QuantileForecast(q, baseline) for q in short.quantiles),
        0,
    )

    class Backbone:
        calls = 0

        def predict(self, given):
            self.calls += 1
            assert given == short
            return result

    backbone = Backbone()
    head = MetaboNetResidualAdapter(algorithm=algorithm, parameter=parameter, backbone=backbone)
    head.fit_arrays(
        np.tile(x, (8, 1)),
        np.full((8, 24), current + 5),
        np.full(8, current),
        np.tile(baseline, (8, 1)),
    )
    assert backbone.calls == 0  # Head fitting never trains or even calls the backbone.
    before = joblib.hash(head)
    forecast = head.predict(request)
    assert backbone.calls == 1 and len(forecast.median) == 24
    assert dict(forecast.metadata)["interval"] == "none"
    assert dict(forecast.metadata)["timing"] == "backbone_plus_head"
    assert joblib.hash(head) == before
    path = tmp_path / "head.joblib"
    joblib.dump(head, path)
    restored = joblib.load(path)
    with pytest.raises(ModelNotLoadedError, match="backbone"):
        restored.predict(request)
    assert restored.predict_from_baseline(request, result).median == forecast.median
    assert restored.attach_backbone(backbone).predict(request).median == forecast.median
    with pytest.raises(ValueError, match="identity|origin"):
        restored.predict_from_baseline(request, replace(result, model_version="different"))
    with pytest.raises(ValueError, match="baseline"):
        restored.predict_array(x[None, :], np.array([current]), np.full((1, 24), np.nan))


def test_correction_cv_keeps_subjects_and_baselines_aligned(tmp_path, monkeypatch):
    import research.pipelines.run_metabonet_correction as runner

    fits = []

    class Spy:
        def fit_arrays(self, x, y, current, baseline, *, sample_weight):
            self.fit_rows = set(x[:, 0])
            assert np.array_equal(baseline[:, 0], x[:, 0] + 100)
            fits.append(self.fit_rows)

        def predict_array(self, x, current, baseline):
            assert not self.fit_rows & set(x[:, 0])
            assert np.array_equal(baseline[:, 0], x[:, 0] + 100)
            return np.repeat(current[:, None], 24, axis=1)

    monkeypatch.setattr(runner, "make_model", lambda config: Spy())
    values = dict(
        x=np.arange(12, dtype=float)[:, None],
        y=np.full((12, 24), 120.0),
        current=np.full(12, 120.0),
        baseline=np.repeat((np.arange(12) + 100)[:, None], 24, axis=1),
        subjects=[f"synthetic{i // 2}" for i in range(12)],
    )
    folds = {f"synthetic{i}": i % 3 for i in range(6)}
    config = dict(name="ridge_residual_10", kind="residual", algorithm="ridge", parameter=10)
    result = runner.cross_validate(config, values, folds, tmp_path, "execution")
    assert len(fits) == 3 and result["macro_mae"] == 0
    assert runner.cross_validate(config, values, folds, tmp_path, "execution") == result
    assert len(fits) == 3
    with (tmp_path / "cv-ridge_residual_10.npy").open("ab") as stream:
        stream.write(b"changed")
    with pytest.raises(ValueError, match="cache"):
        runner.cross_validate(config, values, folds, tmp_path, "execution")


def test_backbone_failure_stays_in_validation_attempt_denominator(tmp_path):
    from research.pipelines.run_metabonet_correction import evaluate
    from research.pipelines.run_metabonet_inference import record_checksum

    w = {**window(), "split": "validation"}
    request = c2_request(window_to_example(w, with_covariates=True).request)
    row = dict(
        event_id=w["event_id"],
        participant_id=w["sid"],
        truth=w["truth"],
        request_sha256=request_fingerprint(request),
        error_type="ModelInferenceError",
        prediction=[],
    )
    row["row_sha256"] = record_checksum(row)

    class Never:
        def predict_array(self, *args):
            pytest.fail("failed backbone must not be replaced by a correction")

    config = dict(name="ridge_residual_10", kind="residual")
    rows, metadata = evaluate(
        Never(), config, {w["event_id"]: w}, {w["event_id"]: row}, tmp_path, "model"
    )
    assert len(rows) == 1 and rows[0]["error_type"] == "BackboneUnavailable"
    assert metadata["events"] == 1 and metadata["failures"] == 1


def test_incremental_gate_requires_five_percent_and_preserves_tolerance():
    from research.pipelines.run_metabonet_correction import incremental_gate

    baseline = dict(
        failure_count=0,
        participant_macro=dict(mae=10, within_10=0.4),
        point_metrics=dict(absolute_error_p95=30),
    )
    good = {**baseline, "participant_macro": dict(mae=9.5, within_10=0.4)}
    assert incremental_gate(good, baseline)["passes"]
    for changed in (
        {**good, "failure_count": 1},
        {**good, "participant_macro": dict(mae=9.6, within_10=0.4)},
        {**good, "participant_macro": dict(mae=9.5, within_10=0.39)},
        {**good, "point_metrics": dict(absolute_error_p95=31)},
    ):
        assert not incremental_gate(changed, baseline)["passes"]


def test_fitted_head_validation_roundtrip_and_corrupt_load_guard(tmp_path, monkeypatch):
    import research.pipelines.run_metabonet_correction as runner
    from research.models.adapters.metabonet_tabular import request_features
    from research.pipelines.run_metabonet_inference import record_checksum

    w = {**window(), "split": "validation"}
    request = window_to_example(w, with_covariates=True).request
    x, _ = request_features(request, history_hours=24, profile="events")
    current = request.target_history[-1].value
    baseline = [current + i for i in range(24)]
    values = dict(
        ids=[str(i) for i in range(8)],
        subjects=[f"synthetic{i // 2}" for i in range(8)],
        x=np.tile(x, (8, 1)),
        y=np.tile(w["truth"], (8, 1)),
        current=np.full(8, current),
        baseline=np.tile(baseline, (8, 1)),
    )
    config = runner.GRID[0]
    model, metadata = runner.fit_final(config, values, tmp_path, "execution")
    row = dict(
        event_id=w["event_id"],
        participant_id=w["sid"],
        truth=w["truth"],
        request_sha256=request_fingerprint(c2_request(request)),
        error_type=None,
        prediction=baseline,
    )
    row["row_sha256"] = record_checksum(row)
    rows, info = runner.evaluate(
        model, config, {w["event_id"]: w}, {w["event_id"]: row}, tmp_path, metadata["model_sha256"]
    )
    assert info["failures"] == 0 and rows[0]["metrics"]["mae"] >= 0
    assert all(type(p) is float for p in rows[0]["prediction"])
    assert (
        runner.evaluate(
            model,
            config,
            {w["event_id"]: w},
            {w["event_id"]: row},
            tmp_path,
            metadata["model_sha256"],
        )[0]
        == rows
    )
    with (tmp_path / f"model-{config['name']}.joblib").open("ab") as stream:
        stream.write(b"changed")
    monkeypatch.setattr(runner.joblib, "load", lambda *a: pytest.fail("unverified deserialization"))
    with pytest.raises(ValueError, match="model changed"):
        runner.fit_final(config, values, tmp_path, "execution")


def test_point_estimate_winner_does_not_bypass_advancement_gate():
    from research.evaluation.refinement_metrics import event_metrics
    from research.pipelines.run_metabonet_correction import analyze

    runs = {}
    for name, error in (
        ("persistence", 20),
        ("lightgbm_direct", 10),
        ("ridge_control", 9.9),
        ("ridge_residual_10", 9.6),
    ):
        truth, prediction = [100.0] * 24, [100.0 + error] * 24
        runs[name] = [
            dict(
                event_id="synthetic",
                participant_id="synthetic",
                source="Loop",
                truth=truth,
                prediction=prediction,
                metrics=event_metrics(truth, prediction),
                error_type=None,
                wall_ms=0,
            )
        ]
    summary = analyze(runs, {"synthetic": dict(source="Loop")}, ["ridge_residual_10"])
    assert summary["selected_candidate"] == "ridge_residual_10"
    assert summary["advancement_candidate"] == "lightgbm_direct"
    assert not summary["incremental_correction_gates"]["ridge_residual_10"]["passes"]
