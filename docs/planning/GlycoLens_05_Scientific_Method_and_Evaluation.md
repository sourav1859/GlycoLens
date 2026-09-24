# GlycoLens Scientific Method and Evaluation Plan

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

## 9. Experiment A - model selection

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
