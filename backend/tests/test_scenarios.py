import pytest
from backend.app.services.inference.scenarios import scaled_meal, actual_metrics


def test_portion_scales_only_grounded_nutrition():
    base = dict(
        id="frozen",
        recorded_at="2026-01-01T12:00:00Z",
        carbs_g=40,
        protein_g=20,
        fat_g=10,
        fiber_g=4,
        calories=330,
    )
    half = scaled_meal(base, 0.5)
    assert [half[f] for f in ("carbs_g", "protein_g", "fat_g", "fiber_g", "calories")] == [
        20,
        10,
        5,
        2,
        165,
    ]
    assert half["recorded_at"] == base["recorded_at"] and base["carbs_g"] == 40
    with pytest.raises(ValueError):
        scaled_meal(base, 0)


def test_independently_known_error_and_inclusive_interval():
    points = [dict(minute=m, q10_mg_dl=90, q50_mg_dl=100, q90_mg_dl=110) for m in range(5, 121, 5)]
    values = [110] * 12 + [80] * 12
    result = actual_metrics(points, values)
    assert result["mae_mg_dl"] == 15 and result["interval_coverage"] == 0.5
    with pytest.raises(ValueError):
        actual_metrics(points, values[:-1])
