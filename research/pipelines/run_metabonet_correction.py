"""Train-only correction selection followed by paired validation; reserved data excluded."""

import argparse
import hashlib
import json
import platform
import time
from collections import Counter
from importlib.metadata import version

import joblib
import numpy as np

from research.datasets.metabonet import window_to_example
from research.evaluation.refinement_metrics import event_metrics
from research.evaluation.statistics import paired_participant_interval
from research.models.adapters.metabonet_context import c2_request
from research.models.adapters.metabonet_residual import MetaboNetResidualAdapter
from research.models.adapters.metabonet_tabular import MetaboNetTabularAdapter
from research.pipelines.cache_metabonet_backbone import OUTPUT, VERSION
from research.pipelines.prepare_metabonet import (
    ROOT,
    hash_file,
    log,
    verify_preparation,
    write_json,
)
from research.pipelines.run_metabonet_inference import (
    VARIANTS,
    collect_validation,
    execution_guard,
    read_execution,
    record_checksum,
    request_fingerprint,
    verify_completed,
)
from research.pipelines.run_metabonet_training import (
    choose_cv,
    collect_training,
    compare,
    frame,
    freeze_json,
    macro_score,
    participant_weights,
    verify_training_completed,
)

GRID = [
    dict(
        name=f"{algorithm}_residual_{parameter}",
        kind="residual",
        algorithm=algorithm,
        parameter=parameter,
    )
    for algorithm in ("ridge", "lightgbm")
    for parameter in ((10, 1000) if algorithm == "ridge" else (15, 31))
]
CONTROLS = [
    dict(name=f"{algorithm}_control", kind="control", algorithm=algorithm, parameter=parameter)
    for algorithm, parameter in (("ridge", 1000), ("lightgbm", 31))
]


def read_frozen(path):
    value = json.loads(path.read_text())
    if value.get("row_sha256") != record_checksum(value):
        raise ValueError("frozen decision checksum changed")
    return value


def make_model(config):
    kwargs = {key: config[key] for key in ("algorithm", "parameter")}
    if config["kind"] == "residual":
        return MetaboNetResidualAdapter(**kwargs)
    return MetaboNetTabularAdapter(**kwargs, history_hours=24, profile="events")


def fit_model(model, config, values, indices):
    kwargs = dict(sample_weight=participant_weights([values["subjects"][i] for i in indices]))
    args = [values["x"][indices], values["y"][indices], values["current"][indices]]
    if config["kind"] == "residual":
        args.append(values["baseline"][indices])
    model.fit_arrays(*args, **kwargs)


def predict_model(model, config, values, indices):
    args = [values["x"][indices], values["current"][indices]]
    if config["kind"] == "residual":
        args.append(values["baseline"][indices])
    return model.predict_array(*args)


def cross_validate(config, values, folds, output, execution_sha):
    metadata_path = output / f"cv-{config['name']}.json"
    path = output / f"cv-{config['name']}.npy"
    if metadata_path.exists():
        item = read_frozen(metadata_path)
        if (
            item["configuration"] != config
            or item["execution_sha256"] != execution_sha
            or item["predictions_sha256"] != hash_file(path)
        ):
            raise ValueError("CV cache changed")
        return item
    if path.exists():
        raise ValueError("partial CV output requires review")
    assignment = np.array([folds[s] for s in values["subjects"]])
    predictions = np.full_like(values["y"], np.nan)
    errors = []
    started = time.perf_counter()
    for fold in range(3):
        fit, held = np.flatnonzero(assignment != fold), np.flatnonzero(assignment == fold)
        if (
            not len(fit)
            or not len(held)
            or {values["subjects"][i] for i in fit} & {values["subjects"][i] for i in held}
        ):
            raise ValueError("subject leakage or empty correction fold")
        try:
            model = make_model(config)
            fit_model(model, config, values, fit)
            predictions[held] = predict_model(model, config, values, held)
        except Exception as error:
            errors.append(dict(fold=fold, error_type=type(error).__name__))
        log("correction_cv_fold", candidate=config["name"], fold=fold, failures=len(errors))
    good = np.isfinite(predictions).all(axis=1)
    score = (
        macro_score(values["y"], predictions, values["subjects"]) if good.all() else (None, None)
    )
    with path.open("xb") as stream:
        np.save(stream, predictions, allow_pickle=False)
    return freeze_json(
        metadata_path,
        dict(
            **config,
            configuration=config,
            macro_mae=score[0],
            within_10=score[1],
            failure_count=len(errors) + int(not good.all() and not errors),
            fold_errors=errors,
            oof_events=len(predictions),
            valid_oof_events=int(good.sum()),
            execution_sha256=execution_sha,
            predictions_sha256=hash_file(path),
            elapsed_seconds=time.perf_counter() - started,
        ),
    )


def fit_final(config, values, output, execution_sha):
    path = output / f"model-{config['name']}.joblib"
    metadata_path = output / f"model-{config['name']}.json"
    if metadata_path.exists():
        item = read_frozen(metadata_path)
        if (
            item["configuration"] != config
            or item["execution_sha256"] != execution_sha
            or item["model_sha256"] != hash_file(path)
        ):
            raise ValueError("saved correction/control model changed")
        return joblib.load(path), item
    if path.exists():
        raise ValueError("partial model output requires review")
    started = time.perf_counter()
    model = make_model(config)
    fit_model(model, config, values, np.arange(len(values["ids"])))
    sample = np.arange(min(10, len(values["ids"])))
    before = predict_model(model, config, values, sample)
    joblib.dump(model, path)
    restored = joblib.load(path)
    if not np.allclose(before, predict_model(restored, config, values, sample), atol=1e-10, rtol=0):
        raise ValueError("model reload changes predictions")
    return restored, freeze_json(
        metadata_path,
        dict(
            configuration=config,
            model_sha256=hash_file(path),
            execution_sha256=execution_sha,
            training_events=len(values["ids"]),
            training_subjects=len(set(values["subjects"])),
            feature_count=model.feature_count_,
            reload_prediction_equivalent=True,
            fit_elapsed_seconds=time.perf_counter() - started,
        ),
    )


def evaluate(model, config, windows, backbone_rows, output, model_sha):
    path = output / f"validation-{config['name']}.jsonl"
    metadata_path = output / f"validation-{config['name']}.json"
    if metadata_path.exists():
        item = read_frozen(metadata_path)
        if item["model_sha256"] != model_sha or item["predictions_sha256"] != hash_file(path):
            raise ValueError("validation output changed")
        rows = [json.loads(s) for s in path.read_text().splitlines()]
        if any(r.get("row_sha256") != record_checksum(r) for r in rows):
            raise ValueError("validation row changed")
        return rows, item
    if path.exists():
        raise ValueError("partial validation output requires review")
    values = frame(windows, 24, "events")
    baseline = np.full((len(values["ids"]), 24), np.nan)
    for i, key in enumerate(values["ids"]):
        row = backbone_rows[key]
        request = c2_request(window_to_example(windows[key], with_covariates=True).request)
        if (
            row["request_sha256"] != request_fingerprint(request)
            or row["truth"] != windows[key]["truth"]
            or row["participant_id"] != windows[key]["sid"]
        ):
            raise ValueError("reused C2 request/target identity differs")
        if row["error_type"] is None:
            baseline[i] = row["prediction"]
    values["baseline"] = baseline
    good = (
        np.isfinite(baseline).all(axis=1)
        if config["kind"] == "residual"
        else np.ones(len(baseline), dtype=bool)
    )
    predictions = np.full_like(baseline, np.nan)
    error_type = None
    started = time.perf_counter()
    try:
        if good.any():
            predictions[good] = predict_model(model, config, values, np.flatnonzero(good))
    except Exception as error:
        error_type = type(error).__name__
    elapsed = (time.perf_counter() - started) * 1000
    rows = []
    with path.open("x", encoding="utf-8") as stream:
        for i, key in enumerate(values["ids"]):
            w = windows[key]
            error = "BackboneUnavailable" if not good[i] else error_type
            prediction = [float(v) for v in predictions[i]] if error is None else []
            row = dict(
                event_id=key,
                participant_id=w["sid"],
                source=w["source"],
                truth=w["truth"],
                prediction=prediction,
                lower=[],
                upper=[],
                error_type=error,
                wall_ms=0,
                timing="batch head only; per-request latency not measured",
                model_sha256=model_sha,
                request_sha256=request_fingerprint(
                    window_to_example(w, with_covariates=True).request
                ),
                backbone_row_sha256=backbone_rows[key]["row_sha256"],
                metrics=event_metrics(w["truth"], prediction) if error is None else {},
            )
            row["row_sha256"] = record_checksum(row)
            stream.write(json.dumps(row, allow_nan=False) + "\n")
            rows.append(row)
    return rows, freeze_json(
        metadata_path,
        dict(
            model_sha256=model_sha,
            predictions_sha256=hash_file(path),
            batch_head_prediction_ms=elapsed,
            events=len(rows),
            failures=sum(r["error_type"] is not None for r in rows),
            interval="none",
        ),
    )


def incremental_gate(candidate, incumbent):
    m, base = candidate["participant_macro"], incumbent["participant_macro"]
    if candidate["failure_count"] or not m:
        return dict(passes=False, mae_improvement_fraction=None)
    improvement = 1 - m["mae"] / base["mae"]
    return dict(
        passes=bool(
            m["mae"] <= 0.95 * base["mae"]
            and m["within_10"] >= base["within_10"]
            and candidate["point_metrics"]["absolute_error_p95"]
            <= incumbent["point_metrics"]["absolute_error_p95"]
        ),
        mae_improvement_fraction=improvement,
    )


def analyze(runs, windows, correction_names):
    summary = compare(runs, windows)
    # New head-only batch rows have no individual latency measurement.
    tables = [
        summary["selection_summary"],
        summary["all_run_summary"],
        *summary["pairs"].values(),
        *summary["by_source"].values(),
    ]
    for table in tables:
        for name, item in table["runs"].items():
            if "residual" in name or "control" in name:
                item["wall_p95_ms"] = None
    incumbent = summary["selection_summary"]["runs"]["lightgbm_direct"]
    gates = {}
    for name in correction_names:
        full = summary["selection_summary"]["runs"].get(name)
        gates[name] = (
            incremental_gate(full, incumbent)
            if full
            else dict(passes=False, mae_improvement_fraction=None)
        )
    eligible = [n for n in correction_names if gates[n]["passes"]]
    chosen = (
        min(
            eligible,
            key=lambda n: (
                summary["selection_summary"]["runs"][n]["participant_macro"]["mae"],
                -summary["selection_summary"]["runs"][n]["participant_macro"]["within_10"],
                n,
            ),
        )
        if eligible
        else "lightgbm_direct"
    )
    summary["incremental_correction_gates"] = gates
    summary["advancement_candidate"] = chosen
    summary["correction_intervals"] = {
        name: {
            against: paired_participant_interval(
                runs[name], runs[against], samples=10000, seed=20261016
            )
            for against in ("lightgbm_direct", name.split("_")[0] + "_control")
        }
        for name in correction_names
        if any(r["error_type"] is None for r in runs[name])
    }
    return summary


def verify_phase5(output=OUTPUT):
    for stage in ("backbone", "heads"):
        verify_completed(output / stage)
    if hash_file(output / "complete.json") != (output / "complete.sha256").read_text().strip():
        raise ValueError("phase completion manifest changed")
    manifest = json.loads((output / "complete.json").read_text())
    if manifest.get("version") != VERSION or any(
        read_execution(output / stage)["configuration"]["version"] != VERSION
        for stage in ("backbone", "heads")
    ):
        raise ValueError("unexpected correction study version")
    for name, digest in manifest["artifact_hashes"].items():
        path = (output / name).resolve()
        if not path.is_relative_to(output.resolve()) or hash_file(path) != digest:
            raise ValueError("completed correction artifact changed")
    summary = json.loads((output / "heads/summary.json").read_text())
    if len(summary["fit_metadata"]) != 4 or summary["calibration_or_test_access"] is not False:
        raise ValueError("unexpected correction study scope")
    return dict(
        artifact_hashes_valid=True,
        small_weights_fitted=True,
        foundation_weights_fitted=False,
        calibration_or_test_access=False,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if args.verify_only:
        log("phase5_verified", **verify_phase5())
        return 0
    output = OUTPUT / "heads"
    if (output / "complete.json").exists():
        raise ValueError("completed correction stage refuses replay")
    prepared = ROOT / "artifacts/evaluation-results/metabonet-phase2-v1"
    phase3 = ROOT / "artifacts/evaluation-results/metabonet-phase3-v1"
    phase4 = ROOT / "artifacts/evaluation-results/metabonet-phase4-v1"
    verify_preparation(prepared)
    verify_completed(phase3)
    verify_training_completed(phase4)
    verify_completed(OUTPUT / "backbone")
    training, original_cohort = collect_training(prepared)
    common = set.intersection(*(set(v) for v in training.values()))
    cached_rows = [
        json.loads(s) for s in (OUTPUT / "backbone/training.jsonl").read_text().splitlines()
    ]
    cached = {r["event_id"]: r for r in cached_rows}
    if len(cached) != len(cached_rows) or set(cached) != common:
        raise ValueError("training cache population differs")
    for key, row in cached.items():
        w = training[6][key]
        if (
            row.get("row_sha256") != record_checksum(row)
            or row["participant_id"] != w["sid"]
            or row["source"] != w["source"]
            or row["request_sha256"]
            != request_fingerprint(c2_request(window_to_example(w, with_covariates=True).request))
        ):
            raise ValueError("training backbone cache mismatch")
    ids = sorted(key for key, row in cached.items() if row["error_type"] is None)
    if len(ids) < 3:
        raise ValueError("insufficient usable training forecasts")
    values = frame({key: training[24][key] for key in ids}, 24, "events")
    values["baseline"] = np.array([cached[key]["prediction"] for key in values["ids"]])
    if values["baseline"].shape != values["y"].shape or not np.isfinite(values["baseline"]).all():
        raise ValueError("invalid successful training backbone rows")
    folds = read_frozen(phase4 / "subject-folds.json")
    folds.pop("row_sha256")
    cohort = dict(
        original_events=len(common),
        original_subjects=original_cohort["common_subject_count"],
        usable_events=len(ids),
        usable_subjects=len(set(values["subjects"])),
        excluded_backbone_failures=len(common) - len(ids),
        sources=dict(Counter(training[24][key]["source"] for key in ids)),
        ids_sha256=hashlib.sha256(json.dumps(ids).encode()).hexdigest(),
    )
    sources = {
        name: ROOT / name
        for name in (
            "research/pipelines/run_metabonet_correction.py",
            "research/pipelines/cache_metabonet_backbone.py",
            "research/models/adapters/metabonet_residual.py",
            "research/models/adapters/metabonet_tabular.py",
            "research/models/adapters/metabonet_context.py",
            "research/models/adapters/base.py",
            "research/pipelines/run_metabonet_training.py",
            "research/pipelines/run_metabonet_inference.py",
            "research/pipelines/prepare_metabonet.py",
            "research/datasets/metabonet.py",
            "research/datasets/t1d_uom.py",
            "research/evaluation/refinement_metrics.py",
            "research/evaluation/statistics.py",
            "docs/planning/GlycoLens_15_MetaboNet_Chronos_Correction.md",
            "pyproject.toml",
            "uv.lock",
        )
    }
    configuration = dict(
        version=VERSION,
        stage="correction_heads",
        grid=GRID,
        controls=CONTROLS,
        cohort=cohort,
        backbone_completion_sha256=hash_file(OUTPUT / "backbone/complete.json"),
        phase3_completion_sha256=hash_file(phase3 / "complete.json"),
        phase4_completion_sha256=hash_file(phase4 / "complete.json"),
        preparation_sha256=hash_file(prepared / "frozen-protocol.json"),
        fold_metadata_sha256=hash_file(phase4 / "subject-folds.json"),
        python=platform.python_version(),
        packages={p: version(p) for p in ("numpy", "scikit-learn", "lightgbm", "joblib", "duckdb")},
        seed=20261016,
        threads=2,
        validation_before_cv_selection=False,
        calibration_or_test_access=False,
    )
    execution_guard(output, configuration, sources)
    execution_sha = hash_file(output / "execution.json")
    freeze_json(output / "training-cohort.json", cohort)
    freeze_json(output / "training-ids.json", dict(ids=ids))
    freeze_json(output / "subject-folds.json", folds)
    log("correction_training_ready", **cohort)
    started = time.perf_counter()
    trials = [
        cross_validate(config, values, folds, output, execution_sha) for config in GRID + CONTROLS
    ]
    chosen = [
        choose_cv([r for r in trials if r["kind"] == "residual"], algorithm)["configuration"]
        for algorithm in ("ridge", "lightgbm")
    ]
    freeze_json(
        output / "cv-selection.json",
        dict(choices=chosen, execution_sha256=execution_sha, selection_inputs="training OOF only"),
    )
    write_json(
        output / "cv-summary.json", dict(candidates=trials, choices=chosen, controls=CONTROLS)
    )
    log("correction_choices_frozen", choices=chosen)
    models, fit_metadata = {}, {}
    for config in chosen + CONTROLS:
        models[config["name"]], fit_metadata[config["name"]] = fit_final(
            config, values, output, execution_sha
        )
    # First prepared validation outcome read; all choices/refits above are frozen.
    validation, validation_cohort = collect_validation(prepared)
    if validation_cohort["matched_event_count"] != 1509 or set(values["subjects"]) & {
        w["sid"] for w in validation[24].values()
    }:
        raise ValueError("validation cohort changed or subject leakage")
    runs = {
        name: [json.loads(s) for s in (phase3 / f"{name}.jsonl").read_text().splitlines()]
        for name in VARIANTS
    }
    for algorithm in ("ridge", "lightgbm"):
        runs[algorithm + "_direct"] = [
            json.loads(s)
            for s in (phase4 / f"validation-{algorithm}.jsonl").read_text().splitlines()
        ]
    for rows in runs.values():
        for row in rows:
            w = validation[24][row["event_id"]]
            if (
                row.get("row_sha256") != record_checksum(row)
                or row["truth"] != w["truth"]
                or row["participant_id"] != w["sid"]
                or row["source"] != w["source"]
            ):
                raise ValueError("baseline reuse mismatch")
    backbone_rows = {r["event_id"]: r for r in runs["chronos_c2_6h"]}
    validation_metadata = {}
    for config in chosen + CONTROLS:
        name = config["name"]
        runs[name], validation_metadata[name] = evaluate(
            models[name],
            config,
            validation[24],
            backbone_rows,
            output,
            fit_metadata[name]["model_sha256"],
        )
    summary = analyze(runs, validation[24], [c["name"] for c in chosen])
    summary.update(
        training_cohort=cohort,
        validation_cohort=validation_cohort,
        cv_selection=chosen,
        fit_metadata=fit_metadata,
        validation_metadata=validation_metadata,
        elapsed_seconds=time.perf_counter() - started,
        backbone_summary=json.loads((OUTPUT / "backbone/summary.json").read_text()),
    )
    write_json(output / "summary.json", summary)
    write_json(
        output / "model-selection.json",
        dict(
            version=VERSION,
            lowest_mae_candidate=summary["selected_candidate"],
            advancement_candidate=summary["advancement_candidate"],
            incremental_gates=summary["incremental_correction_gates"],
            summary_sha256=hash_file(output / "summary.json"),
            calibration_or_test_access=False,
        ),
    )
    write_json(
        output / "complete.json",
        {
            "artifact_hashes": {
                p.name: hash_file(p) for p in sorted(output.iterdir()) if p.is_file()
            }
        },
    )
    (output / "complete.sha256").write_text(hash_file(output / "complete.json") + "\n")
    write_json(
        OUTPUT / "complete.json",
        {
            "version": VERSION,
            "artifact_hashes": {
                p.relative_to(OUTPUT).as_posix(): hash_file(p)
                for p in sorted(OUTPUT.rglob("*"))
                if p.is_file()
            },
        },
    )
    (OUTPUT / "complete.sha256").write_text(hash_file(OUTPUT / "complete.json") + "\n")
    verify_phase5()
    log(
        "phase5_complete",
        point_winner=summary["selected_candidate"],
        advancement_candidate=summary["advancement_candidate"],
        incremental_gates=summary["incremental_correction_gates"],
        calibration_or_test_access=False,
    )
    return 0


if __name__ == "__main__":
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=2):
        raise SystemExit(main())
