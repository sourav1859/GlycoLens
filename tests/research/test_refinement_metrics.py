import pytest

from research.evaluation.refinement_metrics import accuracy_metrics, summarize_records


def test_ten_is_inclusive_and_one_large_error_fails_the_whole_curve():
    scores = accuracy_metrics([100, 100, 100, 100], [90, 110, 100, 200])
    assert scores["within_10"] == 0.75
    assert scores["whole_curve_within_10"] == 0
    assert scores["max_absolute_error"] == 100
    assert scores["mae"] == 30
    assert scores["absolute_error_p95"] > 80
    assert accuracy_metrics([100, 100], [90, 110])["whole_curve_within_10"] == 1


@pytest.mark.parametrize("truth,pred", [([], []), ([1], [1, 2]), ([1], [float("nan")])])
def test_invalid_or_nonfinite_predictions_cannot_improve_accuracy(truth, pred):
    with pytest.raises(ValueError):
        accuracy_metrics(truth, pred)


def test_summary_counts_failures_and_weights_people_equally():
    def row(event, subject, error=None, prediction=100):
        return {
            "event_id": event,
            "participant_id": subject,
            "error_type": error,
            "truth": [100.0] * 24,
            "prediction": [float(prediction)] * 24,
            "wall_ms": 1.0,
            "metrics": {},
        }

    rows = [row("1", "a"), row("2", "a"), row("3", "b", prediction=120), row("4", "b", "invalid")]
    result = summarize_records({"a": rows, "b": rows})
    run = result["runs"]["a"]
    assert result["common_success_event_count"] == 3
    assert run["failure_count"] == 1
    assert run["participant_macro"]["within_10"] == 0.5
    assert run["point_metrics"]["within_10"] == pytest.approx(2 / 3)
    assert run["attempted_event_whole_curve_yield"] == 0.5
    assert run["point_metrics"]["max_absolute_error"] == 20
    with pytest.raises(ValueError, match="same requested"):
        summarize_records({"a": rows, "b": rows[:-1]})
