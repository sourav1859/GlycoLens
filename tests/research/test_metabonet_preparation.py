from datetime import timedelta
from dataclasses import replace

import pytest
import numpy as np

pytest.importorskip("duckdb")
import duckdb  # noqa: E402
import json  # noqa: E402

from research.datasets.metabonet import (  # noqa: E402
    STEP_NS,
    SubjectSeries,
    build_window,
    window_to_example,
    candidate_indices,
    trajectory_fingerprints,
    WindowRejected,
)
from research.pipelines.prepare_metabonet import (  # noqa: E402
    PreparationPolicy,
    subject_catalog,
    choose_subjects,
    build_preparation,
    iter_prepared_windows,
    verify_preparation,
)


def synthetic_series(offset=0):
    times = np.arange(700, dtype=np.int64) * STEP_NS + offset
    values = np.zeros((700, 5), dtype=float)
    values[:, 0] = 100 + np.arange(700) * 0.1 + 20 * np.sin(np.arange(700) / 20)
    values[:, 1] = np.nan
    values[350, 1] = 35.5
    values[:, 2] = np.nan
    values[349, 2] = 2
    values[:, 3] = 0.1
    values[:, 4] = 0.1
    return SubjectSeries("synthetic", "Loop", times, values)


def test_units_masks_delay_and_immutable_forecast_boundary():
    series = synthetic_series(offset=37_000_000_000)
    window = build_window(series, 350, hours=6, delay_minutes=5)
    example = window_to_example(window, with_covariates=True)
    assert example.request.target_history[-1].value == pytest.approx(series.values[351, 0])
    assert len(example.request.target_history) == 72 and len(example.target.points) == 24
    assert example.target.points[0].timestamp - example.request.context_end == timedelta(minutes=5)
    assert example.request.context_end.second == 37
    channels = {s.name: s for s in example.request.past_covariates}
    assert channels["insulin_bolus"].points[-1].value == 2  # IU, no rate conversion
    assert any(p.value == 0 for p in channels["insulin_bolus_record_present"].points)
    assert example.request.known_covariates[0].points[0].value == 35.5
    changed = series.values.copy()
    changed[352:, 0] += 100
    changed[352:, 2] = 999
    altered = window_to_example(
        build_window(replace(series, values=changed), 350, hours=6, delay_minutes=5),
        with_covariates=True,
    )
    assert altered.request == example.request
    assert altered.target != example.target


def test_only_causal_short_history_fill_and_observed_targets():
    series = synthetic_series()
    values = series.values.copy()
    values[351, 0] = np.nan
    filled = build_window(replace(series, values=values), 350, hours=6, delay_minutes=5)
    assert filled["history"][-1] == series.values[350, 0]
    assert filled["history_record_present"][-1] == 0
    values[352, 0] = np.nan
    with pytest.raises(WindowRejected, match="incomplete_target"):
        build_window(replace(series, values=values), 350, hours=6, delay_minutes=5)
    values = series.values.copy()
    values[349:352, 0] = np.nan
    with pytest.raises(WindowRejected, match="incomplete_history"):
        build_window(replace(series, values=values), 350, hours=6, delay_minutes=5)


def test_followup_and_clustered_meals_rejected_without_amount_deduplication():
    series = synthetic_series()
    values = series.values.copy()
    values[360, 1] = 20
    with pytest.raises(WindowRejected, match="follow_up_meal"):
        build_window(replace(series, values=values), 350, hours=6, delay_minutes=5)
    values = series.values.copy()
    values[349, 1] = 35.5
    with pytest.raises(WindowRejected, match="clustered_meal"):
        build_window(replace(series, values=values), 350, hours=6, delay_minutes=5)


def test_sampling_identity_does_not_depend_on_future_glucose():
    series = synthetic_series()
    altered = replace(series, values=series.values.copy())
    altered.values[351:, 0] += 100
    assert candidate_indices(series, limit=10) == candidate_indices(altered, limit=10)
    a = build_window(series, 350, hours=2, delay_minutes=0)
    b = build_window(series, 350, hours=12, delay_minutes=5)
    assert a["event_id"] == b["event_id"]
    assert list(trajectory_fingerprints(series))
    assert list(trajectory_fingerprints(series)) == list(
        trajectory_fingerprints(replace(series, sid="other"))
    )


def test_source_qualified_splits_are_deterministic_and_holdouts_are_metadata_only():
    train = [
        {"source": source, "id": str(i), "rows": 100, "first_ns": 0, "last_ns": 100 * STEP_NS}
        for source in ["Loop", "ReplaceBG"]
        for i in range(20)
    ]
    train += [
        {"source": "AZT1D", "id": "x", "rows": 10, "first_ns": 0, "last_ns": 10 * STEP_NS},
        {"source": "PEDAP", "id": "p", "rows": 10, "first_ns": 0, "last_ns": 10 * STEP_NS},
    ]
    test = [
        {"source": "Loop", "id": "0", "rows": 10, "first_ns": 0, "last_ns": 10 * STEP_NS},
        {"source": "Loop", "id": "new", "rows": 10, "first_ns": 0, "last_ns": 10 * STEP_NS},
    ]
    policy = PreparationPolicy(
        train_per_source=3, validation_per_source=2, calibration_per_source=2
    )
    catalog = choose_subjects(train, test, policy)
    assert catalog == choose_subjects(list(reversed(train)), test, policy)
    selected = catalog["development"]
    assert len({s["sid"] for s in selected}) == len(selected) == 14
    assert {s["source"] for s in selected} == {"Loop", "ReplaceBG"}
    assert len(catalog["primary_test"]) == 1 and catalog["primary_test"][0]["id"] == "new"
    assert {s["source"] for s in catalog["source_test"]} == {"PEDAP"}


def test_real_streaming_preparation_freezes_dev_windows_without_test_value_columns(
    tmp_path, monkeypatch
):
    directory = tmp_path / "input"
    directory.mkdir()
    with duckdb.connect() as con:
        con.execute("""CREATE TABLE training AS SELECT source_file,cast(person AS VARCHAR) AS id,
            TIMESTAMP '2020-01-01'+sample*INTERVAL '5 minutes' AS date,
            100+person*.13+sample*.1+20*sin(sample/20.0)+source_offset AS CGM,
            CASE WHEN sample=350 THEN 35.5 ELSE NULL END AS carbs,
            CASE WHEN sample=349 THEN 2.0 ELSE NULL END AS bolus,
            .1 AS basal,.1 AS insulin,FALSE AS is_test,FALSE AS subject_split_across_traintest
            FROM (VALUES ('Loop',0),('ReplaceBG',5)) s(source_file,source_offset),
            range(20) p(person),range(700) r(sample)""")
        con.execute("""INSERT INTO training SELECT 'PEDAP','heldout',TIMESTAMP '2020-01-01',
            999999,35.5,2.0,.1,.1,FALSE,FALSE""")
        con.execute("COPY training TO ? (FORMAT PARQUET)", [str(directory / "train.parquet")])
        # Deliberately no CGM/carbs/insulin columns: any accidental test-value access fails.
        con.execute("""CREATE TABLE testing AS SELECT 'Loop' AS source_file,'new' AS id,
            TIMESTAMP '2020-01-01' AS date,TRUE AS is_test,FALSE AS subject_split_across_traintest""")
        con.execute("COPY testing TO ? (FORMAT PARQUET)", [str(directory / "test.parquet")])
        catalog = subject_catalog(con, directory / "test.parquet", test=True)
        assert len(catalog) == 1
    output = tmp_path / "prepared"
    policy = PreparationPolicy(
        train_per_source=1, validation_per_source=1, calibration_per_source=1
    )
    summary = build_preparation(directory, output, policy)
    assert summary["model_training_performed"] is False
    assert summary["test_outcome_columns_read"] == []
    assert summary["duplicate_candidate_subject_count"] == 0
    windows = list(iter_prepared_windows(output, split="train", hours=6, delay=5))
    assert len(windows) == 2
    assert all(w["meal_carbs_g"] == 35.5 for w in windows)
    assert verify_preparation(output)["subject_splits_disjoint"]
    assert "999999" not in json.dumps(windows)
    with pytest.raises(ValueError, match="development-only"):
        list(iter_prepared_windows(output, split="primary_test"))
    with pytest.raises(ValueError, match="already exists"):
        build_preparation(directory, output, policy)
    quality = output / "subject-quality.json"
    original_quality = quality.read_bytes()
    quality.write_text("[]")
    with pytest.raises(ValueError, match="artifact changed"):
        list(iter_prepared_windows(output, split="train"))
    quality.write_bytes(original_quality)
    protocol = output / "frozen-protocol.json"
    original_protocol = protocol.read_bytes()
    protocol.write_text("{}")
    with pytest.raises(ValueError, match="protocol changed"):
        list(iter_prepared_windows(output, split="train"))
    protocol.write_bytes(original_protocol)
    (output / "summary.json").write_text("{}")
    with pytest.raises(ValueError, match="artifact changed"):
        verify_preparation(output)
    failed_output = tmp_path / "failed"

    def reject_integrity(directory):
        raise ValueError("injected integrity failure")

    monkeypatch.setattr("research.pipelines.prepare_metabonet.verify_preparation", reject_integrity)
    with pytest.raises(ValueError, match="injected integrity"):
        build_preparation(directory, failed_output, policy)
    assert not failed_output.exists()
    assert list(tmp_path.glob(".failed-building-*"))
