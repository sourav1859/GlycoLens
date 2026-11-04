# GlycoLens Milestone 2 Advisor Email Draft

**Subject:** GlycoLens Milestone 2 progress and model experiment results

Dear Professor Yang,

I have completed the core GlycoLens Milestone 2 prototype and the six-phase model-refinement study. I have attached a report summarizing the implementation, experiments, findings and remaining work.

The prototype supports an authenticated demo session, live py-mgipsim simulation, meal and nutrition review, saved forecasts and historical meal comparison. Live nutrition/recipe-provider verification, physical barcode-camera testing and final presentation/acceptance evidence are still pending, so I am not claiming full milestone closure yet.

I compared Chronos-2 and TimesFM-3 with a persistence baseline, varied the available glucose/insulin/meal context, trained small Ridge and LightGBM models, and tested corrections to frozen Chronos forecasts. The initial pretrained benchmark did not outperform persistence. In the broader MetaboNet experiment, direct LightGBM was the strongest candidate under the predefined average-error criterion; adding a Chronos correction did not provide a convincing incremental benefit.

On independent primary testing across 3,533 meals from 102 held-out participant identities, LightGBM reduced average trajectory error from 36.81 to 29.91 mg/dL, an 18.74% reduction. On the separate pediatric PEDAP cohort, error fell from 48.77 to 40.92 mg/dL. However, only 28.20% and 19.57% of predictions, respectively, were within +/-10 mg/dL. Pediatric uncertainty coverage was also below its nominal target. The precision goal remains unmet, and the findings do not establish clinical reliability.

My proposed next steps are to finish the live application checks, prepare a compatible LightGBM integration, and investigate broader development data, event timing and lightweight personalization. Any further model tuning would need fresh held-out confirmation. The application currently still uses Chronos; no large foundation model was trained or automatically substituted.

Would you recommend prioritizing LightGBM integration and milestone completion, or another accuracy-improvement round? I would also appreciate any suggestions on features, datasets, models or evaluation criteria, and your view on using LightGBM as the research predictor while retaining the pretrained comparisons.

Thank you for your guidance.

Best regards,  
Sourav Patil

**Suggested attachment:** `GlycoLens_Milestone_2_Advisor_Report_2026-10-26.docx`  
**Markdown companion:** `GlycoLens_Milestone_2_Advisor_Report_2026-10-26.md`
