import csv
import zipfile
from datetime import datetime

import pytest

from research.datasets.azt1d import load_records
from research.pipelines.acquire_azt1d import extract_csvs


def test_external_loader_deduplicates_and_removes_conflicting_glucose(tmp_path):
    path = tmp_path / "synthetic.csv"
    fields = ["EventDateTime", "CGM", "CarbSize", "TotalBolusInsulinDelivered"]
    rows = [
        ["2020-01-01 12:00:00", "100", "20", "2"],
        ["2020-01-01 12:00:00", "100", "20", "2"],
        ["2020-01-01 12:05:00", "110", "", ""],
        ["2020-01-01 12:05:00", "130", "", ""],
        ["2020-01-01 12:10:00", "0", "", ""],
    ]
    with path.open("w", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(fields)
        writer.writerows(rows)
    participant, audit = load_records(path)
    assert len(participant.glucose) == 1
    assert participant.glucose[0].glucose_mg_dl == pytest.approx(100)
    assert participant.glucose[0].timestamp == datetime(2020, 1, 1, 12)
    assert len(participant.meals) == len(participant.insulin) == 1
    assert participant.meals[0].carbs_g == 20
    assert audit["duplicate_rows"] == 1
    assert audit["conflicting_glucose_timestamps"] == 1
    assert audit["nonpositive_glucose"] == 1


def test_archive_cannot_extract_outside_destination(tmp_path):
    archive = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive, "w") as output:
        output.writestr("../escape.csv", "private")
    with pytest.raises(ValueError, match="escapes"):
        extract_csvs(archive, tmp_path / "safe")
    assert not (tmp_path / "escape.csv").exists()
