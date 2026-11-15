# Milestone 2 closure implementation and validation

**Checkpoint:** November 12, 2026 America/New_York (execution artifacts also carry November 13 UTC timestamps). **Disposition: implementation delivered locally; M2 acceptance remains open.** Baseline `75191e2f654d9e1cbe4a3676d2948131013ec94b`, followed by an uncommitted working tree. Nothing in this checkpoint authorizes a push or hosted release.

## Outcome and phase disposition

The grounded provider/API journeys, model connector, longer simulation, versioned persistence, research selector and CPU Compose integration are implemented. The [58-case ledger](../testing/m2-closure-lightgbm-results.json) records combined-layer acceptance conservatively. A real API pass cannot close a case that also requires Chrome or presenter review. See [LightGBM implementation evidence](lightgbm-app-validation-2026-11-12.md) and [meal-response results](meal-response-sensitivity-2026-11-12.md).

| Phase | Delivered and observed | Remaining acceptance |
|---|---|---|
| C0 | Guarded cloud target, private readiness, independent provider/sensitivity fixtures, bounded calls, near-cap budget rejection | Earlier runs lack a complete execution-time dirty-tree manifest; concurrent/day-cap exhaustion not fully exercised |
| C1 | GTIN checksum/length validation before network/cache; OFF cache and 15/minute/worker cap; grounded USDA/OFF/recipe API paths; unknown nutrition preserved; edits invalidate review | Representative extraction accuracy, all provider failure permutations and Chrome fallback review |
| C2 | Real providers -> reviewed grams -> cloud save -> real simulator/default Chronos -> owned persisted read; matrix executed | Actual Chrome journeys, revoked-session variants and manual accessibility; Chronos meal-response capability **failed** |
| C3 | Requirements/results, architecture and Markdown presentation claims reconciled | Native v4 deck review, actual presenter rehearsal and owner acceptance |
| L0/L1 | Native frozen export/parity, calibrated serving, separate 48h protocol, feature/mask/unit/availability tests | Biological equivalence and patient accuracy are not established by synthetic compatibility |
| L2 | Shared registry, authenticated capabilities, explicit model choice, owner checks, versioned signed bands, immutable retry/scenario identity | Exhaustive malformed-RPC rollback/revocation variants; separate scratch replay deferred |
| L3 | Explicit selector, long-history action, model/interval provenance, chart table, owned export | Chrome/manual responsive, keyboard/zoom and cross-tab logout acceptance |
| L4 | Actual CPU Compose/cloud/native journey, measured model-only timings, disable/restart recovery | Full Chrome acceptance and release resource/capacity evidence; ordinary enablement stays off |

## Actual validation

- Final offline CI selection: **201 passed, 1 skipped** with network denied. The skip is the explicit real two-run simulator opt-in, exercised separately rather than relabeled as an offline pass. Earlier broad Python run: **284 passed, 2 skipped**, before the final four concurrency/DST additions; do not add these overlapping counts together.
- Frontend: **29 jsdom/unit tests**, lint, TypeScript and production build. Three new recipe name/quantity/unit edit cases first reproduced stale confirmation, then passed after invalidating review and saved-result eligibility.
- Earlier Chromium fixture browser run: **28 passed, 2 skipped**, including selector/calibrated signed table and width-overflow assertions at 320, 390, 768, 1024, 1440 and 1920 px. These use synthetic intercepted responses, predate the last review-state fix, and are neither Google Chrome nor real-provider/browser acceptance. The last edit is covered by jsdom and build checks. No physical-device pass is claimed.
- Real host/cloud integration: **103 guarded requests**, two tagged disposable owners, native forecast/read/retry, changed-model idempotency rejection, owner-B denial, child-point RLS, same-model scenarios, synthetic signed SQL endpoint and legacy v1 compatibility. Run `gl_62c1a708255e40b5a65c08bb`; scoped cleanup completed.
- Real provider journeys recheck: **86 requests**, two USDA reads and one synthetic OpenAI call; USDA, packaged-product and recipe inputs completed reviewed save/default Chronos/owned reload through the API. OFF facts were cached in this run; an earlier bounded uncached OFF lookup was separately executed. Run artifacts retain timestamped provider observations. No camera or real Chrome hop is implied.
- Final actual container/export/recovery run: two tagged owners, **10 directly counted host cloud requests**, at most 18 local HTTP calls with a conservative remote-call reserve (10/call plus 32 for two exports); total guard 250. Owned export retains the exact v2 response/provenance/intervals. Owner B cannot read/create/list/export A's forecast or scenario. Disabling and recreating the API retains existing native results, rejects new native requests without fallback, and permits default Chronos. Option restored only in the isolated review project. Run `gl_cd1f5028aae8428cab1d171d`; cleanup completed. Remote calls made inside the container are conservatively budgeted, not directly instrumented.

Reproducible runners (cloud/paid opt-ins are deliberate, not ordinary CI requirements):

```powershell
uv run --no-sync python -m pytest -p scripts.quality.offline_pytest backend/tests tests/quality tests/contract tests/database tests/research/models/test_forecast_adapters.py tests/research/test_pymgipsim.py -q
pnpm.cmd --dir frontend check
uv run --no-sync python -m scripts.quality.check_api_contract
uv run --no-sync python -m scripts.quality.check_public_files
uv run --no-sync python -m scripts.quality.validate_skills
# Scoped live tests: review target, runtime, fixtures and remaining budget first.
uv run --no-sync python -m scripts.dev.lightgbm_integration --allow-cloud --output .cache/lightgbm-cloud-validation.json
uv run --no-sync python -m scripts.dev.container_model_integration --allow-cloud --output .cache/lightgbm-container-export-validation.json
uv run --no-sync python -m scripts.dev.provider_journeys --allow-cloud --allow-paid --output .cache/provider-journeys-new-run.json
```

Do not rerun paid/provider tests merely to reproduce this report. Raw traces, synthetic rows, per-request inputs, fixture-owner IDs and model files remain ignored. Public aggregate evidence and source/lockfile/migration digests are in [the checkpoint manifest](m2-implementation-manifest-2026-11-12.json). That is a **final review manifest**, not a retroactively captured build revision for every earlier run; exact execution-revision assurance remains partial.

## Provider compatibility and cost

OFF v2 is deliberately retained and live-tested for the existing per-100g fact shape. Current v3.5 nutrition representations need a separately tested adapter migration; the application does not guess compatibility. Invalid GTINs never call the provider; uncached reads have a per-worker 15/minute cap, with explicit failures and caching. A single API worker is the current Compose contract. This is not a distributed quota guarantee. Sources remain community/provider facts requiring user review; recipe parsing supplies no authoritative nutrient values.

The total paid-test allowance remains **USD 5**, including earlier work. Prior known estimate was USD 0.00763580. One successful new extraction used 151 input and 79 output tokens, estimated USD 0.0000546; known cumulative estimate is **USD 0.00769040**. An earlier transport-instrumentation failure occurred after a request and could not recover usage: retain **USD 0.01 unresolved reserve**, giving USD 0.01769040 known estimate plus reserve. Do not treat that request as free. The cloud guard conservatively holds USD 0.02763580, leaving USD 4.97236420 of reservation headroom. These are token estimates/reservations, not reconciled billing. A rollback-only near-cap USD 4.995 test rejected a new reservation before an LLM call and restored the prior counter. Concurrent/day-owner exhaustion still has incomplete combined evidence.

## Safety, acceptance and next human action

Chronos receives recorded meal channels but was effectively invariant in this synthetic experiment: the UI/help explicitly discloses the failed meal-response capability. LightGBM uses current carbohydrates only and has limited synthetic sensitivity. Neither model has new matching-outcome meal accuracy evidence. No training, calibration refit, reserved-cohort access, model default change or treatment/dosing feature was introduced.

Use the isolated review app at `http://127.0.0.1:3102/demo` while its Compose project is running. Chronos is selected initially; explicitly select LightGBM and start the 48-hour research simulation to review it. The ordinary ignored `.env` keeps native enablement **false**; only the non-secret review override enables it. No new credentials are needed. Public catalog, SMTP/domain/VPS, untouched matching-outcome accuracy and deferred scratch restore remain separate gates. Physical-camera testing stays user-deferred.

**Computer Use ended:** installed Chrome automation failed with EACCES, the browser-control host was unavailable, and native browser control then stopped because it could not determine the current Windows browser URL confidently enough to enforce policy. No alternative UI automation was attempted after that stop. Human Chrome review is required for the pending browser cases. The native PowerPoint was not changed or rehearsed; the presenter must review the updated Markdown claims, render the deck and record the 7–8 minute rehearsal. M2 and normal native-option enablement cannot be signed off from this checkpoint alone.
