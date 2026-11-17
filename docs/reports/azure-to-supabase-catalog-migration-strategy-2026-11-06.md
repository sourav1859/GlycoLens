# Azure to Supabase catalog migration strategy

**Latest review: November 14, 2026, America/New_York.** This current strategy supersedes the November 6 sizing and all-whole-recipe assumptions below. It is based on the [updated assessment](azure-nutrition-catalog-assessment-2026-11-06.md) and [aggregate evidence](azure-gold-catalog-audit-2026-11-14.json). No complete export, restore, cloud data import or activation has run.

## November 14 recommendation

Build a **versioned compact food catalog**, selected from the external production database's `gold` schema, in GlycoLens's existing dedicated cloud development project. Keep the two projects' accounts, health records, settings and business data separate. Azure remains unchanged upstream; GlycoLens receives only a validated reference-food release.

The source readiness filter is **`recipes.display_status = 'user_ready'`**, not a `user_ready` column. Select products with the same exact status and `soft_deleted_at IS NULL`; select ready ingredients independently and verify dependency closure. Retain source readiness and a separate GlycoLens validation/publication state. The source tag does not waive the outstanding findings.

### Proposed release contents

| Source / destination concept | Current candidate rows | Retain | Gate / reason |
|---|---:|---|---|
| `recipes` | 33,194 | UUID, title/description, cuisine/meal type, times/difficulty, instructions, declared yield, source/image URL, source status/timestamp | All are unowned catalog rows currently; retain a no-customer-created-row release check |
| `recipe_ingredients` | 264,631 | Line UUID, recipe/ingredient/product IDs, order, raw quantity/unit, normalized grams, preparation, optional/preferred type | All resolve, have positive grams and reference ready ingredients; retain repeated lines |
| `recipe_nutrition_profiles` | 33,194 | Profile UUID, recipe ID, basis, serving mass/yield, five core values, data source/timestamp | 19,111 per_recipe; 14,083 per_serving; no positive serving mass |
| `ingredients` | 5,429 | UUID, names, category/type, USDA ID, five core values, status/timestamp | Includes 3,374 dependency ingredients plus 2,055 standalone search candidates |
| `products` | 11,397 | UUID, name/brand/description, original/canonical GTIN, serving/package fields, five core values, source/image/product URL, status/timestamp | Validate source basis, GTIN and soft-delete state |
| `product_ingredients` | 105,862 | Line UUID, product/ingredient IDs, order, raw/normalized quantity, preparation | Most lines are unquantified; preserve display list without invented amounts |
| Core `nutrition_facts` | 238,988 | Fact UUID, typed entity UUID, nutrient ID, original amount/unit/basis, basis grams, source/confidence/date/timestamp | Calories, carbohydrate, protein, fat and fiber evidence; retain competing bases |
| Compact `data_lineage` | 70,541 | UUID, typed entity UUID, source system, transformation description and ingestion/processing timestamps | Preserve all source associations; review text for unrelated identifiers before export |
| Supporting lookups | 25 cuisines; 122 nutrient definitions; 16 categories; 11,397 category links | Stable IDs, names/codes and selected relationships | Carry cuisine parent closure; drop source retailer category IDs and silver IDs |
| Conversion aids | 26 conversions; 77 active measures | Factor/units, aliases, density/piece/name-pattern rules, approximation/source flags | All measures are approximate; these do not authorize automatic portion conversion |
| Optional active image metadata | 32,200 | Image UUID, recipe UUID, succeeded state, full/thumb path, checksum, source type/timestamp | Host/rights review first; no generation history or binaries |

The five core nutrient codes are `calories-energy`, `total-carbohydrates`, `protein`, `total-fat`, `dietary-fiber`. Definitions are retained as source evidence; the inconsistent 1062/kcal energy mapping must not become a trusted canonical definition. Extra nutrients or product JSON/arrays can be added deliberately after defining their semantics and remeasuring; they are outside these projections.

A dependency-only ingredient package uses 3,374 ingredients: 2,395 referenced by recipes, 1,883 by products, with 904 shared. All selected recipe product references are currently NULL; the exporter must still support product dependencies if this changes. Including all 5,429 ready ingredients is recommended for ingredient search because the additional 2,055 rows add only about **0.25 MiB CSV** to the measured ingredient projection. Inclusion is not publication approval.

Exclude hidden/needs-review records from the initial candidate selection. If a future ready parent references an excluded child, quarantine the parent or explicitly approve that child; never silently drop the line. Exclude source users/customer IDs, vendor/store/price data, health/meal records, source business permissions, silver/bronze records, generated prompts, embeddings, medical/diet-rule claims and unrelated tables.

### Measured sizes and uncertainty

All MiB below are binary (1,048,576 bytes). These are explicit compact projections, not source-table mirrors.

| Projection | Rows | Estimated CSV MiB | Estimated gzip MiB |
|---|---:|---:|---:|
| Recipes | 33,194 | 22.63 | 6.62 |
| Recipe ingredient lines | 264,631 | 41.92 | 16.55 |
| Recipe profiles | 33,194 | 5.51 | 2.08 |
| All ready ingredients | 5,429 | 0.67 | 0.23 |
| Ready products | 11,397 | 3.97 | 1.39 |
| Product ingredient lines | 105,862 | 16.19 | 5.86 |
| **Six-table subtotal** | **453,707** | **90.89** | **32.73** |
| Core nutrient facts | 238,988 | 45.25 | 13.48 |
| Compact lineage | 70,541 | 14.44 | 4.11 |
| All supporting lookups/conversion aids | 11,663 | 1.32 | 0.28 |
| **Candidate package with evidence** | **774,899** | **151.90** | **50.61** |
| Optional active image paths | 32,200 | 11.55 | 3.97 |
| **Including optional paths** | **807,099** | **163.45** | **54.58** |

Unrounded totals are **95,301,925 CSV / 34,324,711 gzip bytes** for six tables, **159,274,334 / 53,063,614 bytes** including evidence/support, or **171,387,566 / 57,227,138 bytes** including optional paths. The projection details and measured sample sizes are in the evidence JSON.

Method: one repeatable-read read-only sizing snapshot; exact row counts, sums of serialized JSON bytes and runtime composite-record sizes across each full projection; native PostgreSQL `COPY (...) TO STDOUT` CSV samples of at most 1,500 rows ordered by a fixed MD5 of the source UUID; in-memory gzip, then linear scaling by row count. CSV uses UTF-8, no sample header and explicit `\\N` NULL. MD5 ordering spreads the sample across UUIDs but supplies no confidence interval or guaranteed representative compression. Small supporting tables were measured in full. Compression ratios can change with ordering, chunk size and real data; final archives must be measured.

For the package with evidence, the measured runtime composite-record sum is **120,113,587 bytes (114.55 MiB)** and its JSON serialization sum is **302,528,916 bytes (288.51 MiB)**. Neither is the destination heap/index size. These different representations illustrate why gzip size cannot predict database allocation.

Plan approximately **130–190 MiB CSV / 45–70 MiB gzip**, plus manifest/checksums and optional paths. Reserve at least **1 GB** of private local working space for files, validation/quarantine and logs; a local restored database needs additional space. Do not retain row samples in Git.

The six full source tables currently occupy **417,759,232 bytes (398.41 MiB)** with existing indexes. Adding the full source fact table alone adds **561.86 MiB**. The 16 measured source relations including lineage, lookups and image metadata occupy **1,157,054,464 bytes (1,103.45 MiB)**. These full-source allocations include unselected rows, all columns/indexes and possible bloat. Do not multiply physical size by ready-row percentage or call those numbers a filtered export size. [PostgreSQL size functions](https://www.postgresql.org/docs/16/functions-admin.html)

### Current destination and capacity decision

Read-only MCP inspection identified the existing **Glycolens** cloud development project, PostgreSQL **17.11**. At approximately 11:07 p.m. EST November 14, `pg_database_size(current_database())` was **15,414,963 bytes (14.70 MiB / 15.41 decimal MB)**; `public` had 18 tables and no `catalog` schema existed. No application rows, Auth records or secrets were fetched.

Supabase currently advertises **500 MB database size**, **1 GB file storage** and shared CPU/500 MB RAM on Free. This does not establish this organization's actual subscription, other-database usage or physical disk headroom; those dashboard readings remain an execution gate. [Pricing](https://supabase.com/pricing), [database versus disk size](https://supabase.com/docs/guides/platform/database-size)

Use the existing conservative operating gate:

```text
remeasured existing whole database bytes
+ measured incremental catalog tables, indexes and release metadata
+ 100,000,000 bytes application-growth reserve
<= 400,000,000 bytes
```

At the observed baseline, that permits at most **284,585,037 bytes (271.40 MiB)** of incremental catalog under this project guardrail. For planning, allow roughly **180–260 MiB** for the indexed compact package with evidence, and another **15–25 MiB** if optional image metadata is retained. These are engineering allowances, not measured restores or reserved capacity. At 260 MiB, baseline + catalog + reserve is about **388.0 decimal MB**; 285 MiB would total about **414.3 MB** and fail this gate. Peak staging/index/WAL disk usage is a separate check.

Thus Free is **plausible, not proven** for the compact selection. A full source-schema mirror is unsuitable. If the measured restore exceeds the gate, first omit optional paths and unnecessary indexes, or publish a smaller approved release; changing plan is a separate decision. The November 6 statement that destination baseline was unknown is now historical. No physical disk/organization-wide quota or actual import size has been measured.

### Proposed target contracts

Use an application-owned, initially unexposed `catalog` schema with recipes, recipe_lines, recipe_profiles, ingredients, products, product_lines, core_source_facts, source_lineage, lookups, release_manifest and validation_results. This is a design, not applied DDL. Keep canonical application `public`, managed `auth/storage` and source-production `gold` separate.

Preserve source UUIDs and source relationship UUIDs. Each record also needs `release_id`, source display status, separate validation state/reason codes, import timestamp and transformation/calculation version. Distinguish singular fact entity types from plural lineage entity types through an explicit mapping; otherwise valid lineage disappears in joins. Retain original source identifiers only as provenance, without foreign keys into silver/bronze, vendors or customer records.

Keep raw profile and fact values alongside any independently validated canonical values, their exact units/bases, selected evidence IDs and precedence reason. Preserve numeric precision and NULL-versus-zero. Do not deduplicate repeated recipe lines or competing fact bases. Do not use source confidence scores as GlycoLens verification.

Keep copied recipe/profile servings separate until conflicts are resolved. For a validated whole-recipe profile:

```text
consumed nutrient = whole-recipe value * consumed servings / authoritative recipe yield
```

For a validated per-serving profile:

```text
consumed nutrient = per-serving value * consumed servings
```

For validated mass-based food facts:

```text
consumed nutrient = source value * consumed grams / verified source basis grams
```

Do not divide a per-serving value again, invent cooked mass, treat all product values as per-serving or apply one global energy repair. `public.foods` currently requires a gram basis; recipe serving-based logging needs a reviewed forward contract/adapter change before connection to that workflow. Preserve immutable save-time meal facts, source release and personal/simulation workspace boundaries.

Start with primary keys, relationship lookup indexes, source/entity evidence indexes, validated canonical GTIN lookup and one justified name-search strategy. Do not mirror production GIN/trigram/instruction/source indexes indiscriminately. An unexposed schema plus a least-privileged backend read role is preferred; revoke browser-role access by default. If deliberately exposed later, define explicit grants and RLS and verify them with application credentials. Limit import/publication writes to the migration owner; never disable existing application RLS.

### Concrete migration runbook

1. **Freeze selection and source rules.** Record corrected/approved source release, exact recipe/product/ingredient UUID sets, dependency closure, licence/reuse permissions and field/basis/yield precedence. Keep generated/estimated and unresolved records quarantined. The request authorizes this audit/strategy, not publishing source-tagged records without those checks.

2. **Prepare a separate exporter.** Use private source-only environment names (for example `AZURE_CATALOG_SOURCE_*`) and separately configured `GL_CATALOG_TARGET_*`; never replace GlycoLens `DATABASE_URL` with production Azure settings. Verify exact source database/schema and exact destination project before every run. Prefer a dedicated SELECT-only source identity for repeatable exports; the supplied account was forced read-only for this audit, but that does not change its account privileges. Require TLS, timeouts and secret-redacted logs.

3. **Capture one consistent source snapshot.** Begin `REPEATABLE READ READ ONLY`; determine all selected IDs/dependencies inside it and export explicit projections with client-side `COPY (SELECT ...) TO STDOUT`. No server-file COPY, DDL, triggers, production functions, writes or replication slots are required. Stream tables serially; coordinated shared snapshots are an advanced alternative. A lost snapshot invalidates the package: restart rather than mixing retries from different source states. Keep the transaction bounded and abort on timeouts. [PostgreSQL COPY](https://www.postgresql.org/docs/16/sql-copy.html)

4. **Create the private release package.** Write per-table UTF-8 CSV.gz plus manifest, approved/rejected ID sets, column/type/order contract, source/correction version, snapshot observation, counts, SHA-256 of compressed and canonical decompressed streams, basis rules and quality totals. Specify CSV NULL `\\N`, quoting, encoding and exact JSON/array representation; distinguish a literal text `\\N` using PostgreSQL's CSV quoting. Add headers deliberately and account for their small size. Review lineage transformation text for unrelated identifiers. No credentials, source customers, store prices or health data enter the package.

5. **Validate and measure outside the running app.** Restore to an isolated disposable PostgreSQL 17 validation database, or a separately authorized cloud scratch target. This does not reinstate local Supabase as the app environment. Verify manifest hashes, expected counts, UUID/type uniqueness, FKs, canonical barcode collisions, no excluded records and correct ordered/optional recipe lines. Independently check source identity, calories/units, profile/fact precedence, yield, NULL/zero, negative values, estimated/generated flags and serving scaling. Recreate the exact intended indexes; measure table/index totals and database growth. A fixture or count match cannot establish food accuracy.

6. **Preview cloud changes and recheck headroom.** Produce reviewed forward catalog DDL through the existing versioned migration workflow; verify installed CLI help/version and explicit cloud target. The current CLI v3 defaults changed, so do not reuse unverified v2 target flags. No schema SQL is applied by this report. Re-read destination baseline, plan/dashboard usage, organization quota and physical disk/staging/WAL allowance. Apply the operating gate using the restored indexed size. [CLI v3 changes](https://supabase.com/changelog/supabase-cli-v3)

7. **Import an unpublished release.** Use a native direct connection, or session pooling when IPv4 requires it, with a controlled import identity. Create only reviewed catalog structures. Load lookup/base rows before dependent lines, profiles, facts and lineage. Client-side COPY is appropriate; do not import the whole production schema or use the dashboard as the main bulk loader. Start with one importer and measured 5,000–20,000-row commits; resume by manifest/table/chunk/checksum, never by assumed row order. Make retries idempotent, verify payload equality on conflicts and never overwrite a published release silently. A target import resumes from the immutable package and does not need to hold Azure open. [Connection guidance](https://supabase.com/docs/guides/database/connecting-to-postgres), [import guidance](https://supabase.com/docs/guides/database/import-data)

8. **Verify before publishing.** Compare every manifest count/hash, FK/quality result and measured database size. Verify least-privileged reads, rejected browser writes and unchanged per-user RLS. Wire only admitted foods into the application adapter; verify search, valid/invalid barcode, ingredient edits, repeat ingredients, both recipe bases, conflicting yield, incomplete nutrients, provider outage and immutable saved totals. Exercise personal and simulation paths separately. New catalog data does not waive real-source forecast eligibility or prove model accuracy.

9. **Activate and retain rollback.** Publish an approved release marker atomically only after acceptance; leave rejected content unavailable for calculation. Keep the exact package and schema privately as rollback evidence. If there is capacity for two releases, use a verified pointer switch; otherwise use a planned maintenance/fallback transition without exposing partial cross-table updates. Revoke an affected release from discovery without changing historical meal/forecast snapshots. Do not hold two full copies merely for convenience.

10. **Refresh deliberately.** Prefer named snapshots while upstream correction continues. A delta refresh must include explicit deletions/soft-deletes, status transitions and dependency changes; `updated_at` alone is inadequate. All selected recipes currently share the same update timestamp, which is not a release certificate. Repeat source-accuracy, imported-size and application gates for every release.

### Execution status and gates

**Completed:** source connection/read-only proof, gold catalog metadata/profile scans, exact candidate/dependency counts, nutrient/GTIN/provenance checks, projected size measurements, current target database baseline, documentation updates.

**Not performed:** full private release export, original-source/licence certification, canonical nutrition correction, restored target/index measurement, cloud DDL/data writes, feature activation, paid plan purchase or acceptance closure. These remain M3/P07 work. The current catalog is a promising migration candidate, not an approved ready-to-serve nutrition release.

## Historical strategy — November 6, 2026

The remaining sections preserve the earlier full-catalog study. Their counts, 737.72 MiB source footprint, 113.95/38.69 MiB six-table estimates, 150–250 MiB target allowance, all-whole-recipe assumption and unknown destination baseline are dated November 6 observations; use the November 14 analysis above for new migration decisions.

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
