# ADR 0004: Chronos-2 Milestone 1 inference boundary

- **Status:** Accepted
- **Date:** September 29, 2026

## Context

Milestone 1 requires at least one pretrained model to run end to end on a real, leakage-safe
T1D-UOM context. Chronos-2 supports univariate, multivariate, and covariate-informed inference,
but implementing every context mode at once would combine checkpoint integration with unresolved
model-specific covariate semantics.

## Decision

- Pin `chronos-forecasting==2.3.2` and Hugging Face model `amazon/chronos-2` at immutable revision
  `29ec3766d36d6f73f0696f85560a422f50e8498c`.
- Validate Phase 3 on CPU because the development machine has no NVIDIA GPU and the official
  model supports CPU inference.
- Implement the first adapter as univariate C0 (CGM-only). Reject requests containing past or
  known covariates instead of silently discarding them.
- Keep future CGM in `ForecastTarget`; pass only `ForecastRequest.target_history` to Chronos-2.
- Normalize q10/q50/q90 output into the common `ForecastResult` and fail closed on malformed
  shapes, non-finite values, or crossing quantiles.
- Require an explicit `--allow-model-download` flag. Store checkpoints under ignored
  `artifacts/models/` and aggregate benchmark records under ignored `artifacts/benchmarks/`.
- Keep normal unit tests offline by injecting a fake backend. The real-checkpoint smoke remains an
  explicit local command.

## Alternatives considered

### Implement the pandas covariate API immediately

Deferred because C1/C3 need explicit model-specific alignment and ablation validation. Silent
fallback to univariate behavior would invalidate the scientific comparison.

### Track the latest model revision

Rejected because model updates could change results without a repository change.

### Commit model weights or raw forecasts

Rejected because weights are large and row-level forecasts can expose health data. Reproducible
identifiers, aggregate measurements, and ignored local artifacts are sufficient for this phase.

## Consequences

- Milestone 1 now has a reproducible pretrained-model feasibility result.
- Chronos-2 C0 can be compared with persistence through the same contract.
- The smoke result does not establish forecast accuracy, calibration, clinical validity, or the
  value of insulin/nutrition context.
- C1/C3 Chronos-2 support requires a later decision and tests before it can be claimed.

## Recovery and change conditions

Update the pinned package or checkpoint only with a lockfile refresh, adapter contract tests, a
new real-data smoke record, and documentation of any changed output or resource behavior. Enable
GPU or covariate-aware paths only after equivalent validation and explicit experiment design.
