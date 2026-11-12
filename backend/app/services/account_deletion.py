"""Hard-delete only the verified password owner; retry nonrecoverable file cleanup.

Passwords and fresh tokens live only in request memory. The database outbox holds
source UUIDs, never an account snapshot or recovery token. Managed backup/log
retention remains a provider/operations release gate.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
import shutil
from threading import Lock
from uuid import UUID

import httpx
from fastapi import HTTPException

from backend.app.core.settings import required_setting
from backend.app.db.client import UserSession
from backend.app.db.trusted import server_headers, trusted_call

# Path lives at repository root (services -> app -> backend -> repository).
SOURCE_ROOT = Path(__file__).resolve().parents[3] / "artifacts/simulation/app/sources"
CLEANUP_LOCK = Lock()
logger = logging.getLogger(__name__)


def auth_call(method, path, *, token=None, admin=False, payload=None):
    headers = server_headers() if admin else {"apikey": required_setting("SUPABASE_ANON_KEY")}
    if token:
        headers["Authorization"] = "Bearer " + token
    return httpx.request(method, required_setting("SUPABASE_URL").rstrip("/") + "/auth/v1/" + path,
                         headers=headers, json=payload, timeout=10)


def delete_account(session: UserSession, password: str, confirmation: str):
    if not 1 <= len(password) <= 128 or confirmation != "DELETE":
        raise HTTPException(422, "Enter your current password and type DELETE to confirm")
    try:
        # Re-fetch canonical Auth identity; never accept an email or owner from the body.
        current = auth_call("GET", "user", token=session.token)
        if current.status_code >= 500:
            raise HTTPException(503, "Reauthentication is unavailable; no deletion was requested")
        if current.status_code != 200 or current.json().get("id") != session.user_id:
            raise HTTPException(401, "Sign in again before deleting your account")
        user = current.json()
        if user.get("is_anonymous") or not user.get("email"):
            raise HTTPException(403, "Deletion requires a password-authenticated account")
        if any(factor.get("status") == "verified" for factor in user.get("factors", [])):
            raise HTTPException(403, "MFA-protected account deletion requires a supported fresh MFA challenge")
        trusted_call(session, "rpc/app_reserve_deletion_attempt")
        fresh = auth_call("POST", "token?grant_type=password", payload={"email": user["email"], "password": password})
        if fresh.status_code == 429:
            raise HTTPException(429, "Too many authentication attempts; try again later")
        if fresh.status_code in {400, 401, 403, 422}:
            raise HTTPException(403, "Current password could not be verified")
        if fresh.status_code != 200:
            raise HTTPException(503, "Reauthentication is unavailable; no deletion was requested")
        proof = fresh.json()
        if not proof.get("access_token"):
            raise HTTPException(403, "Reauthentication did not match your account")
        # Do not leave the temporary verification login behind if deletion fails.
        revoked = auth_call("POST", "logout?scope=local", token=proof["access_token"])
        if revoked.status_code not in {200, 204}:
            raise HTTPException(503, "Reauthentication cleanup failed; no deletion was requested")
        if proof.get("user", {}).get("id") != session.user_id:
            raise HTTPException(403, "Reauthentication did not match your account")
        deleted = auth_call("DELETE", "admin/users/" + str(UUID(session.user_id)), admin=True,
                            payload={"should_soft_delete": False})
        if deleted.status_code not in {200, 204}:
            raise HTTPException(503, "Deletion could not be confirmed; try again after signing in")
    except (RuntimeError, httpx.HTTPError, ValueError, KeyError, TypeError):
        raise HTTPException(503, "Deletion could not be confirmed. If sign-in fails, it may already have completed") from None
    return {"deleted": True, "file_cleanup_pending": not drain_artifact_cleanup()}


def remove_source_artifacts(source_id: str, *, root: Path | None = None):
    """Remove one validated UUID directory, never shared replay/model/research files."""
    root = SOURCE_ROOT if root is None else root
    canonical = str(UUID(source_id))
    target = root / canonical
    # Refuse directory links/junctions, including redirected roots. Check the final
    # resolved absolute path before the single recursive filesystem operation.
    if root.is_symlink() or root.is_junction() or target.is_symlink() or target.is_junction():
        raise ValueError("Redirected artifact directory")
    resolved_root, resolved_target = root.resolve(), target.resolve()
    if resolved_target.parent != resolved_root or resolved_target.name != canonical:
        raise ValueError("Artifact directory escaped its root")
    if target.exists():
        shutil.rmtree(resolved_target)


def cleanup_rpc(payload):
    response = httpx.post(required_setting("SUPABASE_URL").rstrip("/") + "/rest/v1/rpc/app_deletion_artifacts",
                          headers=server_headers(), json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def drain_artifact_cleanup() -> bool:
    if not CLEANUP_LOCK.acquire(blocking=False):
        return False
    complete = True
    try:
        pending = cleanup_rpc({})
        if not isinstance(pending, list):
            return False
        for source in pending:
            try:
                remove_source_artifacts(source)
                cleanup_rpc({"p_complete": source})
            except (OSError, ValueError, RuntimeError, httpx.HTTPError):
                complete = False
        # A full batch can mean more remain; do not claim complete in that case.
        return complete and len(pending) < 100
    except (RuntimeError, ValueError, httpx.HTTPError):
        return False
    finally:
        CLEANUP_LOCK.release()


@asynccontextmanager
async def deletion_cleanup_lifespan(app):
    async def retry():
        while True:
            await asyncio.sleep(30)
            if not await asyncio.to_thread(drain_artifact_cleanup):
                logger.warning("Private source cleanup remains pending; retry scheduled")
    task = None if os.environ.get("GLYCOLENS_DELETION_CLEANUP_WORKER") == "0" else asyncio.create_task(retry())
    try:
        yield
    finally:
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
