# MetaboNet Phase 4 handoff - October 16, 2026

## Goal and accepted decisions

Complete the approved small direct-model phase under
[protocol 14](../planning/GlycoLens_14_MetaboNet_Direct_Models.md). Train modest
Ridge/LightGBM competitors, freeze training-only choices before validation, compare
the same 1,509 validation meals with preserved Phase 3 forecasts, document the actual
result and keep calibration/reserved outcomes untouched. Preserve the common adapter,
research/app separation, foundation weights and earlier experiment artifacts.

## Results and interpretation

All 32 fixed candidates / 96 subject-fold fits succeeded. Common training CV pool:
6,756 meals / 196 identities. Both families selected 24-hour event features; Ridge
alpha 1000 and LightGBM 31 leaves/160 trees. Refit on 6,794 meals / 197 identities,
127 request-only features. Ridge jointly predicts 24 deltas; LightGBM pools horizons
with a horizon feature after splitting. Train-only imputation/scaling and equal
participant weights preserve the protocol.
The 24-hour setting is glucose history; recorded-event summaries cover six hours
plus origin-known current carbs.

On the same 1,509 validation meals / 48 identities:

| Model | Macro MAE mg/dL | Within +/-10 | Pooled p95 | Pooled maximum |
|---|---:|---:|---:|---:|
| LightGBM direct | 31.17 | 26.84% | 91.16 | 235.38 |
| Ridge direct | 31.36 | 28.85% | 91.18 | 229.53 |
| Persistence | 37.12 | 25.47% | 111.00 | 259.50 |
| Frozen six-hour C2 | 37.61 | 25.98% | 113.33 | 364.72 |

LightGBM passes the predeclared MAE-first research gate: 16.03% lower MAE, no lower
within-10 and no worse p95 than persistence. Its descriptive participant-bootstrap
MAE delta is -5.95 mg/dL, 95% interval [-7.60,-4.33]. Both new models have zero
failed events and zero negative predicted points. Validation was reused for selection;
this is not independent confirmation.

Tight tolerance remains poor. Ridge has higher within-10, while LightGBM has slightly
lower average error. Whole-curve within-10 worsens: LightGBM 0.52%, Ridge 0.76%,
persistence 1.44%. Lower average error is not uniform improvement or dependable +/-10
forecasting. Direct equal quantiles are placeholders; no calibrated bands or coverage
claims. Keep Ridge as a tolerance challenger in the next frozen comparison.

## Scoring interruption and provenance

The original run completed every fit and froze both choices/models, then failed
before the first persisted scored validation row: statistics.mean cannot consume
NumPy boolean values produced from NumPy scalar predictions. A failing synthetic
regression reproduced this. The sole scoring-line fix converts predictions to native
floats before metrics/JSON; no prediction value, feature, parameter or choice changed.

`complete_metabonet_training.py` verifies the original execution/source ZIP, all CV
checksums/OOF arrays, training cohort/folds, CV-only choices and model hashes. Its
guard requires the runner to differ from the archived original by exactly that one
conversion. The original empty JSONL is renamed and retained. A separate completion
source/configuration archive freezes this repair before rescoring. Original model
bytes are loaded only after verification and are never refitted. Final completion
hashes cover both execution archives and all saved outputs. No outcome-based retry,
error-based exclusion or hidden restart. Completed studies refuse replay.

Wall time from original execution freeze through completion: 9.26 minutes, including
diagnosis/repair. Batch prediction for 1,509 meals took 75.48 ms LightGBM / 2.33 ms Ridge,
excluding feature extraction. No per-request p95 was measured. Do not compare those
batch timings with individual Chronos calls. No new Chronos inference was required.

## Implementation and artifacts

- `research/models/adapters/metabonet_tabular.py`: native-unit/mask origin-only
  features, weighted direct models and common deterministic point-forecast contract.
- `research/pipelines/run_metabonet_training.py`: fixed training CV, verified progress,
  per-family frozen selection, final refits and paired validation/provenance.
- `research/pipelines/complete_metabonet_training.py`: strictly scoped scoring-only
  completion of the already fitted interrupted run; not a general freeze bypass.
- `research/pipelines/report_metabonet_training.py`: verified aggregate report.
- `tests/research/test_metabonet_models.py`:12 synthetic acceptance/regression cases.
- ADR 0012, planning14 and all affected status/method/risk/navigation documents.

All datasets, identities, timestamps, requests, labels, predictions, OOF arrays,
weights, source ZIPs and logs remain ignored. Output:
`artifacts/evaluation-results/metabonet-phase4-v1/`. Existing Phase 2/3/UOM/AZT1D
results and app inference are unchanged. No external upload, database import,
foundation-model fitting, app model replacement or deployment.

## Requirement traceability and checks

| Requirement / risk | Evidence |
|---|---|
| Unknown amounts become zero / incorrect insulin units | Synthetic masks/native IU/fractional-carb tests; merged total excluded |
| Future or identity leakage | Altered targets/identity leave features unchanged; no ID/source/date predictors |
| Validation tunes training | Reader spy; subject-CV choices/model metadata frozen before prepared validation read |
| Horizon expansion mixes subjects | Fold-spy asserts no held-out feature rows enter fits; expand only inside adapter fit |
| Unequal participant contribution | Stable source-stratified folds and equal-total-weight assertions |
| A failed candidate wins / a hard event disappears | Failure-ineligible ranking; same 1,509 paired identities/targets verified |
| Prediction refits transforms | Model hash unchanged by prediction; both adapter families tested |
| Corrupt progress/model is reused | Changed CV bytes rejected; changed model rejected before deserialization |
| Scoring fix changes trained experiment | Synthetic regression and exact-one-line source amendment guard |
| Misleading accuracy/uncertainty claims | Full/pairwise/common-success denominators, tails, negatives, tradeoffs; no placeholder coverage |

Twelve focused tests pass. Full Python suite:134 passed, one opt-in simulator skip,
one existing FastAPI/Starlette TestClient dependency warning. Ruff lint and format
checks pass for all five new Python files. No frontend/database/live simulator checks
repeated because those behaviors are unchanged.

Independent evidence reproduced every CV and validation macro MAE/within-10 from
saved arrays/predictions. It verified all nine runs have 1,509 paired events, row
checksums and finite OOF predictions; 10 public/batch/saved prediction comparisons
match without changing model state. Twenty-one sampled saved baseline request
fingerprints match fresh prepared requests. All completed artifact/source/model
hashes, original prepared inputs, Phase 3 outputs and Chronos checkpoint files verify.
Logged Ridge scaling RuntimeWarnings did not produce failed folds/nonfinite OOF
outputs; saved scales/coefficients are finite. Calibration/reserved outcomes were
not iterated. Evidence: `.cache/model-refinement-preflight/phase4-real-verification.json`.

Runtime logs/check evidence remain under `.cache/model-refinement-preflight/`:
`phase4-training.log`, `phase4-completion.log`, `phase4-full-tests.log`,
`phase4-validation-regression-red.log`, `phase4-real-verification.log`, and final
documentation/privacy/diff checks. Final Graphify evidence uses
`phase4-graph-update.log`, `phase4-graph-status-after.log` and
`phase4-graph-verification.json`. Refresh only the local code graph: semantic
documentation extraction/upload remains disabled. Optional SQL parser omissions
are unrelated to this Python-only change.

Planning documents 00/01 summarize status; 02/04 adapter/model architecture; 05 evaluation;
06 schedule; 07 local evidence; 08 risks; 09 specification; 10 M2 separation; 11 broader
phase ledger; 12/13 input/preceding phase handoffs; 14 frozen design/outcomes. Planning 03
requires no change because no product UX changes. Root/research/adapter READMEs,
report/tooling/decision navigation and test strategy link this evidence.

## Next phase and remaining limitations

**Phase 5 is next, not yet started on MetaboNet.** Predeclare the correction protocol
before fitting: frozen Chronos backbone, training-only subject-CV correction choices,
the same validation targets, direct LightGBM primary comparator and Ridge tolerance
challenger. Generating training Chronos forecasts will need additional CPU time;
validation forecasts already exist. Do not assume corrections must win or change
Phase 4's ranking because a different metric favours Ridge.

Phase 6 separately calibrates final selected models, then evaluates frozen choices
once on 104 primary-test and 65 PEDAP reservations. Their event eligibility is still
unknown; do not call them usable test-event counts. AZT1D was previously consumed
and is not untouched. Source-qualified IDs are not proof of global identity
independence; upstream processing, missing event logs and carb latency remain unknown.
Retrospectively isolated logged meals and the all-history validation intersection
limit generalization. The +/-10 aspiration remains unmet. No prerequisites are needed
from the user for the next local phase; no live nutrition/M2 closure claim follows.

See [full results](../reports/metabonet-phase4-training-2026-10-16.md) and
[protocol 14](../planning/GlycoLens_14_MetaboNet_Direct_Models.md).
