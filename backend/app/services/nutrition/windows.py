"""Calendar-day boundaries, always converted after local midnight construction."""

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo


def day_bounds(day: date, zone: str):
    local = ZoneInfo(zone)
    return (
        datetime.combine(day, time.min, local).astimezone(timezone.utc),
        datetime.combine(day + timedelta(days=1), time.min, local).astimezone(timezone.utc),
    )
