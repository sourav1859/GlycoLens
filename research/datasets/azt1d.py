"""AZT1D V1 canonical CGM records; no Visual Statistics or serial-number exports.

Carbohydrates (g) and total bolus (U) are recorded events, not recommendations.
Protein/fat/fibre are unavailable: placeholder fields MUST NOT enter models.
Only shared-feature requests are permitted by the study runner. Times are source
local without offsets. Exact duplicate rows collapse; conflicting CGM values at
one timestamp are all removed. Nonpositive/nonfinite readings are missing.
"""

from __future__ import annotations

import csv
import hashlib
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from research.datasets.t1d_uom import (
    MMOL_L_TO_MG_DL,
    GlucosePoint,
    InsulinEvent,
    MealEvent,
    ParticipantData,
)

DOI = "10.17632/gk9m674wcx.1"


def canonical_files(root: Path):
    files = sorted(p for p in root.rglob("*.csv") if "CGM Records" in p.parts)
    if len(files) != 25:
        raise ValueError("AZT1D V1 must contain exactly 25 canonical CGM files")
    return files


def load_records(path: Path):
    counts = Counter()
    glucose = defaultdict(set)
    meals, bolus = defaultdict(float), defaultdict(float)
    seen = set()
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        glucose_field = "CGM" if "CGM" in (reader.fieldnames or []) else "Readings (CGM / BGM)"
        required = {"EventDateTime", glucose_field, "CarbSize", "TotalBolusInsulinDelivered"}
        if not required <= set(reader.fieldnames or []):
            raise ValueError("unsupported canonical AZT1D schema")
        for row in reader:
            counts["rows"] += 1
            signature = tuple(row.items())
            if signature in seen:
                counts["duplicate_rows"] += 1
                continue
            seen.add(signature)
            at = datetime.strptime(row["EventDateTime"], "%Y-%m-%d %H:%M:%S")
            value = float(row[glucose_field])
            if math.isfinite(value) and value > 0:
                glucose[at].add(value)
            else:
                counts["nonpositive_glucose"] += 1
            for field, destination in [("CarbSize", meals), ("TotalBolusInsulinDelivered", bolus)]:
                if not row[field].strip():
                    counts[field + "_missing"] += 1
                    continue
                value = float(row[field])
                if not math.isfinite(value) or value < 0:
                    counts[field + "_invalid"] += 1
                    continue
                if value > 0:
                    destination[at] += value
    counts["conflicting_glucose_timestamps"] = sum(len(values) > 1 for values in glucose.values())
    # Source namespace prevents accidental cross-cohort subject merging.
    subject = "azt1d:" + hashlib.sha256((DOI + "|" + path.parent.name).encode()).hexdigest()[:16]
    participant = ParticipantData(
        subject,
        tuple(
            GlucosePoint(at, next(iter(values)) / MMOL_L_TO_MG_DL)
            for at, values in sorted(glucose.items())
            if len(values) == 1
        ),
        tuple(
            MealEvent(at, "recorded_carbohydrate", "", carbs, 0, 0, 0)
            for at, carbs in sorted(meals.items())
        ),
        tuple(InsulinEvent(at, "bolus", units) for at, units in sorted(bolus.items())),
    )
    counts["glucose_points"] = len(participant.glucose)
    counts["carbohydrate_events"] = len(participant.meals)
    counts["bolus_events"] = len(participant.insulin)
    return participant, dict(counts)
