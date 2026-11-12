"""GL-P00-006: the API/client contract cannot change without a reviewed snapshot."""

from copy import deepcopy

from scripts.quality.check_api_contract import current_contract, contract_matches


def test_current_api_matches_reviewed_snapshot():
    assert contract_matches(current_contract())


def test_response_and_route_drift_fail_the_contract():
    changed = deepcopy(current_contract())
    changed["paths"].pop("/api/v1/forecasts/demo")
    assert not contract_matches(changed)
    changed = deepcopy(current_contract())
    changed["components"]["schemas"]["ForecastResponse"]["required"].remove("history")
    assert not contract_matches(changed)
