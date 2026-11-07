# GlycoLens Capstone Planning Pack

November 7 deployment decision: the user selected **Hostinger KVM 2 with managed
Supabase** as the initial target. [ADR 0016](../decisions/0016-initial-hostinger-kvm2-managed-supabase.md)
and [architecture section 13](GlycoLens_04_Tech_Stack_and_System_Architecture.md#13-deployment)
define the topology; the [M3 deployment checklist](GlycoLens_06_Milestones_and_Schedule.md#initial-hostinger-kvm-2-deployment)
tracks implementation and hosted acceptance. Provider selection is complete;
provisioning and deployment are pending. Model selection, catalog correction gates
and course deadlines are unchanged.

November 6 catalog update: the user confirmed that Azure recipe corrections are ongoing
and the data will be used after correction. The [migration strategy](../reports/azure-to-supabase-catalog-migration-strategy-2026-11-06.md)
measures a proposed compact Supabase copy; [ADR 0015](../decisions/0015-corrected-nutrition-catalog-migration.md)
records the design. No current recipe activation, full export, cloud import or M2 closure is claimed.
The [milestone schedule](GlycoLens_06_Milestones_and_Schedule.md#corrected-nutrition-catalog-migration-from-milestone-2)
tracks execution under M3, with the completed audit/strategy retained as M2 evidence.


## Current model-refinement status - Phase 6 complete

**The broader-data model-refinement sequence, Phases 1-6, is complete.** Separate calibration used 48 participant representatives from 1,488 eligible meals. Frozen LightGBM scored 29.91 mg/dL macro trajectory MAE / 28.20% within +/-10 on 3,533 primary-test meals (102 IDs), and 40.92 / 19.57% on 2,177 PEDAP meals (64 IDs). Both predeclared point-improvement gates passed, with zero failed forecasts; tight precision remains poor. Nominal 80% marginal coverage was 79.05% primary and 63.94% PEDAP. Both test cohorts are now consumed; no test-based reselection, point refit, app promotion or full-M2 closure.

Current research evidence and the remaining M2 live-nutrition/presentation work must be tracked separately.

The [Milestone 2 PowerPoint draft](../presentations/GlycoLens_Milestone_2_Presentation_2026-11-03_v4.pptx)
and [timed speaking notes](../reports/GlycoLens_Milestone_2_Presentation_Notes.md) were
prepared November 2 and revised November 3. At the user’s request, the current
plain-language speech targets 7:30 within 7–8 minutes, replacing the earlier shorter
script. Ten main slides and four hidden backup slides remain. Remaining live checks and final
acceptance still prevent full milestone closure.

The October 26 [advisor report in Markdown](../reports/GlycoLens_Milestone_2_Advisor_Report_2026-10-26.md)
and [Word](../reports/GlycoLens_Milestone_2_Advisor_Report_2026-10-26.docx) consolidate this
evidence with proposed next steps and advisor questions. The accompanying
[email draft](../reports/GlycoLens_Milestone_2_Advisor_Email_Draft_2026-10-26.md) is prepared for review.

See [protocol 16](GlycoLens_16_MetaboNet_Independent_Evaluation.md), [independent results](../reports/metabonet-phase6-independent-2026-10-16.md) and [verification handoff](../tooling/metabonet-phase6-handoff-2026-10-16.md).

**Project:** GlycoLens: AI-Assisted Meal Understanding and Personalized Glucose Response Prediction for Type 1 Diabetes  
**Prepared:** September 7, 2026  
**Status:** Revised after advisor feedback

## What changed after the advisor meeting

The project is now **inference-first and application-first**.

The previous direction emphasized training LightGBM/LSTM models on the available T1D datasets. The revised direction treats large custom model training as unnecessary and potentially risky because the richest multimodal dataset (T1D-UOM) contains dense records but only 17 participants.

The revised plan is:

1. Reuse **pretrained time-series / CGM models**.
2. Benchmark which model best fits meal-centered T1D forecasting.
3. Focus experimentation on **inference context**:
   - CGM only
   - CGM + insulin
   - CGM + meal/carbohydrates
   - CGM + full meal nutrition
   - optional activity/context
4. Fine-tune only if zero-shot/frozen inference is insufficient; prefer a **small adapter, LoRA, linear head, or residual calibration model** over full-model training.
5. Make the main capstone deliverable a **mobile-first PWA** with concrete user outputs:
   - meal understanding
   - verified nutrition
   - personal historical meal evidence
   - 2-hour glucose forecast with uncertainty
   - portion/scenario comparison
6. Keep insulin dosing and pump control out of scope.

## Recommended implementation decisions

| Decision | Recommendation |
|---|---|
| App form factor | **Mobile-first Progressive Web App (PWA)** |
| Frontend | Next.js + TypeScript |
| Backend | FastAPI + Python |
| App database | Supabase PostgreSQL |
| Initial deployment | **Hostinger KVM 2** for PWA/API/CPU inference/simulator; **managed Supabase**, initially Free subject to measured capacity |
| Similar-meal personalization | SQL + pgvector; **not GraphRAG for MVP** |
| Primary model candidates | Chronos-2 and TimesFM-3 |
| Domain-specific exploratory model | CGMformer |
| Literature/reference model | GlucoFM |
| Small learned baseline | Persistence + optional LightGBM |
| Main rich dataset | T1D-UOM V1.0.4, pinned to Zenodo DOI `10.5281/zenodo.17361905` |
| External validation | AZT1D, HUPA-UCM |
| Simulation | py-mgipsim |
| CGM integration | Dexcom Developer Sandbox |
| Nutrition | USDA FoodData Central + Open Food Facts |

## Files in this pack

The user approved full Milestone 2 implementation on October 14, 2026, with
py-mgipsim first, Dexcom deferred, and API-backed recipe extraction followed by
ingredient editing/confirmation. The phase gates and live evidence ledger are in
[Milestone 2 Implementation](GlycoLens_10_Milestone_2_Implementation.md).

1. `GlycoLens_01_Updated_Project_Summary.md` - revised project specification.
2. `GlycoLens_02_Model_Inference_and_Dataset_Strategy.md` - model shortlist, dataset fit, experiment plan.
3. `GlycoLens_03_App_Product_Spec_and_UX.md` - features and end-to-end user experience.
4. `GlycoLens_04_Tech_Stack_and_System_Architecture.md` - final recommended stack, schema, services, architecture.
5. `GlycoLens_05_Scientific_Method_and_Evaluation.md` - scientific framing, hypotheses, experiments and metrics.
6. `GlycoLens_06_Milestones_and_Schedule.md` - course-aligned work plan through the December defense.
7. `GlycoLens_07_Literature_and_Market_Survey.md` - categorized literature and competing-app review.
8. `GlycoLens_08_Risks_Safety_and_Scope.md` - risks, safety boundaries, fallback plan and scope controls.
9. `GlycoLens_09_Project_Specification_Draft.md` - concise project-spec draft matching the course guidance.
10. `GlycoLens_10_Milestone_2_Implementation.md` - approved implementation and closure evidence.
11. `GlycoLens_11_Model_Refinement.md` - approved October 16 refinement protocol, phases and results.
12. `GlycoLens_12_MetaboNet_Experiment.md` - frozen broader-data preparation and reserved-test protocol.
13. `GlycoLens_13_MetaboNet_Frozen_Inference.md` - validation-only frozen history/context comparison.
14. `GlycoLens_14_MetaboNet_Direct_Models.md` - train-only small-model CV, paired validation and completion evidence.
15. `GlycoLens_15_MetaboNet_Chronos_Correction.md` - frozen C2 correction, matched direct controls and incremental gate.

The user approved local model refinement after the original pretrained comparison failed
to beat persistence. This includes small trained direct/residual models, separate calibration,
and an independent common-feature AZT1D test; foundation weights remain frozen. +/-10 mg/dL
is an aspirational tolerance. Original M2 results remain intact; no research winner is
automatically promoted into the app. See the [refinement report](../reports/model-refinement-results-2026-10-16.md).

Subsequent October 16 intake: the user supplied MetaboNet train/test Parquet files
and v1.2 release-note evidence. A metadata/training-quality audit is complete;
No fitting or test-outcome reading occurred during that intake audit. See
[the intake audit and next steps](../reports/metabonet-intake-audit-2026-10-16.md).

Phase 2 preparation is now executed and verified: the Loop/ReplaceBG pilot has
8,973 training, 2,000 validation and 1,948 calibration six-hour windows. Source-qualified
subjects are split before target inspection. Primary test (104 identities) and PEDAP
source test (65 identities) remain metadata-only reservations. See the
[preparation report](../reports/metabonet-phase2-preparation-2026-10-16.md) and document 12.

**Phase 3 is complete.** Seven frozen comparisons
on 1,509 matched validation events found no eligible Chronos winner over persistence
(macro MAE 37.12 mg/dL versus 37.61 for six-hour C2). The improvement gate failed.
The two-hour C0 history is the only failure-free C0, not the point-accuracy optimum;
longer histories have lower conditional errors but native-output failures. No weights
were fitted in Phase 3 and its reserved tests were untouched then. Phase 6 below
now records independent testing. See
[the results](../reports/metabonet-phase3-inference-2026-10-16.md) and document 13.

**Phase 4 is complete.** Thirty-two training-only
CV candidates selected 24-hour event features for both small models. LightGBM reached
31.17 mg/dL macro MAE versus persistence 37.12 on the same 1,509 validation meals:
16.03% lower, passing the research gate. Tight-tolerance accuracy is still poor:
within +/-10 is 26.84% (Ridge 28.85%), not an 80% result or maximum-error guarantee.
No calibration/reserved-test outcomes or app model switch. See
[Phase 4 results](../reports/metabonet-phase4-training-2026-10-16.md) and document 14.



**Phase 5 was complete before the Phase 6 evaluation recorded below.** Frozen C2
generated 6,756 training forecasts; 6,756 usable meals / 196 identities supported six CV
configurations / 18 fold fits and four final refits, with exactly matched direct
controls. Neither correction passed the predeclared incremental gate; retain Phase 4
LightGBM. Lowest-MAE eligible option: `ridge_residual_1000`; advancement candidate:
`lightgbm_direct` (macro MAE 31.17 mg/dL, within +/-10 26.84%). These are
reused-validation findings, not independent confirmation. At Phase 5 completion, calibration/reserved outcomes were untouched.
Phase 6 below supersedes that access status; app inference remains unchanged.
See [protocol 15](GlycoLens_15_MetaboNet_Chronos_Correction.md) and [results](../reports/metabonet-phase5-correction-2026-10-16.md).

## Three decisions to confirm with the advisor/user

1. **PWA vs native mobile:** this pack recommends PWA because it maximizes delivery speed and still supports a mobile-first experience and barcode scanning. If app-store delivery is a requirement, switch the frontend to React Native/Expo.
2. **Model count:** recommend two required candidates (Chronos-2 + TimesFM-3) and one exploratory candidate (CGMformer). Do not benchmark many models at the expense of the app.
3. **Real-user data:** recommend public/de-identified datasets + Dexcom Sandbox + virtual patients only for the capstone unless the advisor explicitly wants a real-user study and the required approvals are available.
