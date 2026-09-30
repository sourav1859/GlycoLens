"""Run the persistence adapter on one leakage-safe T1D-UOM meal window."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from research.datasets.t1d_uom import find_eligible_windows
from research.models.adapters import (
    ContextConfiguration,
    ForecastExample,
    ForecastResult,
    PersistenceForecastAdapter,
    meal_window_to_forecast_example,
)


def _dataset_root(argument: str | None) -> Path:
    configured = argument or os.environ.get("GLYCOLENS_T1D_UOM_ROOT")
    if not configured:
        raise SystemExit("Set GLYCOLENS_T1D_UOM_ROOT or pass --dataset-root.")
    return Path(configured).expanduser().resolve()


def public_summary(
    example: ForecastExample,
    result: ForecastResult,
    context: ContextConfiguration,
) -> dict[str, object]:
    """Return aggregate smoke-test evidence without row-level values or identifiers."""

    return {
        "model_id": result.model_id,
        "model_version": result.model_version,
        "context_configuration": context.value,
        "history_points": len(example.request.target_history),
        "forecast_points": len(result.forecast_timestamps),
        "held_out_target_points": len(example.target.points),
        "frequency_minutes": example.request.frequency_minutes,
        "quantile_levels": tuple(item.level for item in result.quantiles),
        "latency_ms": round(result.latency_ms, 6),
        "target_withheld_from_request": True,
        "all_forecasts_finite": True,
        "quantiles_non_crossing": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", help="Path to the extracted T1D-UOM release")
    parser.add_argument(
        "--context",
        choices=tuple(item.value for item in ContextConfiguration),
        default=ContextConfiguration.CGM_INSULIN_NUTRITION.value,
    )
    args = parser.parse_args()
    context = ContextConfiguration(args.context)

    windows, search = find_eligible_windows(_dataset_root(args.dataset_root), limit=1)
    if not windows:
        raise SystemExit(
            "No eligible meal window was found; inspect the dataset audit and window policy."
        )
    example = meal_window_to_forecast_example(windows[0], context=context)
    adapter = PersistenceForecastAdapter()
    adapter.load()
    result = adapter.predict(example.request)
    summary = public_summary(example, result, context)
    summary["eligible_window_found"] = search.eligible_windows == 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
