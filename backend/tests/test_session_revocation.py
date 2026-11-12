"""A cryptographically valid JWT must still lose API access after logout."""

import httpx
import pytest
from fastapi import HTTPException

from backend.app.db import client


@pytest.mark.parametrize("active,expected", [(False, 401), (True, None)])
def test_verified_user_also_requires_active_managed_session(monkeypatch, active, expected):
    monkeypatch.setenv("SUPABASE_URL", "https://synthetic.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "synthetic-public")
    monkeypatch.setattr(
        client.httpx, "get", lambda *a, **k: httpx.Response(200, json={"id": "synthetic-owner"})
    )
    monkeypatch.setattr(client.httpx, "post", lambda *a, **k: httpx.Response(200, json=active))
    if expected:
        with pytest.raises(HTTPException) as caught:
            client.user_session("Bearer synthetic-verified-token")
        assert caught.value.status_code == expected
    else:
        assert client.user_session("Bearer synthetic-verified-token").user_id == "synthetic-owner"
