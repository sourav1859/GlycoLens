"""Approved CPU refinement study. All row-level outputs stay in ignored artifacts.

Run from repository root with --uom-root. The original M2 artifacts are read-only.
External evaluation is permitted only after an immutable selection is written.
Resuming uses request-only cache keys tied to the pinned frozen checkpoint.
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import os
import platform
import time
from collections import Counter, defaultdict
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from importlib.metadata import version
from pathlib import Path

import joblib
import numpy as np

from research.datasets.azt1d import DOI as AZT_DOI, canonical_files, load_records
from research.datasets.t1d_uom import (
    WindowConfig,
    WindowRejected,
    build_meal_window,
    load_participant,
)
from research.evaluation.protocol import event_id
from research.evaluation.refinement_data import calibration_assignments, enriched_request
from research.evaluation.refinement_metrics import event_metrics, summarize_records
from research.models.adapters.chronos2 import Chronos2ForecastAdapter, CHRONOS2_MODEL_REVISION
from research.models.adapters.converters import (
    ContextConfiguration,
    meal_window_to_forecast_example,
)
from research.models.adapters.tabular import TabularForecastAdapter

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "artifacts/evaluation-results/refinement-v1"
HISTORIES = (2, 6, 12, 24)


def digest(path):
    with Path(path).open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def log(stage, **values):
    print(json.dumps({"stage": stage, **values}), flush=True)


def request_key(request):
    # No target/subject/covariates enter a C0 cache key.
    payload = (
        CHRONOS2_MODEL_REVISION,
        request.prediction_length,
        request.frequency_minutes,
        [(p.timestamp.isoformat(), p.value) for p in request.target_history],
    )
    return hashlib.sha256(json.dumps(payload).encode()).hexdigest()


class FrozenChronos:
    def __init__(self, path):
        self.path = path
        self.cache = json.loads(path.read_text()) if path.exists() else {}
        self.adapter = None

    def result(self, request):
        key = request_key(request)
        if key not in self.cache:
            if self.adapter is None:
                os.environ["HF_HUB_OFFLINE"] = "1"
                self.adapter = Chronos2ForecastAdapter(
                    cache_dir=ROOT / "artifacts/models/huggingface"
                )
                self.adapter.load()
            # Strip enriched features: frozen C0 is exactly CGM-only.
            c0 = replace(request, past_covariates=(), known_covariates=())
            result = self.adapter.predict(c0)
            self.cache[key] = {
                "prediction": list(result.median),
                "wall_ms": result.latency_ms,
                "lower": list(result.quantiles[0].values),
                "upper": list(result.quantiles[-1].values),
            }
            if len(self.cache) % 50 == 0:
                self.flush()
        return self.cache[key]

    def __call__(self, request):
        return self.result(request)["prediction"]

    def flush(self):
        write_json(self.path, self.cache)


def sliced_window(participant, meal, hours, times=None):
    times = times or [p.timestamp for p in participant.glucose]
    start = bisect.bisect_left(times, meal.timestamp - timedelta(hours=hours, minutes=15))
    end = bisect.bisect_right(times, meal.timestamp + timedelta(minutes=125))
    sliced = replace(participant, glucose=participant.glucose[start:end])
    return build_meal_window(sliced, meal, WindowConfig(history_minutes=hours * 60))


def sample(window, participant, identity, split, *, external=False):
    return {
        "event_id": identity,
        "participant_id": participant.participant_id,
        "split": split,
        "c0": meal_window_to_forecast_example(
            window, context=ContextConfiguration.CGM_ONLY
        ).request,
        "shared": enriched_request(window, participant, full_nutrition=False),
        "full": None if external else enriched_request(window, participant, full_nutrition=True),
        "truth": [p.glucose_mg_dl for p in window.target_cgm],
    }


def prepare_uom(root, manifest):
    assignments = calibration_assignments(manifest)
    subjects = defaultdict(dict)
    for entry in manifest:
        subjects[entry["participant_id"]][entry["meal_at"]] = entry
    samples = {h: [] for h in HISTORIES}
    rejected = {h: Counter() for h in HISTORIES}
    for subject, entries in subjects.items():
        participant = load_participant(root, subject)
        times = [p.timestamp for p in participant.glucose]
        for meal in participant.meals:
            entry = entries.get(meal.timestamp.isoformat())
            if entry is None or assignments[entry["event_id"]] == "purged_boundary":
                continue
            for hours in HISTORIES:
                try:
                    window = sliced_window(participant, meal, hours, times)
                except WindowRejected as error:
                    rejected[hours][error.reason] += 1
                    continue
                if event_id(window) != entry["event_id"]:
                    raise ValueError("original M2 event identity changed")
                samples[hours].append(
                    sample(window, participant, entry["event_id"], assignments[entry["event_id"]])
                )
    counts = {str(h): dict(Counter(s["split"] for s in rows)) for h, rows in samples.items()}
    if len(samples[2]) != sum(v != "purged_boundary" for v in assignments.values()):
        raise ValueError("two-hour cohort failed to reproduce original eligible events")
    return samples, {
        "eligible_by_history_split": counts,
        "rejected_by_history": {str(h): dict(c) for h, c in rejected.items()},
        "split_counts": dict(Counter(assignments.values())),
    }


def evaluate(samples, predictor, feature="c0"):
    rows = []
    for s in samples:
        row = {k: s[k] for k in ("event_id", "participant_id", "truth")}
        started = time.perf_counter()
        try:
            prediction = predictor(s[feature])
            if isinstance(prediction, dict):
                row.update(prediction)
            elif hasattr(prediction, "median"):
                row.update(
                    prediction=list(prediction.median),
                    wall_ms=prediction.latency_ms,
                    lower=list(prediction.quantiles[0].values),
                    upper=list(prediction.quantiles[-1].values),
                )
            else:
                row.update(
                    prediction=list(prediction), wall_ms=(time.perf_counter() - started) * 1000
                )
            row["metrics"] = event_metrics(row["truth"], row["prediction"])
            row["error_type"] = None
        except Exception as error:
            # Persist failure type, never raw backend messages or records.
            row.update(prediction=[], metrics={}, error_type=type(error).__name__, wall_ms=0)
        rows.append(row)
    return rows


def persistence(request):
    return [request.target_history[-1].value] * request.prediction_length


def rank(summary, names):
    eligible = [name for name in names if summary["runs"][name]["failure_count"] == 0]
    if not eligible:
        raise ValueError("no failure-free candidate available for selection")
    return min(
        eligible,
        key=lambda n: (
            summary["runs"][n]["participant_macro"]["mae"],
            -summary["runs"][n]["participant_macro"]["within_10"],
            n,
        ),
    )


def intervals(calibration_rows, evaluation_rows):
    successful = [r for r in calibration_rows if r["error_type"] is None]
    if len(successful) < 5:
        return {"available": False, "calibration_count": len(successful)}
    errors = np.array([np.abs(np.array(r["truth"]) - r["prediction"]) for r in successful])
    level = min(1, np.ceil((len(errors) + 1) * 0.8) / len(errors))
    radii = np.quantile(errors, level, axis=0, method="higher")
    groups = defaultdict(list)
    for row in evaluation_rows:
        if row["error_type"] is None:
            groups[row["participant_id"]].append(
                float(np.mean(np.abs(np.array(row["truth"]) - row["prediction"]) <= radii))
            )
    return {
        "available": True,
        "nominal_coverage": 0.8,
        "calibration_count": len(successful),
        "participant_macro_coverage": float(np.mean([np.mean(g) for g in groups.values()])),
        "mean_width_mg_dl": float(np.mean(2 * radii)),
        "radii": radii.tolist(),
    }


def improvement_gate(summary, winner):
    baseline = summary["runs"]["persistence"]
    selected = summary["runs"][winner]
    return {
        "mae_improvement_fraction": 1
        - selected["participant_macro"]["mae"] / baseline["participant_macro"]["mae"],
        "passes": bool(
            selected["participant_macro"]["mae"] <= 0.9 * baseline["participant_macro"]["mae"]
            and selected["participant_macro"]["within_10"]
            >= baseline["participant_macro"]["within_10"]
            and selected["point_metrics"]["absolute_error_p95"]
            <= baseline["point_metrics"]["absolute_error_p95"]
        ),
    }


def paired_bootstrap(rows, baseline):
    by_id = {r["event_id"]: r for r in baseline if r["error_type"] is None}
    groups = defaultdict(list)
    for row in rows:
        if row["error_type"] is None and row["event_id"] in by_id:
            groups[row["participant_id"]].append(
                row["metrics"]["mae"] - by_id[row["event_id"]]["metrics"]["mae"]
            )
    deltas = np.array([np.mean(g) for g in groups.values()])
    rng = np.random.default_rng(20261016)
    boot = rng.choice(deltas, size=(10000, len(deltas)), replace=True).mean(axis=1)
    return {
        "participant_count": len(deltas),
        "mae_delta": float(deltas.mean()),
        "ci95": [float(v) for v in np.quantile(boot, [0.025, 0.975])],
        "method": "participant-cluster bootstrap, 10000 draws, seed 20261016",
    }


def freeze_selection(path, selection):
    if path.exists():
        previous = json.loads(path.read_text())
        if {k: v for k, v in previous.items() if k != "frozen_at_utc"} != selection:
            raise ValueError("selection already frozen; use a new versioned protocol for changes")
        return previous
    value = {**selection, "frozen_at_utc": datetime.now(timezone.utc).isoformat()}
    # Exclusive create prevents a later run silently replacing an external-test selection.
    with path.open("x", encoding="utf-8") as target:
        json.dump(value, target, indent=2, sort_keys=True)
    return value


def prepare_external(root, hours, uom_samples):
    rows, audit, rejections = [], Counter(), Counter()

    # Exact aligned history+truth fingerprint check, independent of source event IDs.
    def fingerprint(s):
        return hashlib.sha256(
            json.dumps(
                [round(p.value, 4) for p in s["c0"].target_history]
                + [round(v, 4) for v in s["truth"]]
            ).encode()
        ).hexdigest()

    known = {fingerprint(s) for s in uom_samples}
    observed = set()
    for path in canonical_files(root):
        participant, counts = load_records(path)
        audit.update(counts)
        audit["participants"] += 1
        times = [p.timestamp for p in participant.glucose]
        for meal in participant.meals:
            try:
                window = sliced_window(participant, meal, hours, times)
            except WindowRejected as error:
                rejections[error.reason] += 1
                continue
            identity = hashlib.sha256(
                f"{AZT_DOI}|{participant.participant_id}|{meal.timestamp.isoformat()}".encode()
            ).hexdigest()
            s = sample(window, participant, identity, "external", external=True)
            key = fingerprint(s)
            if key in known or key in observed:
                raise ValueError("duplicate trajectory found across cohorts or external events")
            observed.add(key)
            rows.append(s)
    return rows, {
        "source_audit": dict(audit),
        "rejections": dict(rejections),
        "eligible_events": len(rows),
        "eligible_participants": len({s["participant_id"] for s in rows}),
        "exact_trajectory_overlap_count": 0,
        "overlap_limitation": "exact rounded trajectory check cannot prove absence of shared people",
    }


def legacy_audit(samples, original, output):
    adapter = Chronos2ForecastAdapter(cache_dir=ROOT / "artifacts/models/huggingface")
    os.environ["HF_HUB_OFFLINE"] = "1"
    adapter.load()
    rows = []
    for s in samples:
        # Full legacy C3 requests are reconstructed separately by prepare_legacy.
        rows.extend(evaluate([s], adapter.predict, "legacy"))
    reference = {r["event_id"]: r for r in original if r["error_type"] is None}
    differences = [
        abs(r["metrics"]["mae"] - reference[r["event_id"]]["metrics"]["mae"])
        for r in rows
        if r["error_type"] is None and r["event_id"] in reference
    ]
    success = [r for r in rows if r["error_type"] is None]
    largest = max(success, key=lambda r: r["metrics"]["max_absolute_error"])
    audit = {
        "matched_reference_count": len(differences),
        "maximum_mae_reproduction_difference": max(differences),
        "failure_count": len(rows) - len(success),
        "prediction_min": min(v for r in success for v in r["prediction"]),
        "prediction_max": max(v for r in success for v in r["prediction"]),
        "truth_min": min(v for r in success for v in r["truth"]),
        "truth_max": max(v for r in success for v in r["truth"]),
        "worst_event": {
            "max_error": largest["metrics"]["max_absolute_error"],
            "mae": largest["metrics"]["mae"],
            "truth_range": max(largest["truth"]) - min(largest["truth"]),
            "prediction_range": max(largest["prediction"]) - min(largest["prediction"]),
        },
        "summary": summarize_records({"legacy_chronos_c3": rows}),
    }
    write_json(output / "legacy-diagnostic-rows.json", rows)
    return audit


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uom-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--skip-external", action="store_true")
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / "artifacts"):
        raise ValueError("health artifacts must remain under ignored artifacts/")
    if (output / "frozen-selection.json").exists():
        raise ValueError(
            "this study is frozen; use verify_refinement for audit, and a new approved "
            "protocol with an untouched test for further tuning"
        )
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    import torch

    torch.set_num_threads(2)
    np.random.seed(20261016)
    original_path = ROOT / "artifacts/evaluation-results/m2-validation.json"
    original_test_path = ROOT / "artifacts/evaluation-results/m2-test.json"
    original = json.loads(original_path.read_text())
    source_paths = sorted((ROOT / "research").rglob("*.py"))
    provenance = {
        "protocol": "refinement_v1",
        "python": platform.python_version(),
        "packages": {
            p: version(p)
            for p in ["numpy", "torch", "chronos-forecasting", "scikit-learn", "lightgbm"]
        },
        "checkpoint": CHRONOS2_MODEL_REVISION,
        "original_validation_sha256": digest(original_path),
        "original_test_sha256": digest(original_test_path),
        "source_hashes": {str(p.relative_to(ROOT)): digest(p) for p in source_paths},
        "uom_csv_hashes": {
            str(p.relative_to(args.uom_root)): digest(p)
            for p in sorted(args.uom_root.rglob("*.csv"))
        },
        "protocol_document_sha256": digest(ROOT / "docs/planning/GlycoLens_11_Model_Refinement.md"),
        "seed": 20261016,
        "threads": 2,
        "device": "cpu",
    }
    write_json(output / "provenance.json", provenance)
    samples, cohort = prepare_uom(args.uom_root, original["manifest"])
    write_json(output / "cohort-summary.json", cohort)
    log("prepared_uom", **cohort)
    frozen = FrozenChronos(output / "chronos-c0-cache.json")
    validation = {h: [s for s in rows if s["split"] == "validation"] for h, rows in samples.items()}
    matched_ids = set.intersection(*[{s["event_id"] for s in rows} for rows in validation.values()])
    history_rows = {
        f"chronos_{h}h": evaluate(rows, frozen.result) for h, rows in validation.items()
    }
    frozen.flush()
    history_matched = {
        name: [r for r in rows if r["event_id"] in matched_ids]
        for name, rows in history_rows.items()
    }
    matched_samples = [s for s in validation[2] if s["event_id"] in matched_ids]
    history_matched["persistence"] = evaluate(matched_samples, persistence)
    history_summary = summarize_records(history_matched)
    best_history_name = rank(history_summary, [f"chronos_{h}h" for h in HISTORIES])
    hours = int(best_history_name.split("_")[1][:-1])
    history_summary["available_event_summaries"] = {
        name: summarize_records({name: rows}) for name, rows in history_rows.items()
    }
    history_summary["selected_history_hours"] = hours
    write_json(output / "history-rows.json", history_rows)
    write_json(output / "history-summary.json", history_summary)
    log("history_selected", hours=hours, matched_events=len(matched_ids))
    train = [s for s in samples[hours] if s["split"] == "train"]
    cal = [s for s in samples[hours] if s["split"] == "calibration"]
    val = validation[hours]
    # Compute frozen backbone once per request, prior to residual training.
    for i, s in enumerate(train + cal):
        frozen.result(s["c0"])
        if (i + 1) % 100 == 0:
            log("backbone_progress", completed=i + 1, total=len(train) + len(cal))
    frozen.flush()
    runs = {"persistence": evaluate(val, persistence), "chronos_c0": evaluate(val, frozen.result)}
    candidates = {}
    for feature in ("shared", "full"):
        for residual in (False, True):
            for algorithm, grid in [("ridge", (1, 10, 100)), ("lightgbm", (7, 15))]:
                for parameter in grid:
                    name = (
                        f"{algorithm}_{'residual' if residual else 'direct'}_{feature}_{parameter}"
                    )
                    model = TabularForecastAdapter(
                        algorithm=algorithm,
                        parameter=parameter,
                        full_nutrition=feature == "full",
                        backbone=frozen if residual else None,
                    )
                    counts = Counter(s["participant_id"] for s in train)
                    weights = np.array([1 / counts[s["participant_id"]] for s in train])
                    weights *= len(weights) / weights.sum()
                    model.fit(
                        [s[feature] for s in train],
                        [s["truth"] for s in train],
                        sample_weight=weights,
                    )
                    runs[name] = evaluate(val, model.predict, feature)
                    candidates[name] = (model, feature)
                    log(
                        "candidate_evaluated",
                        name=name,
                        failed=sum(r["error_type"] is not None for r in runs[name]),
                    )
    summary = summarize_records(runs)
    winners = {
        feature: rank(
            summary,
            ["persistence", "chronos_c0"] + [n for n, (_, f) in candidates.items() if f == feature],
        )
        for feature in ("shared", "full")
    }
    selection = {
        "protocol": "refinement_v1",
        "history_hours": hours,
        "winners": winners,
        "validation_event_count": len(val),
        "training_event_count": len(train),
        "calibration_event_count": len(cal),
        "validation_summary_sha256": hashlib.sha256(
            json.dumps(summary, sort_keys=True).encode()
        ).hexdigest(),
        "research_code_sha256": hashlib.sha256(
            json.dumps(provenance["source_hashes"], sort_keys=True).encode()
        ).hexdigest(),
    }
    # Exclude latency from freeze comparison: it is descriptive and varies per run.
    selection["validation_summary_sha256"] = hashlib.sha256(
        json.dumps(
            {
                n: {k: v for k, v in r.items() if k != "wall_p95_ms"}
                for n, r in summary["runs"].items()
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()
    selection = freeze_selection(output / "frozen-selection.json", selection)
    write_json(output / "validation-rows.json", runs)
    write_json(output / "validation-summary.json", summary)
    log("selection_frozen", **selection)
    calibrated = {}
    calibration_rows = {}
    for name in set(winners.values()) | {"persistence", "chronos_c0"}:
        if name == "persistence":
            predictor, feature = persistence, "c0"
        elif name == "chronos_c0":
            predictor, feature = frozen.result, "c0"
        else:
            model, feature = candidates[name]
            predictor = model.predict
        calibration_rows[name] = evaluate(cal, predictor, feature)
        calibrated[name] = intervals(calibration_rows[name], runs[name])
        if name in candidates:
            model.calibrate([s[feature] for s in cal], [s["truth"] for s in cal])
            # Save the small estimator state only. A frozen residual backbone must
            # be reattached explicitly; never pickle a pipeline or an __main__ closure.
            joblib.dump(
                {
                    "regressor": model._regressor,
                    "scaler": model._scaler,
                    "interval": model._interval,
                    "algorithm": model.algorithm,
                    "parameter": model.parameter,
                    "full_nutrition": model.full_nutrition,
                    "requires_frozen_chronos": model.backbone is not None,
                    "checkpoint": CHRONOS2_MODEL_REVISION,
                    "model_version": model.model_version,
                },
                output / (name + ".joblib"),
            )
    write_json(output / "calibration-rows.json", calibration_rows)
    write_json(output / "validation-calibration.json", calibrated)
    result = {
        "selection": selection,
        "cohort": cohort,
        "validation_gate": {f: improvement_gate(summary, n) for f, n in winners.items()},
        "validation_comparisons": {
            f: paired_bootstrap(runs[n], runs["persistence"]) for f, n in winners.items()
        },
        "external": {"executed": False},
        "limitations": [
            "Small same-subject training cohort; no MetaboNet training in this run.",
            "Validation reused for candidate selection; selected validation improvements are optimistic.",
            "No clinical accuracy or maximum-error guarantee.",
        ],
    }
    if not args.skip_external:
        # This guard must precede any external predictive scoring.
        if not (output / "frozen-selection.json").exists():
            raise ValueError("external test requires frozen selection")
        external, external_audit = prepare_external(
            ROOT / "data/raw/azt1d-v1/csv", hours, samples[hours]
        )
        write_json(output / "external-cohort-summary.json", external_audit)
        name = winners["shared"]
        predictor, feature = (
            (persistence, "c0")
            if name == "persistence"
            else (
                (frozen.result, "c0")
                if name == "chronos_c0"
                else (candidates[name][0].predict, "shared")
            )
        )
        external_runs = {"persistence": evaluate(external, persistence)}
        if name != "persistence":
            external_runs[name] = evaluate(external, predictor, feature)
        external_summary = summarize_records(external_runs)
        result["external"] = {
            "executed": True,
            "cohort": external_audit,
            "winner": name,
            "summary": external_summary,
            "gate": improvement_gate(external_summary, name),
            "paired_mae": paired_bootstrap(external_runs[name], external_runs["persistence"]),
            "calibrated_intervals": {
                n: intervals(calibration_rows[n], rows) for n, rows in external_runs.items()
            },
        }
        write_json(output / "external-rows.json", external_runs)
        write_json(output / "external-summary.json", result["external"])
        log(
            "external_completed",
            events=len(external),
            participants=external_audit["eligible_participants"],
        )
    # Reproduction/outliers are diagnostic and do not feed model selection.
    legacy = [s for s in samples[2] if s["split"] == "diagnostic"]
    subjects = {}
    for s in legacy:
        subject = s["participant_id"]
        if subject not in subjects:
            subjects[subject] = load_participant(args.uom_root, subject)
        participant = subjects[subject]
        meal = next(m for m in participant.meals if m.timestamp == s["c0"].context_end)
        window = sliced_window(participant, meal, 2)
        s["legacy"] = meal_window_to_forecast_example(
            window, context=ContextConfiguration.CGM_INSULIN_NUTRITION
        ).request
    old_test = json.loads(original_test_path.read_text())
    result["legacy_audit"] = legacy_audit(
        legacy, old_test["rows"]["chronos2:cgm_insulin_nutrition"], output
    )
    frozen.flush()
    result["elapsed_seconds"] = time.perf_counter() - started
    result["artifact_hashes"] = {
        p.name: digest(p) for p in sorted(output.glob("*.json")) if p.name != "results.json"
    }
    write_json(output / "results.json", result)
    log(
        "study_completed",
        seconds=result["elapsed_seconds"],
        winners=winners,
        external_executed=result["external"]["executed"],
        validation_gate=result["validation_gate"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
