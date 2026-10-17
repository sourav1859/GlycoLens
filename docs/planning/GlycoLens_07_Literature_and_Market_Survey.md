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

- implementation release pinned to V1.0.4
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
https://zenodo.org/records/17361905
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

October 16 implementation verified public V1 access and CC BY 4.0 licensing against
this source, downloaded/checksummed the archive and audited 25 canonical CGM files.
The 6-hour shared-feature window policy yields 2,610 eligible meals/24 participants.
Detailed protein/fat/fibre is unavailable; one source glucose column mentions CGM/BGM.
The external test is reserved until selection, then consumed for subsequent tuning.
The [refinement execution report](../reports/model-refinement-results-2026-10-16.md)
separates locally observed scores from literature claims. Published results on other
cohorts/horizons are not evidence of +/-10 maximum error for GlycoLens.

## MetaboNet intake evidence

October 16 local files contain 15 training sources including AZT1D/UOM copies and
OhioT1DM. The user-provided v1.2 release notes (October 5) describe five SIESTA training
participants, confirmed locally. The [publication](https://arxiv.org/html/2601.11505v2)
documents standardized units, missing/zero ambiguity, mixed subject/time splits and
source-dependent rights; it lists OhioT1DM as DUA-governed. Confirm current release
terms for that source before training. Do not assume all consolidated data has the
same licence or that the publication's 30-minute scores apply to this two-hour task.
See the [local audit](../reports/metabonet-intake-audit-2026-10-16.md); local counts
and the screenshot release date are distinct from publication-wide historical counts.

## MetaboNet frozen-inference evidence

The [October 16 local experiment](../reports/metabonet-phase3-inference-2026-10-16.md)
compared frozen Chronos histories/context on 1,509 matched validation meals. No eligible
Chronos option beat persistence (macro MAE 37.12 mg/dL; C2 37.61). Longer histories
lowered error among valid outputs but had native contract failures; nominal 80% bands
covered only 49.42-64.08% of points across Chronos options. This is local conditional
validation evidence, not a new literature result or a comparison of every available
model. It supports testing small trained competitors, not claiming +/-10 performance.

The subsequent [Phase 4 local study](../reports/metabonet-phase4-training-2026-10-16.md)
trained Ridge/LightGBM with training-only subject CV. On the same 1,509 validation
meals, 24-hour event LightGBM reduced macro MAE from 37.12 to 31.17 mg/dL (16.03%),
passing the research gate, with zero failed forecasts. Within +/-10 remained only
26.84%; Ridge had a higher 28.85% with slightly larger MAE. This is local selected
validation evidence, not a literature benchmark, a causal feature effect or external
confirmation. It motivates the planned correction/independent-testing stages and
does not establish dependable +/-10 predictions.

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

The independent primary MAE reduction is 18.74%, versus persistence 36.81; PEDAP reduction is 16.10%, versus 48.77. These results compare fixed small models on the same eligible meals, not all architectures or studies. The split-conformal rank is motivated by Angelopoulos and Bates (https://arxiv.org/abs/2107.07511); dependence and study shift limit guarantees.

See [protocol 16](GlycoLens_16_MetaboNet_Independent_Evaluation.md), [independent results](../reports/metabonet-phase6-independent-2026-10-16.md) and [verification handoff](../tooling/metabonet-phase6-handoff-2026-10-16.md).
