"""Project-owned boundary around the source-only py-mgipsim simulator."""

from __future__ import annotations

import json
import math
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PYMGIPSIM_REPOSITORY = "https://github.com/illinoistech-itm/py-mgipsim.git"
PYMGIPSIM_COMMIT = "b985f8c2ea385d1b2b8480957b730866e07772f1"
RESULT_SCHEMA_VERSION = "1.0"


class PyMgipsimError(RuntimeError):
    """A safe, project-owned py-mgipsim integration error."""


@dataclass(frozen=True, slots=True)
class PyMgipsimScenario:
    """The fixed Milestone 1 feasibility scenario.

    These values describe a synthetic research protocol, not food or insulin advice.
    """

    name: str = "m1_fixed_meal_day"
    random_seed: int = 20260929
    duration_days: int = 1
    sample_interval_minutes: int = 5
    virtual_subject_file: str = "Patient_1.json"
    model: str = "T1DM.ExtHovorka"
    controller: str = "OpenLoop"

    def __post_init__(self) -> None:
        if self.name != "m1_fixed_meal_day":
            raise ValueError("Only the reviewed Milestone 1 scenario is supported")
        if self.random_seed != 20260929:
            raise ValueError("The reviewed Milestone 1 random seed is required")
        if self.duration_days != 1:
            raise ValueError("The Milestone 1 scenario must run for exactly one day")
        if self.sample_interval_minutes != 5:
            raise ValueError("The Milestone 1 scenario must use five-minute samples")
        if self.virtual_subject_file != "Patient_1.json":
            raise ValueError("Only the reviewed synthetic virtual subject is supported")
        if self.model != "T1DM.ExtHovorka" or self.controller != "OpenLoop":
            raise ValueError("The reviewed ExtHovorka/OpenLoop configuration is required")


@dataclass(frozen=True, slots=True)
class GlucosePoint:
    minute: int
    glucose_mg_dl: float


@dataclass(frozen=True, slots=True)
class PyMgipsimResult:
    """Validated, privacy-safe result exported from the upstream simulator."""

    schema_version: str
    source: str
    upstream_commit: str
    scenario_name: str
    model: str
    controller: str
    random_seed: int
    duration_minutes: int
    sample_interval_minutes: int
    sample_count: int
    meal_event_count: int
    meal_carbohydrate_total_g: float
    glucose_min_mg_dl: float
    glucose_max_mg_dl: float
    glucose_mean_mg_dl: float
    glucose_start_mg_dl: float
    glucose_end_mg_dl: float
    trajectory: tuple[GlucosePoint, ...]

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> PyMgipsimResult:
        _reject_private_or_clinical_fields(payload)
        try:
            summary = payload["glucose_summary_mg_dl"]
            points = tuple(
                GlucosePoint(
                    minute=int(point["minute"]), glucose_mg_dl=float(point["glucose_mg_dl"])
                )
                for point in payload["trajectory"]
            )
            result = cls(
                schema_version=str(payload["schema_version"]),
                source=str(payload["source"]),
                upstream_commit=str(payload["upstream_commit"]),
                scenario_name=str(payload["scenario_name"]),
                model=str(payload["model"]),
                controller=str(payload["controller"]),
                random_seed=int(payload["random_seed"]),
                duration_minutes=int(payload["duration_minutes"]),
                sample_interval_minutes=int(payload["sample_interval_minutes"]),
                sample_count=int(payload["sample_count"]),
                meal_event_count=int(payload["meal_event_count"]),
                meal_carbohydrate_total_g=float(payload["meal_carbohydrate_total_g"]),
                glucose_min_mg_dl=float(summary["min"]),
                glucose_max_mg_dl=float(summary["max"]),
                glucose_mean_mg_dl=float(summary["mean"]),
                glucose_start_mg_dl=float(summary["start"]),
                glucose_end_mg_dl=float(summary["end"]),
                trajectory=points,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise PyMgipsimError("py-mgipsim returned an invalid result contract") from exc
        result.validate()
        return result

    @classmethod
    def from_json(cls, path: Path) -> PyMgipsimResult:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PyMgipsimError("Unable to read the py-mgipsim result") from exc
        if not isinstance(payload, dict):
            raise PyMgipsimError("py-mgipsim result must be a JSON object")
        return cls.from_payload(payload)

    def validate(self) -> None:
        if self.schema_version != RESULT_SCHEMA_VERSION:
            raise PyMgipsimError("Unsupported py-mgipsim result schema")
        if self.source != "py-mgipsim" or self.upstream_commit != PYMGIPSIM_COMMIT:
            raise PyMgipsimError("Unexpected py-mgipsim source provenance")
        if self.scenario_name != "m1_fixed_meal_day":
            raise PyMgipsimError("Unexpected simulation scenario")
        if self.model != "T1DM.ExtHovorka" or self.controller != "OpenLoop":
            raise PyMgipsimError("Unexpected simulation model or controller")
        if self.random_seed != 20260929:
            raise PyMgipsimError("Unexpected simulation random seed")
        if self.duration_minutes != 1440 or self.sample_interval_minutes != 5:
            raise PyMgipsimError("Unexpected simulation time grid")
        if self.sample_count != len(self.trajectory) or self.sample_count != 288:
            raise PyMgipsimError("Unexpected simulation sample count")
        if self.meal_event_count != 3 or not math.isclose(
            self.meal_carbohydrate_total_g, 210.0, abs_tol=1e-6
        ):
            raise PyMgipsimError("Unexpected fixed-meal protocol")

        expected_minutes = tuple(range(0, self.duration_minutes, self.sample_interval_minutes))
        actual_minutes = tuple(point.minute for point in self.trajectory)
        if actual_minutes != expected_minutes:
            raise PyMgipsimError("Simulation trajectory is not on the required five-minute grid")

        values = tuple(point.glucose_mg_dl for point in self.trajectory)
        if not all(math.isfinite(value) and 18.0 <= value <= 600.0 for value in values):
            raise PyMgipsimError("Simulation glucose contains invalid or implausible values")
        expected_summary = {
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
            "start": values[0],
            "end": values[-1],
        }
        reported_summary = {
            "min": self.glucose_min_mg_dl,
            "max": self.glucose_max_mg_dl,
            "mean": self.glucose_mean_mg_dl,
            "start": self.glucose_start_mg_dl,
            "end": self.glucose_end_mg_dl,
        }
        for name, expected in expected_summary.items():
            if not math.isclose(reported_summary[name], expected, rel_tol=1e-9, abs_tol=1e-6):
                raise PyMgipsimError("Simulation glucose summary is inconsistent")


def run_pymgipsim_scenario(
    *,
    source_directory: Path,
    python_executable: Path,
    output_json: Path,
    scenario: PyMgipsimScenario | None = None,
    timeout_seconds: int = 180,
) -> PyMgipsimResult:
    """Run the fixed scenario in the isolated upstream environment."""

    scenario = scenario or PyMgipsimScenario()
    source_directory = source_directory.resolve()
    python_executable = python_executable.resolve()
    output_json = output_json.resolve()

    if not (source_directory / "pymgipsim").is_dir():
        raise PyMgipsimError("py-mgipsim source directory is missing")
    if not python_executable.is_file():
        raise PyMgipsimError("py-mgipsim Python executable is missing")
    _verify_upstream_commit(source_directory)

    output_json.parent.mkdir(parents=True, exist_ok=True)
    bridge_path = Path(__file__).with_name("_pymgipsim_bridge.py").resolve()
    command = [
        str(python_executable),
        str(bridge_path),
        "--output-json",
        str(output_json),
        "--upstream-commit",
        PYMGIPSIM_COMMIT,
        "--random-seed",
        str(scenario.random_seed),
    ]
    environment = os.environ.copy()
    existing_python_path = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = str(source_directory)
    if existing_python_path:
        environment["PYTHONPATH"] += os.pathsep + existing_python_path
    try:
        completed = subprocess.run(
            command,
            cwd=source_directory,
            capture_output=True,
            check=False,
            env=environment,
            text=True,
            timeout=timeout_seconds,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PyMgipsimError("py-mgipsim execution failed") from exc
    if completed.returncode != 0:
        raise PyMgipsimError("py-mgipsim subprocess returned a nonzero status")

    return PyMgipsimResult.from_json(output_json)


def _verify_upstream_commit(source_directory: Path) -> None:
    try:
        completed = subprocess.run(
            ["git", "-c", f"safe.directory={source_directory.as_posix()}", "rev-parse", "HEAD"],
            cwd=source_directory,
            capture_output=True,
            check=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise PyMgipsimError("Unable to verify py-mgipsim source provenance") from exc
    if completed.stdout.strip() != PYMGIPSIM_COMMIT:
        raise PyMgipsimError("py-mgipsim checkout does not match the reviewed commit")


def _reject_private_or_clinical_fields(value: Any) -> None:
    forbidden = {
        "absolute_timestamp",
        "dose",
        "email",
        "insulin_units",
        "participant_id",
        "patient_id",
        "user_id",
    }
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).lower() in forbidden:
                raise PyMgipsimError("Simulation result contains a forbidden field")
            _reject_private_or_clinical_fields(nested)
    elif isinstance(value, list):
        for nested in value:
            _reject_private_or_clinical_fields(nested)
