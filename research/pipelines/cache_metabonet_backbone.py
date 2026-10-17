"""Freeze and cache training-only C2 forecasts; no head fitting or reserved outcomes."""

import argparse
import json
import os
import platform
import time
from collections import Counter
from importlib.metadata import version

import numpy as np

from research.datasets.metabonet import window_to_example
from research.models.adapters.chronos2 import CHRONOS2_MODEL_REVISION, Chronos2ForecastAdapter
from research.models.adapters.metabonet_context import c2_request
from research.pipelines.prepare_metabonet import (
    ROOT,
    hash_file,
    log,
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
from research.pipelines.run_metabonet_training import collect_training, verify_training_completed

VERSION = "metabonet_phase5_v1"
OUTPUT = ROOT / "artifacts/evaluation-results/metabonet-phase5-v1"


def cache_training(windows, predictor, path):
    if any(w.get("split") != "train" for w in windows.values()):
        raise ValueError("backbone cache accepts training role only")
    rows = {}
    if path.exists():
        try:
            for line in path.read_text().splitlines():
                row = json.loads(line)
                key = row["event_id"]
                if (
                    key in rows
                    or key not in windows
                    or row.get("row_sha256") != record_checksum(row)
                ):
                    raise ValueError("invalid training cache row")
                rows[key] = row
        except (ValueError, KeyError, TypeError) as error:
            raise ValueError("training backbone cache is corrupt") from error
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        for key in sorted(windows):
            w = windows[key]
            if w["split"] != "train":
                raise ValueError("backbone cache accepts training role only")
            request = c2_request(window_to_example(w, with_covariates=True).request)
            fingerprint = request_fingerprint(request)
            if key in rows:
                row = rows[key]
                if (
                    row["request_sha256"] != fingerprint
                    or row["participant_id"] != w["sid"]
                    or row["source"] != w["source"]
                ):
                    raise ValueError("training cache input changed")
                continue  # Failed attempts are frozen, too.
            row = dict(
                event_id=key,
                participant_id=w["sid"],
                source=w["source"],
                request_sha256=fingerprint,
                prediction=[],
                error_type=None,
                error_cause_type=None,
            )
            started = time.perf_counter()
            try:
                result = predictor(request)
                values = np.asarray(result.median, dtype=float)
                if values.shape != (24,) or not np.isfinite(values).all():
                    raise ValueError("invalid frozen point forecast")
                row["prediction"] = [float(v) for v in values]
            except Exception as error:
                row["error_type"] = type(error).__name__
                row["error_cause_type"] = (
                    type(error.__cause__).__name__ if error.__cause__ else None
                )
            row["wall_ms"] = (time.perf_counter() - started) * 1000
            row["row_sha256"] = record_checksum(row)
            stream.write(json.dumps(row, allow_nan=False) + "\n")
            stream.flush()
            rows[key] = row
            if len(rows) % 100 == 0:
                log(
                    "training_backbone_progress",
                    completed=len(rows),
                    total=len(windows),
                    failures=sum(r["error_type"] is not None for r in rows.values()),
                )
    return [rows[key] for key in sorted(rows)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    output = OUTPUT / "backbone"
    if args.verify_only:
        verify_completed(output)
        log(
            "backbone_verified",
            artifact_hashes_valid=True,
            backbone_weights_fitted=False,
            calibration_or_test_access=False,
        )
        return 0
    if (output / "complete.json").exists():
        raise ValueError("completed backbone stage refuses replay")
    prepared = ROOT / "artifacts/evaluation-results/metabonet-phase2-v1"
    prior = ROOT / "artifacts/evaluation-results/metabonet-phase4-v1"
    verify_preparation(prepared)
    verify_training_completed(prior)
    training, cohort = collect_training(prepared)
    common = sorted(set.intersection(*(set(v) for v in training.values())))
    if len(common) != 6756 or cohort != read_execution(prior)["configuration"]["training_cohort"]:
        raise ValueError("Phase 4 common training population changed")
    checkpoint = (
        ROOT
        / "artifacts/models/huggingface/models--amazon--chronos-2/snapshots"
        / CHRONOS2_MODEL_REVISION
    )
    sources = {
        name: ROOT / name
        for name in (
            "research/pipelines/cache_metabonet_backbone.py",
            "research/models/adapters/metabonet_context.py",
            "research/models/adapters/chronos2.py",
            "research/models/adapters/base.py",
            "research/models/adapters/covariates.py",
            "research/models/adapters/converters.py",
            "research/datasets/metabonet.py",
            "research/datasets/t1d_uom.py",
            "research/pipelines/prepare_metabonet.py",
            "research/pipelines/run_metabonet_inference.py",
            "research/pipelines/run_metabonet_training.py",
            "docs/planning/GlycoLens_15_MetaboNet_Chronos_Correction.md",
            "pyproject.toml",
            "uv.lock",
        )
    }
    configuration = dict(
        version=VERSION,
        stage="training_backbone",
        backbone="chronos_c2_6h",
        training_cohort=cohort,
        preparation_sha256=hash_file(prepared / "frozen-protocol.json"),
        phase4_completion_sha256=hash_file(prior / "complete.json"),
        checkpoint=CHRONOS2_MODEL_REVISION,
        checkpoint_files={
            name: hash_file(checkpoint / name) for name in ("config.json", "model.safetensors")
        },
        python=platform.python_version(),
        packages={p: version(p) for p in ("torch", "chronos-forecasting", "numpy", "duckdb")},
        seed=20261016,
        threads=2,
        offline=True,
        calibration_or_test_access=False,
        weights_fitted=False,
    )
    execution_guard(output, configuration, sources)
    write_json(output / "training-cohort.json", cohort)
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1")
    import torch

    torch.set_num_threads(2)
    torch.manual_seed(20261016)
    model = Chronos2ForecastAdapter(cache_dir=ROOT / "artifacts/models/huggingface")
    model.load()
    log("training_backbone_ready", attempts=len(common), identities=cohort["common_subject_count"])
    started = time.perf_counter()
    rows = cache_training(
        {key: training[6][key] for key in common}, model.predict, output / "training.jsonl"
    )
    for name, digest in configuration["checkpoint_files"].items():
        if hash_file(checkpoint / name) != digest:
            raise ValueError("frozen checkpoint changed")
    summary = dict(
        attempts=len(rows),
        successes=sum(r["error_type"] is None for r in rows),
        failures=dict(Counter(r["error_type"] for r in rows if r["error_type"])),
        failure_causes=dict(Counter(r["error_cause_type"] for r in rows if r["error_cause_type"])),
        elapsed_seconds=time.perf_counter() - started,
        weights_fitted=False,
        calibration_or_test_access=False,
    )
    write_json(output / "summary.json", summary)
    write_json(
        output / "complete.json",
        {
            "artifact_hashes": {
                p.name: hash_file(p) for p in sorted(output.iterdir()) if p.is_file()
            }
        },
    )
    (output / "complete.sha256").write_text(hash_file(output / "complete.json") + "\n")
    verify_completed(output)
    log("training_backbone_complete", **summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
