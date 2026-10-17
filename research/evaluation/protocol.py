"""Target-purged temporal splits and explicit subject holdouts.

Manifests contain research identifiers and timestamps: save only to ignored artifacts.
No outcome values influence event IDs or split assignment.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass

from research.datasets.t1d_uom import MealWindow, T1D_UOM_RELEASE_COMMIT


@dataclass(frozen=True)
class SplitPolicy:
    train_fraction: float = 0.6
    validation_fraction: float = 0.2
    version: str = "m2_temporal_v1"

    def __post_init__(self) -> None:
        if not (0 < self.train_fraction < 1 and 0 < self.validation_fraction < 1):
            raise ValueError("split fractions must be strictly between zero and one")
        if self.train_fraction + self.validation_fraction >= 1:
            raise ValueError("split fractions must leave a nonempty test time interval")


def configuration_hash(window: MealWindow, policy: SplitPolicy) -> str:
    payload = {
        "dataset_commit": T1D_UOM_RELEASE_COMMIT,
        "window_config": asdict(window.config),
        "split_policy": asdict(policy),
        "feature_version": "recorded_events_v1",
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def event_id(window: MealWindow) -> str:
    payload = (
        f"{T1D_UOM_RELEASE_COMMIT}|{window.participant_id}|{window.meal.timestamp.isoformat()}"
    )
    return hashlib.sha256(payload.encode()).hexdigest()


@dataclass(frozen=True)
class ManifestEntry:
    event_id: str
    participant_id: str
    meal_at: str
    context_start: str
    target_end: str
    split: str
    configuration_hash: str


def temporal_manifest(
    windows: tuple[MealWindow, ...], policy: SplitPolicy | None = None
) -> tuple[ManifestEntry, ...]:
    policy = policy or SplitPolicy()
    groups: dict[str, list[MealWindow]] = defaultdict(list)
    if len({event_id(window) for window in windows}) != len(windows):
        raise ValueError("duplicate meal events cannot enter the benchmark")
    for window in windows:
        groups[window.participant_id].append(window)
    entries: list[ManifestEntry] = []
    for subject in sorted(groups):
        ordered = sorted(groups[subject], key=lambda window: window.meal.timestamp)
        start = ordered[0].meal.timestamp
        end = ordered[-1].target_cgm[-1].timestamp
        duration = end - start
        train_end = start + duration * policy.train_fraction
        validation_end = start + duration * (policy.train_fraction + policy.validation_fraction)
        for window in ordered:
            origin, target_end = window.meal.timestamp, window.target_cgm[-1].timestamp
            if target_end <= train_end:
                split = "train"
            elif origin >= train_end and target_end <= validation_end:
                split = "validation"
            elif origin >= validation_end:
                split = "test"
            else:
                split = "purged_boundary"
            entries.append(
                ManifestEntry(
                    event_id(window),
                    subject,
                    origin.isoformat(),
                    window.cgm_history[0].timestamp.isoformat(),
                    target_end.isoformat(),
                    split,
                    configuration_hash(window, policy),
                )
            )
    return tuple(entries)


def subject_manifest(
    windows: tuple[MealWindow, ...],
    *,
    validation_subjects: frozenset[str],
    test_subjects: frozenset[str],
) -> tuple[ManifestEntry, ...]:
    subjects = {window.participant_id for window in windows}
    if not validation_subjects or not test_subjects:
        raise ValueError("validation and test subject holdouts must be explicit and nonempty")
    if validation_subjects & test_subjects or not (validation_subjects | test_subjects) <= subjects:
        raise ValueError("subject holdouts must be disjoint and present in the cohort")
    if not subjects - validation_subjects - test_subjects:
        raise ValueError("subject holdouts must leave development subjects")
    temporal = temporal_manifest(windows)
    return tuple(
        ManifestEntry(
            entry.event_id,
            entry.participant_id,
            entry.meal_at,
            entry.context_start,
            entry.target_end,
            "test"
            if entry.participant_id in test_subjects
            else "validation"
            if entry.participant_id in validation_subjects
            else "train",
            hashlib.sha256(
                json.dumps(
                    {
                        "base": entry.configuration_hash,
                        "validation": sorted(validation_subjects),
                        "test": sorted(test_subjects),
                        "version": "m2_subject_v1",
                    },
                    sort_keys=True,
                ).encode()
            ).hexdigest(),
        )
        for entry in temporal
    )


def manifest_summary(entries: tuple[ManifestEntry, ...]) -> dict[str, object]:
    counts = Counter(entry.split for entry in entries)
    subject_splits: dict[str, set[str]] = defaultdict(set)
    for entry in entries:
        subject_splits[entry.participant_id].add(entry.split)
    return {
        "event_count": len(entries),
        "participant_count": len(subject_splits),
        "split_counts": dict(sorted(counts.items())),
        "participants_with_validation_and_test": sum(
            {"validation", "test"} <= splits for splits in subject_splits.values()
        ),
        "contains_row_level_data": False,
    }
