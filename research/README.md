# Research Pipeline

This area will contain reproducible preprocessing, model-comparison, context-ablation, context-length, retrieval-personalization, and evaluation workflows.

Downloaded datasets and derived health-data files belong under `data/` and are excluded from Git. Commit code, small sanitized fixtures, configurations, and aggregate non-sensitive results only.

## Implemented Milestone 1 slice

The repository includes a dependency-free T1D-UOM V1.0.4 adapter, aggregate audit, and meal-window generator. Configure `GLYCOLENS_T1D_UOM_ROOT`; do not copy or commit the downloaded dataset unless it remains inside an ignored raw-data directory.

```powershell
python -m research.pipelines.audit_t1d_uom
python -m research.pipelines.build_meal_windows --limit 1
```
