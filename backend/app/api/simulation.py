from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from typing import Literal
from uuid import UUID
from datetime import datetime

from backend.app.db.client import UserSession, user_session
from backend.app.services.simulation.live import live_scenario, advance_source


router = APIRouter(prefix="/api/v1/simulation", tags=["simulation"])


class SimulationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    replay: bool = False


@router.post("/scenario")
def scenario(body: SimulationRequest, session: UserSession = Depends(user_session)):
    return live_scenario(session, replay=body.replay)


class AdvanceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    minutes: Literal[30, 60, 120]
    expected_clock: datetime


@router.post("/sources/{source_id}/advance")
def advance(source_id: UUID, body: AdvanceRequest, session: UserSession = Depends(user_session)):
    return advance_source(session, source_id, body.minutes, body.expected_clock)
