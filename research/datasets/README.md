# Dataset Adapters

Store dataset adapters, schema mappings, and provenance metadata here. Dataset contents belong in ignored local data directories.

`t1d_uom.py` pins T1D-UOM V1.0.4, validates the four core modalities, loads complete rows, converts glucose from mmol/L to mg/dL at the model boundary, and constructs leakage-safe meal windows. Exact duplicate CGM values collapse; conflicting values at the same timestamp are excluded rather than averaged. Nutrition rows sharing a timestamp are treated as components of one meal and aggregated.

`azt1d.py` ingests only the 25 canonical AZT1D V1 CGM Records files; it excludes
Visual Statistics exports. The public source archive is checksummed by
`research.pipelines.acquire_azt1d`. Source glucose is mg/dL; the loader converts to
the shared internal mmol/L dataclass and back at the forecast boundary without
changing units. Source times have no offset. Collapse exact rows, aggregate positive
same-time carbohydrate/total-bolus events, remove conflicting CGM timestamps and
nonpositive/nonfinite glucose. Basal/correction fields are not added to total bolus.
Full protein/fat/fibre is unavailable; zero placeholders in the reused MealEvent
record MUST NOT enter predictors. The study permits only shared-feature requests
for external data. One canonical glucose field mentions CGM/BGM; retain this caveat.
External event/subject IDs have source namespaces; do not expose them in public reports.

`metabonet.py` handles the fixed Loop/ReplaceBG pilot in native mg/dL, grams and
trailing-five-minute IU amounts. It preserves fractional values, missingness and
relative timestamp grids; no dose forward fill, total-plus-components sum or invented
full nutrients. Candidate origins have stable IDs across history/timing variants.
Past-only history fill is limited to ten minutes, with >=90% source-present history
and all 24 target values required. Nearby meals are excluded by a predeclared
retrospective isolated-meal rule. `window_to_example` returns an immutable request
and separate target; optional covariates carry source-present masks and recorded
channels. Model feature consumers must explicitly support that schema; the older
UOM feature extractor is not automatically validated for it.

The preparation pipeline projects selected training rows with bounded DuckDB, then
streams by subject. Publisher test is metadata-only; PEDAP is reserved separately.
Exact varied CGM fingerprints screen partial duplicate candidates, not verified
identities. Frozen manifests, windows and sources stay ignored. See
[protocol 12](../../docs/planning/GlycoLens_12_MetaboNet_Experiment.md),
[execution report](../../docs/reports/metabonet-phase2-preparation-2026-10-16.md) and
[commands](../README.md#metabonet-phase-2-preparation).
