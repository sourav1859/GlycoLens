import copy
import json
from dataclasses import FrozenInstanceError

import numpy as np
import pytest

from research.datasets.metabonet import STEP_NS, SubjectSeries, build_window, window_to_example
from research.evaluation.metabonet_uncertainty import (
    CalibratedForecastAdapter,
    SymmetricBands,
    calibration_representatives,
    interval_summary,
)
from research.models.adapters.persistence import PersistenceForecastAdapter
from research.pipelines.run_metabonet_independent import (
    CANDIDATES,
    PRIMARY,
    VERSION,
    evaluate_windows,
    finish,
    prepare_reserved,
    require_calibration_gate,
    reserved_subject_windows,
    verify_phase6_stage,
)
from research.pipelines.run_metabonet_inference import execution_guard
from research.pipelines.run_metabonet_training import freeze_json


def window(sid="synthetic", role="calibration"):
    values = np.full((720, 5), 0.1)
    values[:, 0] = 120 + 20 * np.sin(np.arange(720) / 15)
    values[:, 1] = np.nan
    values[350, 1] = 35.5
    series = SubjectSeries(sid, "Loop", np.arange(720) * STEP_NS, values)
    return {**build_window(series, 350, hours=24), "split": role}


def test_calibration_uses_one_event_per_subject_independent_of_values():
    rows = [window("a"), window("b")]
    rows.append({**rows[0], "event_id": "another", "truth": [999.0] * 24})
    selected = calibration_representatives(rows)
    changed = [{**r, "truth": [1.0] * 24, "meal_carbs_g": 1000} for r in rows]
    assert [r["event_id"] for r in selected] == [
        r["event_id"] for r in calibration_representatives(changed)
    ]
    assert len(selected) == 2
    with pytest.raises(ValueError, match="calibration role"):
        calibration_representatives([window(role="primary_test")])
    with pytest.raises(ValueError, match="duplicate"):
        calibration_representatives([rows[0], rows[0]])


def test_bands_use_exact_finite_sample_rank_and_separate_curve_radius():
    prediction = np.full((9, 24), 100.0)
    truth = prediction + np.arange(1, 10)[:, None]
    truth[:, 0] += 20
    bands = SymmetricBands.fit(truth, prediction)
    # ceil((9+1)*.8)=8: the eighth smallest, not an interpolated percentile.
    assert bands.radii[0] == 28 and bands.radii[1] == 8
    assert bands.curve_radius == 28
    assert bands.participant_count == 9
    with pytest.raises(FrozenInstanceError):
        bands.curve_radius = 0
    assert SymmetricBands.from_dict(bands.to_dict()) == bands
    with pytest.raises(ValueError, match="insufficient"):
        SymmetricBands.fit(truth[:2], prediction[:2])
    with pytest.raises(ValueError, match="finite"):
        SymmetricBands.fit(truth, prediction * np.nan)


def test_calibration_adapter_preserves_point_forecast_request_and_state():
    adapter = PersistenceForecastAdapter()
    adapter.load()
    request = window_to_example(window(), with_covariates=True).request
    state, original = copy.deepcopy(adapter.__dict__), copy.deepcopy(request)
    bands = SymmetricBands(tuple([200.0] * 24), 250.0, 0.8, 9)
    result = CalibratedForecastAdapter(adapter, bands).predict(request)
    assert result.median == adapter.predict(request).median
    assert result.quantiles[0].values[0] < 0  # Do not clip negative lower endpoints.
    assert result.quantiles[-1].values[0] - result.median[0] == 200
    assert dict(result.metadata)["interval"] == "participant_representative_marginal_80"
    assert request == original and adapter.__dict__ == state


def test_interval_summary_distinguishes_marginal_curve_and_attempt_yields():
    truth = [100.0] * 24
    row = {
        "participant_id": "a",
        "truth": truth,
        "prediction": truth,
        "lower": [99.0] * 24,
        "upper": [101.0] * 24,
        "curve_lower": [98.0] * 24,
        "curve_upper": [102.0] * 24,
        "error_type": None,
    }
    other = {**row, "participant_id": "b", "truth": [100.0] * 23 + [103.0]}
    failed = {**row, "participant_id": "c", "error_type": "ModelInferenceError"}
    result = interval_summary([row, other, failed])
    assert result["marginal"]["macro_point_coverage"] == 47 / 48
    assert result["marginal"]["macro_whole_curve_coverage"] == 0.5
    assert result["curve"]["mean_width"] == 4
    assert result["marginal"]["attempted_whole_curve_yield"] == 1 / 3


def test_reserved_access_requires_verified_calibration_completion(tmp_path):
    with pytest.raises((ValueError, FileNotFoundError)):
        require_calibration_gate(tmp_path)
    (tmp_path / "complete.json").write_text(json.dumps({"version": "wrong"}))
    with pytest.raises((ValueError, FileNotFoundError)):
        verify_phase6_stage(tmp_path, "calibration")


def test_verified_calibration_gate_detects_band_and_source_corruption(tmp_path):
    directory = tmp_path / "calibration"
    source = tmp_path / "source.py"
    source.write_text("# synthetic execution source\n")
    execution_guard(directory, {"version": VERSION, "stage": "calibration"}, {"source.py": source})
    band = SymmetricBands(tuple([10.0] * 24), 20, 0.8, 9)
    freeze_json(
        directory / "bands.json",
        {
            "primary_candidate": PRIMARY,
            "models": {name: band.to_dict() for name in CANDIDATES},
        },
    )
    finish(
        directory,
        {"stage": "calibration", "point_weights_fitted": False, "test_values_read": False},
    )
    assert require_calibration_gate(directory)[PRIMARY] == band
    with pytest.raises(ValueError, match="completed"):
        execution_guard(directory, {}, {})
    original = (directory / "bands.json").read_bytes()
    (directory / "bands.json").write_bytes(original + b" ")
    with pytest.raises(ValueError, match="changed"):
        require_calibration_gate(directory)


def test_missing_gate_blocks_raw_projection_before_any_connection(tmp_path, monkeypatch):
    import research.pipelines.run_metabonet_independent as pipeline

    def forbidden(*args, **kwargs):
        pytest.fail("reserved data projection was reached before calibration gate")

    monkeypatch.setattr(pipeline.duckdb, "connect", forbidden)
    with pytest.raises((ValueError, FileNotFoundError)):
        prepare_reserved(tmp_path, tmp_path, tmp_path, tmp_path / "missing")


def test_reserved_windows_do_not_borrow_across_publisher_files_or_replace_candidates():
    w = window()
    n = 720
    values = np.full((n, 5), 0.1)
    values[:, 0] = np.arange(n) % 100 + 80
    values[:, 1] = np.nan
    values[350, 1] = 35.5
    series = SubjectSeries("s", "PEDAP", np.arange(n) * STEP_NS, values)
    # Split immediately after origin: the complete combined series could succeed,
    # but the training segment has no complete target. No borrowing is permitted.
    segments = [
        SubjectSeries("s", "PEDAP", series.times[:352], series.values[:352]),
        SubjectSeries("s", "PEDAP", series.times[352:], series.values[352:]),
    ]
    rows, quality = reserved_subject_windows(segments, "source_test")
    assert not rows and quality["rejected"]["incomplete_target"] == 1
    assert quality["sampled_candidate_count"] == 1
    assert w["history_hours"] == 24


def test_duplicate_timestamp_segments_quarantine_subject():
    values = np.full((400, 5), 1.0)
    values[:, 0] = 120
    series = SubjectSeries("s", "PEDAP", np.arange(400) * STEP_NS, values)
    rows, quality = reserved_subject_windows([series, series], "source_test")
    assert not rows and quality["status"] == "duplicate_cross_file_timestamps"


def test_prediction_failure_is_retained_once_and_cannot_be_replayed(tmp_path):
    w = window(role="primary_test")
    calls = []

    class Broken:
        def predict(self, request):
            calls.append(request)
            assert not hasattr(request, "truth")
            raise RuntimeError("synthetic")

    path = tmp_path / "rows.jsonl"
    bands = SymmetricBands(tuple([10.0] * 24), 20, 0.8, 9)
    rows, _ = evaluate_windows([w], {"broken": Broken()}, {"broken": bands}, path)
    assert rows["broken"][0]["error_type"] == "RuntimeError" and len(calls) == 1
    with pytest.raises(ValueError, match="exists"):
        evaluate_windows([w], {"broken": Broken()}, {"broken": bands}, path)
    assert len(calls) == 1


def test_evaluation_rejects_mixed_roles_and_uses_no_future_values_in_request(tmp_path):
    adapter = PersistenceForecastAdapter()
    adapter.load()
    w = window(role="primary_test")
    rows, _ = evaluate_windows([w], {"persistence": adapter}, None, tmp_path / "one.jsonl")
    changed = {**w, "truth": [999.0] * 24}
    altered, _ = evaluate_windows([changed], {"persistence": adapter}, None, tmp_path / "two.jsonl")
    assert rows["persistence"][0]["prediction"] == altered["persistence"][0]["prediction"]
    assert rows["persistence"][0]["request_sha256"] == altered["persistence"][0]["request_sha256"]
    with pytest.raises(ValueError, match="role"):
        evaluate_windows([w, window("other", "calibration")], {}, None, tmp_path / "bad.jsonl")
