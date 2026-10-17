# ADR 0011: MetaboNet development preparation and test reservation

Date: October 16, 2026. Status: accepted within the user-approved Phase 2 implementation.

## Context

The initial UOM residual-head improvement did not generalize to AZT1D. MetaboNet's
downloaded train/test pair contains prior cohorts, reused IDs, shared subjects,
source-dependent event coverage and ambiguous meal availability. The dictionary
clarifies native units and source-specific insulin exceptions but cannot establish
complete logging, raw-sensor observation or globally independent people.

## Decision

Prepare a source-balanced Loop/ReplaceBG development pilot from publisher train.
Split entire source-qualified subjects into training/validation/calibration, then
select metadata-only quotas before target inspection. Cap candidate meals by stable
origin hashes. Preserve masks, fractional grams and native IU amounts. Apply causal
history fill, strict source-present targets and predeclared isolated-meal exclusions.
Use five-minute delayed logged-carb availability as primary and zero-minute as
development sensitivity. Quarantine exact varied CGM duplicate candidates before fits.

Reserve publisher-test IDs absent from all publisher training as primary test;
reserve PEDAP separately as a pediatric source test. Project only test metadata in
Phase 2. Exclude consumed AZT1D/UOM; OhioT1DM stays out pending current terms. Do not
invent full nutrients, ordinary bolus values from merged insulin, or source timestamps.

Use bounded projection plus one-subject streaming; no app-database imports. Store
all rows/IDs/windows/projections under ignored artifacts. Freeze protocol, hashes,
manifest and executed sources; refuse replay into completed output. No forecasting,
fitting or app promotion in this phase.

## Consequences

This yields a fixed pilot population, not the complete MetaboNet benchmark. Attrition
and history sensitivity must accompany scores. Source-present CGM and event masks
do not repair unknown upstream imputation or reporting latency. Clean isolated meals
are a retrospective conditional task; they are not all live meals. Test eligibility
waits until model selection freezes. Phase 3 can reuse common forecast contracts;
Phase 4 needs deliberate handling of the new mask/recorded-channel schema.

See [protocol 12](../planning/GlycoLens_12_MetaboNet_Experiment.md) and the
[preparation report](../reports/metabonet-phase2-preparation-2026-10-16.md).

The authorized follow-on [Phase 3 protocol](../planning/GlycoLens_13_MetaboNet_Frozen_Inference.md)
uses only matched validation examples and the existing frozen common adapter. It
preserves the prepared population and test reservations; inference failures remain
visible and cannot reduce the full-cohort selection population. No app promotion.
