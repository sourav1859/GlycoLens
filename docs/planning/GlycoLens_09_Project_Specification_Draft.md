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
- T1D-UOM

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

### Milestone 1 - understanding and feasibility
- literature survey
- dataset audit
- model smoke tests
- event-window preprocessing
- architecture and DB schema
- PWA/backend skeleton
- simulator feasibility

### Milestone 2 - solve/prototype
- benchmark core models
- context-ablation experiment
- implement nutrition pipeline
- implement forecast UI
- implement meal persistence
- first similar-meal retrieval
- simulator/Dexcom integration

### Milestone 3 - implementation and analysis
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
