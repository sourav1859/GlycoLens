from datetime import datetime, timedelta, timezone
import numpy as np
import pytest
from fastapi import HTTPException

from backend.app.services.inference.tabular_context import build_tabular_request, basal_amount
from research.models.adapters.metabonet_tabular import request_features


def fixture(origin=None):
    origin = origin or datetime(2026, 1, 2, 12, tzinfo=timezone.utc)
    start = origin - timedelta(hours=24)
    meal = dict(recorded_at=origin.isoformat(), carbs_g=10.7, protein_g=20, fat_g=30, fiber_g=2)
    cgm = [
        dict(
            recorded_at=(origin - timedelta(minutes=5 * i)).isoformat(),
            glucose_mg_dl=120,
            source="simulation",
        )
        for i in range(287, -1, -1)
    ]
    insulin = [
        dict(
            recorded_at=start.isoformat(),
            event_type="basal",
            units=1.2,
            source_unit="U/h",
            insulin_kind="R",
        ),
        dict(
            recorded_at=origin.isoformat(),
            event_type="bolus",
            units=2,
            source_unit="U",
            insulin_kind="R",
        ),
    ]
    metadata = dict(
        scenario="lightgbm_warmup_48h_v1",
        event_coverage_start=start.isoformat(),
        event_coverage_end=origin.isoformat(),
        meal_events=[
            dict(recorded_at=(origin - timedelta(minutes=10)).isoformat(), carbs_g=25),
            dict(recorded_at=origin.isoformat(), carbs_g=10.7),
        ],
    )
    return origin, meal, cgm, insulin, metadata


def test_units_masks_and_current_meal_exclusion_have_independent_oracles():
    _, meal, cgm, insulin, metadata = fixture()
    request = build_tabular_request(meal, cgm, insulin, metadata)
    x, names = request_features(request, history_hours=24, profile="events")
    assert len(x) == 127
    assert x[names.index("basal_recorded_sum_30m")] == pytest.approx(0.6)
    assert x[names.index("bolus_recorded_sum_30m")] == 2
    assert x[names.index("previous_carbs_recorded_sum_30m")] == 25
    assert x[names.index("meal_carbs_g")] == 10.7
    assert x[names.index("basal_present_fraction_30m")] == 1


def test_partial_basal_overlap_is_integrated_not_relabelled():
    origin, _, _, insulin, _ = fixture()
    insulin[0]["recorded_at"] = (origin - timedelta(minutes=5)).isoformat()
    insulin.append(
        dict(insulin[0], recorded_at=(origin - timedelta(minutes=3)).isoformat(), units=0.6)
    )
    assert basal_amount(insulin, origin - timedelta(minutes=5), origin) == pytest.approx(0.07)


def test_future_data_cannot_affect_features_and_fat_is_not_a_predictor():
    origin, meal, cgm, insulin, metadata = fixture()
    base = build_tabular_request(meal, cgm, insulin, metadata)
    cgm.append(
        dict(cgm[0], recorded_at=(origin + timedelta(minutes=5)).isoformat(), glucose_mg_dl=599)
    )
    insulin.append(
        dict(insulin[1], recorded_at=(origin + timedelta(minutes=5)).isoformat(), units=999)
    )
    altered = build_tabular_request(dict(meal, fat_g=200, protein_g=500), cgm, insulin, metadata)
    assert np.array_equal(
        request_features(base, history_hours=24, profile="events")[0],
        request_features(altered, history_hours=24, profile="events")[0],
        equal_nan=True,
    )


def test_short_history_duplicate_grid_unknown_units_and_missing_coverage_fail_closed():
    _, meal, cgm, insulin, metadata = fixture()
    for rows, events, meta in [
        (cgm[:-1], insulin, metadata),
        (cgm + cgm[:1], insulin, metadata),
        (cgm, [dict(insulin[0], source_unit="unknown"), insulin[1]], metadata),
        (cgm, insulin, {}),
    ]:
        with pytest.raises(HTTPException):
            build_tabular_request(meal, rows, events, meta)


def test_unknown_event_bins_remain_missing_instead_of_confirmed_zero():
    origin, meal, cgm, insulin, metadata = fixture()
    metadata["missing_event_bins"] = {
        "insulin_bolus": [(origin - timedelta(minutes=5 * i)).isoformat() for i in range(6)]
    }
    request = build_tabular_request(meal, cgm, insulin, metadata)
    x, names = request_features(request, history_hours=24, profile="events")
    assert np.isnan(x[names.index("bolus_recorded_sum_30m")])
    assert x[names.index("bolus_present_fraction_30m")] == 0


def test_serving_translator_matches_original_training_window_on_handcrafted_data():
    from research.datasets.metabonet import SCHEMA_VERSION, window_to_example

    origin, meal, cgm, insulin, metadata = fixture()
    carbs = [0.0] * 72
    carbs[-3], carbs[-1] = 25, 10.7
    window = dict(
        schema_version=SCHEMA_VERSION,
        origin_ns=int(origin.timestamp() * 1_000_000_000),
        history=[120] * 288,
        history_record_present=[1] * 288,
        truth=[120] * 24,
        meal_carbs_g=10.7,
        context=dict(
            carbs=carbs, bolus=[0] * 71 + [2], basal=[0.1] * 72, insulin=[0.1] * 71 + [2.1]
        ),
    )
    original = window_to_example(window, with_covariates=True).request
    serving = build_tabular_request(meal, cgm, insulin, metadata)
    a, names = request_features(original, history_hours=24, profile="events")
    b, other = request_features(serving, history_hours=24, profile="events")
    assert names == other
    np.testing.assert_allclose(a, b, atol=1e-12, rtol=0, equal_nan=True)


@pytest.mark.parametrize(
    "at",
    [
        datetime(2026, 1, 2, 12, tzinfo=timezone.utc),
        datetime(2026, 11, 1, 7, 30, tzinfo=timezone.utc),
        datetime(2026, 3, 8, 8, tzinfo=timezone.utc),
    ],
)
def test_unavailable_glucose_is_not_borrowed_and_display_timezone_is_not_a_feature(at):
    from zoneinfo import ZoneInfo

    origin, meal, cgm, insulin, metadata = fixture(at)
    cgm[-1]["available_at"] = (origin + timedelta(minutes=5)).isoformat()
    with pytest.raises(HTTPException):
        build_tabular_request(meal, cgm, insulin, metadata)
    cgm[-1].pop("available_at")
    original = build_tabular_request(meal, cgm, insulin, metadata)
    zone = ZoneInfo("America/New_York")

    def local(value):
        return datetime.fromisoformat(value).astimezone(zone).isoformat()

    meal["recorded_at"] = local(meal["recorded_at"])
    for row in cgm + insulin + metadata["meal_events"]:
        row["recorded_at"] = local(row["recorded_at"])
    metadata["event_coverage_start"] = local(metadata["event_coverage_start"])
    metadata["event_coverage_end"] = local(metadata["event_coverage_end"])
    translated = build_tabular_request(meal, cgm, insulin, metadata)
    np.testing.assert_array_equal(
        request_features(original, history_hours=24, profile="events")[0],
        request_features(translated, history_hours=24, profile="events")[0],
    )
