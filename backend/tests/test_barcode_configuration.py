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
