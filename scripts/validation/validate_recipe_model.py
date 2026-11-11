"""Bounded, opt-in live validation using synthetic recipe fixtures only."""

import argparse
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
import json
import math
import os
from pathlib import Path
from time import perf_counter
from unittest.mock import patch

from fastapi import HTTPException

from backend.app.core.settings import load_local_configuration
from backend.app.services.nutrition import recipes


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests/fixtures/recipe_extraction_cases.json"
RATES = {
    "gpt-6-luna": (Decimal("0.10"), Decimal("0.01"), Decimal("0.50")),
    "gpt-5-mini": (Decimal("0.25"), Decimal("0.025"), Decimal("2.00")),
}
APPROVED_CAP = Decimal("5")
MAX_INPUT_ALLOWANCE = 64000
MAX_OUTPUT = 2000


def normalize(value):
    return " ".join(value.lower().strip().split())


def check_extraction(case, actual):
    """Score against independently written quantities, units and serving counts."""
    unit_aliases = {
        "grams": "g",
        "gram": "g",
        "milliliters": "ml",
        "millilitres": "ml",
        "milliliter": "ml",
        "millilitre": "ml",
        "cups": "cup",
        "tablespoon": "tbsp",
        "tablespoons": "tbsp",
        "teaspoon": "tsp",
        "teaspoons": "tsp",
        "small bowl": "bowl",
        "bowls": "bowl",
    }
    totals, reviewed, errors = defaultdict(float), set(), []
    expected = case["ingredients"]
    for item in actual["ingredients"]:
        match = next(
            (i for i, want in enumerate(expected) if normalize(item["name"]) in want["names"]),
            None,
        )
        if match is None:
            errors.append("unexpected_ingredient")
            continue
        unit = normalize(item["unit"])
        totals[match, unit_aliases.get(unit, unit)] += item["quantity"]
        if item["needs_review"]:
            reviewed.add(match)
    wanted = {(i, item["unit"]): item["quantity"] for i, item in enumerate(expected)}
    if set(totals) != set(wanted):
        errors.append("ingredient_or_unit_mismatch")
    for key, quantity in wanted.items():
        if not math.isclose(totals.get(key, -1), quantity, abs_tol=1e-9):
            errors.append("quantity_mismatch")
    if not math.isclose(actual["servings"], case["servings"], abs_tol=1e-9):
        errors.append("servings_mismatch")
    if any(item.get("needs_review") and i not in reviewed for i, item in enumerate(expected)):
        errors.append("missing_ambiguity_flag")
    return sorted(set(errors))


def request_reserve(model):
    input_rate, _, output_rate = RATES[model]
    return (MAX_INPUT_ALLOWANCE * input_rate + MAX_OUTPUT * output_rate) / 1000000


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-paid", action="store_true")
    parser.add_argument("--budget-usd", type=Decimal, required=True)
    parser.add_argument("--compare", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = json.loads(FIXTURES.read_text(encoding="utf-8"))
    models = ["gpt-6-luna"] + (["gpt-5-mini"] if args.compare else [])
    budget = args.budget_usd
    if not budget.is_finite() or not 0 < budget <= APPROVED_CAP:
        parser.error("Budget must be positive and within the approved USD 5 cap")
    reserve = sum((request_reserve(m) * len(cases) for m in models), Decimal(0))
    if reserve > budget:
        parser.error("Conservative planned request reserve exceeds the supplied budget")
    if not args.allow_paid:
        print(f"DRY RUN: {len(cases) * len(models)} calls; reserve USD {reserve}; no requests")
        return
    load_local_configuration()
    if os.environ.get("LLM_MODEL") != "gpt-6-luna":
        parser.error("Configured model must be the approved gpt-6-luna target")
    if not os.environ.get("LLM_API_KEY"):
        parser.error("Private LLM_API_KEY is required")
    known_cost, uncertain_reserve = Decimal(0), Decimal(0)
    calls, results, abort = [], [], False
    original_post = recipes.httpx.post

    def bounded_post(url, **kwargs):
        nonlocal known_cost, uncertain_reserve
        body = kwargs["json"]
        model = body["model"]
        if (
            url != "https://api.openai.com/v1/responses"
            or model not in models
            or len(calls) >= len(cases) * len(models)
            or body.get("max_output_tokens") != MAX_OUTPUT
            or body.get("input") not in {case["text"] for case in cases}
            or len(json.dumps(body).encode("utf-8")) > 20000
        ):
            raise RuntimeError("Live validation request guard failed")
        call_reserve = request_reserve(model)
        uncertain_reserve += call_reserve
        calls.append({"model": model, "usage": None})
        response = original_post(url, **kwargs)
        if response.is_success:
            usage = response.json().get("usage")
            if usage:
                calls[-1]["usage"] = usage
                cached = usage.get("input_tokens_details", {}).get("cached_tokens", 0)
                input_rate, cached_rate, output_rate = RATES[model]
                cost = (
                    (usage["input_tokens"] - cached) * input_rate
                    + cached * cached_rate
                    + usage["output_tokens"] * output_rate
                ) / 1000000
                known_cost += cost
                uncertain_reserve -= call_reserve
                calls[-1]["estimated_cost_usd"] = str(cost)
                if usage["input_tokens"] > MAX_INPUT_ALLOWANCE or known_cost > budget:
                    raise RuntimeError("Observed usage exceeded the validation allowance")
        return response

    with patch.object(recipes.httpx, "post", bounded_post):
        for model in models:
            for case in cases:
                os.environ["LLM_MODEL"] = model
                started = perf_counter()
                try:
                    actual = recipes.parse_recipe(case["text"])
                    errors = check_extraction(case, actual)
                except (HTTPException, RuntimeError):
                    actual, errors, abort = None, ["extraction_unavailable"], True
                results.append(
                    {
                        "model": model,
                        "case_id": case["id"],
                        "passed": not errors,
                        "errors": errors,
                        "seconds": round(perf_counter() - started, 3),
                        "actual": actual,
                    }
                )
                print(f"{model} / {case['id']}: {'PASS' if not errors else 'FAIL'}", flush=True)
                if abort:
                    break
            if abort:
                break
    os.environ["LLM_MODEL"] = "gpt-6-luna"
    output = {
        "executed_at_utc": datetime.now(timezone.utc).isoformat(),
        "approved_budget_usd": str(budget),
        "planned_reserve_usd": str(reserve),
        "estimated_known_cost_usd": str(known_cost),
        "unpriced_request_reserve_usd": str(uncertain_reserve),
        "pricing_source": "https://developers.openai.com/api/docs/pricing",
        "fixture_file": str(FIXTURES.relative_to(ROOT)),
        "scope": "Synthetic smoke comparison; not a representative accuracy guarantee",
        "results": results,
        "calls": calls,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(
        f"Calls: {len(calls)}; estimated known cost USD {known_cost}; unpriced reserve USD {uncertain_reserve}"
    )
    if abort or any(not result["passed"] for result in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
