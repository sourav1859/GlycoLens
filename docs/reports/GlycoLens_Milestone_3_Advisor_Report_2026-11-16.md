# GlycoLens Milestone 3 Progress and Implementation Report

**Author:** Sourav Patil  
**Advisor:** Professor Haibo Yang  
**Prepared:** November 16, 2026  
**Reporting period:** Work since the November 3 Milestone 2 presentation

## Main finding and milestone status

Since the Milestone 2 presentation, I have extended GlycoLens from a connected forecasting prototype into a broader application with persistent accounts, reviewed meal logging, nutrition summaries and separate personal and virtual simulation workspaces. I integrated and exercised the USDA food API and the LLM recipe-extraction API, and connected the previously evaluated LightGBM model as an optional research predictor. [R1–R5]

The most important new analytical finding concerns meal sensitivity. Under controlled synthetic conditions, the default Chronos configuration remained effectively unchanged across all 60 eligible meal and portion contrasts. LightGBM showed limited carbohydrate sensitivity, but these tests did not establish accurate responses to particular meals. The implementation supports examining these questions more clearly, while individual meal-response accuracy remains unresolved. [R6]

This report distinguishes implemented behavior, recorded validation and remaining core acceptance work. It does not claim that every application case or prediction-quality requirement is complete.

## Progress on work carried forward from Milestone 2

| Earlier pending work | Progress since the M2 presentation | Current qualification |
|---|---|---|
| Live food-provider verification | Exercised USDA search/detail and Open Food Facts barcode paths | Bounded observations support integration rather than general nutrition correctness |
| Live recipe extraction | Connected the selected LLM extractor and evaluated eight synthetic cases | All eight passed after a documented scoring correction; representative accuracy remains open |
| LightGBM compatibility and history | Implemented model-specific inputs, verified loading and a separate 48-hour simulation | Explicit research option; Chronos remains default |
| Portion comparisons | Added saved comparisons using the original model and historical context | Chronos capability failure and limited native sensitivity remain visible |
| Later outcome follow-up | Added availability checks, numerical error/coverage and eligible outcome saving | Preset simulator outcomes do not validate arbitrary entered meals |
| Earlier-meal evidence | Preserved chronological retrieval and improved discoverability of simulation history | Full personal longitudinal Meal Passport remains incomplete |
| Interaction acceptance | Expanded automated and recorded real-service/browser checks | Remaining manual checks are open; physical camera stays explicitly deferred |

These updates address the core priorities identified in the previous advisor report and M2 presentation. The completed October model study remains earlier evidence rather than a new M3 experiment. [R7, R8]

<!-- page -->

## Application development and UI integration

I reviewed 44 unique Figma reference nodes and adapted suitable navigation, hierarchy and interaction patterns for GlycoLens. The implemented application includes a consistent shell, minimal resumable onboarding, Home, meal history, daily/seven-day nutrition, simulation forecast history, settings and nonclinical notifications. [R1, R2]

Users can review and save meals, edit or cancel them, and copy an existing meal into a new draft. Only confirmed eaten meals contribute to consumed nutrition. Planned meals, hypothetical scenarios and cancelled meals remain separate. Daily totals account for timezone boundaries and missing nutrient information.


*Figure 1. Recorded synthetic-account interface evidence: current personal date, reviewed meal and consumed totals. No personal glucose source is connected. The image does not demonstrate prediction accuracy.*

## Personal and simulation workspace separation

A major correction was separating personal records from the virtual patient. Personal logging uses the actual current date in the confirmed timezone and works without a virtual source. Simulation retains its own clock, owned sources and earlier history. Synthetic meals remain in simulation rather than appearing as personal consumption. [R2]

Recorded real-browser validation covered genuine sign-in, a personal meal, simulation history, returning to the personal workspace and logout. The personal forecast path rejects requests without a real connector rather than borrowing simulated glucose.

<!-- page -->

## Application connections and data flow

The Next.js interface connects to FastAPI for meal, nutrition, forecast and account operations. Supabase Auth manages identity; persisted records retain owner and workspace relationships. Ordinary reads preserve the caller identity, while trusted writes validate ownership and authoritative values. [R1, R2]

Food search, barcode entry and recipe extraction feed the same reviewed meal process. The backend requests provider data and calculates nutrient totals for confirmed quantities. Forecast requests use an explicit model choice and an eligible owned source. Saved results retain the original meal revision, source, model identity and input context.

Editing a meal or selecting another source therefore does not silently reconstruct an earlier result from different information. Account controls include logout, owned export and password-confirmed permanent deletion for supported password accounts. Tests checked that one account could not retrieve or remove another account's data. [R9]

## USDA food API and LLM recipe integration

I integrated USDA FoodData Central for food candidates and nutrient details. Facts retain an explicit gram basis and source information. Open Food Facts supports packaged-food lookup, including barcode checksum validation and labeled community-source facts. [R3]

The LLM API converts recipe text into structured ingredient names, amounts, units and servings. Users can edit the draft before confirmation. The selected server configuration uses GPT-6 Luna. Nutrient values come from reviewed matched food facts and deterministic calculations rather than from the language model. [R4]

A bounded live evaluation covered eight synthetic recipes, including fractions, decimals, repeated ingredients, mixed units and ambiguous portions. All eight passed after correcting an overly narrow flour-name scoring rule. The same saved outputs were rescored without changing model responses. This establishes working extraction on a small sample; broader accuracy still requires evaluation.

<!-- page -->

## LightGBM integration and forecast evidence

The previously selected frozen LightGBM model is now available through the shared forecasting interface. Chronos remains the default and users explicitly select LightGBM as a research option. Recorded application tests produced 24 persisted five-minute forecast points with both model paths. [R2, R5]

Integration required matching the research input contract. LightGBM needs 288 pre-origin glucose samples spanning 24 hours, together with recorded-event information. A separate 48-hour scenario supplies sufficient earlier history. Input preparation preserves timing, event availability and the difference between missing records and observed zeros.

| Serving contract | Chronos application path | Frozen LightGBM path |
|---|---|---|
| Required glucose history | 2 hours / 24 five-minute samples | 24 hours / 288 five-minute samples |
| Proposed meal information | Recorded carbohydrate, protein, fat and fiber channels | Current carbohydrates |
| Forecast output | 24 future five-minute points | 24 future five-minute points |
| Displayed uncertainty | Model quantiles | Saved symmetric marginal calibration bands |

The application rejects insufficient or incompatible history instead of inventing readings. Saved LightGBM forecasts retain model, feature and calibration identity. Its interval coverage in the application simulation remains unverified. Current protein, fat and fiber remain nutrition facts rather than direct predictors for this frozen model.

## Portion comparisons and historical follow up

Portion comparisons preserve the original forecast's history, recorded insulin context and model identity while scaling the reviewed meal. Scenarios remain separate from consumption and cannot increase eaten totals. A 100 percent comparison reproduces the baseline in recorded tests. [R3, R5]

Later observations become eligible only after the owned virtual clock advances and the expected glucose samples exist. The application calculates numerical error/coverage and can save eligible outcomes. Earlier-meal retrieval restricts candidates to the same owner, earlier meal time and already available outcomes. Its demonstration remains same-session simulated history; a broader personal Meal Passport requires further work.

<!-- page -->

## New application meal response analysis

The new diagnostic held earlier glucose and insulin context fixed while varying meals and portions. It included repeated identical requests and a predeclared numerical tolerance of 0.001 mg/dL. Across the complete protocol, 236 predictions finished, including contrast, control/repeat and warm-run observations. [R6]

| Controlled observation | Chronos | LightGBM |
|---|---|---|
| Eligible changed-input contrasts | 60 | 51 |
| Effectively unchanged at the declared tolerance | 60 of 60 | 6 of 51 |
| Largest absolute endpoint change | 0.0000076294 mg/dL | 13.9066 mg/dL |
| Identical-input maximum repeat spread | 0 mg/dL | 0 mg/dL |
| Interpretation | Meal-response capability failed in these tests | Limited synthetic carbohydrate sensitivity |

The application delivered changed meal channels, but Chronos did not demonstrate useful meal sensitivity in these controlled tests. LightGBM changed in 45 of 51 eligible carbohydrate contrasts, although responses could be flat or uneven. Equal-carbohydrate protein/fat/fiber contrasts are not eligible changed-input tests for the native model because it does not use those current-meal predictors.

Responsiveness alone does not establish accurate direction, magnitude or causal meal effects. The simulator follows preset meals, so later readings cannot validate an arbitrary entered meal. A matching-meal evaluation requires the proposed meal and corresponding later observations.

## Earlier research informing the current implementation

The independent October LightGBM study, already reported at M2, remains the research basis for this frozen candidate. It was not repeated as a new M3 cohort evaluation. [R8]

| Earlier LightGBM measure | Primary cohort | PEDAP cohort |
|---|---:|---:|
| Participant-average trajectory MAE | 29.91 mg/dL | 40.92 mg/dL |
| Points within ±10 mg/dL | 28.20% | 19.57% |
| Nominal 80% marginal-band coverage | 79.05% | 63.94% |

Average error improved relative to each cohort's own persistence baseline, while tight precision and pediatric uncertainty transfer remained weak. These cohorts differ from the original Chronos benchmark and cannot form a direct head-to-head ranking. Consumed test groups cannot be relabeled fresh confirmation after further tuning.

<!-- page -->

## Testing debugging and documentation

The November 16 selected offline verification passed 210 Python tests and 36 frontend tests. One explicit real-simulator opt-in test was skipped. Frontend lint, TypeScript and the reviewed API contract also passed. These checks support their stated coverage rather than full acceptance of every combined case. [R10]

Recorded integration tests exercised actual sign-in, meal persistence, both forecast paths, stored-result retrieval, owner isolation and workspace boundaries. Controlled data collection used synthetic inputs, provider observations and saved outputs rather than new patient recruitment. [R2, R3]

Two corrected defects illustrate the debugging work:

- Editing recipe information could leave an earlier review confirmation active. The correction invalidates it and requires renewed review.
- A delayed simulation response could restore context after the user exited. The correction invalidates pending selection changes.

Personal and synthetic records also needed explicit boundaries so virtual history could not affect personal totals. Planning records, API contracts, decisions and validation reports document these corrections. Remaining evidence reconciliation must identify exact missing variants rather than treat broad test totals as complete acceptance.

## Ongoing recipe data expansion

I am currently working on ingesting additional recipe data from thedevastator's Recipes Dataset on Kaggle to broaden the recipe information available in GlycoLens. Ingredient quantities, serving information and nutrient facts will require review before supporting nutrition calculations. This work remains ongoing. [R11]

## Remaining core work and advisor guidance

My remaining priorities are to finish applicable browser and usability checks, strengthen the earlier-meal evidence experience, and define a suitable matching-meal outcome evaluation. I will continue recipe ingestion and consolidate the final demonstration, analysis and written conclusions.

My assessment is that implementation has progressed substantially and tests now expose limits that were less visible in the earlier prototype. The next stage should clarify what users can reasonably infer from a forecast.

I would appreciate guidance on the balance between further prediction analysis and completing the core experience, an appropriate source/protocol for matching-meal evaluation, the expected depth of Meal Passport, and presenting the negative Chronos sensitivity result alongside the implemented application.

<!-- page -->

## Evidence references

The references distinguish current implementation evidence from earlier research. Detailed test inputs and private model/data artifacts remain outside this report.

- [R1] [Application implementation checkpoint](webapp-implementation-checkpoint-2026-11-11.md) and [responsive UI reference review](figma-reference-review-2026-11-10.md).
- [R2] [Personal and simulation workspace validation](workspace-separation-validation-2026-11-14.md).
- [R3] [Provider and forecasting integration evidence](m2-closure-validation-2026-11-12.md).
- [R4] [Live recipe extraction validation](recipe-model-validation-2026-11-11.md).
- [R5] [Frozen LightGBM application integration](lightgbm-app-validation-2026-11-12.md) and [research-model selection evidence](local-lightgbm-enablement-2026-11-14.md).
- [R6] [Controlled meal and portion sensitivity results](meal-response-sensitivity-2026-11-12.md).
- [R7] [Previous advisor report](GlycoLens_Milestone_2_Advisor_Report_2026-10-26.md) and [November 3 M2 presentation](../presentations/GlycoLens_Milestone_2_Presentation_2026-11-03_v4.pptx).
- [R8] [Earlier independent model evaluation](metabonet-phase6-independent-2026-10-16.md).
- [R9] [Account deletion validation](account-deletion-validation-2026-11-11.md).
- [R10] [November 16 verification record](milestone-3-status-audit-2026-11-16.md#fresh-verification-performed-by-this-audit). The selected tests were not rerun for document creation.
- [R11] [Recipes Dataset by thedevastator on Kaggle](https://www.kaggle.com/datasets/thedevastator/better-recipes-for-a-better-life). Source for the ongoing recipe-ingestion work.
