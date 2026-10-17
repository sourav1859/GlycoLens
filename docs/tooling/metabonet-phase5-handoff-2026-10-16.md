# MetaboNet Phase 5 handoff - October 16, 2026

## Goal and accepted decisions

Complete the user-approved correction phase under
[protocol 15](../planning/GlycoLens_15_MetaboNet_Chronos_Correction.md). Use the best
failure-free frozen Chronos option, six-hour C2, with 24-hour glucose/six-hour event
features and 24 frozen forecast changes. Compare Ridge alpha 10/1000 and pooled
LightGBM 15/31 leaves using the unchanged modest budget. Preserve Phase 4 folds,
participant weighting and training-only transformations. No backbone fitting,
calibration/test outcomes, application changes or uploads.

Cache all 6,756 common training forecasts, preserving failures without retry. Correctors
and two fixed direct controls fit exactly the same successful training rows. Three
whole-subject folds precede horizon expansion. Freeze correction choices and all
four final bundles before reading prepared validation outcomes. Reuse original C2
validation predictions and all nine Phase 3/4 options on the same 1,509 meals.

Distinguish lowest-MAE ranking from advancement: a correction requires at least 5%
lower MAE than original Phase 4 LightGBM, no lower within-10, no worse p95 and no
failed validation events. Otherwise retain the incumbent. Matched controls remove
training-population differences; the correction still jointly changes forecast
features and residual targets, so it does not isolate those mechanisms individually.
No guarantee that a correction wins; a negative result closes this phase.

## Implementation and safeguards

- `metabonet_context.py`: fixed immutable C2 request conversion, matching Phase 3.
- `metabonet_residual.py`: common-contract heads; explicit frozen-backbone attachment
  or verified cached baseline. Saved heads strip live foundation models. Equal
  quantiles are deterministic placeholders. Live prediction latency includes
  backbone plus head, while cached/batch head timings exclude backbone work.
- `metabonet_tabular.py`: extract shared fit/predict regression helpers without
  changing direct-model behavior; saved Phase 4 predictions verified equivalent.
- `cache_metabonet_backbone.py`: training-only request cache without labels,
  checksummed every attempt, checkpoint/input/source freezes and completed replay guard.
- `run_metabonet_correction.py`: exact cache/request alignment, matched training
  controls, fixed subject CV, trusted model reloads, failure-aware paired validation,
  incremental gate and source/artifact manifests.
- `report_metabonet_correction.py`: aggregate reporting of all 13 options and tradeoffs.
- ADR 0013 and planning15 record the decision/design before results.

Private artifacts remain under ignored
`artifacts/evaluation-results/metabonet-phase5-v1/`, with separate `backbone/` and
`heads/` execution/source snapshots. No new validation Chronos calls. Native output
failures remain failures; negative predictions are not clipped. Labels, predictions,
identities, timestamps, model weights and source ZIPs never enter tracked reports.

## Requirement traceability

| Requirement / risk | Evidence |
|---|---|
| Backbone sees future labels / wrong event schema | Request-only C2 conversion equals original Phase 3; labels absent from cache |
| Calibration/test enters training | Training-role cache guard, unchanged development readers and scoped runner |
| Failed forecast silently retried | Failure persisted, resume makes no second call, tampering rejected |
| Baseline/labels misalign or subjects cross folds | Fold-spy verifies baseline/features alignment and fit/held separation |
| Validation tunes CV choices | Model/choice freezes precede prepared validation read; execution source archived |
| Model save includes foundation weights | Runtime backbone stripped; trusted reload requires explicit attachment/cache |
| Prediction changes fitted state | Model hashes unchanged by predict; saved/public/batch equivalence |
| Corrupt bytes deserialize | Hash checked before load; synthetic tamper fails before deserialization |
| Failed backbone drops requested validation meals | Failure remains a BackboneUnavailable attempt in full denominator |
| Tiny selected gain is presented as advancement | Exact5%/tolerance/tail/failure boundaries and separate point-winner decision test |
| Uncalibrated bands misrepresented | Corrected equal quantiles explicitly deterministic; no coverage claim |

Ten focused synthetic cases pass. Full Python suite:144 passed, one opt-in simulator
skip and one existing TestClient dependency warning. Ruff lint/format pass across
the seven affected Python files. A separate real check verifies original Phase 4
saved/public prediction equivalence and unchanged prior artifacts/checkpoint files:
`.cache/model-refinement-preflight/phase5-prior-model-verification.log`.

## Completed execution and verified findings

**Phase 5 is complete; Phase 6 calibration/independent testing is next.** Frozen C2
generated 6,756 training forecasts; 6,756 usable meals / 196 identities supported six CV
configurations / 18 fold fits and four final refits, with exactly matched direct
controls. Neither correction passed the predeclared incremental gate; retain Phase 4
LightGBM. Lowest-MAE eligible option: `ridge_residual_1000`; advancement candidate:
`lightgbm_direct` (macro MAE 31.17 mg/dL, within +/-10 26.84%). These are
reused-validation findings, not independent confirmation. Calibration/reserved outcomes
and app inference remain untouched; +/-10 performance remains weak.

Backbone attempts 6,756, successes 6,756, failure types {}; choices: ridge_residual_1000, lightgbm_residual_31.

| Option | Macro MAE | Within +/-10 | Pooled p95 | Maximum |
|---|---:|---:|---:|---:|
| ridge_residual_1000 | 31.14 | 29.12% | 90.53 | 230.26 |
| lightgbm_direct | 31.17 | 26.84% | 91.16 | 235.38 |
| lightgbm_control | 31.25 | 26.60% | 90.84 | 243.75 |
| ridge_control | 31.30 | 28.72% | 90.98 | 230.15 |
| ridge_direct | 31.36 | 28.85% | 91.18 | 229.53 |
| lightgbm_residual_31 | 31.75 | 25.95% | 92.00 | 265.22 |
| persistence | 37.12 | 25.47% | 111.00 | 259.50 |
| chronos_c2_6h | 37.61 | 25.98% | 113.33 | 364.72 |
| chronos_c0_2h | 42.52 | 23.52% | 126.91 | 473.69 |

Independent checks reproduced all six OOF scores and all 13 validation comparisons, verified identical identities/targets, all row/source/model/input hashes and original checkpoint files. Twelve public/batch/saved prediction samples agree without changing model state; all saved heads contain no live backbone. Prior prepared/Phase 3/4 artifacts remain unchanged. Evidence: `.cache/model-refinement-preflight/phase5-real-verification.json`.

Measured backbone runtime 41.20 minutes; head CV/refit/validation 1.99 minutes. Batch head timings exclude features/backbone; no per-request head p95 was measured. Scaling warnings, if present, remain in local logs; successful OOF arrays and saved-model predictions were checked finite.

Logs/check evidence: `phase5-backbone.log`, `phase5-heads.log`, `phase5-full-tests.log`, `phase5-real-verification.json`, final documentation/privacy/diff review and Graphify `phase5-graph-update.log`, `phase5-graph-status-after.log`, `phase5-graph-verification.json`, all under `.cache/model-refinement-preflight/`. Only the local code graph is refreshed; semantic documentation upload remains disabled. Optional SQL parser omissions do not affect this Python-only implementation.

Planning documents 00/01 summarize status; 02/04 models and architecture; 05 experiments; 06 schedule; 07 local evidence; 08 risks; 09 specification; 10 M2 separation; 11 overall ledger; 12/13/14 preceding-stage follow-ups; 15 predeclared protocol/results. Planning 03 is unchanged because no product UX changes. Root/research/adapter READMEs, report/tooling/decision navigation and test strategy link the evidence. No frontend/database/live simulator checks repeated.

The first PowerShell launcher stopped on a retained RuntimeWarning during the first candidate, before completed CV results or validation rows. Its stderr handling was corrected; the same frozen model sources/configuration resumed, recomputing only the incomplete candidate. Interrupted logs and launcher-interruption.json are retained. An isolated import-order audit found NumPy BLAS 2 but late-loaded SciPy BLAS/OpenMP 16 despite the requested limit 2. Strict universal two-thread head execution is not established. Reported head time is the resumed completion attempt, excluding lost partial work. Before future timing claims, preload numerical libraries before applying limits. No model/feature/selection change occurred.

## Next phase and limitations

Phase 6 remains unstarted: predeclare final candidate/calibration/test rules, then
calibrate separately and score frozen choices once on the 104 primary-test and 65
PEDAP source-test identity reservations. Test-event eligibility is still unknown.
Previously consumed AZT1D is not untouched. No foundation-model training, app switch,
official deadline revision or full-M2 closure follows from this research stage.

Retrospectively isolated logged meals, the all-history validation intersection,
unknown event latency/upstream processing, incomplete records and possible identity
aliases limit generalization. Validation was reused for selection; bootstrap
intervals are descriptive. The +/-10 aspiration remains unmet unless future evidence
actually supports it. No prerequisites are needed from the user for this local work.
