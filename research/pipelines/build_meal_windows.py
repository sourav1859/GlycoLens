"""Find leakage-safe, model-ready T1D-UOM meal windows."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from pathlib import Path

from research.datasets.t1d_uom import WindowConfig, find_eligible_windows


def _dataset_root(argument: str | None) -> Path:
    configured = argument or os.environ.get("GLYCOLENS_T1D_UOM_ROOT")
    if not configured:
        raise SystemExit("Set GLYCOLENS_T1D_UOM_ROOT or pass --dataset-root.")
    return Path(configured)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", help="Path to the extracted T1D-UOM release")
    parser.add_argument(
        "--limit", type=int, default=1, help="Stop after this many eligible windows"
    )
    parser.add_argument("--history-minutes", type=int, default=120)
    parser.add_argument("--horizon-minutes", type=int, default=120)
    parser.add_argument("--frequency-minutes", type=int, default=5)
    parser.add_argument(
        "--allow-no-insulin",
        action="store_true",
        help="Allow windows without insulin context (not recommended for the M1 feasibility slice)",
    )
    arguments = parser.parse_args()

    config = WindowConfig(
        history_minutes=arguments.history_minutes,
        horizon_minutes=arguments.horizon_minutes,
        frequency_minutes=arguments.frequency_minutes,
        require_insulin_context=not arguments.allow_no_insulin,
    )
    windows, summary = find_eligible_windows(
        _dataset_root(arguments.dataset_root),
        config,
        limit=arguments.limit,
    )
    payload: dict[str, object] = {
        "configuration": asdict(config),
        "search": asdict(summary),
        "sample_shape": windows[0].shape_summary() if windows else None,
        "contains_row_level_data": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if windows else 2


if __name__ == "__main__":
    raise SystemExit(main())
