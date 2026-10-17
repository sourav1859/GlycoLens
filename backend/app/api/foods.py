from fastapi import APIRouter, Depends, Path, Query
from pydantic import BaseModel, Field

from backend.app.db.client import UserSession, user_session
from backend.app.services.nutrition.providers import resolve_barcode, resolve_usda, search_foods
from backend.app.services.nutrition.recipes import parse_recipe


router = APIRouter(prefix="/api/v1", tags=["nutrition"])


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
    text: str = Field(min_length=3, max_length=4000)


@router.post("/meals/parse-recipe")
def recipe(body: RecipeText, session: UserSession = Depends(user_session)):
    return parse_recipe(body.text)
