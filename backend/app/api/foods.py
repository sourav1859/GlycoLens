from fastapi import APIRouter, Depends, Path, Query
from pydantic import BaseModel, ConfigDict, Field
from backend.app.db.trusted import trusted_call
import os
from fastapi import HTTPException
from uuid import UUID
from backend.app.db.client import database_call

from backend.app.db.client import UserSession, user_session
from backend.app.services.nutrition.providers import resolve_barcode, resolve_usda, search_foods
from backend.app.services.nutrition.recipes import parse_recipe


router = APIRouter(prefix="/api/v1", tags=["nutrition"])


class CachedFoods(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ids: list[UUID] = Field(min_length=1, max_length=100)


@router.post("/foods/cached")
def cached_foods(body: CachedFoods, session: UserSession = Depends(user_session)):
    ids = ",".join(str(value) for value in sorted(set(body.ids)))
    return {"foods": database_call(session, f"foods?id=in.({ids})&select=*&limit=100")}


@router.get("/foods/search")
def search(
    q: str = Query(min_length=2, max_length=100), session: UserSession = Depends(user_session)
):
    return search_foods(q, session)


@router.get("/foods/usda/{identifier}")
def usda(identifier: int = Path(gt=0), session: UserSession = Depends(user_session)):
    return resolve_usda(identifier, session)


@router.get("/foods/barcode/{barcode}")
def barcode_food(
    barcode: str = Path(pattern=r"^\d{8,14}$"), session: UserSession = Depends(user_session)
):
    return resolve_barcode(barcode, session)


class RecipeText(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=3, max_length=4000)


@router.post("/meals/parse-recipe")
def recipe(body: RecipeText, session: UserSession = Depends(user_session)):
    if os.environ.get("LLM_MODEL") != "gpt-6-luna":
        raise HTTPException(503, "Recipe extraction requires the approved model configuration")
    trusted_call(session, "rpc/app_reserve_recipe_request", payload={})
    return parse_recipe(body.text)
