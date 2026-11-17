# Azure nutrition catalog assessment

**Latest review: November 14, 2026, America/New_York.** The current audit below supersedes the November 6 counts and basis assumptions. The original assessment is retained as dated evidence. [Aggregate measurements](azure-gold-catalog-audit-2026-11-14.json) and [updated migration strategy](azure-to-supabase-catalog-migration-strategy-2026-11-06.md) accompany this review.

## November 14 decision

The external production catalog is reachable and has a substantially improved ready subset, but **`user_ready` is a source workflow label, not GlycoLens nutrition approval**. Copy candidates into a private validation release; publish only records that pass source identity, nutrient basis, provenance, yield and application checks. No source adoption, complete export, cloud import or application activation was performed.

### Scope and method

- The supplied Azure database belongs to another project. Only `gold` catalog data was queried; PostgreSQL system catalogs supplied metadata, sizes and connection settings. A foreign-key definition mentions `silver`, but no `silver` or `bronze` data was read.
- PostgreSQL **16.15**, TLS **1.3**, `default_transaction_read_only=on` and `transaction_read_only=on` were verified. Queries used a 20-second statement timeout, two-second lock timeout and short transactions. The sizing pass used one bounded `REPEATABLE READ READ ONLY` snapshot.
- Inspected schema metadata across `gold`, then profiled the food entities, relationships, nutrient definitions/facts, lineage, categories, cuisines, conversions, measures and selected image metadata. No customer, account, health, store-price, secrets or unrelated business rows were read.
- Counts/quality checks are full aggregate scans of the stated selections. Native CSV samples were capped at 1,500 rows per projection, compressed in memory and discarded. No sampled food records or complete export files were retained. Private scripts and aggregate receipts are under ignored `.cache/azure-nutrition-audit/2026-11-14/`.
- Azure observations were approximately **11:00–11:07 p.m. EST on November 14** (04:00–04:07 UTC November 15). Separate profiling transactions are not a frozen release; remeasure at export. Ready-recipe count remained 33,194 at the final check.

### Correct selection and counts

There is **no column named `user_ready`** in `gold.recipes`. The exact selection is:

```sql
SELECT count(*)
FROM gold.recipes
WHERE display_status = 'user_ready';
```

Apply exact status equality, rather than a substring/tag search. Products additionally require `soft_deleted_at IS NULL`.

| Entity | Entire table | Ready selection | Other status |
|---|---:|---:|---|
| Recipes | 42,142 | **33,194** | 8,948 needs_review |
| Ingredients | 69,145 | **5,429** | 63,716 hidden |
| Products | 12,968 | **11,397** | 1,571 needs_review; none currently soft-deleted |
| Recipe ingredient lines | 350,393 | **264,631** linked to ready recipes | Preserve line IDs/order |
| Recipe profiles | 42,140 | **33,194** linked to ready recipes | One per selected recipe |
| Product ingredient lines | 117,025 | **105,862** linked to ready products | Preserve line IDs/order |
| Nutrition facts | 1,427,608 | **238,988 core facts** for ready recipes/products/all 5,429 ready ingredients | Five required nutrient codes; not all micronutrients |
| Data lineage | 146,174 | **70,541 compact lineage rows** for that selection | Keep every relevant source association |

All ready recipes have a title, positive declared servings, a nonempty instruction array, a profile and ingredient lines. None has a nonnull `created_by_user_id`. Their 264,631 lines resolve to **2,395 distinct ingredients**, all ready, with positive quantity and normalized grams. No selected recipe line references a product or has an unresolved ingredient.

Ready products reference **1,883 distinct ingredients**. The combined recipe/product dependency closure is **3,374 ingredients**; the overlap is 904. A minimal connected copy needs those 3,374. Including all 5,429 ready ingredients adds 2,055 standalone search candidates at very little storage cost; it does not approve their nutrition.

### Critical findings

**1. Recipe basis has changed since November 6.** There are **19,111 per_recipe profiles** and **14,083 per_serving profiles**. The latter all have profile servings = 1 and generated-recipe source labels: 7,809 medium-confidence, 6,272 high-confidence and two other Claude-generated records. Do not describe all profiles as whole-recipe totals or divide every profile by recipe servings. No selected profile has a positive `serving_size_g`; raw ingredient mass does not establish cooked yield.

Of 33,194 profiles, **31,851** have all five nonnegative core values; **1,343** are incomplete. There are **299** recipe/profile yield conflicts, all in the per_recipe group. A broad energy screen flags **688** profiles; **20** have fiber above total carbohydrate. These flags overlap and are review signals, not error diagnoses. A simple complete-core/yield-agreement screen leaves 31,565; additionally excluding generated profile sources and those two plausibility flags leaves **16,905 structural candidates**, still without source identity/licence approval.

**2. Positive grams do not establish trustworthy reconstructed nutrition.** All ready recipe lines now have positive normalized grams, versus widespread missing grams in the earlier full-catalog audit. However, only **143 ready recipes** have all five nonnegative ingredient nutrients on every line. **4,934** have enough nonnegative ingredient carbohydrate and gram data for a simple reconstruction; **1,209** differ from the stored profile by more than max(5 g, 20%). This calculation includes every line, including optional lines, and assumes ingredient per-100-g semantics; investigate source identity, preparation, optional-ingredient policy and recipe basis before using it as a validator. Five lines exceed 10 kg and need review. Gram-unit quantities agree with normalized grams within 0.01 g.

**3. Ready ingredients still have missing and estimated facts.** Across all 5,429 ready ingredients, **2,862** have all five nonnegative main-column nutrients and **six** have negative carbohydrate. In the 3,374-ingredient dependency closure, only **1,713** have all five, **475** lack carbohydrate, **1,470** lack fiber and **three** have negative carbohydrate. Do not silently fill NULL with zero, clip negatives or infer nutrition from food names.

Lineage identifies **1,292 ready ingredients with LLM_ESTIMATED** source associations and two with user-generated associations. Within the dependency closure, 609 have LLM_ESTIMATED lineage; nutrient facts identify **634** dependency ingredients with at least one LLM_ESTIMATED fact. These sets differ because lineage and fact-level provenance serve different purposes. Preserve both; do not promote estimates as verified nutrition.

For ready ingredients, fact rows can fill 31 missing calorie, 32 carbohydrate, 37 protein, 52 fat and 65 fiber main-column values. Conversely, nonnull main columns disagree with fact values by over 0.01 for 40 calorie, 40 carbohydrate, 26 protein, 27 fat and six fiber rows. This is evidence for explicit field-level precedence, not automatic fallback. The historically confirmed chicken/apple mapping remains present but is now **hidden**, so the status filter excludes that example; it does not establish correctness of the remaining mappings.

**4. Recipe profiles and facts are not interchangeable.** Whole-recipe calorie facts disagree with profiles by more than 0.01 for **251 recipes**; the other core nutrients also have disagreements. Per-serving facts match their profiles where comparable values exist. There are 31,869 selected recipes with all five nonnegative core fact codes versus 31,851 with complete profile columns. Preserve profile values and fact evidence independently until a source-specific precedence rule is approved.

The current Calories/Energy definition still combines USDA nutrient ID **1062** with unit **kcal**, the inconsistency documented in the historical audit. Do not apply a blanket 4.184 conversion. Numeric plausibility cannot resolve an ambiguous source unit. USDA also documents source-type-specific energy representations; validation must use the actual source nutrient identifier and unit. [USDA Foundation Foods documentation](https://fdc.nal.usda.gov/Foundation_Foods_Documentation/)

**5. Products are useful candidates but need serving and barcode gates.** Of 11,397 ready products, **10,740** have five nonnegative core columns, **9,772** have positive serving grams and **9,132** have both. **247** have serving grams above package mass, **35** have fiber above carbohydrate and **1,179** trigger the broad energy screen.

All have digit-format GTINs of supported length, but only **9,691** pass the check digit; **1,706 fail**. There are no exact or zero-padded canonical duplicate groups in this selection. All `normalized_gtin` values agree with `gtin` after zero padding; `barcode` is unpopulated. Preserve original and canonical text forms, including leading zeros.

The intersection of valid GTIN, complete nonnegative core columns and positive serving grams contains **8,016 products**. Adding the fiber, package-mass and broad energy screens leaves **6,774 candidates**. Neither number is a certified usable count: main-column basis, source label and rights still require validation.

Facts mix `serving`, `per_serving` and `100g`. **778 products have both serving spellings; 12 have both 100g and serving facts.** Main columns conflict with some fact values, and all facts lack positive `per_amount_grams`. A known serving mass helps only after the actual nutrient basis is resolved. Do not divide a per-100-g product by its serving mass.

All ready products have ingredient lists, but only **21,048 / 105,862 lines** have positive quantities/grams. Use the other **84,814** lines for ordered display/context; they cannot support nutrition reconstruction.

**6. Provenance joins have different entity conventions.** `nutrition_facts.entity_type` uses singular `recipe/ingredient/product`; `data_lineage.entity_type` uses plural `recipes/ingredients/products`. Use an explicit mapping. With the correct join, **every selected ready recipe, ingredient and product has lineage**. Multiple distinct lineage sources occur for 14,408 recipes, 1,783 products and two ready ingredients. Null `recipes.source_type` / `products.source_system` do not mean lineage is absent, and a source name alone is not a licence or verification stamp. Only 107 ready recipes have nonblank source URLs.

**7. Supporting capabilities need limits.** The catalog has 25 cuisines (23 referenced by ready recipes), 16 product categories, 11,397 selected category mappings and 122 nutrient definitions. `ingredient_synonyms`, `data_quality_scores` and `product_quality_scores` remain empty. Do not present them as executed quality scoring or synonym search.

There are 26 generic unit conversions and 77 active name-pattern measures: 27 densities and 50 piece weights, all marked approximate, with no ingredient-ID-specific measures. They are potential review aids, not proof of recipe conversion correctness. Preserve already-normalized grams and require explicit policy before editing cups/pieces.

**8. Recipe images use a separate path contract.** Only 157 ready recipes have a direct image URL, but **32,200** reference a succeeded active image row: 23,230 generated_live and 8,970 ingested_legacy. Copying image paths/checksums is optional; first establish the asset host, access and reuse rights. Do not copy prompts, generation parameters, error history or binary images. Path strings do not establish public accessibility or measure image-file bytes. Allergen, dietary and health-condition rule tables are outside initial migration scope and cannot establish allergy/condition safety.

### What can be used

- **Search/detail candidates:** 33,194 recipes, 5,429 ingredients and 11,397 products with the dependencies above, imported privately with per-record validation state.
- **Calculation candidates:** independently verified nutrient facts with known basis; the structural subsets above help prioritize review but do not authorize publication.
- **Estimated/generated content:** separate, clearly labeled research content if deliberately accepted later; never silently treated as verified provider facts.
- **Forecasting/research:** this catalog supplies food descriptions and nutrition, not measured CGM outcomes or evidence of forecasting accuracy. Keep research datasets, personal records and simulation history separate.

The existing `public.foods` and `private.meal_facts` contracts calculate from grams divided by `nutrient_basis_g`, and freeze source snapshots. Ingredients/products can enter that path only after verified gram-basis normalization. Recipe serving fractions require an explicit serving contract or verified cooked mass; do not invent a 100-g serving.

### Review and remaining work

Reviewed Plans 00/01 for current status, 03 for food/recipe UX, 04 for schema/provider/gram contracts, 06 for M3 migration tracking, 08 for provenance and production isolation, 17 for P07 release admission, and 19 for personal/simulation boundaries. Plans 00/01/03/04/06/08/17 and ADR 0015 are updated with the audited selection and remaining gates. Plan 19 is unchanged: shared reference food data must not import or reclassify source-project users, meals or simulation data.

The next step is an approved release manifest plus authority/rights rules, then a private export and measured restore under the migration strategy. This audit does not close P07, M2/M3 acceptance, source correction, licence or clinical gates.

## Historical assessment — November 6, 2026

The following section records the earlier full-catalog snapshot. Its counts, missing-gram observations, all-whole-recipe basis assumption and product/category coverage are historical; use the November 14 selection above for new work.

**Assessment date:** November 6, 2026, America/New_York.

**Scope:** Read-only access and suitability assessment of the supplied PostgreSQL database, schema `gold`. This is a proposed data-source assessment, not an implemented integration or a change to approved milestone gates.

## Finding

Database access succeeded. The catalog could substantially support GlycoLens recipe search, ingredient matching, packaged-food lookup, nutrition review and serving calculations. It should be used through a validated catalog adapter and a reviewed subset. Its current completeness does not establish nutritional correctness. A bulk import or direct substitution for verified nutrition would propagate confirmed mapping errors, ambiguous energy values, missing quantities and estimated facts.

No more connection details are needed for this assessment. Before implementation, the important missing information is the ingestion/transformation specification, authoritative serving/energy rules, and permission to reuse the underlying source content.

## Access and audit boundaries

- The supplied discrete host, port, database and username fields authenticated successfully. The pasted connection URL contains whitespace and unencoded password characters; keyword connection parameters avoided that ambiguity.
- TLS 1.3 was negotiated. SSL was required, as requested; this audit did not establish certificate hostname validation with `verify-full`.
- PostgreSQL confirmed both `default_transaction_read_only=on` and `transaction_read_only=on`. Every query ran in a read-only transaction, with a 20-second statement timeout and two-second lock timeout. Connections were closed after each batch.
- No database rows, schemas, indexes, grants or server configuration were changed. No store-product rows, prices, customer records, health profiles, meal logs or credentials tables were queried. Schema discovery returned table names only for unrelated tables.
- The supplied account can create databases and roles. A future integration should use a dedicated SELECT-only catalog account; the account's ordinary privileges are broader than this audit's enforced read-only sessions.
- Private scripts, metadata, aggregate query results and a small number of catalog examples remain under ignored `.cache/azure-nutrition-audit/`. Credentials were supplied to subprocesses in environment variables and were not written into those files.
- Counts below are exact query results, not planner estimates. Queries ran in separate transactions against a live database; they are not one database-wide point-in-time snapshot. Population statistics may change after this assessment.
- One initial broad distinct-count aggregation timed out. It was replaced with a small sample and then a simpler successful population aggregation; no timeout or production setting was increased.

## What GlycoLens needs

The current application requires a food identity and source, an explicit nutrient gram basis, consumed grams, and five nonnegative nutrient values: calories in kcal, total carbohydrates, protein, fat and fiber in grams. The save transaction recalculates totals from stored facts and preserves food-source snapshots. Missing required nutrients block saving and forecasting.

For a recipe, the application additionally needs ingredient identities, quantities and units, ingredient-to-gram conversions, the recipe yield/serving count, preparation state and a clear distinction between whole-recipe and per-serving nutrition. A recipe title match alone is insufficient to identify the meal someone actually prepared.

For packaged products, the important extra fields are GTIN/barcode, brand, package identity, serving description, serving mass and whether nutrients describe a serving or 100 g. Store-level pricing is unnecessary for this workflow.

These requirements come from [product planning](../planning/GlycoLens_03_App_Product_Spec_and_UX.md), [architecture planning](../planning/GlycoLens_04_Tech_Stack_and_System_Architecture.md), [food normalization](../../backend/app/services/nutrition/providers.py), and the [atomic meal-save implementation](../../supabase/migrations/20261014000100_m2_application_contract.sql).

## Available catalog and project fit

| Table or group | Exact observed scope | Potential GlycoLens use | Main qualification |
|---|---:|---|---|
| `recipes` | 42,142 recipes | Search/select an existing recipe; show instructions and yield | All have titles, instructions and positive serving counts; source metadata is incomplete on this table |
| `recipe_ingredients` | 416,162 links covering all 42,142 recipes | Editable ingredient review; deterministic nutrition calculation | All link to ingredients; none link directly to products; only 344,710 links have positive normalized grams |
| `recipe_nutrition_profiles` | 42,140 profiles | Whole-recipe nutrition and serving-based portions | 38,684 have all five required nutrients; every profile is `per_recipe`; none has a positive serving mass |
| `ingredients` | 69,115 ingredients | Food matching, database-grounded nutrients, user-edited recipes | 35,027 have all five required nutrients; origin and name-to-source matching need validation |
| `products` | 12,329 products | Barcode/search and branded-food nutrition | 12,328 have a populated barcode; 9,147 have complete nonnegative core nutrients and a positive serving mass |
| `product_ingredients` | 163,610 links covering all 12,329 products | Ingredient-list display and composition context | None has positive normalized ingredient grams; not a basis for rebuilding product nutrition |
| `nutrition_facts` and `nutrition_definitions` | 1,284,422 facts for recipe/ingredient/product entities | Explicit nutrient identity, units, basis and data source | Multiple basis spellings, no positive numeric basis grams, and an energy-definition mismatch |
| `data_lineage` | Every current catalog entity has a lineage match | Retain upstream source labels; exclude or label estimated nutrition | Some entities have multiple sources; lineage alone does not establish which source supplied every field |
| `ingredient_synonyms` | 0 rows | Intended synonym matching | No populated synonym service is available from this table |
| `data_quality_scores` | 0 rows | Intended quality ranking | Quality columns/tables cannot be treated as executed validation |

The fact totals are 836,377 ingredient facts, 116,945 product facts and 331,100 recipe facts. Products have 108,492 facts labeled `serving`, 8,243 labeled `per_serving`, and 210 labeled `100g`. Ingredient facts use `per_100g`; recipe facts use `per_recipe`. Every fact in these groups lacks a positive `per_amount_grams`. Text bases can sometimes be interpreted deterministically, but products need the appropriate serving mass joined from their catalog record.

## Findings that affect correctness

### 1. Confirmed incorrect ingredient-to-USDA mapping

The ingredient named **Boneless Chicken Breast -Ounce Skinless** has `usda_fdc_id=1750340`. Its stored values include 15.65 g carbohydrate, 0.15 g protein and 2.08 g fiber per 100 g. A direct check of the [official USDA API record](https://api.nal.usda.gov/fdc/v1/food/1750340?api_key=DEMO_KEY), using the public demo key, identifies that record as **Apples, fuji, with skin, raw** and returns the matching nutrient values.

This proves at least one semantically incorrect food mapping. It does not measure the prevalence of all incorrect mappings. A USDA identifier and a `USDA` source label are insufficient quality gates. The original source description, food type and preparation state need to be compared with the catalog name before promotion.

### 2. Energy definitions and product energy values require review

`nutrition_definitions` maps Calories/Energy to USDA nutrient ID **1062** while declaring the unit **kcal**. The [official USDA API record for food 171445](https://api.nal.usda.gov/fdc/v1/food/171445?api_key=DEMO_KEY) reports nutrient 1062 as energy in **kJ**, and 1008 as energy in **kcal**. USDA's [Foundation Foods documentation](https://fdc.nal.usda.gov/Foundation_Foods_Documentation/) also explains its newer energy representations; a complete importer cannot assume one energy ID covers every source type.

Examples in the database include a 28 g mozzarella serving with 22.3997 stored calories, 7 g protein and about 6 g fat, and a 445 g chicken-chili serving with 1,465.385 stored calories, about 50 g carbohydrate, 23 g protein and 4 g fat. These values warrant source-label comparison. Some other product calories appear plausible, so **do not divide all calories by 4.184** or apply any other blanket repair.

A deliberately broad consistency screen flags stored energy below half or above twice `4*carbs + 4*protein + 9*fat`, among records with available nonnegative macros and at least 20 calculated kcal. It flags 1,199 of 10,527 eligible products and 2,457 of 41,481 eligible recipe profiles. These are investigation flags, not a validated count of incorrect foods: fiber, polyols, alcohol, source methods and rounding can affect reconciliation.

### 3. Recipe yield and gram weights are insufficient for direct gram-based serving

- All 42,140 profiles are whole-recipe totals, not per-serving facts.
- All 42,140 lack a positive `serving_size_g`.
- Recipe and profile serving counts disagree for **442 recipes**. For example, one sweet-potato recipe has six servings on `recipes` and four on its profile; dividing by the wrong field changes every per-serving nutrient.
- **71,452 of 416,162 ingredient links** lack normalized grams; 71,254 also have a missing or nonpositive quantity. Available units are `g` or null, so the table does not supply a general cups/spoons/pieces conversion dictionary.
- Only **19,912 recipes** have positive normalized grams on every linked ingredient.
- Only **120 recipes** have both positive grams and all five nonnegative required ingredient nutrients on every line. This is a structural upper bound for strict ingredient-based reconstruction, not a quality-certified subset.
- A carbohydrate-only reconstruction is possible for 2,846 recipes under analogous completeness rules. Of those, 75 differ from stored recipe carbohydrate by more than the greater of 5 g or 20% of the stored total. This requires investigation of yield, calculation rules, optional ingredients and source facts.

Whole-recipe totals can support consumed-serving fractions after the authoritative yield is established. They cannot be relabeled as per-100-g values. Summed raw ingredient mass also does not establish cooked serving mass; cooking gain/loss and drained components need a defined policy.

### 4. Missing values, true zeros and estimated facts are mixed

- Only **35,027 / 69,115 ingredients (50.7%)** have all five current application nutrients.
- **157 ingredient records have negative carbohydrates**, also present in the fact table. Reject them from the current nonnegative application contract; do not silently clip them.
- For **Rotisserie Chicken Breasts**, the catalog omits carbohydrate and fiber. The linked [USDA record 171445](https://api.nal.usda.gov/fdc/v1/food/171445?api_key=DEMO_KEY) explicitly provides zero for both. This confirms a zero-versus-missing discrepancy in this example; it does not justify filling every null with zero.
- Current-entity lineage identifies **9,945 ingredients with `LLM_ESTIMATED` lineage**, including 5,422 with complete core columns. Another 25 have user-generated lineage. These are source categories to distinguish, not proof of accuracy.
- The `ingredients.source_type` values such as plant, dairy and animal describe food origin, not whether nutrition is verified. Use fact-level source information and lineage for provenance.

The existing GlycoLens boundary says nutrition must not be invented by the recipe language model. Importing upstream estimated facts as verified facts would undermine that boundary even if the application itself never asks an LLM to generate nutrients.

### 5. Barcode coverage is useful but needs validation

All 12,328 populated GTINs have 12 or 13 digits and no exact duplicates were found. However, **1,601 fail their standard GTIN check digit**. Digit-only validation alone is insufficient.

Preserve leading zeros and define UPC-A/EAN equivalence before lookup. Exact uniqueness does not rule out equivalent zero-padded codes. The assessment did not establish package-variant equivalence for every code.

Of 12,329 products, 10,552 have positive serving grams, 10,526 have all five required nutrient values, and **9,147 (74.2%)** have both complete nonnegative core values and positive serving grams. This last count is an availability upper bound, before source, energy, barcode and other plausibility checks. There are also 296 products with serving mass greater than package mass, and 34 with fiber above total carbohydrate.

### 6. Provenance is recoverable, but not uniformly on the main records

Every recipe has null `source_type`; only **145 / 42,142** have a nonblank source URL. Every product has null `source_system`. Nevertheless, `data_lineage` matches every current recipe, ingredient and product, and nutrient facts retain sources such as USDA, Open Food Facts batches and recipe datasets.

Source names are not automatically licences, verification stamps or field-level precedence rules. There are multiple distinct lineage sources for 1,826 products, 531 recipes and 13 ingredients. An integration needs a documented rule for selecting the source for each imported field and retaining the original values and basis.

## Recommended use in GlycoLens

| Capability | Recommendation |
|---|---|
| Search existing recipes | Strong candidate. Return titles, ingredients and yield; require user confirmation and expose unresolved nutrition |
| Ingredient search | Use a curated subset with source-name matching, preparation-state checks, explicit basis and nonnegative required nutrients |
| Packaged-food search/barcodes | Use verified GTINs and source-specific serving normalization; preserve manufacturer/variant identity |
| Recipe portions | Start with verified serving fractions; add cooked-mass support only with a defensible yield/weight |
| Arbitrary user recipe text | The database grounds food facts; it does not itself parse unknown recipe text. Keep manual entry or separately verified extraction |
| Product ingredient quantities | Use the list for display/context. Do not infer quantities or reconstruct nutrition from the currently unquantified links |
| Similar personal meals | Continue using the user's own saved meals and available outcomes; a general recipe catalog is not personal response evidence |
| Glucose model training/evaluation | These catalog tables provide no measured post-meal CGM/insulin outcomes and do not replace the research datasets |
| Pricing/store selection | Excluded and unnecessary for the current capstone scope |

Recommended application boundary: **Azure catalog -> read-only backend adapter -> validation and basis conversion -> versioned food snapshot -> existing local application meal transaction -> existing forecasting adapter**.

Keep session identity, glucose/insulin context, meal history, forecasts and outcomes in the application database. Do not send them to the catalog database. Keep database credentials server-side. Use a short connection pool, query timeouts, parameterized search, bounded result sets and a local validated cache for demo reliability.

For gram-based food facts, normalize only when basis mass is known:

`nutrient_per_100g = source_nutrient * 100 / source_basis_grams`

For a verified whole recipe:

`consumed_nutrient = recipe_total * consumed_servings / authoritative_recipe_servings`

Supporting the second expression directly requires an explicit serving-based representation or a verified conversion to mass in GlycoLens. Do not fabricate a 100-g mass for a serving or recipe to satisfy the current schema.

The existing `foods.source` is flexible enough to label a new provider. An adapter still needs to implement source IDs, gram-basis normalization, provenance, immutable save-time snapshots and failure behavior. Structured recipes additionally need an appropriate serving/yield contract. This has not been implemented by this assessment.

## Implementation order and acceptance evidence

1. Obtain the ingestion specification and resolve the confirmed food mapping, energy definition and serving-count conflicts. Establish which columns/facts are authoritative per source and how explicit zeros were handled.
2. Define a small reviewed pilot, for example a few dozen common ingredients, several recipes and packaged foods. Verify names, preparation states, labels, units, zeros and barcodes against their original sources. Count completeness separately from quality approval.
3. Add the read-only adapter and normalization contract; keep existing providers as optional fallbacks. Cache only reviewed facts with source IDs, units, basis, source timestamps, validation status and a calculation version.
4. Verify a measured ingredient portion, a product serving, a recipe serving fraction, ingredient edits, repeat ingredients, missing nutrients, negative values, conflicting servings, invalid/unknown barcodes and database outage behavior. Ensure grams/servings are applied once and saved totals match displayed totals.
5. Exercise desktop/mobile search -> review -> save -> real forecast -> persisted read. Retain source snapshots and do not claim model-accuracy improvement from catalog availability alone.
6. If this source is adopted, update product, architecture, risk and M2 acceptance documents deliberately. Existing USDA/recipe live-verification gates are not automatically satisfied by a successful database connection. Camera exercise, arbitrary recipe extraction and final acceptance remain separate.

## Information needed before adoption

- Which ingestion jobs produced ingredient mappings, normalized quantities, recipe totals and energy fields? Can they provide the matched original descriptions and calculation rules?
- Which serving count is authoritative when recipe and profile values disagree, and are cooked recipe yields or source serving weights available elsewhere in the catalog pipeline?
- What is the precedence between denormalized nutrient columns and individual `nutrition_facts`, especially when zero-valued facts are absent or sources conflict?
- Which source licences/permissions allow use of recipe text, images and nutrition records in the capstone, local cache, demonstrations and any later distribution?
- Can a dedicated read-only account or catalog view expose the reviewed catalog subset for application use? No additional access credentials are needed to finish the current assessment.

## Documentation and handoff

Planning documents 00 and 01 were reviewed for current scope and app/research boundaries; 03 for food and recipe requirements; 04 for the provider, database and serving contracts; 08 for provenance, estimated facts and safe failure; and 10 for M2 live acceptance requirements. They were left unchanged because the task evaluated an optional source and did not adopt it, change implementation, revise an experiment or close a milestone gate.

No model fitting, forecast benchmarking, application changes, production writes, deployment or credential changes were performed. Future integration and upstream data repairs are separate work. Preserve the private query evidence under its ignored path; do not commit database extracts or credentials.
