# Model performance, improvement options, and external dataset review

Reviewed October 15, 2026. This is an evidence review and proposed research sequence,
not approval of a new implementation, model selection, training run, or clinical claim.
No model weights, inference configuration, evaluation split, or application behavior
were changed during this review. No additional health dataset was downloaded.

## Assessment

The current pretrained forecasting results are disappointing. They demonstrate working
integration but do not demonstrate an accuracy benefit over repeating the last glucose
reading. The appropriate conclusion is that these configurations have not earned a
forecasting-accuracy advantage, not that all pretrained forecasting must fail.

The existing test report uses 208 common successful events across all configurations:

| Method | Participant-average full-trajectory MAE, mg/dL | Error at +30 min | Error at +60 min | Error at +120 min |
|---|---:|---:|---:|---:|
| Persistence | 33.957 | 21.769 | 39.118 | 46.039 |
| Chronos C0, glucose only | 39.348 | 23.698 | 45.516 | 53.516 |
| Chronos C3, insulin and meal macros | 37.920 | 25.269 | 46.293 | 49.173 |
| TimesFM C3, insulin and meal macros | 38.269 | 23.541 | 42.670 | 54.286 |

The endpoint columns are participant-average absolute errors at those individual
forecast times, not averages over all preceding times. They were read from the saved
test artifact's existing matched metrics; no new inference was performed. Chronos C3
has approximately 11.7% higher full-trajectory error than persistence on this set.
It beats persistence in only 3 of the 15 participant-average comparisons on the
same common set. Counts alone do not characterize the magnitude of each person's error.

The separately reported paired comparison uses all 211 successful events for Chronos
C3 and persistence: Chronos has 4.197 mg/dL higher participant-average MAE, with a
descriptive participant-bootstrap 95% interval of [1.894, 6.884]. The difference in
event sets explains why this is not exactly 37.920 minus 33.957. Small-cohort bootstrap
intervals do not establish performance in the wider T1D population.

Full context improves Chronos's aggregate MAE over C0, but worsens its +30 and +60
minute endpoint errors. Claims that every nutrient/context addition consistently
improves accuracy would be false. Selecting Chronos as the pretrained integration
candidate is also different from selecting the most accurate method overall. The
selection utility explicitly excludes persistence as a selectable pretrained run.

Chronos C3's nominal q10-q90 band covers 53.9% of held-out points, rather than its
intended 80%; its mean width is about 74.8 mg/dL. TimesFM C3 coverage is 50.4%.
Neither model's uncertainty is adequately calibrated in this experiment.

## What an 80% target can mean

Glucose forecasting is numerical prediction, so there is no universal classification
accuracy percentage. MAE 37.920 is not 37.920% error and cannot be converted into
accuracy by subtracting it from 100. Likewise, correlation 0.8, R-squared 0.8, error-grid
zone percentages, and interval coverage are different measurements.

One understandable research target is: at least 80% of predictions are within
20 mg/dL of observed glucose. Define the tolerance, horizon, population, failure
denominator, and participant weighting before running the next experiment. Report
this separately at +30, +60, and +120 minutes and across the complete trajectory.
The 20 mg/dL threshold here is a proposed project criterion, not a medical standard.
Reaching it over the entire two-hour T1D post-meal trajectory cannot be promised.

The current saved artifacts retain event metrics, not individual prediction/target
arrays, and do not contain this tolerance-based score. It cannot be recovered from
MAE alone. A future versioned evaluation must explicitly calculate it.

An 80% prediction interval is a separate target: about 80% of individual observed
future readings should lie inside the band. Increasing band width can increase
coverage without improving the central forecast. Assess coverage with width and
quantile loss, including per-horizon and glucose-range breakdowns; point coverage
does not mean an entire two-hour trajectory is covered 80% of the time.

Proposed first performance gate: reduce full-trajectory MAE by at least 10% against
persistence on the identical held-out set, without unacceptable failures or large
errors in important subgroups. On the current table that would correspond to about
30.6 mg/dL, but this is an engineering research target, not a predicted result or
clinical threshold. Report tolerance accuracy and uncertainty separately.

## Findings from source inspection

1. **Inference is already happening.** Both adapters load pretrained checkpoints and
   produce predictions. No diabetes-specific model fitting or interval calibration
   is performed. Repeating the same inference does not teach a model from its mistakes.
2. **Short input history.** The default is 120 minutes, only 24 glucose observations.
   Longer histories are supported by the research configuration but have not been
   compared in the completed benchmark.
3. **Meal representation is limited.** `recorded_events_v1` places nutrients in one
   impulse at forecast origin and zero future meal impulses. It does not supply a
   learned absorption curve. The current converter also omits previous-meal nutrient
   history and activity from the implemented C0-C3 requests.
4. **Insulin records are not insulin action.** Sparse raw observations, masks, and
   older summaries preserve source information; basal units remain ambiguous. They
   do not measure remaining active insulin. A model accepting numerical covariates
   does not prove that it understands these physiological meanings.
5. **Data quality and selection limit the claim.** Only 927 of 3,884 valid loaded
   meals survive filtering, across 15 participants. Missingness, meal-time accuracy,
   contradictory observations, and source timezone ambiguity need sensitivity analysis.
   Retrospectively excluding later meals defines a selected no-follow-up-meal cohort;
   it is not a condition guaranteed at deployment.
6. **Useful leakage safeguards exist.** Model input and held-out target are separate;
   history resampling uses only readings at/before origin; later insulin is excluded;
   crossing targets are purged at chronological split boundaries. This inspection
   did not establish a specific software defect explaining the ranking.
7. **Generalization remains untested.** Later periods of the same participants were
   tested; subject-disjoint support exists but that benchmark has not been run.
   Thousands of correlated CGM points do not equal thousands of independent people.
8. **The original test has now been examined.** It remains the historical M2 result.
   Any iterative improvements informed by it need a fresh external/subject holdout
   for an independent final confirmation, not a relabeling of the same test.

These are observed design limitations and research hypotheses. They do not prove
which change will improve accuracy, or that small sample size caused the poor score.
Additional test subjects improve confidence in assessment; they do not automatically
improve a fixed model.

## Research evidence and implications

- [GlucoFM-Bench](https://arxiv.org/html/2606.06881v1) evaluates multiple populations
  and training regimes. Its main comparisons use 12-hour input and shorter endpoint
  forecasts; its TimesFM model is 2.5. These results support testing longer input and
  adaptation, but do not validate our TimesFM-3 configuration or guarantee two-hour
  meal-centered performance. The paper finds supervised LSTM competitive/stronger
  with enough task-specific data; pretraining is not automatically the best choice.
- [Xiong et al.](https://www.frontiersin.org/journals/endocrinology/articles/10.3389/fendo.2024.1423303/full)
  use LightGBM with glucose, insulin, nutrition and participant context in 13 people
  with T1D. This supports a small task-specific baseline. Its correlation of 0.63
  for a meal-response summary is neither 63% accuracy nor a full-trajectory MAE result.
- [Wolber et al.](https://pubmed.ncbi.nlm.nih.gov/41177244/) combine temporal nutrient
  features and LightGBM, including AZT1D validation. The useful idea is to model
  events over time instead of relying solely on isolated impulses. Reported results
  use a different task/protocol and cannot be transferred to GlycoLens.
- [Shen et al.](https://pubmed.ncbi.nlm.nih.gov/40042044/) study meal-response summaries
  in 397 T1DEXI participants; food categories improve on macros alone. This motivates
  a later feature experiment, not a claim that food labels ensure accuracy.
- [CGMformer's official repository](https://github.com/YurunLu/CGMformer/) exposes a
  checkpoint, but its diet prediction component explicitly requires paired-data
  training. A frozen encoder plus small downstream head is a realistic experiment,
  not a ready-made zero-training replacement. The
  [official GlucoFM page](https://research.google/blog/glucofm-foundation-model-for-continuous-glucose-monitoring/)
  reports promising frozen-representation results in a different cohort. An official
  downloadable forecasting checkpoint was not verified in this review.
- [Chronos's official implementation](https://github.com/amazon-science/chronos-forecasting/blob/main/src/chronos/chronos2/pipeline.py)
  supports full and LoRA fitting; the locally installed pinned package also exposes
  these modes. Availability is not evidence of improvement. GPU access mainly affects
  feasibility/speed; it does not itself fix accuracy.
- [Adaptive conformal inference](https://proceedings.neurips.cc/paper/2021/hash/0d441de75945e5acbc865406fc9a2559-Abstract.html)
  provides a basis for interval calibration under changing conditions. Ordinary
  split-conformal guarantees require assumptions not automatically satisfied by
  correlated CGM streams; use separate chronological calibration data and validate
  coverage under temporal/participant shift. Do not promise per-person or every-horizon
  coverage merely from overall empirical coverage.

## Proposed improvement sequence

| Stage | Work | Training needed? | Decision gate |
|---|---|---|---|
| 1 | Audit units, timestamp alignment, missingness, origin glucose/trend, failures, and participant/horizon errors; add explicit tolerance metrics | No | Reproduce baseline and document data-quality strata |
| 2 | Compare 2/6/12/24-hour histories on development/validation; keep forecast task fixed | No | Improvement on matched events, with changed eligibility also reported |
| 3 | Compare ridge regression and small LightGBM models predicting glucose change; try a regularized correction/blend of persistence and frozen Chronos | Yes, small supervised fit | Beat persistence and a direct small-model baseline on validation without participant leakage |
| 4 | Add validated past-meal/time-since-event features; insulin-action or nutrient-response features only with justified units/types and train-only parameter fitting | Small fitting may be needed | Ablations demonstrate incremental value; no invented biology |
| 5 | Calibrate intervals on a distinct earlier calibration period, assess width and quantile loss | Calibration fit | Coverage approaches declared target without uselessly wide intervals |
| 6 | Freeze preprocessing/model/thresholds, evaluate untouched subjects and a source-disjoint external cohort | No test-set fitting | Paired comparisons and participant-level uncertainty support the improvement |
| 7, optional | Frozen CGM encoder plus head, then Chronos LoRA if simpler methods fail and data/compute justify it | Yes | Improvement survives independent validation; preserve inference-first scope |

Useful small-model features include current glucose, recent slopes and variability,
meal macros, time since recorded bolus/prior meal, and time of day where timestamp
semantics are justified. Personal corrections must use only a person's earlier records;
new-person evaluation must not use their held-out outcomes. Missing future insulin or
activity cannot be added retrospectively as though it were known at origin.

Large-model training from scratch is not recommended. Some supervised task adaptation
is a sensible next candidate, not a proven necessity or a guarantee of 80% performance.
Changing the recipe LLM/API keys will not repair this retrospective benchmark: its
nutrition inputs already come from recorded dataset values. Similar-meal display also
does not change the forecast unless explicitly added and tested as a model input.

## External dataset options

Published cohort counts are not guaranteed usable meal-window counts. Access and
metadata were researched; file downloads and harmonized participant counts were not
verified. Some Mendeley record requests were inaccessible to the browsing tool, so
original papers and author resources support the descriptions below.

| Resource | Published size/context | Best use | Constraint/access |
|---|---|---|---|
| [AZT1D](https://arxiv.org/abs/2506.14789) / [data record](https://data.mendeley.com/datasets/gk9m674wcx/1) | 25 people with T1D, 6-8 weeks; glucose, insulin, carbs, pump mode | First independent common-feature cohort, C0-C2 | Public research release; no equivalent full protein/fat/fiber labels; audit source units, modes and duplicates |
| [HUPA-UCM](https://pmc.ncbi.nlm.nih.gov/articles/PMC11214197/) / [data record](https://data.mendeley.com/datasets/3hbcscwz44/1) | 25 people with T1D; glucose, insulin, carbs, activity, sleep | Second cohort and sensor/activity shift | Native glucose is 15-minute; processed 5-minute values include interpolation. Carb servings are 10 g; calories are burned, not eaten. Verify record licensing on acquisition |
| [MetaboNet, 2026 paper version](https://arxiv.org/html/2601.11505v2) | 1,895 public-subset participants, 3,135 total across public and restricted sources | Larger common-feature development and cohort-holdout testing | [Author access page](https://www.replica.health/research/metabonet/) requires an account for public files; restricted cohorts need separate source approvals. Full meal nutrients vary/may be unavailable |
| [DiaTrend](https://www.nature.com/articles/s41597-023-02469-5) | 54 people with T1D, long glucose/pump histories and carb announcements | Personalization and longer-history evaluation | Synapse certification, intended-use statement and conditions; basal available for only 17 participants, glucose/pump coverage does not always align |
| [T1DEXI](https://search.vivli.org/doiLanding/studies/PR00008428/isLanding) | Hundreds of adults with T1D; a published meal analysis uses 397 | Larger meal-response/activity validation | Vivli access process; usable count depends on task and fields; do not assume complete macros or pump data for everyone |
| [OhioT1DM](https://webpages.charlotte.edu/rbunescu/ohiot1dm.html) | 12 people with T1D, approximately eight weeks | Established benchmark compatibility | Signed DUA and custodian process; not an instant unrestricted download |
| [CGMacros](https://physionet.org/content/cgmacros/1.0.0/) | 45 participants, ten days, full macros, paired sensors | Nutrition-method development and a separately labeled population-transfer study | No T1D participants: healthy, prediabetes and T2D. Open access under CC BY-NC-SA 4.0; cannot replace T1D validation |
| [GlucoFM-Bench resources](https://github.com/Augmented-Health-Lab/GlucoseML_benchmark) | Multi-cohort standardized glucose benchmark | CGM-only reproduction and adapter sanity checks | Standardized CGM arrays do not replace source meal/insulin logs; audit overlap with every other source |

For HUPA-UCM, score observed sensor timestamps separately or preferentially use original
records. Interpolating to five minutes creates no new independent observations; an
interpolated pre-origin value may use a post-origin sensor endpoint if preprocessing
is not causal. Audit this before claiming deployment-realistic forecasting.

MetaboNet consolidates T1D-UOM, AZT1D, HUPA-UCM and other cohorts. Do not count its full
size as additional unique participants or train on those components and then test on
their original copies. Hold out entire source cohorts, preserve source provenance,
and check within/across-source duplication. It is also not a guarantee of accurate
insulin conversions: compare harmonized semantics with original records, particularly
for ambiguous T1D-UOM basal observations. Public and restricted totals must remain
distinct in any data claim.

Recommended acquisition order: AZT1D first; assess/register for MetaboNet public data
in parallel for broader development; HUPA-UCM next with interpolation controls. Add
DiaTrend/T1DEXI if access and semester time allow. Keep T1D-UOM for full-macro ablation.
Do not fill missing external protein/fat/fiber with assumed zero or compare an external
C2 experiment as though it independently validated C3. Synthetic py-mgipsim and Dexcom
sandbox data remain integration/stress-test resources, not real-person accuracy proof.

## Review evidence and documentation scope

Source reviewed: model-results report; evaluation metrics, runner, statistics and split
protocol; benchmark, selection and report pipelines; T1D-UOM loader/windowing; model
adapters, converters and covariates; ADR 0008; security policy and safety checklist.
Stored test aggregates and participant-win counts were recomputed locally without
printing identifiers, timestamps, predictions, or dataset rows.

Planning documents reviewed: 00 and 01 for source-of-truth direction; 02 for models,
data and adaptation ladder; 05 for scientific evaluation; 07 for literature; 08 for
safety. They remain unchanged because this review proposes experiments rather than
adopting a new model, dataset, hypothesis, scope or schedule. The existing model report
is preserved. Graphify was ACTIVE and queried; important relationships were verified
against source. Documentation semantic extraction was not authorized or enabled.
