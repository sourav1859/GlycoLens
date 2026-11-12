"""User-token PostgREST calls preserve Supabase row-level security."""

from dataclasses import dataclass

import httpx
from fastapi import Header, HTTPException

from backend.app.core.settings import required_setting


@dataclass(frozen=True)
class UserSession:
    token: str
    user_id: str


def user_session(authorization: str | None = Header(default=None)) -> UserSession:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Sign in to access your application records")
    token = authorization[7:]
    try:
        response = httpx.get(
            required_setting("SUPABASE_URL").rstrip("/") + "/auth/v1/user",
            headers={
                "apikey": required_setting("SUPABASE_ANON_KEY"),
                "Authorization": authorization,
            },
            timeout=10,
        )
        if response.status_code != 200:
            raise HTTPException(401, "Session is invalid or expired")
        active = httpx.post(
            required_setting("SUPABASE_URL").rstrip("/") + "/rest/v1/rpc/current_session_active",
            headers={
                "apikey": required_setting("SUPABASE_ANON_KEY"),
                "Authorization": authorization,
            },
            json={},
            timeout=10,
        )
        if active.status_code != 200:
            raise HTTPException(503, "Session validation is unavailable")
        if active.json() is not True:
            raise HTTPException(401, "Session is invalid or expired")
        return UserSession(token, response.json()["id"])
    except (RuntimeError, httpx.HTTPError, KeyError, ValueError):
        raise HTTPException(503, "Session service is unavailable") from None


def database_call(session: UserSession, path: str, *, method: str = "GET", payload=None):
    try:
        response = httpx.request(
            method,
            required_setting("SUPABASE_URL").rstrip("/") + "/rest/v1/" + path,
            headers={
                "apikey": required_setting("SUPABASE_ANON_KEY"),
                "Authorization": "Bearer " + session.token,
                "Prefer": "return=representation,resolution=merge-duplicates",
            },
            json=payload,
            timeout=20,
        )
        if response.is_error:
            raise HTTPException(
                409 if response.status_code == 409 else 400, "Database request rejected"
            )
        return response.json() if response.content else None
    except (RuntimeError, httpx.HTTPError, ValueError):
        raise HTTPException(503, "Application database is unavailable") from None
