# GlycoLens Scientific Method and Evaluation Plan

## November 12 implementation outcome — current status

The frozen synthetic matrix completed 236/236 predictions with three histories, meal/portion/composition contrasts and repeated identical inputs. At the earlier predeclared 0.001 mg/dL tolerance, **Chronos was invariant in 60/60 eligible contrasts: FAIL_INVARIANT** (max endpoint change 0.0000076294 mg/dL). LightGBM was invariant in 6/51 carbohydrate-changing contrasts; fat/protein/fiber-only invariance is expected because those current-meal features are unused. Exact repeats had zero spread. [Full interpretation](../reports/meal-response-sensitivity-2026-11-12.md). GL-P09-011 records capability failure despite engineering success. GL-P09-012 matching-outcome accuracy remains NOT_RUN: preset simulator future is not truth for arbitrary meals, and consumed cohorts were not reopened. No refit, calibration update or threshold tuning occurred.

The dated planning/checkpoint entries below remain historical where they describe unexecuted work.

## November 12: model integration is not a new accuracy study

[Plan 18](GlycoLens_18_M2_Closure_and_LightGBM_Integration.md) permits synthetic feature/prediction parity, repeatability and
sensitivity checks for the frozen LightGBM candidate, with Chronos still default.
It does not refit weights/calibration, reopen consumed primary/PEDAP tests or compare
different-cohort MAEs as a head-to-head model win. Saved symmetric participant
calibration has no verified synthetic/personal coverage guarantee. Fat/protein/fiber-
only changes should leave this carbohydrate-only candidate unchanged; report the
limitation. GL-P09-011 sensitivity is separate from GL-P09-012 matching-outcome
accuracy, which remains pending a new approved protocol/source. The old simulator's
preset later meals cannot validate an arbitrary proposed meal.

## November 12: application meal-response validation gate

Existing context-ablation and portion-calculation plans do not close application
meal-response validation. The [P09 protocol](../testing/meal-response-validation-protocol.md)
predeclares frozen-context portion/composition contrasts, repeated identical inputs,
input snapshots, trajectory/quantile changes and failures (GL-P09-011). Separately,
GL-P09-012 requires genuinely matching observed outcomes and an untouched approved
evaluation protocol for accuracy. Both are planned, not executed. The fixed demo
simulator's preset meals are not changed by the user's meal; its later trajectory
cannot validate that proposed meal. No model change, mandatory monotonic response,
causal claim or reuse of consumed primary/PEDAP test sets is authorized.

This document maps GlycoLens directly to the scientific-method structure required by the CSCI-788 course material:

> Introduction -> Background -> Analysis -> Solution/Hypothesis -> System/Experimentation/Synthesis -> Results -> Conclusions -> Future Work

## 1. Introduction - the problem

People with T1D repeatedly interpret:
- CGM changes
- food/macronutrients
- externally administered insulin
- activity
- personal history

Existing device data is rich, but turning it into a meal-specific, concrete explanation remains difficult.

### Capstone problem statement

> Can existing pretrained time-series/CGM models be used effectively at inference time, together with T1D-specific meal and physiological context, to generate useful short-term post-meal glucose forecasts inside a practical meal-intelligence application?

## 2. Background

The background will cover four bodies of work:

1. **T1D glucose forecasting**
2. **nutrition-aware/postprandial forecasting**
3. **time-series/CGM foundation models**
4. **consumer diabetes data applications**

This avoids presenting the idea as completely new and clearly positions the system relative to existing work.

## 3. Analysis

### Constraint A - data volume

T1D-UOM provides rich multimodal history but only 17 participants. That makes it valuable for evaluation and context studies but risky for training a large deep model.

### Constraint B - current model landscape

Strong pretrained time-series models now exist, and current glucose benchmarking shows that zero/few-shot foundation models can approach fully supervised glucose models.

### Constraint C - app usefulness

A technically good glucose forecast is not enough. The output must be:
- understandable
- uncertainty-aware
- grounded in meal facts
- connected to the user's own history

### Constraint D - safety

The capstone must not become a dose calculator or pump controller.

## 4. Proposed solution

Build GlycoLens as an **inference-first AI system** with:

- meal understanding
- nutrition grounding
- T1D context construction
- swappable pretrained model adapters
- event-centered retrospective evaluation
- probabilistic forecasts
- same-user historical meal retrieval
- portion comparison
- mobile-first PWA

## 5. Research questions

### RQ1 - model fit
Which pretrained model best fits the GlycoLens meal-centered T1D forecasting task?

### RQ2 - context
Does adding insulin and meal context improve forecasts over CGM-only inference?

### RQ3 - context richness
Does full nutrition (protein/fat/fiber) add value beyond carbohydrate alone?

### RQ4 - context window
What amount of pre-meal history provides the best accuracy/latency tradeoff?

### RQ5 - system usability
Can the selected model be integrated into an application with sufficiently low latency and a concrete, understandable output?

## 6. Hypotheses

These are hypotheses to test, not assumed truths.

### H1
At least one pretrained model will outperform a persistence baseline on held-out meal-centered T1D windows.

### H2
Adding available insulin and meal information will reduce forecast error relative to CGM-only inference.

### H3
Full meal nutrition will improve some postprandial forecasts relative to carbohydrate-only context, although the magnitude may be small and dataset-dependent.

### H4
A frozen pretrained model will be practically preferable to large custom training for this capstone when accuracy, engineering time, and inference latency are considered together.

## 7. Experimental unit

A single experiment instance is a **meal-centered window**.

```text
past context                  forecast target
-----------------------|---------------------------
CGM                    | future CGM
insulin                | 0 to +120 minutes
activity               |
previous meal          |
                       |
                    meal t=0
```

## 8. Data preparation

1. Harmonize timestamps.
2. Resample CGM to a consistent grid if needed.
3. Align insulin, nutrition and activity.
4. Identify meal events.
5. Build pre-meal context.
6. Remove or flag windows with conflicting future meal events.
7. Store the true future CGM separately.
8. Keep participant IDs for subject-aware evaluation.

### Milestone 1 operational policy

The first executable T1D-UOM V1.0.4 pipeline applies the following conservative feasibility policy:

- interpret source dates day-first, because this matches the observed files despite contradictory upstream README wording
- keep source timestamps timezone-naive and do not combine them with timezone-aware sources yet
- exclude nutrition rows that contain a date but no meal time
- use 120 minutes of CGM history and a 120-minute target on a five-minute grid
- require at least one basal or bolus event during the six hours before or at the meal
- aggregate nutrition components logged at the same timestamp
- exclude conflicting duplicate CGM timestamps instead of choosing or averaging a value
- reject gaps requiring interpolation across more than 15 minutes
- reject windows containing another meal in the forecast horizon

The resulting 927 eligible windows establish feasibility. Later experiments must report sensitivity to filtering, context length, missingness, and subject/time splits rather than treating this count as a fixed benchmark corpus.

Milestone 1 Phase 2 adds a structural leakage boundary: each window is converted into an immutable
model request and a separate held-out target. Adapters receive only the request. The implemented
persistence baseline carries the final pre-meal/current CGM observation across all 24 forecast
points. Its identical q10/q50/q90 trajectories are deterministic placeholders, not probabilistic
calibration. Accuracy metrics remain unreported until a defined evaluation split is executed.

Milestone 1 Phase 3 runs the pinned Chronos-2 model on C0 only. A real eligible 24-point history
produced a finite, non-crossing 24-point q10/q50/q90 forecast with the target withheld. This is an
interface/resource smoke test, not a comparison with persistence: no MAE, RMSE, CRPS, coverage, or
clinical metric is claimed from a single window. M2 implements C1-C3 covariate
alignment and offline tests; real ablation status is tracked separately in the
milestone ledger and is required before scientific conclusions.

Milestone 1 Phase 6 executes one pinned py-mgipsim ExtHovorka/OpenLoop synthetic day twice with a
fixed seed. Both 288-point, five-minute outputs are byte-identical and pass finite/range/grid and
aggregate-consistency checks. This is a reproducibility and software-feasibility result only.
Simulation trajectories must remain labeled synthetic and must not enter T1D-UOM accuracy metrics,
subject-level splits, or clinical claims.

## 9. Experiment A - model selection

M2 uses versioned temporal 60/20/20 time cuts with target purging and explicit
subject-holdout definitions. The real cohort has 536 development, 177 validation,
211 test and three purged events; twelve of fifteen participants have validation
and test events. Select on validation and require a frozen selection record before
test execution. Report failures and common successful events alongside event and
participant-macro metrics. Metric code implements MAE/RMSE, horizon errors, pinball
loss and interval coverage/width; deterministic persistence has no interval claim.
CI analysis remains pending. ADR 0008 defines recorded-event features and limitations.

Run the same test events through:

- Persistence
- Chronos-2
- TimesFM-3
- optional stable TimesFM-2.5
- optional CGMformer-based method
- optional LightGBM baseline

No conclusion is made before results.

## 10. Experiment B - context ablation

For the strongest one or two models:

```text
C0  CGM
C1  CGM + insulin
C2  C1 + carbohydrate
C3  C1 + full meal nutrition
C4  C3 + activity/time
```

This is the capstone's clearest scientific experiment.

## 11. Experiment C - context length

Compare a small number of history windows, for example:
- 2h
- 6h
- 12h
- 24h

Avoid an exhaustive search that consumes the semester.

## 12. Experiment D - application performance

Measure:
- model latency
- end-to-end API latency
- barcode lookup latency
- forecast error handling
- cache benefit
- mobile page performance

## 13. Experiment E - optional small usability study

Only if allowed and time permits.

Participants do **not** make medical decisions.

Tasks:
- scan a packaged food
- enter a recipe
- interpret a forecast
- find a similar historical meal
- compare portion scenarios

Possible measures:
- task completion
- completion time
- simple usability survey
- qualitative confusion points

## 14. Evaluation metrics

### Forecast quality

**MAE**
- intuitive average absolute error

**RMSE**
- penalizes large errors

**Horizon-specific MAE**
- +30
- +60
- +120 minutes

**Full-trajectory MAE**
- all forecast points over 2 hours

### Probabilistic forecasts

**CRPS**
- evaluates quality of forecast distributions where supported

**Interval coverage**
- how often actual glucose falls in the predicted interval

**Interval width**
- prevents "good coverage" from an excessively wide interval

### System

- p50 and p95 latency
- memory usage
- model load time
- failed-request rate

## 15. Statistical analysis

Where enough meal events are available:

- report mean + median error
- bootstrap confidence intervals over meal events
- repeat analysis by participant
- avoid treating thousands of highly correlated CGM points as independent participants
- compare models on the same event set

If formal paired testing is used:
- paired bootstrap or another paired method is preferable because the same meal windows are forecast by each model

## 16. Results section - planned structure

### October 16 refinement protocol

The subsequent [MetaboNet intake audit](../reports/metabonet-intake-audit-2026-10-16.md)
is preprocessing evidence, not a new experiment result. It read training values and
test metadata only. Supplied test is not wholly subject-disjoint: 169 source-qualified
IDs overlap, 166 have shared flags in both files, and 164 have at most a five-minute
forward boundary gap. Five have interleaved/reversed ranges; no exact cross-file key
duplicates were found. A future two-hour protocol must namespace IDs, define genuinely
test-only participants, retain a source holdout where feasible and purge targets at
all cuts. Build eligibility/missingness/source weighting before model selection.
Do not treat raw rows or positive-carb rows as independent eligible meal counts.
This intake performs no training/selection/test prediction. Subsequent experiments
follow the approved research direction with a new frozen split/protocol.

Saved-dictionary review confirms trailing-five-minute insulin amounts, but not exact
carbohydrate availability/bin endpoints. Define origin availability and development-only
timing sensitivity before meal windows. Preserve missingness; do not reinterpret all
nulls as observed zero. Global dictionary coverage (203.4M rows) is not coverage of
the local 154.88M-row pair. Split-flag meanings are confirmed; observed shared IDs
and horizon purging remain authoritative. No predictive experiment was run in the review.

The later Phase 2 preparation is now executed under
[document 12](GlycoLens_12_MetaboNet_Experiment.md). The source-balanced Loop/ReplaceBG
pilot fixes metadata-only subject quotas and hash-sampled origins before quality
inspection; rejected subjects are not replaced. Primary six-hour eligibility is
8,973 training / 2,000 validation / 1,948 calibration events, on disjoint subject roles.
The 104 primary-test and 65 PEDAP source-test identities are reserved using metadata
only. Test-event eligibility waits until the model/configuration freeze. Masks retain
unknown events; history fill uses past readings only (<=10 minutes, >=90% source-present),
with no target imputation or outcome clipping. The five-minute availability assumption
and zero-minute development sensitivity are predeclared. Isolated-meal filtering uses
future logged-meal presence retrospectively: subsequent scores estimate this conditional
population, not unrestricted live-meal performance. Exact partial duplicate checks are
not proof of distinct people. Compare histories on matched event IDs and report
variant eligibility/failed attempts, participant- and study-level metrics. Calibration
does not select a model. Data-preparation success is not prediction accuracy. See the
[aggregate preparation report](../reports/metabonet-phase2-preparation-2026-10-16.md).

The user approved +/-10 mg/dL as an aspiration. Report participant-average trajectory
MAE, point fractions within +/-10 (inclusive), 30/60/120-minute errors, whole-curve
pass rates, pooled p95/p99/max error, failures and attempted-event yields. Do not call
these regression measures an undefined "80% accuracy". A single good average cannot
establish a maximum-error guarantee.

MetaboNet Phase 3 fixes the full matched validation population before prediction.
Its primary selection table includes failure-free candidates only on that complete
population; failed candidates cannot delete hard events from it. Also report the
all-candidate common-success comparison and each candidate paired with persistence,
with their distinct denominators explicit. Failed attempted points count as unsuccessful
for within-10 yields. Native bands stay uncalibrated; do not sort crossing quantiles
or clip forecasts. Freeze sources/configuration/checkpoint hashes before inference
and preserve checksummed attempts across interruptions. The exact 10% gate boundary
is tested. Bootstrap at the participant level, not independent CGM points; selected
validation confidence intervals are descriptive. C1/C2 prediction differences do
not establish causal insulin/nutrition effects. See
[protocol 13](GlycoLens_13_MetaboNet_Frozen_Inference.md).

Executed Phase 3: 1,509 matched events/48 identities; 10,563 total attempts across
seven runs. Persistence selected (macro MAE 37.12; within-10 25.47%), improvement
gate failed. The only failure-free C0 is two hours, not the lowest-error C0 among
valid outputs. On 1,487 all-option common-success events, 24-hour C0 MAE is 33.50
versus 36.84 persistence, but 15/1,509 native outputs failed. Do not present the
strict reliability-based history choice as proof that shorter history predicts
better. Nominal 80% native-band coverage was only 49.42-64.08% across Chronos options.
These are validation findings, not calibrated/external accuracy or independent
before/after improvements on earlier cohorts. See
[the complete report](../reports/metabonet-phase3-inference-2026-10-16.md).

MetaboNet [Phase 4](GlycoLens_14_MetaboNet_Direct_Models.md) is complete. Histories,
feature profiles and two parameters per family were selected with three whole-subject
training folds on the common 6,756-meal/196-identity pool. Imputation/scaling fit only
fold-training data; pooled horizons expand after splitting; training weights equalize
participant totals. Freeze one CV winner per family and refit all eligible training
meals at its history before reading prepared validation outcomes. No validation
early stopping/adaptive search; no calibration/test data in selection.

The same 1,509-event validation comparison selects 24-hour event LightGBM:
MAE 31.17 versus 37.12 persistence, within-10 26.84% versus 25.47%, pooled p95
91.16 versus 111.00. The >=10% improvement gate passes (16.03%). Descriptive
participant-bootstrap MAE delta is -5.95 mg/dL, 95% interval[-7.60,-4.33]. This
reused validation evidence is not independent confirmation. Ridge has slightly
larger MAE 31.36 but higher within-10 28.85%; LightGBM's whole-curve-within-10 is
0.52% versus 1.44% persistence. Preserve these tradeoffs. No placeholder-band
coverage is reported. All 96 CV fits, saved predictions and reloads were verified;
a scoring-only NumPy conversion repair changed no fit/choice. See
[Phase 4 report](../reports/metabonet-phase4-training-2026-10-16.md). Phase 5 compares
corrections before Phase 6 calibration/reserved testing; no +/-10 guarantee.

Preserve original M2 results. Reused original test data is now diagnostic. Subdivide
the original development interval into 432 training, 101 calibration and three extra
purged events before history exclusions (six purged including original boundaries).
At the selected six-hour history there are 391 training, 93 calibration and 162
validation events. Training fits weights/transforms; validation selects; calibration
only estimates symmetric marginal 80% bands. Selection is written before external
AZT1D predictions. External data is never fitted or used for selection in this run.

The research improvement gate is >=10% MAE reduction against matched persistence,
nondecreasing +/-10 rate and no higher pooled p95 error. Report all candidate results
and failed gates. Participant-cluster paired bootstrap uses 10,000 draws/seed20261016;
selected validation confidence intervals are descriptive, not selection-adjusted.
Temporal dependence and source shift limit marginal interval coverage. No outcome
clipping, outlier deletion or future event inputs. Full-nutrient results cannot be
validated by AZT1D common features. See [protocol](GlycoLens_11_Model_Refinement.md)
and [aggregate results](../reports/model-refinement-results-2026-10-16.md).

October 14 real validation and test results are in `docs/reports/milestone-2-model-results.md`.
The application choice was frozen on 177 validation requests before 211 test requests.
Across all combinations there are 171/208 common successful events respectively;
pairwise bootstrap comparisons use their own explicitly reported common set.
Chronos C3 test macro MAE is 37.920 mg/dL on the all-run matched set versus persistence
33.957; coverage is about 53.9% for the nominal q10-q90 interval. H1 is not supported
by this held-out comparison. Nutrition improves some pretrained comparisons but
does not establish clinical efficacy, causal meal effects or calibrated uncertainty.
Participant-cluster paired percentile intervals use 2,000 draws and a fixed seed;
the small cohort remains a limitation. No test-based reselection was performed.

Do not write conclusions before experiments.

Planned tables/figures:

1. dataset/event counts
2. model selection table
3. context-ablation plot
4. context-length plot
5. latency/resource table
6. forecast examples
7. uncertainty calibration plot
8. app screenshots / system outputs

## 17. Conclusion questions

At the end, answer:

- Which model worked best?
- Did context improve it?
- Which context mattered?
- Was the latency acceptable?
- What did the app make easier?
- What failed?
- What cannot be concluded because of limited data?

## 18. Future work

Potential future work:
- official GlucoFM checkpoint if released
- more diverse T1D cohorts
- native mobile application
- real-user study with approvals
- robust activity/wearable integration
- clinician-facing summary
- carefully validated calibration/fine-tuning
- medical-device pathway only in a future regulated project

## Course alignment

The CSCI-788 materials explicitly define:
- project work as scientific work
- project presentation as problem -> background -> solution -> implementation -> milestones -> evaluation
- milestone progress as work completed, obstacles, insights and next plans
- final report around introduction, background, analysis, hypothesis, system/experimentation, results, conclusions and future work

GlycoLens will maintain this structure throughout the semester rather than treating the final report as something written only at the end.


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

The incremental gate requires >=5% lower MAE than the Phase 4 LightGBM incumbent, nondecreasing within-10, nonincreasing p95 and zero failures. Keep lowest-MAE ranking separate from advancement. Control and correction fits use identical usable training events/weights/folds; baseline failures are reported and never retried. Corrections jointly add forecast features and change labels to residuals, so the mechanisms are not individually isolated. Intervals are descriptive after selection; corrected bands remain placeholders.

## MetaboNet Phase 6 completion - current status

**The broader-data model-refinement sequence, Phases 1-6, is complete.** Separate calibration used 48 participant representatives from 1,488 eligible meals. Frozen LightGBM scored 29.91 mg/dL macro trajectory MAE / 28.20% within +/-10 on 3,533 primary-test meals (102 IDs), and 40.92 / 19.57% on 2,177 PEDAP meals (64 IDs). Both predeclared point-improvement gates passed, with zero failed forecasts; tight precision remains poor. Nominal 80% marginal coverage was 79.05% primary and 63.94% PEDAP. Both test cohorts are now consumed; no test-based reselection, point refit, app promotion or full-M2 closure.

One hash-selected meal per calibration participant limits repeated-meal dominance. Exact rank 40/48 calibrates 24 marginal radii and a separate maximum-error curve radius. Exchangeability is unverified. Primary curve-band coverage is 80.57%, PEDAP 61.11%; marginal average coverage hides weak individual horizons. Test bootstrap intervals are descriptive participant-cluster intervals.

See [protocol 16](GlycoLens_16_MetaboNet_Independent_Evaluation.md), [independent results](../reports/metabonet-phase6-independent-2026-10-16.md) and [verification handoff](../tooling/metabonet-phase6-handoff-2026-10-16.md).
