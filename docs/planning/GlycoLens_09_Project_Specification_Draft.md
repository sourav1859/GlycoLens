# GlycoLens Project Specification Draft

**Title:** GlycoLens: AI-Assisted Meal Understanding and Personalized Glucose Response Prediction for Type 1 Diabetes  
**Cluster:** Artificial Intelligence / Data Science  
**Student:** Sourav Patil  
**Advisor:** Professor Yang

## Project Rationale

People with Type 1 Diabetes (T1D) continuously manage the relationship among glucose, food, externally administered insulin, physical activity, and individual physiological variation. Continuous Glucose Monitors provide dense glucose measurements, but food-related decisions remain burdensome, particularly when a meal is home-cooked or does not have a simple nutrition label. Existing diabetes applications can log glucose, insulin, food and activity, but the user still has to interpret how all of these signals relate to a specific meal.

GlycoLens will investigate whether current pretrained time-series/CGM models can be used effectively at inference time to forecast a short-term post-meal glucose trajectory when provided with T1D-specific context. The project intentionally avoids training a large deep model from the available small cohorts. Instead, it will compare existing pretrained models, determine what contextual information improves inference, and integrate the selected approach into a mobile-first meal-intelligence application.

## Goal

The goal is to build and evaluate an end-to-end research prototype that allows a user to enter a packaged or home-cooked meal, obtain grounded nutritional information, combine the meal with recent CGM/insulin/context information, and view a probabilistic two-hour glucose forecast together with similar historical meal outcomes.

The system will emphasize understandable, concrete output rather than automated treatment. GlycoLens will not generate insulin doses or control a pump.

## Background

Nutrition-aware T1D glucose forecasting is an established research area. A 2024 review identified 138 prediction models using nutritional information. Prior T1D studies have shown that glucose history, insulin and detailed meal information can improve postprandial prediction compared with carbohydrate-only approaches.

Recent time-series foundation models change the design space. GlucoFM-Bench (2026) reports strong zero/few-shot glucose forecasting from models such as Chronos-2 and TimesFM, with the best zero-shot approaches close to fully supervised models. CGM-specific models such as CGMformer and the very recent GlucoFM further show that pretrained CGM representations can support postprandial prediction when combined with pre-meal CGM and meal nutrition.

This motivates an inference-first capstone: evaluate pretrained models rather than building a large glucose model from scratch.

## Attack Plan

### Model inference

Required candidates:
- Chronos-2
- TimesFM-3

Exploratory:
- CGMformer

Reference:
- GlucoFM

Baseline:
- persistence
- optional LightGBM

The main experiment will compare progressively richer context:
- CGM
- CGM + insulin
- CGM + carbs
- CGM + full meal nutrition
- optional activity/time context

### Data

Primary:
- T1D-UOM V1.0.4 (`10.5281/zenodo.17361905`), stored outside Git and processed through leakage-safe meal windows

External/shared-feature validation:
- AZT1D
- HUPA-UCM

Simulation:
- py-mgipsim

Device integration:
- Dexcom Sandbox

Nutrition:
- USDA FoodData Central
- Open Food Facts

### App

A mobile-first PWA will be built using:
- Next.js/TypeScript
- FastAPI/Python
- PostgreSQL/Supabase
- pgvector for similar-meal personalization

Core application flow:
`meal -> nutrition -> T1D context -> pretrained inference -> uncertainty -> personal history -> portion comparison`

## Work Plan

October 16 addition: the user approved local model refinement with frozen Chronos
history comparisons, modest trained Ridge/LightGBM direct/residual heads and separate
calibration. +/-10 mg/dL is aspirational; no clinical/max-error claim is made. The
original test is now diagnostic; AZT1D external scores follow immutable selection.
MetaboNet training was deferred in favor of local data first. Subsequent v1.2
downloads now have an intake audit and executed Phase 2 preparation, with no new
training/test predictions. A fixed Loop/ReplaceBG pilot supplies 8,973/2,000/1,948
six-hour training/validation/calibration windows. Native units, causal fill, masks,
timing, isolated-meal exclusions and frozen hashes are defined in
[document 12](GlycoLens_12_MetaboNet_Experiment.md). Metadata-only reservations cover
104 unseen test identities and 65 PEDAP source-test identities; test eligibility
waits until selection freezes. Phase 3 is now complete: seven runs on 1,509 matched
validation events found persistence best among failure-free options (macro MAE 37.12
versus six-hour C2 37.61), failing the improvement gate. Two-hour C0 is the only
failure-free C0, not the lowest-error history among valid outputs. Native intervals
undercovered and negative forecasts occurred.
no fitting, calibration or reserved-test access occurred in Phase 3. See
[protocol/results 13](GlycoLens_13_MetaboNet_Frozen_Inference.md).
Phase 4 direct training is now complete: training-only subject CV selected 24-hour
event Ridge/LightGBM, refitted on 6,794 training meals/197 identities. On the same
1,509 validation meals, LightGBM macro MAE 31.17 versus 37.12 persistence passes the
16.03% improvement gate. Within +/-10 remains poor at 26.84% (Ridge 28.85%); this
does not establish a maximum-error guarantee or independently tested performance.
At Phase 4 completion calibration/reserved outcomes were untouched; Phase 6 below now records their use. See [protocol 14](GlycoLens_14_MetaboNet_Direct_Models.md) and
[report](../reports/metabonet-phase4-training-2026-10-16.md).
The two-hour task, application
boundaries and official deadlines remain. No automatic app model promotion or large
foundation-model training. See [the approved protocol](GlycoLens_11_Model_Refinement.md)
and [execution results](../reports/model-refinement-results-2026-10-16.md).

### Milestone 1 - understanding and feasibility
- literature survey
- dataset audit
- model smoke tests
- event-window preprocessing
- architecture and DB schema
- PWA/backend skeleton
- simulator feasibility

Implemented Milestone 1 evidence now includes a pinned py-mgipsim ExtHovorka/OpenLoop synthetic
day with 288 five-minute samples and byte-identical results across two executions. The simulator is
isolated from the application environment and retained as synthetic feasibility evidence only.

Milestone 1 is complete. The final closure audit maps every required research, data, model,
application, database, simulation, safety, and presentation deliverable to executable evidence.
The original seven-slide closure presentation is preserved. The revised eight-slide RIT
presentation reports aggregate/synthetic results, separates the research and application paths,
and carries the same research-only, uncertainty, privacy, and no-dosing boundaries as the
application. It includes meal-window eligibility evidence, lessons learned, and timed Word/PDF
presentation notes.

### Milestone 2 - solve/prototype

The full phase implementation was approved October 14, 2026: py-mgipsim first,
Dexcom later, API-backed recipe extraction with ingredient confirmation. Progress
and verification are tracked in `GlycoLens_10_Milestone_2_Implementation.md`; this
approval is not a change to course dates or a claim of milestone completion.
- benchmark core models
- context-ablation experiment
- implement nutrition pipeline
- implement forecast UI
- implement meal persistence
- first similar-meal retrieval
- simulator/Dexcom integration

### Milestone 3 - implementation and analysis

M2 current evidence includes real Chronos/TimesFM/persistence C0-C3 comparisons,
frozen validation selection and held-out results; the selected Chronos C3 does not
beat persistence and uncertainty is under-covered. The real local simulated meal
workflow is verified on desktop/mobile. Live nutrition/recipe and physical camera
verification plus final acceptance remain pending, so full milestone closure is not asserted.
The November 3 [M2 presentation draft](../presentations/GlycoLens_Milestone_2_Presentation_2026-11-03_v4.pptx)
and [timed notes](../reports/GlycoLens_Milestone_2_Presentation_Notes.md) were prepared
November 2 and retain the research and application limitations.
- final model selection
- uncertainty UI
- Meal Passport
- portion comparison
- testing/debugging
- final experiments
- results and limitations
- final demo preparation

## Deliverables

1. Mobile-first GlycoLens PWA.
2. FastAPI inference/data backend.
3. Reproducible meal-centered T1D preprocessing pipeline.
4. Pretrained-model comparison and context-ablation results.
5. Nutrition/barcode/recipe pipeline.
6. Personal Meal Passport and similar-meal retrieval.
7. What-if portion comparison.
8. Dexcom Sandbox and/or virtual-patient demo.
9. Source code and reproducibility documentation.
10. Course milestone presentations, poster and final report.

## Safety Boundary

The project is a research prototype. It will not:
- recommend insulin doses
- control a medical device
- diagnose disease
- claim clinical validation
- provide treatment instructions

## Primary references

- GlucoFM-Bench: https://arxiv.org/abs/2606.06881
- Chronos-2: https://huggingface.co/amazon/chronos-2
- TimesFM: https://github.com/google-research/timesfm
- CGMformer: https://github.com/YurunLu/CGMformer
- T1D-UOM: https://www.nature.com/articles/s41597-025-05695-1


## MetaboNet Phase 5 completion

**Phase 5 was complete before the Phase 6 evaluation recorded below.** Frozen C2
generated 6,756 training forecasts; 6,756 usable meals / 196 identities supported six CV
configurations / 18 fold fits and four final refits, with exactly matched direct
controls. Neither correction passed the predeclared incremental gate; retain Phase 4
LightGBM. Lowest-MAE eligible option: `ridge_residual_1000`; advancement candidate:
`lightgbm_direct` (macro MAE 31.17 mg/dL, within +/-10 26.84%). These are
reused-validation findings, not independent confirmation. At Phase 5 completion, calibration/reserved outcomes were untouched.
Phase 6 below supersedes that access status; app inference remains unchanged.
See [protocol 15](GlycoLens_15_MetaboNet_Chronos_Correction.md) and [results](../reports/metabonet-phase5-correction-2026-10-16.md).

## MetaboNet Phase 6 completion - current status

**The broader-data model-refinement sequence, Phases 1-6, is complete.** Separate calibration used 48 participant representatives from 1,488 eligible meals. Frozen LightGBM scored 29.91 mg/dL macro trajectory MAE / 28.20% within +/-10 on 3,533 primary-test meals (102 IDs), and 40.92 / 19.57% on 2,177 PEDAP meals (64 IDs). Both predeclared point-improvement gates passed, with zero failed forecasts; tight precision remains poor. Nominal 80% marginal coverage was 79.05% primary and 63.94% PEDAP. Both test cohorts are now consumed; no test-based reselection, point refit, app promotion or full-M2 closure.

The app specification and safety boundary are unchanged. The completed research experiment does not prove causal nutrient effects or authorize clinical use, application replacement or release. The November 3 presentation draft is prepared. Live recipe/nutrition and physical camera verification plus final acceptance remain separate M2 work.

See [protocol 16](GlycoLens_16_MetaboNet_Independent_Evaluation.md), [independent results](../reports/metabonet-phase6-independent-2026-10-16.md) and [verification handoff](../tooling/metabonet-phase6-handoff-2026-10-16.md).
