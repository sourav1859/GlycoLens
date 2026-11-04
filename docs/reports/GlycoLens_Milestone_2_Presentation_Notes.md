# GlycoLens Milestone 2 Presentation Notes

**Presenter:** Sourav Patil  
**Advisor:** Professor Haibo Yang  
**Course:** CSCI-788  
**Presentation date:** November 3, 2026  
**Revised:** November 3, 2026  
**Target:** 7–8 minutes plus questions. Rehearse Slides 1–10 to 7:30.  
**Speech length:** 875 words in Suggested speech and 927 including transitions. Approximately 124 words per minute over 7:30, including chart pauses. Rehearsal determines the final pace.  
**Deck:** [Milestone 2 PowerPoint with matching speaker notes](../presentations/GlycoLens_Milestone_2_Presentation_2026-11-03_v4.pptx)  
**Scope:** Ten main slides and four hidden backup slides. Backup material and question answers are outside the timed talk.

## Presentation strategy

Use the Milestone 1 progress-report style: a short project reminder, followed by what was built, what was measured, what the findings support, and what remains. Explain unfamiliar technical terms briefly when they first matter. Avoid elementary lessons, extended analogies and invented arithmetic examples.

Read Suggested speech and Transition for the timed talk. What to emphasize, the optional term reference and prepared answers support rehearsal and questions. They are not additional speech. Pause at the charts and round spoken results where the script does so. Exact values remain visible on the slides.

Keep the original pretrained comparison, later broader-data study, current Chronos application and LightGBM research candidate distinct. Lower average error is useful progress, while tight precision and pediatric reliability remain weak.

Slides 11–14 are hidden during normal slideshow playback. Open them through the slide navigator or a slide-number jump for relevant questions. The embedded PowerPoint notes match the slide-specific speech, emphasis and evidence references below.

The implementation and experiment evidence comes from October 14–16. The screenshot is the recorded virtual-patient demonstration with example nutrition and real Chronos inference. It is interface evidence, not a new November run or an accuracy example. Live food/recipe-provider verification and final acceptance remain pending.

## Optional technical-term reference

Keep these short definitions ready for questions. Do not read the table as part of the presentation.

| Term | Brief explanation |
|---|---|
| Persistence baseline | Repeat the latest glucose reading for every future point. It is the simple comparison a model should beat. |
| MAE, or mean absolute error | Average size of prediction errors. Lower is better. The main result gives each participant equal weight. |
| Inference / training | Inference runs an existing model. Training fits its parameters using development examples. |
| Held-out participants | Participants reserved from development. Final test results are examined after model choices are fixed. |
| Calibration / coverage | Calibration sets prediction-band widths on separate data. Coverage measures how often actual readings fall inside those bands. |
| Within ±10 | A central prediction differs from the recorded value by no more than ten mg/dL. This differs from band coverage. |

## Suggested timing

| Slide | Topic | Target | Cumulative |
|---|---|---:|---|
| 1 | GlycoLens Milestone 2 | 20 sec | 0:00–0:20 |
| 2 | The problem | 40 sec | 0:20–1:00 |
| 3 | The GlycoLens solution | 45 sec | 1:00–1:45 |
| 4 | What Milestone 1 established | 30 sec | 1:45–2:15 |
| 5 | The connected Milestone 2 prototype | 50 sec | 2:15–3:05 |
| 6 | Pretrained models did not beat the baseline | 60 sec | 3:05–4:05 |
| 7 | LightGBM improved average prediction error | 70 sec | 4:05–5:15 |
| 8 | Precise predictions remain difficult | 65 sec | 5:15–6:20 |
| 9 | Obstacles, insights and personal assessment | 30 sec | 6:20–6:50 |
| 10 | Remaining work and Milestone 3 priorities | 40 sec | 6:50–7:30 |
| **Total** | **Timed presentation** | **450 sec** | **7:30** |

## Slide-by-slide notes and suggested speech

## Slide 1: GlycoLens Milestone 2

**Target time:** 20 seconds (0:00–0:20)

### What to emphasize

- Introduce the milestone and the progress/results/next-steps structure. Keep the project reminder brief.
- Use Slides 1–10 for the 7–8 minute talk, targeting 7:30. Slides 11–14 are hidden backups for questions.

### Suggested speech

Good afternoon. This is my Milestone 2 update for GlycoLens. I will cover the connected prototype, the model experiments, what the results support, and the work that remains before the next milestone.

### Transition

First, a brief reminder of the problem.

### Evidence

- [Project specification](../planning/GlycoLens_09_Project_Specification_Draft.md)
- [Milestone 2 implementation and acceptance ledger](../planning/GlycoLens_10_Milestone_2_Implementation.md)

---

## Slide 2: The problem

**Target time:** 40 seconds (0:20–1:00)

### What to emphasize

- Give the project reminder without repeating the specification or a diabetes lesson.
- Expand CGM once. Keep the research question about added meal/insulin information distinct from the later comparison between model families.

### Suggested speech

GlycoLens aims to help people with Type 1 Diabetes understand how their glucose might change during the two hours after a meal. A continuous glucose monitor, or CGM, provides regular readings, but interpreting them alongside food and insulin records takes effort. The project brings these records together with a forecast and evidence from earlier meals. The research question is whether meal and insulin information improve that forecast beyond using glucose history alone. That benefit needs to be measured rather than assumed.

### Transition

This is the proposed solution.

### Evidence

- [Project specification](../planning/GlycoLens_09_Project_Specification_Draft.md)

---

## Slide 3: The GlycoLens solution

**Target time:** 45 seconds (1:00–1:45)

### What to emphasize

- Follow the workflow diagram. Keep proposed capabilities distinct from completed acceptance evidence.
- The common adapter is a shared input/output interface. Explain its purpose in one sentence.
- The current app uses Chronos. LightGBM remains a separately evaluated research candidate.
- Live food-provider verification, full Meal Passport and portion comparison remain pending/later work.

### Suggested speech

The proposed workflow starts with meal entry and editable nutrition information. After the user confirms the ingredients and portions, the application combines the meal with earlier glucose and available insulin records to produce a two-hour forecast. It also retrieves earlier similar meals for comparison. The design keeps forecasting behind a common interface, so different models can be evaluated without rebuilding the application. At this stage, the working application uses Chronos. LightGBM, which I will discuss later, is a separate research candidate. The application remains for research and education, with no insulin-dose recommendations.

### Transition

Milestone 1 provided the foundations.

### Evidence

- [Milestone 2 implementation verification](milestone-2-implementation-verification.md)
- [Milestone 2 implementation and acceptance ledger](../planning/GlycoLens_10_Milestone_2_Implementation.md)
- [Project specification](../planning/GlycoLens_09_Project_Specification_Draft.md)

---

## Slide 4: What Milestone 1 established

**Target time:** 30 seconds (1:45–2:15)

### What to emphasize

- Recap M1 briefly: data audit, standalone model execution, browser display and reproducible simulation.
- M1 established feasibility. M2 adds comparative accuracy evidence and the connected workflow.

### Suggested speech

Milestone 1 established the individual building blocks. I audited the glucose, meal and insulin data, prepared meal-centered examples, ran Chronos locally, built the browser forecast display, and verified a reproducible simulation. The main open questions were prediction quality and integration. Milestone 2 therefore focused on connecting the workflow and evaluating the models against a simple comparison.

### Transition

Here is the progress on integration.

### Evidence

- [Milestone 1 closure audit](milestone-1-closure-audit.md)
- [Milestone 2 implementation verification](milestone-2-implementation-verification.md)

---

## Slide 5: The connected Milestone 2 prototype

**Target time:** 50 seconds (2:15–3:05)

### What to emphasize

- Identify the recorded virtual-patient demo, example nutrition and real Chronos execution.
- The saved forecast has 24 points on a five-minute grid. Earlier-meal retrieval is numeric and limited to the same session.
- Treat the screenshot as interface evidence. It does not demonstrate model accuracy.
- Offline food/recipe tests do not replace pending live provider verification and final acceptance.

### Suggested speech

The screenshot shows the connected local prototype. A simulated patient supplies the glucose timeline. I can review and save a meal, run real Chronos inference, save the twenty-four five-minute forecast points, and retrieve earlier simulated meal outcomes within the same session. Inference means running an already-trained model to produce predictions. The recorded demonstration uses example nutrition, so it demonstrates the application flow rather than prediction accuracy. Automated checks covered data storage and the main desktop and mobile flows. Food and recipe-provider paths are implemented and tested offline, but live verification and final acceptance checks remain open.

### Transition

The model experiments addressed prediction quality.

### Evidence

- [Milestone 2 implementation verification](milestone-2-implementation-verification.md)
- [Milestone 2 implementation and acceptance ledger](../planning/GlycoLens_10_Milestone_2_Implementation.md)

---

## Slide 6: Pretrained models did not beat the baseline

**Target time:** 60 seconds (3:05–4:05)

### What to emphasize

- Define persistence and MAE briefly, then focus on the bars and the negative finding.
- Use the original T1D-UOM cohort only: 208 common-success test windows out of 211 attempts.
- The models used fixed pretrained weights. Input configurations were selected on validation before the test.
- Trajectory MAE averages all 24 forecast points and weights participants equally. It is not the two-hour endpoint error.
- The original temporal split was not participant-disjoint. Do not describe it as the later independent MetaboNet test.

### Suggested speech

I first compared Chronos and TimesFM against persistence, a baseline that repeats the latest glucose reading throughout the forecast. Both pretrained models were used without retraining. I varied the inputs from glucose alone through insulin, carbohydrates and the available fuller nutrition. The chart reports mean absolute error, or MAE: the average size of the prediction error, where lower is better. On the same 208 successful test examples, persistence scored about thirty-four milligrams per deciliter, while both pretrained models scored about thirty-eight. These are averages across the two-hour forecast, with each participant weighted equally. The pretrained models did not beat the baseline. That result justified testing broader data and smaller models trained for this task.

### Transition

The broader study produced a stronger candidate.

### Evidence

- [Original pretrained-model comparison](milestone-2-model-results.md)
- [Frozen Chronos history and context comparison](metabonet-phase3-inference-2026-10-16.md)
- [Direct Ridge and LightGBM training](metabonet-phase4-training-2026-10-16.md)
- [Frozen-Chronos correction and matched controls](metabonet-phase5-correction-2026-10-16.md)

---

## Slide 7: LightGBM improved average prediction error

**Target time:** 70 seconds (4:05–5:15)

### What to emphasize

- Explain the experimental sequence without reading every development configuration aloud.
- LightGBM was retained before independent outcomes. No test-based reselection occurred.
- Primary: 3,533 meals / 102 eligible IDs. PEDAP: 2,177 meals / 64 eligible IDs.
- Use each cohort’s own persistence baseline. Report relative MAE reduction, not percentage accuracy.
- Ridge had somewhat higher within-10 rates, but LightGBM had lower MAE. The chosen rule prioritizes MAE.
- The correction did not meet the predefined 5% incremental improvement requirement. Foundation-model weights stayed frozen.

### Suggested speech

The broader study used MetaboNet, with separate participant groups for development, setting prediction ranges, and independent testing. I compared longer Chronos histories, trained Ridge and LightGBM, and tested a correction model on top of Chronos. The correction added too little benefit to justify the extra complexity, so direct LightGBM remained the selected candidate before the final tests. It uses a full day of glucose history and summaries of recorded meals and insulin. On 3,533 test meals from 102 participants, LightGBM reduced average error from 36.81 to 29.91, nearly nineteen percent. On the separate pediatric group, error fell from 48.77 to 40.92, about sixteen percent. Ridge was close, but LightGBM performed better under the selection rule that prioritized average error. The improvement percentages describe reductions in error, not an overall accuracy score.

### Transition

However, precise forecasts remain difficult.

### Evidence

- [Direct Ridge and LightGBM training](metabonet-phase4-training-2026-10-16.md)
- [Frozen-Chronos correction and matched controls](metabonet-phase5-correction-2026-10-16.md)
- [Independent MetaboNet evaluation and calibration](metabonet-phase6-independent-2026-10-16.md)

---

## Slide 8: Precise predictions remain difficult

**Target time:** 65 seconds (5:15–6:20)

### What to emphasize

- State the poor within-10 and whole-curve results directly.
- The tolerance is a stretch goal, not a maximum-error guarantee or a clinical acceptance condition.
- Explain coverage in one sentence. Distinguish coverage of broad bands from precision of the central prediction.
- Calibration set band widths without changing point predictions. Primary average coverage does not imply coverage at every horizon.
- Pediatric performance is weaker. The evaluation covers retrospectively isolated logged meals, not every live meal.

### Suggested speech

The improvement still leaves a substantial precision problem. LightGBM predictions were within ten milligrams per deciliter of the recorded value only about twenty-eight percent of the time in the primary group, and twenty percent in the pediatric group. For the entire two-hour curve to stay within that tolerance, the rate was below one percent in both groups. Error also increased further into the forecast. I separately calibrated prediction bands using participants reserved for that purpose. Coverage means how often actual readings fall inside those bands. Against an eighty-percent target, coverage was about seventy-nine percent in the primary group but sixty-four percent in the pediatric group. These bands were broad. Their coverage does not establish precise predictions, and the pediatric result shows that reliability did not transfer consistently between groups.

### Transition

These results shaped my main lessons.

### Evidence

- [Independent MetaboNet evaluation and calibration](metabonet-phase6-independent-2026-10-16.md)

---

## Slide 9: Obstacles, insights and personal assessment

**Target time:** 30 seconds (6:20–6:50)

### What to emphasize

- Give the main data, evaluation and integration lessons. Avoid repeating the full methods section.
- A working prototype and an average-error improvement do not establish dependable individual predictions.

### Suggested speech

The main obstacles were incomplete records, differences between datasets, and the gap between a working demonstration and a dependable predictor. My strongest lesson was to establish a baseline and keep independent testing separate from model development. The experiments produced a better research candidate, but also showed why lower average error alone is insufficient evidence for reliable individual forecasts.

### Transition

Here are the next priorities.

### Evidence

- [Original pretrained-model comparison](milestone-2-model-results.md)
- [Milestone 2 implementation verification](milestone-2-implementation-verification.md)
- [Independent MetaboNet evaluation and calibration](metabonet-phase6-independent-2026-10-16.md)
- [Milestone 2 implementation and acceptance ledger](../planning/GlycoLens_10_Milestone_2_Implementation.md)

---

## Slide 10: Remaining work and Milestone 3 priorities

**Target time:** 40 seconds (6:50–7:30)

### What to emphasize

- Complete live nutrition/recipe verification and final acceptance evidence. Credentials remain private.
- Review units, feature timing, logging availability and simulator warm-up before integrating the 24-hour LightGBM candidate.
- Full Meal Passport and actual-versus-predicted follow-up are later priorities. Portion effects are not causally validated.
- Further outcome-based tuning needs fresh confirmation. The completed test groups are no longer untouched.
- End with the advisor-priority request and invite questions.

### Suggested speech

Next, I will finish live food and recipe verification and the remaining acceptance checks. LightGBM integration needs a reviewed input pipeline because it expects twenty-four hours of glucose history, while the application currently supplies two. Milestone 3 should also improve the earlier-meal view and comparison of predicted and actual outcomes. Further model tuning will require fresh confirmation data, since the current test groups have already been examined. I would appreciate guidance on prioritizing integration versus another improvement experiment. Thank you. I am happy to take questions.

### Evidence

- [Milestone 2 implementation and acceptance ledger](../planning/GlycoLens_10_Milestone_2_Implementation.md)
- [Independent MetaboNet evaluation and calibration](metabonet-phase6-independent-2026-10-16.md)
- [Course-aligned milestone schedule](../planning/GlycoLens_06_Milestones_and_Schedule.md)
- [Risk, safety and scope record](../planning/GlycoLens_08_Risks_Safety_and_Scope.md)

---

## Slide 11: Backup A: experiment design

**Timing:** Backup for questions. Outside the 7–8 minute talk.

### What to emphasize

- These are the six phases of the additional model-refinement sequence, not the separate M2 application phase numbers.
- The selected model refit used 6,794 training meals / 197 source-qualified IDs. Validation used 1,509 matched meals / 48 IDs.
- Calibration had 1,488 eligible 24-hour windows, but one hash-selected event per eligible identity gave 48 representatives.
- Independent cohorts used 3,533/102 primary and 2,177/64 PEDAP meals/IDs. Roles are separated, not a random row split.
- Native five-minute insulin amounts and record-presence masks are source-specific. Event availability assumes five-minute delayed logged carbohydrates.
- Eligibility excludes meals followed by another logged meal within the target horizon. That retrospective rule limits live generalization.

### Suggested speech

The broader-data study followed six stages: define evaluation rules, prepare separated data, compare frozen inference, train direct small models, test Chronos corrections, and perform separate calibration and independent testing. The chosen model used twenty-four hours of glucose and six hours of recorded event summaries. Participant roles were separated before testing, and transformations learned from training only. The isolated-meal eligibility rule means these results do not represent every live meal.

### Evidence

- [MetaboNet preparation and reserved roles](metabonet-phase2-preparation-2026-10-16.md)
- [Frozen Chronos history and context comparison](metabonet-phase3-inference-2026-10-16.md)
- [Direct Ridge and LightGBM training](metabonet-phase4-training-2026-10-16.md)
- [Frozen-Chronos correction and matched controls](metabonet-phase5-correction-2026-10-16.md)
- [Independent MetaboNet evaluation and calibration](metabonet-phase6-independent-2026-10-16.md)

---

## Slide 12: Backup B: additional model comparisons

**Timing:** Backup for questions. Outside the 7–8 minute talk.

### What to emphasize

- Validation numbers below use the same 1,509 meals / 48 IDs. They are development findings, not new test evidence.
- Chronos C2 six hours is the best failure-free frozen option, not the lowest conditional score among models with failed forecasts.
- Correction gain over original LightGBM is only 0.03 mg/dL / 0.10%, versus the predefined 5% incremental requirement. Its descriptive 95% delta interval [-0.48, 0.43] includes zero.
- Exact matched controls remove the Phase 4/5 training-pool difference. They do not isolate every feature/target mechanism.
- The earlier UOM→AZT1D result is separate: shared residual MAE 34.87 versus persistence 33.87 on 2,608 matched successes / 2,610 requests. It failed external improvement.
- A bounded negative correction result does not prove that all possible correction methods fail.

### Suggested speech

The development table explains why we kept the direct model. The best Chronos correction scored 31.14 versus 31.17 for LightGBM, which is too small a gain to meet the predefined incremental requirement. Longer frozen histories sometimes reduced conditional error but also produced invalid outputs. An earlier, separate UOM-to-AZT1D correction failed to improve external performance. These are reasons for a simpler candidate and cautious transfer claims, not proof that every larger-model approach must fail.

### Evidence

- [Frozen Chronos history and context comparison](metabonet-phase3-inference-2026-10-16.md)
- [Direct Ridge and LightGBM training](metabonet-phase4-training-2026-10-16.md)
- [Frozen-Chronos correction and matched controls](metabonet-phase5-correction-2026-10-16.md)
- [Initial refinement and AZT1D external evaluation](model-refinement-results-2026-10-16.md)

---

## Slide 13: Backup C: horizon errors and uncertainty

**Timing:** Backup for questions. Outside the 7–8 minute talk.

### What to emphasize

- The line chart shows error at each specified horizon, not participant-average trajectory MAE.
- LightGBM primary MAE at 30/60/120 minutes: 20.94/34.26/40.90 mg/dL. PEDAP: 32.21/47.13/52.91.
- Marginal-band point coverage: 79.05%/63.94%. Separate curve-band whole-curve coverage: 80.57%/61.11%. Both have nominal 80% targets but different coverage events.
- Mean marginal width is 96.73 mg/dL; constant curve-band width is 160.70. Both were fixed before test.
- Whole curves within ±10 are 0.94%/0.18%; largest pooled point errors are 264.87/268.63 mg/dL.
- Only 48 calibration representatives and source shift limit stability and exchangeability. Do not claim patient-specific coverage or clinical reliability.

### Suggested speech

The two-hour endpoint is harder than the average across the full forecast. Its error is about forty-one mg/dL in the primary cohort and fifty-three in PEDAP. Separate prediction bands target individual points or the entire curve, so their coverage events must not be mixed. The pediatric shortfall and broad widths expose substantial uncertainty. Rare large errors also remain, even though no forecast requests failed in independent testing.

### Evidence

- [Independent MetaboNet evaluation and calibration](metabonet-phase6-independent-2026-10-16.md)

---

## Slide 14: Backup D: delivery and evidence checklist

**Timing:** Backup for questions. Outside the 7–8 minute talk.

### What to emphasize

- The checklist distinguishes implemented, locally verified, pending live checks and proposed research/application changes.
- Recorded implementation evidence: 35 pgTAP database tests, six desktop/mobile browser checks, five frontend tests plus lint/type/build; opted-in simulator suite 11 passed.
- Latest recorded research preflight: 155 Python tests passed, one explicit opt-in simulator skip. These are dated October execution records, not tests rerun for this presentation.
- No full M2 closure, clinical validation, real-user deployment, dosing or pump control follows from this deck.
- Keep the original app on Chronos until a reviewed compatible model-serving change. Research and app data stores remain separate.
- No private credentials or row-level research identifiers belong in the presentation. Sources in notes point to aggregate reports.

### Suggested speech

The core application and research sequence have evidence, while live external nutrition and final acceptance still need completion. LightGBM serving is proposed and requires a compatibility bridge. The recorded test counts refer to their original execution dates. Milestone 3 should complete integration and analysis without treating a portion comparison as a validated treatment forecast. All outputs remain research and education only.

### Evidence

- [Milestone 2 implementation verification](milestone-2-implementation-verification.md)
- [Milestone 2 implementation and acceptance ledger](../planning/GlycoLens_10_Milestone_2_Implementation.md)
- [Independent MetaboNet evaluation and calibration](metabonet-phase6-independent-2026-10-16.md)
- [Course-aligned milestone schedule](../planning/GlycoLens_06_Milestones_and_Schedule.md)
- [Risk, safety and scope record](../planning/GlycoLens_08_Risks_Safety_and_Scope.md)

---

## Potential questions and suggested answers

These answers describe the documented evidence and proposed next steps. They are outside the timed presentation.

### 1. What is the main Milestone 2 achievement?

**Suggested answer:** A connected local simulated-patient prototype plus comparative forecasting evidence. The broader-data research study is complete. Live food/recipe verification and final acceptance remain open.

### 2. Which model should we choose?

**Suggested answer:** Retain direct LightGBM as the research candidate under the predefined participant-average MAE rule. A reviewed compatibility bridge is required before using it in the application, which still runs Chronos C3.

### 3. Why did the project train a model after starting inference first?

**Suggested answer:** The existing pretrained models did not beat the simple persistence comparison in the original experiment. The approved extension trained small comparison models. The large pretrained models were kept unchanged.

### 4. What does 18.74 percent improvement mean?

**Suggested answer:** It means that the average prediction gap fell from 36.81 to 29.91 mg/dL on the same primary test group. It is a relative reduction in average error, not an overall accuracy score or a maximum-error guarantee.

### 5. What is persistence?

**Suggested answer:** A simple forecast that repeats the latest glucose reading for all 24 future time points. It makes a useful test of whether a more complex model adds value.

### 6. Why not show Chronos versus LightGBM on the final test?

**Suggested answer:** Chronos was compared on matched MetaboNet validation data before final selection. Phase 6 independently evaluated frozen LightGBM, Ridge and persistence only. Adding a new Chronos test comparison now would be a separate analysis, not an already completed result.

### 7. Why not choose Ridge, which has a higher within-10 rate?

**Suggested answer:** The predefined primary selection criterion was participant-average trajectory MAE. Ridge had slightly higher within-10 rates but higher MAE on both independent cohorts. The tradeoff is reported rather than changing the selection rule after testing.

### 8. Did the model achieve ±10 mg/dL?

**Suggested answer:** No. LightGBM within-10 rates were 28.20% primary and 19.57% PEDAP under equal participant weighting. Whole-curve rates were 0.94% and 0.18%. ±10 is an aspiration, not a demonstrated maximum or a firm acceptance requirement.

### 9. Does 80 percent coverage mean 80 percent accuracy?

**Suggested answer:** No. Coverage asks whether the actual reading falls somewhere inside a predicted range. Within-10 asks whether the central prediction is within ten of the actual reading. A broad range can cover often while its central prediction is still far away.

### 10. What happens at the two-hour endpoint?

**Suggested answer:** LightGBM endpoint MAE is 40.90 mg/dL primary and 52.91 PEDAP. The headline 29.91 and 40.92 average all 24 future time points, not just the endpoint.

### 11. Why is pediatric performance worse?

**Suggested answer:** The study shows weaker transfer to PEDAP, including uncertainty undercoverage. Differences in cohorts, recording and physiology are possible contributors, but this experiment does not isolate their causes.

### 12. Did full nutrition improve the selected model?

**Suggested answer:** The original T1D-UOM study tested available full nutrition, but did not establish a reliable advantage over persistence. The selected MetaboNet model uses recorded carbohydrates and insulin, not validated protein/fat/fibre effects.

### 13. Can we reliably predict a different portion?

**Suggested answer:** Not from these results. Portion changes are counterfactuals, and the evaluated logged-meal models have not established causal nutrient effects. Any exploratory UI must retain that limitation.

### 14. What did the Chronos correction add?

**Suggested answer:** The best eligible correction improved reused-validation MAE by only 0.03 mg/dL over direct LightGBM. It missed the predefined 5% incremental improvement requirement; the descriptive difference interval includes no benefit.

### 15. How did you prevent data leakage?

**Suggested answer:** Later glucose remains a separate target. Participant roles are separated for MetaboNet; fitting and transformations use training data only. Point-model selection froze before calibration and reserved outcomes. Retrospective meal exclusions and logging assumptions remain explicit limitations.

### 16. Why do meal counts change between phases?

**Suggested answer:** History completeness and matching requirements change eligibility. Six-hour preparation counts, the four-history CV intersection, 24-hour final refits and final test eligibility have different denominators. The deck labels the relevant population instead of summing them.

### 17. Are held-out participant IDs guaranteed to be unique people globally?

**Suggested answer:** No. Source-qualified roles and partial exact-trajectory checks reduce known overlap, but cannot prove global uniqueness across all public datasets or absence from foundation pretraining.

### 18. Why not keep tuning on these test sets?

**Suggested answer:** The primary, PEDAP and earlier AZT1D outcomes have now been examined. Further tuning must use development data and fresh held-out confirmation, rather than reusing these cohorts as untouched evidence.

### 19. What is needed to put LightGBM in the application?

**Suggested answer:** Match its 24-hour glucose history, six-hour event summaries, insulin amount units, masks and timing; handle insufficient history; verify saved-model/API equivalence. The fixed one-day simulator needs a reviewed warm-up or another suitable path.

### 20. What remains before full Milestone 2 closure?

**Suggested answer:** Privately configure the live food and recipe providers, verify their actual results and source information, complete the browser acceptance checks for those paths, and finish the requirement-to-evidence review.

### 21. Is the screenshot evidence of forecast accuracy?

**Suggested answer:** No. It is a recorded interface demonstration with a virtual patient, synthetic nutrition and a real Chronos prediction. Accuracy evidence comes from the separate aggregate research cohorts.

### 22. Does the simulator prove realistic physiology?

**Suggested answer:** No. It supports a bounded reproducible software demonstration. Repeated execution and interface checks do not establish physiological realism or treatment safety.

### 23. What advice can the system give?

**Suggested answer:** It displays uncertain research forecasts and historical evidence. It does not recommend insulin doses, change clinician settings, control a pump or establish clinical validity.

### 24. What feedback would be most useful?

**Suggested answer:** Confirm whether model integration and milestone closure should precede another improvement round, and suggest focused features, cohorts or evaluation criteria for the next development-only study.

## Short answers to keep ready

**Main achievement:** Connected local prototype and a completed six-phase broader-data research study.

**Research candidate:** Direct LightGBM under the rule that prioritizes average error.

**Current application model:** Chronos-2 C3. LightGBM is not yet integrated.

**Primary result:** Average error 29.91 versus persistence 36.81 mg/dL, an 18.74% reduction.

**Precision limitation:** Within ±10 is 28.20% primary and 19.57% pediatric.

**Milestone status:** Research study complete. Live food/recipe verification and final acceptance remain pending.

**Help needed:** Advisor priorities for integration versus another improvement experiment.

## Final rehearsal checklist

- Rehearse Slides 1–10 to 7:30, within the requested 7–8 minutes. Backups and answers are outside that time.
- Keep the project and M1 reminders brief. Use technical definitions only where they help interpret the work or results.
- At each chart, state the comparison and result, then its implication. Allow a short viewing pause.
- Use each cohort’s own baseline. Keep original T1D-UOM and later MetaboNet results separate.
- Distinguish trajectory-average error from the two-hour endpoint, and within-10 precision from band coverage.
- Do not describe error reductions or coverage as an overall percentage accuracy score.
- Identify the screenshot as the recorded virtual-patient flow with example nutrition and actual Chronos inference.
- Keep the current Chronos app separate from the proposed LightGBM integration.
- Retain pending live food/recipe verification and final acceptance. Do not claim full M2 closure.
- Retain the research/education and no-dosing boundaries. More tuning requires fresh confirmation.
- Finish with the request for advisor priorities and invite questions.

## Evidence references

Links point to aggregate source reports. PowerPoint notes include URLs pinned to the published implementation checkpoint. This wording revision adds no experiments, application verification or clinical evidence.

- [Milestone 2 implementation verification](milestone-2-implementation-verification.md)
- [Milestone 2 implementation and acceptance ledger](../planning/GlycoLens_10_Milestone_2_Implementation.md)
- [Original pretrained-model comparison](milestone-2-model-results.md)
- [Initial refinement and AZT1D external evaluation](model-refinement-results-2026-10-16.md)
- [MetaboNet preparation and reserved roles](metabonet-phase2-preparation-2026-10-16.md)
- [Frozen Chronos history and context comparison](metabonet-phase3-inference-2026-10-16.md)
- [Direct Ridge and LightGBM training](metabonet-phase4-training-2026-10-16.md)
- [Frozen-Chronos correction and matched controls](metabonet-phase5-correction-2026-10-16.md)
- [Independent MetaboNet evaluation and calibration](metabonet-phase6-independent-2026-10-16.md)
- [Milestone 1 closure audit](milestone-1-closure-audit.md)
- [Course-aligned milestone schedule](../planning/GlycoLens_06_Milestones_and_Schedule.md)
- [Risk, safety and scope record](../planning/GlycoLens_08_Risks_Safety_and_Scope.md)
- [Project specification](../planning/GlycoLens_09_Project_Specification_Draft.md)
- [Consolidated October 26 advisor report](GlycoLens_Milestone_2_Advisor_Report_2026-10-26.md)
- [Milestone 1 notes style reference](GlycoLens_Milestone_1_Presentation_Notes_v2.md)
