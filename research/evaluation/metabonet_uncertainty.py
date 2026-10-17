"""Participant-representative symmetric bands; no point-model fitting or guarantees.

Marginal horizon bands and a separately calibrated maximum-error curve band are
different estimands. Study shift and participant exchangeability remain unverified.
"""

from __future__ import annotations

import hashlib
import math
from collections import defaultdict
from dataclasses import asdict, dataclass, replace

import numpy as np

from research.models.adapters.base import ForecastModelAdapter, QuantileForecast


def calibration_representatives(windows):
    groups, seen = defaultdict(list), set()
    for window in windows:
        if window["split"] != "calibration":
            raise ValueError("interval fitting requires calibration role only")
        if window["event_id"] in seen:
            raise ValueError("duplicate calibration event")
        if window["history_hours"] != 24 or window["carb_delay_minutes"] != 5:
            raise ValueError("calibration window differs from frozen configuration")
        seen.add(window["event_id"])
        groups[window["sid"]].append(window)
    return [
        min(
            groups[sid],
            key=lambda w: hashlib.sha256(f"phase6-calibration|{w['event_id']}".encode()).digest(),
        )
        for sid in sorted(groups)
    ]


@dataclass(frozen=True)
class SymmetricBands:
    radii: tuple[float, ...]
    curve_radius: float
    coverage: float
    participant_count: int

    def __post_init__(self):
        if (
            len(self.radii) != 24
            or self.coverage != 0.8
            or self.participant_count < 4
            or any(not math.isfinite(v) or v < 0 for v in (*self.radii, self.curve_radius))
        ):
            raise ValueError("invalid finite frozen 80% interval state")
        object.__setattr__(self, "radii", tuple(float(v) for v in self.radii))

    @classmethod
    def fit(cls, truth, prediction):
        truth, prediction = np.asarray(truth, dtype=float), np.asarray(prediction, dtype=float)
        if (
            truth.ndim != 2
            or truth.shape[1] != 24
            or prediction.shape != truth.shape
            or not np.isfinite(truth).all()
            or not np.isfinite(prediction).all()
        ):
            raise ValueError("calibration arrays must be aligned finite 24-point trajectories")
        m = len(truth)
        rank = math.ceil((m + 1) * 0.8)
        if rank > m or m < 4:
            raise ValueError("insufficient participants for a finite 80% calibration rank")
        absolute = np.abs(truth - prediction)
        radii = np.sort(absolute, axis=0)[rank - 1]
        radius = np.sort(absolute.max(axis=1))[rank - 1]
        return cls(tuple(float(v) for v in radii), float(radius), 0.8, m)

    def to_dict(self):
        return {**asdict(self), "radii": list(self.radii)}

    @classmethod
    def from_dict(cls, value):
        return cls(**value)

    def bounds(self, prediction):
        prediction = np.asarray(prediction, dtype=float)
        if prediction.shape[-1:] != (24,) or not np.isfinite(prediction).all():
            raise ValueError("bands require a finite 24-point prediction")
        return (
            prediction - self.radii,
            prediction + self.radii,
            prediction - self.curve_radius,
            prediction + self.curve_radius,
        )


class CalibratedForecastAdapter(ForecastModelAdapter):
    """Immutable interval wrapper; the supplied adapter's point forecast is unchanged."""

    def __init__(self, adapter, bands):
        self.adapter, self.bands = adapter, bands
        self.model_id, self.model_version = adapter.model_id, adapter.model_version

    def load(self):
        self.adapter.load()

    def predict(self, request):
        if request.quantiles != (0.1, 0.5, 0.9) or request.prediction_length != 24:
            raise ValueError("calibrated wrapper requires the frozen 24-point/80% contract")
        result = self.adapter.predict(request)
        lower, upper, _, _ = self.bands.bounds(result.median)
        metadata = tuple((k, v) for k, v in result.metadata if k != "interval")
        return replace(
            result,
            quantiles=(
                QuantileForecast(0.1, tuple(lower)),
                QuantileForecast(0.5, result.median),
                QuantileForecast(0.9, tuple(upper)),
            ),
            metadata=metadata
            + (
                ("interval", "participant_representative_marginal_80"),
                ("coverage_guarantee", "unverified_exchangeability"),
            ),
        )


def interval_summary(rows):
    good = [r for r in rows if r["error_type"] is None]
    output = {"attempted_events": len(rows), "successful_events": len(good)}
    for kind, lower_key, upper_key in (
        ("marginal", "lower", "upper"),
        ("curve", "curve_lower", "curve_upper"),
    ):
        if not good:
            output[kind] = {}
            continue
        truth = np.asarray([r["truth"] for r in good])
        lower = np.asarray([r[lower_key] for r in good])
        upper = np.asarray([r[upper_key] for r in good])
        if (
            lower.shape != truth.shape
            or upper.shape != truth.shape
            or not np.isfinite(lower).all()
            or not np.isfinite(upper).all()
            or np.any(lower > upper)
        ):
            raise ValueError("invalid interval records")
        covered = (lower <= truth) & (truth <= upper)
        groups = defaultdict(list)
        for i, r in enumerate(good):
            groups[r["participant_id"]].append(i)
        macro_horizon = np.mean([covered[g].mean(axis=0) for g in groups.values()], axis=0)
        output[kind] = {
            "macro_point_coverage": float(macro_horizon.mean()),
            "pooled_point_coverage": float(covered.mean()),
            "macro_whole_curve_coverage": float(
                np.mean([covered[g].all(axis=1).mean() for g in groups.values()])
            ),
            "pooled_whole_curve_coverage": float(covered.all(axis=1).mean()),
            "attempted_whole_curve_yield": float(covered.all(axis=1).sum() / len(rows)),
            "mean_width": float((upper - lower).mean()),
            "negative_lower_points": int((lower < 0).sum()),
            "macro_coverage_by_horizon": [float(v) for v in macro_horizon],
            "width_by_horizon": [float(v) for v in (upper - lower).mean(axis=0)],
            "macro_coverage_30": float(macro_horizon[5]),
            "macro_coverage_60": float(macro_horizon[11]),
            "macro_coverage_120": float(macro_horizon[23]),
        }
    return output
