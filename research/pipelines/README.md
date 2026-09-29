# Research Pipelines

Own deterministic dataset ingestion, event-window generation, model comparison, context ablation, and evaluation pipelines here.

Available commands:

- `python -m research.pipelines.audit_t1d_uom` validates release identity, schemas, timestamps, numeric fields, missing required fields, duplicate timestamps, and modality coverage.
- `python -m research.pipelines.build_meal_windows --limit 1` finds a model-ready event with two hours of CGM history, six hours of prior insulin context, full meal nutrition, and a separate two-hour CGM target.

Both commands accept `--dataset-root`; otherwise they read `GLYCOLENS_T1D_UOM_ROOT`. Output is aggregate and does not contain participant identifiers or timestamps for selected windows.
