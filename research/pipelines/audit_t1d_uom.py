"""Audit a local T1D-UOM V1.0.4 extraction without emitting row-level data."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from research.datasets.t1d_uom import audit_dataset


def _dataset_root(argument: str | None) -> Path:
    configured = argument or os.environ.get("GLYCOLENS_T1D_UOM_ROOT")
    if not configured:
        raise SystemExit("Set GLYCOLENS_T1D_UOM_ROOT or pass --dataset-root.")
    return Path(configured)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", help="Path to the extracted T1D-UOM release")
    parser.add_argument(
        "--include-file-details", action="store_true", help="Include per-file aggregate checks"
    )
    parser.add_argument(
        "--include-participant-ids",
        action="store_true",
        help="Include de-identified source participant IDs in output",
    )
    arguments = parser.parse_args()

    audit = audit_dataset(_dataset_root(arguments.dataset_root))
    print(
        json.dumps(
            audit.to_dict(
                include_files=arguments.include_file_details,
                include_participant_ids=arguments.include_participant_ids,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
