"""Phase 6: separately frozen calibration, then one reserved independent evaluation.

No point-model fitting, test-based selection, automatic app promotion or uploads.
"""

from __future__ import annotations

import argparse
import heapq
import itertools
import json
import platform
import time
from collections import Counter, defaultdict
from importlib.metadata import version
from pathlib import Path

import duckdb
import joblib
import numpy as np

from research.datasets.metabonet import (
    SubjectSeries,
    WindowRejected,
    build_window,
    candidate_indices,
    event_identity,
    trajectory_fingerprints,
    window_to_example,
)
from research.evaluation.metabonet_uncertainty import (
    SymmetricBands,
    calibration_representatives,
    interval_summary,
)
from research.evaluation.refinement_metrics import event_metrics, summarize_records
from research.evaluation.statistics import paired_participant_interval
from research.models.adapters.persistence import PersistenceForecastAdapter
from research.pipelines.prepare_metabonet import (
    ROOT,
    hash_file,
    iter_prepared_windows,
    log,
    project_development,
    projected_subjects,
    read_frozen_protocol,
    verify_preparation,
    write_json,
)
from research.pipelines.run_metabonet_inference import (
    execution_guard,
    read_execution,
    record_checksum,
    request_fingerprint,
    verify_completed,
)
from research.pipelines.run_metabonet_training import freeze_json, verify_training_completed

VERSION = "metabonet_phase6_v1"
CANDIDATES = ("persistence", "lightgbm_direct", "ridge_direct")
PRIMARY = "lightgbm_direct"
OUTPUT = ROOT / "artifacts/evaluation-results/metabonet-phase6-v1"
PREPARED = ROOT / "artifacts/evaluation-results/metabonet-phase2-v1"
TRAINED = ROOT / "artifacts/evaluation-results/metabonet-phase4-v1"
RAW = ROOT / "data/raw/metabonet"
PROTOCOL = ROOT / "docs/planning/GlycoLens_16_MetaboNet_Independent_Evaluation.md"


def read_checked(path):
    value = json.loads(path.read_text())
    if value.get("row_sha256") != record_checksum(value):
        raise ValueError("frozen phase 6 record changed")
    return value


def verify_phase6_stage(directory, stage):
    verify_completed(directory)  # Reuse integrity checks, never its Phase 3 access flags.
    execution = read_execution(directory)
    result = json.loads((directory / "summary.json").read_text())
    if (
        execution["configuration"]["version"] != VERSION
        or execution["configuration"]["stage"] != stage
        or result["stage"] != stage
        or result["point_weights_fitted"] is not False
        or result["test_values_read"] != (stage == "test")
    ):
        raise ValueError("phase 6 stage/access metadata disagree")
    return {
        "artifact_hashes_valid": True,
        "point_weights_fitted": False,
        "calibration_values_read": True,
        "test_values_read": stage == "test",
    }


def require_calibration_gate(directory):
    verify_phase6_stage(directory, "calibration")
    state = read_checked(directory / "bands.json")
    if set(state["models"]) != set(CANDIDATES) or state["primary_candidate"] != PRIMARY:
        raise ValueError("calibration candidate set changed")
    return {name: SymmetricBands.from_dict(value) for name, value in state["models"].items()}


def reserved_subject_windows(segments, role):
    if role not in ("primary_test", "source_test"):
        raise ValueError("reserved windows require an explicit test role")
    quality = {
        "status": "ready",
        "sampled_candidate_count": 0,
        "positive_carb_rows": 0,
        "rejected": {},
    }
    if not segments:
        return [], {**quality, "status": "no_projected_records"}
    if len({s.sid for s in segments}) != 1:
        raise ValueError("reserved segments have different identities")
    if any(
        np.intersect1d(left.times, right.times).size
        for i, left in enumerate(segments)
        for right in segments[i + 1 :]
    ):
        return [], {**quality, "status": "duplicate_cross_file_timestamps"}
    candidates = []
    for segment_number, series in enumerate(segments):
        quality["positive_carb_rows"] += len(series.meal_indices)
        for index in candidate_indices(series, limit=100):
            candidates.append(
                (event_identity(series.sid, series.times[index]), segment_number, index)
            )
    # Each segment's first 100 contains every possible member of the global first 100.
    candidates = sorted(candidates)[:100]
    quality["sampled_candidate_count"] = len(candidates)
    rows, rejected = [], Counter()
    for _, segment_number, index in candidates:
        try:
            window = build_window(segments[segment_number], index, hours=24, delay_minutes=5)
        except WindowRejected as error:
            rejected[error.reason] += 1
            continue
        window_to_example(window, with_covariates=True)
        rows.append({**window, "split": role, "publisher_segment": segment_number})
    quality["rejected"] = dict(rejected)
    quality["eligible_event_count"] = len(rows)
    return rows, quality


def prepare_reserved(prepared, raw, output, calibration):
    # The only raw test projection entry point is behind this completed-stage gate.
    require_calibration_gate(calibration)
    catalog = json.loads((prepared / "subject-manifest.json").read_text())
    selected = catalog["primary_test"] + catalog["source_test"]
    development = {s["sid"] for s in catalog["development"]}
    if development & {s["sid"] for s in selected}:
        raise ValueError("reserved identity leaked into development")
    if {s["sid"] for s in catalog["primary_test"]} & set(catalog["publisher_training_sids"]):
        raise ValueError("primary identity exists in publisher training")
    metadata = {s["sid"]: s for s in selected}
    projections = {}
    for role in ("train", "test"):
        path = output / f"reserved-{role}-projection.parquet"
        if path.exists():
            raise ValueError("partial reserved projection exists; review before further access")
        subset = [s for s in selected if role in s["file_roles"]]
        with duckdb.connect(
            config={
                "threads": 2,
                "memory_limit": "2GB",
                "temp_directory": str(output / "scratch"),
                "autoinstall_known_extensions": False,
                "autoload_known_extensions": False,
            }
        ) as con:
            project_development(con, raw / f"{role}.parquet", subset, path)
        projections[role] = path
    log("reserved_values_projected", reserved_identity_count=len(selected))
    owners, quarantined, contaminated_references = {}, set(), set()
    references = {s["sid"]: s for s in catalog["development"]}
    for number, (sid, times, values) in enumerate(
        projected_subjects(prepared / "development-projection.parquet"), 1
    ):
        try:
            series = SubjectSeries(sid, references[sid]["source"], times, values)
        except ValueError:
            continue
        for fingerprint in trajectory_fingerprints(series):
            owners.setdefault(fingerprint, sid)
        if number % 50 == 0:
            log("reference_fingerprints", subjects_completed=number)
    reference_count = len(owners)

    def stream(role, path):
        for sid, times, values in projected_subjects(path):
            yield sid, role, times, values

    merged = heapq.merge(
        *(stream(role, path) for role, path in projections.items()),
        key=lambda item: (item[0], item[1]),
    )
    windows, quality = [], []
    for number, (sid, group) in enumerate(itertools.groupby(merged, key=lambda item: item[0]), 1):
        segments, invalid = [], False
        for _, _, times, values in group:
            try:
                segments.append(SubjectSeries(sid, metadata[sid]["source"], times, values))
            except ValueError:
                invalid = True
        for series in segments:
            for fingerprint in trajectory_fingerprints(series):
                previous = owners.setdefault(fingerprint, sid)
                if previous != sid:
                    quarantined.add(sid)
                    if previous in development:
                        contaminated_references.add(previous)
                    else:
                        quarantined.add(previous)
        if invalid:
            rows, item = [], {"status": "invalid_subject_timestamps", "rejected": {}}
        else:
            rows, item = reserved_subject_windows(segments, metadata[sid]["split"])
        windows.extend(rows)
        quality.append(
            {"sid": sid, "source": metadata[sid]["source"], "split": metadata[sid]["split"], **item}
        )
        if number % 20 == 0:
            log("reserved_subjects_prepared", completed=number, total=len(selected))
    if {q["sid"] for q in quality} != set(metadata):
        raise ValueError("reserved projected identities differ from reservation")
    for item in quality:
        if item["sid"] in quarantined:
            item["status"] = "exact_trajectory_candidate_quarantine"
    windows = [w for w in windows if w["sid"] not in quarantined]
    freeze_json(
        output / "reserved-quality.json",
        {
            "subjects": quality,
            "quarantined_sids": sorted(quarantined),
            "contaminated_development_references": sorted(contaminated_references),
            "reference_distinct_fingerprints": reference_count,
            "all_distinct_fingerprints": len(owners),
        },
    )
    with (output / "reserved-windows.jsonl").open("x", encoding="utf-8") as target:
        for window in sorted(windows, key=lambda w: w["event_id"]):
            target.write(json.dumps(window, allow_nan=False) + "\n")
    aggregate = {}
    for role in ("primary_test", "source_test"):
        group = [q for q in quality if q["split"] == role]
        ready = [q for q in group if q["status"] == "ready"]
        usable = [w for w in windows if w["split"] == role]
        rejected = Counter()
        for item in ready:
            rejected.update(item["rejected"])
        aggregate[role] = {
            "reserved_identities": len(group),
            "eligible_identities": len({w["sid"] for w in usable}),
            "eligible_events": len(usable),
            "status_counts": dict(Counter(q["status"] for q in group)),
            "positive_carb_rows": sum(q.get("positive_carb_rows", 0) for q in group),
            "sampled_candidate_count": sum(q.get("sampled_candidate_count", 0) for q in group),
            "rejections_ready_subjects": dict(rejected),
            "eligible_events_by_source": dict(Counter(w["source"] for w in usable)),
        }
    return windows, {
        **aggregate,
        "quarantined_identities": len(quarantined),
        "contaminated_development_references": len(contaminated_references),
        "reference_distinct_fingerprints": reference_count,
        "all_distinct_fingerprints": len(owners),
    }


def evaluate_windows(windows, models, bands, path):
    if path.exists():
        raise ValueError("prediction output exists; no retry/overwrite of attempted forecasts")
    roles = {w["split"] for w in windows}
    if (
        len(roles) != 1
        or not roles <= {"calibration", "primary_test", "source_test"}
        or len({w["event_id"] for w in windows}) != len(windows)
    ):
        raise ValueError("evaluation requires one allowed role and unique event identities")
    runs = {name: [] for name in models}
    started = time.perf_counter()
    with path.open("x", encoding="utf-8") as target:
        for index, window in enumerate(sorted(windows, key=lambda w: w["event_id"])):
            if window["history_hours"] != 24 or window["carb_delay_minutes"] != 5:
                raise ValueError("evaluation window differs from frozen preprocessing")
            request = window_to_example(window, with_covariates=True).request
            fingerprint = request_fingerprint(request)
            for name, model in models.items():
                row = {
                    "event_id": window["event_id"],
                    "participant_id": window["sid"],
                    "source": window["source"],
                    "role": window["split"],
                    "model": name,
                    "truth": window["truth"],
                    "request_sha256": fingerprint,
                    "prediction": [],
                    "lower": [],
                    "upper": [],
                    "curve_lower": [],
                    "curve_upper": [],
                    "metrics": {},
                    "error_type": None,
                    "error_cause_type": None,
                }
                attempt = time.perf_counter()
                try:
                    result = model.predict(request)
                    prediction = [float(v) for v in result.median]
                    if len(prediction) != 24 or not np.isfinite(prediction).all():
                        raise ValueError("invalid point prediction")
                    row.update(
                        prediction=prediction, metrics=event_metrics(window["truth"], prediction)
                    )
                    if bands is not None:
                        bounds = bands[name].bounds(prediction)
                        for key, values in zip(
                            ("lower", "upper", "curve_lower", "curve_upper"), bounds
                        ):
                            row[key] = [float(v) for v in values]
                except Exception as error:
                    row.update(
                        prediction=[],
                        metrics={},
                        lower=[],
                        upper=[],
                        curve_lower=[],
                        curve_upper=[],
                        error_type=type(error).__name__,
                        error_cause_type=(
                            type(error.__cause__).__name__ if error.__cause__ else None
                        ),
                    )
                row["wall_ms"] = (time.perf_counter() - attempt) * 1000
                row["row_sha256"] = record_checksum(row)
                target.write(json.dumps(row, allow_nan=False) + "\n")
                target.flush()
                runs[name].append(row)
            if (index + 1) % 500 == 0:
                log(
                    "independent_predictions", completed_events=index + 1, total_events=len(windows)
                )
    return runs, {
        "elapsed_seconds": time.perf_counter() - started,
        "prediction_file_sha256": hash_file(path),
    }


def cohort_summary(runs):
    output = {"common_success": summarize_records(runs), "models": {}}
    for name, rows in runs.items():
        metrics = summarize_records({name: rows})["runs"][name]
        good = [r for r in rows if r["error_type"] is None]
        subjects = defaultdict(list)
        for row in good:
            subjects[row["participant_id"]].append(row)
        subject_mae = [np.mean([r["metrics"]["mae"] for r in group]) for group in subjects.values()]
        subject_within = [
            np.mean([r["metrics"]["within_10"] for r in group]) for group in subjects.values()
        ]
        output["models"][name] = {
            **metrics,
            "intervals": interval_summary(rows),
            "failure_types": dict(Counter(r["error_type"] for r in rows if r["error_type"])),
            "negative_prediction_points": sum(p < 0 for r in good for p in r["prediction"]),
            "macro_mae_by_horizon": [
                float(v)
                for v in np.mean(
                    [
                        np.abs(
                            np.asarray([r["truth"] for r in group])
                            - np.asarray([r["prediction"] for r in group])
                        ).mean(axis=0)
                        for group in subjects.values()
                    ],
                    axis=0,
                )
            ]
            if subjects
            else [],
            "participant_mae_percentiles": [
                float(v) for v in np.percentile(subject_mae, [0, 25, 50, 75, 100])
            ]
            if subjects
            else [],
            "participant_within10_percentiles": [
                float(v) for v in np.percentile(subject_within, [0, 25, 50, 75, 100])
            ]
            if subjects
            else [],
        }
    primary, baseline = output["models"][PRIMARY], output["models"]["persistence"]
    pm, bm = primary["participant_macro"], baseline["participant_macro"]
    output["frozen_primary_confirmation_gate"] = {
        "candidate": PRIMARY,
        "test_based_reselection": False,
        "mae_improvement_fraction": 1 - pm["mae"] / bm["mae"]
        if pm and bm and bm["mae"] > 0
        else None,
        "passes": bool(
            pm
            and bm
            and primary["failure_count"] == 0
            and baseline["failure_count"] == 0
            and pm["mae"] <= 0.9 * bm["mae"]
            and pm["within_10"] >= bm["within_10"]
            and primary["point_metrics"]["absolute_error_p95"]
            <= baseline["point_metrics"]["absolute_error_p95"]
        ),
    }
    output["paired_mae_intervals"] = {}
    for name in (PRIMARY, "ridge_direct"):
        if any(not r["error_type"] for r in runs[name]):
            output["paired_mae_intervals"][name + "_minus_persistence"] = (
                paired_participant_interval(
                    runs[name], runs["persistence"], seed=20261016, samples=10000
                )
            )
    return output


def subgroup_labels(window):
    current, carbs = window["history"][-1], window["meal_carbs_g"]
    presence = min(
        np.mean([v is not None for v in window["context"][channel]])
        for channel in ("basal", "bolus")
    )
    return {
        "source": window["source"],
        "origin_cgm": "below70" if current < 70 else "70to180" if current <= 180 else "above180",
        "carbs": "below30" if carbs < 30 else "30to60" if carbs <= 60 else "above60",
        "insulin_record_masks": "at_least90pct" if presence >= 0.9 else "below90pct",
    }


def summarize_subgroups(runs, windows):
    groups = defaultdict(set)
    for window in windows:
        for key, value in subgroup_labels(window).items():
            groups[f"{key}:{value}"].add(window["event_id"])
    # No within-subgroup model selection or bootstrapped post-hoc significance testing.
    return {
        label: {
            "event_count": len(ids),
            "models": {
                name: {
                    **summarize_records({name: [r for r in rows if r["event_id"] in ids]})["runs"][
                        name
                    ],
                    "intervals": interval_summary([r for r in rows if r["event_id"] in ids]),
                }
                for name, rows in runs.items()
            },
        }
        for label, ids in sorted(groups.items())
    }


def finish(directory, summary):
    write_json(directory / "summary.json", summary)
    write_json(
        directory / "complete.json",
        {
            "version": VERSION,
            "artifact_hashes": {
                p.relative_to(directory).as_posix(): hash_file(p)
                for p in sorted(directory.rglob("*"))
                if p.is_file()
                and "scratch" not in p.parts
                and p.name not in ("complete.json", "complete.sha256")
            },
        },
    )
    (directory / "complete.sha256").write_text(hash_file(directory / "complete.json") + "\n")
    return verify_phase6_stage(directory, summary["stage"])


def source_files():
    names = [
        "research/pipelines/run_metabonet_independent.py",
        "research/evaluation/metabonet_uncertainty.py",
        "research/datasets/metabonet.py",
        "research/datasets/t1d_uom.py",
        "research/pipelines/prepare_metabonet.py",
        "research/pipelines/run_metabonet_inference.py",
        "research/pipelines/run_metabonet_training.py",
        "research/models/adapters/base.py",
        "research/models/adapters/metabonet_tabular.py",
        "research/models/adapters/persistence.py",
        "research/models/adapters/chronos2.py",
        "research/models/adapters/covariates.py",
        "research/evaluation/refinement_metrics.py",
        "research/evaluation/statistics.py",
        "tests/research/test_metabonet_independent.py",
        "docs/planning/GlycoLens_16_MetaboNet_Independent_Evaluation.md",
        "pyproject.toml",
        "uv.lock",
    ]
    return {name: ROOT / name for name in names}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("calibration", "test"), required=True)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / "artifacts"):
        raise ValueError("health artifacts must remain under ignored artifacts/")
    directory, calibration = output / args.stage, output / "calibration"
    if args.verify_only:
        log("verification", **verify_phase6_stage(directory, args.stage))
        return 0
    if (directory / "complete.json").exists():
        raise ValueError("completed independent stage cannot be replayed; use --verify-only")
    verify_preparation(PREPARED)
    verify_training_completed(TRAINED)
    prep = read_frozen_protocol(PREPARED)
    for name, evidence in prep["inputs"].items():
        if hash_file(RAW / name) != evidence["sha256"]:
            raise ValueError("raw input differs from frozen preparation")
    configuration = {
        "version": VERSION,
        "stage": args.stage,
        "primary_candidate": PRIMARY,
        "candidates": CANDIDATES,
        "history_hours": 24,
        "carb_delay_minutes": 5,
        "preparation_protocol_sha256": hash_file(PREPARED / "frozen-protocol.json"),
        "trained_completion_sha256": hash_file(TRAINED / "complete.json"),
        "raw_hashes": {name: evidence["sha256"] for name, evidence in prep["inputs"].items()},
        "model_hashes": {
            a: hash_file(TRAINED / f"model-{a}.joblib") for a in ("lightgbm", "ridge")
        },
        "coverage": 0.8,
        "requested_cpu_threads": 2,
    }
    bands = None
    if args.stage == "test":
        bands = require_calibration_gate(calibration)
        previous = read_execution(calibration)
        for key, value in configuration.items():
            if key != "stage" and previous["configuration"][key] != json.loads(json.dumps(value)):
                raise ValueError("test configuration differs from pre-calibration freeze")
        if previous["source_hashes"] != {
            name: hash_file(path) for name, path in source_files().items()
        }:
            raise ValueError("test sources differ from pre-calibration freeze")
        configuration["calibration_completion_sha256"] = hash_file(calibration / "complete.json")
    execution_guard(directory, configuration, source_files())
    started = time.perf_counter()
    # Load estimator libraries BEFORE limiting pools: late imports escaped Phase 5's context.
    import lightgbm  # noqa: F401
    import scipy.linalg  # noqa: F401
    import sklearn.impute  # noqa: F401
    import sklearn.linear_model  # noqa: F401
    import sklearn.preprocessing  # noqa: F401
    from threadpoolctl import threadpool_info, threadpool_limits

    with threadpool_limits(limits=2):
        pools = threadpool_info()
        if any(p["num_threads"] > 2 for p in pools):
            raise ValueError("numerical thread limit did not take effect")
        models = {
            a + "_direct": joblib.load(TRAINED / f"model-{a}.joblib") for a in ("lightgbm", "ridge")
        }
        for algorithm in ("lightgbm", "ridge"):
            model = models[algorithm + "_direct"]
            expected = 31 if algorithm == "lightgbm" else 1000
            if (model.algorithm, model.parameter, model.history_hours, model.profile) != (
                algorithm,
                expected,
                24,
                "events",
            ):
                raise ValueError("frozen model configuration differs")
        models["persistence"] = PersistenceForecastAdapter()
        models["persistence"].load()
        pools = threadpool_info()
        if any(p["num_threads"] > 2 for p in pools):
            raise ValueError("model deserialization loaded an uncontrolled numerical pool")
        before = {name: joblib.hash(model) for name, model in models.items()}
        summary = {
            "version": VERSION,
            "stage": args.stage,
            "point_weights_fitted": False,
            "calibration_values_read": True,
            "test_values_read": args.stage == "test",
            "primary_candidate": PRIMARY,
            "test_based_reselection": False,
            "environment": {
                "python": platform.python_version(),
                "packages": {
                    name: version(name)
                    for name in ("numpy", "scikit-learn", "lightgbm", "duckdb", "joblib")
                },
                "threadpools": pools,
            },
        }
        if args.stage == "calibration":
            eligible = list(iter_prepared_windows(PREPARED, split="calibration", hours=24, delay=5))
            windows = calibration_representatives(eligible)
            freeze_json(
                directory / "representatives.json",
                {
                    "eligible_event_count": len(eligible),
                    "selected_event_ids": [w["event_id"] for w in windows],
                    "participant_count": len(windows),
                    "sources": dict(Counter(w["source"] for w in windows)),
                },
            )
            runs, timing = evaluate_windows(windows, models, None, directory / "predictions.jsonl")
            if any(r["error_type"] for rows in runs.values() for r in rows):
                raise ValueError(
                    "calibration prediction failure; no adaptive replacement or test access"
                )
            bands = {
                name: SymmetricBands.fit(
                    [r["truth"] for r in rows], [r["prediction"] for r in rows]
                )
                for name, rows in runs.items()
            }
            freeze_json(
                directory / "bands.json",
                {
                    "primary_candidate": PRIMARY,
                    "models": {name: band.to_dict() for name, band in bands.items()},
                    "execution_sha256": hash_file(directory / "execution.json"),
                    "prediction_sha256": hash_file(directory / "predictions.jsonl"),
                },
            )
            for name, rows in runs.items():
                for row in rows:
                    for key, values in zip(
                        ("lower", "upper", "curve_lower", "curve_upper"),
                        bands[name].bounds(row["prediction"]),
                    ):
                        row[key] = [float(v) for v in values]
            summary.update(
                eligible_events=len(eligible),
                participant_count=len(windows),
                calibration_descriptive=cohort_summary(runs),
                timing=timing,
            )
        else:
            windows, cohort = prepare_reserved(PREPARED, RAW, directory, calibration)
            summary["cohort"] = cohort
            summary["cohorts"] = {}
            for role in ("primary_test", "source_test"):
                subset = [w for w in windows if w["split"] == role]
                if not subset:
                    summary["cohorts"][role] = {"status": "no_eligible_events"}
                    continue
                runs, timing = evaluate_windows(
                    subset, models, bands, directory / f"{role}-predictions.jsonl"
                )
                summary["cohorts"][role] = {
                    **cohort_summary(runs),
                    "timing": timing,
                    "subgroups": summarize_subgroups(runs, subset),
                }
        after = {name: joblib.hash(model) for name, model in models.items()}
        if before != after:
            raise ValueError("point model state changed during independent evaluation")
        summary["point_model_state_unchanged"] = True
        summary["point_model_state_hashes"] = before
        summary["elapsed_seconds"] = time.perf_counter() - started
    verify_preparation(PREPARED)
    verify_training_completed(TRAINED)
    log(
        "independent_stage_complete",
        stage_name=args.stage,
        **finish(directory, summary),
        elapsed_seconds=summary["elapsed_seconds"],
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        log("independent_stage_failed", error_type=type(error).__name__)
        raise SystemExit(1) from None
