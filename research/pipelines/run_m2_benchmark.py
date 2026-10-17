"""Matched validation benchmark; raw research results stay in ignored artifacts."""

from __future__ import annotations

import argparse
import json
import os
import platform
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

from research.datasets.t1d_uom import WindowConfig, find_eligible_windows
from research.evaluation.protocol import event_id, temporal_manifest
from research.evaluation.runner import comparison_summary, evaluate
from research.models.adapters import (
    Chronos2ForecastAdapter,
    ContextConfiguration,
    PersistenceForecastAdapter,
)
from research.models.adapters.timesfm3 import TimesFM3ForecastAdapter


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root")
    parser.add_argument("--allow-model-download", action="store_true")
    parser.add_argument("--split", choices=("validation", "test"), default="validation")
    parser.add_argument("--frozen-selection", type=Path)
    parser.add_argument(
        "--models",
        nargs="+",
        choices=("persistence", "chronos2", "timesfm3"),
        default=["persistence", "chronos2", "timesfm3"],
    )
    parser.add_argument(
        "--contexts",
        nargs="+",
        choices=[c.value for c in ContextConfiguration],
        default=[ContextConfiguration.CGM_ONLY.value],
    )
    parser.add_argument("--limit", type=int)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "artifacts/evaluation-results/m2-validation.json"
    )
    args = parser.parse_args()
    if args.limit is not None and args.limit <= 0:
        raise SystemExit("limit must be positive")
    if args.split == "test":
        # Test evaluation is locked until a validation-based selection exists.
        if not args.frozen_selection or not args.frozen_selection.is_file():
            raise SystemExit("Test evaluation requires --frozen-selection from validation.")
        selection = json.loads(args.frozen_selection.read_text(encoding="utf-8"))
        if selection.get("split") != "validation" or not selection.get("selection_frozen"):
            raise SystemExit(
                "Selection must be frozen using validation evidence before test evaluation."
            )
        if selection.get("feature_version") != "recorded_events_v1":
            raise SystemExit("Frozen feature representation differs from the current benchmark.")
    dataset = args.dataset_root or os.environ.get("GLYCOLENS_T1D_UOM_ROOT")
    if not dataset:
        raise SystemExit("Set GLYCOLENS_T1D_UOM_ROOT or pass --dataset-root.")
    output = args.output.resolve()
    if not output.is_relative_to((ROOT / "artifacts/evaluation-results").resolve()):
        raise SystemExit("Results must stay inside ignored artifacts/evaluation-results.")
    all_windows, _ = find_eligible_windows(dataset, WindowConfig())
    manifest = temporal_manifest(all_windows)
    ids = {entry.event_id for entry in manifest if entry.split == args.split}
    windows = tuple(w for w in all_windows if event_id(w) in ids)
    if args.limit:
        windows = windows[: args.limit]
    if not windows:
        raise SystemExit("No events in requested split.")
    factories = {
        "persistence": PersistenceForecastAdapter,
        "chronos2": lambda: Chronos2ForecastAdapter(
            cache_dir=ROOT / "artifacts/models/huggingface"
        ),
        "timesfm3": lambda: TimesFM3ForecastAdapter(
            cache_dir=ROOT / "artifacts/models/huggingface",
            local_files_only=not args.allow_model_download,
        ),
    }
    runs = {}
    loads = {}
    identities = {}
    import psutil

    memory = {}
    for name in args.models:
        model = factories[name]()
        # Enforce offline behavior for Chronos too when download was not acknowledged.
        if name == "chronos2" and not args.allow_model_download:
            os.environ["HF_HUB_OFFLINE"] = "1"
        started = perf_counter()
        try:
            model.load()
        except Exception as error:
            raise SystemExit(
                f"{name} load failed ({type(error).__name__}); no model ranking produced."
            ) from None
        loads[name] = (perf_counter() - started) * 1000
        identities[name] = {"id": model.model_id, "revision": model.model_version}
        for context in args.contexts:
            runs[f"{name}:{context}"] = evaluate(windows, model, ContextConfiguration(context))
        memory[name] = psutil.Process().memory_info().rss / 1024**2
        del model
    summary = comparison_summary(runs)
    summary.update(
        {
            "split": args.split,
            "limited_pilot": args.limit is not None,
            "model_load_ms": loads,
            "process_rss_after_run_mib": memory,
            "model_identities": identities,
            "python": platform.python_version(),
            "feature_version": "recorded_events_v1",
        }
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "summary": summary,
                "rows": {name: [asdict(r) for r in rows] for name, rows in runs.items()},
                "manifest": [asdict(e) for e in manifest],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["common_success_event_count"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
