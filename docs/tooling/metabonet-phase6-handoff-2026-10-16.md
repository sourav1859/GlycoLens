# MetaboNet Phase 6 handoff — October 16, 2026

## Goal and accepted decisions

Complete the sixth phase of the approved broader-data model-refinement sequence:
freeze candidates, calibrate separately, evaluate reserved subjects/sources once and
document accuracy, tails, failures, uncertainty and subgroups. The user's instruction
to proceed authorized local implementation and execution. No additional input was
needed. No application changes, uploads, foundation training or deployment.

Original Phase 4 LightGBM is the frozen primary; original Ridge is a diagnostic
challenger and persistence is the baseline. Neither Phase 5 correction advanced.
No point refits or test-based reselection. Preserve 24-hour glucose history, six-hour
event features, native mg/dL/g/trailing-five-minute IU semantics, five-minute carb
availability and 24 future five-minute targets. The +/-10 objective is aspirational.

## Current state and results

**Phases 1-6 of this research sequence are complete. Tight precision remains poor.**

| Cohort | Eligible meals / IDs | Persistence MAE | LightGBM MAE | LightGBM within +/-10 | Nominal 80% marginal coverage |
|---|---:|---:|---:|---:|---:|
| Unseen Loop/ReplaceBG | 3,533 / 102 | 36.81 | 29.91 | 28.20% | 79.05% |
| Pediatric PEDAP | 2,177 / 64 | 48.77 | 40.92 | 19.57% | 63.94% |

Both fixed point-improvement gates passed: 18.74% / 16.10% MAE reductions, no lower
within-10, no worse pooled p95 and no failures. PEDAP within-10 is practically
unchanged from persistence's 19.56%. Both cohorts' complete-curve within-10 rates
remain weak (LightGBM 0.94% / 0.18%). Maximum errors are 264.87 / 268.63 mg/dL.
The two-hour endpoint MAE is 40.90 / 52.91, larger than trajectory-average MAE.
Descriptive primary-minus-persistence participant-bootstrap MAE intervals:
-6.90 [-7.94,-5.87] primary; -7.85 [-9.65,-6.24] PEDAP.

Calibration had 1,488 eligible 24-hour windows. Exactly one hash-selected meal per
participant supplied 48 representatives; exact rank 40/48 produces symmetric marginal
radii and a separately calibrated maximum-error curve radius. LightGBM marginal
radii at 30/60/120 minutes: 27.24/56.88/64.05 mg/dL; curve radius 80.35. Curve-band
coverage is 80.57% primary / 61.11% PEDAP. Mean marginal width is 96.73 mg/dL; curve
width is 160.70. These are not precise predictions or conditional/clinical guarantees.
Near-80% average primary coverage also hides undercoverage at some early horizons.

All 104/65 metadata reservations were opened after calibration completed. Eligible
identities are 102/64; zero-event identities were not replaced. Candidate origins:
10,180 / 6,332, with complete rejection accounting. Primary studies contribute
2,914 Loop and 619 ReplaceBG meals. Exact partial fingerprint screening checked
1,474,695 distinct development references / 2,519,890 distinct overall sequences,
with zero quarantined reserved IDs or flagged development references. This cannot
prove globally unique people. PEDAP file segments were not concatenated for windows.

## Implementation and artifacts

- `research/evaluation/metabonet_uncertainty.py`: participant representative rule,
  immutable finite-rank bands, common adapter wrapper, marginal/curve coverage.
- `research/pipelines/run_metabonet_independent.py`: candidate freeze, explicit gated
  reserved projection, separate-file preparation, duplicate screening, all-attempt
  scoring, fixed confirmation gate, descriptive bootstrap and predeclared subgroups.
- `research/pipelines/report_metabonet_independent.py`: aggregate results renderer;
  added after frozen scoring and does not change model predictions or selection.
- `tests/research/test_metabonet_independent.py`: 11 synthetic acceptance tests.
- [Protocol 16](../planning/GlycoLens_16_MetaboNet_Independent_Evaluation.md),
  [ADR 0014](../decisions/0014-independent-testing-and-participant-calibration.md),
  [aggregate results](../reports/metabonet-phase6-independent-2026-10-16.md).

Ignored output: `artifacts/evaluation-results/metabonet-phase6-v1/calibration/` and
`test/`, each with immutable source ZIP, configuration/execution SHA, row/artifact
hashes and completion manifest. Test configuration chains to calibration completion.
Calibration bands were saved before any reserved CGM/event projection. Original
point-model bundles/imputers/scalers remained unchanged. No Chronos calls occurred.
Pre-outcome sources match across stages; subsequent living protocol notes are
preserved separately from the archived initial protocol.

Derived aggregate figure: `artifacts/evaluation-results/metabonet-phase6-v1/figures/phase6-accuracy-and-coverage.png`
and PDF. Figures are outside the immutable completed-stage directories. Visual
inspection passed. Raw data, projections, windows, rows, IDs, weights and runtime
logs remain ignored; no participant details are in the report.

## Commands and verification

```powershell
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m research.pipelines.run_metabonet_independent --stage calibration
.venv/Scripts/python.exe -m research.pipelines.run_metabonet_independent --stage test
# For an already completed run, use only these verification commands:
.venv/Scripts/python.exe -m research.pipelines.run_metabonet_independent --stage calibration --verify-only
.venv/Scripts/python.exe -m research.pipelines.run_metabonet_independent --stage test --verify-only
.venv/Scripts/python.exe -m research.pipelines.report_metabonet_independent
```

Completed stages refuse replay. Partial attempts require review, not forecast retries
or overwriting. The full Python preflight passed **155 tests**, one explicit opt-in
simulator skip and one existing TestClient dependency warning. The new module first
failed test collection before implementation; all 11 synthetic cases then passed.
Research-only changes did not require repeating frontend/database/live simulator checks.

| Requirement/risk | Synthetic fixture and check | Real evidence |
|---|---|---|
| Leakage through roles | Non-calibration rows rejected; absent gate blocks raw connection; mixed evaluation roles rejected | Calibration-before-test hash chain; reserved/source IDs disjoint from development |
| Repeated participant dominance | Two events from one synthetic subject; value changes cannot alter representative | 48 distinct representatives, exact hash selection independently reproduced |
| Incorrect finite-rank/curve calibration | Known order statistics, small/nonfinite samples, separate max-error radius | Exact rank/radii independently reproduced for all three predictors |
| Point forecast/state mutation | Immutable request and wrapper/state equality; negative lower endpoints retained | Both stage states unchanged; original models/prior artifacts/checkpoints verified |
| File-boundary/duplicate borrowing | Incomplete segment target cannot borrow later file; duplicate timestamps rejected | Separate PEDAP projections/segments and complete candidate/rejection accounting |
| Failure/survivor bias | Synthetic failed prediction retained; attempted yields include failure; replay refused | 17,130 test records, identical attempts per model; zero failures |
| Artifact corruption/replay | Band-byte modification detected; completed execution refused | All source ZIP/row/input/model/completion hashes verified |
| Misleading metrics/uncertainty | Marginal versus whole-curve and failure yield synthetic example | NumPy reproduction of point/tail/coverage metrics and 19 subgroup counts/MAEs |
| Saved/public/batch drift | Common-contract wrapper tests | 18 public/batch/wrapper/saved samples agree; state unchanged |

Independent audit: `.cache/model-refinement-preflight/verify_phase6.py`, with aggregate
proof `phase6-real-verification.json`. It reproduced all reported test macro accuracy,
pooled p95/p99/max, band bounds and point/curve coverage, calibration ranks, 19
subgroups, checksums and unchanged prior Phase 2/3/4/5/checkpoint bytes. It did not
refit models or alter any original result. Logs: `phase6-full-tests.log`,
`phase6-calibration.log`, `phase6-test.log`, `phase6-verification.log`.

Python 3.12.5; pinned NumPy 2.5.3, sklearn 1.7.2, LightGBM 4.6.0, DuckDB 1.4.4 and
joblib 1.6.0. Preloading sklearn/SciPy/LightGBM before thread limits resolved Phase 5's
late-import resource caveat: all four loaded pools reported two threads. Calibration
took 3.35 seconds; preparation/scoring 217.72 seconds, excluding initial hashing.
No interrupted execution or failed forecast retry occurred in this phase.

## Documentation reviewed and next action

Planning 00/01: current status; 02 model/datasets; 04 architecture; 05 method;
06 schedule; 07 local scientific evidence; 08 safety; 09 specification; 10 M2 scope;
11 phase ledger; 12-15 historical experiment follow-ups; 16 locked protocol/results.
All were updated in this cycle. Planning 03 is unchanged: this phase changes no UX.
Root/research/adapter READMEs, decisions/report/tooling navigation, test strategy and
Graphify notes were synchronized. Security policy, skill/checklist instructions and
planning impact map were reviewed and did not require changes.

Retain LightGBM as the research incumbent, with no automatic app promotion. Both
test cohorts are consumed and may be used only as diagnostic evidence in future
tuning. The next research round needs development-only improvement of cohort size,
event timing and participant adaptation, followed by fresh confirmation data.
Forty-eight calibration representatives, correlated meals, retrospective isolation,
unknown logging latency/processing, incomplete event records and cross-source aliases
limit conclusions. PEDAP undercoverage must not be hidden by primary average coverage.
Live nutrition/recipe verification and presentation remain separate M2 prerequisites;
no official deadline revision or full milestone closure is claimed.

Final Graphify evidence is recorded in `phase6-graph-before.log`,
`phase6-graph-update.log`, `phase6-graph-after.log` and
`phase6-graph-verification.json` under the same ignored preflight directory. The
closing workflow permits one code-only update, with no semantic backend. Known
optional SQL-parser omissions are unrelated to this Python-only change; read the
final status/content proof for readiness rather than treating graph output as
scientific evidence.
