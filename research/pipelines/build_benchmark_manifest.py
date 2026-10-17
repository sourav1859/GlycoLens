"""Build private event manifests; stdout contains only aggregate quality/split counts."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from pathlib import Path

from research.datasets.t1d_uom import WindowConfig, find_eligible_windows
from research.evaluation.protocol import manifest_summary, temporal_manifest


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root")
    parser.add_argument(
        "--output", type=Path, default=ROOT / "artifacts/evaluation-results/m2-manifest.json"
    )
    args = parser.parse_args()
    dataset = args.dataset_root or os.environ.get("GLYCOLENS_T1D_UOM_ROOT")
    if not dataset:
        raise SystemExit("Set GLYCOLENS_T1D_UOM_ROOT or pass --dataset-root.")
    output = args.output.resolve()
    if not output.is_relative_to((ROOT / "artifacts/evaluation-results").resolve()):
        raise SystemExit("Manifests must remain inside ignored artifacts/evaluation-results.")
    windows, quality = find_eligible_windows(dataset, WindowConfig())
    entries = temporal_manifest(windows)
    summary = manifest_summary(entries)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "quality": asdict(quality),
                "summary": summary,
                "events": [asdict(entry) for entry in entries],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"quality": asdict(quality), "splits": summary}, indent=2, sort_keys=True))
    return 0 if summary["participants_with_validation_and_test"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
