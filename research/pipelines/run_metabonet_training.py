"""Phase 4 subject-CV direct training; validation follows frozen CV choices only."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from collections import Counter, defaultdict
from importlib.metadata import version
from pathlib import Path

import joblib
import numpy as np

from research.datasets.metabonet import window_to_example
from research.evaluation.refinement_metrics import event_metrics, summarize_records
from research.evaluation.statistics import paired_participant_interval
from research.models.adapters.metabonet_tabular import (
    FEATURE_VERSION,
    MetaboNetTabularAdapter,
    request_features,
)
from research.pipelines.prepare_metabonet import (
    ROOT,
    hash_file,
    iter_prepared_windows,
    log,
    verify_preparation,
    write_json,
)
from research.pipelines.run_metabonet_inference import (
    HISTORIES,
    VARIANTS,
    collect_validation,
    execution_guard,
    read_execution,
    record_checksum,
    request_fingerprint,
    verify_completed,
)

VERSION = "metabonet_phase4_v1"
GRID = [
    {
        "name": f"{algorithm}_{hours}h_{profile}_{parameter}",
        "algorithm": algorithm,
        "history_hours": hours,
        "profile": profile,
        "parameter": parameter,
    }
    for algorithm in ("ridge", "lightgbm")
    for hours in HISTORIES
    for profile in ("cgm", "events")
    for parameter in ((10, 1000) if algorithm == "ridge" else (15, 31))
]


def collect_training(directory, *, reader=iter_prepared_windows):
    data = {}
    counts = {}
    for hours in HISTORIES:
        rows = list(reader(directory, split="train", hours=hours, delay=5))
        if any(w["split"] != "train" for w in rows):
            raise ValueError("nontraining role in model development")
        by_id = {w["event_id"]: w for w in rows}
        if len(by_id) != len(rows):
            raise ValueError("duplicate training event")
        data[hours] = by_id
        counts[str(hours)] = {"events": len(rows), "subjects": len({w["sid"] for w in rows})}
    common = set.intersection(*(set(v) for v in data.values()))
    if not common:
        raise ValueError("no common training events")
    for key in common:
        reference = data[2][key]
        for hours in HISTORIES:
            if any(
                data[hours][key][field] != reference[field]
                for field in ("sid", "source", "origin_ns", "truth")
            ):
                raise ValueError("training histories disagree on targets or identity")
    reference = [data[2][key] for key in sorted(common)]
    return data, {
        "eligible_by_history": counts,
        "common_event_count": len(common),
        "common_subject_count": len({w["sid"] for w in reference}),
        "common_sources": dict(Counter(w["source"] for w in reference)),
        "common_ids_sha256": hashlib.sha256(json.dumps(sorted(common)).encode()).hexdigest(),
        "roles_consumed_for_cv": ["train"],
    }


def subject_folds(rows):
    sources = {}
    for row in rows:
        if row["sid"] in sources and sources[row["sid"]] != row["source"]:
            raise ValueError("subject has conflicting source provenance")
        sources[row["sid"]] = row["source"]
    result = {}
    for source in sorted(set(sources.values())):
        subjects = sorted(
            (s for s in sources if sources[s] == source),
            key=lambda s: hashlib.sha256(f"20261016|{s}".encode()).digest(),
        )
        if len(subjects) < 3:
            raise ValueError("insufficient subjects for three source-stratified folds")
        result.update({subject: i % 3 for i, subject in enumerate(subjects)})
    return result


def participant_weights(subjects):
    counts = Counter(subjects)
    return np.array([len(subjects) / (len(counts) * counts[s]) for s in subjects], dtype=float)


def choose_cv(results, algorithm):
    eligible = [r for r in results if r["algorithm"] == algorithm and r["failure_count"] == 0]
    if not eligible:
        raise ValueError("no eligible candidate in model family")
    return min(eligible, key=lambda r: (r["macro_mae"], -r["within_10"], r["name"]))


def freeze_json(path, value):
    payload = {**value, "row_sha256": record_checksum(value)}
    if path.exists():
        previous = json.loads(path.read_text())
        if previous != payload:
            raise ValueError("frozen training decision changed")
    else:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n")
    return payload


def frame(windows, history_hours, profile):
    ids = sorted(windows)
    requests = [window_to_example(windows[key], with_covariates=True).request for key in ids]
    features = [request_features(r, history_hours=history_hours, profile=profile) for r in requests]
    if any(f[1] != features[0][1] for f in features):
        raise ValueError("feature names changed within a frame")
    return {
        "ids": ids,
        "subjects": [windows[key]["sid"] for key in ids],
        "x": np.stack([f[0] for f in features]),
        "y": np.array([windows[key]["truth"] for key in ids], dtype=float),
        "current": np.array([r.target_history[-1].value for r in requests]),
        "feature_names": features[0][1],
    }


def macro_score(truth, prediction, subjects):
    mae = np.abs(truth - prediction).mean(axis=1)
    tolerance = (np.abs(truth - prediction) <= 10).mean(axis=1)
    groups = defaultdict(list)
    for i, sid in enumerate(subjects):
        groups[sid].append(i)
    return float(np.mean([mae[g].mean() for g in groups.values()])), float(
        np.mean([tolerance[g].mean() for g in groups.values()])
    )


def cross_validate(config, values, folds, output, execution_sha):
    path = output / f"cv-{config['name']}.json"
    predictions_path = output / f"cv-{config['name']}.npy"
    if path.exists():
        result = json.loads(path.read_text())
        if (
            result.get("row_sha256") != record_checksum(result)
            or result["execution_sha256"] != execution_sha
            or result["configuration"] != config
            or hash_file(predictions_path) != result["prediction_sha256"]
        ):
            raise ValueError("CV progress changed")
        return result
    if predictions_path.exists():
        raise ValueError("partial CV output requires review")
    assignments = np.array([folds[s] for s in values["subjects"]])
    prediction = np.full_like(values["y"], np.nan)
    errors = []
    started = time.perf_counter()
    for fold in range(3):
        fit = np.flatnonzero(assignments != fold)
        held = np.flatnonzero(assignments == fold)
        fit_subjects = [values["subjects"][i] for i in fit]
        if not len(held) or set(fit_subjects) & {values["subjects"][i] for i in held}:
            raise ValueError("cross-validation subject leakage or empty fold")
        try:
            model = MetaboNetTabularAdapter(**{k: v for k, v in config.items() if k != "name"})
            model.fit_arrays(
                values["x"][fit],
                values["y"][fit],
                values["current"][fit],
                sample_weight=participant_weights(fit_subjects),
            )
            prediction[held] = model.predict_array(values["x"][held], values["current"][held])
        except Exception as error:
            errors.append({"fold": fold, "error_type": type(error).__name__})
        log("cv_fold_complete", candidate=config["name"], fold=fold, failures=len(errors))
    good = np.isfinite(prediction).all(axis=1)
    score = macro_score(values["y"], prediction, values["subjects"]) if good.all() else (None, None)
    with predictions_path.open("xb") as stream:
        np.save(stream, prediction, allow_pickle=False)
    result = {
        **config,
        "configuration": config,
        "failure_count": len(errors) + int(not good.all() and not errors),
        "fold_errors": errors,
        "oof_events": len(prediction),
        "valid_oof_events": int(good.sum()),
        "macro_mae": score[0],
        "within_10": score[1],
        "execution_sha256": execution_sha,
        "prediction_sha256": hash_file(predictions_path),
        "elapsed_seconds": time.perf_counter() - started,
    }
    return freeze_json(path, result)


def fit_final(config, values, output, execution_sha):
    path = output / f"model-{config['algorithm']}.joblib"
    metadata_path = output / f"model-{config['algorithm']}.json"
    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text())
        if (
            metadata.get("row_sha256") != record_checksum(metadata)
            or metadata["model_sha256"] != hash_file(path)
            or metadata["execution_sha256"] != execution_sha
            or metadata["configuration"] != config
        ):
            raise ValueError("saved model or fit metadata changed")
        model = joblib.load(path)  # Trusted local bytes checked against their frozen hash first.
        return model, metadata
    if path.exists():
        raise ValueError("partial model save requires review")
    model = MetaboNetTabularAdapter(**{k: v for k, v in config.items() if k != "name"})
    started = time.perf_counter()
    model.fit_arrays(
        values["x"],
        values["y"],
        values["current"],
        sample_weight=participant_weights(values["subjects"]),
    )
    before = model.predict_array(values["x"][:10], values["current"][:10])
    joblib.dump(model, path)
    digest = hash_file(path)
    restored = joblib.load(path)
    after = restored.predict_array(values["x"][:10], values["current"][:10])
    if not np.allclose(before, after, rtol=0, atol=1e-10):
        raise ValueError("saved model reload changes predictions")
    metadata = {
        "configuration": config,
        "execution_sha256": execution_sha,
        "model_sha256": digest,
        "training_events": len(values["ids"]),
        "training_subjects": len(set(values["subjects"])),
        "feature_count": values["x"].shape[1],
        "feature_names_sha256": hashlib.sha256(
            json.dumps(values["feature_names"]).encode()
        ).hexdigest(),
        "reload_prediction_equivalent": True,
        "fit_elapsed_seconds": time.perf_counter() - started,
    }
    return restored, freeze_json(metadata_path, metadata)


def evaluate_direct(model, config, windows, output, model_sha):
    path = output / f"validation-{config['algorithm']}.jsonl"
    metadata_path = output / f"validation-{config['algorithm']}.json"
    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text())
        if (
            metadata.get("row_sha256") != record_checksum(metadata)
            or metadata["model_sha256"] != model_sha
            or metadata["predictions_sha256"] != hash_file(path)
        ):
            raise ValueError("validation progress changed")
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        if any(r.get("row_sha256") != record_checksum(r) for r in rows):
            raise ValueError("validation record changed")
        return rows, metadata
    if path.exists():
        raise ValueError("partial validation output requires review")
    values = frame(windows, config["history_hours"], config["profile"])
    started = time.perf_counter()
    error_type = None
    try:
        predictions = model.predict_array(values["x"], values["current"])
    except Exception as error:
        predictions = None
        error_type = type(error).__name__
    elapsed = (time.perf_counter() - started) * 1000
    rows = []
    with path.open("x", encoding="utf-8") as stream:
        for index, key in enumerate(values["ids"]):
            window = windows[key]
            prediction = [float(v) for v in predictions[index]] if predictions is not None else []
            row = {
                "event_id": key,
                "participant_id": window["sid"],
                "source": window["source"],
                "truth": window["truth"],
                "prediction": prediction,
                "lower": [],
                "upper": [],
                "metrics": event_metrics(window["truth"], prediction) if error_type is None else {},
                "error_type": error_type,
                "wall_ms": 0,
                "timing": "batch; per-event latency not measured",
                "model_sha256": model_sha,
                "request_sha256": request_fingerprint(
                    window_to_example(window, with_covariates=True).request
                ),
            }
            row["row_sha256"] = record_checksum(row)
            stream.write(json.dumps(row, allow_nan=False) + "\n")
            rows.append(row)
    metadata = {
        "model_sha256": model_sha,
        "predictions_sha256": hash_file(path),
        "batch_prediction_ms": elapsed,
        "event_count": len(rows),
        "error_type": error_type,
        "interval": "none",
    }
    return rows, freeze_json(metadata_path, metadata)


def compare(runs, windows):
    all_summary = summarize_records(runs)
    qualified = {
        name: rows for name, rows in runs.items() if all(r["error_type"] is None for r in rows)
    }
    primary = summarize_records(qualified)
    choices = [
        {
            "name": name,
            "algorithm": "comparison",
            "failure_count": 0,
            "macro_mae": v["participant_macro"]["mae"],
            "within_10": v["participant_macro"]["within_10"],
        }
        for name, v in primary["runs"].items()
    ]
    winner = choose_cv(choices, "comparison")["name"]
    baseline = primary["runs"]["persistence"]
    selected = primary["runs"][winner]
    m, bm = selected["participant_macro"], baseline["participant_macro"]
    pairs = {
        name: summarize_records({"persistence": runs["persistence"], name: rows})
        for name, rows in runs.items()
    }
    for table in [all_summary, primary, *pairs.values()]:
        for name, item in table["runs"].items():
            if name in ("ridge_direct", "lightgbm_direct"):
                item["wall_p95_ms"] = None
    by_source = {
        source: summarize_records(
            {name: [r for r in rows if r["source"] == source] for name, rows in runs.items()}
        )
        for source in sorted({w["source"] for w in windows.values()})
    }
    for table in by_source.values():
        for name, item in table["runs"].items():
            if name in ("ridge_direct", "lightgbm_direct"):
                item["wall_p95_ms"] = None
    return {
        "selected_candidate": winner,
        "selection_summary": primary,
        "all_run_summary": all_summary,
        "pairs": pairs,
        "selection_gate": {
            "mae_improvement_fraction": 1 - m["mae"] / bm["mae"],
            "passes": bool(
                m["mae"] <= 0.9 * bm["mae"]
                and m["within_10"] >= bm["within_10"]
                and selected["point_metrics"]["absolute_error_p95"]
                <= baseline["point_metrics"]["absolute_error_p95"]
            ),
        },
        "paired_intervals": {
            name: paired_participant_interval(
                rows, runs["persistence"], seed=20261016, samples=10000
            )
            for name, rows in runs.items()
            if any(r["error_type"] is None for r in rows)
        },
        "negative_prediction_points": {
            name: sum(p < 0 for r in rows if r["error_type"] is None for p in r["prediction"])
            for name, rows in runs.items()
        },
        "by_source": by_source,
        "weights_fitted": True,
        "calibration_or_test_access": False,
        "uncertainty": "direct model fields are deterministic placeholders; no calibrated intervals",
    }


def verify_training_completed(directory):
    verify_completed(directory)  # Reuse integrity checks, not Phase 3's inference-only flags.
    execution = read_execution(directory)
    summary = json.loads((directory / "summary.json").read_text())
    if (
        execution["configuration"]["version"] != VERSION
        or summary.get("weights_fitted") is not True
        or summary.get("calibration_or_test_access") is not False
        or set(summary.get("fit_metadata", {})) != {"ridge", "lightgbm"}
    ):
        raise ValueError("completed study is not the expected training protocol")
    return {
        "artifact_hashes_valid": True,
        "weights_fitted": True,
        "calibration_or_test_access": False,
        "saved_model_count": 2,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prepared", type=Path, default=ROOT / "artifacts/evaluation-results/metabonet-phase2-v1"
    )
    parser.add_argument(
        "--phase3", type=Path, default=ROOT / "artifacts/evaluation-results/metabonet-phase3-v1"
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / "artifacts/evaluation-results/metabonet-phase4-v1"
    )
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    prepared, phase3, output = args.prepared.resolve(), args.phase3.resolve(), args.output.resolve()
    if not output.is_relative_to(ROOT / "artifacts"):
        raise ValueError("health artifacts must remain under ignored artifacts/")
    if args.verify_only:
        log("verification", **verify_training_completed(output))
        return 0
    if (output / "complete.json").exists():
        raise ValueError("completed training cannot be replayed; use --verify-only")
    verify_preparation(prepared)
    verify_completed(phase3)
    training, cohort = collect_training(prepared)
    common = set.intersection(*(set(v) for v in training.values()))
    common_ids = sorted(common)
    folds = subject_folds([training[2][key] for key in common_ids])
    sources = {
        p.relative_to(ROOT).as_posix(): p
        for p in [
            Path(__file__),
            ROOT / "research/models/adapters/metabonet_tabular.py",
            ROOT / "research/models/adapters/base.py",
            ROOT / "research/datasets/metabonet.py",
            ROOT / "research/datasets/t1d_uom.py",
            ROOT / "research/pipelines/prepare_metabonet.py",
            ROOT / "research/pipelines/run_metabonet_inference.py",
            ROOT / "research/evaluation/refinement_metrics.py",
            ROOT / "research/evaluation/statistics.py",
            ROOT / "docs/planning/GlycoLens_14_MetaboNet_Direct_Models.md",
            ROOT / "pyproject.toml",
            ROOT / "uv.lock",
        ]
    }
    configuration = {
        "version": VERSION,
        "feature_version": FEATURE_VERSION,
        "grid": GRID,
        "training_cohort": cohort,
        "fold_assignment_sha256": hashlib.sha256(
            json.dumps(folds, sort_keys=True).encode()
        ).hexdigest(),
        "preparation_sha256": hash_file(prepared / "frozen-protocol.json"),
        "phase3_completion_sha256": hash_file(phase3 / "complete.json"),
        "python": platform.python_version(),
        "packages": {
            p: version(p) for p in ("numpy", "scikit-learn", "lightgbm", "joblib", "duckdb")
        },
        "seed": 20261016,
        "threads": 2,
        "folds": 3,
        "validation_access_before_cv_selection": False,
        "calibration_or_test_access": False,
    }
    execution_guard(output, configuration, sources)
    execution_sha = hash_file(output / "execution.json")
    freeze_json(output / "training-cohort.json", cohort)
    freeze_json(output / "subject-folds.json", folds)
    log("training_ready", **cohort)
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=2):
        started = time.perf_counter()
        cached = {}
        results = []
        for config in GRID:
            key = (config["history_hours"], config["profile"])
            if key not in cached:
                cached[key] = frame({i: training[key[0]][i] for i in common_ids}, *key)
            result = cross_validate(config, cached[key], folds, output, execution_sha)
            results.append(result)
            log(
                "cv_candidate_complete",
                candidate=config["name"],
                completed=len(results),
                total=len(GRID),
                macro_mae=result["macro_mae"],
                failures=result["failure_count"],
            )
        selected = {
            algorithm: choose_cv(results, algorithm)["configuration"]
            for algorithm in ("ridge", "lightgbm")
        }
        freeze_json(
            output / "cv-selection.json",
            {
                "version": VERSION,
                "choices": selected,
                "execution_sha256": execution_sha,
                "selection_inputs": "training out-of-fold only",
            },
        )
        write_json(
            output / "cv-summary.json",
            {"candidates": results, "selection": selected, "training_cohort": cohort},
        )
        log("cv_selection_frozen", choices=selected)
        models = {}
        fit_metadata = {}
        for algorithm, config in selected.items():
            values = frame(
                training[config["history_hours"]], config["history_hours"], config["profile"]
            )
            models[algorithm], fit_metadata[algorithm] = fit_final(
                config, values, output, execution_sha
            )
            log(
                "final_model_fit",
                algorithm=algorithm,
                events=len(values["ids"]),
                subjects=len(set(values["subjects"])),
                reload_equivalent=True,
            )
        # This is the first prepared-validation read. All per-family choices/models are frozen.
        validation, validation_cohort = collect_validation(prepared)
        if validation_cohort["matched_event_count"] != 1509:
            raise ValueError("validation differs from frozen primary comparison")
        train_subjects = {w["sid"] for group in training.values() for w in group.values()}
        if train_subjects & {w["sid"] for w in validation[2].values()}:
            raise ValueError("training/validation subject leakage")
        write_json(output / "validation-cohort.json", validation_cohort)
        runs = {}
        for name in VARIANTS:
            rows = [
                json.loads(line) for line in (phase3 / f"{name}.jsonl").read_text().splitlines()
            ]
            if any(r.get("row_sha256") != record_checksum(r) for r in rows):
                raise ValueError("Phase 3 saved row changed")
            for row in rows:
                w = validation[2][row["event_id"]]
                if (
                    row["truth"] != w["truth"]
                    or row["participant_id"] != w["sid"]
                    or row["source"] != w["source"]
                ):
                    raise ValueError("baseline reuse has mismatched targets/identities")
            runs[name] = rows
        validation_metadata = {}
        for algorithm, model in models.items():
            config = selected[algorithm]
            runs[algorithm + "_direct"], validation_metadata[algorithm] = evaluate_direct(
                model,
                config,
                validation[config["history_hours"]],
                output,
                fit_metadata[algorithm]["model_sha256"],
            )
        summary = compare(runs, validation[2])
        summary.update(
            training_cohort=cohort,
            validation_cohort=validation_cohort,
            cv_selection=selected,
            fit_metadata=fit_metadata,
            validation_metadata=validation_metadata,
            elapsed_seconds=time.perf_counter() - started,
        )
        write_json(output / "summary.json", summary)
        write_json(
            output / "model-selection.json",
            {
                "version": VERSION,
                "scope": "validation selection before residual comparison and independent testing",
                "selected_candidate": summary["selected_candidate"],
                "cv_choices": selected,
                "summary_sha256": hash_file(output / "summary.json"),
            },
        )
        write_json(
            output / "complete.json",
            {
                "artifact_hashes": {
                    p.relative_to(output).as_posix(): hash_file(p)
                    for p in sorted(output.iterdir())
                    if p.is_file()
                }
            },
        )
        (output / "complete.sha256").write_text(hash_file(output / "complete.json") + "\n")
        verify_training_completed(output)
        log(
            "phase4_complete",
            selected_candidate=summary["selected_candidate"],
            gate=summary["selection_gate"],
            weights_fitted=True,
            calibration_or_test_access=False,
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        log("phase4_failed", error_type=type(error).__name__)
        raise SystemExit(1) from None
