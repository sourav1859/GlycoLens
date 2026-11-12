"""Synthetic deletion boundary tests; real cleanup is checked in the cloud harness."""

from uuid import uuid4

import httpx
import pytest
from fastapi import HTTPException

from backend.app.db.client import UserSession
from backend.app.services import account_deletion as deletion


OWNER = "10000000-0000-4000-8000-000000000001"
SESSION = UserSession("synthetic-existing-token", OWNER)


def configure(monkeypatch, *, login_owner=OWNER, password_status=200, delete_status=200):
    monkeypatch.setenv("SUPABASE_URL", "https://synthetic.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "synthetic-public")
    monkeypatch.setenv("SUPABASE_SECRET_KEY", "sb_secret_synthetic")
    calls = []

    def send(method, url, **kwargs):
        calls.append((method, url, kwargs))
        if url.endswith("/auth/v1/user"):
            body, status = {"id": OWNER, "email": "synthetic@example.invalid"}, 200
        elif "grant_type=password" in url:
            assert kwargs["json"]["email"] == "synthetic@example.invalid"
            body, status = {"user": {"id": login_owner}, "access_token": "fresh-token"}, password_status
        elif "/logout" in url:
            body, status = {}, 204
        elif "/admin/users/" in url:
            assert url.endswith("/" + OWNER)
            assert kwargs["json"] == {"should_soft_delete": False}
            body, status = {}, delete_status
        else:
            pytest.fail("Unexpected endpoint")
        return httpx.Response(status, json=body, request=httpx.Request(method, url))

    monkeypatch.setattr(deletion.httpx, "request", send)
    monkeypatch.setattr(deletion, "trusted_call", lambda *a, **k: None)
    monkeypatch.setattr(deletion, "drain_artifact_cleanup", lambda: True)
    return calls


@pytest.mark.parametrize("password,confirmation", [("", "DELETE"), ("x" * 129, "DELETE"), ("valid", "delete"), ("valid", "")])
def test_no_destructive_call_without_explicit_confirmation(monkeypatch, password, confirmation):
    monkeypatch.setattr(deletion.httpx, "request", lambda *a, **k: pytest.fail("No network expected"))
    with pytest.raises(HTTPException) as caught:
        deletion.delete_account(SESSION, password, confirmation)
    assert caught.value.status_code == 422


@pytest.mark.parametrize("status,owner,expected", [(400, OWNER, 403), (429, OWNER, 429), (503, OWNER, 503), (200, str(uuid4()), 403)])
def test_password_failure_or_different_identity_never_deletes(monkeypatch, status, owner, expected):
    calls = configure(monkeypatch, login_owner=owner, password_status=status)
    with pytest.raises(HTTPException) as caught:
        deletion.delete_account(SESSION, "synthetic-password", "DELETE")
    assert caught.value.status_code == expected
    assert not any("/admin/users/" in url for _, url, _ in calls)


def test_hard_delete_is_bound_to_verified_owner_and_reauth_session_is_revoked(monkeypatch):
    calls = configure(monkeypatch)
    assert deletion.delete_account(SESSION, "synthetic-password", "DELETE") == {"deleted": True, "file_cleanup_pending": False}
    paths = [url for _, url, _ in calls]
    assert paths[-2].endswith("/logout?scope=local") and paths[-1].endswith("/admin/users/" + OWNER)
    assert calls[-2][2]["headers"]["Authorization"] == "Bearer fresh-token"


def test_failed_auth_delete_is_not_reported_as_success(monkeypatch):
    configure(monkeypatch, delete_status=500)
    with pytest.raises(HTTPException) as caught:
        deletion.delete_account(SESSION, "synthetic-password", "DELETE")
    assert caught.value.status_code == 503
    assert "password" not in caught.value.detail.lower()


def test_completed_auth_delete_with_pending_files_is_honest(monkeypatch):
    configure(monkeypatch)
    monkeypatch.setattr(deletion, "drain_artifact_cleanup", lambda: False)
    assert deletion.delete_account(SESSION, "synthetic-password", "DELETE")["file_cleanup_pending"] is True


def test_filesystem_cleanup_only_removes_exact_source_and_is_repeatable(tmp_path):
    source, other = str(uuid4()), str(uuid4())
    for name in (source, other):
        target = tmp_path / name
        target.mkdir()
        (target / "context.json").write_text("synthetic")
    shared = tmp_path.parent / "scenario.json"
    shared.write_text("shared synthetic replay")
    deletion.remove_source_artifacts(source, root=tmp_path)
    deletion.remove_source_artifacts(source, root=tmp_path)
    assert not (tmp_path / source).exists()
    assert (tmp_path / other / "context.json").exists() and shared.exists()
    with pytest.raises(ValueError):
        deletion.remove_source_artifacts("../outside", root=tmp_path)


def test_cleanup_refuses_redirected_directory(tmp_path):
    source = str(uuid4())
    outside = tmp_path.parent / "outside"
    outside.mkdir(exist_ok=True)
    try:
        (tmp_path / source).symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Symlink creation unavailable on this Windows account")
    with pytest.raises(ValueError):
        deletion.remove_source_artifacts(source, root=tmp_path)
    assert outside.exists()


def test_failed_cleanup_keeps_job_for_retry(monkeypatch):
    source = str(uuid4())
    calls = []
    monkeypatch.setattr(deletion, "cleanup_rpc", lambda body: calls.append(body) or [source])
    monkeypatch.setattr(deletion, "remove_source_artifacts", lambda *a, **k: (_ for _ in ()).throw(OSError("synthetic")))
    assert deletion.drain_artifact_cleanup() is False
    assert calls == [{}]


def test_successful_cleanup_acknowledges_only_after_removal(monkeypatch):
    source, events = str(uuid4()), []
    monkeypatch.setattr(deletion, "cleanup_rpc", lambda body: events.append(body) or ([source] if not body else []))
    monkeypatch.setattr(deletion, "remove_source_artifacts", lambda sid: events.append(sid))
    assert deletion.drain_artifact_cleanup() is True
    assert events == [{}, source, {"p_complete": source}]


def test_attempt_limit_prevents_password_and_delete_requests(monkeypatch):
    calls = configure(monkeypatch)
    def limited(*args, **kwargs):
        raise HTTPException(429, "Try later")
    monkeypatch.setattr(deletion, "trusted_call", limited)
    with pytest.raises(HTTPException) as caught:
        deletion.delete_account(SESSION, "synthetic-password", "DELETE")
    assert caught.value.status_code == 429
    assert len(calls) == 1


def test_api_rejects_foreign_owner_and_redacts_invalid_secret_input():
    from fastapi.testclient import TestClient
    from backend.app.main import app
    from backend.app.db.client import user_session
    app.dependency_overrides[user_session] = lambda: SESSION
    try:
        with TestClient(app) as api:
            for body in ({"password": "synthetic-private", "confirmation": "DELETE", "user_id": str(uuid4())},
                         {"password": {"secret": "synthetic-private"}, "confirmation": "DELETE"}):
                response = api.request("DELETE", "/api/v1/me", json=body)
                assert response.status_code == 422
                assert "synthetic-private" not in response.text
                assert response.headers["cache-control"] == "private, no-store"
    finally:
        app.dependency_overrides.clear()


def test_mfa_account_cannot_be_deleted_with_password_alone(monkeypatch):
    configure(monkeypatch)
    def send(*args, **kwargs):
        return httpx.Response(200, json={"id": OWNER, "email": "synthetic@example.invalid", "factors": [{"status": "verified"}]})
    monkeypatch.setattr(deletion.httpx, "request", send)
    monkeypatch.setattr(deletion, "trusted_call", lambda *a, **k: pytest.fail("No deletion attempt expected"))
    with pytest.raises(HTTPException) as caught:
        deletion.delete_account(SESSION, "synthetic-password", "DELETE")
    assert caught.value.status_code == 403


def test_cleanup_worker_retries_failed_batch_until_shutdown(monkeypatch):
    import asyncio
    monkeypatch.delenv("GLYCOLENS_DELETION_CLEANUP_WORKER", raising=False)
    async def exercise():
        finished, waiting = asyncio.Event(), asyncio.Event()
        results = []
        def cleanup():
            results.append(len(results) > 0)
            return results[-1]
        real_sleep = asyncio.sleep
        async def sleep(seconds):
            assert seconds == 30
            if len(results) >= 2:
                finished.set()
                await waiting.wait()
            await real_sleep(0)
        monkeypatch.setattr(deletion, "drain_artifact_cleanup", cleanup)
        monkeypatch.setattr(deletion.asyncio, "sleep", sleep)
        async with deletion.deletion_cleanup_lifespan(None):
            await asyncio.wait_for(finished.wait(), timeout=2)
        assert results == [False, True]
    asyncio.run(exercise())
