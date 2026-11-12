from datetime import date

import pytest

from backend.app.services.nutrition.windows import day_bounds


@pytest.mark.parametrize(
    "day,hours", [(date(2026, 3, 8), 23), (date(2026, 7, 8), 24), (date(2026, 11, 1), 25)]
)
def test_local_day_uses_calendar_midnights(day, hours):
    start, end = day_bounds(day, "America/New_York")
    assert (end - start).total_seconds() == hours * 3600
    assert start.tzinfo is not None and end.tzinfo is not None


def test_non_hour_offset_and_adjacent_day_boundary():
    start, end = day_bounds(date(2026, 1, 1), "Asia/Kathmandu")
    following, _ = day_bounds(date(2026, 1, 2), "Asia/Kathmandu")
    assert start.isoformat() == "2025-12-31T18:15:00+00:00"
    assert end == following
