from __future__ import annotations

import csv
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from research.datasets.t1d_uom import (
    DatasetValidationError,
    WindowConfig,
    WindowRejected,
    audit_dataset,
    build_meal_window,
    load_participant,
    parse_timestamp,
)


MEAL_TIME = datetime(2026, 1, 15, 12, 0)


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _timestamp(value: datetime) -> str:
    return value.strftime("%m/%d/%Y %H:%M:%S")


def _build_fixture(root: Path, *, second_meal: bool = False, target_gap: bool = False) -> None:
    glucose_rows: list[dict[str, object]] = []
    current = MEAL_TIME - timedelta(minutes=115)
    end = MEAL_TIME + timedelta(minutes=120)
    while current <= end:
        if not (
            target_gap
            and MEAL_TIME + timedelta(minutes=40) <= current <= MEAL_TIME + timedelta(minutes=60)
        ):
            glucose_rows.append(
                {"bg_ts": _timestamp(current), "value": f"{6.0 + len(glucose_rows) * 0.01:.2f}"}
            )
        current += timedelta(minutes=5)

    meals = [
        {
            "meal_ts": MEAL_TIME.strftime("%m/%d/%Y %H:%M"),
            "meal_type": "Lunch",
            "meal_tag": "synthetic meal",
            "carbs_g": "45",
            "prot_g": "20",
            "fat_g": "12",
            "fibre_g": "6",
        }
    ]
    if second_meal:
        meals.append(
            {
                "meal_ts": (MEAL_TIME + timedelta(minutes=60)).strftime("%m/%d/%Y %H:%M"),
                "meal_type": "Snack",
                "meal_tag": "synthetic follow-up",
                "carbs_g": "10",
                "prot_g": "1",
                "fat_g": "1",
                "fibre_g": "1",
            }
        )

    _write_csv(root / "Glucose Data" / "UoMGlucose9999.csv", ["bg_ts", "value"], glucose_rows)
    _write_csv(
        root / "Nutrition Data" / "UoMNutrition9999.csv",
        ["meal_ts", "meal_type", "meal_tag", "carbs_g", "prot_g", "fat_g", "fibre_g"],
        meals,
    )
    _write_csv(
        root / "Insulin Data" / "Bolus Data" / "UoMBolus9999.csv",
        ["bolus_ts", "bolus_dose"],
        [
            {
                "bolus_ts": (MEAL_TIME - timedelta(minutes=10)).strftime("%m/%d/%Y %H:%M"),
                "bolus_dose": "3.5",
            },
            {
                "bolus_ts": (MEAL_TIME + timedelta(minutes=5)).strftime("%m/%d/%Y %H:%M"),
                "bolus_dose": "1.0",
            },
        ],
    )
    _write_csv(
        root / "Insulin Data" / "Basal Data" / "UoMBasal9999.csv",
        ["basal_ts", "basal_dose", "insulin_kind"],
        [
            {
                "basal_ts": (MEAL_TIME - timedelta(minutes=60)).strftime("%m/%d/%Y %H:%M"),
                "basal_dose": "0.8",
                "insulin_kind": "R",
            }
        ],
    )


class T1DUOMPipelineTests(unittest.TestCase):
    def test_ambiguous_source_date_is_parsed_day_first(self) -> None:
        self.assertEqual(parse_timestamp("05/10/2023 13:45"), datetime(2023, 10, 5, 13, 45))

    def test_audit_reports_core_participant_and_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            _build_fixture(root)

            audit = audit_dataset(root)

            self.assertEqual(audit.total_csv_files, 4)
            self.assertEqual(audit.total_rows, 52)
            self.assertEqual(audit.core_participants, ("UoM9999",))
            self.assertEqual(audit.full_multimodal_participants, ("UoM9999",))
            self.assertEqual(audit.invalid_timestamp_count, 0)
            self.assertEqual(audit.invalid_numeric_count, 0)
            public_summary = audit.to_dict()
            self.assertNotIn("core_participants", public_summary)
            self.assertEqual(public_summary["core_participant_count"], 1)
            public_file_summary = audit.to_dict(include_files=True)
            self.assertNotIn("participant_id", public_file_summary["files"][0])

    def test_window_has_strict_temporal_boundary_and_expected_shape(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            _build_fixture(root)
            participant = load_participant(root, "UoM9999")

            window = build_meal_window(participant, participant.meals[0], WindowConfig())

            self.assertEqual(len(window.cgm_history), 24)
            self.assertEqual(len(window.target_cgm), 24)
            self.assertTrue(
                all(point.timestamp <= window.meal.timestamp for point in window.cgm_history)
            )
            self.assertTrue(
                all(point.timestamp > window.meal.timestamp for point in window.target_cgm)
            )
            self.assertTrue(
                all(event.timestamp <= window.meal.timestamp for event in window.insulin_history)
            )
            self.assertAlmostEqual(window.cgm_history[0].glucose_mg_dl, 6.0 * 18.0182, places=4)

    def test_follow_up_meal_inside_horizon_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            _build_fixture(root, second_meal=True)
            participant = load_participant(root, "UoM9999")

            with self.assertRaisesRegex(WindowRejected, "follow_up_meal"):
                build_meal_window(participant, participant.meals[0], WindowConfig())

    def test_long_target_gap_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            _build_fixture(root, target_gap=True)
            participant = load_participant(root, "UoM9999")

            with self.assertRaisesRegex(WindowRejected, "incomplete_target"):
                build_meal_window(participant, participant.meals[0], WindowConfig())

    def test_future_insulin_does_not_satisfy_required_context(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            _build_fixture(root)
            _write_csv(
                root / "Insulin Data" / "Bolus Data" / "UoMBolus9999.csv",
                ["bolus_ts", "bolus_dose"],
                [
                    {
                        "bolus_ts": (MEAL_TIME + timedelta(minutes=5)).strftime("%m/%d/%Y %H:%M"),
                        "bolus_dose": "1.0",
                    }
                ],
            )
            (root / "Insulin Data" / "Basal Data" / "UoMBasal9999.csv").unlink()
            participant = load_participant(root, "UoM9999")

            with self.assertRaisesRegex(WindowRejected, "missing_insulin_context"):
                build_meal_window(participant, participant.meals[0], WindowConfig())

    def test_conflicting_duplicate_cgm_timestamp_is_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            _build_fixture(root)
            conflicting_timestamp = MEAL_TIME - timedelta(minutes=30)
            glucose_path = root / "Glucose Data" / "UoMGlucose9999.csv"
            with glucose_path.open("a", newline="", encoding="utf-8") as handle:
                csv.writer(handle).writerow([_timestamp(conflicting_timestamp), "15.0"])

            audit = audit_dataset(root)
            participant = load_participant(root, "UoM9999")

            self.assertEqual(audit.conflicting_glucose_timestamp_count, 1)
            self.assertNotIn(
                conflicting_timestamp, {point.timestamp for point in participant.glucose}
            )

    def test_same_timestamp_nutrition_components_are_aggregated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            _build_fixture(root)
            nutrition_path = root / "Nutrition Data" / "UoMNutrition9999.csv"
            with nutrition_path.open("a", newline="", encoding="utf-8") as handle:
                csv.writer(handle).writerow(
                    [
                        MEAL_TIME.strftime("%m/%d/%Y %H:%M"),
                        "Lunch",
                        "synthetic side",
                        "5",
                        "2",
                        "1",
                        "1",
                    ]
                )

            participant = load_participant(root, "UoM9999")

            self.assertEqual(len(participant.meals), 1)
            self.assertEqual(participant.meals[0].carbs_g, 50.0)
            self.assertEqual(participant.meals[0].protein_g, 22.0)

    def test_date_only_meal_is_audited_and_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            _build_fixture(root)
            nutrition_path = root / "Nutrition Data" / "UoMNutrition9999.csv"
            with nutrition_path.open("a", newline="", encoding="utf-8") as handle:
                csv.writer(handle).writerow(["15/01/2026", "Snack", "no time", "10", "1", "1", "1"])

            audit = audit_dataset(root)
            participant = load_participant(root, "UoM9999")

            self.assertEqual(audit.insufficient_timestamp_precision_count, 1)
            self.assertEqual(len(participant.meals), 1)

    def test_missing_required_column_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            _build_fixture(root)
            glucose_path = root / "Glucose Data" / "UoMGlucose9999.csv"
            _write_csv(
                glucose_path,
                ["wrong_timestamp", "value"],
                [{"wrong_timestamp": "x", "value": "6.0"}],
            )

            with self.assertRaisesRegex(DatasetValidationError, "missing required columns"):
                audit_dataset(root)


if __name__ == "__main__":
    unittest.main()
