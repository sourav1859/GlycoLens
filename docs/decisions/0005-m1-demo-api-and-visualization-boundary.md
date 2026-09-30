# ADR 0005: Milestone 1 demo API and visualization boundary

- **Status:** Accepted
- **Date:** September 29, 2026

## Context

Milestone 1 must prove that the Next.js application can consume and visualize a forecast through
FastAPI. Loading the 120M-parameter Chronos-2 checkpoint on every page request would add avoidable
latency and memory requirements, while exposing a selected real-data window through a public demo
route would create privacy and interpretation risks.

## Decision

- Implement `GET /api/v1/forecasts/demo` as a deterministic synthetic, read-only endpoint.
- Construct the fixture through the canonical `ForecastRequest` and `ForecastResult` boundary,
  then map it to Pydantic transport schemas.
- Return only relative minutes, glucose values, model identity, context configuration, summaries,
  and an explicit safety notice. Do not return participant IDs, user IDs, source paths, or absolute
  timestamps.
- Keep the pinned Chronos-2 real-data plot as an explicit offline research command whose outputs
  remain under ignored `artifacts/forecasts/`.
- Render observed history, median/q50, and a q10-q90 interval; do not label interval width as
  clinical confidence.
- Add real authenticated forecast endpoints later without changing the canonical research
  adapter contract.

## Alternatives considered

### Serve the real Chronos-2 model directly from the demo route

Rejected for Milestone 1 because it couples page loading to checkpoint availability, adds roughly
800 MiB observed process memory, and unnecessarily places a real-data inference path behind a
public endpoint.

### Embed static chart values only in the frontend

Rejected because it would not test the FastAPI transport boundary or CORS configuration.

### Return absolute timestamps and a dataset participant key

Rejected because neither is needed to validate the chart and both increase disclosure risk.

## Consequences

- The UI/API integration is fast, deterministic, offline-testable, and safe to demonstrate.
- Real-model feasibility and application integration are validated separately and must not be
  confused with a clinical or accuracy result.
- A later production forecast route still needs authentication, authorization, persistence,
  observability, stale-data handling, and model-serving lifecycle design.

## Recovery and change conditions

Replace the synthetic route in product workflows only after the authenticated forecast contract,
database/RLS boundary, model-serving lifecycle, safe error behavior, and end-to-end tests are in
place. Keep the synthetic route for demonstrations or contract testing only if it remains clearly
labeled and isolated from user data.
