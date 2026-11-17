# GlycoLens Milestone 3 Presentation Notes

**Presenter:** Sourav Patil  
**Advisor:** Professor Haibo Yang  
**Course:** CSCI-788  
**Presentation date:** November 17, 2026  
**Prepared:** November 16, 2026  
**Speech:** 851 words across ten main slides. Target 7:30, within 7–8 minutes plus questions.  
**Pace:** approximately 120 words per minute plus about 25 seconds of visual pauses. Rehearsal determines the final timing.  
**Deck:** [Milestone 3 PowerPoint](../presentations/GlycoLens_Milestone_3_Presentation_2026-11-17.pptx)

## Presentation strategy

Give a short project and M2 reminder, then focus on implementation and new analysis. Read Suggested speech for the timed talk. Presenter emphasis, backup material, definitions, sources and prepared answers are rehearsal support rather than additional timed speech.

The earlier independent accuracy study was already presented at M2. Current work integrates the frozen LightGBM candidate and tests application behavior. Interface screenshots use recorded synthetic accounts. Matching-meal outcome accuracy remains unestablished.

## Suggested timing

| Slide | Topic | Target | Cumulative |
|---|---|---:|---|
| 1 | GlycoLens Milestone 3 | 15 sec | 0:00–0:15 |
| 2 | The problem | 30 sec | 0:15–0:45 |
| 3 | The implemented GlycoLens workflow | 40 sec | 0:45–1:25 |
| 4 | What Milestone 2 established | 30 sec | 1:25–1:55 |
| 5 | Personal logging and research simulation | 55 sec | 1:55–2:50 |
| 6 | Food and recipe services are connected | 55 sec | 2:50–3:45 |
| 7 | LightGBM is an optional research model | 60 sec | 3:45–4:45 |
| 8 | Meal changes exposed a forecasting limitation | 70 sec | 4:45–5:55 |
| 9 | Testing improved the implementation | 55 sec | 5:55–6:50 |
| 10 | Remaining core work and advisor input | 40 sec | 6:50–7:30 |
| **Total** | **Ten main slides** | **450 sec** | **7:30** |

## Slide 1 GlycoLens Milestone 3

**Target:** 15 seconds.

### Presenter emphasis

- Introduce implementation progress and the new meal-response analysis. Keep the opening brief.

### Suggested speech

Good afternoon. This is my Milestone 3 update for GlycoLens. Since the previous presentation, I have connected more of the application and tested what its meal forecasts actually respond to.

### Transition

First, a quick reminder of the problem.

### Evidence

- [Project specification](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/planning/GlycoLens_09_Project_Specification_Draft.md)

## Slide 2 The problem

**Target:** 30 seconds.

### Presenter emphasis

- Expand CGM once. Describe the user problem without repeating the full project specification.

### Suggested speech

GlycoLens addresses a familiar problem in Type 1 Diabetes: food information and glucose readings are usually viewed separately. A continuous glucose monitor, or CGM, shows glucose over time, but understanding a particular meal still takes work. The project brings reviewed nutrition, earlier glucose information and an understandable two-hour forecast into one application.

### Transition

Here is how the application addresses it.

### Evidence

- [Project specification](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/planning/GlycoLens_09_Project_Specification_Draft.md)

## Slide 3 The implemented GlycoLens workflow

**Target:** 40 seconds.

### Presenter emphasis

- Personal meal logging and simulated forecasting are distinct workflows.
- No insulin-dose recommendation or treatment claim.

### Suggested speech

The workflow starts with food search, a barcode or recipe text. The user reviews the ingredients and quantities before saving a meal. In the research workspace, the application combines that meal with simulated glucose and recorded insulin information, runs a selected model, and saves the forecast. The user can inspect prediction ranges, compare portions and later view available observations. Personal meal logging works separately, without requiring a simulated patient. Forecasts remain research estimates and must not guide insulin dosing.

### Transition

Milestone 2 provided the starting point.

### Evidence

- [Application implementation checkpoint](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/webapp-implementation-checkpoint-2026-11-11.md)
- [Personal and simulation workspace validation](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/workspace-separation-validation-2026-11-14.md)

## Slide 4 What Milestone 2 established

**Target:** 30 seconds.

### Presenter emphasis

- Describe M2's completed prototype and experiments, then move to the later integration work.
- The independent LightGBM accuracy study was already presented in M2.

### Suggested speech

At Milestone 2, I had demonstrated the connected Chronos prototype and completed the model comparison study. LightGBM had improved average error in the separate research evaluation, but it was not available in the application. Live food and recipe services also needed verification. My focus since then has been to close those integration gaps and test the resulting behavior.

### Transition

Here is what I implemented since then.

### Evidence

- [November 3 Milestone 2 presentation](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/presentations/GlycoLens_Milestone_2_Presentation_2026-11-03_v4.pptx)
- [Earlier independent model evaluation](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/metabonet-phase6-independent-2026-10-16.md)

## Slide 5 Personal logging and research simulation

**Target:** 55 seconds.

### Presenter emphasis

- Point to the real current-date personal view and the separate virtual clock.
- Screenshots are recorded synthetic-account interface evidence, not patient outcomes.
- Only confirmed eaten meals contribute to consumed totals.

### Suggested speech

The application now has a consistent interface for Home, meal history, nutrition summaries and simulation forecasts. Users can sign in, complete a short setup, review meals and edit or cancel them. Only meals marked as eaten contribute to the nutrition totals.

A practical correction was separating everyday records from the virtual patient. Personal pages use the current date in the user's timezone. Simulation keeps its own clock and history. Moving between them does not turn synthetic meals into personal consumption.

These screens show recorded tests with synthetic accounts. Personal glucose forecasting is still unavailable because a real glucose connector is not enabled.

### Transition

Next, the food and recipe connections.

### Evidence

- [Responsive UI reference review](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/figma-reference-review-2026-11-10.md)
- [Personal and simulation workspace validation](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/workspace-separation-validation-2026-11-14.md)

## Slide 6 Food and recipe services are connected

**Target:** 55 seconds.

### Presenter emphasis

- Define API as the connection to another service.
- The LLM extracts editable ingredients. Reviewed food records supply nutrient facts.
- The eight-case result follows a documented scoring-rule correction and is not general recipe accuracy.

### Suggested speech

I integrated and exercised the USDA food service and the language-model recipe service. An API is the connection that lets the application request information from another service.

USDA provides food matches and nutrient facts. The language model extracts ingredient names, quantities and servings from recipe text. It does not supply authoritative calorie or nutrient values. Those values come from reviewed food records and are calculated for the selected amounts. Barcode lookup uses Open Food Facts.

All paths require user review. Eight synthetic recipe cases passed for the selected extractor after a documented scoring correction. That verifies a small sample, while broader recipe accuracy still needs evaluation.

### Transition

I also added another forecasting option.

### Evidence

- [Live recipe extraction validation](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/recipe-model-validation-2026-11-11.md)
- [Provider and forecasting integration evidence](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/m2-closure-validation-2026-11-12.md)

## Slide 7 LightGBM is an optional research model

**Target:** 60 seconds.

### Presenter emphasis

- Chronos remains default. LightGBM is explicitly selected and requires eligible history.
- Explain the 24-hour input requirement and separate 48-hour scenario.
- Current meal carbohydrates are a native-model predictor; current protein/fat/fiber are not.

### Suggested speech

LightGBM is now an optional research model in the application, while Chronos remains the default. Integrating it required more than changing the model name.

Chronos uses two hours of glucose history here, while the selected LightGBM needs twenty-four. I added a separate forty-eight-hour virtual scenario to provide enough earlier readings, and matched the timing and units of past meal and insulin records.

Saved forecasts retain the model, meal revision and prediction bands used at that moment. Both models produced twenty-four stored forecast points in recorded application tests. LightGBM uses the current meal's carbohydrates. Protein, fat and fibre remain visible nutrition information, but are not direct predictors for this frozen model.

### Transition

I then tested their response to meals.

### Evidence

- [Frozen LightGBM application integration](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/lightgbm-app-validation-2026-11-12.md)
- [Local research-model selection evidence](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/local-lightgbm-enablement-2026-11-14.md)

## Slide 8 Meal changes exposed a forecasting limitation

**Target:** 70 seconds.

### Presenter emphasis

- Pause after the 60-of-60 Chronos finding.
- 236 predictions include controlled contrasts, controls/repeats and warm runs; they are not 236 independent accuracy examples.
- Changed predictions are sensitivity evidence, not matching-meal accuracy.

### Suggested speech

The most important new analysis asked whether changing a meal changes the forecast when the earlier glucose and insulin information stays fixed. I tested different meal profiles and portions, including repeated identical requests.

All 236 predictions completed. However, Chronos was effectively unchanged across all sixty eligible meal contrasts. That means the application can pass meal information correctly without the model showing a useful meal response in these tests.

LightGBM changed across most carbohydrate contrasts, although some responses were flat or uneven. A changed prediction alone does not show that the change is accurate.

The simulator also follows its preset meals, so its later readings cannot validate any arbitrary meal entered by a user. I therefore report working comparison features separately from unproven meal-response accuracy.

### Transition

These findings also shaped the testing.

### Evidence

- [Controlled meal and portion sensitivity results](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/meal-response-sensitivity-2026-11-12.md)

## Slide 9 Testing improved the implementation

**Target:** 55 seconds.

### Presenter emphasis

- The November 16 210/36 counts are scoped offline checks, not full phase acceptance.
- Name both corrected bugs and the user consequences.
- Give the personal assessment in the final sentence.

### Suggested speech

I checked the implementation at several levels. The latest selected offline checks passed 210 Python tests and 36 frontend tests. One simulator test remained explicitly skipped, and these counts do not mean every acceptance case has passed.

Recorded integration checks also exercised real sign-in, saved meals, both forecasting paths and access restrictions between accounts.

Testing exposed practical mistakes: changing recipe ingredients could leave an old confirmation active, and a delayed simulation response could restore the wrong screen context after exit. Those issues were fixed and checked.

My main lesson is to test what users would reasonably believe the result means, alongside whether the software runs.

### Transition

That brings me to the remaining priorities.

### Evidence

- [Provider and forecasting integration evidence](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/m2-closure-validation-2026-11-12.md)
- [Personal and simulation workspace validation](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/workspace-separation-validation-2026-11-14.md)

## Slide 10 Remaining core work and advisor input

**Target:** 40 seconds.

### Presenter emphasis

- Kaggle source: thedevastator / better-recipes-for-a-better-life, page title Recipes Dataset.
- Ingestion is ongoing author-reported work. No stage, validated count or completed import is asserted.
- Invite guidance about remaining core implementation versus further prediction analysis.

### Suggested speech

My remaining capstone priorities are to finish the browser and usability checks, strengthen the earlier-meal evidence view, and establish an appropriate test with matching meals and later glucose observations.

I am also working on adding recipe data from Kaggle to broaden the available recipe information. The ingredients, portions and nutrition information will still require review.

The progress is a more complete application and clearer evidence about its limits. Thank you.

### Transition

I welcome your questions and feedback.

### Evidence

- [Personal and simulation workspace validation](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/workspace-separation-validation-2026-11-14.md)
- [Controlled meal and portion sensitivity results](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/meal-response-sensitivity-2026-11-12.md)
- [Recipes Dataset by thedevastator on Kaggle](https://www.kaggle.com/datasets/thedevastator/better-recipes-for-a-better-life)

## Slide 11 Earlier research supporting model selection

**Outside the timed talk. Hidden backup for questions.**

### Presenter emphasis

- These are completed October research results already reported at Milestone 2.
- Compare each cohort with its own persistence baseline. Do not compare cross-cohort MAEs as a head-to-head model ranking.
- Neither interval coverage nor MAE reduction is percentage accuracy.

### Suggested speech

This table summarizes the earlier independent research study, already presented at Milestone 2. LightGBM improved participant-average trajectory MAE relative to persistence on both cohorts. Tight precision remained poor, and the nominal 80% marginal bands covered only 63.94% on PEDAP. These results justify a research candidate, not dependable individual prediction.

### Transition

If useful, I can explain the model inputs next.

### Evidence

- [Earlier independent model evaluation](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/metabonet-phase6-independent-2026-10-16.md)

## Slide 12 Model inputs and saved evidence

**Outside the timed talk. Hidden backup for questions.**

### Presenter emphasis

- Both paths produce 24 five-minute forecast points.
- Never pad a short source or borrow future glucose to meet the native history requirement.
- Saved intervals, model identity and meal revisions preserve the meaning of historical results.

### Suggested speech

The models share one application interface but have different input contracts. Chronos uses 24 historical samples in this application; native LightGBM uses 288. The frozen candidate uses current carbohydrates with past glucose and recorded-event features. Results preserve their model, input and interval identity.

### Transition

I can also show how portion comparisons work.

### Evidence

- [Frozen LightGBM application integration](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/lightgbm-app-validation-2026-11-12.md)

## Slide 13 Portion comparisons and later observations

**Outside the timed talk. Hidden backup for questions.**

### Presenter emphasis

- Scenarios use the original frozen model/context and stay separate from consumption.
- Later observations require the correct source clock and exact coverage.
- Preset simulator meals do not match arbitrary user-entered meals.

### Suggested speech

A portion comparison freezes the original context and model while scaling the reviewed meal amounts. Later-observation metrics use genuinely available virtual source readings. Neither the comparison nor a preset simulator future establishes the causal effect or accuracy of an arbitrary entered meal.

### Transition

The remaining question is how these features are verified.

### Evidence

- [Application implementation checkpoint](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/webapp-implementation-checkpoint-2026-11-11.md)
- [Controlled meal and portion sensitivity results](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/meal-response-sensitivity-2026-11-12.md)

## Slide 14 Verification and remaining core checks

**Outside the timed talk. Hidden backup for questions.**

### Presenter emphasis

- Separate offline, fixture-browser, live-service and human/manual evidence.
- Do not add overlapping historical test totals.
- Physical-camera testing remains deferred rather than passed.

### Suggested speech

The offline checks and recorded integration/browser journeys establish stated behavior only. Human Chrome keyboard and zoom checks, representative recipe review, combined follow-up/retrieval variants and matching-outcome evaluation remain open. Camera testing remains an explicit deferral.

### Transition

I would welcome guidance on the remaining checks.

### Evidence

- [Provider and forecasting integration evidence](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/m2-closure-validation-2026-11-12.md)
- [Personal and simulation workspace validation](https://github.com/sourav1859/GlycoLens/blob/7ce5f608b6dcd93684d59e8ae48a8630659c84df/docs/reports/workspace-separation-validation-2026-11-14.md)

## Technical term reference

| Term | Brief explanation |
|---|---|
| CGM | A continuous glucose monitor that records glucose over time. |
| API | A connection through which the application requests information from another service. |
| Frozen inputs | The saved meal, model and historical information used for a particular forecast. |
| Prediction band | A range expressing uncertainty around the central prediction. |
| Coverage | How often observed values fall inside the displayed range. |
| Sensitivity | Whether the forecast changes when an input changes; it does not establish accuracy. |

## Prepared questions and answers

### What is new since the Milestone 2 presentation?

Live provider verification, the redesigned application and persistent account/meal flows, optional native LightGBM serving, separate personal/simulation workspaces, portion/follow-up features and the controlled application sensitivity diagnostic.

### Was the LightGBM accuracy study repeated for Milestone 3?

No. The completed independent study was already reported at M2. M3 integrates the frozen candidate and evaluates application behavior; it does not claim a new independent cohort score.

### Why does Chronos remain the default after the sensitivity failure?

The approved default remains in place and its limitation is disclosed. The diagnostic does not authorize an automatic model switch. LightGBM remains an explicit research choice.

### Does a changing LightGBM forecast prove accurate meal effects?

No. It shows that the frozen model can respond to carbohydrate inputs in these synthetic contexts. Accurate magnitude, direction and matching outcomes remain unestablished.

### Does the LLM calculate nutrition?

No. It proposes ingredient and quantity drafts. Users review the matches and amounts; the application calculates totals from source food facts.

### How strong is the eight-recipe result?

It is a bounded live smoke evaluation. The scoring correction accepted valid flour role-name variants without changing outputs. Broader representative accuracy remains unmeasured.

### Why is a longer simulation necessary?

The frozen native model needs 24 hours of pre-origin glucose. The separate 48-hour scenario supplies history without padding the short demonstration or exposing future readings.

### Do personal meals receive glucose forecasts?

No personal glucose connector is enabled. Personal logging and nutrition work independently; forecasts remain in the virtual research workspace.

### Can later simulator readings validate any entered meal?

No. The future follows preset simulated meals. A matching-meal evaluation needs the proposed meal and corresponding later observations.

### What does an 80 percent prediction band mean?

It names the calibration coverage target for a range. It does not mean 80 percent of point forecasts are within ten mg/dL, nor guarantee coverage for an individual or a new population.

### How does earlier-meal retrieval avoid future information?

Candidate filtering restricts the owner, earlier meal time and outcome availability before the query origin. The current demonstration is same-session simulated history.

### What is the Kaggle ingestion status?

I am working on recipe ingestion from thedevastator's Recipes Dataset on Kaggle. The goal is to broaden recipe information while reviewing ingredient quantities, portions and nutrition before use.

## Rehearsal checklist

- Rehearse only Slides 1–10 and record the actual duration.
- Pause briefly at the workspace screenshot, model requirements and sensitivity table.
- Keep the earlier M2 accuracy results separate from new M3 findings.
- Distinguish implemented behavior, synthetic diagnostic evidence and prediction accuracy.
- Explain that the LLM proposes ingredients while reviewed food records supply nutrition.
- Keep Kaggle ingestion ongoing; do not invent a completed count or stage.
- Use hidden backups only for relevant questions.
