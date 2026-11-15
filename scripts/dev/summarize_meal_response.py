"""Score saved synthetic results using the original protocol's 0.001 tolerance.

No model execution, refit, new cohort access or post-hoc threshold selection.
The driver also used a stricter pre-run 1e-6 repeat check; both are reported.
"""

import argparse
import json
from pathlib import Path

PRIMARY_TOLERANCE = 0.001


def summarize(report):
    result = {}
    for model in ("chronos", "lightgbm"):
        rows = [row for row in report["rows"] if row["model"] == model]
        eligible = [
            row
            for row in rows
            if row.get("portion") != 1
            and not (
                model == "lightgbm"
                and row.get("single_nutrient") in {"protein_g", "fat_g", "fiber_g"}
            )
        ]
        if not eligible:
            result[model] = dict(status="NOT_EVALUATED", eligible_contrasts=0)
            continue
        flat = sum(row["max_endpoint_delta_mg_dl"] <= PRIMARY_TOLERANCE for row in eligible)
        result[model] = dict(
            status="FAIL_INVARIANT" if flat == len(eligible) else "LIMITED_SYNTHETIC_SENSITIVITY",
            complete_rows=len(rows),
            eligible_contrasts=len(eligible),
            indistinguishable_contrasts=flat,
            indistinguishable_fraction=flat / len(eligible),
            max_endpoint_change_mg_dl=max(row["max_endpoint_delta_mg_dl"] for row in rows),
            repeat_max_error_mg_dl=report["models"][model]["identical_repeat_max_error_mg_dl"],
            current_meal_features="carbohydrates only"
            if model == "lightgbm"
            else "recorded carbohydrate/protein/fat/fiber channels",
            accuracy_status="NOT_VALIDATED",
        )
    return dict(
        engineering_checks=report.get("engineering_checks", report["status"]),
        primary_protocol_tolerance_mg_dl=PRIMARY_TOLERANCE,
        driver_repeat_tolerance_mg_dl=0.000001,
        models=result,
        accuracy_status="NOT_VALIDATED",
        all_phase_gates_passed=False,
        notice="Successful input wiring, finite intervals and repeatability do not establish meal-response capability or accuracy.",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = summarize(json.loads(args.input.read_text(encoding="utf-8-sig")))
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
