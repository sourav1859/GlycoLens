# Milestone 1 Phase 6: py-mgipsim Virtual-Patient Scenario

**Date:** September 29, 2026
**Status:** Implemented and validated locally
**Scope:** Reproducible source setup, isolated dependencies, fixed scenario, safe result contract,
and deterministic real-simulator validation

## Outcome

GlycoLens now installs and executes the official py-mgipsim source at pinned commit
`b985f8c2ea385d1b2b8480957b730866e07772f1`. One fixed ExtHovorka/OpenLoop virtual-patient day
completed twice with byte-identical result files. This closes the Milestone 1 simulator-feasibility
deliverable.

The simulator remains an offline research tool in Phase 6. It is not yet called by FastAPI or the
PWA, and its output is not stored in Supabase.

## Fixed feasibility protocol

| Setting | Value |
|---|---:|
| Upstream source | `illinoistech-itm/py-mgipsim` |
| Upstream commit | `b985f8c2ea385d1b2b8480957b730866e07772f1` |
| Python | 3.12.5 |
| Isolated resolved packages | 68 |
| Model | `T1DM.ExtHovorka` |
| Controller | `OpenLoop` |
| Virtual subjects | 1 synthetic subject |
| Duration | 1,440 minutes |
| Sampling interval | 5 minutes |
| Expected samples | 288 |
| Random seed | 20,260,929 |
| Positive meal events | 3 |
| Synthetic meal carbohydrate total | 210 g |
| Physical activity | disabled |

Meal and controller settings are part of a synthetic test protocol. They are not food, therapy, or
insulin-dose guidance.

## Quantified result

| Measure | Observed result |
|---|---:|
| Samples | 288 |
| Relative-time range | 0-1,435 minutes |
| Simulated glucose minimum | 106.62 mg/dL |
| Simulated glucose maximum | 141.78 mg/dL |
| Simulated glucose mean | 118.62 mg/dL |
| Simulated glucose start | 108.00 mg/dL |
| Simulated glucose end | 107.63 mg/dL |
| Result size | 23,657 bytes |
| Result SHA-256 | `60acdd058e53586cb43a0db09f71d700f1a34840b443f97f446132a27116c3b4` |

These numbers establish that the software runs deterministically and produces a structurally valid
trajectory. They do not establish accuracy, realism for all people with T1D, clinical safety, or
superiority to any forecasting model.

## Implemented boundary

- `scripts/simulation/Install-PyMgipsim.ps1` clones the exact reviewed commit and synchronizes a
  separate ignored Python environment from a committed lock file.
- `research.simulation.pymgipsim` verifies source provenance, launches a subprocess bridge, and
  validates the normalized result.
- The bridge retains relative time, simulated glucose, aggregate meal metadata, and provenance.
- It omits absolute timestamps, real identifiers, individual insulin values, and dose fields.
- Generated JSON is stored in ignored `artifacts/simulation/`; upstream files and its environment
  remain under ignored `.cache/` paths.
- The command requires explicit `--allow-upstream-execution`.

## Test traceability

| Requirement or risk | Scenario | Layer | Result |
|---|---|---|---|
| Reviewed protocol only | Reject different day, subject, or controller | Unit | Pass |
| Valid result contract | Parse 288 relative-time points | Unit | Pass |
| Grid integrity | Mutate one minute value | Unit | Pass: rejected |
| Numeric safety | Inject `NaN` glucose | Unit | Pass: rejected |
| Aggregate integrity | Corrupt reported mean | Unit | Pass: rejected |
| Privacy/safety fields | Add `patient_id` | Unit | Pass: rejected |
| Explicit execution consent | Omit opt-in flag | CLI contract | Pass: refused |
| Source provenance | Verify Git `HEAD` | Integration boundary | Pass |
| Real simulator execution | Run pinned upstream scenario | Integration | Pass |
| Reproducibility | Run twice and compare object/bytes | Integration | Pass |
| Existing Python behavior | Full pytest suite | Regression | Pass: 73 passed, 1 opt-in skip |
| Existing frontend behavior | Lint, tests, typecheck, build | Regression | Pass: 5 tests and production build |

Targeted offline tests passed 10 tests with the external test skipped. The explicit real test
passed all 11 tests, including two real simulator executions, in 10.52 seconds.

Graphify 0.9.69 then refreshed the ignored code-only graph to 1,276 nodes, 1,875 edges, and 160
communities. Its query located the scenario runner, adapter, bridge, source-commit check, validators,
and reproducibility test; these relationships were confirmed against source. SQL extraction still
lacks Graphify's optional `tree_sitter_sql` dependency and is not simulator evidence.

The final validation also passed Ruff lint/format, Python bytecode compilation, all nine
repository-skill validators, the complete 73-test Python regression suite, all five frontend tests,
TypeScript checking, ESLint, and the Next.js production build.

## Reproduce safely

From the repository root:

```powershell
./scripts/simulation/Install-PyMgipsim.ps1
uv run python -m research.pipelines.run_pymgipsim_scenario --allow-upstream-execution
$env:GLYCOLENS_RUN_PYMGIPSIM = "1"
uv run pytest -q tests/research/test_pymgipsim.py
Remove-Item Env:GLYCOLENS_RUN_PYMGIPSIM
```

The first command needs network access only when the ignored source or dependencies are absent.
The scenario itself runs locally. Do not commit generated result files.

## Milestone 1 closure

The simulator requirement and the subsequent presentation requirement are complete. The final
[Milestone 1 closure audit](milestone-1-closure-audit.md) records the full regression, database,
privacy, safety, and presentation gates. TimesFM remains a desirable comparison, but the schedule
treats it as optional for Milestone 1 because Chronos-2 satisfies pretrained-model feasibility.

## Sources

- Official repository: https://github.com/illinoistech-itm/py-mgipsim
- Official documentation: https://illinoistech-itm.github.io/py-mgipsim/
- Architecture decision: [ADR 0007](../decisions/0007-isolated-pymgipsim-feasibility-boundary.md)
