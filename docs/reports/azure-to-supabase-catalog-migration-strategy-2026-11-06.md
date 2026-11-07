# Azure to Supabase catalog migration strategy

**Prepared for:** Sourav Patil and the GlycoLens capstone

**Evidence checked:** November 6, 2026

**Status:** Planning only. Recipe data is being corrected upstream and must not be activated in GlycoLens until a corrected release passes validation. No complete export or cloud import was performed.

**Milestone placement:** The audit and strategy are M2 feasibility/planning evidence.
Export, local restore, cloud import and application acceptance are tracked as M3
integration work in the [milestone schedule](../planning/GlycoLens_06_Milestones_and_Schedule.md#corrected-nutrition-catalog-migration-from-milestone-2).
Existing M2 live-nutrition gates remain open; correction readiness and course dates
are not changed by this placement.

## Recommendation

The selected data can be exported from Azure PostgreSQL without changing Azure. A compact, corrected catalog is a plausible fit for Supabase Free. A mirror preserving the selected source tables and their existing indexes is not a suitable Free plan design.

The measured core source footprint is **737.72 MiB**, including indexes and TOAST. The proposed six-table application projection has an estimated **113.95 MiB of CSV data**, or **38.69 MiB compressed**, before adding compact provenance and lookup dictionaries. Budget **150 to 250 MiB for the imported catalog with necessary indexes and metadata**, then prove the actual result in a local restore. This is an engineering estimate, not a measured Supabase restore.

Use a corrected release, retain stable source UUIDs, export only explicit food-related columns, validate locally, and import a compact catalog schema. Keep the source database intact. Continue to keep application identities, CGM, insulin, meals and forecasts separate from the food catalog.

## Scope and current authorization

The user confirmed that recipe refinements are ongoing and that corrected data will be used later. This work measures storage and defines a future migration; it does not activate the current data or replace existing nutrition providers.

Azure was queried in server-enforced read-only transactions. PostgreSQL 16.15 and TLS 1.3 were observed. Queries measured metadata, exact row counts and bounded samples; sampled records were discarded after calculating sizes. No store-product rows, pricing, customer records, meal logs, account data or secrets tables were exported. Private measurement scripts and aggregate receipts remain under ignored `.cache/azure-nutrition-audit/`.

No Supabase cloud project was inspected or modified, so its existing database usage, disk utilization and remaining quota are unknown. Those values are required before an actual cloud import.

## Current Supabase Free limits

Supabase currently lists **500 MB database size**, **1 GB file storage**, **5 GB egress**, shared CPU and **500 MB RAM** for Free. It permits two active Free projects and pauses inactive projects after one week. Automatic backups are not included. File storage is a separate allowance; it does not increase the PostgreSQL database quota. These are current published limits, not reserved capacity for this migration. [Supabase pricing](https://supabase.com/pricing).

The database quota covers table data and indexes. Supabase separately documents a fixed **2 GB physical disk** for Free, including operational files such as WAL, with read-only protection around 95% disk utilization. That disk size is not permission to plan a 2 GB catalog under a 500 MB database allowance. Bulk loading and index creation also require temporary disk headroom. [Database and disk size](https://supabase.com/docs/guides/platform/database-size).

There is a documentation inconsistency worth checking at execution time: the billing overview describes 500 MB per project, while the disk-size page describes a fair-use calculation across an organization. This strategy conservatively budgets one project below 500,000,000 bytes and requires checking the target organization's actual Usage dashboard as well. It does not rely on splitting data across projects to evade a quota. [Billing overview](https://supabase.com/docs/guides/platform/billing-on-supabase).

If the compact design does not fit with adequate headroom, retain a smaller approved subset or use a paid plan. Pro currently starts at **$25 per month** and lists **8 GB disk per project**; no upgrade was purchased or authorized by this document. [Supabase pricing](https://supabase.com/pricing).

## Measured Azure footprint

All sizes in the measurement tables are binary MiB: 1 MiB = 1,048,576 bytes. Supabase's displayed MB quota is treated conservatively as decimal MB: 500 MB = approximately 476.84 MiB.

Sizes were read with `pg_table_size`, `pg_indexes_size` and `pg_total_relation_size`. Table size includes TOAST and auxiliary table storage; total size adds indexes. Current allocated pages can include free space or bloat. A logical export does not copy that physical layout, and a rebuilt target can be smaller. [PostgreSQL size functions](https://www.postgresql.org/docs/16/functions-admin.html).

| Source table | Exact current rows | Tables and TOAST MiB | Indexes MiB | Total MiB |
|---|---:|---:|---:|---:|
| `nutrition_facts` | 1,284,422 catalog facts | 184.39 | 244.03 | 428.42 |
| `recipe_ingredients` | 416,162 | 57.63 | 51.23 | 108.87 |
| `recipes` | 42,142 | 43.43 | 21.90 | 65.33 |
| `data_lineage` | 130,279 catalog lineage rows | 24.76 | 28.89 | 53.65 |
| `product_ingredients` | 163,610 | 18.58 | 22.34 | 40.91 |
| `ingredients` | 69,115 | 13.87 | 8.29 | 22.16 |
| `recipe_nutrition_profiles` | 42,140 | 7.41 | 3.55 | 10.97 |
| `products` | 12,329 | 3.98 | 2.97 | 6.95 |
| Five small dictionaries | See below | Combined | Combined | 0.46 |
| **Selected core total** | **13 source tables** | | | **737.72** |

The five dictionaries are `nutrition_definitions` (122 rows), `nutrition_categories` (31), `cuisines` (25), `product_categories` (0) and `ingredient_synonyms` (0). Empty dictionaries should not be represented as populated capabilities.

The core measurement is **773,554,176 bytes**, or **773.55 decimal MB**. The core without the general `nutrition_facts` table occupies **309.30 MiB** in Azure. Omitting that table alone does not guarantee a target will fit: provenance, target baseline usage, search indexes and future application data still need space.

An expanded group of 26 catalog-related tables occupies **925.57 MiB**. This includes optional image metadata, allergen and dietary mappings. In particular, `recipe_images` occupies **72.62 MiB**, partly because it stores generation prompts and parameters; it is not a measurement of downloaded image files. `product_images` adds **1.77 MiB**. These operational image records are unnecessary for the first catalog migration.

Row counts and size queries ran in separate read-only transactions against a live database, rather than a single migration snapshot. Corrections may change both row counts and sizes. Remeasure the corrected release before exporting it.

## Estimated compact export

The export estimate uses explicit projections of six tables, preserving source row UUIDs, required nutrition, quantities, recipe instructions, serving fields and update timestamps. It drops unrelated operational fields and most unused micronutrients. It retains raw quantity/unit alongside normalized grams, since missing normalization must remain visible.

Each table was sampled with PostgreSQL `TABLESAMPLE SYSTEM (20) REPEATABLE (6) LIMIT 5000`. Five tables yielded 5,000 sampled rows; products yielded 2,866. Actual UTF-8 CSV and gzip sizes were calculated in memory, then scaled by exact population counts. Samples are page based and capped; they are not a confidence interval or a guaranteed representative sample of all text lengths. Array/JSON serialization and NULL handling must be finalized in the real exporter.

| Projected table | Rows at current scale | Estimated CSV MiB | Estimated gzip MiB |
|---|---:|---:|---:|
| Recipes | 42,142 | 29.74 | 9.11 |
| Recipe ingredients | 416,162 | 50.88 | 17.15 |
| Recipe nutrition profiles | 42,140 | 5.06 | 1.69 |
| Ingredients | 69,115 | 7.62 | 3.09 |
| Products | 12,329 | 2.12 | 0.91 |
| Product ingredients | 163,610 | 18.53 | 6.73 |
| **Total** | **745,498** | **113.95** | **38.69** |

The underlying totals are **119,485,887 estimated CSV bytes** and **40,564,877 estimated gzip bytes**. Sample-based projected tuple content totals approximately **91.30 MiB**, before the complete target layout, indexes, provenance, validation fields and release metadata.

For planning, allow roughly **100 to 160 MiB uncompressed** or **30 to 60 MiB compressed** for these six data projections, plus a small number of dictionaries and a separately measured compact provenance file. These ranges are contingency allowances around the sample estimates, not measured full-export sizes. Retain at least 1 GB of local working space for archive, unpacked files, quarantine and validation logs. A full-fidelity archive of all original columns would be larger and has not been compression-measured.

The **150 to 250 MiB imported catalog budget** allows for selected indexes, page overhead, compact lineage and application validation fields. It excludes actual image binaries, embeddings, complete nutrient history and the existing application database. Only a local restore using the intended schema and indexes can settle the real target size.

## Recommended migration contents

| Content | Initial migration decision | Reason |
|---|---|---|
| Corrected recipes, ingredient links and profiles | Include after release validation | Core meal-selection and nutrition functionality |
| Ingredients referenced by selected recipes/products | Include after source and nutrient validation | Preserve joins and deterministic calculation |
| Validated packaged products and ingredient lists | Include if useful for the capstone | Enables barcode/search without store pricing |
| Cuisine and required nutrition dictionaries | Include relevant populated values | Small supporting lookups |
| Provenance | Include a compact representation | Source, original entity ID, nutrient basis and validation must survive |
| All 1.28 million nutrient facts | Exclude from the first cloud serving copy | Most micronutrients and duplicate nutrient storage are unnecessary for current inference |
| Needed nutrient-fact evidence | Retain selected evidence in the export/provenance design | Do not lose source-specific bases or assume denormalized columns are authoritative |
| Image generation history and prompts | Exclude | High storage cost without meal-planning benefit |
| Image URLs | Optional after URL and reuse checks | URLs are cheap; image files have a separate budget |
| Raw image files, embeddings and broad dietary rules | Defer | Not required to close the nutrition workflow |
| Stores, prices, users, health profiles, meal logs and secrets | Exclude | Outside this catalog migration |

Excluding `nutrition_facts` is a storage decision, not permission to erase uncertainty. Export a documented canonical value only after source precedence is resolved, and preserve its original value, unit, basis, source and transformation version. Estimated nutrition must remain identifiable and must not be promoted as verified facts.

## Proposed destination design

Use a separate application-owned `catalog` schema rather than restoring the production `gold` schema wholesale. Keep catalog UUIDs and relationship-row UUIDs stable. Repeated ingredients must not be collapsed merely because a recipe uses the same ingredient twice.

The initial structure should contain the six compact entities, a small cuisine lookup, catalog release metadata and compact source evidence. Each published entry needs source identity, import release, fetched/corrected timestamp, validation state and a nutrient basis. Recipe profiles need explicit whole-recipe yield; products need a basis of 100 g or a serving with a known gram weight. Missing values must remain NULL, distinct from confirmed zero.

Retain source numeric precision for nutrition; avoid float conversions and broad rounding during copying. Preserve GTINs as text, including leading zeros. Preserve instructions as structured JSON where possible. Source update timestamps have no timezone offset: record them as source-local/unspecified unless the source owner confirms the timezone, and use a separate timezone-aware import timestamp.

The existing application `foods` contract is gram based. Catalog loading alone does not make whole-recipe totals compatible with it. A later application change must either support explicit consumed servings or use a verified cooked recipe mass to derive a gram basis. Never assign a fabricated gram weight to a recipe. When catalog entries become application food snapshots, use a source-qualified identity such as `ingredient:<source UUID>` or `product:<source UUID>` so entity types and later source updates remain traceable.

Do not restore Azure roles, grants, production triggers, duplicate indexes, references to `silver`/`bronze`, vendor accounts, `created_by_user_id`, or foreign keys to customer records. Resolve the needed catalog relationships in the new schema. The source currently contains repeated equivalent foreign-key definitions; create only the target constraints actually needed.

Apply SELECT-only catalog access for application consumers, with writes limited to a migration/import role. Keep the schema outside directly exposed APIs unless deliberately exposed with explicit grants and RLS. Existing per-user application RLS remains in force. Save immutable food snapshots into the application meal workflow so later catalog updates cannot change historical meals.

Start with primary keys, relationship lookup indexes, a validated barcode index and one justified name-search method. Avoid copying every source index or adding vector indexes in this first release. The general fact table alone has **244.03 MiB of indexes** in the current source.

## Migration runbook after correction

### 1 Establish a corrected release

Obtain a named release or manifest from the data owner. Recipe use remains on hold until name-to-source mapping, calorie units, serving-count conflicts, required nutrients, quantities and provenance pass checks. Validate any ingredient/product subset independently; correction of recipe text alone does not establish correction of its linked nutrients.

Capture the approved entity UUID set and dependency closure. Every exported recipe/product relationship must resolve to an exported ingredient; every retained cuisine or source dictionary key must resolve. Quarantine a whole unresolved recipe when a required ingredient cannot be validated, rather than exporting a silently incomplete recipe.

### 2 Export through a consistent read-only snapshot

Use a dedicated SELECT-only Azure account and a client-side PostgreSQL connection. Establish a single bounded `REPEATABLE READ READ ONLY` transaction for the release, and stream explicit column projections using `COPY (SELECT ...) TO STDOUT`. This exports over the connection and writes local files, not files on the Azure server. PostgreSQL supports exporting selected query results this way. [PostgreSQL COPY](https://www.postgresql.org/docs/16/sql-copy.html).

Run tables serially or use a deliberately coordinated shared snapshot; independent per-table snapshots are insufficient for a consistent final release. Avoid long idle transactions while the source is being refined. If the export connection or snapshot is lost, discard the partial release and restart consistently; do not mix data from a resumed snapshot with earlier tables.

The release package should contain compressed per-table UTF-8 CSV files, reviewed target schema SQL, `manifest.json`, SHA-256 checksums, row counts and aggregate quality results. Document column order, encoding, NULL-versus-empty-string representation, JSON/array handling, source version and correction version. Keep credentials out of commands, manifests and logs. Keep the package in an ignored private export directory.

For an optional archival copy, PostgreSQL `pg_dump -Fc` can preserve selected source tables in a compressed logical archive. It is not the recommended serving import: table selection does not automatically include all dependencies, and production schema objects need review. Source PostgreSQL is 16.15; choose a compatible client and test the destination version. [PostgreSQL pg_dump](https://www.postgresql.org/docs/16/app-pgdump.html).

### 3 Validate and measure in local PostgreSQL or Supabase

Create the intended compact schema locally and restore the actual corrected package. Import small dictionaries and base ingredient/product/recipe records before relationship tables, then add the reviewed indexes and validate constraints. Compute canonical per-serving/per-100-g values exactly once, with the source basis preserved.

Compare manifest counts and checksums, reject orphan references, verify nutrient/quantity constraints, and test representative labels and recipes against corrected source evidence. Measure both the catalog relations and whole local database after index creation. This phase determines whether the Free plan estimate holds.

### 4 Check target capacity before cloud loading

Obtain the intended Supabase project connection details privately and read its Usage dashboard, PostgreSQL version, database size and physical disk utilization. Use a direct connection for native migration commands; if the network requires IPv4, Supabase documents session pooling as the alternative. Avoid transaction pooling for the migration session. [Connection guidance](https://supabase.com/docs/guides/database/connecting-to-postgres).

Use this conservative project gate in bytes:

```text
existing whole database size
+ measured incremental catalog and index size
+ 100,000,000 bytes reserved for application growth
<= 400,000,000 bytes
```

The 400 MB operating target and 100 MB growth reserve are project recommendations, not Supabase limits. Also allow transient staging/index/WAL space under the separate disk constraint. If the gate fails, reduce the approved catalog, reduce unnecessary indexes, or choose a paid plan. Never treat compressed archive size as imported database size.

For illustration, a 60 MB existing database plus a 200 MiB catalog plus a 100 MB growth reserve totals about **370 MB**, within this gate. A 150 MB existing database plus a 250 MiB catalog plus the same reserve totals about **512 MB**, which fails even the advertised quota. The actual target baseline has not been measured.

### 5 Load without exposing incomplete catalog data

Create only the reviewed target schema, grants and release tables. Stream CSV using client-side `COPY FROM STDIN`/`psql \copy`, in bounded resumable chunks where appropriate. Supabase recommends COPY for large loads; the dashboard CSV importer has a 100 MB file limit and is not the primary method for this migration. [Supabase import guide](https://supabase.com/docs/guides/database/import-data), [bulk loading](https://supabase.com/docs/guides/database/tables#bulk-data-loading).

On Free, start with one importer and conservative chunks, for example 5,000 to 20,000 rows per destination commit, then adjust from observed latency and disk growth. Bound temporary target staging to roughly 10 to 25 MiB. These are initial operating choices to test, not provider guarantees. Source consistency is preserved by the already-completed package; destination chunk commits do not need a long-lived Azure transaction.

Keep the new catalog unpublished until all counts, joins, validation checks and required indexes pass. Do not disable RLS globally or replace the existing public application schema. Initial activation can switch a published-release marker or backend feature setting only after acceptance.

### 6 Verify behavior and preserve rollback

Verify food search, a valid barcode, recipe/ingredient editing, grams, serving fractions, deterministic displayed/saved totals, provenance snapshots, missing nutrient handling and a real forecast through the existing adapter. Compare imported values with the release package, not changing live Azure rows.

Retain the corrected package and target schema outside the cloud database as the rollback source. Do not keep two full cloud catalog copies unless a measured capacity check permits it. During a later refresh, use a maintenance/read-fallback strategy or a capacity-approved version switch; never let partially updated recipe and ingredient records become visible together. Historical saved-meal snapshots must remain intact.

## Updates after the initial migration

Treat Azure as the upstream source and Supabase as the serving copy. Prefer explicit corrected releases over live replication while refinements continue. Full compact snapshots simplify deletion handling at this scale; selective updates are possible later using stable UUIDs and source timestamps plus a release manifest that identifies deletions. A timestamp watermark alone cannot discover deleted rows and must not be treated as sufficient synchronization.

Re-run quality and capacity checks for each release. Preserve existing meal snapshots; do not rewrite them when source nutrition changes. Record the release used for every imported food fact. Keep research model datasets and weights outside this catalog process.

## Images and archives

Actual image binary sizes were not measured. The Azure image tables contain paths, URLs, prompts and generation metadata, not a complete accounting of image object bytes. Do not add their PostgreSQL table size to a file-storage estimate.

For the initial capstone copy, omit image binaries and generation history. If images are later required, measure the selected files, confirm reuse rights, and budget them separately against the 1 GB file-storage allowance. Free also limits individual Storage uploads to at most 50 MB; archive sharding may therefore be needed if using that service. Keeping a gzip archive in Storage does not make its contents queryable PostgreSQL tables. [Storage upload limits](https://supabase.com/docs/guides/storage/uploads/file-limits).

## Acceptance checklist

- A corrected source release is identified, with its approved record set and dependency closure.
- All catalog data files, schema and manifest agree on row counts, column order, types and checksums.
- No secrets, customers, health profiles, store prices or unrelated production objects enter the package.
- Food identity, preparation state, energy units, servings, quantities, barcode checks and provenance pass the agreed rules.
- Recipe totals and user portions are reconciled without double scaling; missing nutrients are not silently zero-filled.
- A local restore measures the real target tables and required indexes.
- Target database and disk usage pass the operating budget; migration transient space is included.
- SELECT-only application access and existing owner RLS are verified.
- Desktop/mobile meal-to-forecast acceptance passes against the imported catalog.
- The release is published only after acceptance; rollback is verified from the preserved package.

## Decision and remaining inputs

The recommended direction is a corrected, compact serving copy on Supabase, with a local full validation step. This is feasible enough to plan for Free, but Free suitability remains conditional on the corrected export and target baseline. A full source-layout mirror is outside the recommended Free design.

Before execution, the remaining inputs are the corrected release/approval manifest, authoritative nutrition and serving rules, source reuse permission, a SELECT-only Azure export account, the chosen Supabase project and its private connection details, and a target capacity reading. There is no need to provide those credentials in chat to complete this strategy.

No data was activated, no full export was generated, no cloud schema was created and no Azure rows were changed. The earlier [catalog quality assessment](azure-nutrition-catalog-assessment-2026-11-06.md) remains the evidence for the current quality blockers. [ADR 0015](../decisions/0015-corrected-nutrition-catalog-migration.md) records the proposed architecture and the correction gate.

## Documentation alignment

Planning 00 and 01 were updated to record the user's correction hold and future-use intent. Planning 03 records the prospective recipe/ingredient/product UX source; 04 records the proposed catalog boundary; 08 records correction, provenance and export safeguards; and 10 preserves the remaining M2 verification gates. The root README and report/decision indexes link the strategy. Model selection, research protocols, course dates and implemented application behavior were not revised.

Planning 06 now carries the execution checklist under M3 and identifies the completed
audit/strategy as M2 evidence. This is tracking and integration planning, not a claim
that the migration has run or that a milestone has closed.
