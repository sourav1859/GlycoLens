# ADR 0003: Forecast contract and leakage boundary

- **Status:** Accepted
- **Date:** September 29, 2026

## Context

GlycoLens must compare persistence, Chronos-2, TimesFM, and possible later models on the same
meal-centered task. Passing raw arrays or complete dataset windows directly to model code would
make shapes ambiguous, couple adapters to T1D-UOM, and create a high-risk path for held-out future
CGM to leak into inference.

## Decision

- Use immutable standard-library dataclasses as the canonical research forecast contract under
  `research/models/adapters/`.
- `ForecastRequest` contains only target history, past covariates, known-at-forecast covariates,
  horizon, frequency, and requested quantiles.
- `ForecastTarget` contains held-out future truth and is never accepted by an adapter.
- `ForecastExample` pairs request and target only for evaluation and validates their grids.
- Every adapter implements `load()` and `predict(request)` and returns a validated
  `ForecastResult` with model identity, context bounds, future timestamps, median, quantiles,
  latency, and non-sensitive metadata.
- Fail closed on non-finite values, invalid shapes, irregular time grids, mixed timestamp
  awareness, future values in past covariates, ambiguous duplicate covariate names, and crossing
  quantiles.
- Implement persistence as last observation carried forward. Its q10, q50, and q90 are identical
  because it is deterministic; this does not represent calibrated uncertainty.
- Convert T1D-UOM windows outside adapters. The converter supports CGM-only, CGM+insulin, and
  CGM+insulin+nutrition contexts and excludes participant identifiers from requests.

## Alternatives considered

### Pass `MealWindow` directly to each adapter

Rejected because it exposes future target data to model code and couples every model to one
dataset representation.

### Use model-specific request objects

Rejected because experiments could silently use different temporal boundaries and would require
duplicated API/backend integration logic.

### Add Pydantic to the research contract now

Deferred. Frozen dataclasses provide the required validation without adding a runtime dependency.
The FastAPI phase may introduce Pydantic transport schemas that map to this canonical contract.

## Consequences

- Leakage prevention becomes structural and testable.
- Dataset converters and model adapters can evolve independently.
- The backend should delegate to this contract rather than create a competing forecast interface.
- Irregular raw model outputs must be normalized and validated before becoming a result.
- Adapter latency is diagnostic metadata; benchmark conclusions require the separate measurement
  protocol and repeated runs.

## Recovery and change conditions

The contract can gain optional fields through additive changes. Breaking changes require a new
ADR, migration of all adapters and converters, and contract-test updates. If array-copy overhead
becomes material during measured batch evaluation, internal model-specific arrays may be used
behind the adapter while preserving the external immutable contract.
