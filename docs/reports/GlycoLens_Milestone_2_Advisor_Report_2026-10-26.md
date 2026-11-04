# GlycoLens Milestone 2 Progress and Experimentation Report

**Author** Sourav Patil  
**Advisor** Professor Haibo Yang  
**Prepared** October 26, 2026  
**Experiment period** October 14 to 16, 2026

## Main finding and milestone status

I completed the core Milestone 2 application prototype and the six-phase MetaboNet model-refinement study. The strongest research candidate is the trained direct LightGBM model. On the primary held-out cohort, it reduced participant-average trajectory error from 36.81 to 29.91 mg/dL, an 18.74% reduction relative to persistence. Its predictions were within +/-10 mg/dL only 28.20% of the time under participant-equal averaging. Tight precision remains poor, and performance on the pediatric PEDAP cohort is weaker. [R1, R6]

The research sequence is complete. Full Milestone 2 closure still requires live nutrition and recipe-provider verification, physical barcode-camera testing, and final presentation and acceptance evidence. The application continues to use the earlier validation-selected Chronos-2 configuration. LightGBM has not been substituted into the application. [R1, R7]

## Completed application work

| Area | Delivered capability | Evidence status |
|---|---|---|
| Demo workflow | Local authenticated session, glucose timeline, live py-mgipsim execution and labeled replay | Demonstrated with synthetic data |
| Meals and forecasts | Confirmed meal saving, real Chronos inference, 24 forecast points and persisted result retrieval | Local end-to-end path passed |
| Historical evidence | Same-user numeric similar-meal retrieval using outcomes available before the query origin | Implemented and locally verified |
| Nutrition and recipes | Food search, barcode/manual entry, structured recipe extraction, editable ingredients and deterministic nutrient calculations | Implemented; fixtures/offline tests passed; live provider and camera checks pending |
| Data protection | Ownership checks, row-level security, atomic saves, retry deduplication and server-side configuration | Automated and local database checks passed |

The prototype uses a Next.js interface, FastAPI backend and local Supabase database. Research datasets and model artifacts remain separate from application storage. Dexcom remains deferred. Meal Passport, portion comparison and later actual-versus-predicted follow-up remain later milestone work. The system is for research and education; no dosing or pump-control capability is included. [R1, R7]

<!-- page -->

## Experimental task and evaluation rules

The task is to predict 24 glucose readings at five-minute intervals over the next two hours. Persistence repeats the current glucose reading and provides the comparison baseline. Mean absolute error, or MAE, measures the average distance between forecast and actual readings in mg/dL; lower is better. The within-10 rate measures how often individual forecast points fall within +/-10 mg/dL. Neither is an overall percentage accuracy score. [R2, R6]

The original T1D-UOM benchmark compared Chronos-2 and TimesFM-3 with persistence. Context increased from glucose alone, to glucose with recorded insulin, then carbohydrates, and then available full meal nutrition. An initial UOM/AZT1D refinement was followed by the separate MetaboNet study. Scores from these different cohorts and protocols are reported separately. [R2, R3]

## Completed MetaboNet phases

| Phase | Experimentation | Finding or delivered evidence |
|---|---|---|
| 1 | Define within-10, tail-error and failure metrics; preserve prior results | Fixed evaluation rules and large-error audit |
| 2 | Audit source units, select participant roles and prepare causal windows | Loop/ReplaceBG development; primary and PEDAP reservations |
| 3 | Compare frozen Chronos histories and recorded-event context | Seven validation runs; no failure-free Chronos option beat persistence on MAE |
| 4 | Train direct Ridge and LightGBM models | 32 fixed candidates, three subject folds and 96 fold fits; 24-hour event models selected |
| 5 | Train corrections to frozen Chronos and matched direct controls | 18 fold fits and four final refits; neither correction passed the incremental advancement gate |
| 6 | Freeze candidates, calibrate intervals separately and evaluate reserved cohorts | Independent testing, uncertainty assessment and subgroup analysis completed |

For the selected direct models, training used 6,794 eligible meals from 197 source-qualified identities. Validation compared the same 1,509 matched meals from 48 identities. The final model uses 24-hour glucose history and six-hour recorded meal/insulin summaries. MetaboNet does not supply the full protein, fat and fibre context needed to establish their forecasting benefit. [R4, R5]

Participant roles were separated, transformations fitted on training data only, and point-model choices frozen before reserved outcomes were opened. Primary MetaboNet testing used publisher-test identities absent from all publisher training. PEDAP was a separate pediatric source holdout. Targets were not imputed, failed forecasts were retained, and predictions were not clipped or repaired to improve scores. [R4, R6]

<!-- page -->

## Model comparisons and selection

### Original pretrained benchmark

On the initial T1D-UOM test, 211 meals were requested and 208 succeeded across all model/context combinations. The following participant-average MAEs use that common-success population. C3 denotes glucose, recorded insulin and available full meal nutrition. [R2]

| Predictor on original T1D-UOM test | Trajectory MAE mg/dL |
|---|---:|
| Persistence | 33.96 |
| Chronos-2 C3 | 37.92 |
| TimesFM-3 C3 | 38.27 |

Chronos C3 was the strongest pretrained validation choice and was frozen before testing; persistence was more accurate on this test. Temporal partitions shared some participants, so this original benchmark was not subject-disjoint. A subsequent shared-feature Chronos correction improved UOM validation, but failed to transfer to AZT1D: MAE 34.87 versus persistence 33.87 on 2,608 matched successes from 2,610 requests. This negative external result supported broader development data. [R2, R3]

### MetaboNet development comparison

On the same 1,509 validation meals, direct LightGBM achieved MAE 31.17 versus persistence 37.12, a 16.03% reduction. The best failure-free frozen Chronos option achieved 37.61. Longer-history Chronos options sometimes improved conditional scores but also produced invalid outputs. The best Chronos correction achieved 31.14, only 0.03 mg/dL better than direct LightGBM; its uncertainty interval for the MAE difference included no improvement. No correction met the predeclared 5% incremental improvement requirement. [R4, R5]

### Final independent comparison

The primary cohort contained 3,533 meals from 102 eligible identities. PEDAP contained 2,177 meals from 64 eligible identities. All three fixed predictors attempted identical meals within each cohort and returned accepted outputs for every attempt. [R6]

| Cohort and predictor | MAE mg/dL | Within +/-10 |
|---|---:|---:|
| Primary persistence | 36.81 | 25.96% |
| Primary LightGBM | 29.91 | 28.20% |
| Primary Ridge | 30.31 | 28.94% |
| PEDAP persistence | 48.77 | 19.56% |
| PEDAP LightGBM | 40.92 | 19.57% |
| PEDAP Ridge | 41.69 | 21.04% |

LightGBM remains the research candidate under the predeclared MAE-first rule. It reduced MAE by 18.74% on primary testing and 16.10% on PEDAP. Ridge placed slightly more points within +/-10, while having higher MAE. The results support a useful average-error improvement; no tested model achieved dependable tight precision. Chronos was not rerun in Phase 6, and no test-based reselection occurred. [R6]

<!-- page -->

## Precision and uncertainty limitations

Trajectory MAE averages all 24 future time points. It should not be confused with the error at the two-hour endpoint. Forecasts became less accurate further into the future. [R6]

| LightGBM forecast horizon | Primary MAE mg/dL | PEDAP MAE mg/dL |
|---|---:|---:|
| 30 minutes | 20.94 | 32.21 |
| 60 minutes | 34.26 | 47.13 |
| 120 minutes | 40.90 | 52.91 |

Only 0.94% of primary and 0.18% of PEDAP meal curves stayed within +/-10 at every forecast point. The largest individual errors were 264.87 and 268.63 mg/dL, respectively. PEDAP's within-10 improvement over persistence was effectively negligible, even though its average-error improvement gate passed. [R6]

## Separately calibrated prediction bands

Calibration used one hash-selected eligible meal from each of 48 calibration identities, drawn from 1,488 eligible 24-hour windows. Separate radii were calibrated for individual horizons and for maximum error across the whole curve. Calibration changed uncertainty ranges, not point predictions. [R6]

| LightGBM uncertainty measure | Primary | PEDAP |
|---|---:|---:|
| Marginal point coverage with nominal 80% target | 79.05% | 63.94% |
| Whole-curve coverage using the separate curve band | 80.57% | 61.11% |
| Mean marginal interval width mg/dL | 96.73 | 96.73 |
| Constant whole-curve interval width mg/dL | 160.70 | 160.70 |

An 80% band is intended to contain actual values frequently within a range; it does not mean 80% of point predictions are within +/-10. LightGBM's two-hour marginal radius was about 64 mg/dL. These broad ranges expose substantial uncertainty. Primary average coverage also hides undercoverage at some early horizons, and pediatric coverage transferred poorly. [R6]

The following limits affect interpretation:

- Eligibility retrospectively excludes meals followed by another recorded meal during the forecast. These results do not cover all live meal situations.
- Five-minute carbohydrate availability is an assumption; actual logging latency and upstream processing are not fully known. Missing records cannot establish that no meal or insulin was delivered.
- Source-qualified identity separation and partial exact-trajectory checks reduce known overlap; they do not prove globally unique people or independence from foundation-model pretraining.
- Calibration has only 48 participant representatives. Dependence, study shift and incomplete records prevent patient-specific or clinical coverage guarantees.
- The model has not established causal nutrient effects, reliable portion-change predictions or safe treatment decisions. [R4, R6, R7]

<!-- page -->

## Proposed next steps

I recommend closing the remaining M2 application gates, preparing a reviewed LightGBM integration, and then running a separate development experiment for further accuracy improvements. These are proposed next actions rather than completed features. [R1, R7]

| Priority | Work | Evidence required before completion |
|---|---|---|
| 1 | Configure and verify live food search, barcode lookup and recipe parsing | Actual provider calls, editable ingredient confirmation, provenance and failure handling |
| 2 | Complete camera, desktop/mobile acceptance and presentation | Repeatable end-to-end demonstration and final requirement-to-evidence review |
| 3 | Build the LightGBM application compatibility bridge | Matching source units, event masks, 24-hour history and identical saved-model/API forecasts |
| 4 | Audit unused development subjects and test focused improvements | A new frozen protocol, participant-aware validation and a meaningful gain over current LightGBM |
| 5 | Reserve fresh confirmation and evaluate once | Separate calibration, held-out evaluation, tails, tolerance and subgroup evidence |

The current app supplies two hours of glucose history to Chronos. LightGBM requires 24 hours, previous recorded carbohydrates and consistent five-minute insulin amounts/masks. The fixed one-day simulator demonstration also needs a reviewed longer warm-up or another suitable demonstration path. A model-name substitution would not establish equivalent preprocessing or transfer the measured research accuracy to simulated application data. [R7, R8]

The current configuration still lacks the USDA key, recipe API key and recipe model name. Provider/model confirmation is needed; credentials stay private. Nutrition may show protein, fat and fibre, but the selected model's trained inputs do not establish effects for those nutrients. [R1, R4]

A metadata review identifies 463 additional training identities outside the pilot, plus 92 unused validation and 94 unused calibration identities. Their eligible windows and independence still require audit. Further work can test broader training, better recorded-event timing and small past-only personal adjustments. More calibration subjects may stabilize uncertainty estimates. Both completed test cohorts and the earlier AZT1D test are now consumed; a new confirmation group must be reserved before future outcome-based tuning. The unused pool is mostly Loop, so study balance needs attention. [R6, R9]

## Guidance requested from the advisor

1. Is LightGBM an appropriate research predictor for the next stage while retaining Chronos and TimesFM as pretrained comparisons?
2. Should I prioritize application integration and milestone closure or another accuracy-improvement experiment?
3. Which additional features, datasets or personalization methods would you recommend investigating?
4. Are MAE, within-10 rates, horizon-specific errors and interval coverage an appropriate evaluation emphasis, or should I add another criterion?

<!-- page -->

## Verification and reproducibility

The latest recorded Python preflight passed 155 tests with one explicit opt-in simulator skip. Earlier M2 evidence includes five frontend tests plus lint/type/build, 35 local database tests, six desktop/mobile browser checks, and an independently opted-in simulator suite with 11 passing tests. These are dated execution records rather than a claim that every integration was rerun on the report date. Live external nutrition and physical camera verification remain pending. [R1, R6]

The Phase 6 audit verified 17,130 test prediction records, calibration ranks, point and tail metrics, interval bounds and coverage, 19 subgroup counts/MAEs, and 18 saved/public/batch/wrapper prediction samples. Point-model states, original artifacts and checkpoint hashes remained unchanged. Configuration/source snapshots and completion manifests record the calibration-before-test sequence. No foundation-model weights were trained in the refinement sequence. [R6]

The research candidate is `lightgbm_24h_events_31`, refitted on 6,794 training meals. The original application still uses Chronos C3. The completed code and aggregate experiment reports were committed and pushed to repository checkpoint `474e57f`. Downloaded data, raw health rows, credentials, model weights and detailed prediction artifacts remain excluded from Git. [R4, R7, R10]

## Evidence references

- [R1] [Milestone 2 implementation verification](milestone-2-implementation-verification.md) and [approved implementation ledger](../planning/GlycoLens_10_Milestone_2_Implementation.md). Prototype evidence and remaining gates.
- [R2] [Original pretrained comparison and context ablation](milestone-2-model-results.md). T1D-UOM validation/test populations, errors and failure accounting.
- [R3] [Initial local refinement and AZT1D results](model-refinement-results-2026-10-16.md). Development improvements and failed external transfer.
- [R4] [MetaboNet direct-model training](metabonet-phase4-training-2026-10-16.md). Training-only CV, selected features, final refits and validation.
- [R5] [MetaboNet frozen-Chronos correction](metabonet-phase5-correction-2026-10-16.md). Matched controls, incremental gate and retained candidate.
- [R6] [MetaboNet independent evaluation](metabonet-phase6-independent-2026-10-16.md) and [verification handoff](../tooling/metabonet-phase6-handoff-2026-10-16.md). Final cohorts, uncertainty, limitations and audit evidence.
- [R7] [Model refinement ledger](../planning/GlycoLens_11_Model_Refinement.md) and [risk and scope record](../planning/GlycoLens_08_Risks_Safety_and_Scope.md). Research/application distinction and boundaries.
- [R8] [Application context builder](../../backend/app/services/inference/application.py) and [fixed simulator adapter](../../research/simulation/adapter.py). Serving input requirements and current demonstration constraints.
- [R9] [MetaboNet preparation protocol](../planning/GlycoLens_12_MetaboNet_Experiment.md). The frozen local subject manifest supplies the aggregate counts of unused roles; row-level identities remain ignored.
- [R10] [Published repository checkpoint](https://github.com/sourav1859/GlycoLens/commit/474e57fb536c1876fb95633964746ec724480e91). Committed implementation and aggregate evidence.

The proposed model and application changes require their own verification. This report records research progress and outstanding delivery work; it does not claim full Milestone 2 closure or clinical validation.
