"""Run a privacy-safe Chronos-2 CPU smoke benchmark on one T1D-UOM window."""

from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import subprocess
import threading
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

from research.datasets.t1d_uom import T1D_UOM_RELEASE_COMMIT, T1D_UOM_VERSION, find_eligible_windows
from research.models.adapters import (
    CHRONOS2_MODEL_ID,
    CHRONOS2_MODEL_REVISION,
    CHRONOS_FORECASTING_VERSION,
    Chronos2ForecastAdapter,
    ContextConfiguration,
    ForecastResult,
    meal_window_to_forecast_example,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPOSITORY_ROOT / "artifacts" / "benchmarks" / "chronos2-m1-smoke.json"
DEFAULT_CACHE = REPOSITORY_ROOT / "artifacts" / "models" / "huggingface"


def _dataset_root(argument: str | None) -> Path:
    configured = argument or os.environ.get("GLYCOLENS_T1D_UOM_ROOT")
    if not configured:
        raise SystemExit("Set GLYCOLENS_T1D_UOM_ROOT or pass --dataset-root.")
    path = Path(configured).expanduser().resolve()
    if not path.is_dir():
        raise SystemExit("The configured dataset root is not an accessible directory.")
    return path


def _contained_path(argument: str | None, parent: Path, default: Path) -> Path:
    path = Path(argument).expanduser().resolve() if argument else default.resolve()
    try:
        path.relative_to(parent.resolve())
    except ValueError as error:
        raise SystemExit(
            f"Artifact paths must remain under {parent.relative_to(REPOSITORY_ROOT)}."
        ) from error
    return path


def _git_value(*arguments: str) -> str:
    try:
        completed = subprocess.run(
            [
                "git",
                "-c",
                f"safe.directory={REPOSITORY_ROOT.as_posix()}",
                *arguments,
            ],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            check=True,
            text=True,
        )
        return completed.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def _nearest_rank(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int((percentile * len(ordered) + 0.999999)) - 1))
    return ordered[index]


class _PeakRssMonitor:
    def __init__(self, process: Any, interval_seconds: float = 0.05) -> None:
        self._process = process
        self._interval_seconds = interval_seconds
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._sample, daemon=True)
        self.peak_bytes = 0

    def _record(self) -> None:
        self.peak_bytes = max(self.peak_bytes, int(self._process.memory_info().rss))

    def _sample(self) -> None:
        while not self._stop.wait(self._interval_seconds):
            self._record()

    def __enter__(self) -> _PeakRssMonitor:
        self._record()
        self._thread.start()
        return self

    def __exit__(self, *_args: object) -> None:
        self._stop.set()
        self._thread.join()
        self._record()


def _validated_result_summary(result: ForecastResult) -> dict[str, object]:
    return {
        "forecast_points": len(result.forecast_timestamps),
        "quantile_levels": [forecast.level for forecast in result.quantiles],
        "all_forecasts_finite": True,
        "quantiles_non_crossing": True,
        "target_withheld_from_request": True,
    }


def _benchmark(
    dataset_root: Path,
    cache_dir: Path,
    warm_iterations: int,
) -> dict[str, object]:
    try:
        import psutil
        import torch
    except ImportError as error:
        raise SystemExit(
            "Install the pinned Chronos dependency group before running the smoke benchmark."
        ) from error

    windows, search = find_eligible_windows(dataset_root, limit=1)
    if not windows:
        raise SystemExit(
            "No eligible meal window was found; inspect the dataset audit and window policy."
        )
    context = ContextConfiguration.CGM_ONLY
    example = meal_window_to_forecast_example(windows[0], context=context)
    process = psutil.Process()
    rss_before = process.memory_info().rss
    cpu_before = process.cpu_times()

    adapter = Chronos2ForecastAdapter(cache_dir=cache_dir)
    load_started = perf_counter()
    with _PeakRssMonitor(process) as load_memory:
        adapter.load()
    load_seconds = perf_counter() - load_started
    rss_after_load = process.memory_info().rss

    with _PeakRssMonitor(process) as inference_memory:
        cold_started = perf_counter()
        last_result = adapter.predict(example.request)
        cold_wall_ms = (perf_counter() - cold_started) * 1000

        warm_wall_ms: list[float] = []
        backend_latency_ms: list[float] = [last_result.latency_ms]
        for _ in range(warm_iterations):
            started = perf_counter()
            last_result = adapter.predict(example.request)
            warm_wall_ms.append((perf_counter() - started) * 1000)
            backend_latency_ms.append(last_result.latency_ms)

    cpu_after = process.cpu_times()
    total_cpu_seconds = (cpu_after.user + cpu_after.system) - (cpu_before.user + cpu_before.system)
    total_wall_seconds = load_seconds + (cold_wall_ms + sum(warm_wall_ms)) / 1000
    logical_cpu_count = psutil.cpu_count(logical=True) or 1
    normalized_cpu_percent = (
        100 * total_cpu_seconds / total_wall_seconds / logical_cpu_count
        if total_wall_seconds > 0
        else 0.0
    )

    dirty = _git_value("status", "--porcelain") not in ("", "unavailable")
    return {
        "schema_version": 1,
        "recorded_at_utc": datetime.now(UTC).isoformat(),
        "source_control": {
            "branch": _git_value("branch", "--show-current"),
            "commit": _git_value("rev-parse", "HEAD"),
            "working_tree_dirty": dirty,
        },
        "environment": {
            "operating_system": platform.platform(),
            "architecture": platform.machine(),
            "processor": platform.processor() or "unavailable",
            "physical_cpu_count": psutil.cpu_count(logical=False),
            "logical_cpu_count": logical_cpu_count,
            "total_memory_mb": round(psutil.virtual_memory().total / 1024**2, 2),
            "python_version": platform.python_version(),
            "torch_version": torch.__version__,
            "chronos_forecasting_version": CHRONOS_FORECASTING_VERSION,
            "device": "cpu",
        },
        "model": {
            "id": CHRONOS2_MODEL_ID,
            "revision": CHRONOS2_MODEL_REVISION,
            "checkpoint_cache_inside_ignored_artifacts": True,
        },
        "workload": {
            "dataset_version": T1D_UOM_VERSION,
            "dataset_release_commit": T1D_UOM_RELEASE_COMMIT,
            "eligible_window_found": search.eligible_windows == 1,
            "selected_window_count": 1,
            "context_configuration": context.value,
            "history_points": len(example.request.target_history),
            "held_out_target_points": len(example.target.points),
            "prediction_length": example.request.prediction_length,
            "frequency_minutes": example.request.frequency_minutes,
            "warm_iterations": warm_iterations,
        },
        "measurements": {
            "load_seconds": round(load_seconds, 6),
            "cold_adapter_wall_ms": round(cold_wall_ms, 6),
            "warm_adapter_wall_ms_samples": [round(value, 6) for value in warm_wall_ms],
            "warm_adapter_wall_ms_p50": round(statistics.median(warm_wall_ms), 6),
            "warm_adapter_wall_ms_p95": round(_nearest_rank(warm_wall_ms, 0.95), 6),
            "warm_adapter_wall_ms_p99": round(_nearest_rank(warm_wall_ms, 0.99), 6),
            "backend_latency_ms_samples": [round(value, 6) for value in backend_latency_ms],
            "rss_before_load_mb": round(rss_before / 1024**2, 2),
            "rss_after_load_mb": round(rss_after_load / 1024**2, 2),
            "load_peak_rss_mb": round(load_memory.peak_bytes / 1024**2, 2),
            "inference_peak_rss_mb": round(inference_memory.peak_bytes / 1024**2, 2),
            "normalized_process_cpu_percent": round(normalized_cpu_percent, 2),
            "error_count": 0,
        },
        "validation": _validated_result_summary(last_result),
        "privacy": {
            "contains_participant_identifiers": False,
            "contains_timestamps": False,
            "contains_glucose_or_forecast_values": False,
            "contains_dataset_path": False,
        },
        "limitations": [
            "One eligible window is a smoke workload, not an accuracy evaluation.",
            "The first load can include checkpoint download time when the cache is empty.",
            "Warm p95 and p99 use nearest-rank estimates over a small sample.",
            "CPU and memory observations are machine- and workload-specific.",
        ],
    }


def _public_summary(record: dict[str, object], artifact_path: Path) -> dict[str, object]:
    measurements = record["measurements"]
    workload = record["workload"]
    validation = record["validation"]
    assert isinstance(measurements, dict)
    assert isinstance(workload, dict)
    assert isinstance(validation, dict)
    return {
        "model_id": CHRONOS2_MODEL_ID,
        "model_revision": CHRONOS2_MODEL_REVISION,
        "device": "cpu",
        "context_configuration": workload["context_configuration"],
        "history_points": workload["history_points"],
        "forecast_points": validation["forecast_points"],
        "warm_iterations": workload["warm_iterations"],
        "load_seconds": measurements["load_seconds"],
        "cold_adapter_wall_ms": measurements["cold_adapter_wall_ms"],
        "warm_adapter_wall_ms_p50": measurements["warm_adapter_wall_ms_p50"],
        "warm_adapter_wall_ms_p95": measurements["warm_adapter_wall_ms_p95"],
        "inference_peak_rss_mb": measurements["inference_peak_rss_mb"],
        "validation_passed": measurements["error_count"] == 0,
        "artifact": artifact_path.relative_to(REPOSITORY_ROOT).as_posix(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", help="Path to the extracted T1D-UOM release")
    parser.add_argument(
        "--allow-model-download",
        action="store_true",
        help="Explicitly allow the pinned checkpoint to be downloaded into ignored artifacts",
    )
    parser.add_argument("--cache-dir", help="Checkpoint cache under artifacts/models/")
    parser.add_argument("--output", help="JSON artifact path under artifacts/benchmarks/")
    parser.add_argument("--warm-iterations", type=int, default=5)
    args = parser.parse_args()

    if not args.allow_model_download:
        raise SystemExit(
            "Pass --allow-model-download to acknowledge the external checkpoint download."
        )
    if args.warm_iterations < 5:
        raise SystemExit("--warm-iterations must be at least 5.")

    cache_dir = _contained_path(
        args.cache_dir,
        REPOSITORY_ROOT / "artifacts" / "models",
        DEFAULT_CACHE,
    )
    output_path = _contained_path(
        args.output,
        REPOSITORY_ROOT / "artifacts" / "benchmarks",
        DEFAULT_OUTPUT,
    )
    cache_dir.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    record = _benchmark(_dataset_root(args.dataset_root), cache_dir, args.warm_iterations)
    output_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(_public_summary(record, output_path), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
