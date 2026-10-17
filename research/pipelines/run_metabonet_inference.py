"""Validation-only frozen Phase 3 comparison; all row-level outputs stay ignored."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import time
import zipfile
from collections import Counter
from dataclasses import replace
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from research.datasets.metabonet import window_to_example
from research.evaluation.refinement_metrics import event_metrics, summarize_records
from research.evaluation.statistics import paired_participant_interval
from research.models.adapters.chronos2 import (
    CHRONOS2_MODEL_REVISION,
    Chronos2ForecastAdapter,
)
from research.models.adapters.covariates import FEATURE_VERSION
from research.pipelines.prepare_metabonet import (
    ROOT,
    hash_file,
    iter_prepared_windows,
    log,
    verify_preparation,
    write_json,
)

VERSION = "metabonet_phase3_v1"
HISTORIES = (2, 6, 12, 24)
VARIANTS = {
    "persistence": (2, "c0"),
    **{f"chronos_c0_{h}h": (h, "c0") for h in HISTORIES},
    "chronos_c1_6h": (6, "c1"),
    "chronos_c2_6h": (6, "c2"),
}


def collect_validation(directory, *, reader=iter_prepared_windows):
    variants = {}
    eligible = {}
    for hours in HISTORIES:
        rows = list(reader(directory, split="validation", hours=hours, delay=5))
        by_id = {w["event_id"]: w for w in rows}
        if len(by_id) != len(rows) or any(w["split"] != "validation" for w in rows):
            raise ValueError("invalid validation identities or role")
        variants[hours] = by_id
        eligible[str(hours)] = {
            "event_count": len(rows),
            "subject_count": len({w["sid"] for w in rows}),
            "sources": dict(Counter(w["source"] for w in rows)),
        }
    common = set.intersection(*(set(v) for v in variants.values()))
    if not common:
        raise ValueError("no matched validation events")
    matched = {h: {key: variants[h][key] for key in sorted(common)} for h in HISTORIES}
    for key in sorted(common):
        reference = matched[2][key]
        for hours in HISTORIES:
            w = matched[hours][key]
            if (
                any(
                    w[name] != reference[name]
                    for name in ("sid", "source", "origin_ns", "truth", "meal_carbs_g")
                )
                or w["history"][-1] != reference["history"][-1]
            ):
                raise ValueError("matched histories disagree on identities, origins or targets")
    rows = list(matched[2].values())
    return matched, {
        "eligible_by_history": eligible,
        "matched_event_count": len(common),
        "matched_subject_count": len({w["sid"] for w in rows}),
        "matched_sources": dict(Counter(w["source"] for w in rows)),
        "matched_event_ids_sha256": hashlib.sha256(json.dumps(sorted(common)).encode()).hexdigest(),
        "roles_consumed": ["validation"],
    }


def request_for(window, variant):
    if variant not in VARIANTS or window["split"] != "validation":
        raise ValueError("unsupported inference variant or role")
    hours, context = VARIANTS[variant]
    if window["history_hours"] != hours:
        raise ValueError("history does not match inference variant")
    request = window_to_example(window, with_covariates=context != "c0").request
    if context != "c0":
        insulin = {
            "insulin_bolus",
            "insulin_basal",
            "insulin_bolus_record_present",
            "insulin_basal_record_present",
            "cgm_record_present",
        }
        if context == "c2":
            insulin |= {"previous_meal_carbohydrates", "previous_meal_carbohydrates_record_present"}
        request = replace(
            request,
            past_covariates=tuple(c for c in request.past_covariates if c.name in insulin),
            known_covariates=request.known_covariates if context == "c2" else (),
        )
    return request


def request_fingerprint(request):
    def series(items):
        return [
            (s.name, s.unit, [(p.timestamp.isoformat(), p.value) for p in s.points]) for s in items
        ]

    payload = {
        "checkpoint": CHRONOS2_MODEL_REVISION,
        "alignment": FEATURE_VERSION,
        "history": [(p.timestamp.isoformat(), p.value) for p in request.target_history],
        "past": series(request.past_covariates),
        "known": series(request.known_covariates),
        "horizon": request.prediction_length,
        "frequency": request.frequency_minutes,
        "quantiles": request.quantiles,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, allow_nan=False).encode()).hexdigest()


def evaluate_variant(windows, variant, predictor, path):
    expected = {key: request_for(w, variant) for key, w in windows.items()}
    rows = []
    if path.exists():
        try:
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            ids = [r["event_id"] for r in rows]
            if len(set(ids)) != len(ids) or any(key not in windows for key in ids):
                raise ValueError("unknown/duplicate progress identity")
            for row in rows:
                checksum = row.get("row_sha256")
                if checksum != record_checksum(row):
                    raise ValueError("changed progress record")
                w = windows[row["event_id"]]
                if (
                    row["request_sha256"] != request_fingerprint(expected[row["event_id"]])
                    or row["truth"] != w["truth"]
                    or row["participant_id"] != w["sid"]
                    or row["source"] != w["source"]
                ):
                    raise ValueError("changed progress input")
        except (ValueError, KeyError, TypeError) as error:
            raise ValueError("inference progress is corrupt or mismatched") from error
    seen = {r["event_id"] for r in rows}
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        for key in sorted(windows):
            if key in seen:
                continue
            window, request = windows[key], expected[key]
            row = {
                "event_id": key,
                "participant_id": window["sid"],
                "source": window["source"],
                "truth": window["truth"],
                "request_sha256": request_fingerprint(request),
                "prediction": [],
                "lower": [],
                "upper": [],
                "metrics": {},
                "error_type": None,
                "error_cause_type": None,
            }
            started = time.perf_counter()
            try:
                result = predictor(request)
                if hasattr(result, "median"):
                    row.update(
                        prediction=list(result.median),
                        lower=list(result.quantiles[0].values),
                        upper=list(result.quantiles[-1].values),
                    )
                else:
                    row["prediction"] = list(result)
                row["metrics"] = event_metrics(row["truth"], row["prediction"])
            except Exception as error:
                row.update(
                    prediction=[],
                    lower=[],
                    upper=[],
                    metrics={},
                    error_type=type(error).__name__,
                    error_cause_type=type(error.__cause__).__name__ if error.__cause__ else None,
                )
            row["wall_ms"] = (time.perf_counter() - started) * 1000
            row["row_sha256"] = record_checksum(row)
            stream.write(json.dumps(row, allow_nan=False) + "\n")
            stream.flush()
            rows.append(row)
            if len(rows) % 100 == 0:
                log("inference_progress", variant=variant, completed=len(rows), total=len(windows))
    return rows


def record_checksum(row):
    payload = {k: v for k, v in row.items() if k != "row_sha256"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, allow_nan=False).encode()).hexdigest()


def analyze_runs(runs, windows):
    runs = {
        name: [
            {**r, "metrics": event_metrics(r["truth"], r["prediction"])}
            if r["error_type"] is None
            else r
            for r in rows
        ]
        for name, rows in runs.items()
    }
    all_summary = summarize_records(runs)
    qualified = {
        name: rows for name, rows in runs.items() if all(r["error_type"] is None for r in rows)
    }
    if "persistence" not in qualified:
        raise ValueError("persistence failed; experiment cannot select a configuration")
    selection = summarize_records(qualified)

    def order(name):
        macro = selection["runs"][name]["participant_macro"]
        return macro["mae"], -macro["within_10"], name

    winner = min(qualified, key=order)
    c0 = [name for name in qualified if name.startswith("chronos_c0_")]
    best_history = min(c0, key=order) if c0 else None
    baseline = selection["runs"]["persistence"]
    chosen = selection["runs"][winner]
    macro, bm = chosen["participant_macro"], baseline["participant_macro"]
    improvement = 1 - macro["mae"] / bm["mae"] if bm["mae"] > 0 else 0
    pairs, intervals, bands = {}, {}, {}
    for name, rows in runs.items():
        pairs[name] = summarize_records({"persistence": runs["persistence"], name: rows})
        good = [r for r in rows if r["error_type"] is None]
        if good:
            intervals[name] = paired_participant_interval(
                rows, runs["persistence"], seed=20261016, samples=10000
            )
        band_rows = [
            r for r in good if len(r.get("lower", [])) == 24 and len(r.get("upper", [])) == 24
        ]
        bands[name] = {
            "native_band_event_count": len(band_rows),
            "coverage": sum(
                sum(lo <= y <= hi for lo, y, hi in zip(r["lower"], r["truth"], r["upper"]))
                for r in band_rows
            )
            / (24 * len(band_rows))
            if band_rows
            else None,
            "mean_width": sum(
                sum(hi - lo for lo, hi in zip(r["lower"], r["upper"])) for r in band_rows
            )
            / (24 * len(band_rows))
            if band_rows
            else None,
            "negative_prediction_points": sum(p < 0 for r in good for p in r["prediction"]),
            "failure_types": dict(Counter(r["error_type"] for r in rows if r["error_type"])),
        }
    sources = sorted({w["source"] for w in windows.values()})
    return {
        "all_run_summary": all_summary,
        "selection_summary": selection,
        "selected_frozen_candidate": winner,
        "selected_history_hours": VARIANTS[best_history][0] if best_history else 6,
        "history_selection_reason": "best failure-free C0 validation macro MAE"
        if best_history
        else "no failure-free C0; predeclared six-hour fallback",
        "selected_c0_candidate": best_history,
        "selection_gate": {
            "mae_improvement_fraction": improvement,
            "passes": bool(
                macro["mae"] <= 0.9 * bm["mae"]
                and macro["within_10"] >= bm["within_10"]
                and chosen["point_metrics"]["absolute_error_p95"]
                <= baseline["point_metrics"]["absolute_error_p95"]
            ),
        },
        "pairs": pairs,
        "paired_intervals": intervals,
        "native_bands": bands,
        "by_source": {
            source: summarize_records(
                {name: [r for r in rows if r["source"] == source] for name, rows in runs.items()}
            )
            for source in sources
        },
        "test_values_read": False,
        "weights_fitted": False,
        "limitation": "Validation-selected estimates are optimistic; isolated logged meals and unknown latency limit generalization.",
    }


def read_execution(directory):
    if (
        hash_file(directory / "execution.json")
        != (directory / "execution.sha256").read_text().strip()
    ):
        raise ValueError("frozen execution changed")
    value = json.loads((directory / "execution.json").read_text())
    if hash_file(directory / "execution-source.zip") != value["source_zip_sha256"]:
        raise ValueError("execution source snapshot changed")
    with zipfile.ZipFile(directory / "execution-source.zip") as snapshot:
        for name, expected in value["source_hashes"].items():
            if hashlib.sha256(snapshot.read(name)).hexdigest() != expected:
                raise ValueError("execution source snapshot changed")
    return value


def execution_guard(directory, configuration, sources):
    if (directory / "complete.json").exists():
        raise ValueError("completed inference cannot be replayed; use --verify-only")
    expected = {
        "configuration": configuration,
        "source_hashes": {name: hash_file(path) for name, path in sources.items()},
    }
    if (directory / "execution.json").exists():
        previous = read_execution(directory)
        if any(previous[key] != expected[key] for key in expected):
            raise ValueError("execution configuration/source changed; use a new versioned study")
        return previous
    if directory.exists() and any(directory.iterdir()):
        raise ValueError("incomplete execution initialization requires review")
    directory.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        directory / "execution-source.zip", "w", compression=zipfile.ZIP_DEFLATED
    ) as snapshot:
        for name, path in sources.items():
            snapshot.write(path, name)
    value = {
        **expected,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_zip_sha256": hash_file(directory / "execution-source.zip"),
    }
    with (directory / "execution.json").open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")
    (directory / "execution.sha256").write_text(hash_file(directory / "execution.json") + "\n")
    return value


def verify_completed(directory):
    if (
        hash_file(directory / "complete.json")
        != (directory / "complete.sha256").read_text().strip()
    ):
        raise ValueError("completion manifest changed")
    complete = json.loads((directory / "complete.json").read_text())
    read_execution(directory)
    for name, expected in complete["artifact_hashes"].items():
        path = (directory / name).resolve()
        if not path.is_relative_to(directory.resolve()) or hash_file(path) != expected:
            raise ValueError("completed inference artifact changed")
    return {"artifact_hashes_valid": True, "test_values_read": False, "weights_fitted": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prepared", type=Path, default=ROOT / "artifacts/evaluation-results/metabonet-phase2-v1"
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / "artifacts/evaluation-results/metabonet-phase3-v1"
    )
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    prepared, output = args.prepared.resolve(), args.output.resolve()
    if not output.is_relative_to(ROOT / "artifacts"):
        raise ValueError("health artifacts must remain under ignored artifacts/")
    if args.verify_only:
        log("verification", **verify_completed(output))
        return 0
    if (output / "complete.json").exists():
        raise ValueError("completed inference cannot be replayed; use --verify-only")
    verify_preparation(prepared)
    windows, cohort = collect_validation(prepared)
    if cohort["matched_event_count"] != 1509:
        raise ValueError("validation population differs from approved Phase 3 cohort")
    sources = {
        p.relative_to(ROOT).as_posix(): p
        for p in [
            Path(__file__),
            ROOT / "research/datasets/metabonet.py",
            ROOT / "research/datasets/t1d_uom.py",
            ROOT / "research/pipelines/prepare_metabonet.py",
            ROOT / "research/evaluation/refinement_metrics.py",
            ROOT / "research/evaluation/statistics.py",
            ROOT / "research/models/adapters/base.py",
            ROOT / "research/models/adapters/chronos2.py",
            ROOT / "research/models/adapters/covariates.py",
            ROOT / "docs/planning/GlycoLens_13_MetaboNet_Frozen_Inference.md",
            ROOT / "pyproject.toml",
            ROOT / "uv.lock",
        ]
    }
    cache = ROOT / "artifacts/models/huggingface"
    snapshot = cache / "models--amazon--chronos-2/snapshots" / CHRONOS2_MODEL_REVISION
    configuration = {
        "version": VERSION,
        "checkpoint": CHRONOS2_MODEL_REVISION,
        "checkpoint_files": {
            name: hash_file(snapshot / name) for name in ("config.json", "model.safetensors")
        },
        "preparation_protocol_sha256": hash_file(prepared / "frozen-protocol.json"),
        "cohort": cohort,
        "variants": {k: list(v) for k, v in VARIANTS.items()},
        "python": platform.python_version(),
        "packages": {p: version(p) for p in ("numpy", "torch", "chronos-forecasting", "duckdb")},
        "threads": 2,
        "seed": 20261016,
        "offline": True,
        "quantiles": [0.1, 0.5, 0.9],
        "alignment": FEATURE_VERSION,
        "candidate_batch_size": 1,
        "calibration_or_test_access": False,
    }
    execution_guard(output, configuration, sources)
    write_json(output / "validation-cohort.json", cohort)
    log("validation_ready", **cohort)
    import torch

    torch.set_num_threads(2)
    torch.manual_seed(20261016)
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    adapter = Chronos2ForecastAdapter(cache_dir=cache)
    adapter.load()
    runs = {}
    started = time.perf_counter()
    for name, (hours, _) in VARIANTS.items():
        predictor = (
            (lambda r: [r.target_history[-1].value] * r.prediction_length)
            if name == "persistence"
            else adapter.predict
        )
        runs[name] = evaluate_variant(windows[hours], name, predictor, output / f"{name}.jsonl")
        log(
            "variant_complete",
            variant=name,
            attempts=len(runs[name]),
            failures=sum(r["error_type"] is not None for r in runs[name]),
        )
    result = analyze_runs(runs, windows[2])
    result["elapsed_seconds"] = time.perf_counter() - started
    write_json(output / "summary.json", result)
    write_json(
        output / "history-decision.json",
        {
            "version": VERSION,
            "scope": "validation only; not a final model/test selection",
            "history_hours": result["selected_history_hours"],
            "selected_c0_candidate": result["selected_c0_candidate"],
            "selected_frozen_candidate": result["selected_frozen_candidate"],
            "summary_sha256": hash_file(output / "summary.json"),
            "execution_sha256": hash_file(output / "execution.json"),
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
    log(
        "phase3_complete",
        selected_frozen_candidate=result["selected_frozen_candidate"],
        history_hours=result["selected_history_hours"],
        gate=result["selection_gate"],
        **verify_completed(output),
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        log("phase3_failed", error_type=type(error).__name__)
        raise SystemExit(1) from None
