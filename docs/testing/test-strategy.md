# GlycoLens Test Strategy

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

## Final Milestone 1 closure gate

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
