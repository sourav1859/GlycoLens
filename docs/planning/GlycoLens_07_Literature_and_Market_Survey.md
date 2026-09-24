# GlycoLens Literature and Market Survey

## 1. Survey objective

This survey is not intended to prove that "no one has done glucose forecasting." A large body of work already exists.

The useful categorization is:

1. nutrition-aware T1D forecasting
2. task-specific PPGR models
3. generic time-series foundation models
4. CGM-specific foundation models
5. event/context-aware forecasting
6. patient-facing diabetes applications

GlycoLens sits at the intersection of these categories.

---

# 2. Nutrition-aware T1D forecasting

## Lubasinski et al. - 2024 review

**Blood Glucose Prediction from Nutrition Analytics in Type 1 Diabetes: A Review**

Key points:
- systematic review identified **138** nutrition-aware T1D glucose prediction models
- categorized methods as data-driven, physiological and hybrid
- many models use only carbohydrates
- full meal composition remains less common
- longer prediction horizons are relevant for meal planning

GlycoLens takeaway:
- glucose forecasting is not novel by itself
- nutrition/context integration is scientifically justified
- app value must come from concrete integration and interpretation

Source:
https://pmc.ncbi.nlm.nih.gov/articles/PMC11280346/

---

# 3. Task-specific postprandial models

## Xiong et al. - 2024

**Prediction of personalised postprandial glycaemic response in type 1 diabetes mellitus**

Method:
- 13 participants with T1D
- LightGBM
- glucose
- insulin
- meal nutrients
- other patient features

Reported:
- full model PPGR correlation R=0.63
- carbohydrate-only R=0.14
- model interpretation highlighted meal-time glucose and recent trend

GlycoLens takeaway:
- confirms that multimodal context matters
- supports LightGBM as a small baseline
- also illustrates the limitation of small task-specific cohorts

Source:
https://www.frontiersin.org/journals/endocrinology/articles/10.3389/fendo.2024.1423303/full

## Shen, Choi, Kleinberg - 2025/2026

**Predicting Postprandial Glycemic Responses With Limited Data in Type 1 and Type 2 Diabetes**

T1D:
- 397 T1DEXI participants
- dietary, temporal and personal information
- 2-hour PPGR and peak rise

Reported:
- T1D PPGR R=0.61
- peak rise R=0.64
- food categories improved prediction beyond macronutrients alone
- time of day contributed to within-person variability

GlycoLens takeaway:
- meal semantics/category may be useful in Meal Passport
- personal context is important even when full personal model training is unavailable

Source:
https://pubmed.ncbi.nlm.nih.gov/40042044/

## Wolber et al. - 2025

**Multimodal large language models and mechanistic modeling for glucose forecasting in type 1 diabetes patients**

Pipeline:
- meal image
- multimodal LLM nutrient estimation
- mechanistic nutrient-effect features
- LightGBM forecast

Data:
- D1NAMO
- AZT1D validation

GlycoLens takeaway:
- meal AI + forecasting integration is feasible
- photo nutrition is still not necessary for MVP
- meal context can improve forecast accuracy

Source:
https://pubmed.ncbi.nlm.nih.gov/41177244/

---

# 4. Generic time-series foundation models

## Chronos-2

Current public model:
- 120M parameters
- zero-shot
- univariate
- multivariate
- covariate-informed
- quantile forecasts
- CPU/GPU
- Apache-2.0

GlycoLens role:
- safest primary implementation candidate

Source:
https://huggingface.co/amazon/chronos-2

## TimesFM-3 - August 31, 2026

Newest TimesFM:
- native multivariate forecasting
- covariate support
- zero-shot generalist model
- 0.3B class
- current pretrained weights are non-commercial/non-production

GlycoLens role:
- highly attractive because T1D is inherently multivariate
- must be treated as a student/research dependency
- too new to have the same glucose-specific evidence as older TimesFM variants

Sources:
https://research.google/blog/timesfm-3-a-zero-shot-foundation-model-for-multivariate-forecasting/
https://github.com/google-research/timesfm

## GlucoFM-Bench - 2026

Benchmark:
- 15 diabetes-relevant datasets
- 1,117 individuals
- zero-shot, few-shot, full-shot
- multiple TSFMs and supervised models

Main result:
- pretrained TSFMs, especially Chronos-2 and TimesFM, show strong zero/few-shot transfer
- best zero-shot performance was within about 5% of the strongest fully supervised model
- when abundant task-specific labels exist, lightweight LSTM remains strong
- T1D/hypo/hyperglycemic ranges remain challenging

GlycoLens takeaway:
- directly supports advisor's inference-first recommendation
- model inference can be scientifically meaningful without training a large model

Source:
https://arxiv.org/abs/2606.06881

---

# 5. CGM-specific foundation models

## CGMformer

CGMformer is pretrained specifically on CGM data and exposes a public checkpoint.

Its `CGMformer_Diet` work uses:
- individual CGM embedding
- one-hour pre-meal glucose
- calories/carbs/protein/fat/fiber
- two-hour post-meal trajectory

Reported diet prediction:
- Pearson correlation around 0.763 in the paper's setting

Important implementation caveat:
- the public repository states that the diet downstream component requires training on paired CGM embeddings, meal nutrition and pre/post-meal glucose

GlycoLens role:
- excellent domain-specific exploratory candidate
- not a zero-training dependency for MVP

Sources:
https://pmc.ncbi.nlm.nih.gov/articles/PMC11970253/
https://github.com/YurunLu/CGMformer

## GlucoFM - 2026

Very recent Google Research model.

Architecture:
- CGM-specific
- dual stream:
  - slower state
  - short-term events
- self-supervised pretrained representations

PPGR experiment:
- 874 paired meal events
- 34 participants
- Dexcom/Libre
- frozen representation
- progressively adds one-hour pre-meal CGM and meal nutrition
- full context achieved lower mean MAE than evaluated baselines in the reported setting

GlycoLens takeaway:
- perhaps strongest direct evidence for context-rich frozen inference
- aligns closely with advisor direction
- official weights are not currently public, so do not make it an implementation dependency

Sources:
https://research.google/blog/glucofm-foundation-model-for-continuous-glucose-monitoring/
https://arxiv.org/abs/2605.30865

---

# 6. Event-aware forecasting

## EventGlucoseBench

A recent public benchmark/framework centered around:
- meals
- medication
- exercise
- contextual information
- probabilistic forecasting
- TS foundation models and other baselines

GlycoLens takeaway:
- reuse event-centered sampling/evaluation concepts
- supports our choice to treat the meal as the experimental unit instead of arbitrary sliding windows

Source:
https://github.com/JHU-CDHAI/EventGlucoseBench

---

# 7. Datasets

## T1D-UOM

- 17 PwT1D
- ~3 months
- CGM
- basal/bolus insulin
- carbs/protein/fat/fiber
- activity
- sleep

Role:
- **primary rich-context retrospective evaluation**

Sources:
https://zenodo.org/records/15806142
https://www.nature.com/articles/s41597-025-05695-1

## AZT1D

- 25 T1D participants
- 6-8 weeks
- CGM
- insulin
- carbohydrates
- device mode

Role:
- external common-feature validation

Source:
https://data.mendeley.com/datasets/gk9m674wcx/1

## HUPA-UCM

- 25 people with T1D
- CGM
- insulin
- carbs
- steps
- calories
- HR
- sleep

Role:
- external/context validation

Source:
https://data.mendeley.com/datasets/3hbcscwz44/1

---

# 8. Consumer app / market context

## Undermyfork

Provides:
- meal photo tracking
- glucose + insulin context
- postprandial Time in Range
- compare similar meals/situations

Implication:
- "show how a meal affected glucose" is already a product capability
- GlycoLens needs inference + nutrition grounding + uncertainty as differentiators

Source:
https://www.undermyfork.com/

## Tidepool

Provides:
- device aggregation
- CGM/pump/BGM data
- notes for meals/exercise/context
- visual timelines

Implication:
- timeline/context logging is not novel
- use it as UX inspiration, not a claimed contribution

Source:
https://www.tidepool.org/how-it-works

## Glooko

Provides:
- glucose
- insulin
- food
- exercise
- health data
- trend visualizations
- care-team sharing

Implication:
- avoid making GlycoLens a generic diabetes dashboard

Source:
https://glooko.com/patients/

## mySugr

Provides:
- diabetes logbook
- meals/activity/insulin
- meal photos
- stats/reports
- device connections

Implication:
- logging alone is insufficient differentiation

Source:
https://www.mysugr.com/diabetes-app

---

# 9. GlycoLens position after literature review

GlycoLens should **not claim**:
- new glucose forecasting science
- new foundation model
- first meal logging system
- first similar-meal view

The capstone's defensible contribution is:

> **A practical inference-first architecture that evaluates current pretrained forecasting models under progressively richer T1D meal context and integrates the selected model into a grounded, uncertainty-aware, personalized meal application.**

The novelty for the capstone is primarily **integration, evaluation, and system design**, which is consistent with the advisor's guidance.

---

# 10. Literature survey categories for final report

Recommended Background subsections:

1. Type 1 Diabetes and CGM
2. Nutrition-aware glucose forecasting
3. Postprandial glucose prediction
4. Time-series foundation models
5. CGM-specific representation models
6. Event-aware/context-aware forecasting
7. Existing diabetes applications
8. Gap addressed by GlycoLens
