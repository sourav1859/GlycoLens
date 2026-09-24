# GlycoLens Capstone Planning Pack

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
| Similar-meal personalization | SQL + pgvector; **not GraphRAG for MVP** |
| Primary model candidates | Chronos-2 and TimesFM-3 |
| Domain-specific exploratory model | CGMformer |
| Literature/reference model | GlucoFM |
| Small learned baseline | Persistence + optional LightGBM |
| Main rich dataset | T1D-UOM |
| External validation | AZT1D, HUPA-UCM |
| Simulation | py-mgipsim |
| CGM integration | Dexcom Developer Sandbox |
| Nutrition | USDA FoodData Central + Open Food Facts |

## Files in this pack

1. `GlycoLens_01_Updated_Project_Summary.md` - revised project specification.
2. `GlycoLens_02_Model_Inference_and_Dataset_Strategy.md` - model shortlist, dataset fit, experiment plan.
3. `GlycoLens_03_App_Product_Spec_and_UX.md` - features and end-to-end user experience.
4. `GlycoLens_04_Tech_Stack_and_System_Architecture.md` - final recommended stack, schema, services, architecture.
5. `GlycoLens_05_Scientific_Method_and_Evaluation.md` - scientific framing, hypotheses, experiments and metrics.
6. `GlycoLens_06_Milestones_and_Schedule.md` - course-aligned work plan through the December defense.
7. `GlycoLens_07_Literature_and_Market_Survey.md` - categorized literature and competing-app review.
8. `GlycoLens_08_Risks_Safety_and_Scope.md` - risks, safety boundaries, fallback plan and scope controls.
9. `GlycoLens_09_Project_Specification_Draft.md` - concise project-spec draft matching the course guidance.

## Three decisions to confirm with the advisor/user

1. **PWA vs native mobile:** this pack recommends PWA because it maximizes delivery speed and still supports a mobile-first experience and barcode scanning. If app-store delivery is a requirement, switch the frontend to React Native/Expo.
2. **Model count:** recommend two required candidates (Chronos-2 + TimesFM-3) and one exploratory candidate (CGMformer). Do not benchmark many models at the expense of the app.
3. **Real-user data:** recommend public/de-identified datasets + Dexcom Sandbox + virtual patients only for the capstone unless the advisor explicitly wants a real-user study and the required approvals are available.
