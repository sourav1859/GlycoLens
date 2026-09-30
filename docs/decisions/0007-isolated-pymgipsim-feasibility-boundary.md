# ADR 0007: Isolated py-mgipsim feasibility boundary

**Status:** Accepted
**Date:** September 29, 2026

## Context

Milestone 1 requires py-mgipsim to be installed and one virtual T1D scenario to run. The upstream
project is source-only rather than a conventional PyPI package, requires Python 3.12, uses paths
relative to its checkout, and declares a large dependency set that includes older pinned packages.
Adding that dependency set to the main GlycoLens environment would unnecessarily couple the API,
forecast, and simulation stacks.

The simulator can generate insulin therapy internally. GlycoLens must not expose those values as
dosing recommendations or present a simulated trajectory as clinical or real-patient evidence.

## Decision

- Pin upstream repository `illinoistech-itm/py-mgipsim` at commit
  `b985f8c2ea385d1b2b8480957b730866e07772f1`.
- Keep the upstream checkout and virtual environment under ignored `.cache/` directories.
- Lock its 68 resolved Python packages separately from the main `uv.lock`.
- Invoke the upstream simulator through a small subprocess bridge; do not import it into the
  FastAPI process in Milestone 1.
- Support one reviewed feasibility protocol: one synthetic virtual subject, ExtHovorka,
  OpenLoop, one day, five-minute sampling, fixed seed, three fixed synthetic meals, and no
  simulated physical activity.
- Export only relative minutes, simulated glucose, meal count/total, provenance, and aggregate
  statistics to ignored `artifacts/simulation/`.
- Require explicit `--allow-upstream-execution`; ordinary tests use the project-owned contract and
  stay offline. A separate opt-in integration test executes the real simulator twice and requires
  byte-identical output.
- Keep live app/API simulation integration for Milestone 2. Phase 6 proves feasibility only.

## Consequences

The simulator cannot destabilize the main application environment, the exact source and dependency
set are reproducible, and generated trajectories remain local. Setup requires a one-time source
checkout and separate environment. The upstream project is GPL-3.0; GlycoLens does not vendor its
source, and its license must be reviewed before distributing a combined simulator bundle.

This scenario is synthetic stress/demo evidence only. It is not model-accuracy evidence, a
clinical validation cohort, a dosing recommendation, or a substitute for held-out T1D-UOM data.

## Alternatives considered

- **Install upstream dependencies into the main environment:** rejected because it expands and
  couples unrelated runtime dependencies.
- **Vendor or modify upstream source:** rejected because it complicates provenance, updating, and
  license handling.
- **Reimplement a glucose simulator:** rejected because it would not satisfy the named py-mgipsim
  feasibility requirement.
- **Expose a simulation API immediately:** deferred until the Milestone 2 product contract,
  authorization, persistence, and UI behavior are defined.

## Verification

- offline contract/safety tests;
- exact source-commit verification before each run;
- fixed 288-point five-minute grid and finite 18-600 mg/dL sanity bound;
- aggregate-summary consistency checks;
- forbidden identifier, timestamp, insulin, and dose field checks; and
- an explicit real integration test that runs the scenario twice and compares both parsed results
  and output bytes.
