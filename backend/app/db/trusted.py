"""Narrow server writes after user_session has independently verified identity.

Ordinary reads continue to use the caller JWT and RLS. This module never accepts
a client owner field; each RPC owner is overwritten with the verified identity.
"""

import os
from uuid import UUID

from fastapi import HTTPException
import httpx

from backend.app.core.settings import required_setting
from backend.app.db.client import UserSession, database_call

RPCS = {
    "app_reserve_deletion_attempt",
    "app_initialize_user",
    "app_save_meal",
    "app_save_forecast",
    "app_update_preferences",
    "app_save_onboarding",
    "app_complete_onboarding",
    "app_commit_meal",
    "app_store_source_context",
    "app_commit_forecast",
    "app_read_notifications",
    "app_reserve_recipe_request",
    "app_save_scenario",
    "app_advance_source",
    "app_store_actuals",
}


def server_headers() -> dict[str, str]:
    modern = os.environ.get("SUPABASE_SECRET_KEY", "").strip()
    key = modern or required_setting("SUPABASE_SERVICE_ROLE_KEY")
    headers = {"apikey": key, "Prefer": "return=representation,resolution=merge-duplicates"}
    if not modern:
        headers["Authorization"] = "Bearer " + key
    return headers


def trusted_call(session: UserSession, path: str, *, method: str = "POST", payload=None):
    try:
        owner = str(UUID(session.user_id))
    except ValueError:
        raise HTTPException(401, "A verified session is required") from None
    if path.startswith("rpc/") and path[4:] in RPCS and method == "POST":
        payload = {**(payload or {}), "p_user": owner}
    elif (
        path in {"cgm_readings?on_conflict=user_id,recorded_at,source", "insulin_events"}
        and method == "POST"
    ):
        rows = payload if isinstance(payload, list) else [payload]
        if not rows or any(
            not isinstance(row, dict) or row.get("user_id") != owner for row in rows
        ):
            raise HTTPException(403, "Record owner must match the verified session")
    elif path == "insulin_events?source=eq.simulation" and method == "DELETE":
        path += "&user_id=eq." + owner
    elif path == "meal_outcomes?on_conflict=meal_id" and method == "POST":
        try:
            meal = str(UUID(payload["meal_id"]))
        except (ValueError, KeyError, TypeError):
            raise HTTPException(422, "A valid owned meal is required") from None
        if not database_call(session, f"meals?id=eq.{meal}&select=id"):
            raise HTTPException(404, "Meal not found")
    else:
        raise HTTPException(403, "This server write operation is unavailable")
    try:
        response = httpx.request(
            method,
            required_setting("SUPABASE_URL").rstrip("/") + "/rest/v1/" + path,
            headers=server_headers(),
            json=payload,
            timeout=20,
        )
        if response.is_error:
            code = (
                response.json().get("code")
                if response.headers.get("content-type", "").startswith("application/json")
                else None
            )
            # SELECT INTO STRICT reports unknown food as P0002/HTTP 500.
            # Classify only known domain errors; real outages remain unavailable.
            domain_error = code in {"P0002", "23514", "22023", "22P02", "22003"}
            if response.status_code == 429 or code == "PT429":
                raise HTTPException(429, "The request limit has been reached; retry later")
            if response.status_code in {401, 403} or (
                response.status_code >= 500 and not domain_error
            ):
                raise HTTPException(503, "Application storage is unavailable")
            raise HTTPException(
                409 if response.status_code == 409 or code == "23505" else 422,
                "The write was rejected; review the record and retry",
            )
        return response.json() if response.content else None
    except (RuntimeError, httpx.HTTPError, ValueError):
        raise HTTPException(503, "Application storage is unavailable") from None
