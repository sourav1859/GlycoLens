import pytest
from research.evaluation.statistics import paired_participant_interval


def test_pairing_is_by_event_and_clusters_by_participant():
    left = [
        {
            "event_id": str(i),
            "participant_id": "a" if i < 4 else "b",
            "error_type": None,
            "metrics": {"mae": 12 if i < 4 else 8},
        }
        for i in range(5)
    ]
    right = [{**row, "metrics": {"mae": 10}} for row in reversed(left)]
    result = paired_participant_interval(left, right, samples=100)
    assert result["participant_count"] == 2
    assert result["macro_mae_difference"] == 0  # Equal subjects, not five independent CGM windows.
    assert result == paired_participant_interval(left, right, samples=100)
    with pytest.raises(ValueError):
        paired_participant_interval([], [])
