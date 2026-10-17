from dataclasses import replace

import joblib
import numpy as np
import pytest

from research.datasets.metabonet import STEP_NS, SubjectSeries, build_window, window_to_example
from research.models.adapters.base import ModelNotLoadedError, TimePoint
from research.models.adapters.metabonet_tabular import MetaboNetTabularAdapter, request_features
from research.pipelines.run_metabonet_training import (
    choose_cv,
    collect_training,
    cross_validate,
    evaluate_direct,
    fit_final,
    participant_weights,
    subject_folds,
)


def example(hours=6, shift=0):
    values = np.full((720, 5), 0.1)
    values[:, 0] = 120 + shift + 20 * np.sin(np.arange(720) / 15)
    values[:, 1:3] = np.nan
    values[350, 1] = 35.5
    values[349, 2] = 2.25
    series = SubjectSeries("synthetic", "Loop", np.arange(720) * STEP_NS, values)
    window = build_window(series, 350, hours=hours)
    return window_to_example(window, with_covariates=True), window


def test_features_are_origin_only_and_preserve_units_masks_and_fractional_values():
    ex, window = example()
    vector, names = request_features(ex.request, history_hours=6, profile="events")
    assert vector[names.index("meal_carbs_g")] == 35.5
    assert vector[names.index("bolus_recorded_sum_30m")] == 2.25
    assert 0 < vector[names.index("bolus_present_fraction_30m")] < 1
    assert vector[names.index("basal_recorded_sum_30m")] == pytest.approx(0.6)
    changed = {**window, "truth": [999] * 24, "sid": "other", "source": "ReplaceBG"}
    altered = window_to_example(changed, with_covariates=True)
    assert np.array_equal(
        vector,
        request_features(altered.request, history_hours=6, profile="events")[0],
        equal_nan=True,
    )
    assert not any("total" in n or "source" in n or "subject" in n for n in names)
    cgm, _ = request_features(ex.request, history_hours=6, profile="cgm")
    meal = replace(ex.request.known_covariates[0], points=(TimePoint(ex.request.context_end, 80),))
    assert np.array_equal(
        cgm,
        request_features(
            replace(ex.request, known_covariates=(meal,)), history_hours=6, profile="cgm"
        )[0],
    )
    bad = replace(ex.request.past_covariates[0], unit="IU_per_hour")
    with pytest.raises(ValueError, match="unit"):
        request_features(
            replace(ex.request, past_covariates=(bad, *ex.request.past_covariates[1:])),
            history_hours=6,
            profile="events",
        )


def test_unknown_events_do_not_become_confirmed_zero_and_history_is_enforced():
    ex, _ = example()
    past = tuple(
        replace(s, points=tuple(TimePoint(p.timestamp, 0) for p in s.points))
        if s.name == "insulin_bolus_record_present"
        else s
        for s in ex.request.past_covariates
        if s.name != "insulin_bolus"
    )
    values, names = request_features(
        replace(ex.request, past_covariates=past), history_hours=6, profile="events"
    )
    assert np.isnan(values[names.index("bolus_recorded_sum_30m")])
    assert values[names.index("bolus_present_fraction_30m")] == 0
    with pytest.raises(ValueError, match="history"):
        request_features(ex.request, history_hours=24, profile="cgm")


def test_training_reader_never_consumes_validation_calibration_or_test():
    _, window = example()
    calls = []

    def reader(path, *, split, hours, delay):
        calls.append(split)
        return iter([{**window, "history_hours": hours, "split": "train"}])

    values, summary = collect_training(None, reader=reader)
    assert calls == ["train"] * 4 and summary["common_event_count"] == 1
    assert len(values) == 4


def test_subject_folds_and_weights_use_no_outcomes_or_identity_predictors():
    rows = [{"sid": f"{s}{i}", "source": s} for s in ("Loop", "ReplaceBG") for i in range(9)]
    folds = subject_folds(rows)
    assert folds == subject_folds(list(reversed(rows)))
    assert set(folds.values()) == {0, 1, 2}
    for fold in range(3):
        assert all(
            any(folds[r["sid"]] == fold and r["source"] == s for r in rows)
            for s in ("Loop", "ReplaceBG")
        )
    ids = ["a", "a", "b"]
    weights = participant_weights(ids)
    assert weights[0] + weights[1] == weights[2]
    assert weights.mean() == pytest.approx(1)


@pytest.mark.parametrize("algorithm,parameter", [("ridge", 10), ("lightgbm", 15)])
def test_train_only_fit_common_contract_and_trusted_reload(tmp_path, algorithm, parameter):
    samples = [example(shift=i)[0] for i in range(8)]
    model = MetaboNetTabularAdapter(
        algorithm=algorithm, parameter=parameter, history_hours=6, profile="events"
    )
    with pytest.raises(ModelNotLoadedError):
        model.predict(samples[0].request)
    model.fit([s.request for s in samples], [[p.value for p in s.target.points] for s in samples])
    before = joblib.hash(model)
    result = model.predict(example(shift=500)[0].request)
    assert len(result.median) == 24 and np.isfinite(result.median).all()
    assert dict(result.metadata)["interval"] == "none"
    assert before == joblib.hash(model)  # Prediction cannot refit imputation/scaling/weights.
    path = tmp_path / "trusted.joblib"
    joblib.dump(model, path)
    restored = joblib.load(path)
    assert restored.predict(samples[0].request).median == model.predict(samples[0].request).median


def test_failed_cv_candidates_are_ineligible_without_validation_selection():
    rows = [
        {"name": "bad", "algorithm": "ridge", "failure_count": 1, "macro_mae": 0, "within_10": 1},
        {
            "name": "good",
            "algorithm": "ridge",
            "failure_count": 0,
            "macro_mae": 20,
            "within_10": 0.3,
        },
    ]
    assert choose_cv(rows, "ridge")["name"] == "good"
    with pytest.raises(ValueError, match="eligible"):
        choose_cv(rows, "lightgbm")


def toy_frame():
    return {
        "ids": [str(i) for i in range(12)],
        "subjects": [f"synthetic{i // 2}" for i in range(12)],
        "x": np.arange(24, dtype=float).reshape(12, 2),
        "y": np.full((12, 24), 120.0),
        "current": np.full(12, 120.0),
        "feature_names": ("a", "b"),
    }


def test_cv_splits_before_fit_and_resume_rejects_changed_predictions(tmp_path, monkeypatch):
    import research.pipelines.run_metabonet_training as runner

    fits = []

    class SpyModel:
        def __init__(self, **kwargs):
            pass

        def fit_arrays(self, x, y, current, *, sample_weight):
            self.fitted = set(x[:, 0])
            fits.append(self.fitted)

        def predict_array(self, x, current):
            assert not self.fitted & set(x[:, 0])
            return np.repeat(current[:, None], 24, axis=1)

    monkeypatch.setattr(runner, "MetaboNetTabularAdapter", SpyModel)
    values = toy_frame()
    folds = {s: i % 3 for i, s in enumerate(sorted(set(values["subjects"])))}
    config = dict(name="toy", algorithm="ridge", parameter=10, history_hours=2, profile="cgm")
    result = cross_validate(config, values, folds, tmp_path, "execution")
    assert len(fits) == 3 and result["macro_mae"] == 0
    assert cross_validate(config, values, folds, tmp_path, "execution") == result
    assert len(fits) == 3  # Completed CV is verified, never silently refitted.
    with (tmp_path / "cv-toy.npy").open("ab") as stream:
        stream.write(b"changed")
    with pytest.raises(ValueError, match="progress changed"):
        cross_validate(config, values, folds, tmp_path, "execution")


def test_model_resume_checks_bytes_before_deserialization(tmp_path, monkeypatch):
    import research.pipelines.run_metabonet_training as runner

    config = dict(name="toy", algorithm="ridge", parameter=10, history_hours=2, profile="cgm")
    _, metadata = fit_final(config, toy_frame(), tmp_path, "execution")
    assert metadata["reload_prediction_equivalent"]
    with (tmp_path / "model-ridge.joblib").open("ab") as stream:
        stream.write(b"changed")

    def forbidden_load(*args, **kwargs):
        pytest.fail("unverified model bytes must never be deserialized")

    monkeypatch.setattr(runner.joblib, "load", forbidden_load)
    with pytest.raises(ValueError, match="saved model"):
        fit_final(config, toy_frame(), tmp_path, "execution")


def test_training_verification_does_not_inherit_inference_only_flags(tmp_path, monkeypatch):
    import json

    import research.pipelines.run_metabonet_training as runner

    monkeypatch.setattr(runner, "verify_completed", lambda path: {"weights_fitted": False})
    monkeypatch.setattr(
        runner, "read_execution", lambda path: {"configuration": {"version": runner.VERSION}}
    )
    (tmp_path / "summary.json").write_text(
        json.dumps(
            dict(
                weights_fitted=True,
                calibration_or_test_access=False,
                fit_metadata={"ridge": {}, "lightgbm": {}},
            )
        )
    )
    result = runner.verify_training_completed(tmp_path)
    assert result["weights_fitted"] is True and result["saved_model_count"] == 2
    assert result["calibration_or_test_access"] is False


def test_batch_validation_converts_numpy_numbers_before_statistics_and_json(tmp_path):
    _, window = example()
    window = {**window, "split": "validation"}

    class BatchModel:
        def predict_array(self, x, current):
            return np.repeat(current[:, None], 24, axis=1)

    config = dict(algorithm="ridge", history_hours=6, profile="events")
    rows, metadata = evaluate_direct(
        BatchModel(), config, {window["event_id"]: window}, tmp_path, "synthetic"
    )
    assert metadata["event_count"] == 1
    assert isinstance(rows[0]["metrics"]["within_10"], float)
    assert all(type(p) is float for p in rows[0]["prediction"])


def test_scoring_repair_rejects_any_change_beyond_numeric_conversion():
    from research.pipelines.complete_metabonet_training import verify_scoring_patch

    original = b"prediction = list(predictions[index]) if predictions is not None else []\n"
    corrected = (
        b"prediction = [float(v) for v in predictions[index]] if predictions is not None else []\n"
    )
    verify_scoring_patch(original, corrected)
    with pytest.raises(ValueError, match="only the native-float"):
        verify_scoring_patch(original, corrected + b"changed_training_parameters = True\n")
