"""Server writes cannot trust a client owner or leak the privileged key."""

import httpx
import pytest
from fastapi import HTTPException

from backend.app.db.client import UserSession
from backend.app.db import trusted

OWNER = "10000000-0000-4000-8000-000000000001"


def test_rpc_owner_is_always_derived_from_verified_session(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://synthetic.supabase.co")
    monkeypatch.setenv("SUPABASE_SECRET_KEY", "sb_secret_synthetic")
    captured = {}

    def send(method, url, **kwargs):
        captured.update(kwargs)
        return httpx.Response(200, json=OWNER, request=httpx.Request(method, url))

    monkeypatch.setattr(trusted.httpx, "request", send)
    result = trusted.trusted_call(
        UserSession("synthetic-jwt", OWNER), "rpc/app_initialize_user", payload={"p_user": "forged"}
    )
    assert result == OWNER
    assert captured["json"]["p_user"] == OWNER
    assert "Authorization" not in captured["headers"]


@pytest.mark.parametrize(
    "path,method,payload",
    [
        ("users", "DELETE", {}),
        ("forecasts", "POST", {}),
        ("rpc/save_forecast", "POST", {}),
        ("insulin_events", "POST", [{"user_id": "foreign"}]),
    ],
)
def test_unsupported_or_foreign_writes_fail_before_network(monkeypatch, path, method, payload):
    monkeypatch.setattr(
        trusted.httpx, "request", lambda *a, **k: pytest.fail("Network must not be contacted")
    )
    with pytest.raises(HTTPException) as caught:
        trusted.trusted_call(
            UserSession("synthetic-jwt", OWNER), path, method=method, payload=payload
        )
    assert caught.value.status_code == 403


def test_deleting_simulation_context_is_explicitly_owner_scoped(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://synthetic.supabase.co")
    monkeypatch.setenv("SUPABASE_SECRET_KEY", "sb_secret_synthetic")

    def send(method, url, **kwargs):
        assert url.endswith("&user_id=eq." + OWNER)
        return httpx.Response(200, json=[], request=httpx.Request(method, url))

    monkeypatch.setattr(trusted.httpx, "request", send)
    trusted.trusted_call(
        UserSession("synthetic-jwt", OWNER), "insulin_events?source=eq.simulation", method="DELETE"
    )


@pytest.mark.parametrize(
    "http_status,code,expected",
    [(500, "P0002", 422), (500, "XX000", 503), (409, "23505", 409), (401, "invalid", 503)],
)
def test_database_domain_errors_and_outages_have_distinct_safe_responses(
    monkeypatch, http_status, code, expected
):
    monkeypatch.setenv("SUPABASE_URL", "https://synthetic.supabase.co")
    monkeypatch.setenv("SUPABASE_SECRET_KEY", "sb_secret_synthetic")

    def send(method, url, **kwargs):
        return httpx.Response(
            http_status,
            json={"code": code, "message": "private database context"},
            request=httpx.Request(method, url),
        )

    monkeypatch.setattr(trusted.httpx, "request", send)
    with pytest.raises(HTTPException) as caught:
        trusted.trusted_call(UserSession("synthetic-jwt", OWNER), "rpc/app_initialize_user")
    assert caught.value.status_code == expected
    assert "private database context" not in caught.value.detail
