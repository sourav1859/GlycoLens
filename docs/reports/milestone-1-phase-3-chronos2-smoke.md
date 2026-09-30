# Milestone 1 Phase 3: Chronos-2 Adapter and Real-Data Smoke Test

**Date:** September 29, 2026
**Status:** Implemented and validated
**Scope:** Pinned Chronos-2 CPU inference, contract normalization, and privacy-safe measurement

## Outcome

The official Chronos-2 checkpoint now runs end to end on one real eligible T1D-UOM V1.0.4
CGM context through the common forecast contract. A 24-point, five-minute history produced 24
q10/q50/q90 forecast points. The validated result was finite and non-crossing, and held-out future
CGM remained outside the model request.

This is a technical feasibility result. It is not an accuracy, calibration, personalization, or
clinical-validity result.

## Reproducibility pins

| Component | Pin |
|---|---|
| Python | 3.12.5 |
| `chronos-forecasting` | 2.3.2 |
| `psutil` | 7.2.2 |
| Chronos-2 model | `amazon/chronos-2` |
| Model revision | `29ec3766d36d6f73f0696f85560a422f50e8498c` |
| Dataset | T1D-UOM V1.0.4, release commit `ea52718b41cd27286df46acf87825555d4ec0463` |
| Device | CPU |

The official [Chronos-2 model card](https://huggingface.co/amazon/chronos-2) identifies the model
as Apache-2.0, 120M parameters, F32, and capable of CPU inference. The package is pinned from the
official [`chronos-forecasting` PyPI release](https://pypi.org/project/chronos-forecasting/).

## Implemented controls

- lazy backend imports keep ordinary unit tests offline;
- the exact package and checkpoint revision are pinned;
- only C0/CGM-only requests are accepted in this phase;
- requests with insulin or nutrition covariates fail explicitly rather than being ignored;
- only history values, prediction length, and requested quantiles reach the backend;
- model output is normalized into `ForecastResult` and revalidated;
- backend errors are mapped to safe adapter errors without local paths or row data;
- model downloads require explicit opt-in and remain under ignored `artifacts/models/`;
- benchmark artifacts are constrained to ignored `artifacts/benchmarks/`;
- public output contains no participant ID, source path, timestamps, glucose values, target values,
  or forecast values.

## Test evidence

The new tests cover:

- idempotent load and exact checkpoint/device/cache arguments;
- prediction-before-load and unsupported-device failures;
- exact history-only backend input;
- 24-step q10/q50/q90 normalization and q50 median selection;
- explicit covariate rejection;
- malformed task, variate, horizon, and quantile dimensions;
- crossing-quantile rejection;
- safe load/inference error mapping;
- benchmark summary privacy and artifact-directory containment.

Verification result:

| Check | Result |
|---|---|
| `uv run --all-groups ruff check .` | Passed |
| `uv run --all-groups pytest -q` | Passed: 48 tests |
| Graphify 0.9.69 code-only refresh | Passed: 1,022 nodes, 1,422 edges, 129 communities |
| Real pinned-checkpoint smoke | Passed |
| Finite 24-point output | Passed |
| Non-crossing q10/q50/q90 | Passed |
| Held-out target excluded | Passed |

## Measured smoke result

Environment: AMD Ryzen 7 7840HS, 8 physical/16 logical cores, approximately 27.7 GiB RAM,
Windows, CPU-only PyTorch 2.14.0, and Python 3.12.5.

| Measurement | Result |
|---|---:|
| First load including initial checkpoint download | 28.645649 s |
| Cached checkpoint load | 5.540285 s |
| First forecast after cached load | 56.0379 ms |
| Warm calls | 10 |
| Warm latency p50 | 54.62905 ms |
| Warm latency p95 | 61.2581 ms |
| Warm latency p99 | 61.2581 ms |
| RSS before model load | 206.93 MiB |
| RSS after cached model load | 804.34 MiB |
| Observed inference peak RSS | 810.83 MiB |
| Approximate ignored checkpoint cache | 455.79 MiB |
| Inference errors | 0 |

Raw aggregate records remain local and ignored:

- `artifacts/benchmarks/chronos2-m1-smoke.json`
- `artifacts/benchmarks/chronos2-m1-smoke-cached.json`

The percentile estimates use only ten warm calls and the memory sampler observes process RSS at
50 ms intervals. Values are machine-specific. The one selected window is sufficient for interface
and runtime feasibility only; it cannot support a model-quality conclusion.

## Reproduce

```powershell
uv sync --all-groups --frozen
uv run --all-groups pytest -q
uv run --all-groups python -m research.pipelines.run_chronos2_smoke `
  --dataset-root 'C:\path\to\T1D-UOM-V1.0.4' `
  --allow-model-download `
  --warm-iterations 10
```

## Historical remaining work at Phase 3 completion

The pretrained-model success criterion is now satisfied. At the time of this phase, Milestone 1
still required the FastAPI skeleton, executable Supabase/PostgreSQL migration, one dummy
browser-to-API flow, one py-mgipsim scenario, and the milestone presentation artifact. Phase 4
subsequently completed the FastAPI and browser visualization boundary; see
`milestone-1-phase-4-api-visualization.md`. Phases 5 and 6 subsequently completed the local database
and pinned py-mgipsim scenario. A TimesFM smoke remains desirable if time permits, but it is not
required to prove that at least one pretrained model runs end to end. The presentation and final
closure audit subsequently completed the remaining Milestone 1 artifact; see
`milestone-1-closure-audit.md`.
