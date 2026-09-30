from __future__ import annotations

import json
import math
import os
from pathlib import Path

import pytest

from research.pipelines import run_pymgipsim_scenario as pipeline
from research.simulation.adapter import (
    PYMGIPSIM_COMMIT,
    PyMgipsimError,
    PyMgipsimResult,
    PyMgipsimScenario,
    run_pymgipsim_scenario,
)


def _valid_payload() -> dict[str, object]:
    values = [108.0 + index / 100 for index in range(288)]
    return {
        "schema_version": "1.0",
        "source": "py-mgipsim",
        "upstream_commit": PYMGIPSIM_COMMIT,
        "scenario_name": "m1_fixed_meal_day",
        "model": "T1DM.ExtHovorka",
        "controller": "OpenLoop",
        "random_seed": 20260929,
        "duration_minutes": 1440,
        "sample_interval_minutes": 5,
        "sample_count": len(values),
        "meal_event_count": 3,
        "meal_carbohydrate_total_g": 210.0,
        "glucose_summary_mg_dl": {
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
            "start": values[0],
            "end": values[-1],
        },
        "trajectory": [
            {"minute": index * 5, "glucose_mg_dl": value} for index, value in enumerate(values)
        ],
    }


def test_fixed_scenario_rejects_unreviewed_protocol_changes() -> None:
    with pytest.raises(ValueError, match="random seed"):
        PyMgipsimScenario(random_seed=1)
    with pytest.raises(ValueError, match="one day"):
        PyMgipsimScenario(duration_days=2)
    with pytest.raises(ValueError, match="synthetic virtual subject"):
        PyMgipsimScenario(virtual_subject_file="Patient_2.json")
    with pytest.raises(ValueError, match="ExtHovorka/OpenLoop"):
        PyMgipsimScenario(controller="SAPT")


def test_result_contract_accepts_valid_relative_time_trajectory(tmp_path: Path) -> None:
    path = tmp_path / "result.json"
    path.write_text(json.dumps(_valid_payload()), encoding="utf-8")

    result = PyMgipsimResult.from_json(path)

    assert result.sample_count == 288
    assert result.trajectory[0].minute == 0
    assert result.trajectory[-1].minute == 1435
    assert result.meal_carbohydrate_total_g == 210.0


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda payload: payload.update(sample_count=287), "sample count"),
        (lambda payload: payload.update(random_seed=1), "random seed"),
        (
            lambda payload: payload["trajectory"][1].update(minute=6),
            "five-minute grid",
        ),
        (
            lambda payload: payload["trajectory"][1].update(glucose_mg_dl=math.nan),
            "invalid or implausible",
        ),
        (
            lambda payload: payload["glucose_summary_mg_dl"].update(mean=1.0),
            "summary is inconsistent",
        ),
        (lambda payload: payload.update(patient_id="forbidden"), "forbidden field"),
    ],
)
def test_result_contract_fails_closed(mutate, message: str) -> None:
    payload = _valid_payload()
    mutate(payload)

    with pytest.raises(PyMgipsimError, match=message):
        PyMgipsimResult.from_payload(payload)


def test_runner_rejects_missing_source_before_execution(tmp_path: Path) -> None:
    fake_python = tmp_path / "python.exe"
    fake_python.touch()

    with pytest.raises(PyMgipsimError, match="source directory is missing"):
        run_pymgipsim_scenario(
            source_directory=tmp_path / "missing",
            python_executable=fake_python,
            output_json=tmp_path / "result.json",
        )


def test_pipeline_requires_explicit_upstream_execution_opt_in(monkeypatch) -> None:
    monkeypatch.setattr("sys.argv", ["run_pymgipsim_scenario"])

    with pytest.raises(SystemExit, match="allow-upstream-execution"):
        pipeline.main()


@pytest.mark.skipif(
    os.getenv("GLYCOLENS_RUN_PYMGIPSIM") != "1",
    reason="set GLYCOLENS_RUN_PYMGIPSIM=1 after running the isolated installer",
)
def test_real_pymgipsim_scenario_is_reproducible(tmp_path: Path) -> None:
    first_path = tmp_path / "first.json"
    second_path = tmp_path / "second.json"

    first = run_pymgipsim_scenario(
        source_directory=pipeline.DEFAULT_SOURCE,
        python_executable=pipeline.DEFAULT_PYTHON,
        output_json=first_path,
    )
    second = run_pymgipsim_scenario(
        source_directory=pipeline.DEFAULT_SOURCE,
        python_executable=pipeline.DEFAULT_PYTHON,
        output_json=second_path,
    )

    assert first == second
    assert first_path.read_bytes() == second_path.read_bytes()
    serialized = first_path.read_text(encoding="utf-8").lower()
    for forbidden in ("email", "participant_id", "patient_id", "timestamp", "insulin"):
        assert forbidden not in serialized
