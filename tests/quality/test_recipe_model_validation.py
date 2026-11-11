"""Validate the live-check budget gate and independently scored recipe oracle."""

from copy import deepcopy
from decimal import Decimal
import json

import pytest

from scripts.validation import validate_recipe_model as validation


@pytest.mark.parametrize("budget", ["0", "-1", "5.01", "0.01", "NaN"])
def test_paid_run_rejects_unapproved_or_insufficient_budget_before_http(monkeypatch, budget):
    monkeypatch.setattr(
        "sys.argv",
        [
            "validate",
            "--allow-paid",
            "--budget-usd",
            budget,
            "--compare",
            "--output",
            "unused.json",
        ],
    )

    def unexpected(*args, **kwargs):
        pytest.fail("Budget rejection must happen before making an API request")

    monkeypatch.setattr(validation.recipes.httpx, "post", unexpected)
    with pytest.raises(SystemExit) as caught:
        validation.main()
    assert caught.value.code == 2


def test_default_is_dry_run_with_conservative_reserve(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv", ["validate", "--budget-usd", "5", "--compare", "--output", "unused.json"]
    )

    def unexpected(*args, **kwargs):
        pytest.fail("Dry-run mode must not make API requests")

    monkeypatch.setattr(validation.recipes.httpx, "post", unexpected)
    validation.main()
    assert "16 calls; reserve USD 0.2192; no requests" in capsys.readouterr().out
    assert validation.request_reserve("gpt-6-luna") < Decimal("0.01")


@pytest.mark.parametrize("failure", ["quantity", "unit", "servings", "extra_ingredient"])
def test_oracle_detects_incorrect_extraction(failure):
    case = json.loads(validation.FIXTURES.read_text())[0]
    actual = {
        "servings": 2,
        "ingredients": [
            {"name": "rice", "quantity": 100, "unit": "g", "needs_review": False},
            {"name": "chicken breast", "quantity": 150, "unit": "g", "needs_review": False},
        ],
    }
    assert not validation.check_extraction(case, actual)
    bad = deepcopy(actual)
    if failure == "quantity":
        bad["ingredients"][0]["quantity"] = 101
    elif failure == "unit":
        bad["ingredients"][0]["unit"] = "ml"
    elif failure == "servings":
        bad["servings"] = 3
    else:
        bad["ingredients"].append(
            {"name": "invented food", "quantity": 1, "unit": "g", "needs_review": False}
        )
    assert validation.check_extraction(case, bad)


def test_oracle_requires_review_for_ambiguous_portion():
    case = json.loads(validation.FIXTURES.read_text())[-1]
    actual = {
        "servings": 1,
        "ingredients": [
            {"name": "cooked rice", "quantity": 1, "unit": "small bowl", "needs_review": False}
        ],
    }
    assert "missing_ambiguity_flag" in validation.check_extraction(case, actual)
    actual["ingredients"][0]["needs_review"] = True
    assert not validation.check_extraction(case, actual)


@pytest.mark.parametrize("parentheses", [True, False])
def test_repeated_ingredient_role_labels_preserve_total_quantity(parentheses):
    case = json.loads(validation.FIXTURES.read_text())[4]

    def role(text):
        return f"flour ({text})" if parentheses else f"flour {text}"

    actual = {
        "servings": 2,
        "ingredients": [
            {"name": role("for the dough"), "quantity": 100, "unit": "g", "needs_review": False},
            {"name": role("for dusting"), "quantity": 50, "unit": "g", "needs_review": False},
            {"name": "water", "quantity": 100, "unit": "ml", "needs_review": False},
        ],
    }
    assert not validation.check_extraction(case, actual)
    actual["ingredients"][1]["quantity"] = 49
    assert "quantity_mismatch" in validation.check_extraction(case, actual)
