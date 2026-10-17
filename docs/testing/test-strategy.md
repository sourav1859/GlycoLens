# GlycoLens Test Strategy

## Milestone 2 executable checks

The offline suite covers split purging, immutable input/target separation, C2 membership,
kind-separated basal semantics, metrics/failure accounting, actual model input delivery,
recipe structured extraction, provider basis/missingness, app origin boundaries and owner
validation. Real local Supabase tests cover atomicity, retries, source snapshots and
retrieval outcome chronology. Real simulator/model execution remains an explicit opt-in.

`python -m scripts.dev.check_m2_application --allow-live-local` tests actual local Auth,
simulator execution, meal save/retry, Chronos C3, persisted read/retry, cross-user denial
and numeric history. Playwright tests separately identify fixture input contracts and
opt-in real desktop/mobile flows; both verify no page-wide horizontal overflow.
Physical camera capture and live USDA/recipe-provider tests are still outstanding.
See the M2 evidence ledger; do not claim mocked providers as live integration passes.

## Principles

- Derive tests from requirements, risks, and safety boundaries before enumerating cases.
- Use the lowest layer that proves the behavior without duplicating the same assertion everywhere.
- Keep fixtures deterministic, synthetic, or demonstrably de-identified.
- Test safe degradation for missing, stale, delayed, malformed, and partial data.

## Planned layers

| Layer | Primary responsibility |
|---|---|
| Unit/property | Calculations, transformations, boundaries, invariants, and metric implementations. |
| Integration | Database, RLS, provider adapters, caching, retries, and partial failures. |
| Contract/API | Schemas, authorization, idempotency, malformed payloads, and error contracts. |
| Playwright/end-to-end | Mobile meal-to-forecast flow, keyboard use, accessibility, slow network, fallback, and safety messaging. |
| Security | Secrets, server/client boundaries, input validation, authorization, abuse controls, and privacy-safe logging. |
| Performance | p50/p95/p99 latency, memory, throughput, failure rate, and reproducibility. |
| Scientific evaluation | Leakage controls, subject/time splits, event boundaries, baselines, metrics, uncertainty, and unusable-run accounting. |

## Required risk coverage

Cover happy paths, boundaries, invalid inputs, missing data, time zones and DST, concurrency, retries, timeouts, external API degradation, authorization, privacy, accessibility, recovery, and stale CGM behavior where relevant.

## Executable Phase 1 checks

The repository now has checked-in Python and frontend runners. From the repository root:

```powershell
uv sync --frozen
uv run ruff check .
uv run ruff format --check backend research tests scripts
uv run pytest -q
uv run python -m compileall -q backend research tests scripts
uv run python scripts/quality/validate_skills.py
uv run python scripts/quality/validate_codex_config.py
uv run pytest -q tests/quality/test_validate_codex_config.py

pnpm install --frozen-lockfile
pnpm frontend:lint
pnpm frontend:test
pnpm frontend:typecheck
pnpm frontend:build
```

The frontend has executable Vitest/Testing Library coverage for response validation, loading,
failure, retry, chart rendering, interval rendering, summary values, and safety messaging.
Playwright remains required when the complete meal-to-forecast workflow is implemented; component
tests, strict type checking, and a production build are not substitutes for that later end-to-end
coverage.

## Executable Phase 2 contract checks

```powershell
uv run pytest -q tests/research/models/test_forecast_adapters.py
uv run python -m research.pipelines.run_persistence_baseline
```

The Phase 2 suite covers adapter lifecycle, deterministic persistence behavior, timestamp grids,
input shapes, finite values, quantile ordering, defensive copying, context ablation, malformed
meal windows, future-event exclusion, and privacy-safe smoke output. The real-data command uses a
local ignored dataset and prints aggregate evidence only.

## Executable Phase 3 Chronos-2 checks

```powershell
uv run --all-groups pytest -q tests/research/models/test_chronos2_adapter.py
uv run --all-groups pytest -q tests/research/test_chronos2_smoke.py
uv run --all-groups python -m research.pipelines.run_chronos2_smoke `
  --allow-model-download --warm-iterations 10
```

Fake-backend tests validate the adapter offline. They cover checkpoint pinning, lifecycle,
history-only input, output shape, q50/median consistency, covariate rejection, malformed/crossing
outputs, safe errors, privacy-safe summaries, and ignored-artifact containment. Only the last
command accesses the real checkpoint, and it requires explicit download consent.

## Executable Phase 4 API and visualization checks

```powershell
uv run pytest -q backend/tests tests/research/test_forecast_plot.py
pnpm frontend:test
pnpm frontend:lint
pnpm frontend:typecheck
pnpm frontend:build
uv run --all-groups python -m research.pipelines.render_chronos2_forecast `
  --allow-model-download
```

Backend contract tests cover schema shape, summary consistency, quantile ordering, privacy fields,
OpenAPI generation, and allowed/denied CORS origins. Frontend tests cover runtime response
validation, loading/error/retry behavior, an accessible SVG chart, the q10-q90 band, forecast
summaries, and safety text. Plot tests cover PNG output, grid mismatch rejection, privacy metadata,
and ignored-directory containment. The real plot command is a separate local validation using one
eligible C0 window; it is not an accuracy result.

## Executable Phase 5 local database checks

Initialize an ignored machine-local Supabase configuration once, then use the wrapper that
suppresses generated connection details:

```powershell
supabase init
./scripts/database/Test-LocalSupabase.ps1
uv run pytest -q tests/database
```

The wrapper starts the local stack, rebuilds the database from zero, applies the migration and
synthetic seed, runs schema lint, and executes pgTAP. Coverage includes all required tables,
pgvector, RLS enablement, owner access, cross-user read/write denial, anonymous denial, invalid
glucose rejection, and crossing-quantile rejection. Static pytest coverage rejects committed
connection strings, local endpoints, token-shaped values, and credential assignments.

## Executable Phase 6 py-mgipsim checks

Install the exact source commit and isolated locked dependencies, then run the fixed scenario:

```powershell
./scripts/simulation/Install-PyMgipsim.ps1
uv run python -m research.pipelines.run_pymgipsim_scenario --allow-upstream-execution
```

Ordinary tests validate the project-owned protocol and result contract without external execution:

```powershell
uv run pytest -q tests/research/test_pymgipsim.py
```

Run the explicit real integration test only after the installer succeeds:

```powershell
$env:GLYCOLENS_RUN_PYMGIPSIM = "1"
uv run pytest -q tests/research/test_pymgipsim.py
Remove-Item Env:GLYCOLENS_RUN_PYMGIPSIM
```

Coverage includes fixed-protocol enforcement, exact upstream provenance, opt-in execution,
five-minute grid and finite-value validation, aggregate consistency, forbidden privacy/clinical
fields, real simulator execution, and byte-for-byte reproducibility across two runs.

## October 16 model refinement checks

Synthetic tests cover inclusive +/-10, outlier/tail and whole-curve semantics,
participant versus pooled weighting, failures in attempted-event denominators,
unaltered original identities and purged calibration cuts, origin-only features,
future target/meal invariance, small-head fit/calibration, immutable selection,
CGM-only backbone cache identity, duplicate/conflicting external rows and archive
path traversal. Run `pytest -q`; the actual CPU study is separate from unit tests.
The execution report records real cohorts, candidate predictions, original-result
reproduction and post-freeze external testing. No app/database/frontend behavior
changed in this refinement cycle; existing full Python regression remains required.

## MetaboNet Phase 2 preparation checks

Run `pytest -q tests/research/test_metabonet_preparation.py`. Six tests cover causal
history fill and masks, target separation, native IU/fractional grams, shifted relative
cadence, nearby meals, stable origin hashes and source-qualified subject splits.
The DuckDB integration fixture deliberately omits all outcome columns from test and
includes a reserved-source poison value; preparation must still pass without reading
either. Corrupted protocol/split metadata/window artifacts fail verification, reserved
test iteration is blocked, completed output cannot be overwritten, and injected
integrity failure cannot publish a completed directory.

The October 16 real build is separate evidence: audited input hashes, frozen source
ZIP/protocol, verified development/test roles, per-variant counts/exclusions and a
real reader/contract check. All four histories share 1,509 eligible validation events;
no inference or fitting occurred. Final Python suite: 117 passed, one opt-in real
simulator test skipped; one upstream TestClient deprecation warning. Research subset:
92 passed, the same one skipped. See the
[handoff](../tooling/metabonet-phase2-handoff-2026-10-16.md). No frontend/database
behavior changed, so their integration checks were not rerun for this preparation.

## MetaboNet Phase 3 inference checks

Five synthetic tests in `tests/research/test_metabonet_inference.py` cover matching
validation-only IDs/targets, native-unit context/masks without total-insulin duplication,
request fingerprints independent of future truth/identity, failure persistence without
retry, corrupted/mismatched progress, complete-cohort selection despite another
candidate's failures, the exact 10% improvement boundary, frozen execution and replay
protection. Research suite: 97 passed, one opt-in simulator skip. Full Python suite:
122 passed, the same skip and one upstream TestClient deprecation warning.

Actual CPU inference is distinct evidence, under a pre-execution source/configuration
freeze. The aggregate report includes matched/attempted/success denominators, failures,
native uncertainty/tails and source subgroups. No future values enter adapter requests.
See [protocol 13](../planning/GlycoLens_13_MetaboNet_Frozen_Inference.md) and the
[handoff](../tooling/metabonet-phase3-handoff-2026-10-16.md). App/database/frontend
checks are not repeated for this offline research-only orchestration.

## MetaboNet Phase 4 direct-training checks

`tests/research/test_metabonet_models.py` adds 12 synthetic checks for native units,
fractional carbs, missing versus recorded-zero masks, request-only/identity-free
features, training-only readers, deterministic subject folds/equal weights, both
adapter lifecycles, immutable prediction state/reloads, failure-ineligible CV ranking,
actual fit/held-subject separation, verified CV resume, rejection of changed model
bytes before deserialization, truthful training verification flags, native-float
batch validation and a scoring-repair guard rejecting any additional code change.

The numeric regression was confirmed failing before its fix. All 12 focused tests
and the full 134-test Python suite pass; one opt-in simulator test is skipped and one
existing TestClient dependency warning remains. Ruff lint/format passed for changed
Python files. Research-only changes do not require frontend/database/live simulator
checks to be repeated.

Real evidence: 32 candidates/96 subject-fold fits, two final refits, same 1,509-event
validation comparisons against seven verified saved baselines. Independent checks
reproduce every CV/validation macro score, verify all row/source/model hashes,
check public/batch/saved prediction equivalence and unchanged model state, and
confirm prior prepared outputs/checkpoint files unchanged. All OOF predictions and
saved Ridge scaler/coefficients are finite despite logged scaling warnings. A
scoring-only completion archive preserves original fits/choices and the zero-row
interruption evidence. No calibration/reserved outcomes read. See
[protocol 14](../planning/GlycoLens_14_MetaboNet_Direct_Models.md),
[report](../reports/metabonet-phase4-training-2026-10-16.md) and
[handoff](../tooling/metabonet-phase4-handoff-2026-10-16.md).

## MetaboNet Phase 5 correction checks

Ten focused synthetic tests cover exact C2 request equivalence/label isolation, training-only roles, failure persistence without retry/tamper rejection, both correction families, no foundation serialization, explicit backbone attachment and latency metadata, train-fold baseline alignment/subject separation, native-float validation/reload/corrupt-byte checks, failed-backbone denominators and the exact 5% gate with point-winner/advancement separation.

Full Python suite:144 passed, one opt-in simulator skip, one existing TestClient dependency warning. Ruff lint/format pass across seven affected Python files. Real frozen-backbone inference, six CV configurations/ 18 fold fits, four refits and all 13 same-event validation comparisons are separate evidence. Independent checks reproduce all macro scores and public/batch/saved predictions without changing model state, and verify input/source/row/model hashes plus original artifacts/checkpoints. No calibration/reserved outcomes read. See [protocol 15](../planning/GlycoLens_15_MetaboNet_Chronos_Correction.md), [report](../reports/metabonet-phase5-correction-2026-10-16.md) and [handoff](../tooling/metabonet-phase5-handoff-2026-10-16.md).

## Historical Milestone 1 closure gate

The September 29, 2026 closure audit reran the complete offline suite and the explicitly opted-in
real feasibility checks:

- Ruff format/lint, bytecode compilation, and all nine repository-skill validators;
- 73 passing Python tests with the real simulator test skipped by default;
- 11 passing py-mgipsim tests with real upstream execution enabled;
- five passing frontend behavior tests plus ESLint, TypeScript, and production build;
- a clean local database reset, schema lint, and all 20 pgTAP tests using Supabase CLI 2.118.0;
- the pinned Chronos-2 CPU smoke on one real eligible C0 window;
- the full privacy-safe T1D-UOM audit and 927-window eligibility scan; and
- PowerPoint package, layout, font, native chart/table, re-import, privacy, and visual checks.

See [`milestone-1-closure-audit.md`](../reports/milestone-1-closure-audit.md) for the exact results,
claim boundaries, residual limitations, and Milestone 2 entry plan.

## MetaboNet Phase 6 independent-evaluation verification

Eleven synthetic tests in `tests/research/test_metabonet_independent.py` cover
calibration-only roles, value-independent participant representatives, exact finite
ranks, separate marginal/curve radii, immutable wrapper/point state, attempted failure
yields, corruption/replay, missing-gate projection denial and publisher-file boundaries.
The preflight full Python suite passed 155 tests, one opt-in simulator skip and one
existing TestClient dependency warning. No app/database/frontend behavior changed.

Actual calibration was frozen before reserved outcome projection. All 17,130 test
prediction records and the original point models remained intact. Independent NumPy
checks reproduced macro accuracy, pooled tails, band bounds/coverage, 19 subgroup
counts/MAEs, finite calibration ranks and 18 public/batch/wrapper prediction samples.
Source/input/row/model/prior/checkpoint hashes and both completion manifests passed.
Actual loaded numerical pools reported two threads. Test-data access is truthfully
recorded as consumed; successful point gates do not establish clinical or pediatric
uncertainty reliability. See [Phase 6 traceability and evidence](../tooling/metabonet-phase6-handoff-2026-10-16.md).
