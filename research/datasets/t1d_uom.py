"""T1D-UOM V1.0.4 audit, loading, and meal-window construction.

The adapter deliberately avoids writing row-level health data. Callers receive
in-memory records and may emit aggregate summaries only. All input timestamps
are naive because the source release does not provide timezone offsets.
"""

from __future__ import annotations

import bisect
import csv
import math
import re
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterator, Sequence


T1D_UOM_VERSION = "V1.0.4"
T1D_UOM_DOI = "10.5281/zenodo.17361905"
T1D_UOM_RELEASE_COMMIT = "ea52718b41cd27286df46acf87825555d4ec0463"
MMOL_L_TO_MG_DL = 18.0182

_TIMESTAMP_FORMATS = (
    # The V1.0.4 files are produced by a UK study and use day-first dates,
    # despite the upstream README describing the fields as MM/DD/YYYY.
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%d/%m/%Y",
    "%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y %H:%M",
    "%m/%d/%Y",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
)


class DatasetValidationError(ValueError):
    """Raised when the dataset layout or a required schema is invalid."""


class WindowRejected(ValueError):
    """Raised when a meal cannot safely form a model-ready window."""

    def __init__(self, reason: str, detail: str = "") -> None:
        self.reason = reason
        message = reason if not detail else f"{reason}: {detail}"
        super().__init__(message)


@dataclass(frozen=True)
class ModalitySpec:
    name: str
    relative_directory: str
    filename_pattern: re.Pattern[str]
    timestamp_field: str
    numeric_fields: tuple[str, ...]
    required_fields: tuple[str, ...]


MODALITY_SPECS = (
    ModalitySpec(
        name="glucose",
        relative_directory="Glucose Data",
        filename_pattern=re.compile(r"^UoMGlucose(?P<id>\d+)\.csv$", re.IGNORECASE),
        timestamp_field="bg_ts",
        numeric_fields=("value",),
        required_fields=("bg_ts", "value"),
    ),
    ModalitySpec(
        name="nutrition",
        relative_directory="Nutrition Data",
        filename_pattern=re.compile(r"^UoMNutrition(?P<id>\d+)\.csv$", re.IGNORECASE),
        timestamp_field="meal_ts",
        numeric_fields=("carbs_g", "prot_g", "fat_g", "fibre_g"),
        required_fields=("meal_ts", "meal_type", "carbs_g", "prot_g", "fat_g", "fibre_g"),
    ),
    ModalitySpec(
        name="bolus",
        relative_directory=str(Path("Insulin Data") / "Bolus Data"),
        filename_pattern=re.compile(r"^UoMBolus(?P<id>\d+)\.csv$", re.IGNORECASE),
        timestamp_field="bolus_ts",
        numeric_fields=("bolus_dose",),
        required_fields=("bolus_ts", "bolus_dose"),
    ),
    ModalitySpec(
        name="basal",
        relative_directory=str(Path("Insulin Data") / "Basal Data"),
        filename_pattern=re.compile(r"^UoMBasal(?P<id>\d+)\.csv$", re.IGNORECASE),
        timestamp_field="basal_ts",
        numeric_fields=("basal_dose",),
        required_fields=("basal_ts", "basal_dose", "insulin_kind"),
    ),
)


@dataclass(frozen=True)
class FileAudit:
    modality: str
    participant_id: str
    row_count: int
    blank_required_count: int
    invalid_timestamp_count: int
    insufficient_timestamp_precision_count: int
    invalid_numeric_count: int
    duplicate_timestamp_count: int
    conflicting_glucose_timestamp_count: int


@dataclass(frozen=True)
class DatasetAudit:
    dataset_version: str
    doi: str
    release_commit: str
    release_directory_matches: bool
    total_csv_files: int
    total_rows: int
    file_counts: dict[str, int]
    row_counts: dict[str, int]
    participants_by_modality: dict[str, tuple[str, ...]]
    core_participants: tuple[str, ...]
    full_multimodal_participants: tuple[str, ...]
    blank_required_count: int
    invalid_timestamp_count: int
    insufficient_timestamp_precision_count: int
    invalid_numeric_count: int
    duplicate_timestamp_count: int
    conflicting_glucose_timestamp_count: int
    files: tuple[FileAudit, ...]

    def to_dict(
        self,
        *,
        include_files: bool = False,
        include_participant_ids: bool = False,
    ) -> dict[str, object]:
        payload = asdict(self)
        if not include_files:
            payload.pop("files", None)
        if not include_participant_ids:
            payload["participant_counts_by_modality"] = {
                modality: len(participants)
                for modality, participants in self.participants_by_modality.items()
            }
            payload["core_participant_count"] = len(self.core_participants)
            payload["full_multimodal_participant_count"] = len(self.full_multimodal_participants)
            payload.pop("participants_by_modality", None)
            payload.pop("core_participants", None)
            payload.pop("full_multimodal_participants", None)
            if include_files:
                payload["files"] = tuple(
                    {
                        key: value
                        for key, value in file_summary.items()
                        if key != "participant_id"
                    }
                    for file_summary in payload["files"]
                )
        return payload


@dataclass(frozen=True)
class ParticipantFiles:
    glucose: Path | None = None
    nutrition: Path | None = None
    bolus: Path | None = None
    basal: Path | None = None


@dataclass(frozen=True)
class GlucosePoint:
    timestamp: datetime
    glucose_mmol_l: float

    @property
    def glucose_mg_dl(self) -> float:
        return self.glucose_mmol_l * MMOL_L_TO_MG_DL


@dataclass(frozen=True)
class MealEvent:
    timestamp: datetime
    meal_type: str
    meal_tag: str
    carbs_g: float
    protein_g: float
    fat_g: float
    fiber_g: float


@dataclass(frozen=True)
class InsulinEvent:
    timestamp: datetime
    event_type: str
    dose: float
    insulin_kind: str | None = None


@dataclass(frozen=True)
class ParticipantData:
    participant_id: str
    glucose: tuple[GlucosePoint, ...]
    meals: tuple[MealEvent, ...]
    insulin: tuple[InsulinEvent, ...]


@dataclass(frozen=True)
class WindowConfig:
    history_minutes: int = 120
    horizon_minutes: int = 120
    frequency_minutes: int = 5
    insulin_history_minutes: int = 360
    max_interpolation_gap_minutes: int = 15
    max_edge_gap_minutes: int = 5
    exclude_follow_up_meals: bool = True
    require_insulin_context: bool = True

    def __post_init__(self) -> None:
        positive_fields = (
            self.history_minutes,
            self.horizon_minutes,
            self.frequency_minutes,
            self.insulin_history_minutes,
            self.max_interpolation_gap_minutes,
            self.max_edge_gap_minutes,
        )
        if any(value <= 0 for value in positive_fields):
            raise ValueError("window configuration values must be positive")
        if self.history_minutes % self.frequency_minutes:
            raise ValueError("history_minutes must be divisible by frequency_minutes")
        if self.horizon_minutes % self.frequency_minutes:
            raise ValueError("horizon_minutes must be divisible by frequency_minutes")


@dataclass(frozen=True)
class MealWindow:
    participant_id: str
    meal: MealEvent
    cgm_history: tuple[GlucosePoint, ...]
    insulin_history: tuple[InsulinEvent, ...]
    target_cgm: tuple[GlucosePoint, ...]
    config: WindowConfig

    def shape_summary(self) -> dict[str, object]:
        return {
            "history_points": len(self.cgm_history),
            "target_points": len(self.target_cgm),
            "insulin_events": len(self.insulin_history),
            "nutrition_fields": ("carbs_g", "protein_g", "fat_g", "fiber_g"),
            "history_minutes": self.config.history_minutes,
            "horizon_minutes": self.config.horizon_minutes,
            "frequency_minutes": self.config.frequency_minutes,
        }


@dataclass(frozen=True)
class WindowSearchSummary:
    participants_considered: int
    meals_considered: int
    eligible_windows: int
    rejection_counts: dict[str, int]


def parse_timestamp(value: str) -> datetime:
    normalized = value.strip()
    for timestamp_format in _TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(normalized, timestamp_format)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as error:
        raise DatasetValidationError(f"unsupported timestamp: {value!r}") from error


def _require_dataset_root(dataset_root: Path | str) -> Path:
    root = Path(dataset_root).expanduser().resolve()
    if not root.is_dir():
        raise DatasetValidationError(f"dataset root does not exist: {root}")
    missing = [spec.relative_directory for spec in MODALITY_SPECS if not (root / spec.relative_directory).is_dir()]
    if missing:
        raise DatasetValidationError(f"dataset root is missing required directories: {', '.join(missing)}")
    return root


def discover_participant_files(dataset_root: Path | str) -> dict[str, ParticipantFiles]:
    root = _require_dataset_root(dataset_root)
    discovered: dict[str, dict[str, Path]] = {}
    for spec in MODALITY_SPECS:
        for path in sorted((root / spec.relative_directory).glob("*.csv")):
            match = spec.filename_pattern.match(path.name)
            if not match:
                continue
            participant_id = f"UoM{match.group('id')}"
            discovered.setdefault(participant_id, {})[spec.name] = path
    return {
        participant_id: ParticipantFiles(**paths)
        for participant_id, paths in sorted(discovered.items())
    }


def _validate_headers(path: Path, required_fields: Sequence[str]) -> tuple[str, ...]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        try:
            headers = tuple(header.strip() for header in next(reader))
        except StopIteration as error:
            raise DatasetValidationError(f"empty CSV file: {path.name}") from error
    missing = sorted(set(required_fields) - set(headers))
    if missing:
        raise DatasetValidationError(f"{path.name} missing required columns: {', '.join(missing)}")
    return headers


def _audit_file(path: Path, spec: ModalitySpec, participant_id: str) -> FileAudit:
    _validate_headers(path, spec.required_fields)
    row_count = 0
    blank_required_count = 0
    invalid_timestamp_count = 0
    insufficient_timestamp_precision_count = 0
    invalid_numeric_count = 0
    duplicate_timestamp_count = 0
    timestamps: set[datetime] = set()
    glucose_values_by_timestamp: dict[datetime, set[float]] = {}

    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            row_count += 1
            if any(not (row.get(field) or "").strip() for field in spec.required_fields):
                blank_required_count += 1
            timestamp: datetime | None = None
            raw_timestamp = row.get(spec.timestamp_field, "")
            try:
                timestamp = parse_timestamp(raw_timestamp)
            except DatasetValidationError:
                invalid_timestamp_count += 1
            if timestamp is not None and ":" not in raw_timestamp:
                insufficient_timestamp_precision_count += 1
            if timestamp is not None:
                if timestamp in timestamps:
                    duplicate_timestamp_count += 1
                timestamps.add(timestamp)
            for field in spec.numeric_fields:
                raw = (row.get(field) or "").strip()
                if not raw:
                    continue
                try:
                    value = float(raw)
                    if not math.isfinite(value):
                        raise ValueError
                except ValueError:
                    invalid_numeric_count += 1
            if timestamp is not None and spec.name == "glucose":
                try:
                    glucose_value = float((row.get("value") or "").strip())
                    if math.isfinite(glucose_value):
                        glucose_values_by_timestamp.setdefault(timestamp, set()).add(glucose_value)
                except ValueError:
                    pass

    return FileAudit(
        modality=spec.name,
        participant_id=participant_id,
        row_count=row_count,
        blank_required_count=blank_required_count,
        invalid_timestamp_count=invalid_timestamp_count,
        insufficient_timestamp_precision_count=insufficient_timestamp_precision_count,
        invalid_numeric_count=invalid_numeric_count,
        duplicate_timestamp_count=duplicate_timestamp_count,
        conflicting_glucose_timestamp_count=sum(
            1 for values in glucose_values_by_timestamp.values() if len(values) > 1
        ),
    )


def audit_dataset(dataset_root: Path | str) -> DatasetAudit:
    root = _require_dataset_root(dataset_root)
    participant_files = discover_participant_files(root)
    file_audits: list[FileAudit] = []
    participants_by_modality: dict[str, set[str]] = {spec.name: set() for spec in MODALITY_SPECS}

    for participant_id, files in participant_files.items():
        for spec in MODALITY_SPECS:
            path = getattr(files, spec.name)
            if path is None:
                continue
            participants_by_modality[spec.name].add(participant_id)
            file_audits.append(_audit_file(path, spec, participant_id))

    glucose = participants_by_modality["glucose"]
    nutrition = participants_by_modality["nutrition"]
    any_insulin = participants_by_modality["bolus"] | participants_by_modality["basal"]
    core = glucose & nutrition & any_insulin
    full = glucose & nutrition & participants_by_modality["bolus"] & participants_by_modality["basal"]
    file_counts = Counter(audit.modality for audit in file_audits)
    row_counts = Counter()
    for item in file_audits:
        row_counts[item.modality] += item.row_count

    return DatasetAudit(
        dataset_version=T1D_UOM_VERSION,
        doi=T1D_UOM_DOI,
        release_commit=T1D_UOM_RELEASE_COMMIT,
        release_directory_matches=T1D_UOM_RELEASE_COMMIT[:7].lower() in root.name.lower(),
        total_csv_files=len(file_audits),
        total_rows=sum(item.row_count for item in file_audits),
        file_counts=dict(sorted(file_counts.items())),
        row_counts=dict(sorted(row_counts.items())),
        participants_by_modality={
            modality: tuple(sorted(participants))
            for modality, participants in sorted(participants_by_modality.items())
        },
        core_participants=tuple(sorted(core)),
        full_multimodal_participants=tuple(sorted(full)),
        blank_required_count=sum(item.blank_required_count for item in file_audits),
        invalid_timestamp_count=sum(item.invalid_timestamp_count for item in file_audits),
        insufficient_timestamp_precision_count=sum(
            item.insufficient_timestamp_precision_count for item in file_audits
        ),
        invalid_numeric_count=sum(item.invalid_numeric_count for item in file_audits),
        duplicate_timestamp_count=sum(item.duplicate_timestamp_count for item in file_audits),
        conflicting_glucose_timestamp_count=sum(
            item.conflicting_glucose_timestamp_count for item in file_audits
        ),
        files=tuple(sorted(file_audits, key=lambda item: (item.modality, item.participant_id))),
    )


def _read_dict_rows(path: Path, required_fields: Sequence[str]) -> Iterator[dict[str, str]]:
    _validate_headers(path, required_fields)
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            yield {str(key): (value or "").strip() for key, value in row.items() if key is not None}


def _finite_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError("numeric value must be finite")
    return parsed


def _load_glucose(path: Path) -> tuple[GlucosePoint, ...]:
    values_by_timestamp: dict[datetime, set[float]] = {}
    for row in _read_dict_rows(path, ("bg_ts", "value")):
        try:
            timestamp = parse_timestamp(row["bg_ts"])
            value = _finite_float(row["value"])
        except (DatasetValidationError, KeyError, ValueError):
            continue
        if value <= 0:
            continue
        values_by_timestamp.setdefault(timestamp, set()).add(value)
    # Exact repeated rows collapse to one value. Conflicting readings at the
    # same timestamp are excluded rather than averaged or selected arbitrarily.
    readings = [
        GlucosePoint(timestamp=timestamp, glucose_mmol_l=next(iter(values)))
        for timestamp, values in values_by_timestamp.items()
        if len(values) == 1
    ]
    return tuple(sorted(readings, key=lambda item: item.timestamp))


def _load_meals(path: Path) -> tuple[MealEvent, ...]:
    required = ("meal_ts", "meal_type", "carbs_g", "prot_g", "fat_g", "fibre_g")
    meals_by_timestamp: dict[datetime, list[MealEvent]] = {}
    for row in _read_dict_rows(path, required):
        if ":" not in row.get("meal_ts", ""):
            continue
        try:
            meal = MealEvent(
                timestamp=parse_timestamp(row["meal_ts"]),
                meal_type=row["meal_type"],
                meal_tag=row.get("meal_tag", ""),
                carbs_g=_finite_float(row["carbs_g"]),
                protein_g=_finite_float(row["prot_g"]),
                fat_g=_finite_float(row["fat_g"]),
                fiber_g=_finite_float(row["fibre_g"]),
            )
        except (DatasetValidationError, KeyError, ValueError):
            continue
        if min(meal.carbs_g, meal.protein_g, meal.fat_g, meal.fiber_g) < 0:
            continue
        meals_by_timestamp.setdefault(meal.timestamp, []).append(meal)

    meals: list[MealEvent] = []
    for timestamp, components in meals_by_timestamp.items():
        meal_types = tuple(dict.fromkeys(item.meal_type for item in components if item.meal_type))
        meal_tags = tuple(dict.fromkeys(item.meal_tag for item in components if item.meal_tag))
        meals.append(
            MealEvent(
                timestamp=timestamp,
                meal_type=" + ".join(meal_types),
                meal_tag="; ".join(meal_tags),
                carbs_g=sum(item.carbs_g for item in components),
                protein_g=sum(item.protein_g for item in components),
                fat_g=sum(item.fat_g for item in components),
                fiber_g=sum(item.fiber_g for item in components),
            )
        )
    return tuple(sorted(meals, key=lambda item: item.timestamp))


def _load_insulin(path: Path, *, event_type: str) -> tuple[InsulinEvent, ...]:
    if event_type == "bolus":
        timestamp_field, dose_field = "bolus_ts", "bolus_dose"
        required = (timestamp_field, dose_field)
    elif event_type == "basal":
        timestamp_field, dose_field = "basal_ts", "basal_dose"
        required = (timestamp_field, dose_field, "insulin_kind")
    else:
        raise ValueError(f"unsupported insulin event type: {event_type}")

    events: list[InsulinEvent] = []
    for row in _read_dict_rows(path, required):
        try:
            timestamp = parse_timestamp(row[timestamp_field])
            dose = _finite_float(row[dose_field])
        except (DatasetValidationError, KeyError, ValueError):
            continue
        if dose < 0:
            continue
        events.append(
            InsulinEvent(
                timestamp=timestamp,
                event_type=event_type,
                dose=dose,
                insulin_kind=row.get("insulin_kind") or None,
            )
        )
    return tuple(sorted(events, key=lambda item: item.timestamp))


def load_participant(dataset_root: Path | str, participant_id: str) -> ParticipantData:
    participant_files = discover_participant_files(dataset_root)
    try:
        files = participant_files[participant_id]
    except KeyError as error:
        raise DatasetValidationError(f"participant not found: {participant_id}") from error
    if files.glucose is None or files.nutrition is None:
        raise DatasetValidationError(f"participant {participant_id} lacks glucose or nutrition data")
    if files.bolus is None and files.basal is None:
        raise DatasetValidationError(f"participant {participant_id} lacks insulin data")

    insulin: list[InsulinEvent] = []
    if files.bolus is not None:
        insulin.extend(_load_insulin(files.bolus, event_type="bolus"))
    if files.basal is not None:
        insulin.extend(_load_insulin(files.basal, event_type="basal"))
    return ParticipantData(
        participant_id=participant_id,
        glucose=_load_glucose(files.glucose),
        meals=_load_meals(files.nutrition),
        insulin=tuple(sorted(insulin, key=lambda item: item.timestamp)),
    )


def _resample_glucose(
    readings: Sequence[GlucosePoint],
    desired_timestamps: Sequence[datetime],
    *,
    max_interpolation_gap: timedelta,
    max_edge_gap: timedelta,
) -> tuple[GlucosePoint, ...] | None:
    if not readings:
        return None
    ordered = sorted(readings, key=lambda item: item.timestamp)
    timestamps = [point.timestamp for point in ordered]
    result: list[GlucosePoint] = []

    for desired in desired_timestamps:
        index = bisect.bisect_left(timestamps, desired)
        if index < len(ordered) and ordered[index].timestamp == desired:
            value = ordered[index].glucose_mmol_l
        elif index == 0:
            gap = ordered[0].timestamp - desired
            if gap < timedelta(0) or gap > max_edge_gap:
                return None
            value = ordered[0].glucose_mmol_l
        elif index == len(ordered):
            gap = desired - ordered[-1].timestamp
            if gap < timedelta(0) or gap > max_edge_gap:
                return None
            value = ordered[-1].glucose_mmol_l
        else:
            left = ordered[index - 1]
            right = ordered[index]
            span = right.timestamp - left.timestamp
            if span <= timedelta(0) or span > max_interpolation_gap:
                return None
            fraction = (desired - left.timestamp).total_seconds() / span.total_seconds()
            value = left.glucose_mmol_l + fraction * (right.glucose_mmol_l - left.glucose_mmol_l)
        result.append(GlucosePoint(timestamp=desired, glucose_mmol_l=value))
    return tuple(result)


def build_meal_window(
    participant: ParticipantData,
    meal: MealEvent,
    config: WindowConfig | None = None,
) -> MealWindow:
    effective = config or WindowConfig()
    frequency = timedelta(minutes=effective.frequency_minutes)
    history_count = effective.history_minutes // effective.frequency_minutes
    target_count = effective.horizon_minutes // effective.frequency_minutes
    horizon_end = meal.timestamp + timedelta(minutes=effective.horizon_minutes)

    if effective.exclude_follow_up_meals and any(
        meal.timestamp < other.timestamp <= horizon_end for other in participant.meals
    ):
        raise WindowRejected("follow_up_meal", "another meal occurs inside the forecast horizon")

    history_timestamps = tuple(
        meal.timestamp - frequency * offset for offset in range(history_count - 1, -1, -1)
    )
    target_timestamps = tuple(meal.timestamp + frequency * offset for offset in range(1, target_count + 1))
    premeal_readings = tuple(point for point in participant.glucose if point.timestamp <= meal.timestamp)
    target_readings = tuple(
        point
        for point in participant.glucose
        if meal.timestamp < point.timestamp <= horizon_end + timedelta(minutes=effective.max_edge_gap_minutes)
    )
    maximum_interpolation_gap = timedelta(minutes=effective.max_interpolation_gap_minutes)
    maximum_edge_gap = timedelta(minutes=effective.max_edge_gap_minutes)

    history = _resample_glucose(
        premeal_readings,
        history_timestamps,
        max_interpolation_gap=maximum_interpolation_gap,
        max_edge_gap=maximum_edge_gap,
    )
    if history is None:
        raise WindowRejected("incomplete_history", "CGM history cannot be safely resampled")
    target = _resample_glucose(
        target_readings,
        target_timestamps,
        max_interpolation_gap=maximum_interpolation_gap,
        max_edge_gap=maximum_edge_gap,
    )
    if target is None:
        raise WindowRejected("incomplete_target", "future CGM cannot be safely resampled")

    insulin_start = meal.timestamp - timedelta(minutes=effective.insulin_history_minutes)
    insulin_history = tuple(
        event for event in participant.insulin if insulin_start <= event.timestamp <= meal.timestamp
    )
    if effective.require_insulin_context and not insulin_history:
        raise WindowRejected(
            "missing_insulin_context",
            "no basal or bolus event is available inside the configured pre-meal window",
        )
    return MealWindow(
        participant_id=participant.participant_id,
        meal=meal,
        cgm_history=history,
        insulin_history=insulin_history,
        target_cgm=target,
        config=effective,
    )


def find_eligible_windows(
    dataset_root: Path | str,
    config: WindowConfig | None = None,
    *,
    limit: int | None = None,
) -> tuple[tuple[MealWindow, ...], WindowSearchSummary]:
    if limit is not None and limit <= 0:
        raise ValueError("limit must be positive when supplied")
    effective = config or WindowConfig()
    audit = audit_dataset(dataset_root)
    windows: list[MealWindow] = []
    rejection_counts: Counter[str] = Counter()
    meals_considered = 0
    participants_considered = 0

    for participant_id in audit.core_participants:
        participants_considered += 1
        participant = load_participant(dataset_root, participant_id)
        for meal in participant.meals:
            meals_considered += 1
            try:
                windows.append(build_meal_window(participant, meal, effective))
            except WindowRejected as error:
                rejection_counts[error.reason] += 1
                continue
            if limit is not None and len(windows) >= limit:
                return (
                    tuple(windows),
                    WindowSearchSummary(
                        participants_considered=participants_considered,
                        meals_considered=meals_considered,
                        eligible_windows=len(windows),
                        rejection_counts=dict(sorted(rejection_counts.items())),
                    ),
                )

    return (
        tuple(windows),
        WindowSearchSummary(
            participants_considered=participants_considered,
            meals_considered=meals_considered,
            eligible_windows=len(windows),
            rejection_counts=dict(sorted(rejection_counts.items())),
        ),
    )
