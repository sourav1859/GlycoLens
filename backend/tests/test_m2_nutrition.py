import pytest
from fastapi import HTTPException

from backend.app.services.nutrition.providers import off_food, usda_food
from backend.app.services.nutrition.recipes import parse_recipe, ParsedRecipe


def test_provider_basis_and_missing_nutrients_remain_explicit():
    food = usda_food(
        {
            "description": "Synthetic food",
            "fdcId": 123,
            "foodNutrients": [
                {"nutrient": {"id": 1005, "unitName": "g"}, "amount": 40},
            ],
        }
    )
    assert food["nutrient_basis_g"] == 100 and food["carbs_g"] == 40
    assert food["fiber_g"] is None
    other = off_food(
        {
            "product": {
                "product_name": "Synthetic product",
                "nutriments": {"carbohydrates_100g": 20},
            }
        },
        "12345678",
    )
    assert other["carbs_g"] == 20 and other["calories"] is None
    with pytest.raises(ValueError, match="units"):
        usda_food(
            {
                "description": "bad",
                "fdcId": 1,
                "foodNutrients": [{"nutrient": {"id": 1008, "unitName": "kJ"}, "amount": 100}],
            }
        )


def test_recipe_contract_rejects_model_supplied_nutrition_and_bad_quantities():
    with pytest.raises(ValueError):
        ParsedRecipe.model_validate(
            {
                "ingredients": [
                    {"name": "rice", "quantity": -1, "unit": "g", "needs_review": False}
                ],
                "servings": 1,
            }
        )
    with pytest.raises(ValueError):
        ParsedRecipe.model_validate(
            {
                "ingredients": [
                    {
                        "name": "rice",
                        "quantity": 100,
                        "unit": "g",
                        "needs_review": False,
                        "carbs": 50,
                    }
                ],
                "servings": 1,
            }
        )


def test_recipe_uses_structured_extraction_without_sending_patient_context(monkeypatch):
    import json
    import httpx
    import backend.app.services.nutrition.recipes as recipes

    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("LLM_API_KEY", "test-only")
    captured = {}

    def post(url, **kwargs):
        captured.update(kwargs["json"])
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={
                "status": "completed",
                "output": [
                    {
                        "content": [
                            {
                                "type": "output_text",
                                "text": json.dumps(
                                    {
                                        "ingredients": [
                                            {
                                                "name": "rice",
                                                "quantity": 100,
                                                "unit": "g",
                                                "needs_review": False,
                                            }
                                        ],
                                        "servings": 2,
                                    }
                                ),
                            }
                        ]
                    }
                ],
            },
        )

    monkeypatch.setattr(recipes.httpx, "post", post)
    result = parse_recipe("100 g rice for two servings")
    assert result["verification"] == "user_confirmation_required"
    assert captured["store"] is False
    assert captured["text"]["format"]["strict"] is True
    assert captured["input"] == "100 g rice for two servings"


def test_recipe_configuration_errors_are_redacted(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(HTTPException) as caught:
        parse_recipe("100 g rice")
    assert caught.value.status_code == 503
    assert "LLM_API_KEY" not in caught.value.detail
