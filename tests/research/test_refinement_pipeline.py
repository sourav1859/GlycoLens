import json
from dataclasses import replace

import pytest

from research.pipelines.run_refinement import (
    freeze_selection,
    request_key,
    evaluate,
    persistence,
    intervals,
)
from research.models.adapters.converters import meal_window_to_forecast_example
from tests.research.test_m2_protocol import shifted_window
from research.pipelines import run_refinement


def test_completed_study_rejects_replay_before_any_artifact_is_overwritten(tmp_path, monkeypatch):
    monkeypatch.setattr(run_refinement, "ROOT", tmp_path)
    output = tmp_path / "artifacts" / "frozen"
    output.mkdir(parents=True)
    selection = output / "frozen-selection.json"
    selection.write_text('{"winner":"unchanged"}')
    with pytest.raises(ValueError, match="study is frozen"):
        run_refinement.main(["--uom-root", str(tmp_path / "not-accessed"), "--output", str(output)])
    assert selection.read_text() == '{"winner":"unchanged"}'
    assert list(output.iterdir()) == [selection]


def test_external_selection_is_immutable(tmp_path):
    path = tmp_path / "selection.json"
    initial = freeze_selection(path, {"winner": "persistence"})
    assert freeze_selection(path, {"winner": "persistence"}) == initial
    with pytest.raises(ValueError, match="already frozen"):
        freeze_selection(path, {"winner": "new_model"})
    assert json.loads(path.read_text())["winner"] == "persistence"


def test_backbone_cache_key_ignores_enriched_covariates_but_detects_history():
    request = meal_window_to_forecast_example(shifted_window(0)).request
    assert request_key(request) == request_key(
        replace(request, past_covariates=(), known_covariates=())
    )
    changed = replace(
        request, target_history=tuple(replace(p, value=p.value + 1) for p in request.target_history)
    )
    assert request_key(changed) != request_key(request)


def test_failures_remain_in_attempted_rows_and_calibration_does_not_fit_evaluation():
    request = meal_window_to_forecast_example(shifted_window(0)).request
    samples = [
        {
            "event_id": str(i),
            "participant_id": "synthetic",
            "c0": request,
            "truth": [request.target_history[-1].value + 5] * 24,
        }
        for i in range(6)
    ]
    calibration = evaluate(samples, persistence)
    evaluation = evaluate(
        [{**s, "truth": [s["truth"][0] + 100] * 24} for s in samples], persistence
    )
    report = intervals(calibration, evaluation)
    assert report["mean_width_mg_dl"] == 10
    assert report["participant_macro_coverage"] == 0

    def broken(request):
        raise RuntimeError("private backend details")

    failed = evaluate(samples, broken)
    assert len(failed) == len(samples)
    assert all(r["error_type"] == "RuntimeError" for r in failed)
