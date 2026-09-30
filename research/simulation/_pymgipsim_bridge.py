"""Execute the reviewed scenario inside an isolated py-mgipsim checkout."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from pymgipsim.Interface.parser import generate_parser_cli
from pymgipsim.InputGeneration.activity_settings import activity_args_to_scenario
from pymgipsim.Utilities import simulation_folder
from pymgipsim.Utilities.Scenario import load_scenario
from pymgipsim.Utilities.paths import default_settings_path, results_path
from pymgipsim.Utilities.units_conversions_constants import UnitConversion
from pymgipsim.generate_inputs import generate_inputs_main
from pymgipsim.generate_results import generate_results_main
from pymgipsim.generate_settings import generate_simulation_settings_main
from pymgipsim.generate_subjects import generate_virtual_subjects_main


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--upstream-commit", required=True)
    parser.add_argument("--random-seed", type=int, required=True)
    return parser.parse_args()


def _scenario_args(random_seed: int) -> argparse.Namespace:
    args = generate_parser_cli().parse_args([])
    args.number_of_days = 1
    args.sampling_time = 5
    args.random_seed = random_seed
    args.model_name = "T1DM.ExtHovorka"
    args.controller_name = "OpenLoop"
    args.patient_names = ["Patient_1.json"]
    args.number_of_subjects = 1
    args.breakfast_carb_range = [60.0]
    args.lunch_carb_range = [70.0]
    args.dinner_carb_range = [80.0]
    args.am_snack_carb_range = [0.0]
    args.pm_snack_carb_range = [0.0]
    args.running_start_time = ["16:00"]
    args.running_duration = [30.0]
    args.running_incline = [0.0]
    args.running_speed = [0.0]
    args.cycling_start_time = ["16:00"]
    args.cycling_duration = [30.0]
    args.cycling_power = [0.0]
    args.no_progress_bar = True
    args.no_print = True
    args.to_excel = False
    return args


def _run(random_seed: int, upstream_commit: str) -> dict[str, object]:
    Path(results_path).mkdir(parents=True, exist_ok=True)
    _, _, _, work_directory = simulation_folder.create_simulation_results_folder(results_path)
    scenario = load_scenario(str(Path(default_settings_path) / "scenario_default.json"))
    args = _scenario_args(random_seed)

    scenario = generate_simulation_settings_main(scenario, args, work_directory)
    scenario = generate_virtual_subjects_main(scenario, args, work_directory)
    activity_args_to_scenario(scenario, args)
    scenario = generate_inputs_main(scenario, args, work_directory)
    cohort, _ = generate_results_main(scenario, vars(args), work_directory)

    model = cohort.singlescale_model
    glucose = UnitConversion.glucose.concentration_mmolL_to_mgdL(
        model.states.as_array[0, model.glucose_state, :] / model.parameters.VG[0]
    )
    minutes = model.time.as_unix.astype(int)
    meal_magnitudes = np.asarray(scenario.inputs.meal_carb.magnitude, dtype=float)[0]
    meal_count = int(np.count_nonzero(meal_magnitudes > 0))
    values = glucose.astype(float)

    return {
        "schema_version": "1.0",
        "source": "py-mgipsim",
        "upstream_commit": upstream_commit,
        "scenario_name": "m1_fixed_meal_day",
        "model": "T1DM.ExtHovorka",
        "controller": "OpenLoop",
        "random_seed": random_seed,
        "duration_minutes": 1440,
        "sample_interval_minutes": 5,
        "sample_count": int(values.size),
        "meal_event_count": meal_count,
        "meal_carbohydrate_total_g": float(meal_magnitudes.sum()),
        "glucose_summary_mg_dl": {
            "min": float(values.min()),
            "max": float(values.max()),
            "mean": float(values.mean()),
            "start": float(values[0]),
            "end": float(values[-1]),
        },
        "trajectory": [
            {"minute": int(minute), "glucose_mg_dl": float(value)}
            for minute, value in zip(minutes, values, strict=True)
        ],
    }


def main() -> None:
    args = _parse_args()
    payload = _run(args.random_seed, args.upstream_commit)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
