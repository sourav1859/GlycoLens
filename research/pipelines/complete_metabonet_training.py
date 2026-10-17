"""Audited scoring-only completion of Phase 4's already frozen, fitted experiment.

The original run completed every CV/refit but failed before its first scored row:
NumPy booleans are incompatible with statistics.mean. Preserve its source archive,
choices and model bytes; archive this scoring repair separately. Never fit here.
"""

import json
import hashlib
import zipfile
from datetime import datetime, timezone

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
    verify_completed,
)
from research.pipelines.run_metabonet_training import (
    GRID,
    VERSION,
    choose_cv,
    collect_training,
    compare,
    evaluate_direct,
    fit_final,
    verify_training_completed,
)

OUTPUT = ROOT / "artifacts/evaluation-results/metabonet-phase4-v1"


def verify_scoring_patch(original, current):
    old = b"prediction = list(predictions[index]) if predictions is not None else []"
    new = b"prediction = [float(v) for v in predictions[index]] if predictions is not None else []"
    if original.count(old) != 1 or original.replace(old, new, 1) != current:
        raise ValueError("repair must change only the native-float scoring boundary")


def checked_json(path):
    value = json.loads(path.read_text())
    if value.get("row_sha256") != record_checksum(value):
        raise ValueError("fitted-study metadata checksum changed")
    return value


def fitted_state(output, prepared, phase3):
    if (output / "complete.json").exists():
        raise ValueError("completed training cannot be replayed")
    execution = read_execution(output)
    execution_sha = hash_file(output / "execution.json")
    configuration = execution["configuration"]
    if (
        configuration["version"] != VERSION
        or configuration["grid"] != GRID
        or configuration["preparation_sha256"] != hash_file(prepared / "frozen-protocol.json")
        or configuration["phase3_completion_sha256"] != hash_file(phase3 / "complete.json")
    ):
        raise ValueError("fitted-study inputs or grid changed")
    # Only the runner's native-float scoring boundary may differ from original sources.
    for name, digest in execution["source_hashes"].items():
        if (
            name != "research/pipelines/run_metabonet_training.py"
            and hash_file(ROOT / name) != digest
        ):
            raise ValueError("non-scoring source changed")
    runner_name = "research/pipelines/run_metabonet_training.py"
    with zipfile.ZipFile(output / "execution-source.zip") as snapshot:
        verify_scoring_patch(snapshot.read(runner_name), (ROOT / runner_name).read_bytes())
    cohort = checked_json(output / "training-cohort.json")
    cohort.pop("row_sha256")
    folds = checked_json(output / "subject-folds.json")
    folds.pop("row_sha256")
    if (
        cohort != configuration["training_cohort"]
        or hashlib.sha256(json.dumps(folds, sort_keys=True).encode()).hexdigest()
        != configuration["fold_assignment_sha256"]
    ):
        raise ValueError("training population or folds changed")
    trials = []
    for config in GRID:
        trial = checked_json(output / f"cv-{config['name']}.json")
        if (
            trial["configuration"] != config
            or trial["execution_sha256"] != execution_sha
            or trial["prediction_sha256"] != hash_file(output / f"cv-{config['name']}.npy")
            or trial["failure_count"] != 0
        ):
            raise ValueError("frozen CV changed or incomplete")
        trials.append(trial)
    selected = checked_json(output / "cv-selection.json")
    if selected["execution_sha256"] != execution_sha or selected["choices"] != {
        family: choose_cv(trials, family)["configuration"] for family in ("ridge", "lightgbm")
    }:
        raise ValueError("frozen training-only selection changed")
    cv_summary = json.loads((output / "cv-summary.json").read_text())
    if cv_summary != {
        "candidates": trials,
        "selection": selected["choices"],
        "training_cohort": cohort,
    }:
        raise ValueError("CV summary differs from frozen candidate records")
    metadata = {}
    for family, config in selected["choices"].items():
        item = checked_json(output / f"model-{family}.json")
        if (
            item["configuration"] != config
            or item["execution_sha256"] != execution_sha
            or item["model_sha256"] != hash_file(output / f"model-{family}.joblib")
        ):
            raise ValueError("fitted model changed")
        metadata[family] = item
    return execution, selected["choices"], metadata


def main():
    prepared = ROOT / "artifacts/evaluation-results/metabonet-phase2-v1"
    phase3 = ROOT / "artifacts/evaluation-results/metabonet-phase3-v1"
    output = OUTPUT
    verify_preparation(prepared)
    verify_completed(phase3)
    execution, selected, metadata = fitted_state(output, prepared, phase3)
    interrupted = output / "interrupted-validation-ridge.jsonl"
    original_empty = output / "validation-ridge.jsonl"
    if not interrupted.exists():
        if not original_empty.exists() or original_empty.stat().st_size != 0:
            raise ValueError("expected original zero-row interruption evidence")
        original_empty.rename(interrupted)  # Preserve the original empty artifact, never delete it.
    if interrupted.stat().st_size != 0:
        raise ValueError("interruption evidence changed")
    repair = execution_guard(
        output / "completion-repair",
        {
            "reason": "convert NumPy scalar predictions to native floats before metrics/JSON",
            "original_execution_sha256": hash_file(output / "execution.json"),
            "original_empty_predictions_sha256": hash_file(interrupted),
            "model_hashes": {family: item["model_sha256"] for family, item in metadata.items()},
            "cv_selection_sha256": hash_file(output / "cv-selection.json"),
            "weights_refitted": False,
            "validation_rows_before_repair": 0,
        },
        {
            name: ROOT / name
            for name in (
                "research/pipelines/complete_metabonet_training.py",
                "research/pipelines/run_metabonet_training.py",
                "research/models/adapters/metabonet_tabular.py",
                "research/evaluation/refinement_metrics.py",
                "research/pipelines/run_metabonet_inference.py",
            )
        },
    )
    training, cohort = collect_training(prepared)
    if cohort != execution["configuration"]["training_cohort"]:
        raise ValueError("training population changed")
    models = {}
    for family, config in selected.items():
        # Metadata existence/hash was checked above, so fit_final can only load, never fit.
        models[family], _ = fit_final(config, {}, output, hash_file(output / "execution.json"))
    validation, validation_cohort = collect_validation(prepared)
    if validation_cohort["matched_event_count"] != 1509:
        raise ValueError("validation population changed")
    training_subjects = {w["sid"] for group in training.values() for w in group.values()}
    if training_subjects & {w["sid"] for w in validation[2].values()}:
        raise ValueError("training/validation subject overlap")
    runs = {}
    for name in VARIANTS:
        rows = [json.loads(line) for line in (phase3 / f"{name}.jsonl").read_text().splitlines()]
        for row in rows:
            w = validation[2][row["event_id"]]
            if (
                row.get("row_sha256") != record_checksum(row)
                or row["truth"] != w["truth"]
                or row["participant_id"] != w["sid"]
                or row["source"] != w["source"]
            ):
                raise ValueError("baseline identities/targets/records changed")
        runs[name] = rows
    validation_metadata = {}
    for family, model in models.items():
        config = selected[family]
        runs[family + "_direct"], validation_metadata[family] = evaluate_direct(
            model,
            config,
            validation[config["history_hours"]],
            output,
            metadata[family]["model_sha256"],
        )
    summary = compare(runs, validation[2])
    summary.update(
        training_cohort=cohort,
        validation_cohort=validation_cohort,
        cv_selection=selected,
        fit_metadata=metadata,
        validation_metadata=validation_metadata,
        elapsed_seconds=(
            datetime.now(timezone.utc) - datetime.fromisoformat(execution["created_at_utc"])
        ).total_seconds(),
        completion_repair=repair["configuration"],
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
                for p in sorted(output.rglob("*"))
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
        weights_refitted_during_repair=False,
        calibration_or_test_access=False,
    )
    return 0


if __name__ == "__main__":
    from threadpoolctl import threadpool_limits

    with threadpool_limits(limits=2):
        raise SystemExit(main())
