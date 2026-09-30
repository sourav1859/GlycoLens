# Milestone 1 Phase 4: FastAPI and Forecast Visualization

**Date:** September 29, 2026
**Status:** Implemented and validated
**Scope:** Typed demo API, mobile-first forecast chart, and local real-model research plot

## Outcome

GlycoLens now has a working application vertical slice for the Milestone 1 forecast result. A
Next.js client fetches a typed FastAPI response and renders 24 observed five-minute CGM points, a
24-point median forecast, a shaded q10-q90 interval, and 30/60/120-minute summaries. Loading,
failure, and retry states are implemented.

The public demonstration route uses deterministic synthetic data and never loads the model. A
separate research command successfully ran the pinned Chronos-2 checkpoint on one eligible local
T1D-UOM V1.0.4 C0 window and saved the corresponding graph under ignored artifacts.

This phase proves transport and visualization feasibility. It does not prove forecast accuracy,
calibration, personalization, or clinical validity.

## Implemented boundary

```text
Canonical ForecastRequest / ForecastResult
                |
                v
       Pydantic transport mapper
                |
                v
 GET /api/v1/forecasts/demo
                |
                v
 Next.js runtime validator and SVG chart
```

- `GET /health` exposes a minimal service-health response.
- `GET /api/v1/forecasts/demo` returns an identifier-free `synthetic_demo` payload.
- Pydantic validates finite values, ordered time grids, q10 <= q50 <= q90, and summary agreement.
- The TypeScript client repeats the critical response checks before rendering.
- CORS accepts only configured local frontend origins and rejects wildcard configuration.
- The chart has an accessible name and description, visible legend, summary cards, and safety text.
- Chronos model loading stays outside the page-request path.

## Visualization behavior

The browser view contains:

- observed CGM history through relative minute 0;
- forecast points from relative minute 5 through 120;
- the median/q50 trajectory;
- a shaded q10-q90 interval, described as uncertainty rather than confidence;
- exact 30-, 60-, and 120-minute forecast values; and
- a notice that the output is uncertain, not clinical guidance, and not for insulin dosing.

The local research plot uses the same essential visual vocabulary. Its default output is
`artifacts/forecasts/chronos2-example.png`. That directory is ignored by Git. The default graph
omits held-out target CGM, participant identifiers, source paths, and absolute timestamps.

## Test evidence

| Check | Result |
|---|---|
| Ruff formatting | Passed: 72 files formatted |
| Ruff lint | Passed |
| Full Python suite | Passed: 59 tests |
| Frontend lint | Passed with zero warnings |
| Frontend behavior suite | Passed: 3 files, 5 tests |
| TypeScript type check | Passed |
| Next.js production build | Passed |
| Live FastAPI request | HTTP 200; 24 history and 24 forecast points |
| Live CORS header | `http://localhost:3000` allowed |
| Live Next.js request | HTTP 200 |
| Real pinned Chronos-2 plot | Passed; 24 history and 24 forecast points |
| Plot privacy summary | Relative minutes only; no participant ID or absolute timestamp |
| Held-out target default | Excluded |
| Graphify 0.9.69 code-only refresh | Passed: 1,170 nodes, 1,700 edges, 146 communities |

Backend tests cover health, OpenAPI, transport shape, summary consistency, quantile crossing,
privacy-field absence, and allowed/denied origins. Frontend tests cover fetch validation, malformed
responses, loading, errors, retries, the SVG chart, uncertainty band, summaries, and safety notice.
Plot tests cover PNG creation, path containment, mismatched time grids, and privacy metadata.

The validation environment did not expose a controllable browser surface, so no browser screenshot
test was recorded. The running frontend and backend endpoints, live CORS response, client fetch
tests, component behavior tests, type check, and production build collectively validate the M1
dummy application boundary. A full Playwright meal-to-forecast flow remains later work.

## Reproduce

```powershell
uv sync --all-groups --frozen
uv run ruff format --check backend research tests scripts
uv run ruff check .
uv run pytest -q

pnpm install --frozen-lockfile
pnpm frontend:lint
pnpm frontend:test
pnpm frontend:typecheck
pnpm frontend:build
```

Run the local demonstration:

```powershell
uv run uvicorn backend.app.main:app --reload
pnpm frontend:dev
```

Render one local real-model graph after configuring `GLYCOLENS_T1D_UOM_ROOT`:

```powershell
uv run --all-groups python -m research.pipelines.render_chronos2_forecast `
  --allow-model-download
```

## Historical remaining work at Phase 4 completion

Phase 4 closed the FastAPI skeleton, forecast UI, and dummy application-boundary work. At the time,
Milestone 1 still required:

- an executable PostgreSQL/Supabase migration matching the documented schema;
- one validated py-mgipsim virtual scenario; and
- the milestone presentation artifact.

Phase 5 subsequently completed the executable local PostgreSQL/Supabase migration; see
`milestone-1-phase-5-local-database.md`.
Phase 6 subsequently completed the pinned deterministic py-mgipsim scenario; see
`milestone-1-phase-6-pymgipsim-scenario.md`.
The RIT-branded presentation and final closure audit subsequently completed the last Milestone 1
artifact; see `milestone-1-closure-audit.md`.

TimesFM remains an optional comparison rather than a closure requirement because the required
pretrained-model feasibility criterion is already satisfied by Chronos-2.
