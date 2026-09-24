# GlycoLens Risks, Safety Boundaries, and Scope Controls

## 1. Core safety boundary

GlycoLens is a research prototype.

It will not:
- calculate a real-user insulin dose
- modify physician settings
- send commands to an insulin pump
- classify a meal as medically safe/unsafe
- diagnose T1D
- claim clinical-grade accuracy
- replace a clinician or regulated diabetes-management system

## 2. Model risk

### Risk
A pretrained general time-series model may not transfer well to T1D postprandial dynamics.

### Mitigation
- persistence baseline
- compare multiple pretrained models
- use real held-out T1D data
- show uncertainty
- keep historical evidence visible
- small calibration fallback rather than large training

## 3. TimesFM-3 maturity risk

### Risk
TimesFM-3 is extremely new as of September 2026.

### Mitigation
- implement Chronos-2 first
- keep TimesFM-2.5 as stable fallback
- do not architect the system around one model

## 4. GlucoFM checkpoint risk

### Risk
GlucoFM is highly relevant, but official weights are not currently public.

### Mitigation
- literature/reference only
- revisit at Milestone 2
- do not use unofficial weights as the main result unless provenance is fully documented

## 5. Dataset size risk

### Risk
T1D-UOM has only 17 participants.

### Mitigation
- no large model training
- inference-first
- subject-aware analysis
- external validation with AZT1D/HUPA-UCM
- make claims about the evaluated dataset, not all people with T1D

## 6. Meal-label quality risk

### Risk
Free-living food logs can be incomplete or inaccurate.

### Mitigation
- data-quality filtering
- sensitivity analysis
- describe source limitations
- do not treat self-reported nutrition as laboratory truth

## 7. Data leakage

### Risk
Future CGM or later events accidentally enter context.

### Mitigation
- strict timestamp boundary at meal time
- event-window tests
- chronological/subject-aware split
- retrieval only from data available prior to the tested event

## 8. Counterfactual risk

### Risk
"What-if 50% portion" can sound causal.

### Mitigation
Use wording:
- "model-based scenario"
- "predicted trajectory under changed meal features"

Do not use:
- "this is what would definitely happen"
- "this is safe"
- "you should eat this"

## 9. GraphRAG scope risk

### Risk
GraphRAG consumes time without improving the core goal.

### Decision
Not in MVP.

Use:
- PostgreSQL
- pgvector
- SQL/numeric similarity

Only add graph technology if:
1. all M2 core features work
2. a concrete retrieval question cannot be handled cleanly in Postgres
3. advisor agrees it adds capstone value

## 10. Mobile scope risk

### Risk
Native iOS + Android doubles delivery complexity.

### Decision
Mobile-first PWA.

Native React Native/Expo only if advisor explicitly requests native.

## 11. External API risk

### USDA
API key and rate/access dependence.

Mitigation:
- backend caching
- save resolved foods locally

### Open Food Facts
Community data can be incomplete/inaccurate.

Mitigation:
- display source
- prefer USDA where appropriate
- ask user to verify nutrition label
- do not silently merge conflicting values

### Dexcom
Developer access/sandbox behavior can change.

Mitigation:
- device-agnostic `CGMProvider`
- demo works with historical/simulated providers

## 12. Cloud/inference cost risk

### Mitigation
- models selected partly for practical inference
- local inference for defense
- cache model in process
- do not depend on expensive managed GPU service
- PWA/backend can run with a local Docker stack if needed

## 13. Privacy risk

For MVP:
- use public de-identified research data
- simulated users
- sandbox data

If real users are ever added:
- advisor/IRB/privacy requirements must be checked
- OAuth tokens and health data require stronger security
- HIPAA/compliance should not be assumed from ordinary cloud configuration

## 14. Schedule risk

### Scope-cut priority

Cut first:
1. image-based meal estimation
2. GraphRAG
3. clinician portal/report
4. native mobile
5. real-user integration
6. CGMformer downstream training
7. learned personalization

Protect:
1. research pipeline
2. pretrained model comparison
3. core context experiment
4. working meal/nutrition flow
5. forecast UI
6. Meal Passport
7. final results

## 15. Go/no-go checkpoints

### By Milestone 1
At least one pretrained model must run on real CGM data.

If not:
- use TimesFM-2.5 / simpler Chronos variant
- keep LightGBM as emergency forecast baseline

### By Milestone 2
End-to-end:
`meal -> context -> forecast -> UI`

If not:
- stop adding integrations
- focus only on core app

### By Milestone 3
No new major features.
Only:
- test
- analyze
- fix
- document
- improve presentation
