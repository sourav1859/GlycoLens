# Research Pipeline

This area will contain reproducible preprocessing, model-comparison, context-ablation, context-length, retrieval-personalization, and evaluation workflows.

Downloaded datasets and derived health-data files belong under `data/` and are excluded from Git. Commit code, small sanitized fixtures, configurations, and aggregate non-sensitive results only.

## Implemented Milestone 1 slice

The repository includes a dependency-free T1D-UOM V1.0.4 adapter, aggregate audit, meal-window
generator, common forecast contract, persistence baseline, pinned Chronos-2 CPU adapter, and an
isolated pinned py-mgipsim virtual-patient feasibility scenario.
Configure
`GLYCOLENS_T1D_UOM_ROOT`; do not copy or commit the downloaded dataset unless it remains inside an
ignored raw-data directory.

```powershell
python -m research.pipelines.audit_t1d_uom
python -m research.pipelines.build_meal_windows --limit 1
uv run python -m research.pipelines.run_persistence_baseline
uv run --all-groups python -m research.pipelines.run_chronos2_smoke --allow-model-download
./scripts/simulation/Install-PyMgipsim.ps1
uv run python -m research.pipelines.run_pymgipsim_scenario --allow-upstream-execution
```

The persistence command converts one real eligible window while keeping future CGM in a separate
evaluation target. Its output is aggregate and contains no participant ID, timestamp, glucose
value, or held-out target value.

The Chronos-2 command runs the C0/CGM-only path, requires explicit checkpoint-download consent,
and writes aggregate timing/memory evidence only under ignored `artifacts/benchmarks/`. It rejects
covariate-bearing requests until their model-specific alignment is implemented and tested.

The simulator command runs one fixed synthetic ExtHovorka/OpenLoop day and writes a validated
relative-time trajectory under ignored `artifacts/simulation/`. It is not a clinical result and
does not expose individual insulin values or dose guidance.
