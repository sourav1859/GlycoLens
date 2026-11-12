from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from backend.app.api.meals import MealSave, MealUpdate


def body(**values):
    return dict(
        name="Reviewed meal",
        recorded_at="2026-01-01T12:00:00Z",
        confirmed=True,
        idempotency_key=str(uuid4()),
        items=[dict(food_id=str(uuid4()), grams=125)],
        **values,
    )


@pytest.mark.parametrize(
    "change",
    [
        {"state": "logged"},
        {"consumed_at": "2026-01-01T12:00:00Z"},
        {"recorded_at": "2026-01-01T12:00:00"},
        {"confirmed": False},
        {"name": "   "},
        {"user_id": str(uuid4())},
        {"calories": 500},
    ],
)
def test_invalid_lifecycle_rejected(change):
    values = body()
    values.update(change)
    with pytest.raises(ValidationError):
        MealSave.model_validate(values)


def test_consumed_time_and_revision_required():
    values = body(state="logged", consumed_at="2026-01-01T12:15:00Z")
    assert MealSave.model_validate(values).consumed_at == datetime.fromisoformat(
        "2026-01-01T12:15:00+00:00"
    )
    with pytest.raises(ValidationError):
        MealUpdate.model_validate(values)


def test_legacy_explicit_review_snapshot_is_accepted():
    values = body()
    del values["confirmed"]
    values["input_snapshot"] = {"confirmed": True}
    assert MealSave.model_validate(values).confirmed


@pytest.mark.parametrize(
    "change", [{"nutrient_basis_g": 0}, {"calories": -1}, {"fiber_g": "NaN"}, {"forged_total": 100}]
)
def test_reviewed_facts_cannot_override_validation(change):
    values = body()
    facts = dict(nutrient_basis_g=100, calories=180, carbs_g=30, protein_g=6, fat_g=4, fiber_g=None)
    facts.update(change)
    values["items"][0]["expected_facts"] = facts
    with pytest.raises(ValidationError):
        MealSave.model_validate(values)
