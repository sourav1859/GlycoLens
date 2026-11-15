from unittest.mock import patch
import pytest
from fastapi import HTTPException
from backend.app.db.client import UserSession
from backend.app.services.nutrition.providers import resolve_barcode


@pytest.mark.parametrize("agent", ["", "GlycoLens/0.1", "GlycoLens/0.1 (https://example.invalid)"])
def test_uncached_live_lookup_needs_explicit_project_contact(monkeypatch, agent):
    monkeypatch.setenv("OPEN_FOOD_FACTS_USER_AGENT", agent)
    with (
        patch("backend.app.services.nutrition.providers.database_call", return_value=[]),
        patch("backend.app.services.nutrition.providers.provider_request") as provider,
    ):
        with pytest.raises(HTTPException) as error:
            resolve_barcode("3017620422003", UserSession("synthetic", "owner"))
        assert error.value.status_code == 503
        provider.assert_not_called()


def test_off_uncached_reads_are_bounded_and_expire(monkeypatch):
    import backend.app.services.nutrition.providers as source
    from collections import deque

    monkeypatch.setattr(source, "_OFF_READS", deque())
    monkeypatch.setattr(source, "monotonic", lambda: 100)
    for _ in range(15):
        source.admit_off_read()
    with pytest.raises(HTTPException) as error:
        source.admit_off_read()
    assert error.value.status_code == 429
    monkeypatch.setattr(source, "monotonic", lambda: 160)
    source.admit_off_read()
    assert len(source._OFF_READS) == 1


@pytest.mark.parametrize("code", ["123456789", "3017620422004", "not-a-code"])
def test_invalid_gtin_never_calls_cache_or_provider(code):
    with (
        patch("backend.app.services.nutrition.providers.database_call") as cache,
        patch("backend.app.services.nutrition.providers.provider_request") as provider,
    ):
        with pytest.raises(HTTPException) as error:
            resolve_barcode(code, UserSession("synthetic", "owner"))
        assert error.value.status_code == 422
        cache.assert_not_called()
        provider.assert_not_called()
