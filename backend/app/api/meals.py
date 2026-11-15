"""Authenticated meal/timeline APIs; identity is derived from the verified session."""

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend.app.db.client import UserSession, database_call, user_session
from backend.app.db.trusted import trusted_call
from backend.app.services.retrieval.numeric import similar_meals
from backend.app.services.nutrition.windows import day_bounds
from urllib.parse import quote
from backend.app.services.workspaces import Workspace, meal_partition, owned_source


router = APIRouter(prefix="/api/v1", tags=["application"])


class ReviewedFacts(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nutrient_basis_g: float = Field(gt=0, allow_inf_nan=False)
    calories: float | None = Field(ge=0, allow_inf_nan=False)
    carbs_g: float | None = Field(ge=0, allow_inf_nan=False)
    protein_g: float | None = Field(ge=0, allow_inf_nan=False)
    fat_g: float | None = Field(ge=0, allow_inf_nan=False)
    fiber_g: float | None = Field(ge=0, allow_inf_nan=False)


class MealItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    food_id: UUID
    grams: float = Field(gt=0, le=10000, allow_inf_nan=False)
    expected_facts: ReviewedFacts | None = None


class MealSave(BaseModel):
    model_config = ConfigDict(extra="forbid")
    workspace: Literal["personal", "simulation"]
    source_session_id: UUID | None = None
    name: str = Field(min_length=1, max_length=200)
    recorded_at: datetime
    idempotency_key: UUID
    items: list[MealItem] = Field(min_length=1, max_length=100)
    input_snapshot: dict = Field(default_factory=dict)
    confirmed: Literal[True]
    state: Literal["planned", "logged"] = "planned"
    consumed_at: datetime | None = None
    meal_type: Literal["breakfast", "lunch", "dinner", "snack"] | None = None

    @model_validator(mode="before")
    @classmethod
    def legacy_review(cls, value):
        snapshot = value.get("input_snapshot") if isinstance(value, dict) else None
        if (
            isinstance(value, dict)
            and "confirmed" not in value
            and isinstance(snapshot, dict)
            and snapshot.get("confirmed") is True
        ):
            return {**value, "confirmed": True}
        return value

    @field_validator("recorded_at", "consumed_at")
    @classmethod
    def aware_time(cls, value):
        if value is not None and value.tzinfo is None:
            raise ValueError("Meal time must include a timezone")
        return value

    @field_validator("name")
    @classmethod
    def nonblank_name(cls, value):
        if not value.strip():
            raise ValueError("Name must not be blank")
        return value.strip()

    @model_validator(mode="after")
    def consumption_contract(self):
        if (self.workspace == "simulation") != (self.source_session_id is not None):
            raise ValueError(
                "Simulation requires an explicit source; personal meals cannot use one"
            )
        if (self.state == "logged") != (self.consumed_at is not None):
            raise ValueError("Only logged meals require consumed_at")
        if len(str(self.input_snapshot)) > 16000:
            raise ValueError("Input snapshot is too large")
        return self


class MealUpdate(MealSave):
    revision: int = Field(ge=1)


class MealCancel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    revision: int = Field(ge=1)
    idempotency_key: UUID


def commit(session, body, *, meal_id=None, revision=0):
    values = body.model_dump(mode="json", exclude={"idempotency_key", "revision"})
    values["items"] = [
        item.model_dump(
            mode="json", exclude={"expected_facts"} if item.expected_facts is None else set()
        )
        for item in body.items
    ]
    return trusted_call(
        session,
        "rpc/app_commit_meal",
        payload={
            "p_meal": str(meal_id) if meal_id else None,
            "p_revision": revision,
            "p_key": str(body.idempotency_key),
            "p_values": values,
        },
    )


@router.post("/demo/session")
def initialize_demo(session: UserSession = Depends(user_session)):
    return {"user_id": trusted_call(session, "rpc/app_initialize_user", payload={})}


@router.post("/meals")
def save_meal(body: MealSave, session: UserSession = Depends(user_session)):
    return commit(session, body)


@router.get("/meals")
def list_meals(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0, le=10000),
    day: date | None = None,
    slot: Literal["breakfast", "lunch", "dinner", "snack"] | None = None,
    workspace: Workspace = "personal",
    source_session_id: UUID | None = None,
    session: UserSession = Depends(user_session),
):
    if day and not 1970 <= day.year <= 2100:
        raise HTTPException(422, "Choose a local day between 1970 and 2100")
    preferences = database_call(session, "user_preferences?select=timezone&limit=1")
    partition = meal_partition(session, workspace, source_session_id)
    filters = ""
    if day and preferences:
        start, end = day_bounds(day, preferences[0]["timezone"])
        a, b = quote(start.isoformat(), safe=""), quote(end.isoformat(), safe="")
        filters += f"&or=(and(state.eq.logged,consumed_at.gte.{a},consumed_at.lt.{b}),and(state.neq.logged,recorded_at.gte.{a},recorded_at.lt.{b}))"
    if slot:
        filters += "&meal_type=eq." + slot
    rows = database_call(
        session,
        f"meals?select=*&{partition}&order=recorded_at.desc,id.desc&limit={limit + 1}&offset={offset}"
        + filters,
    )
    return {
        "meals": rows[:limit],
        "has_more": len(rows) > limit,
        "workspace": workspace,
        "source_session_id": str(source_session_id) if source_session_id else None,
    }


@router.patch("/meals/{meal_id}")
def update_meal(meal_id: UUID, body: MealUpdate, session: UserSession = Depends(user_session)):
    return commit(session, body, meal_id=meal_id, revision=body.revision)


@router.delete("/meals/{meal_id}")
def cancel_meal(meal_id: UUID, body: MealCancel, session: UserSession = Depends(user_session)):
    rows = database_call(session, f"meals?id=eq.{meal_id}&select=*,meal_items(*)")
    if not rows:
        raise HTTPException(404, "Meal not found")
    meal = rows[0]
    return trusted_call(
        session,
        "rpc/app_commit_meal",
        payload={
            "p_meal": str(meal_id),
            "p_revision": body.revision,
            "p_key": str(body.idempotency_key),
            "p_values": {
                "workspace": meal["workspace"],
                "source_session_id": meal["source_session_id"],
                "name": meal["name"],
                "recorded_at": meal["recorded_at"],
                "state": "cancelled",
                "confirmed": True,
                "meal_type": meal.get("meal_type"),
                "input_snapshot": meal["input_snapshot"],
                "items": [
                    {"food_id": item["food_id"], "grams": item["grams"]}
                    for item in meal["meal_items"]
                ],
            },
        },
    )


@router.get("/meals/{meal_id}")
def get_meal(meal_id: UUID, session: UserSession = Depends(user_session)):
    return database_call(session, f"meals?id=eq.{meal_id}&select=*,meal_items(*,foods(*))")


@router.get("/timeline")
def timeline(
    source_session_id: UUID,
    workspace: Literal["simulation"] = "simulation",
    session: UserSession = Depends(user_session),
):
    source = owned_source(session, source_session_id)["id"]
    partition = "&source_session_id=eq." + str(source)
    return {
        "workspace": "simulation",
        "source_session_id": source,
        "cgm": database_call(
            session,
            "cgm_readings?select=recorded_at,glucose_mg_dl,source&order=recorded_at.desc&limit=288"
            + partition,
        ),
        "insulin": database_call(
            session,
            "insulin_events?select=recorded_at,event_type,units,insulin_kind,source_unit&order=recorded_at.desc&limit=500"
            + partition,
        ),
        "meals": database_call(
            session,
            "meals?select=id,name,recorded_at,state,consumed_at,carbs_g,protein_g,fat_g,fiber_g&order=recorded_at.desc&limit=100"
            + partition,
        ),
    }


@router.get("/meals/{meal_id}/similar")
def similar(meal_id: UUID, session: UserSession = Depends(user_session)):
    return {"meals": similar_meals(session, meal_id)}
