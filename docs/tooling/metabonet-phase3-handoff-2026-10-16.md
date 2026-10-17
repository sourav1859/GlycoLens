# MetaboNet Phase 3 handoff - October 16, 2026

## Goal and accepted decisions

Execute the approved frozen-inference comparison under
[protocol 13](../planning/GlycoLens_13_MetaboNet_Frozen_Inference.md). Use the 1,509
matched validation events and the fixed five-minute availability assumption. Seven
runs: persistence, C0 at 2/6/12/24 hours, C1/C2 at six hours. Keep cached Chronos
weights/adapter frozen. No training, calibration, reserved test access, app change
or external data transfer. Preserve Phase 2 and initial UOM/AZT1D evidence.

## Current repository state

**Phase 3 complete; Phase 4 direct-model training is next.** Seven runs attempted
1,509 events each, 48 identities, 10,563 total attempts (9,054 real Chronos calls).
The all-option common-success population is 1,487 events. Inference/aggregation:
28.86 minutes, excluding validation loading/model initialization. CPU with two Torch
threads, offline cached weights; no model batch speedup claimed.

| Failure-free option | Macro MAE mg/dL | Macro within +/-10 |
|---|---:|---:|
| Persistence | 37.12 | 25.47% |
| C2, six hours | 37.61 | 25.98% |
| C0, two hours | 42.52 | 23.52% |

Persistence wins; the improvement gate fails. Frozen history decision: two hours,
because it is the only failure-free C0, not the lowest-error C0 among valid outputs.
C0 six/twelve/24 hours failed 2/11/15 times; C1 failed once, C2 zero. All saved causes
are ForecastValidationError wrapped by ModelInferenceError. Exact invalid raw
quantiles were not saved or rerun; cause metadata cannot locate a crossing/nonfinite
point individually. No failure was silently repaired or retried.

On the 1,487 common-success events, 24-hour C0 has MAE 33.50 versus persistence 36.84.
Longer history therefore has useful conditional point-accuracy signal. Small trained
models need not inherit the native quantile failures; history features deserve
training-only subject-CV assessment in the next protocol. Preserve the frozen two-hour
baseline decision instead of changing it after outcomes. Native nominal 80% bands
covered only 49.42-64.08%; negative medians occurred. The +/-10 aspiration remains unmet.
The C2 paired MAE delta is +0.49, descriptive 95% interval [-0.95,2.03]; there is no
clear benefit from that fixed context representation over persistence here.

Saved output is ignored `artifacts/evaluation-results/metabonet-phase3-v1/`, with
execution/source ZIP, initial protocol, package and checkpoint hashes, checksummed
attempt rows, aggregate summary, history decision and completed-artifact hashes.
The working planning ledger was updated after execution; its pre-outcome snapshot
remains unchanged in the ZIP. No Phase 2 or previous experiment artifacts changed.

## Files changed

- `research/pipelines/run_metabonet_inference.py`: validation matching, context
  selection, request-only fingerprints, checksummed progress/resume, failure-aware
  ranking and frozen artifacts/provenance.
- `research/pipelines/report_metabonet_inference.py`: verified aggregate report.
- `tests/research/test_metabonet_inference.py`: synthetic scientific acceptance tests.
- Planning document 13, affected planning status, research/navigation and this handoff.

## Requirement traceability

| Requirement / risk | Scenario / layer / fixture | Evidence |
|---|---|---|
| Reserved outcomes influence selection | Validation-only reader spy; no raw data access in runner | Synthetic match test plus actual roles in frozen execution |
| Unfair history comparison | Identical IDs/origins/current glucose/targets; reject altered future target | Synthetic matching test and real common-cohort manifest |
| Wrong insulin units or double counting | C1 contains amount/mask channels; total omitted; C2 fractional carbs | Synthetic context test; unchanged common adapter alignment |
| Future leakage / cache identity | Future truth and identity changes leave request hash unchanged; past/context changes alter hash | Synthetic fingerprint test |
| Silent retry or output loss | Failed attempt persists; resume makes no second call; changed/tampered progress rejected | Synthetic failure/resume/checksum test |
| Failed candidate excludes hard cases | One failed candidate cannot shrink full-cohort selection population | Synthetic selection test |
| Threshold rounding changes gate | Exactly 10% MAE reduction remains eligible | Synthetic boundary assertion |
| Frozen source/input/configuration drift | Changed execution rejected, completed replay blocked | Synthetic execution-guard test |
| Unsupported accuracy claim | All candidates, failure yields, tails/native coverage and source differences reported | Actual aggregate report; no max-error guarantee |

## Checks completed

Five focused synthetic tests passed before inference. Research suite: 97 passed,
one opt-in simulator skip. Full Python suite: 122 passed, the same skip and one upstream
TestClient deprecation warning. Ruff passed across backend/research/tests/scripts.
Completed-artifact/source ZIP verification passed. An independent check reproduced
participant-average MAE/within-10 from saved predictions, verified all row checksums,
identical paired identities/targets, 1,509 attempts per run, unchanged prepared-input
protocol and unchanged checkpoint files. Evidence:
`.cache/model-refinement-preflight/phase3-real-verification.json`.
App/database/frontend behavior is unchanged; their integration checks were not repeated.
Final documentation/privacy/diff and Graphify evidence are stored alongside the
inference/test logs under `.cache/model-refinement-preflight/`.

The final review checked 21 Markdown files for local links and six new files for
whitespace/secret/contact patterns: no findings. Repository-configured Git diff check
and final Ruff lint passed. Downloaded data, predictions, weights, source snapshots
and runtime logs remain Git-ignored and Graphify-excluded. No semantic backend used.

One final code-only Graphify update exited 0; the read-only freshness check returned
ACTIVE. Graph: 1,964 nodes, 3,601 edges, 213 communities; all three new Phase 3 code
files are present. The known optional SQL parser warning still skips seven SQL files;
no SQL changed here. Community labels were partially derived from hubs; no model-based
semantic relabeling/upload was used. Logs: `phase3-graph-update.log`,
`phase3-graph-status-after.log`, `phase3-graph-verification.json`.

Python 3.12.5; NumPy 2.5.3, Torch 2.14.0, chronos-forecasting 2.3.2, DuckDB 1.4.4.
Full results: [aggregate report](../reports/metabonet-phase3-inference-2026-10-16.md).

## Documentation reviewed/updated

Planning 00/01 track status/scope, 02 the fixed context/adapter comparison, 05 metrics
and failure populations, 06 stage/schedule, 07 local evidence, 08 native-output risks,
09 the formal specification, 10 M2 separation, 11 the broader-data ledger, 12 the
completed input stage and 13 the predeclared protocol/outcome ledger. Planning 03/04
are unchanged because no product UX or application architecture changed. Root/research
READMEs, report/tooling navigation, ADR 0011 and test strategy link the new evidence.

## Known limitations and next action

The matched cohort is a subset of the pilot, with retrospective isolated-meal
eligibility and unknown carb-reporting latency. Source-present masks cannot prove
complete logs or reverse upstream interpolation. Context experiments use existing
recorded-event alignment; no physiological insulin model is claimed. Validation is
used for selection and optimistic; participant-bootstrap intervals are descriptive.
Raw native intervals are not calibrated. Test-only identities are not yet proven
globally independent people. PEDAP remains a separate pediatric shift holdout.

Phase 4 follows completion: fit modest direct Ridge/LightGBM models on training only,
with deliberate masks and native units, and compare against the frozen options.
Keep separate calibration and tests untouched until their predeclared stage. Further
history/context searches require a new documented comparison, not changes to this run.
If Phase 4 uses every event eligible at its chosen history rather than the 1,509-event
four-history intersection, evaluate baselines on exactly that new population too.
Reuse a saved prediction only when IDs, requests and targets match; keep additional
Phase 4 inference in its own output. Do not compare scores on different cohorts.
