# ADR 0022: Opt-in LightGBM through the common forecasting interface

## November 14: local LightGBM selection enabled for user review

At the user's request, the existing local development runtime now exposes **LightGBM · research option** alongside default Chronos. The ignored local enablement flag is true; the running API's native bundle/digest/read-only mount were verified and real synthetic inference returned 24 ordered points. The shipped environment template remains disabled by default. This is a user-authorized local research exposure for manual testing, not completed L0–L4 acceptance, production enablement or a model default change. All existing history/artifact/owner checks remain enforced.

An existing meal attached to the short one-day source remains ineligible for native inference. Explicitly prepare the 48-hour research source and save a new reviewed meal at that source's clock; existing meal/source snapshots are unchanged. Current carbohydrates are the native meal predictor; matching-outcome accuracy and transferred interval coverage remain unvalidated. [Enablement and verification](../reports/local-lightgbm-enablement-2026-11-14.md). November 12 off-state descriptions below are historical checkpoints; their outstanding acceptance results remain valid.

## Implementation evidence — November 12

The shared native registry, exact 24h feature builder, separate 48h protocol, forward cloud v2 migration, signed calibrated bands, research UI/export and CPU packaging/recovery are implemented. [Actual validation](../reports/lightgbm-app-validation-2026-11-12.md) records limits and open Chrome/manual gates. Chronos remains default despite failed synthetic meal-response capability; native sensitivity is not accuracy. No refit or consumed-cohort access. Ordinary enablement remains false, controlled local review only.

**Date:** November 12, 2026. **Status:** implemented; ordinary enablement remains gated by [plan 18](../planning/GlycoLens_18_M2_Closure_and_LightGBM_Integration.md).

## Context

The app uses Chronos C3. The frozen MetaboNet LightGBM adapter implements the same canonical interface and passed that study's point-improvement gates, with material accuracy/coverage limitations. The cohorts differ from original M2 UOM: research results do not establish a direct app-model comparison or authorize a default switch. Existing app context has two hours of CGM and incompatible insulin/missingness semantics; LightGBM needs 24 hours and recorded-event features. Raw direct-adapter bounds are placeholders; saved calibration must be explicitly integrated.

## Options and tradeoffs

Scores are engineering judgments, 1–5 (higher is better), not measured performance. Weights reflect one-developer capstone delivery. A separate model service adds deployment/auth/transport failure modes without solving feature compatibility. Keeping Chronos alone has the lowest immediate change risk but cannot deliver the requested research option.

| Criterion | Weight | Keep Chronos only | Same-backend opt-in | Separate LightGBM service |
|---|---|---|---|---|
| Requested delivery fit | 25 | 1 | 5 | 3 |
| Correctness/privacy | 25 | 5 | 4 | 3 |
| Maintainability/testability | 20 | 5 | 4 | 2 |
| Operational cost/complexity | 15 | 5 | 4 | 2 |
| Observability/rollback | 15 | 4 | 5 | 3 |
| Weighted score / 5 | 100 | 3.85 | **4.40** | 2.65 |

Same-backend correctness is conditional on training-compatible inputs, verified artifact identities and interval contracts. It adds CPU dependencies and registry complexity but reuses ownership, snapshots, bounded inference and deployment. Performance is unmeasured; separate service isolation becomes credible only if measured resource/conflicting-dependency needs justify it.

## Decision

1. Keep Chronos as default; add LightGBM only as an explicit research option after L0–L4. No automatic fallback or model promotion.
2. Reuse the common adapter in FastAPI, with one allowlisted registry shared by ordinary and portion-scenario inference. Freeze full model/bundle/feature/calibration identity in each result and retry key.
3. Retain the existing one-day demo. Add a separately versioned longer synthetic scenario, preferably 48h, with verified 24h pre-origin history and withheld later data. Do not pad/relabel old history or change old replay checksums.
4. Match 288-point CGM, masks, five-minute insulin amounts, previous-carbohydrate timing and current carbohydrate feature semantics. Distinguish unknown from observed zero; do not treat U/hour as U/bin. Current frozen LightGBM does not use protein/fat/fiber directly.
5. Load trusted checksum-verified frozen artifacts and saved calibration, not retrained weights. Prefer narrow native serving export only with synthetic parity. No client-supplied artifact paths; no research rows/weights in app storage or frontend.
6. Version API/storage/UI semantics for calibrated symmetric marginal bands and accurate provenance before enablement. Preserve mathematically valid signed endpoints; no clipping or equal-placeholder uncertainty. Preserve old v1 results.
7. Chrome/manual barcode acceptance proceeds now. Physical camera is deferred by user, retained as future acceptance and never marked passed. LightGBM integration is additional app work, not a new original-M2 prerequisite.

## Validation and rollback

Use [the traceability catalog](../testing/m2-closure-lightgbm-test-cases.md): artifact trust/parity, unit/mask/timing oracles, no-future leakage, API/storage interval compatibility, owner/retry checks, responsive opt-in flows, CPU Compose and unchanged Chronos regressions. Primary/PEDAP test cohorts stay consumed; sensitivity is not independent accuracy.

Disable the option if readiness or correctness fails; preserve Chronos default and immutable historic LightGBM reads. Forward storage migrations remain compatible with old results. Revisit service isolation only after measured contention or dependency evidence. A future default change requires a separate reviewed decision and relevant comparative validation.
