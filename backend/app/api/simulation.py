from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from typing import Literal
from uuid import UUID
from datetime import datetime

from backend.app.db.client import UserSession, user_session, database_call
from backend.app.services.workspaces import owned_source
from backend.app.services.simulation.live import live_scenario, advance_source


router = APIRouter(prefix="/api/v1/simulation", tags=["simulation"])


@router.get("/sources")
def sources(offset: int = Query(0, ge=0, le=10000), session: UserSession = Depends(user_session)):
    rows = database_call(
        session,
        f"source_sessions?select=id,mode,clock_at,created_at&order=created_at.desc,id.desc&limit=21&offset={offset}",
    )
    return {"sources": rows[:20], "has_more": len(rows) > 20}


@router.get("/sources/{source_id}")
def source_detail(source_id: UUID, session: UserSession = Depends(user_session)):
    value = owned_source(session, source_id)
    return {key: value[key] for key in ("id", "mode", "clock_at", "created_at", "metadata")}


class SimulationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    replay: bool = False
    protocol: Literal["m1_fixed_meal_day", "lightgbm_warmup_48h_v1"] = "m1_fixed_meal_day"


@router.post("/scenario")
def scenario(body: SimulationRequest, session: UserSession = Depends(user_session)):
    return live_scenario(session, replay=body.replay, protocol=body.protocol)


class AdvanceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    minutes: Literal[30, 60, 120]
    expected_clock: datetime


@router.post("/sources/{source_id}/advance")
def advance(source_id: UUID, body: AdvanceRequest, session: UserSession = Depends(user_session)):
    return advance_source(session, source_id, body.minutes, body.expected_clock)
