"""Local aggregate preflight. Test values are restricted to split/provenance metadata.

No model fitting, forecasting or test outcome profiling. Downloaded rows, IDs,
timestamps and free text never appear in stdout or the aggregate output. Unknown
cohort names remain unknown until a release manifest can resolve them.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
TEST_METADATA_COLUMNS = ("id", "source_file", "date", "is_test", "subject_split_across_traintest")
KNOWN_COHORTS = (
    ("CTR3", ("ctr3",)),
    ("ReplaceBG", ("replacebg", "replace_bg")),
    ("SIESTA", ("siesta",)),
    ("AZT1D", ("azt1d", "azt")),
    ("T1D-UOM", ("manchester", "uom")),
    ("HUPA-UCM", ("hupa",)),
    ("BrisT1D", ("brist1d", "bristol", "brist")),
    ("ShanghaiT1DM", ("shanghai",)),
    ("OhioT1DM", ("ohio",)),
    ("T1DEXIP", ("t1dexip",)),
    ("T1DEXI", ("t1dexi",)),
    ("DCLP3", ("dclp3",)),
    ("DCLP5", ("dclp5",)),
    ("DCLP1", ("dclp1",)),
    ("DCLP", ("dclp",)),
    ("IOBP2", ("iobp2",)),
    ("FLAIR", ("flair",)),
    ("PEDAP", ("pedap",)),
    ("Loop", ("loop",)),
    ("OpenAPS", ("openaps",)),
    ("Tidepool", ("tidepool",)),
    ("DiaTrend", ("diatrend",)),
)


def cohort_expression():
    # Fixed allowlist produces cohort names, never participant-derived strings.
    value = "lower(coalesce(source_file,'') || ' ' || coalesce(id,''))"
    clauses = ["CASE"]
    for name, patterns in KNOWN_COHORTS:
        predicate = " OR ".join(f"contains({value},'{p}')" for p in patterns)
        clauses.append(f"WHEN {predicate} THEN '{name}'")
    return " ".join(clauses) + " ELSE 'UNRESOLVED' END"


def connection(temporary_directory):
    temporary_directory.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(
        config={
            "threads": 2,
            "memory_limit": "2GB",
            "temp_directory": str(temporary_directory),
            "max_temp_directory_size": "20GB",
            "autoinstall_known_extensions": False,
            "autoload_known_extensions": False,
        }
    )


def file_metadata(con, path):
    with path.open("rb") as source:
        if source.read(4) != b"PAR1":
            raise ValueError("invalid Parquet file signature")
        source.seek(-4, 2)
        if source.read(4) != b"PAR1":
            raise ValueError("incomplete Parquet footer")
        source.seek(0)
        sha = hashlib.file_digest(source, "sha256").hexdigest()
    created, rows, groups = con.execute(
        "SELECT created_by,num_rows,num_row_groups FROM parquet_file_metadata(?)", [str(path)]
    ).fetchone()
    schema = [
        {"name": r[0], "type": r[1]}
        for r in con.execute("DESCRIBE SELECT * FROM read_parquet(?)", [str(path)]).fetchall()
    ]
    keys = [
        bytes(r[0]).decode("utf-8", errors="replace")
        for r in con.execute("SELECT key FROM parquet_kv_metadata(?)", [str(path)]).fetchall()
    ]
    return {
        "bytes": path.stat().st_size,
        "sha256": sha,
        "rows": rows,
        "row_groups": groups,
        "created_by": created,
        "schema": schema,
        "metadata_keys": keys,
        "release_version": "not established; schema writer version is not dataset version",
    }


def metadata_view(con, path, name, columns):
    # Explicit column projection is also used for test. Never SELECT * from its values.
    projection = ",".join('"' + column + '"' for column in columns)
    con.read_parquet(str(path)).project(projection).create_view(name, replace=True)


def dictionaries(cursor):
    names = [d[0] for d in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def training_profile(con):
    expressions = [
        "count(*) AS rows",
        "count(DISTINCT id) AS participants",
        "count(DISTINCT source_file) AS source_files",
        "count(*) FILTER(WHERE id IS NULL) AS missing_id",
        "count(*) FILTER(WHERE date IS NULL) AS missing_timestamp",
        "count(*) FILTER(WHERE is_test IS TRUE) AS unexpected_test_flag",
        "count(*) FILTER(WHERE subject_split_across_traintest IS TRUE) AS shared_subject_flag_rows",
    ]
    for name in ("CGM", "carbs", "bolus", "basal", "insulin"):
        expressions += [
            f'count(*) FILTER(WHERE "{name}" IS NULL OR NOT isfinite("{name}")) AS "{name}_missing_or_nonfinite"',
            f'count(*) FILTER(WHERE isfinite("{name}") AND "{name}" > 0) AS "{name}_positive"',
            f'count(*) FILTER(WHERE "{name}" = 0) AS "{name}_zero"',
            f'count(*) FILTER(WHERE isfinite("{name}") AND "{name}" < 0) AS "{name}_negative"',
        ]
    return dictionaries(
        con.execute(
            "SELECT "
            + ",".join(expressions)
            + ", "
            + cohort_expression()
            + " AS cohort FROM train GROUP BY cohort ORDER BY cohort"
        )
    )


def split_metadata(con):
    cohort = cohort_expression()
    for name in ("train", "test_metadata"):
        con.execute(f"""CREATE TEMP TABLE {name}_subjects AS SELECT {cohort} AS cohort,id,
            min(date) AS first_at,max(date) AS last_at,count(*) AS rows,
            bool_or(subject_split_across_traintest) AS marked_shared
            FROM {name} GROUP BY cohort,id""")
    cohorts = dictionaries(
        con.execute("""SELECT cohort,count(*) AS participants,sum(rows) AS rows
        FROM test_metadata_subjects GROUP BY cohort ORDER BY cohort""")
    )
    totals = dictionaries(
        con.execute("""SELECT
        (SELECT count(*) FROM train_subjects) AS training_cohort_subject_pairs,
        (SELECT count(*) FROM test_metadata_subjects) AS test_cohort_subject_pairs,
        count(*) AS shared_cohort_subject_pairs,
        count(*) FILTER(WHERE tr.marked_shared IS TRUE AND te.marked_shared IS TRUE) AS both_marked_shared,
        count(*) FILTER(WHERE tr.last_at>=te.first_at) AS shared_with_overlapping_time_ranges,
        count(*) FILTER(WHERE te.first_at-tr.last_at<INTERVAL '24 hours') AS shared_without_24h_forward_gap
        FROM train_subjects tr JOIN test_metadata_subjects te USING(cohort,id)""")
    )[0]
    flags = dictionaries(
        con.execute("""SELECT count(*) FILTER(WHERE is_test IS NOT TRUE) AS unexpected_train_or_null_flag,
        count(*) FILTER(WHERE id IS NULL) AS missing_id,
        count(*) FILTER(WHERE date IS NULL) AS missing_timestamp FROM test_metadata""")
    )[0]
    return {
        "test_cohort_counts_metadata_only": cohorts,
        "overlap": totals,
        "test_flags": flags,
        "test_projected_columns": list(TEST_METADATA_COLUMNS),
        "test_outcome_columns_read": [],
    }


def grid_and_duplicates(con):
    # Only keys, no CGM, are needed. Spillable GROUP BY avoids materializing all rows in Python.
    return dictionaries(
        con.execute("""SELECT
        coalesce(sum(n-1),0) AS excess_duplicate_keys,
        count(*) FILTER(WHERE n>1) AS repeated_subject_timestamp_keys,
        count(*) FILTER(WHERE epoch_ns(date)%300000000000!=0) AS off_five_minute_grid_keys
        FROM (SELECT source_file,id,date,count(*) AS n FROM train GROUP BY source_file,id,date)""")
    )[0]


def metadata_diagnostics(con):
    # Source and subject/date keys only; this never touches test outcomes.
    gaps = dictionaries(
        con.execute("""SELECT
        count(*) FILTER(WHERE te.first_at<tr.last_at) AS reversed_or_interleaved_ranges,
        count(*) FILTER(WHERE te.first_at-tr.last_at BETWEEN INTERVAL '0 seconds' AND INTERVAL '5 minutes') AS zero_to_five_minute_gap,
        count(*) FILTER(WHERE te.first_at-tr.last_at>INTERVAL '5 minutes' AND te.first_at-tr.last_at<INTERVAL '2 hours') AS five_minute_to_two_hour_gap,
        count(*) FILTER(WHERE te.first_at-tr.last_at>=INTERVAL '2 hours' AND te.first_at-tr.last_at<INTERVAL '24 hours') AS two_to_twentyfour_hour_gap,
        count(*) FILTER(WHERE te.first_at-tr.last_at>=INTERVAL '24 hours') AS at_least_twentyfour_hour_gap
        FROM train_subjects tr JOIN test_metadata_subjects te USING(cohort,id)""")
    )[0]
    collisions = con.execute("""SELECT count(*) FROM
        (SELECT id FROM train_subjects GROUP BY id HAVING count(DISTINCT cohort)>1)""").fetchone()[
        0
    ]
    siesta = dictionaries(
        con.execute("""SELECT count(*) FILTER(WHERE gap IS NOT NULL) AS within_subject_intervals,
        count(*) FILTER(WHERE gap=INTERVAL '5 minutes') AS exactly_five_minute_intervals,
        count(*) FILTER(WHERE gap<INTERVAL '0 seconds') AS negative_intervals,
        count(DISTINCT offset_ns) AS distinct_wallclock_offsets
        FROM (SELECT date-lag(date) OVER(PARTITION BY id ORDER BY date) AS gap,
              epoch_ns(date)%300000000000 AS offset_ns FROM train WHERE
              contains(lower(coalesce(source_file,'') || ' ' || coalesce(id,'')),'siesta'))""")
    )[0]
    exact = con.execute("""WITH overlapping AS (
        SELECT tr.id,tr.cohort FROM train_subjects tr JOIN test_metadata_subjects te USING(cohort,id)
        WHERE tr.last_at>=te.first_at),
        tr_keys AS (SELECT tr.source_file,tr.id,tr.date FROM train tr SEMI JOIN overlapping o ON tr.id=o.id),
        te_keys AS (SELECT te.source_file,te.id,te.date FROM test_metadata te SEMI JOIN overlapping o ON te.id=o.id)
        SELECT count(*) FROM tr_keys tr JOIN te_keys te USING(source_file,id,date)""").fetchone()[0]
    return {
        "shared_time_gap_bins": gaps,
        "training_ids_in_multiple_named_cohorts": collisions,
        "siesta_timestamp_cadence": siesta,
        "identical_subject_source_timestamp_keys_across_files": exact,
    }


def audit(directory, output, *, duplicate_audit=True):
    started = time.perf_counter()
    with connection(output / "scratch") as con:
        files = {
            name: file_metadata(con, directory / name) for name in ("train.parquet", "test.parquet")
        }
        train_columns = [r["name"] for r in files["train.parquet"]["schema"]]
        test_columns = [r["name"] for r in files["test.parquet"]["schema"]]
        required = set(TEST_METADATA_COLUMNS) | {"CGM", "carbs", "bolus", "basal", "insulin"}
        if not required <= set(train_columns) or not set(TEST_METADATA_COLUMNS) <= set(
            test_columns
        ):
            raise ValueError("required schema fields are missing")
        # Train projection omits free text, demographics and device identifiers.
        metadata_view(con, directory / "train.parquet", "train", sorted(required))
        metadata_view(con, directory / "test.parquet", "test_metadata", TEST_METADATA_COLUMNS)
        profiles = training_profile(con)
        print(
            json.dumps({"stage": "training_profile_complete", "cohorts": len(profiles)}), flush=True
        )
        metadata = split_metadata(con)
        print(json.dumps({"stage": "split_metadata_complete", **metadata["overlap"]}), flush=True)
        diagnostics = metadata_diagnostics(con)
        duplicates = grid_and_duplicates(con) if duplicate_audit else {"executed": False}
    return {
        "audit_version": "metabonet_preflight_v1",
        "reader": "duckdb " + duckdb.__version__,
        "files": files,
        "training_cohort_profiles": profiles,
        "split_metadata": metadata,
        "training_key_audit": duplicates,
        "schema_equal": files["train.parquet"]["schema"] == files["test.parquet"]["schema"],
        "metadata_diagnostics": diagnostics,
        "cohort_mapping": "allowlisted name matching against source_file and id; verify release manifest",
        "training_exclusion_cohorts": ["AZT1D", "T1D-UOM", "UNRESOLVED"],
        "terms_review_cohorts": [
            "OhioT1DM",
            "T1DEXI",
            "T1DEXIP",
            "OpenAPS",
            "Tidepool",
            "DiaTrend",
        ],
        "training_started": False,
        "test_predictions_computed": False,
        "elapsed_seconds": time.perf_counter() - started,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=ROOT / "data/raw/metabonet")
    parser.add_argument(
        "--output", type=Path, default=ROOT / "artifacts/evaluation-results/metabonet-audit"
    )
    parser.add_argument("--skip-duplicate-audit", action="store_true")
    parser.add_argument("--release-version", default="unknown")
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / "artifacts"):
        raise ValueError("audit outputs must remain under ignored artifacts/")
    output.mkdir(parents=True, exist_ok=True)
    result = audit(args.directory, output, duplicate_audit=not args.skip_duplicate_audit)
    result["reported_release"] = {
        "version": args.release_version,
        "evidence": "user-provided portal release-notes screenshot; not embedded in files",
    }
    (output / "audit.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "stage": "audit_complete",
                "seconds": result["elapsed_seconds"],
                "test_outcome_columns_read": [],
                "training_started": False,
            }
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
