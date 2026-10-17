"""Verify trusted-local saved heads and original artifact integrity; no model tuning."""

import argparse
import json
import hashlib
import zipfile
from pathlib import Path

import joblib
import numpy as np

from research.models.adapters.tabular import FEATURE_VERSION, TabularForecastAdapter
from research.pipelines.run_refinement import (
    CHRONOS2_MODEL_REVISION,
    DEFAULT_OUTPUT,
    ROOT,
    FrozenChronos,
    digest,
    prepare_uom,
    request_key,
    write_json,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uom-root", type=Path, required=True)
    args = parser.parse_args()
    directory = DEFAULT_OUTPUT
    results = json.loads((directory / "results.json").read_text())
    provenance = json.loads((directory / "provenance.json").read_text())
    original = ROOT / "artifacts/evaluation-results/m2-validation.json"
    original_test = ROOT / "artifacts/evaluation-results/m2-test.json"
    assert digest(original) == provenance["original_validation_sha256"]
    assert digest(original_test) == provenance["original_test_sha256"]
    with zipfile.ZipFile(directory / "execution-source-snapshot.zip") as snapshot:
        expected_files = {
            **provenance["source_hashes"],
            "docs/planning/GlycoLens_11_Model_Refinement.md": provenance[
                "protocol_document_sha256"
            ],
        }
        for name, expected in expected_files.items():
            assert hashlib.sha256(snapshot.read(name.replace("\\", "/"))).hexdigest() == expected
    for name, expected in results["artifact_hashes"].items():
        assert digest(directory / name) == expected, "study artifact changed after execution"
    assert json.loads((directory / "frozen-selection.json").read_text()) == results["selection"]
    selection = results["selection"]
    samples, _ = prepare_uom(args.uom_root, json.loads(original.read_text())["manifest"])
    validation = [s for s in samples[selection["history_hours"]] if s["split"] == "validation"]
    rows = json.loads((directory / "validation-rows.json").read_text())
    frozen = FrozenChronos(directory / "chronos-c0-cache.json")
    deltas = {}
    for feature, name in selection["winners"].items():
        if name in ("persistence", "chronos_c0"):
            continue
        # Load only artifacts written by this approved local run, never user-supplied pickle.
        state = joblib.load(directory / (name + ".joblib"))
        assert state["model_version"] == FEATURE_VERSION
        assert state["checkpoint"] == CHRONOS2_MODEL_REVISION
        adapter = TabularForecastAdapter(
            algorithm=state["algorithm"],
            parameter=state["parameter"],
            full_nutrition=state["full_nutrition"],
            backbone=frozen if state["requires_frozen_chronos"] else None,
        )
        adapter._regressor, adapter._scaler, adapter._interval = (
            state["regressor"],
            state["scaler"],
            state["interval"],
        )
        reference = {r["event_id"]: r for r in rows[name]}
        difference = 0
        for sample in validation:
            if adapter.backbone is not None:
                assert request_key(sample["c0"]) in frozen.cache, (
                    "verification must not run fresh inference"
                )
            median = adapter.predict(sample[feature]).median
            difference = max(
                difference,
                float(
                    np.max(np.abs(np.array(median) - reference[sample["event_id"]]["prediction"]))
                ),
            )
        assert difference < 1e-9, "saved model does not reproduce frozen validation predictions"
        deltas[name] = difference
    verification = {
        "original_artifacts_unchanged": True,
        "result_artifact_hashes_valid": True,
        "frozen_selection_unchanged": True,
        "saved_head_validation_max_differences": deltas,
        "validation_events_per_head": len(validation),
        "fresh_inference_performed": False,
        "execution_source_snapshot_verified": True,
    }
    write_json(directory / "verification.json", verification)
    print(json.dumps(verification, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
