from unittest.mock import patch
import pytest
from backend.app.api.nutrition import home
from backend.app.db.client import UserSession


@pytest.mark.parametrize(
    "meal,visible",
    [
        ({"revision": 2, "state": "logged"}, True),
        ({"revision": 3, "state": "logged"}, False),
        ({"revision": 2, "state": "cancelled"}, False),
    ],
)
def test_home_only_shows_unchanged_active_forecast(meal, visible):
    mid = "10000000-0000-4000-8000-000000000001"
    with (
        patch(
            "backend.app.api.nutrition.nutrition_summary", return_value={"source": {"id": "source"}}
        ),
        patch(
            "backend.app.api.nutrition.database_call",
            side_effect=[[], [{"meal_id": mid, "meal_revision": 2}], [meal]],
        ),
    ):
        assert bool(home(session=UserSession("synthetic", "owner"))["forecasts"]) is visible
