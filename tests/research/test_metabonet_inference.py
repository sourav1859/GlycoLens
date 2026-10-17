import json
from dataclasses import replace

import numpy as np
import pytest

from research.datasets.metabonet import STEP_NS, SubjectSeries, build_window
from research.models.adapters.base import ModelInferenceError, TimePoint
from research.pipelines.run_metabonet_inference import (
    analyze_runs,
    collect_validation,
    evaluate_variant,
    execution_guard,
    request_fingerprint,
    request_for,
)


def windows():
    values = np.full((720, 5), 0.1)
    values[:, 0] = 120 + 20 * np.sin(np.arange(720) / 15)
    values[:, 1:3] = np.nan
    values[350, 1] = 35.5
    values[349, 2] = 2
    series = SubjectSeries("synthetic", "Loop", np.arange(720) * STEP_NS, values)
    return {
        h: {**build_window(series, 350, hours=h), "split": "validation"} for h in (2, 6, 12, 24)
    }


def test_validation_only_matching_and_target_identity():
    variants = windows()
    calls = []

    def reader(directory, *, split, hours, delay):
        calls.append((split, delay))
        return iter([variants[hours]])

    matched, cohort = collect_validation(None, reader=reader)
    assert cohort["matched_event_count"] == 1
    assert calls == [("validation", 5)] * 4
    assert set(matched) == {2, 6, 12, 24}
    variants[24]["truth"] = [999] * 24
    with pytest.raises(ValueError, match="targets"):
        collect_validation(None, reader=reader)


def test_context_units_masks_and_request_only_fingerprint():
    window = windows()[6]
    c0 = request_for(window, "chronos_c0_6h")
    c1 = request_for(window, "chronos_c1_6h")
    c2 = request_for(window, "chronos_c2_6h")
    assert not c0.past_covariates and not c0.known_covariates
    names = {c.name for c in c1.past_covariates}
    assert "insulin_total" not in names
    assert {"insulin_bolus", "insulin_bolus_record_present", "cgm_record_present"} <= names
    assert not c1.known_covariates
    assert c2.known_covariates[0].points[0].value == 35.5
    changed = {**window, "truth": [999] * 24, "sid": "different", "source": "ReplaceBG"}
    assert request_fingerprint(c2) == request_fingerprint(request_for(changed, "chronos_c2_6h"))
    assert request_fingerprint(c1) != request_fingerprint(c2)
    altered = replace(c0, target_history=(*c0.target_history[:-1], TimePoint(c0.context_end, 90)))
    assert request_fingerprint(c0) != request_fingerprint(altered)


def test_attempts_failures_resume_and_corrupt_progress(tmp_path):
    window = windows()[6]
    path = tmp_path / "rows.jsonl"
    calls = []

    def failing(request):
        calls.append(request)
        raise ModelInferenceError("synthetic failure")

    rows = evaluate_variant({window["event_id"]: window}, "chronos_c0_6h", failing, path)
    assert len(rows) == 1 and rows[0]["error_type"] == "ModelInferenceError"
    assert evaluate_variant({window["event_id"]: window}, "chronos_c0_6h", failing, path) == rows
    assert len(calls) == 1  # Failed forecasts are attempts, never retried to improve scores.
    original = path.read_text()
    altered = json.loads(original)
    altered["error_type"] = None
    path.write_text(json.dumps(altered) + "\n")
    with pytest.raises(ValueError, match="progress"):
        evaluate_variant({window["event_id"]: window}, "chronos_c0_6h", failing, path)
    path.write_text(original)
    changed = {**window, "history": [90] * 72}
    with pytest.raises(ValueError, match="progress"):
        evaluate_variant({window["event_id"]: changed}, "chronos_c0_6h", failing, path)
    path.write_text("{broken")
    with pytest.raises(ValueError, match="progress"):
        evaluate_variant({window["event_id"]: window}, "chronos_c0_6h", failing, path)


def test_failed_candidate_cannot_shrink_selection_or_hide_poor_accuracy():
    window = windows()[6]
    base = {
        "event_id": "synthetic",
        "participant_id": "synthetic",
        "source": "Loop",
        "truth": [100] * 24,
        "prediction": [120] * 24,
        "error_type": None,
        "wall_ms": 1,
        "lower": [],
        "upper": [],
    }
    runs = {
        "persistence": [base],
        "chronos_c0_6h": [{**base, "prediction": [110] * 24}],
        "chronos_c0_24h": [{**base, "error_type": "ModelInferenceError", "prediction": []}],
    }
    result = analyze_runs(runs, {"synthetic": window})
    assert result["selected_history_hours"] == 6
    assert result["selected_frozen_candidate"] == "chronos_c0_6h"
    assert result["selection_summary"]["common_success_event_count"] == 1
    assert result["all_run_summary"]["common_success_event_count"] == 0
    assert result["pairs"]["chronos_c0_24h"]["runs"]["chronos_c0_24h"]["failure_count"] == 1
    assert result["selection_gate"]["passes"]
    assert (
        result["selection_summary"]["runs"]["chronos_c0_6h"]["participant_macro"]["within_10"] == 1
    )
    boundary = {
        "persistence": [{**base, "prediction": [200] * 24}],
        "chronos_c0_6h": [{**base, "prediction": [190] * 24}],
    }
    assert analyze_runs(boundary, {"synthetic": window})["selection_gate"]["passes"]


def test_execution_guard_rejects_changed_configuration_and_completed_replay(tmp_path):
    path = tmp_path / "run"
    execution_guard(path, {"input": "synthetic", "settings": 1}, {})
    execution_guard(path, {"input": "synthetic", "settings": 1}, {})
    with pytest.raises(ValueError, match="execution"):
        execution_guard(path, {"input": "synthetic", "settings": 2}, {})
    (path / "complete.json").write_text(json.dumps({}))
    with pytest.raises(ValueError, match="completed"):
        execution_guard(path, {"input": "synthetic", "settings": 1}, {})
