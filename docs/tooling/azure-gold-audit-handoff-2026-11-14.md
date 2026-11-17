# Azure gold catalog audit handoff — November 14, 2026

## Goal

Reassess the two Azure reports against the external production gold catalog,
measure source-ready candidates/dependencies and export sizes, and prepare a
GlycoLens cloud migration strategy without importing or activating data.

## Accepted decisions

- External production remains a distinct project and source; gold data only.
- Exact readiness is display_status = 'user_ready', with non-deleted products.
- Source readiness and GlycoLens validation/publication are separate states.
- Preserve nutrient basis, original facts/lineage and immutable app meal snapshots.
- Keep existing managed cloud app development and personal/simulation boundaries.

## Current repository state

Documentation and aggregate evidence changed locally. No commit, push, migration,
source write, complete export, target restore/import or app activation was performed.
Private audit scripts/dependencies/receipts remain ignored under
`.cache/azure-nutrition-audit/2026-11-14/`; no credentials were saved in them.

## Files changed

- [Assessment](../reports/azure-nutrition-catalog-assessment-2026-11-06.md),
  [strategy](../reports/azure-to-supabase-catalog-migration-strategy-2026-11-06.md),
  [aggregate evidence](../reports/azure-gold-catalog-audit-2026-11-14.json).
- Root README, reports index and ADR 0015.
- Planning 00, 01, 03, 04, 06, 08 and 17; this handoff.

## Documentation reviewed/updated

Plans 00/01: current status and source/app separation. Plan 03: catalog UX and
recipe portions. Plan 04: schemas, provider/gram contract and capacity. Plan 06:
M3 execution tracking. Plan 08: provenance, nutrition uncertainty and production
isolation. Plan 17: P07 admission/acceptance. These were updated. Plan 19 was
reviewed and unchanged because reference-food copying cannot reclassify personal
or simulation history. AGENTS.md, SECURITY.md, nutrition provider source and
current gram-based meal calculation migrations were also reviewed.

## Checks completed

- Azure PostgreSQL 16.15/TLS1.3 and server-enforced read-only settings verified.
- Gold metadata, complete aggregate selection/quality scans, corrected plural
  lineage joins and singular fact joins; initial query mistakes corrected.
- One repeatable-read read-only sizing snapshot: exact projection counts/logical
  byte sums and at most 1,500 native CSV rows per projection compressed in memory.
- Supabase 17.11 baseline: 15,414,963 bytes, no catalog schema; SELECTs only.
- Local validator: numerical reconciliation and credential-artifact checks PASS;
  373 relative links across the 13 primary changed artifacts resolve.
- Git diff whitespace check PASS; private scripts/environment confirmed ignored.
- Graphify exclusion prerequisites PASS; one code-only refresh completed with
  3,723 nodes / 7,999 edges. SQL AST support is absent for 19 SQL files. Source SQL
  was read directly. Semantic documentation extraction was not run; no model
  backend or external document transfer was authorized or needed for this audit.
- No application tests were run: only documentation/aggregate evidence changed.

## Known failures or blockers

Source-ready tags do not supply independent nutrition approval. Source identity,
licences, recipe serving authority, competing fact precedence and generated/
estimated content require explicit resolution. Full package export, actual
indexed restore, organization/physical disk capacity and P07 acceptance are pending.

## Remaining risks

33,194 recipe candidates mix 19,111 whole-recipe and 14,083 per-serving profiles;
299 yield conflicts and 1,343 incomplete profiles remain. Of 5,429 ready
ingredients, only 2,862 have all five nonnegative main-column nutrients; six have
negative carbohydrate. Of 11,397 ready products, 1,706 fail GTIN checks.

The evidence-bearing package estimate is 151.90 MiB CSV / 50.61 MiB gzip.
180–260 MiB of indexed catalog allocation is provisional; optional image paths
add storage and require host/reuse checks. Snapshot samples are not full exports
or confidence intervals. Audit batches do not freeze a final source release.

## Next action

Establish the approved UUID/release manifest, source rights and nutrition/basis
rules; then prepare the reviewed private exporter and isolated measured restore.
Follow the strategy's guarded catalog migration/publication sequence after those
conditions are met. Do not replace GlycoLens runtime DB configuration with Azure
production settings or apply/import data merely because this audit completed.
