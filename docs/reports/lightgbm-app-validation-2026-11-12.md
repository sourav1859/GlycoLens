# Frozen LightGBM application integration

**November 12, 2026:** implemented and tested through real local CPU/API/cloud paths, with ordinary enablement gated off. Chronos remains default. This is application integration, not a new research evaluation or accuracy claim. [Actual case ledger](../testing/m2-closure-lightgbm-results.json); [closure report](m2-closure-validation-2026-11-12.md).

## L0 / Trusted bundle and parity

`scripts/dev/export_lightgbm_bundle.py` checks the trusted winning completion/model/calibration hashes and the frozen 31-leaf, 24h, events recipe before exporting. Only this explicit local exporter loads the known trusted research joblib; the server loads native Booster text with fixed filenames, bounded files, exact feature order/dependency checks and an out-of-band manifest SHA. Client parameters cannot supply a file, Python module or model URL. No weights or research rows enter Git or the web image.

Serving manifest SHA256: `21d796add343bf7dbefe56a5e9fe406efce4cca3e072c2f660804d652a6961bf`; calibration SHA256: `11a192c8a192232886a202e0683eb3cf6bae568f1cf483f2fea461df280f0355`. Feature version `metabonet_tabular_v1`: 127 origin features plus one horizon fraction, 288 five-minute history samples, 24 forecast points. Four handcrafted synthetic requests had **zero median/band endpoint error**, within the predeclared 1e-6 mg/dL tolerance. No fit, recalibration or consumed primary/PEDAP row projection occurred. Missing/tampered files, identities and invalid bands fail before a model can serve. Tests use a fake native constructor for rejection boundaries; actual native parity and inference use the frozen real Booster.

## L1 / Separate simulation and context

The existing `m1_fixed_meal_day` default stays intact. The separate `lightgbm_warmup_48h_v1` produces **576 five-minute samples over 2,880 minutes**, origin minute **2,170**, with 710 future minutes withheld. Two real Windows executions matched trajectory/context hashes; real Linux execution also passed. The source exposes only the last 288 pre-origin readings for native inference; it never pads the short demo or reads withheld future values.

`tabular_context.py` preserves CGM/event presence masks and explicit coverage, the six-hour past event window, previous carbohydrate timing and current carbohydrate input. Unknown is distinct from observed zero. Basal **1.2 U/hour over 5 minutes becomes 0.1 U**, and 2 minutes at 1.2 plus 3 minutes at 0.6 gives **0.07 U**; a bolus remains an amount. Duplicate/off-grid samples, insufficient history, unknown units and absent coverage fail closed. Explicit late availability and future records are excluded; missing `available_at` on existing simulator glucose retains its documented immediate-observation behavior. UTC-equivalent display offsets and spring/fall DST boundaries leave features unchanged. Synthetic insulin numeric conversion does not prove physiological equivalence to the training cohort.

## L2 / Registry, API and persistence

The ordinary and portion services share the allowlisted registry and bounded model lock. `GET /api/v1/forecasts/models` is authenticated. `POST /api/v1/forecasts` accepts optional `model_key` (`chronos` default or explicit `lightgbm`); unsupported choices are rejected. Readiness, short history, busy and failed inference return explicit errors, release locks and never silently switch models or persist fake results.

Version 2 responses carry immutable model/bundle/feature/calibration identity, input/history requirements and interval kind. Native bands are **saved symmetric marginal 80% calibration bands**, not native quantiles or individual confidence guarantees. Ordered finite signed lower endpoints are retained through SQL, Python, frontend and exports; glucose history/median checks remain separate. Legacy valid v1 results still read under their original rules. Retry identity includes meal revision and full resolved model identity. Scenarios reuse the frozen baseline source/model; 100% reproduces it, and changing the global default does not change its model.

Forward migration `20261113031950_forecast_model_identity_and_calibrated_intervals.sql` was previewed in a rollback transaction and applied only to the approved cloud development project. New constraints/RPC checks preserve invoker execution and existing service-only grants. There was no reset, data rewrite or new public mutation grant. Post-change advisors showed only the preexisting private no-policy informational findings and leaked-password-protection warning. Separate empty-cloud replay remains deferred; not every malformed RPC/rollback variant has been exercised live.

Actual host/cloud and Linux/API runs covered native forecast, read, retry conflict, owner A/B isolation, child points, 100% and changed portions, signed synthetic storage, legacy reads and immutable export. Native disable/recreate preserves saved results, rejects new native calls and keeps default Chronos working. Broader session revocation/logout/browser variants remain partial. Tests also cover overlapping ordinary/scenario locking and timeout release without persistence.

## L3 / User interface and data contract

Demo and saved-meal flows have an explicit research selector and a separate action to prepare long history. Facts and explanations state that the frozen candidate uses current **carbohydrates only**, with glucose, recorded insulin, prior carbohydrates and masks. Protein/fat/fiber stay visible as nutrition facts. The chart shows the last two hours for readability but discloses all 288 input samples, full model/version and calibrated band semantics. The accessible table preserves signed endpoints. Unknown facts show `Unknown`, and edited recipe candidates clear review and saved forecast eligibility.

Fixture Chromium and jsdom evidence supports rendering/contracts, not Google Chrome/live-provider or human/device acceptance. Owned export was tested against actual container/cloud storage and retains the exact v2 response. Other owners cannot retrieve/create/list/export its forecast/scenario/points. The endpoint accepts no mixed-model scenario override.

## L4 / CPU runtime, sensitivity and rollback

The root Compose API installs frozen Chronos and native refinement dependencies, using two CPU inference threads and one API worker. It mounts only a narrow native bundle **read-only**, alongside the existing reviewed Chronos cache. Research rows and joblib files are not mounted into serving. Normal `.env` native enablement is false; only isolated review project `glycolens-implementation-check` uses a public-value override to enable it at web 3102/API 8102. Restarts do not alter cloud records or regenerate a model.

| Observed local Linux model-only measure | Chronos | Native LightGBM |
|---|---:|---:|
| Cold load, seconds | 10.316 | 0.100 |
| Warm sequential samples | 20 | 20 |
| Warm median, seconds | 0.238 | 0.0020 |
| Warm p95, seconds | 0.467 | 0.0035 |

Across the entire synthetic run, sampled process RSS reached **997,642,240 bytes** (about 951 MiB). The 20,975,349,760-byte denominator is the Docker environment, not a verified VPS allocation; sampled RSS is not a guaranteed true peak. There were 236/236 successful predictions and zero inference failures. Cold/warm model-only observations satisfy the existing local 120s/30s targets, but they do not establish full HTTP p95, multiuser capacity or hosting acceptance. An actual native forecast HTTP example was about 3.3s; one request is not p95. No GPU or external model service is required.

The [frozen sensitivity result](meal-response-sensitivity-2026-11-12.md) found limited carbohydrate response from native LightGBM and **failed meal-response capability for default Chronos**. No stronger accuracy claim follows. Mandatory Chrome/manual and enablement sign-off remain open, so do not enable the ordinary runtime merely because the review stack works. Disabling the option preserves historic native reads and default Chronos; no migration rollback or result deletion is required.
