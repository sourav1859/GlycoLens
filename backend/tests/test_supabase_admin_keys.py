"""Provider writes support modern server keys without treating them as JWTs."""

import httpx
import pytest
from fastapi import HTTPException

from backend.app.services.nutrition import providers


@pytest.mark.parametrize(
    ("secret", "legacy", "expected_key", "expected_bearer"),
    [
        ("sb_secret_synthetic", "legacy-synthetic", "sb_secret_synthetic", None),
        (None, "legacy-synthetic", "legacy-synthetic", "Bearer legacy-synthetic"),
        ("  ", "legacy-synthetic", "legacy-synthetic", "Bearer legacy-synthetic"),
    ],
)
def test_provider_write_key_compatibility(
    monkeypatch, secret, legacy, expected_key, expected_bearer
):
    monkeypatch.setenv("SUPABASE_URL", "https://synthetic.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", legacy)
    if secret is None:
        monkeypatch.delenv("SUPABASE_SECRET_KEY", raising=False)
    else:
        monkeypatch.setenv("SUPABASE_SECRET_KEY", secret)
    food = {"name": "Synthetic food", "source": "usda", "source_food_id": "123"}
    captured = {}

    def post(url, **kwargs):
        captured.update(kwargs)
        return httpx.Response(200, request=httpx.Request("POST", url), json=[food])

    monkeypatch.setattr(providers.httpx, "post", post)
    assert providers.store_provider_food(food) == food
    assert captured["headers"]["apikey"] == expected_key
    assert captured["headers"].get("Authorization") == expected_bearer


def test_missing_server_keys_prevents_network_request(monkeypatch):
    monkeypatch.delenv("SUPABASE_SECRET_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)

    def post(*args, **kwargs):
        pytest.fail("Missing credentials must fail before making a network request")

    monkeypatch.setattr(providers.httpx, "post", post)
    with pytest.raises(HTTPException) as caught:
        providers.store_provider_food({"name": "Synthetic food"})
    assert caught.value.status_code == 503
    assert "SUPABASE" not in caught.value.detail
