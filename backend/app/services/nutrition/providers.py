"""Provider-grounded food facts. Every stored nutrient uses an explicit gram basis."""

from __future__ import annotations

import math
import os
import re
from urllib.parse import quote

import httpx
from fastapi import HTTPException

from backend.app.core.settings import required_setting
from backend.app.db.client import UserSession, database_call


NUTRIENTS = {1008: "calories", 1005: "carbs_g", 1003: "protein_g", 1004: "fat_g", 1079: "fiber_g"}


def valid_amount(value):
    if value is None:
        return None
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError("invalid food nutrient")
    return value


def usda_food(payload: dict) -> dict:
    nutrients = {name: None for name in NUTRIENTS.values()}
    for entry in payload.get("foodNutrients", []):
        nutrient = entry.get("nutrient", entry)
        identifier = nutrient.get("id", entry.get("nutrientId"))
        unit = nutrient.get("unitName", entry.get("unitName", "")).lower()
        if identifier in NUTRIENTS:
            field = NUTRIENTS[identifier]
            if unit != ("kcal" if field == "calories" else "g"):
                raise ValueError("unexpected nutrient units")
            nutrients[field] = valid_amount(entry.get("amount", entry.get("value")))
    return {
        "name": payload["description"],
        "source": "usda",
        "source_food_id": str(payload["fdcId"]),
        "nutrient_basis_g": 100,
        **nutrients,
        "raw_payload": {"dataType": payload.get("dataType"), "basis": "per_100g"},
    }


def off_food(payload: dict, barcode: str) -> dict:
    product = payload["product"]
    values = product.get("nutriments", {})
    fields = {
        "calories": "energy-kcal_100g",
        "carbs_g": "carbohydrates_100g",
        "protein_g": "proteins_100g",
        "fat_g": "fat_100g",
        "fiber_g": "fiber_100g",
    }
    return {
        "name": product.get("product_name") or product.get("generic_name") or "Packaged food",
        "source": "open_food_facts",
        "source_food_id": barcode,
        "barcode": barcode,
        "nutrient_basis_g": 100,
        **{key: valid_amount(values.get(field)) for key, field in fields.items()},
        "raw_payload": {"basis": "per_100g", "verification": "community_label_requires_review"},
    }


def provider_request(url: str, **kwargs) -> dict:
    try:
        response = httpx.get(url, timeout=12, **kwargs)
        if response.status_code == 404:
            raise HTTPException(404, "Food not found")
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError, KeyError):
        raise HTTPException(
            503, "Food provider is unavailable; use a cached food or retry"
        ) from None


def store_provider_food(food: dict) -> dict:
    """Privileged access is restricted to facts fetched by trusted provider adapters."""
    try:
        secret_key = os.environ.get("SUPABASE_SECRET_KEY", "").strip()
        key = secret_key or required_setting("SUPABASE_SERVICE_ROLE_KEY")
        headers = {
            "apikey": key,
            "Prefer": "resolution=merge-duplicates,return=representation",
        }
        # Modern API keys are not JWTs. Only the legacy fallback is a bearer token.
        if not secret_key:
            headers["Authorization"] = "Bearer " + key
        response = httpx.post(
            required_setting("SUPABASE_URL").rstrip("/")
            + "/rest/v1/foods?on_conflict=source,source_food_id",
            headers=headers,
            json=food,
            timeout=12,
        )
        response.raise_for_status()
        return response.json()[0]
    except (RuntimeError, httpx.HTTPError, ValueError, KeyError, IndexError):
        raise HTTPException(503, "Food facts could not be cached") from None


def search_foods(query: str, session: UserSession) -> dict:
    cached = database_call(
        session, "foods?select=*&name=ilike.*" + quote(query, safe="") + "*&limit=10"
    )
    if not os.environ.get("USDA_FDC_API_KEY"):
        return {"foods": cached, "source": "cache", "notice": "Live USDA search is not configured"}
    try:
        payload = provider_request(
            "https://api.nal.usda.gov/fdc/v1/foods/search",
            params={
                "api_key": required_setting("USDA_FDC_API_KEY"),
                "query": query,
                "pageSize": 10,
            },
        )
        # Search returns candidates. Fetch details only after user picks an identifier.
        candidates = [
            {"name": p["description"], "source_food_id": str(p["fdcId"]), "source": "usda"}
            for p in payload.get("foods", [])
        ]
        return {"foods": cached, "candidates": candidates, "source": "usda"}
    except HTTPException:
        if cached:
            return {
                "foods": cached,
                "source": "cache",
                "notice": "Provider unavailable; cached facts shown",
            }
        raise


def resolve_usda(identifier: int, session: UserSession) -> dict:
    cached = database_call(session, f"foods?source=eq.usda&source_food_id=eq.{identifier}&limit=1")
    if cached:
        return cached[0]
    try:
        return store_provider_food(
            usda_food(
                provider_request(
                    f"https://api.nal.usda.gov/fdc/v1/food/{identifier}",
                    params={"api_key": required_setting("USDA_FDC_API_KEY")},
                )
            )
        )
    except RuntimeError:
        raise HTTPException(503, "Live USDA lookup is not configured") from None
    except (ValueError, KeyError):
        raise HTTPException(422, "Food nutrition requires source verification") from None


def resolve_barcode(barcode: str, session: UserSession) -> dict:
    cached = database_call(session, f"foods?barcode=eq.{barcode}&limit=1")
    if cached:
        return cached[0]
    agent = os.environ.get("OPEN_FOOD_FACTS_USER_AGENT", "").strip()
    if not re.fullmatch(r"GlycoLens/[\w.]+ \([^\s()@]+@[^\s()@]+\.[^\s()@]+\)", agent):
        raise HTTPException(
            503,
            "Live barcode lookup needs the project contact configured; use food search meanwhile",
        )
    payload = provider_request(
        f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json",
        headers={"User-Agent": agent},
    )
    if payload.get("status") != 1:
        raise HTTPException(404, "Barcode not found; try food search")
    try:
        return store_provider_food(off_food(payload, barcode))
    except (ValueError, KeyError):
        raise HTTPException(422, "Product nutrition requires verification") from None
