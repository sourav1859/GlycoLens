# Research Pipelines

Own deterministic dataset ingestion, event-window generation, model comparison, context ablation, and evaluation pipelines here.

Available commands:

- `python -m research.pipelines.audit_t1d_uom` validates release identity, schemas, timestamps, numeric fields, missing required fields, duplicate timestamps, and modality coverage.
- `python -m research.pipelines.build_meal_windows --limit 1` finds a model-ready event with two hours of CGM history, six hours of prior insulin context, full meal nutrition, and a separate two-hour CGM target.
- `uv run python -m research.pipelines.run_persistence_baseline` converts one eligible window into
  the common adapter contract and runs the persistence baseline.
- `uv run --all-groups python -m research.pipelines.run_chronos2_smoke --allow-model-download`
  runs the pinned Chronos-2 C0 checkpoint, records cold/warm latency and process RSS, and stores a
  sanitized JSON record under ignored `artifacts/benchmarks/`.
- `uv run --all-groups python -m research.pipelines.render_chronos2_forecast
  --allow-model-download` runs the pinned checkpoint on one eligible C0 window and writes a
  relative-time PNG under ignored `artifacts/forecasts/`. Held-out truth is omitted unless the
  explicit local-only overlay flag is supplied.
- `uv run python -m research.pipelines.run_pymgipsim_scenario --allow-upstream-execution` runs the
  fixed, pinned virtual-patient feasibility protocol after the isolated simulator installer has
  completed. It writes only simulated relative-time data and aggregate metadata under ignored
  `artifacts/simulation/`.

All commands accept `--dataset-root`; otherwise they read `GLYCOLENS_T1D_UOM_ROOT`. Output is
aggregate and does not contain participant identifiers, timestamps, glucose values, or held-out
target values for selected windows.
The py-mgipsim command is synthetic and contains no research participant data.
