from __future__ import annotations

from pathlib import Path

import pytest

from research.pipelines.run_chronos2_smoke import (
    DEFAULT_OUTPUT,
    REPOSITORY_ROOT,
    _contained_path,
    _public_summary,
)


def test_public_benchmark_summary_contains_no_row_level_health_data() -> None:
    record: dict[str, object] = {
        "measurements": {
            "load_seconds": 5.5,
            "cold_adapter_wall_ms": 60.0,
            "warm_adapter_wall_ms_p50": 50.0,
            "warm_adapter_wall_ms_p95": 55.0,
            "inference_peak_rss_mb": 810.0,
            "error_count": 0,
        },
        "workload": {
            "context_configuration": "cgm_only",
            "history_points": 24,
            "warm_iterations": 5,
        },
        "validation": {"forecast_points": 24},
    }

    summary = _public_summary(record, DEFAULT_OUTPUT)

    assert summary["validation_passed"] is True
    assert not any(
        forbidden in key
        for key in summary
        for forbidden in ("participant", "timestamp", "glucose", "target_value", "dataset_root")
    )


def test_benchmark_artifact_paths_cannot_escape_ignored_directory(tmp_path: Path) -> None:
    benchmark_parent = REPOSITORY_ROOT / "artifacts" / "benchmarks"
    allowed = _contained_path(None, benchmark_parent, DEFAULT_OUTPUT)
    assert allowed == DEFAULT_OUTPUT.resolve()

    with pytest.raises(SystemExit, match="must remain under"):
        _contained_path(str(tmp_path / "outside.json"), benchmark_parent, DEFAULT_OUTPUT)
