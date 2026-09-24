# GlycoLens Model Inference and Dataset Strategy

## 1. Objective

Select the pretrained forecasting approach that best fits a **meal-centered T1D inference task** without requiring large custom model training.

The selected model must be judged on:

1. forecast accuracy
2. ability to consume T1D context
3. probabilistic/uncertainty output
4. latency and memory
5. checkpoint availability
6. license suitability for a student project
7. implementation stability
8. reproducibility

## 2. Candidate model matrix

| Model | What it gives us | T1D/glucose evidence | Covariates | Training required | Project decision |
|---|---|---|---|---|---|
| **Chronos-2** | 120M TS foundation model; zero-shot; quantiles; CPU/GPU | Strong generic glucose results reported in GlucoFM-Bench | Native multivariate/covariate-informed | No | **Required candidate** |
| **TimesFM-3** | New 0.3B model; native multivariate + covariates; quantiles | Too new for the June 2026 glucose benchmark | Native | No | **Required candidate**, pending smoke test |
| **TimesFM-2.5** | Mature/stable fallback; 200M; quantile head/XReg | Evaluated in current glucose TSFM work | XReg | No | **Fallback if 3.0 integration is unstable** |
| **CGMformer** | CGM-specific pretrained embeddings | Strong postprandial diet paper; public checkpoint | Downstream fusion, not direct general TS covariate API | Encoder no; diet head yes | **Exploratory candidate** |
| **GlucoFM** | CGM-specific dual-stream model; strong PPGR results | Very strong/current | Frozen embeddings + context in published work | Official weights not public | **Literature benchmark / revisit later** |
| **LightGBM** | Small task-specific model | Prior T1D PPGR evidence | Natural tabular features | Yes, modest | **Baseline/residual only** |
| **LSTM** | Supervised sequence model | Strong full-shot benchmark when enough labels exist | Flexible | Yes | **Not required** |

## 3. Important 2026 update: TimesFM-3

TimesFM-3 was announced on August 31, 2026. It adds native multivariate forecasting and flexible past-only / past-and-future covariate support. This is highly relevant to GlycoLens because the target is glucose while contextual channels include insulin and meal-related variables.

However:

- it is extremely new
- it has not yet accumulated T1D-specific benchmark evidence comparable to older TimesFM variants
- the pretrained weights use a **non-commercial/non-production license**

For a university capstone this license is likely appropriate, but it should be documented and the model should not be described as production-ready.

## 4. Why Chronos-2 remains the safest first implementation

Chronos-2 has several practical advantages:

- public Apache-2.0 weights
- 120M parameters
- zero-shot inference
- multivariate and covariate-informed forecasting
- multi-step quantile output
- CPU and GPU support
- strong performance among public TSFMs
- recent glucose benchmark evidence for the Chronos family/Chronos-2

Recommendation:

> **Implement Chronos-2 first, then TimesFM-3.**

This minimizes the risk of spending Milestone 1 debugging a newly released model.

## 5. Why CGMformer is important but not the default

CGMformer is directly relevant to glucose physiology. Its paper introduces `CGMformer_Diet`, which uses:

- a pretrained CGMformer individual embedding
- one hour of pre-meal glucose
- meal nutrition:
  - calories
  - carbohydrates
  - protein
  - fat
  - fiber

and predicts a two-hour post-meal glucose trajectory.

This is extremely close to GlycoLens.

However, the public repository states that `CGMformer_Diet` requires paired embeddings, nutrition, before-meal glucose and post-meal glucose for **training** the downstream diet model. Therefore it is not a pure plug-and-play meal forecaster.

Recommended use:

1. Test the pretrained CGMformer encoder.
2. If integration is straightforward, use frozen embeddings.
3. Only train a small downstream regression head if time/data permit.
4. Do not make CGMformer_Diet a dependency for project completion.

## 6. Why GlucoFM matters

GlucoFM (2026) is perhaps the closest research validation of the advisor's inference-first idea.

The reported PPGR experiment:

- froze the pretrained glucose representation
- added one hour of pre-meal CGM
- added meal nutrition
- added participant-level context
- predicted the complete two-hour glucose-change trajectory
- showed progressive improvement as context was added

This supports GlycoLens's planned **context-ablation** design.

At the time of this planning pack, Google's official public page links to the paper but does not provide official pretrained weights. Community reimplementations exist, but they should not be treated as equivalent to an official checkpoint.

Use GlucoFM as:
- literature support
- experiment-design inspiration
- a candidate only if official weights are released in time

## 7. Core forecasting task

### Event definition

A meal is an event at time `t = 0`.

### Context

Candidate history lengths:

- 2 hours
- 6 hours
- 12 hours
- 24 hours

Do not assume the longest is best. Context length itself can be evaluated.

### Inputs

**Target series**
- CGM glucose sampled/harmonized to 5-minute resolution

**Past covariates**
- bolus insulin
- basal insulin if available
- meal history
- activity

**Meal event at t=0**
- calories
- carbohydrates
- protein
- fat
- fiber
- meal type/tag

### Forecast

2 hours = 24 five-minute points.

User-facing summaries:
- 30 min
- 60 min
- 120 min
- median/quantile band
- predicted peak rise (optional)

### Future-event assumption

For the core offline experiment, no unknown future meal/activity event is injected during the two-hour forecast window. Windows containing another major meal should be filtered or marked as a separate experimental condition.

GlycoLens will **not generate an insulin dose**. If a known insulin event exists at/before meal time, it can be used as context.

## 8. Main inference experiments

### Experiment 1 - model comparison

Same windows, same context, different models:

- Persistence
- Chronos-2
- TimesFM-3
- optional TimesFM-2.5
- optional CGMformer-based method
- optional LightGBM baseline

### Experiment 2 - context ablation

For the selected models:

| Configuration | Inputs |
|---|---|
| C0 | CGM only |
| C1 | CGM + insulin |
| C2 | C1 + carbohydrates |
| C3 | C1 + calories/carbs/protein/fat/fiber |
| C4 | C3 + activity/time context |

### Experiment 3 - context length

Compare e.g. 2h / 6h / 12h / 24h.

### Experiment 4 - personalization by retrieval

Compare:
- model forecast alone
- model forecast + display of same-user similar historical outcomes
- optional small patient residual calibration

Retrieval should primarily improve **interpretability and personalization**, not be misrepresented as changing model physiology unless it is explicitly used as an input/calibration feature.

## 9. Metrics

### Point forecast
- MAE
- RMSE
- error at 30, 60, 120 min
- full two-hour trajectory MAE

### Probabilistic forecast
- CRPS where samples/quantiles support it
- empirical prediction interval coverage
- prediction interval width

### System
- p50/p95 inference latency
- RAM / GPU memory
- failed inference rate
- model load time

### Optional domain metric
A Clarke/Surveillance Error Grid can be reported as a secondary analysis if used carefully; it should not replace standard forecast metrics or be presented as clinical validation.

## 10. Dataset audit

### T1D-UOM - primary multimodal dataset

**Use:** rich meal-centered inference evaluation.

Available:
- CGM
- basal insulin
- bolus insulin
- carbs
- protein
- fat
- fiber
- activity
- sleep
- meal timestamp/type/tag

Strength:
- exactly the modalities GlycoLens wants.

Limitation:
- only 17 participants
- self-recorded nutrition
- missingness across streams

Implication:
- excellent for context experiments
- weak basis for training a large deep model
- use subject-aware / chronological splits

### AZT1D

**Use:** external validation with common features.

Available:
- 25 T1D participants
- 6-8 weeks
- CGM
- insulin
- carbohydrates
- device modes

Not available in same detail:
- full protein/fat/fiber meal composition

### HUPA-UCM

**Use:** external validation / activity context.

Available:
- 25 T1D participants
- CGM
- insulin
- carbohydrates
- steps
- calories burned
- HR
- sleep

### GlucoFM-Bench dataset

**Use:** quick CGM-only forecasting sanity check and reproducibility.

It aggregates multiple public cohorts into a standardized five-minute format.

Limitation:
- aggregated format primarily exposes CGM arrays, so it does not replace the original multimodal T1D-UOM data for the meal-context experiment.

### EventGlucoseBench

**Use:** methodology and code inspiration for event-centered sampling and probabilistic evaluation.

## 11. Data split rules

### Primary personalized/temporal test

Per participant:
- early history -> train/calibration if any
- middle -> validation
- latest -> test

For pure zero-shot, the "train" portion can still be used for retrieval/index building while model weights remain frozen.

### Subject-disjoint test

Hold out entire participants for a harder generalization analysis.

### Leakage controls

- no post-meal CGM in input
- no later insulin/activity events unless the experiment explicitly assumes them known
- no same exact meal outcome copied into context
- retrieval should not include future occurrences relative to the tested event

## 12. Fine-tuning fallback ladder

Do not jump directly to full fine-tuning.

1. Zero-shot/frozen inference.
2. Prompt/API/covariate representation changes.
3. Small statistical calibration.
4. Small residual LightGBM/linear model on top of forecast.
5. Frozen CGM encoder + small head.
6. LoRA/PEFT only if supported and justified.
7. Full fine-tuning: **out of scope unless advisor explicitly approves**.

## References

- Chronos-2: https://huggingface.co/amazon/chronos-2
- TimesFM: https://github.com/google-research/timesfm
- TimesFM-3: https://research.google/blog/timesfm-3-a-zero-shot-foundation-model-for-multivariate-forecasting/
- CGMformer paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC11970253/
- CGMformer code: https://github.com/YurunLu/CGMformer
- GlucoFM: https://research.google/blog/glucofm-foundation-model-for-continuous-glucose-monitoring/
- GlucoFM-Bench: https://arxiv.org/abs/2606.06881
- EventGlucoseBench: https://github.com/JHU-CDHAI/EventGlucoseBench
- T1D-UOM: https://www.nature.com/articles/s41597-025-05695-1
- AZT1D: https://data.mendeley.com/datasets/gk9m674wcx/1
- HUPA-UCM: https://data.mendeley.com/datasets/3hbcscwz44/1
