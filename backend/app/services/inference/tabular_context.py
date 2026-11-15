"""Training-compatible, past-only features for the reviewed long synthetic source."""

from datetime import datetime, timedelta
import math
from fastapi import HTTPException
from research.models.adapters.base import CovariateSeries, ForecastRequest, TimePoint

PROTOCOL = "lightgbm_warmup_48h_v1"


def stamp(value):
    at = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if at.tzinfo is None:
        raise ValueError("aware source timestamps required")
    return at


def basal_amount(events, start, end):
    rates = sorted(
        (stamp(e["recorded_at"]), float(e["units"]))
        for e in events
        if e["event_type"] == "basal" and stamp(e["recorded_at"]) <= end
    )
    if not any(at <= start for at, _ in rates):
        return None
    cuts = sorted({start, end, *(at for at, _ in rates if start < at < end)})
    amount = 0.0
    for left, right in zip(cuts, cuts[1:]):
        rate = next(value for at, value in reversed(rates) if at <= left)
        amount += rate * (right - left).total_seconds() / 3600
    return amount


def build_tabular_request(meal, cgm, insulin, metadata):
    try:
        origin = stamp(meal["recorded_at"])
        if metadata.get("scenario") != PROTOCOL:
            raise ValueError("Start the separate 48-hour research simulation for LightGBM")
        first = origin - timedelta(hours=6)
        if (
            stamp(metadata["event_coverage_start"]) > first
            or stamp(metadata["event_coverage_end"]) < origin
        ):
            raise ValueError("Reviewed event observation coverage is incomplete")
        grid = tuple(origin - timedelta(minutes=5 * i) for i in range(287, -1, -1))
        by_time = {}
        for p in cgm:
            at = stamp(p["recorded_at"])
            if stamp(p.get("available_at", p["recorded_at"])) > origin:
                continue
            if not grid[0] <= at <= origin:
                continue
            if at in by_time or at not in grid or p.get("source") != "simulation":
                raise ValueError("Duplicate, off-grid or unreviewed CGM context")
            value = float(p["glucose_mg_dl"])
            if not math.isfinite(value) or not 20 <= value <= 600:
                raise ValueError("Invalid CGM history")
            by_time[at] = value
        if set(by_time) != set(grid):
            raise ValueError("LightGBM needs 288 regular CGM samples (24 hours)")
        events = []
        for e in insulin:
            at = stamp(e["recorded_at"])
            if at > origin or stamp(e.get("available_at", e["recorded_at"])) > origin:
                continue
            unit = "U/h" if e["event_type"] == "basal" else "U"
            if (
                e["event_type"] not in {"basal", "bolus"}
                or e.get("source_unit") != unit
                or e.get("insulin_kind") != "R"
            ):
                raise ValueError("Unverified synthetic insulin units or kind")
            if not math.isfinite(float(e["units"])) or float(e["units"]) < 0:
                raise ValueError("Invalid recorded insulin")
            events.append(e)
        basal_times = [stamp(e["recorded_at"]) for e in events if e["event_type"] == "basal"]
        if len(basal_times) != len(set(basal_times)):
            raise ValueError("Conflicting duplicate basal rate")
        times = [origin - timedelta(minutes=5 * i) for i in range(71, -1, -1)]

        def bucket(at):
            return origin - timedelta(seconds=math.floor((origin - at).total_seconds() / 300) * 300)

        bolus, carbs = {}, {}
        for e in events:
            at = stamp(e["recorded_at"])
            if e["event_type"] == "bolus" and first < at <= origin:
                b = bucket(at)
                bolus[b] = bolus.get(b, 0) + float(e["units"])
        for e in metadata.get("meal_events", []):
            at = stamp(e["recorded_at"])
            if first < at <= origin and stamp(e.get("available_at", e["recorded_at"])) <= origin:
                amount = float(e["carbs_g"])
                if not math.isfinite(amount) or amount < 0:
                    raise ValueError("Invalid previous carbohydrates")
                b = bucket(at)
                carbs[b] = carbs.get(b, 0) + amount
        past = [
            CovariateSeries(
                "cgm_record_present",
                tuple(TimePoint(at, 1) for at in grid),
                "source_record_present",
            )
        ]
        for name, values, unit in (
            ("insulin_bolus", bolus, "IU_per_source_interval"),
            ("insulin_basal", None, "IU_per_source_interval"),
            ("previous_meal_carbohydrates", carbs, "g"),
        ):
            absent = {stamp(at) for at in metadata.get("missing_event_bins", {}).get(name, [])}
            points, masks = [], []
            for at in times:
                amount = (
                    basal_amount(events, at - timedelta(minutes=5), at)
                    if values is None
                    else values.get(at, 0)
                )
                observed = at not in absent and amount is not None
                masks.append(TimePoint(at, int(observed)))
                if observed:
                    points.append(TimePoint(at, amount))
            if points:
                past.append(CovariateSeries(name, tuple(points), unit))
            past.append(
                CovariateSeries(name + "_record_present", tuple(masks), "source_record_present")
            )
        current = float(meal["carbs_g"])
        if not math.isfinite(current) or current < 0:
            raise ValueError("Reviewed current carbohydrates required")
        return ForecastRequest(
            tuple(TimePoint(at, by_time[at]) for at in grid),
            past_covariates=tuple(past),
            known_covariates=(
                CovariateSeries("meal_carbohydrates", (TimePoint(origin, current),), "g"),
            ),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(
            422,
            str(exc)
            if isinstance(exc, ValueError)
            else "Reviewed 24-hour source context is required",
        ) from None
