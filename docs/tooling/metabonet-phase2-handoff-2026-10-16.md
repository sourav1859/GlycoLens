# MetaboNet Phase 2 preparation handoff - October 16, 2026

## Goal

Complete the user-approved broader-development-data preparation stage and document
it. The new experiment follows the failed initial UOM-to-AZT1D generalization test.
It preserves original M2 and `refinement-v1` evidence. No model fitting, inference,
app model switch, deployment or external data upload in this stage.

## Accepted decisions

- Version `metabonet_phase2_v1`; exact audited v1.2 bytes and reviewed saved dictionary.
- Loop/ReplaceBG development; source-stratified whole-subject hash roles, then
  100/25/25 metadata-only quotas per source. No quality-based replacement.
- At most 100 stable positive-carb origins per selected subject, independent of
  future CGM. Histories 2/6/12/24 hours; availability delay five minutes primary,
  zero development sensitivity. Both timing choices and isolated-meal selection
  are assumptions, not confirmed physical meal/logging times.
- Native mg/dL/grams/trailing-five-minute IU, masks for missing entries, causal
  history fill <=10 minutes with >=90% source-present readings, complete targets.
- Metadata-only primary test and separate PEDAP pediatric source holdout. Consumed
  AZT1D/UOM, OhioT1DM pending terms and other nonpilot studies stay out.
- Retrospective isolated logged meals are a conditional benchmark. Future logged
  meals affect eligibility, never request features. No general unrestricted-meal claim.

## Current repository state

**Phase 2 complete; Phase 3 frozen-inference validation is next.** Real preparation
ran in 281.24 seconds and published ignored
`artifacts/evaluation-results/metabonet-phase2-v1/` (285,656,775 retained bytes;
300 compressed per-subject window files). Selected pool: 200 training / 50 validation /
50 calibration IDs, with 374,898 positive-carb rows and 28,852 sampled origins.

| Primary six-hour role | Windows | Eligible identities |
|---|---:|---:|
| Training | 8,973 | 197 |
| Validation | 2,000 | 48 |
| Calibration | 1,948 | 48 |

Seven selected identities have no eligible six-hour events; no replacement. There
are **1,509 matched validation events across all four histories** (separately checked
through the final reader). Partial exact duplicate screening checked 1,474,695 distinct
varied six-hour CGM fingerprints, with zero shared-ID candidates. This is not proof
of independent people. Primary test reserves 104 source-qualified identities absent
from all publisher training; PEDAP reserves 65. Test-event eligibility is not computed.
No test outcome columns were projected and no prediction accuracy was measured.

The frozen source ZIP contains the dataset module, preparation module and common
forecast contract as executed. After this real build, the final code added protocol/
split-metadata validation before consumption and full verification before publication.
The original build had already passed full post-publication verification. The frozen
source ZIP and window/policy bytes were preserved; the final verifier passes on them.
For exact build reproduction use its recorded execution source, not a claim that
the final working-tree preparation module has identical bytes.

The same local environment was recorded after the run; no dependency changes occurred
during preparation: Python 3.12.5, DuckDB 1.4.4, NumPy 2.5.3, pytest 9.1.1 and Ruff
0.16.9. Versions and dependency-file hashes are separate post-run evidence in ignored
`phase2-environment.json`; they were not embedded retroactively in the frozen protocol.
Protocol SHA-256: `a4e976b788c2a3324dcbc9f6b742c582d6f0548806db3948290f8eab95ed2e6f`.
`pyproject.toml`: `66ef93117de5ed5ac401ca34082604229037e1ac73c6c17b99abd557c8b96a8d`;
`uv.lock`: `bd3eae947be65d51a4b5aeaa159b0840d4fb99c9320791a8ab4997b1cd9625b2`.

## Files changed

- `research/datasets/metabonet.py`: native-unit subject series, stable origins,
  causal windows, masks, immutable adapter examples and partial fingerprints.
- `research/pipelines/prepare_metabonet.py`: bounded DuckDB projection, fixed subject
  roles, staging/publication, ignored artifacts, frozen protocol/source and verification.
- `research/pipelines/report_metabonet_preparation.py`: verified aggregate Markdown report.
- `tests/research/test_metabonet_preparation.py`: six unit/integration acceptance tests.
- Planning document 12, ADR 0011, preparation report, navigation and this handoff.

Preexisting changes in backend/frontend/M2 research files were retained. No app,
database, environment, dependency or credential edits were needed for this phase.

## Documentation reviewed/updated

Updated planning 00/01 (navigation/scope/status), 02 (data adapter/protocol), 05
(eligibility and evaluation boundaries), 06 (phase gate), 08 (privacy/leakage/task
limitations), 09 (specification), 10 (M2 separation), 11 (broader-data ledger) and
new 12 (fixed protocol plus executed counts). Planning 03/04/07 were reviewed for
impact and unchanged: no UX, application architecture or literature claim changed.
Root/research/dataset READMEs, decision/report/tooling indexes and test strategy
were updated. Source-of-truth counts agree with the ignored frozen summary.

## Checks completed

| Requirement | Evidence |
|---|---|
| Future values excluded from requests | Perturb future glucose/insulin: request unchanged, target changes |
| Source units/missingness preserved | Fractional carbs, IU amount, source-present masks, relative-offset fixture |
| Causal history/strict targets | Missing-history fill uses only past; long gaps and missing targets rejected |
| Explicit meal eligibility | Clustered and follow-up entries rejected; no equal-amount deduplication |
| Stable candidate/split roles | Event identity independent of history/delay/outcomes; deterministic source-qualified splits |
| Reserved tests untouched | Test Parquet fixture has metadata only; reserved-source poison value excluded |
| Frozen evidence | Completed-output replay rejected, protocol/quality/summary corruption detected, failed integrity cannot publish |
| Real preparation | Completed, nonempty required roles, full artifact/source ZIP hash verification and disjointness passed |
| Real consumer | Counts match; CGM-only/shared examples valid; matched four-history validation count 1,509 |
| Regression | 117 passed, one opt-in simulator skip, one upstream TestClient deprecation warning |
| Research subset | 92 passed, same opt-in simulator skip |
| Static checks | Ruff formatting of new code and lint across backend/research/tests/scripts passed |
| Privacy/docs/diff | All 20 reviewed Markdown files have valid local file links; eight new files passed whitespace/secret/contact-pattern checks; Git diff check passed |
| Graphify | One code-only update produced a fresh graph containing all four new modules; status ACTIVE, 1,906 nodes / 3,422 edges; wrapper warning described below |

Ignored command evidence is under `.cache/model-refinement-preflight/`, including
`phase2-preparation.log`, `phase2-research-tests.log`, `phase2-full-tests.log` and
`phase2-consumer-verification.json`. Additional final privacy/diff/link and Graphify
evidence is recorded there. Frontend, database, live providers and real simulator
were not rerun: no related behavior changed. No new model run is an intended check
of this data-preparation phase.

## Known failures or blockers

No Phase 2 blocker. Current OhioT1DM terms remain unresolved and isolated. The real
simulator integration is deliberately skipped without its opt-in. The TestClient
warning is an upstream deprecation, not a preparation failure. Do not change unrelated
dependencies as part of this task.

The Graphify update wrapper exited 1 when PowerShell treated its optional missing
`tree_sitter_sql` warning as a native-command error. The graph itself was written
after final code edits, contains all four new modules, and the subsequent read-only
freshness check returned ACTIVE. Seven SQL files were skipped; no SQL changed in this
phase. No second extraction, semantic backend or data upload was used. Logs:
`phase2-graph-update.log` and `phase2-graph-status-after.log`.

## Remaining risks

Only a bounded development pilot, not all MetaboNet. Unknown upstream interpolation,
unlogged intake, source-dependent zero/null semantics, meal latency and cross-study
aliases remain. Source-present masks do not certify actual complete observation.
PEDAP measures a separate pediatric distribution shift. Subject-level roles and
fingerprints reduce identifiable leakage but do not prove globally unique people.
New mask/recorded-channel schema requires deliberate Phase 4 feature handling;
the old UOM tabular extractor is not automatically validated for it.

## Next action

Phase 3: freeze the validation inference configuration and compare 2/6/12/24-hour
histories on the 1,509 matched events, with persistence, native C0 and any explicitly
supported recorded-context variants. Report all eligible/attempted/failed counts,
participant-average MAE, within +/-10, horizons and tails. Retain six hours only if
the new validation evidence supports it. Then train direct small models on training,
compare frozen-Chronos corrections, calibrate separately and freeze choices before
test-value access. Do not select on calibration/test or promise +/-10 maximum error.

Reproduction/verification commands and full exclusions:
[preparation report](../reports/metabonet-phase2-preparation-2026-10-16.md).
