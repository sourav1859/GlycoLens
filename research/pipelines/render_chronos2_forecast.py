"""Render one ignored, relative-time Chronos-2 research forecast figure."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from research.datasets.t1d_uom import find_eligible_windows
from research.models.adapters import (
    Chronos2ForecastAdapter,
    ContextConfiguration,
    meal_window_to_forecast_example,
)
from research.visualization import save_forecast_plot


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
FORECAST_ARTIFACT_ROOT = REPOSITORY_ROOT / "artifacts" / "forecasts"
MODEL_CACHE = REPOSITORY_ROOT / "artifacts" / "models" / "huggingface"
DEFAULT_OUTPUT = FORECAST_ARTIFACT_ROOT / "chronos2-example.png"


def _dataset_root(argument: str | None) -> Path:
    configured = argument or os.environ.get("GLYCOLENS_T1D_UOM_ROOT")
    if not configured:
        raise SystemExit("Set GLYCOLENS_T1D_UOM_ROOT or pass --dataset-root.")
    root = Path(configured).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit("The configured dataset root is not an accessible directory.")
    return root


def _output_path(argument: str | None) -> Path:
    output = Path(argument).expanduser().resolve() if argument else DEFAULT_OUTPUT.resolve()
    try:
        output.relative_to(FORECAST_ARTIFACT_ROOT.resolve())
    except ValueError as error:
        raise SystemExit("Forecast figures must remain under artifacts/forecasts/.") from error
    if output.suffix.lower() != ".png":
        raise SystemExit("Forecast figure output must use the .png extension.")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", help="Path to the extracted T1D-UOM release")
    parser.add_argument("--output", help="PNG path under artifacts/forecasts/")
    parser.add_argument(
        "--allow-model-download",
        action="store_true",
        help="Explicitly permit use/download of the pinned checkpoint in ignored artifacts",
    )
    parser.add_argument(
        "--include-held-out-target",
        action="store_true",
        help="Overlay evaluation truth; keep the resulting health-data figure local and ignored",
    )
    args = parser.parse_args()
    if not args.allow_model_download:
        raise SystemExit(
            "Pass --allow-model-download to acknowledge use of the external checkpoint."
        )

    windows, _search = find_eligible_windows(_dataset_root(args.dataset_root), limit=1)
    if not windows:
        raise SystemExit("No eligible meal window was found.")
    example = meal_window_to_forecast_example(windows[0], context=ContextConfiguration.CGM_ONLY)
    adapter = Chronos2ForecastAdapter(cache_dir=MODEL_CACHE)
    adapter.load()
    result = adapter.predict(example.request)
    output = _output_path(args.output)
    summary = save_forecast_plot(
        example,
        result,
        output,
        include_held_out_target=args.include_held_out_target,
    )
    summary["artifact"] = output.relative_to(REPOSITORY_ROOT).as_posix()
    summary["model_id"] = result.model_id
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
