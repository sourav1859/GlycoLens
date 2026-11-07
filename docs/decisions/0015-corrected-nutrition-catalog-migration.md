# Corrected nutrition catalog migration

**Date:** November 6, 2026

**Status:** Proposed migration design. The user confirmed future use after upstream correction; implementation and cloud activation are deferred.

**Milestone:** Audit/design evidence belongs to M2; execution and application
verification are M3 carry-forward work in the
[milestone schedule](../planning/GlycoLens_06_Milestones_and_Schedule.md#corrected-nutrition-catalog-migration-from-milestone-2).

## Context

The supplied Azure `gold` catalog contains recipes, ingredients, products, serving information and nutrient facts. A read-only quality audit found incorrect mappings and unresolved serving/energy semantics. The user reports that recipe corrections are ongoing and instructed that the data is not yet to be used.

The selected 13 source tables currently occupy 737.72 MiB with indexes. Supabase Free advertises a 500 MB database allowance. A bounded projection study estimates 113.95 MiB CSV / 38.69 MiB gzip for six compact tables at current row counts, excluding compact provenance and lookups. Budgeting 150 to 250 MiB for the indexed serving catalog is plausible but must be verified by a real local restore.

## Proposed design

Use a corrected release, export selected food columns under a consistent read-only snapshot, validate locally, and load an application-owned compact catalog schema. Preserve stable source UUIDs, required nutrition, serving bases, source evidence and release identity. Leave Azure intact. Keep application users, CGM/insulin, saved meals and forecasts separate; retain immutable meal nutrition snapshots.

Do not mirror all source indexes, complete nutrient history, image-generation records, store pricing or customer data. Do not discard nutrient provenance when avoiding duplicate general fact storage. No uncorrected recipe data may be activated.

## Alternatives

- A full source-layout mirror retains unnecessary storage and dependencies and is not the recommended Free design.
- Continuing read-through Azure access avoids a copy but leaves the demo dependent on upstream availability and changing corrections. It remains an optional backend fallback after validation.
- A smaller reviewed pilot is the fallback if the full compact release lacks quality or storage headroom.
- Paid Supabase is an option when measured requirements exceed Free; this record does not authorize purchase.

## Execution conditions

A corrected manifest, source semantics, reuse permission, destination project details, local restore evidence and target capacity check precede activation. The strategy recommends a 400,000,000-byte operating budget including a 100,000,000-byte growth reserve; these are project guardrails, not Supabase limits. Account for temporary staging and WAL separately.

Preserve a private release package for rollback. Avoid duplicate full cloud catalog versions unless measured headroom permits them. Validate ownership boundaries, food facts and end-to-end behavior before publication. No source writes, full export, target deployment or application integration were performed for this design.

See the [measured migration strategy](../reports/azure-to-supabase-catalog-migration-strategy-2026-11-06.md) and [catalog quality assessment](../reports/azure-nutrition-catalog-assessment-2026-11-06.md).
