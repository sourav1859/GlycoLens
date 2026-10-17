# Milestone 2 implementation verification

Date: October 14, 2026. Status: core implementation verified; full closure pending
live nutrition/recipe configuration and final presentation verification.

## Implemented outcome

The browser now supports local authenticated demo selection, live py-mgipsim or
labeled replay, a pre-origin glucose timeline, meal capture/nutrition confirmation,
atomic meal saving, a real validation-selected Chronos C3 forecast, persisted results
and same-session numeric historical retrieval. Barcode camera code and manual entry,
USDA search/details, Open Food Facts lookup, structured recipe extraction and editable
ingredients are present. The live fixture-food path does not prove external nutrition.

The modular monolith, common immutable adapter contract and separate research data
boundary remain intact. No hosted service was changed, and no commit/push/deployment
was performed. Pre-existing M1 presentations and user documentation changes were preserved.

## Requirement-to-evidence matrix

| Requirement | Evidence | State |
|---|---|---|
| Reproducible baseline | Normal Python/Node commands, value-free preflight, lockfiles | Pass |
| Robust windows/data quality | 927 windows / 3,884 loaded meals; exclusion counts reproduced | Pass with selection-bias limitation |
| Splits/leakage | Versioned time cuts, target purging, explicit subject definitions, input/target tests | Pass; subject-disjoint benchmark not run |
| Model comparison | Real pinned Chronos/TimesFM/persistence on 177 validation and 211 test requests | Pass |
| Context ablation | Real C0-C3 covariate execution, masks/raw-kind descriptors, matched results | Pass; source-unit ambiguity remains explicit |
| Selection | Chronos C3 frozen before test | Pass; persistence is more accurate |
| Demo session/timeline | Real local Supabase anonymous Auth and owner-token RLS | Pass |
| Nutrition persistence | SQL basis/serving math, source snapshots, repeat-ingredient aggregation, atomic rollback | Pass |
| Food search/barcode | Provider adapters, private catalog caching, missingness/units tests, fixture browser path | Implemented; live provider/camera verification pending |
| Recipe parser | Responses JSON schema, no patient context/nutrient guessing, editable ingredients | Offline/fixture verified; live key/model pending |
| Live integration | Actual isolated py-mgipsim through app/API, server-internal synthetic context | Pass |
| Forecast API/chart | Actual Chronos C3, 24 validated points, persisted read/retry, relative chart | Pass |
| Similar meals | SQL same-user/past-outcome filtering, numeric ranking, one earlier simulated meal | Pass |
| Mobile UX | Real and fixture Playwright flows; no page-wide overflow; rounded summaries | Pass |
| Final milestone closure | All live nutrition input paths, final presentation and closure audit | Pending |

## Verification evidence

- 94 passing offline Python tests, one explicit real-simulator skip; Ruff lint/format
  and nine repository skill/config validators pass. The opted-in real simulator suite
  separately passes all 11 tests, including two-run reproducibility.
- Five frontend component/client tests, ESLint, TypeScript, production build.
- 35 real local pgTAP tests after clean migration/reset/lint.
- Six Playwright checks across desktop/mobile: two real Auth/simulator/Chronos flows
  and four fixture UI contracts for confirmation, recipe editing and barcode fallback.
- Live application acceptance verifies meal/forecast retry deduplication, owner denial,
  persistence, 24-point output and earlier historical retrieval.
- Real model validation/test runs and participant-cluster intervals are exported only
  as sanitized aggregates in [the results report](milestone-2-model-results.md).

Artifacts remain ignored: application evidence, browser screenshots/traces, full model
event rows, simulator exports/internal context, weights and generated local configuration.
Physical camera capture and live USDA/recipe API behavior have not been verified.

## Scientific findings

The matched test table has 208/211 common successful events. Chronos C3 macro MAE is
37.920 mg/dL, versus persistence 33.957. Its q10-q90 coverage is approximately 53.9%,
not the nominal 80%. Pairwise Chronos-vs-persistence intervals use their own full
211-event successful set, explicitly different from the all-model table intersection.
H1 is not supported. These findings do not authorize dosing, clinical accuracy,
causal meal effects or calibrated confidence claims.

## Operations and unresolved items

Normal local runtimes worked; earlier sandbox permission errors did not require rebuild.
Two pre-existing formatter failures were corrected. Local startup later exposed a
PostgreSQL collation mismatch; index rebuild/metadata refresh restored the full stack.
Supabase 2.118.0 is pinned in the ignored workspace cache; global CLI remains unchanged.
The auxiliary vector log shipper is distinct from PostgreSQL pgvector and is not in
the meal/forecast path. Starlette emits a non-blocking httpx TestClient deprecation warning.

USDA_FDC_API_KEY, LLM_API_KEY and LLM_MODEL remain absent. The user was asked to
configure them privately and confirm recipe provider/model; no key should be posted
in chat. OpenAI Responses is the prepared adapter, not a silently chosen paid model.
Once configured: verify live provider normalization, parsing/refusals/timeouts,
food-source provenance and actual browser search/barcode/recipe input paths, then
finalize presentation/closure. Course dates were not revised by implementation approval.
