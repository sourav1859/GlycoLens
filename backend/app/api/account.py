"""Owner-derived account preferences and server-validated resumable onboarding."""

from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend.app.db.client import UserSession, database_call, user_session
from backend.app.db.trusted import trusted_call

router = APIRouter(prefix="/api/v1/me", tags=["account"])
NOTICE_VERSION = "research-v1"


class PreferenceValues(BaseModel):
    model_config = ConfigDict(extra="forbid")
    timezone: str | None = Field(default=None, max_length=100)
    glucose_unit: Literal["mg/dL", "mmol/L"] | None = None
    source_mode: Literal["personal", "simulation", "replay"] | None = None
    display_name: str | None = Field(default=None, min_length=1, max_length=100)
    food_preferences: list[str] | None = Field(default=None, max_length=20)

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value):
        if value is not None:
            try:
                ZoneInfo(value)
            except (ZoneInfoNotFoundError, ValueError):
                raise ValueError("Choose a valid IANA timezone") from None
        return value

    @field_validator("display_name")
    @classmethod
    def valid_name(cls, value):
        if value is not None and not value.strip():
            raise ValueError("Display name must not be blank")
        return value.strip() if value else value

    @field_validator("food_preferences")
    @classmethod
    def valid_preferences(cls, value):
        if value is not None and any(not item.strip() or len(item) > 80 for item in value):
            raise ValueError("Use at most 20 short preferences")
        return [item.strip() for item in value] if value is not None else value


class PreferenceUpdate(PreferenceValues):
    revision: int = Field(ge=0)


class OnboardingProgress(BaseModel):
    model_config = ConfigDict(extra="forbid")
    revision: int = Field(ge=0)
    step: Literal["preferences", "source", "optional"]
    values: PreferenceValues

    @model_validator(mode="after")
    def required_step_fields(self):
        if self.step == "preferences" and (
            not self.values.timezone or not self.values.glucose_unit
        ):
            raise ValueError("Confirm timezone and glucose unit")
        if self.step == "source" and not self.values.source_mode:
            raise ValueError("Choose an available source")
        return self


class OnboardingComplete(BaseModel):
    model_config = ConfigDict(extra="forbid")
    revision: int = Field(ge=0)
    notice_version: Literal["research-v1"]
    acknowledged: Literal[True]


def read_me(session: UserSession):
    records = database_call(
        session,
        "users?select=id,display_name,user_preferences(*),onboarding_state(*),nutrition_goals(*)&id=eq."
        + session.user_id,
    )
    if not records:
        raise HTTPException(404, "Initialize your account to continue")
    record = records[0]

    def one(value):
        return value[0] if isinstance(value, list) and value else value

    preferences, onboarding = (
        one(record.get("user_preferences")),
        one(record.get("onboarding_state")),
    )
    if not preferences or not onboarding:
        raise HTTPException(503, "Account preferences are unavailable")
    return {
        "user_id": record["id"],
        "display_name": record["display_name"],
        "preferences": preferences,
        "onboarding": onboarding,
        "goals": record.get("nutrition_goals", []),
        "notice_version": NOTICE_VERSION,
    }


@router.get("")
def me(session: UserSession = Depends(user_session)):
    return read_me(session)


@router.post("/bootstrap")
def bootstrap(session: UserSession = Depends(user_session)):
    trusted_call(session, "rpc/app_initialize_user")
    return read_me(session)


@router.patch("/preferences")
def preferences(body: PreferenceUpdate, session: UserSession = Depends(user_session)):
    trusted_call(
        session,
        "rpc/app_update_preferences",
        payload={
            "p_revision": body.revision,
            "p_values": body.model_dump(exclude={"revision"}, exclude_none=True),
        },
    )
    return read_me(session)


@router.patch("/onboarding")
def progress(body: OnboardingProgress, session: UserSession = Depends(user_session)):
    trusted_call(
        session,
        "rpc/app_save_onboarding",
        payload={
            "p_revision": body.revision,
            "p_step": body.step,
            "p_values": body.values.model_dump(exclude_none=True),
        },
    )
    return read_me(session)


@router.post("/onboarding/complete")
def complete(body: OnboardingComplete, session: UserSession = Depends(user_session)):
    trusted_call(
        session,
        "rpc/app_complete_onboarding",
        payload={
            "p_revision": body.revision,
            "p_notice": body.notice_version,
            "p_acknowledged": body.acknowledged,
        },
    )
    return read_me(session)
