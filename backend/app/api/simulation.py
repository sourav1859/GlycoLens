from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.app.db.client import UserSession, user_session
from backend.app.services.simulation.live import live_scenario


router = APIRouter(prefix="/api/v1/simulation", tags=["simulation"])


class SimulationRequest(BaseModel):
    replay: bool = False


@router.post("/scenario")
def scenario(body: SimulationRequest, session: UserSession = Depends(user_session)):
    return live_scenario(session, replay=body.replay)
