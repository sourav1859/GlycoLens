# GlycoLens Milestone 1 Presentation Notes

**Presenter:** Sourav Patil  
**Advisor:** Professor Haibo Yang  
**Course:** CSCI-788  
**Presentation date:** October 5, 2026  
**Target presentation length:** 5 to 6 minutes plus questions  
**Estimated speech length:** 702 words in Suggested speech; 765 including transitions. Target 5 minutes 30 seconds at about 140 words per minute, allowing brief pauses within the 5–6 minute slot.  

## Presentation strategy

This is a Milestone 1 progress presentation. The audience has already received the project-specification introduction and explanation of why the problem matters. Give a brief reminder, then explain what was learned, what was implemented, what the measurements support, and what remains unresolved.

The main message is that the individual building blocks work: the data can be prepared, a forecasting model can run, and the early application and simulation can be demonstrated. The next milestone must test how accurate the predictions are and connect these pieces into one working experience.

Read Suggested speech and the short transitions for the timed presentation. The speech uses everyday language for an audience with minimal technical background. Keep What to emphasize and the question sections for preparation; they contain technical detail that does not need to be read aloud. Spend the most time on Slides 4 through 6, pointing to the evidence rather than reading every number. Allow short pauses and target 5 minutes 30 seconds in rehearsal.

## Suggested timing

| Slide | Topic | Target time | Cumulative time |
|---|---|---:|---|
| 1 | GlycoLens Milestone 1 | 15 sec | 0:00–0:15 |
| 2 | Project reminder and Milestone 1 objectives | 25 sec | 0:15–0:40 |
| 3 | Methods learned and feasibility paths | 35 sec | 0:40–1:15 |
| 4 | Dataset and model feasibility | 60 sec | 1:15–2:15 |
| 5 | Meal window eligibility | 50 sec | 2:15–3:05 |
| 6 | Application and simulation evidence | 55 sec | 3:05–4:00 |
| 7 | Challenges and personal assessment | 45 sec | 4:00–4:45 |
| 8 | Milestone 2 plan and advisor input | 45 sec | 4:45–5:30 |
| **Total** | **Spoken presentation** | **330 sec** | **5 minutes 30 seconds** |

---

# Slide-by-slide speaker notes and speech

## Slide 1: GlycoLens Milestone 1

**Target time:** 15 seconds (0:00–0:15)

### What to emphasize

- Open with the milestone update, not another explanation of T1D or CGM. Those introductory topics were covered in the project specification.
- State that this presentation reports completed feasibility work and remaining limitations. Keep the introduction near fifteen seconds.

### Suggested speech

Good afternoon. This is my Milestone 1 update for GlycoLens. I have tested whether its main building blocks work. Today, I will share the results, lessons, and next steps.

### Transition

First, a brief reminder of the goal.

---

## Slide 2: Project reminder and Milestone 1 objectives

**Target time:** 25 seconds (0:15–0:40)

### What to emphasize

- Use only one sentence to remind the audience of the project goal. Do not repeat the full meal workflow or the four original user questions.
- Explain that Milestone 1 concerns understanding, planning, and technical feasibility. A working component is evidence of feasibility, not a completed capstone feature.
- Distinguish the completed feasibility objectives from the still-pending accuracy evaluation and real meal-to-model application flow.

### Suggested speech

GlycoLens aims to help a person understand how their blood sugar might change during the two hours after a meal. This milestone asked: do we have usable data, can a prediction model run, and can the application display the result? I have working building blocks for each. Testing prediction accuracy and joining everything together come next.

### Transition

Here is how I approached those checks.

---

## Slide 3: Methods learned and feasibility paths

**Target time:** 35 seconds (0:40–1:15)

### What to emphasize

- Explain a model adapter as a shared input/output interface. It allows model comparisons without rewriting the surrounding pipeline.
- The persistence baseline repeats the last observed glucose value. Its implementation exists, but an accuracy comparison with Chronos-2 has not yet run.
- Future glucose is stored separately as the target. A model request includes only information available at forecast time.
- Separate the real-data research command from the synthetic API/browser demonstration. Do not describe them as one integrated real-model application.
- Summarize the literature as motivation for context comparisons. Do not repeat the specification literature survey or claim richer context has already helped.

### Suggested speech

I tested the project in smaller pieces. One runs Chronos-2, an existing prediction model, on real readings from a continuous glucose monitor. Another displays a forecast in the browser using sample data. I also prepared a simple comparison: assume blood sugar stays at its latest reading. Later, I will check whether the model predicts better. The model only receives information available before the prediction; later readings are kept separate for checking its answer.

### Transition

The first results concern the data and prediction model.

---

## Slide 4: Dataset and model feasibility

**Target time:** 60 seconds (1:15–2:15)

### What to emphasize

- Define the four core streams: CGM, nutrition, bolus insulin, and basal insulin. The 17/15/13 bars are nested coverage groups and must not be added together.
- Explain 24 historical and 24 future five-minute readings as the two-hour context and target grids. The historical grid ends at the forecast boundary.
- A smoke test checks whether the model loads, runs, and produces a valid output shape. One window cannot establish accuracy across people or meals.
- q10, q50, and q90 are the model’s 10th, 50th, and 90th percentile forecasts. q50 is the median. The interval needs a separate calibration study before its coverage can be trusted.
- Median latency summarizes the middle warm call. p95 summarizes the upper tail of these ten warm calls; it is a small-sample estimate, not a production service guarantee.
- RSS measures the memory of the Python process, including the model and supporting libraries. It is not the checkpoint size or GPU memory. These CPU timings exclude the browser request path.

### Suggested speech

I checked sixty-two files containing more than 386,000 records of blood sugar, food, and insulin. The chart shows seventeen participants with glucose readings, fifteen with food and some insulin records, and thirteen with all four types of records. These groups overlap, so we should not add the bars together. For each usable meal, I prepare two hours of earlier readings and keep the next two hours for checking the prediction. Chronos-2 produced a forecast for one real example, including a middle estimate and a range of possible values. Once loaded, its typical prediction time was about fifty-four milliseconds, well under one second. This shows the model can run locally. It does not yet tell us how accurate its predictions are or how reliable that range is.

### Transition

Next, which meals had enough information for testing?

---

## Slide 5: Meal window eligibility

**Target time:** 50 seconds (2:15–3:05)

### What to emphasize

- Distinguish 4,351 audited nutrition rows from 3,884 valid loaded meal events. Same-time components and loading rules affect the meal count.
- Use the chart to explain why data preparation was substantial work. The eligible count is 927/3,884, not 927 participants.
- The initial policy requires two hours of history and target, a five-minute grid, at least one insulin event in the previous six hours, no second meal within the target horizon, and limited interpolation across CGM gaps.
- The four rejection categories record the first failure. A meal might fail several rules but is counted only once.
- Do not conclude that incomplete history affects only 32.98 percent of all source meals. The chart describes this evaluated event set and this rule order.
- Filtering sensitivity and participant-level reporting remain necessary. More windows do not automatically mean more independent or representative evidence.

### Suggested speech

Of 3,884 meals checked, 927 had enough information under the initial rules. That is about twenty-four percent, or roughly one in four meals. The largest problem was missing earlier glucose readings. Other meals had another meal too soon afterward, insufficient earlier insulin information, or missing later readings needed to check the prediction. Each excluded meal appears under the first rule it failed, so it is counted only once. This was an important lesson: having many records does not mean every meal is usable. Next, I will examine whether these rules are too restrictive and whether some participants contribute much more usable data than others.

### Transition

I also checked the application and a simulated day.

---

## Slide 6: Application and simulation evidence

**Target time:** 55 seconds (3:05–4:00)

### What to emphasize

- The browser data are synthetic. The real Chronos-2 model runs in a separate research command.
- Describe the uncertainty band as model quantiles, not a clinically validated confidence guarantee.
- The database is local Supabase/PostgreSQL, not a deployed hosted service. Ownership tests support the local schema and policy behavior, not a claim of complete production security.
- The simulation graph includes all 288 five-minute points, displayed to two decimals, from one ExtHovorka/OpenLoop virtual day.
- Byte-identical runs show reproducibility for this pinned scenario. They do not establish physiological accuracy, treatment safety, or model prediction accuracy.
- Keep the application, database, and simulator evidence distinct. Simulator-to-app integration is still pending.

### Suggested speech

The early application can display earlier readings, a predicted blood sugar line, a range of possible values, and summaries for the next thirty, sixty, and 120 minutes. Five checks of the display passed. I also tested how information is stored locally, with twenty database checks passing. The browser currently uses made-up example data; it is not yet connected to the real prediction model. On the right is a simulated day, with 288 readings taken five minutes apart. Running the same scenario twice gave exactly the same result. That tells us the simulation runs consistently. It does not prove that it accurately represents a person's body. These pieces now work separately, and connecting them remains part of the next milestone.

### Transition

The work also revealed some important challenges.

---

## Slide 7: Challenges and personal assessment

**Target time:** 45 seconds (4:00–4:45)

### What to emphasize

- Explain why an incorrect date order can parse successfully while assigning the wrong day and month. This is more consequential than a parser simply rejecting a row.
- The 253 figure counts conflicting CGM timestamp groups, not participants or all duplicate rows. Conflicting values were excluded.
- Present assessment in first person: what you learned, what is ready, and what remains risky. Avoid claiming that all final product requirements are complete.
- Current Chronos-2 covariate rejection is a real implementation boundary. The upstream model’s capabilities do not mean the local adapter already supports insulin and nutrition.
- Describe the schedule pressure specifically: evaluation, richer-context support, and real-model integration are competing tasks.

### Suggested speech

One challenge was reading dates correctly. Mixing up the day and month could place a meal beside the wrong glucose readings without an obvious error. I also excluded 253 groups of readings with conflicting values at the same recorded time. My main lesson is that trustworthy predictions begin with trustworthy data. The building blocks work, but the biggest tasks remain: checking prediction quality and connecting the application. The current model setup uses only glucose readings. Adding insulin and food information will require further work and testing, so I need to prioritize carefully.

### Transition

That leads to my Milestone 2 plan.

---

## Slide 8: Milestone 2 plan and advisor input

**Target time:** 45 seconds (4:45–5:30)

### What to emphasize

- Use dates from the recorded course plan. The schedule is provisional and the instructor may change it.
- The primary evaluation plan is chronological within each participant. A separate subject-disjoint analysis holds out entire participants. These answer different questions.
- Preserve the carbohydrate-only stage: CGM, insulin, carbohydrates, then fuller nutrition. This tests the incremental value of protein, fat, and fiber.
- TimesFM was non-blocking for M1 feasibility, but the broader plan includes a second pretrained-model comparison. Any reduction needs an explicit scope decision.
- Ask for concrete advisor input on metrics and priorities. Close with the research-only boundary when questioned, rather than adding another lengthy safety recap to the speech.

### Suggested speech

The recorded Milestone 2 work deadline is October sixteenth, with presentations on October twenty-seventh and November third, subject to course updates. First, I will test predictions on later data that the model has not been given, and separately check performance on people left out of the development data. I will compare the model with the simple unchanged-blood-sugar prediction. Then I will investigate whether insulin and food information improve the results, and connect meal entry to real predictions in the browser. Given the limited time, I would like advisor guidance on priorities and whether to revise the planned comparison with a second prediction model.

### Transition

Thank you, and I am happy to take questions.

---

# Potential questions and suggested answers

These answers describe the Milestone 1 implementation and the planned next work. They are outside the timed presentation.

## 1. How accurate is the forecast?

**Suggested answer:**  
Accuracy has not been measured across the evaluation cohort. One real CGM-only window verified output shape, finite values, quantile ordering, and runtime. MAE, RMSE, horizon errors, and calibration belong to the planned benchmark.

## 2. Why did only 927 meals qualify?

**Suggested answer:**  
The initial policy requires two hours of history and future glucose, sufficient insulin context, acceptable CGM gaps, and no second meal in the forecast horizon. Of 3,884 valid loaded meals, 927 qualified. Rejection counts are sequential first-failure categories.

## 3. Are the application forecasts real model predictions?

**Suggested answer:**  
The browser currently receives synthetic data through FastAPI. A separate research command runs the real Chronos-2 model on T1D-UOM. Real model execution is not yet in the browser request path.

## 4. Do insulin and nutrition already influence Chronos 2?

**Suggested answer:**  
No. The common contract and converters represent context, but the current Chronos-2 adapter accepts CGM-only requests and explicitly rejects covariates. Model-specific context support remains implementation work.

## 5. Why use pretrained models?

**Suggested answer:**  
The project focuses on inference context and application integration. The rich primary cohort has seventeen participants, so training a large model from scratch would add considerable effort and generalization risk.

## 6. Why compare carbohydrates and full nutrition separately?

**Suggested answer:**  
This isolates whether protein, fat, and fiber add value beyond carbohydrate information. The planned sequence is CGM only, insulin, carbohydrates, then fuller nutrition. Missing source features will not be invented.

## 7. Is TimesFM optional?

**Suggested answer:**  
Its Milestone 1 smoke test was conditional on feasibility and time. The broader project plan includes a second pretrained-model comparison. Any reduction of that requirement needs an explicit scope decision with the advisor.

## 8. What does the simulation prove?

**Suggested answer:**  
One pinned ExtHovorka/OpenLoop virtual day produced 288 five-minute samples and identical results across two executions. This supports deterministic software execution, not physiological realism or clinical validity.

## 9. What do the runtime figures measure?

**Suggested answer:**  
The September 29 closure run measured 22.61 seconds for loading, 117.20 milliseconds for the first adapter call, warm p50 of 53.94 milliseconds and p95 of 80.05 milliseconds over ten calls, and 810.91 MiB observed peak process RSS. These are local CPU observations on one window, not end-to-end web latency.

## 10. How will leakage be controlled?

**Suggested answer:**  
Future CGM remains in a separate target object. Only information available by forecast time may enter requests or retrieval. The primary plan uses chronological splits within each participant and a separate subject-disjoint analysis. Final split definitions remain to be frozen.

## 11. Can the application recommend an insulin dose?

**Suggested answer:**  
No. Insulin dosing, pump control, diagnosis, and clinical-grade treatment claims are outside the approved capstone scope.

## 12. What help is needed from the advisor?

**Suggested answer:**  
Confirm primary evaluation metrics and calibration requirements, prioritize the end-to-end workflow versus model comparison under the October 16 deadline, and decide explicitly whether the planned second-model requirement should change.

## 13. What changed since the project specification?

**Suggested answer:**  
The specification described the intended system and evaluation. Milestone 1 now provides an audited event pipeline, a real Chronos-2 CGM-only execution, a common adapter and persistence baseline, a synthetic browser/API path, a local database migration, and a reproducible offline simulation. The full integrated application and comparative accuracy results remain pending.

## 14. What is a meal window?

**Suggested answer:**  
It is a meal-centered experimental example with a pre-meal glucose history, context available at forecast time, and a separate future glucose target. The initial policy uses 24 historical and 24 future readings on a five-minute grid.

## 15. Why are there fewer loaded meals than nutrition rows?

**Suggested answer:**  
Nutrition rows and meal events are different units. The audit counts 4,351 nutrition rows. Loading excludes unsuitable records and combines nutrition components at the same timestamp, leaving 3,884 valid loaded meal events for the eligibility scan.

## 16. Can the participant coverage bars be added together?

**Suggested answer:**  
No. The groups overlap: 17 participants have CGM, 15 also have nutrition and an insulin modality, and 13 contain all four core streams. Adding the bars would count some participants multiple times.

## 17. What do q10 q50 and q90 mean?

**Suggested answer:**  
They are percentile forecasts from the model. q50 is the median, while q10 and q90 form an interval containing the central 80 percent of the model distribution. Whether that interval actually covers observed glucose at the intended rate must be evaluated; ordered quantiles alone do not establish calibration.

## 18. What do median latency and p95 tell us?

**Suggested answer:**  
The median is the middle warm-call latency. p95 describes the upper tail under the recorded percentile method. Here only ten warm calls on one selected window were measured, so the figures are local feasibility observations, not a service-level guarantee.

## 19. Is 810 point 91 MiB the model size?

**Suggested answer:**  
No. It is observed peak process RSS, which includes the Python process, loaded model, libraries, and supporting allocations. The checkpoint cache size, process memory, and any GPU memory are different measures.

## 20. Have the final evaluation splits been implemented?

**Suggested answer:**  
The chronological and subject-disjoint policies are documented, but the final split manifests and participant-level benchmark remain Milestone 2 work. A planning calculation is not a completed held-out evaluation.

## 21. Does the local database prove the system is production ready?

**Suggested answer:**  
No. A clean reset, schema lint, and 20 local database tests support the migration, constraints, and ownership policies. They do not establish complete production security, deployment readiness, or real-user usability.

## 22. What if Chronos 2 does not outperform persistence?

**Suggested answer:**  
That is still a meaningful result. The capstone should report paired evidence on matched events and analyze the error, calibration, and runtime tradeoffs. The scientific outcome does not depend on a pretrained model winning.

---

# Short answers to keep ready

**What is GlycoLens in one sentence?**  
A research prototype that aims to combine meal information and recent glucose context into an understandable two-hour forecast with uncertainty.

**What did Milestone 1 establish?**  
Technical feasibility of the data pipeline, real-model execution, synthetic application boundary, local database, and offline simulator.

**What is the strongest quantitative data result?**  
927 eligible meal windows from 3,884 valid loaded meals under the initial strict policy, a 23.87 percent yield.

**What is the model result?**  
One real CGM-only Chronos-2 window produced 24 valid q10/q50/q90 points. Accuracy and calibration remain unmeasured.

**Is the browser running Chronos 2?**  
No. The browser currently displays a typed synthetic forecast; real-model application integration is pending.

**What is the immediate next step?**  
Freeze the evaluation cohorts, benchmark against persistence, and connect the real inference path to the meal workflow.

**What help is needed?**  
Advisor confirmation of metrics and priorities, including an explicit decision if the planned second-model comparison changes.

**What is outside scope?**  
Insulin-dose advice, pump control, diagnosis, and clinical-grade treatment claims.

---

# Final rehearsal checklist

Before presenting:

- Practice with a timer and target 5 minutes 30 seconds. Keep the opening and recap to about forty seconds combined.
- Do not repeat the introductory T1D explanation, the original multi-signal diagram, or the full proposed product workflow.
- Spend the most time on slides 4 through 6. Point to the chart or table, explain what the numbers mean, then state the limitation.
- Keep What to emphasize and the question sections for preparation. Read Suggested speech and the short transitions; explain technical labels only if asked.
- Say completed or verified for actual M1 evidence. Say planned or pending for accuracy benchmarks, richer covariates, personalization, and real-model browser integration.
- Keep 927 meal windows distinct from 17 participants. Do not add the overlapping 17/15/13 coverage groups.
- Identify runtime measurements as local CPU observations on one window and ten warm calls. Do not call them end-to-end application latency.
- Identify the browser demonstration and simulator graph as synthetic. Reproducibility does not establish physiology or clinical usefulness.
- Use the first-failure qualification when explaining rejection categories. Do not present them as independent missingness rates.
- Answer questions directly before adding detail. Keep the no-dosing and research-only boundary clear.
- Confirm the actual presentation slot and any instructor schedule updates before presenting.
- Close with Thank you and I am happy to take questions.

---

# Evidence references

Local paths below are relative to the GlycoLens repository. Runtime values use the final September 29 closure run. Course dates follow the recorded plan and remain subject to instructor changes.

- **Data audit and meal-window counts**: `docs/reports/milestone-1-data-pipeline-implementation.md`
- **Final runtime and validation record**: `docs/reports/milestone-1-closure-audit.md`
- **Raw aggregate CPU measurement record**: `artifacts/benchmarks/chronos2-m1-smoke.json`
- **Common forecast contract and persistence**: `docs/reports/milestone-1-phase-2-forecast-contract.md`
- **Synthetic API and browser boundary**: `docs/reports/milestone-1-phase-4-api-visualization.md`
- **Local database evidence**: `docs/reports/milestone-1-phase-5-local-database.md`
- **Offline simulator evidence**: `docs/reports/milestone-1-phase-6-pymgipsim-scenario.md`
- **Model candidates and supported context**: `docs/planning/GlycoLens_02_Model_Inference_and_Dataset_Strategy.md`
- **Evaluation and split policies**: `docs/planning/GlycoLens_05_Scientific_Method_and_Evaluation.md`
- **Course milestone schedule**: `docs/planning/GlycoLens_06_Milestones_and_Schedule.md`
- **Literature synthesis**: `docs/planning/GlycoLens_07_Literature_and_Market_Survey.md`
