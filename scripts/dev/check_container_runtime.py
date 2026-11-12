"""Opt-in container smoke: real fixed simulator + cached CPU model, no cloud or LLM.

Run: docker compose exec api /app/.venv/bin/python -m scripts.dev.check_container_runtime
Only aggregate synthetic execution metadata is printed. Scratch artifacts are removed.
This checks runtime plumbing, not meal sensitivity, accuracy or cloud readiness.
"""

from datetime import datetime, timedelta, timezone
from importlib.metadata import version
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter

from backend.app.services.inference.application import build_request
from research.models.adapters import Chronos2ForecastAdapter
from research.simulation.adapter import run_pymgipsim_scenario


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    stage = "simulator"
    started = perf_counter()
    try:
        directory = root / "artifacts/simulation"
        directory.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(prefix="runtime-smoke-", dir=directory) as scratch:
            output, context_path = Path(scratch) / "scenario.json", Path(scratch) / "context.json"
            result = run_pymgipsim_scenario(
                source_directory=Path(os.environ["GLYCOLENS_SIMULATOR_SOURCE_DIR"]),
                python_executable=Path(os.environ["GLYCOLENS_SIMULATOR_PYTHON"]),
                output_json=output,
                internal_context_output=context_path,
            )
            context = json.loads(context_path.read_text(encoding="utf-8"))
            epoch = datetime(2026, 1, 1, tzinfo=timezone.utc)
            origin = epoch + timedelta(minutes=context["origin_minute"])
            cgm = [dict(recorded_at=(epoch + timedelta(minutes=p.minute)).isoformat(),
                        glucose_mg_dl=p.glucose_mg_dl, source="simulation")
                   for p in result.trajectory if p.minute <= context["origin_minute"]]
            insulin = [dict(recorded_at=(epoch + timedelta(minutes=e["minute"])).isoformat(),
                            event_type=e["event_type"], units=e["source_value"],
                            insulin_kind=e["insulin_kind"]) for e in context["insulin_events"]]
            request = build_request(dict(recorded_at=origin.isoformat(), carbs_g=30,
                                         protein_g=10, fat_g=8, fiber_g=4), cgm, insulin)
            stage = "cached_cpu_forecast"
            import torch
            assert torch.version.cuda is None, "CPU wheel required"
            adapter = Chronos2ForecastAdapter(cache_dir=root / "artifacts/models/huggingface")
            adapter.load()
            forecast = adapter.predict(request)
            assert len(forecast.median) == 24
            print(json.dumps(dict(status="PASS", simulator_samples=result.sample_count,
                                  forecast_points=len(forecast.median), model=forecast.model_id,
                                  model_revision=forecast.model_version, torch=version("torch"),
                                  cpu_only=True, elapsed_seconds=round(perf_counter()-started, 2),
                                  cloud_requests=0, llm_calls=0)))
    except Exception:
        print(json.dumps(dict(status="FAIL", stage=stage)))
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
