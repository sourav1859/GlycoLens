"""Bounded own-account export. Never includes Auth credentials or provider secrets."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from backend.app.db.client import UserSession, database_call, user_session
from pydantic import BaseModel, ConfigDict, SecretStr
from backend.app.services.account_deletion import delete_account

router = APIRouter(prefix="/api/v1/me", tags=["privacy"])


class DeleteAccountRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    password: SecretStr
    confirmation: SecretStr


@router.delete("")
def delete_own_account(body: DeleteAccountRequest, session: UserSession = Depends(user_session)):
    return delete_account(session, body.password.get_secret_value(), body.confirmation.get_secret_value())


EXPORT_TABLES = (
    "portion_scenarios",
    "users",
    "user_preferences",
    "onboarding_state",
    "notice_acknowledgements",
    "nutrition_goals",
    "source_sessions",
    "meals",
    "meal_items",
    "meal_revisions",
    "cgm_readings",
    "insulin_events",
    "activity_events",
    "forecasts",
    "forecast_points",
    "meal_outcomes",
    "notifications",
)


@router.get("/export")
def export_account(session: UserSession = Depends(user_session)):
    records = {}
    total = 0
    for table in EXPORT_TABLES:
        rows = []
        for offset in range(0, 6000, 1000):
            order = {
                "user_preferences": "user_id",
                "onboarding_state": "user_id",
                "notice_acknowledgements": "user_id,notice_version",
                "meal_revisions": "meal_id,revision",
                "meal_items": "meal_id,food_id",
                "meal_outcomes": "meal_id",
                "forecast_points": "forecast_id,forecast_at",
            }.get(table, "id")
            page = database_call(
                session, f"{table}?select=*&order={order}&limit=1000&offset={offset}"
            )
            total += len(page)
            if total > 5000:
                raise HTTPException(
                    409,
                    "Export exceeds the development synchronous limit; no partial download was produced",
                )
            rows.extend(page)
            if len(page) < 1000:
                break
        records[table] = rows
    # Child snapshots include food facts and frozen forecast points; no global catalog dump.
    return JSONResponse(
        {
            "schema_version": "1.0",
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "user_id": session.user_id,
            "records": records,
        },
        headers={
            "Content-Disposition": 'attachment; filename="glycolens-export.json"',
            "Cache-Control": "private, no-store",
        },
    )
