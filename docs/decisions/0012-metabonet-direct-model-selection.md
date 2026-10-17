# ADR 0012: train-only selection of MetaboNet direct models

Date: October 16, 2026. Status: accepted within the approved Phase 4 implementation.

## Context

The frozen Phase 3 comparison did not beat persistence under its accuracy/reliability
gate. Longer histories improved conditional point accuracy but some native quantile
outputs failed. The earlier UOM adapter's feature/unit assumptions cannot be silently
applied to MetaboNet's recorded five-minute IU amounts and observation masks.

## Decision

Add a research-only MetaboNet tabular adapter behind the immutable common forecast
contract. Features read requests only, preserve native units and missingness, and omit
merged insulin total when components are supplied. No participant/source/absolute-time
predictors. Current known carbs and recorded-event summaries are descriptive context,
not dosing advice or physiological activity estimates.

Compare Ridge and LightGBM across four histories and two profiles using a fixed
32-candidate grid and three whole-subject training folds. Use a common training-event
pool, source-stratified hash folds and equal participant weights. Ridge fits 24 delta
outputs with train-only imputation/scaling. LightGBM fits one pooled-horizon delta
regressor; expand horizons after subject splitting. Freeze one CV winner per family,
refit all eligible training events at that history, then compare on the same 1,509
validation meals as Phase 3. Reuse checksummed prior forecasts with identical targets.

Save local model bundles, frozen sources/configuration and checksummed progress only
under ignored artifacts. Verify saved bytes before resume deserialization; reject
changed or partial output. Equal quantile fields are deterministic placeholders, not
uncertainty estimates. Keep calibration/reserved outcomes untouched for later phases.

## Consequences

This tests whether inexpensive direct training adds predictive value without fitting
foundation weights or repeating Chronos inference. Validation is reused for selection;
its gains need independent testing. A history-specific refit can use more meals than
the common CV pool and must disclose this. The pooled booster constrains horizon
behavior differently from independent regressors. Research scores do not replace the
application model or demonstrate a +/-10 maximum-error guarantee.

See [protocol 14](../planning/GlycoLens_14_MetaboNet_Direct_Models.md) and the
[aggregate results](../reports/metabonet-phase4-training-2026-10-16.md).
