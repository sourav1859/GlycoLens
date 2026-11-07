# Azure nutrition catalog assessment

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
