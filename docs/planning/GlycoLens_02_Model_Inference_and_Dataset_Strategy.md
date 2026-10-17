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

### Implemented forecast-contract boundary

Milestone 1 Phase 2 implements one immutable contract for baselines and pretrained models:

- `ForecastRequest` contains only CGM history, past covariates, covariates known at forecast time,
  the horizon, frequency, and requested quantiles.
- Held-out future CGM is stored in a separate `ForecastTarget`; adapters cannot accept it.
- `ForecastExample` joins request and target only for post-prediction evaluation and requires an
  exact five-minute target grid.
- The T1D-UOM converter supports C0 (CGM), C1 (CGM + insulin), and the currently available portion
  of C3 (C1 + carbs/protein/fat/fiber). M2 adds C2 (C1 + carbohydrate) and separates basal
  observations by insulin kind. Calories are not invented when the source does not provide
  them.
- Persistence repeats the final observed CGM value. Its q10/q50/q90 are equal because the baseline
  is deterministic and must not be interpreted as calibrated uncertainty.

Requests reject non-finite values, irregular history grids, mixed timezone awareness, future
values in past covariates, and duplicate covariate names. Results reject invalid shapes,
non-finite values, irregular forecast grids, and crossing quantiles.

### Implemented Chronos-2 feasibility boundary

Milestone 1 Phase 3 pins `chronos-forecasting==2.3.2` and `amazon/chronos-2` revision
`29ec3766d36d6f73f0696f85560a422f50e8498c`. The first adapter is intentionally C0/CGM-only and
CPU-based. It transforms the 24 historical CGM values into the official tensor API, requests a
24-step q10/q50/q90 forecast, and normalizes the result into `ForecastResult`.

The M1 adapter rejected C1/C3 requests rather than silently ignoring insulin or nutrition. One real
T1D-UOM window completed successfully with finite, non-crossing output. Cached CPU measurements
were 5.54 s model load, 56.04 ms first forecast, 54.63 ms warm p50, 61.26 ms warm p95, and
810.83 MiB observed peak RSS. These measurements prove local feasibility only; model ranking
still requires predefined subject/time splits and accuracy/calibration evaluation over many
windows.

## 8. Main inference experiments

### Milestone 2 implementation - October 14, 2026

`research/evaluation/protocol.py` implements target-purged temporal 60/20/20 cuts and
explicit subject holdouts. The real scan reproduces 927 events: 536 development,
177 validation, 211 test and three purged. Twelve of fifteen participants have both
validation and test events. Manifests stay ignored. The evaluator reports failures,
matched successful events and participant-macro metrics. The original validation
selection was frozen before final test execution (see the original M2 results report).

#### Approved refinement - October 16

The new [refinement protocol](GlycoLens_11_Model_Refinement.md) preserves that M2
evidence and treats its inspected test as diagnostic. Development is subdivided into
training and separate calibration with target purging. History variants inherit the
original split identities. Frozen C0 Chronos is compared at 2/6/12/24 hours on the
130 common eligible events (129 common successful forecasts); available-event
sensitivity and the failed 24-hour request are reported separately.
Six hours was selected before the small-model grid. Train-only weighted Ridge and
LightGBM direct/residual heads use origin-known CGM, recorded bolus, clock and meals.
Shared and full-nutrient variants are separate; ambiguous basal values are omitted.
Foundation weights remain frozen. All results, including baseline wins or failed
gates, belong in the [execution report](../reports/model-refinement-results-2026-10-16.md).

Chronos covariate input and TimesFM 3.0.2 implement `recorded_events_v1`: kind-separated
insulin values/masks, older-context descriptors, and meal-origin impulses. These are
source-record features, not insulin-action estimates. See ADR 0008 and the milestone
ledger for real validation status. Offline tests alone do not establish efficacy.

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

**Pinned release:** V1.0.4, Zenodo DOI `10.5281/zenodo.17361905`, Git release commit `ea52718b41cd27286df46acf87825555d4ec0463`.

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

### Milestone 1 implementation audit

The executable audit covers the four core modalities required for initial forecasting feasibility: CGM, nutrition, bolus insulin, and basal insulin. It found 15 participants with CGM, nutrition, and at least one insulin stream; 13 contain all four streams.

Important implementation findings and rules:

- V1.0.4 values use day-first timestamps even though the upstream README describes month-first formatting; GlycoLens parses day-first first.
- Source timestamps have no timezone offsets and remain timezone-naive pending an explicit cross-source/DST policy.
- Rows with missing required model fields are reported and excluded.
- Nutrition rows without a meal time are reported and excluded rather than assigned an artificial midnight timestamp.
- Exact repeated CGM values collapse; conflicting values at the same timestamp are excluded rather than averaged.
- Multiple nutrition rows at the same timestamp are aggregated as one meal event.
- Initial windows use 120 minutes of pre-meal CGM, a five-minute grid, six hours of prior insulin context, and a separate 120-minute/24-point target.
- Windows with another meal inside the target horizon or with CGM gaps beyond the configured interpolation boundary are rejected.

Under this initial policy, 927 of 3,884 valid loaded meal events produced eligible windows. These rules are a feasibility configuration and require later sensitivity analysis; they are not clinical validation criteria.

### AZT1D

**Use:** external validation with common features.

October 16 acquisition: V1 archive SHA-256
`2c6b4183fdc729c708c1b3230ab1988d2c9006dd35729537f2de07f649f0d113`,
776,131,685 bytes, CC BY 4.0. The tested loader restricts ingestion to 25 canonical
CGM Records files (306,712 source rows), excluding five Visual Statistics exports.
Exact duplicate rows collapse; conflicting CGM timestamps are excluded; only finite
positive glucose is retained. Carbohydrate events use CarbSize (g); bolus uses total
delivered units without adding correction twice. Missing full nutrients never enter
shared features. One glucose header also mentions BGM, a retained modality caveat.
Same source-local timestamps, CGM-gap and follow-up-meal exclusions apply. At six
hours, 2,610 events from 24 participants are eligible. Exact aligned trajectory
fingerprints check overlap but cannot prove subject disjointness across sources.
Selection is immutable before external scoring. Later tuning must treat this test
as consumed. MetaboNet was deferred for the first run; its later intake is recorded below.

Available:
- 25 T1D participants
- 6-8 weeks
- CGM
- insulin
- carbohydrates
- device modes

Not available in same detail:
- full protein/fat/fiber meal composition

### MetaboNet v1.2 intake - October 16

The user supplied both Parquet files and portal release notes for v1.2 (October 5).
Local hashes/footers identify 132,811,004 training and 22,069,548 test rows, matching
37-column schemas. Training has 1,730 source-qualified IDs across 15 studies; raw IDs
are reused across studies. There are 169 source-qualified IDs in both files and 182
test-only combinations before exclusions. Most shared boundaries have a five-minute
gap, not a 24-hour purge. No test outcome columns were read; only schema, IDs/source,
date and split flags. No new training or predictive evaluation has occurred.

Exclude AZT1D/UOM copies from development. Separate meal-bearing studies from those
without carbohydrate entries; missing sparse events are not confirmed zeros. BrisT1D
and CTR3 have merged insulin without separate bolus/basal. SIESTA has five-minute cadence
with per-subject wall-clock offsets; preserve that grid. OhioT1DM needs current terms
confirmation because the publication lists it as DUA-governed. The remaining sources
can proceed through documented preparation independently. See the
[audit](../reports/metabonet-intake-audit-2026-10-16.md) for all counts and limitations.

The subsequent saved dictionary documents all 37 fields and confirms all 15 actual
training source labels. CGM is mg/dL; carbs are grams; basal/bolus/total insulin are IU
delivered in the previous five minutes, not hourly rates. Total is basal plus bolus;
do not double-count. In IOBP2, all insulin is encoded as bolus. Keep that exception
separate from conventional bolus channels. Source zero/null differences, ambiguous
timezones and physical DOUBLE columns must be preserved rather than normalized by
assumption. Carb availability/bin endpoints are not explicit. The dictionary does
not grant use rights or replace observed identity/split checks. See the
[dictionary review](../reports/metabonet-dictionary-review-2026-10-16.md).

The approved Phase 2 loader is now implemented in `research/datasets/metabonet.py`
and `research/pipelines/prepare_metabonet.py`. A bounded DuckDB projection of selected
publisher-training rows is followed by one-subject streaming. Loop/ReplaceBG supply
100/25/25 preselected subjects per source after a source-stratified 70/15/15 subject
split. Candidate meals are capped at 100 per subject using stable hashes, before
target inspection. The primary six-hour sets contain 8,973/2,000/1,948 windows across
197/48/48 usable IDs. Histories 2/6/12/24 hours and five-/zero-minute carb-availability
variants share candidate IDs; compare only matched eligible events later.

Keep unknown event entries and source-present masks; insulin is not forward-filled.
History permits at most ten minutes of past-only fill with >=90% source-present CGM;
all 24 targets must be finite positive source values. Reject clustered/follow-up
meals under the predeclared retrospective isolated-meal task. Immutable requests
exclude future truth. Primary reserved test is 104 test-only Loop/ReplaceBG identities;
the separate PEDAP holdout is 65 identities. Their eligibility is intentionally unknown
until selection freezes. Exclude consumed cohorts and OhioT1DM; partial exact CGM
duplicate screening found no candidates, not proof of globally distinct people.
Frozen sources/hashes and replay/integrity checks preserve evidence. No model fitting
or app change. See [document 12](GlycoLens_12_MetaboNet_Experiment.md),
[ADR 0011](../decisions/0011-metabonet-development-and-reserved-tests.md) and
[executed counts](../reports/metabonet-phase2-preparation-2026-10-16.md).

### MetaboNet frozen-inference comparison

The authorized Phase 3 experiment is fixed in
[document 13](GlycoLens_13_MetaboNet_Frozen_Inference.md). It consumes validation only,
matching 1,509 events across all four history lengths before prediction. Seven runs
compare persistence, C0 at 2/6/12/24 hours and C1/C2 at a fixed six-hour reference.
C1 uses recorded bolus/basal amounts and masks; C2 adds logged carbs. Total insulin
is omitted when components are used. The existing Chronos adapter/alignment and
checkpoint remain unchanged. No full nutrients or physiological insulin activity
are inferred. Failed native outputs are counted, not repaired/retried. History and
context selection are validation decisions, not independent performance confirmation.
See the [results](../reports/metabonet-phase3-inference-2026-10-16.md) for execution.

Executed result: persistence is the best failure-free option (macro MAE 37.12,
within-10 25.47%); C2 is 37.61/25.98%, while C0 two hours is 42.52/23.52%.
Six-/twelve-/24-hour C0 have 2/11/15 native-output failures; C1 has one, C2 none.
On the 1,487-event all-option common-success set, 24-hour C0 has MAE 33.50 versus
36.84 persistence, showing useful longer-history signal conditional on valid output.
It still fails the frozen reliability rule. The Phase 4 history artifact records two
hours as the only failure-free C0; train-only CV may assess longer-history features
for small models without rewriting that decision. No frozen option passed the gate.

### MetaboNet direct-model training

Executed [Phase 4](GlycoLens_14_MetaboNet_Direct_Models.md): a dedicated common-contract
adapter preserves native amount units and missingness masks. Training-only three-fold
subject CV compares 32 fixed history/profile/parameter candidates on 6,756 meals from
196 identities. Both families select 24-hour event features: Ridge alpha 1000 and one
pooled-horizon LightGBM with31 leaves/160 trees. Refit 6,794 eligible training meals
from 197 identities, freezing train-only imputation/scaling before validation.

On the same 1,509 validation meals, LightGBM wins the predeclared MAE-first rule:
31.17 mg/dL versus persistence 37.12, 16.03% improvement, gate passes. Ridge has
MAE 31.36 and higher within-10 (28.85% versus 26.84%); retain it as a tolerance
challenger rather than claim LightGBM dominates every metric. Both have zero failed
forecasts/negative predictions here, but tight-tolerance/whole-curve performance is
still weak. At Phase 4 completion there were no calibrated bands or reserved-test results. Phases 5 and 6 subsequently completed; see the current ledger below. Original CV/model bytes and frozen baselines were preserved through a
documented scoring-only numeric-conversion repair. See
[results](../reports/metabonet-phase4-training-2026-10-16.md) and ADR 0012.

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
- T1D-UOM V1.0.4: https://zenodo.org/records/17361905
- T1D-UOM data descriptor: https://www.nature.com/articles/s41597-025-05695-1
- AZT1D: https://data.mendeley.com/datasets/gk9m674wcx/1
- HUPA-UCM: https://data.mendeley.com/datasets/3hbcscwz44/1


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

Retain original Phase 4 LightGBM as the frozen research candidate. Ridge remains a diagnostic tolerance challenger. Phase 5 correction heads did not advance. New tuning needs development-only selection and fresh confirmation.

See [protocol 16](GlycoLens_16_MetaboNet_Independent_Evaluation.md), [independent results](../reports/metabonet-phase6-independent-2026-10-16.md) and [verification handoff](../tooling/metabonet-phase6-handoff-2026-10-16.md).
