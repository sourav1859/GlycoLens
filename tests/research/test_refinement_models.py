from dataclasses import replace
from datetime import timedelta

import numpy as np
import pytest

from research.datasets.t1d_uom import ParticipantData
from research.evaluation.refinement_data import enriched_request, calibration_assignments
from research.models.adapters.tabular import request_features, TabularForecastAdapter
from research.models.adapters.converters import (
    meal_window_to_forecast_example,
    ContextConfiguration,
)
from tests.research.test_m2_protocol import shifted_window
from research.evaluation.protocol import temporal_manifest
from dataclasses import asdict


def test_future_meals_never_enter_features_and_basal_is_not_invented():
    window = shifted_window(0)
    earlier = replace(window.meal, timestamp=window.meal.timestamp - timedelta(hours=1))
    future = replace(
        window.meal, timestamp=window.meal.timestamp + timedelta(minutes=5), carbs_g=999
    )

    def request(meals):
        return enriched_request(window, ParticipantData("synthetic", (), meals, ()))

    before = request((earlier, window.meal))
    after = request((earlier, window.meal, future))
    np.testing.assert_array_equal(request_features(before), request_features(after))
    assert not any("basal" in s.name for s in after.past_covariates)


def test_held_out_targets_cannot_change_tabular_features():
    window = shifted_window(0)
    participant = ParticipantData("synthetic", (), (window.meal,), ())
    changed = replace(
        window, target_cgm=tuple(replace(p, glucose_mmol_l=99) for p in window.target_cgm)
    )
    np.testing.assert_array_equal(
        request_features(enriched_request(window, participant)),
        request_features(enriched_request(changed, participant)),
    )


def test_training_calibration_are_disjoint_and_targets_purged():
    manifest = [asdict(e) for e in temporal_manifest(tuple(shifted_window(i) for i in range(30)))]
    assigned = calibration_assignments(manifest)
    train = [e for e in manifest if assigned[e["event_id"]] == "train"]
    cal = [e for e in manifest if assigned[e["event_id"]] == "calibration"]
    assert train and cal
    assert max(e["target_end"] for e in train) <= min(e["meal_at"] for e in cal)
    assert any(s == "diagnostic" for s in assigned.values())


def test_small_model_fit_predict_and_separate_calibration_preserve_point_forecast():
    requests = [
        meal_window_to_forecast_example(
            shifted_window(i), context=ContextConfiguration.CGM_ONLY
        ).request
        for i in range(10)
    ]
    targets = [tuple(r.target_history[-1].value + 5 for _ in range(24)) for r in requests]
    model = TabularForecastAdapter()
    model.fit(requests[:5], targets[:5])
    prediction = model.predict(requests[-1])
    assert prediction.median == pytest.approx(targets[-1])
    model.calibrate(requests[5:], targets[5:])
    assert model.predict(requests[-1]).median == prediction.median
    assert dict(model.predict(requests[-1]).metadata)["deterministic"] == "false"
