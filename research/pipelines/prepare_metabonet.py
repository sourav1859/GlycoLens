"""Phase 2 development preparation and frozen metadata-only test reservation.

No forecasts or model fitting. Raw test values are never projected. The completed
output is immutable; failures retain a separate ignored building directory.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
import time
import zipfile
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import numpy as np

from research.datasets.metabonet import (
    SubjectSeries,
    WindowRejected,
    build_window,
    candidate_indices,
    trajectory_fingerprints,
    window_to_example,
)

ROOT = Path(__file__).resolve().parents[2]
VERSION = "metabonet_phase2_v1"
TEST_COLUMNS = ("source_file", "id", "date", "is_test", "subject_split_across_traintest")


@dataclass(frozen=True)
class PreparationPolicy:
    train_per_source: int = 100
    validation_per_source: int = 25
    calibration_per_source: int = 25
    candidates_per_subject: int = 100
    histories: tuple = (2, 6, 12, 24)
    delays: tuple = (5, 0)
    development_sources: tuple = ("Loop", "ReplaceBG")
    source_test: str = "PEDAP"
    seed: int = 20261016

    def __post_init__(self):
        if (
            min(
                self.train_per_source,
                self.validation_per_source,
                self.calibration_per_source,
                self.candidates_per_subject,
            )
            <= 0
        ):
            raise ValueError("preparation caps must be positive")
        if self.development_sources != ("Loop", "ReplaceBG") or self.source_test != "PEDAP":
            raise ValueError("source changes require a new versioned protocol")


def hash_file(path):
    with Path(path).open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def write_json(path, value):
    path.write_text(
        json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )


def log(stage, **values):
    print(json.dumps({"stage": stage, **values}), flush=True)


def sid_for(source, identity):
    return hashlib.sha256(f"{VERSION}|{source}|{identity}".encode()).hexdigest()[:32]


def subject_catalog(con, path, *, test=False):
    # Same explicit projection for both: no test glucose/event values, not even stats.
    con.read_parquet(str(path)).project(",".join(TEST_COLUMNS)).create_view(
        "catalog_input", replace=True
    )
    flags = con.execute(
        "SELECT count(*) FILTER(WHERE is_test IS DISTINCT FROM ?) FROM catalog_input", [test]
    ).fetchone()[0]
    if flags:
        raise ValueError("publisher split flags disagree with file role")
    rows = con.execute("""SELECT source_file,id,count(*),min(epoch_ns(date)),max(epoch_ns(date))
        FROM catalog_input GROUP BY source_file,id ORDER BY source_file,id""").fetchall()
    if any(
        source is None or identity is None or first is None
        for source, identity, _, first, _ in rows
    ):
        raise ValueError("missing subject provenance or timestamps")
    return [
        {"source": s, "id": i, "rows": n, "first_ns": a, "last_ns": b} for s, i, n, a, b in rows
    ]


def choose_subjects(train, test, policy):
    train = sorted(train, key=lambda s: (s["source"], s["id"]))
    test = sorted(test, key=lambda s: (s["source"], s["id"]))
    keys = {(s["source"], s["id"]) for s in train}
    development = []
    all_assignments = []
    for source in policy.development_sources:
        population = [
            {**s, "sid": sid_for(s["source"], s["id"])} for s in train if s["source"] == source
        ]
        population.sort(key=lambda s: hashlib.sha256(f"{policy.seed}|{s['sid']}".encode()).digest())
        train_end = int(len(population) * 0.7)
        validation_end = train_end + int(len(population) * 0.15)
        for split, group, cap in [
            ("train", population[:train_end], policy.train_per_source),
            ("validation", population[train_end:validation_end], policy.validation_per_source),
            ("calibration", population[validation_end:], policy.calibration_per_source),
        ]:
            for position, s in enumerate(group):
                entry = {**s, "split": split, "selected": position < cap}
                all_assignments.append(entry)
                if position < cap:
                    development.append(entry)

    def annotate(s, role, file_roles):
        return {**s, "sid": sid_for(s["source"], s["id"]), "split": role, "file_roles": file_roles}

    primary = [
        annotate(s, "primary_test", ["test"])
        for s in test
        if s["source"] in policy.development_sources and (s["source"], s["id"]) not in keys
    ]
    holdout = {}
    for role, population in [("train", train), ("test", test)]:
        for s in population:
            if s["source"] != policy.source_test:
                continue
            key = (s["source"], s["id"])
            if key not in holdout:
                holdout[key] = annotate(s, "source_test", [role])
            else:
                holdout[key]["file_roles"].append(role)
    if {s["sid"] for s in primary} & {sid_for(s["source"], s["id"]) for s in train}:
        raise ValueError("primary test appears in publisher training")
    return {
        "development": development,
        "all_development_assignments": all_assignments,
        "primary_test": primary,
        "source_test": [holdout[k] for k in sorted(holdout)],
        "publisher_training_sids": sorted(sid_for(s["source"], s["id"]) for s in train),
        "excluded_training_source_counts": dict(
            Counter(
                s["source"]
                for s in train
                if s["source"] not in policy.development_sources
                and s["source"] != policy.source_test
            )
        ),
    }


def project_development(con, train_path, selection, destination):
    con.read_parquet(str(train_path)).create_view("development_input", replace=True)
    con.execute("CREATE TEMP TABLE selected(sid VARCHAR,source_file VARCHAR,id VARCHAR)")
    con.executemany(
        "INSERT INTO selected VALUES(?,?,?)", [(s["sid"], s["source"], s["id"]) for s in selection]
    )
    con.execute(
        """COPY (SELECT s.sid,epoch_ns(r.date) AS at_ns,r.CGM,r.carbs,r.bolus,r.basal,r.insulin
        FROM development_input r JOIN selected s USING(source_file,id)
        ORDER BY s.sid,at_ns) TO ? (FORMAT PARQUET,COMPRESSION ZSTD,ROW_GROUP_SIZE 65536)""",
        [str(destination)],
    )


def projected_subjects(path):
    # Single file and one reader thread preserve the explicitly written order.
    # Assert it at runtime; never silently build a subject from interleaved chunks.
    with duckdb.connect(
        config={"threads": 1, "memory_limit": "512MB", "preserve_insertion_order": True}
    ) as con:
        cursor = con.execute(
            "SELECT sid,at_ns,CGM,carbs,bolus,basal,insulin FROM read_parquet(?)", [str(path)]
        )

        def rows():
            previous = None
            while batch := cursor.fetchmany(32768):
                for row in batch:
                    key = (row[0], row[1])
                    if previous is not None and key < previous:
                        raise ValueError("projected stream is not sorted")
                    previous = key
                    yield row

        for sid, group in itertools.groupby(rows(), key=lambda r: r[0]):
            records = list(group)
            times = np.array([r[1] for r in records], dtype=np.int64)
            values = np.array([r[2:] for r in records], dtype=np.float64)
            yield sid, times, values


def summarize_catalog(catalog):
    counts = Counter((s["source"], s["split"]) for s in catalog["development"])
    return {
        "selected_development": [
            {"source": source, "split": split, "subject_count": n}
            for (source, split), n in sorted(counts.items())
        ],
        "primary_test_subject_count": len(catalog["primary_test"]),
        "source_test_subject_count": len(catalog["source_test"]),
        "excluded_training_source_counts": catalog["excluded_training_source_counts"],
    }


def build_preparation(directory, output, policy, *, dictionary_evidence=None):
    if output.exists():
        raise ValueError("preparation output already exists; verify the frozen build instead")
    started = time.perf_counter()
    parent = output.parent.resolve()
    parent.mkdir(parents=True, exist_ok=True)
    working = parent / (
        f".{output.name}-building-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    )
    working.mkdir()
    (working / "windows").mkdir()
    inputs = {
        name: {"sha256": hash_file(directory / name), "bytes": (directory / name).stat().st_size}
        for name in ("train.parquet", "test.parquet")
    }
    with duckdb.connect(
        config={
            "threads": 2,
            "memory_limit": "2GB",
            "temp_directory": str(working / "scratch"),
            "max_temp_directory_size": "20GB",
            "autoinstall_known_extensions": False,
            "autoload_known_extensions": False,
        }
    ) as con:
        train = subject_catalog(con, directory / "train.parquet")
        test = subject_catalog(con, directory / "test.parquet", test=True)
        catalog = choose_subjects(train, test, policy)
        if not catalog["development"] or not catalog["primary_test"] or not catalog["source_test"]:
            raise ValueError("required development or reserved metadata cohorts are empty")
        write_json(working / "subject-manifest.json", catalog)
        write_json(working / "proposed-policy.json", asdict(policy))
        log("metadata_reserved", **summarize_catalog(catalog))
        project_development(
            con,
            directory / "train.parquet",
            catalog["development"],
            working / "development-projection.parquet",
        )
    log("development_projected", bytes=(working / "development-projection.parquet").stat().st_size)
    selected = {s["sid"]: s for s in catalog["development"]}
    owners = {}
    quarantined = set()
    subject_results = []
    for number, (sid, times, values) in enumerate(
        projected_subjects(working / "development-projection.parquet"), 1
    ):
        metadata = selected[sid]
        row = {
            "sid": sid,
            "source": metadata["source"],
            "split": metadata["split"],
            "rows": len(times),
            "eligible": {},
            "rejected": {},
            "status": "ready",
        }
        try:
            series = SubjectSeries(sid, metadata["source"], times, values)
        except ValueError:
            row["status"] = "invalid_subject_timestamps"
            subject_results.append(row)
            continue
        for fingerprint in trajectory_fingerprints(series):
            previous = owners.setdefault(fingerprint, sid)
            if previous != sid:
                quarantined.update((previous, sid))
        candidates = candidate_indices(series, limit=policy.candidates_per_subject)
        row["positive_carb_rows"] = len(series.meal_indices)
        row["sampled_candidate_count"] = len(candidates)
        rejects = defaultdict(Counter)
        with gzip.GzipFile(
            filename=str(working / "windows" / f"{sid}.jsonl.gz"), mode="wb", mtime=0
        ) as target:
            for index in candidates:
                for delay in policy.delays:
                    for hours in policy.histories:
                        variant = f"{hours}h_delay{delay}"
                        try:
                            window = build_window(series, index, hours=hours, delay_minutes=delay)
                        except WindowRejected as error:
                            rejects[variant][error.reason] += 1
                            continue
                        if window["origin_ns"] + 24 * 300_000_000_000 > metadata["last_ns"]:
                            raise ValueError("target crossed publisher training range")
                        # Exercise the public immutable contract before serializing any example.
                        window_to_example(window, with_covariates=True)
                        window["split"] = metadata["split"]
                        target.write(
                            (
                                json.dumps(window, separators=(",", ":"), allow_nan=False) + "\n"
                            ).encode()
                        )
                        row["eligible"][variant] = row["eligible"].get(variant, 0) + 1
        row["rejected"] = {k: dict(v) for k, v in rejects.items()}
        subject_results.append(row)
        if number % 10 == 0:
            log("subjects_prepared", completed=number, total=len(selected))
    if {s["sid"] for s in subject_results} != set(selected):
        raise ValueError("projected subject coverage does not match selection")
    for row in subject_results:
        if row["sid"] in quarantined:
            row["status"] = "exact_trajectory_candidate_quarantine"
    write_json(working / "subject-quality.json", subject_results)
    counts = defaultdict(lambda: Counter())
    subjects = defaultdict(lambda: Counter())
    rejections = defaultdict(Counter)
    for row in subject_results:
        if row["status"] != "ready":
            continue
        key = row["split"] + ":" + row["source"]
        for variant, n in row["eligible"].items():
            counts[key][variant] += n
            subjects[key][variant] += int(n > 0)
        for variant, reasons in row["rejected"].items():
            rejections[variant].update(reasons)
    summary = {
        **summarize_catalog(catalog),
        "eligible_events": {k: dict(v) for k, v in counts.items()},
        "eligible_subjects": {k: dict(v) for k, v in subjects.items()},
        "rejection_counts": {k: dict(v) for k, v in rejections.items()},
        "quality_status_counts": dict(Counter(s["status"] for s in subject_results)),
        "duplicate_candidate_subject_count": len(quarantined),
        "distinct_fingerprints_checked": len(owners),
        "positive_carb_rows_in_selected_subjects": sum(
            s.get("positive_carb_rows", 0) for s in subject_results
        ),
        "sampled_candidate_count": sum(
            s.get("sampled_candidate_count", 0) for s in subject_results
        ),
        "test_outcome_columns_read": [],
        "test_eligible_event_count": None,
        "test_eligibility_status": "deferred until model-selection freeze; metadata reservation only",
        "model_training_performed": False,
        "elapsed_seconds": time.perf_counter() - started,
    }
    for split in ("train", "validation", "calibration"):
        if (
            sum(
                v.get("6h_delay5", 0)
                for k, v in summary["eligible_events"].items()
                if k.startswith(split + ":")
            )
            == 0
        ):
            raise ValueError("a required primary development split has no eligible events")
    write_json(working / "summary.json", summary)
    source_files = [
        ROOT / "research/datasets/metabonet.py",
        Path(__file__),
        ROOT / "research/models/adapters/base.py",
    ]
    with zipfile.ZipFile(
        working / "preparation-source.zip", "w", compression=zipfile.ZIP_DEFLATED
    ) as snapshot:
        for path in source_files:
            snapshot.write(path, path.relative_to(ROOT).as_posix())
    protocol = {
        "version": VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "policy": asdict(policy),
        "inputs": inputs,
        "dictionary_evidence": dictionary_evidence,
        "source_hashes": {p.relative_to(ROOT).as_posix(): hash_file(p) for p in source_files},
        "primary_carb_delay_minutes": 5,
        "sensitivity_delay_minutes": 0,
        "horizon_minutes": 120,
        "frequency_minutes": 5,
        "history_forward_fill_max_minutes": 10,
        "minimum_history_record_fraction": 0.9,
        "target_imputation": "none",
        "subject_split": "source-stratified stable-hash ordering, 70/15/15 by subject",
        "duplicate_rule": "quarantine all selected IDs sharing varied exact six-hour CGM fingerprints",
        "future_test_rules": "primary only publisher-test IDs absent from all publisher training; PEDAP source reserved",
        "selection_metric": "participant-average trajectory MAE; tie higher within +/-10",
        "proposed_improvement_gate": "at least10% lower MAE than matched persistence; within10 not lower; pooled p95 not higher",
        "clipping": False,
        "permitted_future_work": "frozen histories, direct small models, frozen Chronos residuals; no automatic app promotion",
        "test_values_projected": False,
        "limitations": [
            "Retrospectively isolated logged meals; unknown unlogged intake.",
            "Five-minute carb availability is a conservative assumption; actual logging latency unknown.",
            "Record-present means finite in the harmonized file, not verified raw sensor/event availability.",
            "Cross-ID fingerprint checks are exact and partial; independent people are not guaranteed.",
            "PEDAP is a pediatric source shift; report separately.",
            "Reserved test eligibility is deliberately not measured before model selection.",
        ],
    }
    protocol["artifact_hashes"] = {
        p.relative_to(working).as_posix(): hash_file(p)
        for p in sorted(working.rglob("*"))
        if p.is_file() and "scratch" not in p.parts
    }
    write_json(working / "frozen-protocol.json", protocol)
    (working / "frozen-protocol.sha256").write_text(
        hash_file(working / "frozen-protocol.json") + "\n", encoding="ascii"
    )
    # Both resolved targets are verified inside the explicitly selected output parent.
    if not working.resolve().is_relative_to(parent) or not output.resolve().is_relative_to(parent):
        raise ValueError("prepared output rename escapes artifact parent")
    verify_preparation(working)
    working.rename(output)
    verify_preparation(output)
    return summary


def read_frozen_protocol(directory):
    if (
        hash_file(directory / "frozen-protocol.json")
        != (directory / "frozen-protocol.sha256").read_text().strip()
    ):
        raise ValueError("frozen protocol changed")
    return json.loads((directory / "frozen-protocol.json").read_text())


def verify_preparation(directory):
    protocol = read_frozen_protocol(directory)
    with zipfile.ZipFile(directory / "preparation-source.zip") as snapshot:
        for name, expected in protocol["source_hashes"].items():
            if hashlib.sha256(snapshot.read(name)).hexdigest() != expected:
                raise ValueError("execution source snapshot changed")
    for name, expected in protocol["artifact_hashes"].items():
        path = (directory / name).resolve()
        if not path.is_relative_to(directory.resolve()) or hash_file(path) != expected:
            raise ValueError("frozen preparation artifact changed")
    catalog = json.loads((directory / "subject-manifest.json").read_text())
    development = [s["sid"] for s in catalog["development"]]
    if len(development) != len(set(development)):
        raise ValueError("development subject assigned to multiple splits")
    if set(s["sid"] for s in catalog["primary_test"]) & set(catalog["publisher_training_sids"]):
        raise ValueError("primary test has a publisher-training identity")
    if set(development) & set(s["sid"] for s in catalog["source_test"]):
        raise ValueError("source test leaks into development")
    return {
        "artifact_hashes_valid": True,
        "subject_splits_disjoint": True,
        "test_values_read": False,
    }


def iter_prepared_windows(directory, *, split, hours=6, delay=5):
    if split not in ("train", "validation", "calibration"):
        raise ValueError(
            "prepared windows are development-only; test requires a later frozen-selection gate"
        )
    protocol = read_frozen_protocol(directory)
    if (
        hash_file(directory / "subject-quality.json")
        != protocol["artifact_hashes"]["subject-quality.json"]
    ):
        raise ValueError("frozen preparation artifact changed")
    quality = json.loads((directory / "subject-quality.json").read_text())
    for subject in quality:
        if subject["split"] != split or subject["status"] != "ready":
            continue
        relative = "windows/" + subject["sid"] + ".jsonl.gz"
        path = directory / relative
        if hash_file(path) != protocol["artifact_hashes"][relative]:
            raise ValueError("prepared window file changed")
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            for line in stream:
                window = json.loads(line)
                if window["history_hours"] == hours and window["carb_delay_minutes"] == delay:
                    yield window


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=ROOT / "data/raw/metabonet")
    parser.add_argument(
        "--output", type=Path, default=ROOT / "artifacts/evaluation-results/metabonet-phase2-v1"
    )
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / "artifacts"):
        raise ValueError("health artifacts must remain under ignored artifacts/")
    if args.verify_only:
        log("verification", **verify_preparation(output))
        return 0
    if output.exists():
        raise ValueError("frozen output already exists; use --verify-only")
    audit = json.loads(
        (ROOT / "artifacts/evaluation-results/metabonet-audit/audit.json").read_text()
    )
    dictionary = json.loads(
        (ROOT / "artifacts/evaluation-results/metabonet-audit/dictionary-review.json").read_text()
    )
    for name in ("train.parquet", "test.parquet"):
        if hash_file(args.directory / name) != audit["files"][name]["sha256"]:
            raise ValueError(
                "download differs from audited input; audit the new release before preparation"
            )
    if hash_file(args.directory / "MetaboNet.html") != dictionary["dictionary_file_sha256"]:
        raise ValueError("saved dictionary differs from reviewed evidence")
    summary = build_preparation(
        args.directory,
        output,
        PreparationPolicy(),
        dictionary_evidence={
            "html_sha256": dictionary["dictionary_file_sha256"],
            "release": "v1.2 user screenshot",
            "all37_fields_documented": dictionary["schema_fields_documented"] == 37,
        },
    )
    log("preparation_complete", **summary)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        # No raw identifiers, record values or backend SQL messages in logs.
        log("preparation_failed", error_type=type(error).__name__)
        raise SystemExit(1) from None
