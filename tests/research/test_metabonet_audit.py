from datetime import datetime, timedelta
import json

import pytest

duckdb = pytest.importorskip("duckdb")

from research.pipelines.audit_metabonet import audit, TEST_METADATA_COLUMNS  # noqa: E402
# The optional reader must be checked before importing its pipeline.


def make_files(path):
    con = duckdb.connect()
    con.execute("""CREATE TABLE rows(id VARCHAR,source_file VARCHAR,date TIMESTAMP,CGM DOUBLE,
        carbs DOUBLE,bolus DOUBLE,basal DOUBLE,insulin DOUBLE,is_test BOOLEAN,
        subject_split_across_traintest BOOLEAN)""")
    at = datetime(2020, 1, 1)
    con.executemany(
        "INSERT INTO rows VALUES(?,?,?,?,?,?,?,?,?,?)",
        [
            ("synthetic1", "AZT1D.csv", at, 100, None, 1, 0.1, 1.1, False, False),
            ("synthetic2", "FLAIR.csv", at, 110, 20, 2, 0.1, 2.1, False, True),
            ("synthetic2", "FLAIR.csv", at, 110, 20, 2, 0.1, 2.1, False, True),
            ("synthetic3", "unknown.csv", at, 90, None, None, None, None, False, False),
            ("synthetic2", "CTR3.csv", at, 120, 10, 1, 0.1, 1.1, False, False),
            (
                "synthetic4",
                "SIESTA.csv",
                at + timedelta(seconds=37),
                100,
                None,
                0,
                0.1,
                0.1,
                False,
                False,
            ),
            (
                "synthetic4",
                "SIESTA.csv",
                at + timedelta(minutes=5, seconds=37),
                100,
                None,
                0,
                0.1,
                0.1,
                False,
                False,
            ),
        ],
    )
    con.execute("COPY rows TO ? (FORMAT PARQUET)", [str(path / "train.parquet")])
    con.execute("DELETE FROM rows")
    con.execute(
        "INSERT INTO rows VALUES(?,?,?,?,?,?,?,?,?,?)",
        [
            "synthetic2",
            "FLAIR.csv",
            at + timedelta(days=2),
            999999,
            999999,
            999999,
            999999,
            999999,
            True,
            True,
        ],
    )
    con.execute("COPY rows TO ? (FORMAT PARQUET)", [str(path / "test.parquet")])
    con.close()


def test_audit_projects_only_test_metadata_and_keeps_unknown_sources_unresolved(tmp_path):
    make_files(tmp_path)
    result = audit(tmp_path, tmp_path / "output")
    assert result["files"]["train.parquet"]["rows"] == 7
    profiles = {p["cohort"]: p for p in result["training_cohort_profiles"]}
    assert profiles["AZT1D"]["rows"] == 1
    assert profiles["UNRESOLVED"]["rows"] == 1
    assert result["split_metadata"]["test_projected_columns"] == list(TEST_METADATA_COLUMNS)
    assert result["split_metadata"]["test_outcome_columns_read"] == []
    assert result["split_metadata"]["overlap"]["shared_cohort_subject_pairs"] == 1
    assert result["split_metadata"]["overlap"]["shared_without_24h_forward_gap"] == 0
    assert result["training_key_audit"]["excess_duplicate_keys"] == 1
    assert result["metadata_diagnostics"]["training_ids_in_multiple_named_cohorts"] == 1
    assert (
        result["metadata_diagnostics"]["identical_subject_source_timestamp_keys_across_files"] == 0
    )
    assert (
        result["metadata_diagnostics"]["siesta_timestamp_cadence"]["exactly_five_minute_intervals"]
        == 1
    )
    assert result["training_key_audit"]["off_five_minute_grid_keys"] == 2
    assert "999999" not in json.dumps(result)
    assert "synthetic2" not in json.dumps(result)
    assert result["training_started"] is False


def test_truncated_download_is_rejected(tmp_path):
    (tmp_path / "train.parquet").write_bytes(b"PAR1truncated")
    with pytest.raises(ValueError, match="footer"):
        audit(tmp_path, tmp_path / "output")
