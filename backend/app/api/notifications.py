"""Owned, nonclinical application events; no email or push dispatch."""

from uuid import UUID
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict, Field
from backend.app.db.client import UserSession, database_call, user_session
from backend.app.db.trusted import trusted_call

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


class ReadNotifications(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ids: list[UUID] = Field(min_length=1, max_length=100)


@router.get("")
def notifications(
    offset: int = Query(0, ge=0, le=10000), session: UserSession = Depends(user_session)
):
    rows = database_call(
        session,
        f"notifications?select=id,kind,entity_id,created_at,read_at&order=created_at.desc,id.desc&limit=51&offset={offset}",
    )
    meal_ids = [str(UUID(row["entity_id"])) for row in rows if row["kind"] == "meal_saved"]
    meals = (
        database_call(session, "meals?select=id,workspace&id=in.(" + ",".join(meal_ids) + ")")
        if meal_ids
        else []
    )
    scopes = {meal["id"]: meal["workspace"] for meal in meals}
    for row in rows:
        workspace = (
            scopes.get(row["entity_id"], "legacy_unclassified")
            if row["kind"] == "meal_saved"
            else "simulation"
        )
        prefix = {
            "meal_saved": ("" if workspace == "personal" else "/demo") + "/meals/",
            "forecast_ready": "/demo/forecasts/",
            "source_ready": "/demo/sessions/",
        }[row["kind"]]
        row["workspace"] = workspace
        row["href"] = prefix + str(UUID(row["entity_id"]))
    return {"notifications": rows[:50], "has_more": len(rows) > 50}


@router.patch("/read")
def read(body: ReadNotifications, session: UserSession = Depends(user_session)):
    return {
        "updated": trusted_call(
            session, "rpc/app_read_notifications", payload={"p_ids": [str(i) for i in body.ids]}
        )
    }
