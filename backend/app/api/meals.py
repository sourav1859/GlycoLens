"""Authenticated meal/timeline APIs; identity is derived from the verified session."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field

from backend.app.db.client import UserSession, database_call, user_session
from backend.app.services.retrieval.numeric import similar_meals


router = APIRouter(prefix="/api/v1", tags=["application"])


class MealItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    food_id: UUID
    grams: float = Field(gt=0, le=10000, allow_inf_nan=False)


class MealSave(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=200)
    recorded_at: datetime
    idempotency_key: UUID
    items: list[MealItem] = Field(min_length=1, max_length=100)
    input_snapshot: dict = Field(default_factory=dict)


@router.post("/demo/session")
def initialize_demo(session: UserSession = Depends(user_session)):
    return {"user_id": database_call(session, "rpc/initialize_demo", method="POST", payload={})}


@router.post("/meals")
def save_meal(body: MealSave, session: UserSession = Depends(user_session)):
    if body.recorded_at.tzinfo is None:
        from fastapi import HTTPException

        raise HTTPException(422, "Meal time must include a timezone")
    meal = database_call(
        session,
        "rpc/save_meal",
        method="POST",
        payload={
            "p_name": body.name,
            "p_recorded_at": body.recorded_at.isoformat(),
            "p_key": str(body.idempotency_key),
            "p_items": [item.model_dump(mode="json") for item in body.items],
            "p_snapshot": body.input_snapshot,
        },
    )
    return {"meal_id": meal}


@router.get("/meals/{meal_id}")
def get_meal(meal_id: UUID, session: UserSession = Depends(user_session)):
    return database_call(session, f"meals?id=eq.{meal_id}&select=*,meal_items(*)")


@router.get("/timeline")
def timeline(session: UserSession = Depends(user_session)):
    return {
        "cgm": database_call(
            session,
            "cgm_readings?select=recorded_at,glucose_mg_dl,source&order=recorded_at.desc&limit=288",
        ),
        "insulin": database_call(
            session,
            "insulin_events?select=recorded_at,event_type,units,insulin_kind,source_unit&order=recorded_at.desc&limit=500",
        ),
        "meals": database_call(
            session,
            "meals?select=id,name,recorded_at,carbs_g,protein_g,fat_g,fiber_g&order=recorded_at.desc&limit=100",
        ),
    }


@router.get("/meals/{meal_id}/similar")
def similar(meal_id: UUID, session: UserSession = Depends(user_session)):
    return {"meals": similar_meals(session, meal_id)}
