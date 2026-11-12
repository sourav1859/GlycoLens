"""One consumed-only daily/seven-day aggregate for Home and Nutrition."""

from datetime import date, datetime, timedelta
from urllib.parse import quote
from uuid import UUID
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException

from backend.app.db.client import UserSession, database_call, user_session
from backend.app.services.nutrition.windows import day_bounds

router = APIRouter(prefix="/api/v1", tags=["nutrition-summary"])


def nutrition_summary(session, day=None):
    if day and not 1970 <= day.year <= 2100:
        raise HTTPException(422, "Choose a local day between 1970 and 2100")
    prefs = database_call(session, "user_preferences?select=timezone,source_session_id&limit=1")
    if not prefs:
        raise HTTPException(409, "Complete account setup first")
    zone, source_id = prefs[0]["timezone"], prefs[0].get("source_session_id")
    sources = (
        database_call(session, f"source_sessions?id=eq.{UUID(source_id)}&select=*")
        if source_id
        else []
    )
    if not sources:
        return {
            "available": False,
            "timezone": zone,
            "source": None,
            "days": [],
            "goals": [],
            "meals": [],
        }
    source = sources[0]
    selected = (
        day
        or datetime.fromisoformat(source["clock_at"].replace("Z", "+00:00"))
        .astimezone(ZoneInfo(zone))
        .date()
    )
    start, end = day_bounds(selected, zone)
    week_start, _ = day_bounds(selected - timedelta(days=6), zone)
    days = database_call(
        session,
        "rpc/consumed_nutrition_window",
        method="POST",
        payload={
            "p_source": source_id,
            "p_start": week_start.isoformat(),
            "p_end": end.isoformat(),
            "p_timezone": zone,
        },
    )
    meals = database_call(
        session,
        f"meals?source_session_id=eq.{source_id}&state=eq.logged&consumed_at=gte.{quote(start.isoformat(), safe='')}&consumed_at=lt.{quote(end.isoformat(), safe='')}&select=*&order=consumed_at.desc,id.desc&limit=100",
    )
    goals = database_call(
        session,
        f"nutrition_goals?effective_date=lte.{selected.isoformat()}&select=nutrient,target,unit,effective_date&order=effective_date.desc",
    )
    # The newest applicable value wins per nutrient. No default prescriptions.
    active_goals = {row["nutrient"]: row for row in reversed(goals)}
    return {
        "available": True,
        "timezone": zone,
        "source": source,
        "day": selected.isoformat(),
        "days": days,
        "goals": list(active_goals.values()),
        "meals": meals,
        "meals_display_limit": 100,
    }


@router.get("/nutrition")
def nutrition(day: date | None = None, session: UserSession = Depends(user_session)):
    return nutrition_summary(session, day)


@router.get("/home")
def home(day: date | None = None, session: UserSession = Depends(user_session)):
    result = nutrition_summary(session, day)
    source_id = result["source"]["id"] if result["source"] else None
    result["latest_glucose"] = (
        database_call(
            session,
            f"cgm_readings?source_session_id=eq.{source_id}&select=recorded_at,glucose_mg_dl,source&order=recorded_at.desc&limit=1",
        )
        if source_id
        else []
    )
    result["forecasts"] = (
        database_call(
            session,
            f"forecasts?source_session_id=eq.{source_id}&select=id,meal_id,meal_revision,forecast_origin,model_id&order=created_at.desc&limit=1",
        )
        if source_id
        else []
    )
    if result["forecasts"]:
        candidate = result["forecasts"][0]
        meals = (
            database_call(
                session, f"meals?id=eq.{UUID(candidate['meal_id'])}&select=revision,state"
            )
            if candidate.get("meal_id")
            else []
        )
        if (
            not meals
            or meals[0]["revision"] != candidate["meal_revision"]
            or meals[0]["state"] == "cancelled"
        ):
            result["forecasts"] = []
    return result
