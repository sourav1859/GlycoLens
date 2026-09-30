# Milestone 1 Final Closure Audit

**Date:** September 29, 2026
**Decision:** **PASS — Milestone 1 is complete**
**Scope:** Understanding, feasibility, planning, executable validation, safety, and presentation

## Executive conclusion

GlycoLens satisfies every required Milestone 1 deliverable and success criterion in the approved
course-aligned plan. The repository now contains a verified dataset pipeline, a leakage-resistant
forecast contract, a pinned Chronos-2 feasibility run, a typed FastAPI-to-PWA visualization slice,
an executable local Supabase/PostgreSQL contract, a deterministic py-mgipsim scenario, and an
editable RIT-branded milestone presentation.

The closure decision establishes technical feasibility and planning readiness for Milestone 2. It
does **not** establish forecast accuracy, clinical validity, physiological realism, production
security, or fitness for insulin dosing or treatment decisions.

## Requirement-to-evidence matrix

| Required Milestone 1 item | Closure evidence | Result |
|---|---|---|
| Categorized literature survey | `GlycoLens_07_Literature_and_Market_Survey.md` | Pass |
| Model-selection matrix | Candidate roles and decision criteria in planning documents | Pass |
| Dataset audit | T1D-UOM V1.0.4 provenance and aggregate audit | Pass |
| Evaluation protocol | Leakage boundary, participant-aware plan, metrics, and ablation protocol | Pass |
| Chronos-2 smoke test | Pinned CPU checkpoint produced 24 q10/q50/q90 points | Pass |
| TimesFM smoke if possible | Explicitly optional; Chronos-2 satisfies the required pretrained-model criterion | Not blocking |
| Common model adapter | Immutable `ForecastModelAdapter` contract with separated held-out target | Pass |
| Two-hour output and quantiles | 24 five-minute forecast points with finite, non-crossing q10/q50/q90 | Pass |
| Runtime and memory evidence | Cold/warm latency and process RSS recorded | Pass |
| T1D-UOM ingestion/alignment | CGM, meals, bolus, and basal audit and loaders | Pass |
| First meal-centered windows | 927 eligible leakage-safe windows | Pass |
| Next.js PWA skeleton | Buildable mobile-first page with accessible forecast chart and error states | Pass |
| FastAPI skeleton | Health and typed synthetic forecast routes | Pass |
| PostgreSQL/Supabase schema | Ten-table migration, pgvector, constraints, indexes, and RLS | Pass |
| Architecture diagram | Planning architecture plus editable deck flow diagram | Pass |
| Dummy end-to-end API flow | Typed browser client consumes the synthetic FastAPI forecast contract | Pass |
| py-mgipsim scenario | Pinned ExtHovorka/OpenLoop scenario reproduced byte-for-byte | Pass |
| Milestone presentation | Seven-slide RIT-branded editable deck with notes, charts, and audit table | Pass |

## Quantified closure evidence

### Dataset and window pipeline

The final privacy-safe rerun reproduced the Phase 1 findings:

| Measure | Result |
|---|---:|
| Dataset version | V1.0.4 |
| Audited CSV files | 62 |
| Audited rows | 386,564 |
| CGM rows | 356,146 |
| Nutrition rows | 4,351 |
| Bolus rows | 5,660 |
| Basal rows | 20,407 |
| Participants with CGM, nutrition, and insulin | 15 |
| Participants with all four core modalities | 13 |
| Invalid timestamps | 0 |
| Invalid numeric values | 0 |
| Blank required fields | 844 |
| Repeated timestamps | 16,099 |
| Conflicting CGM timestamp groups | 253 |
| Valid loaded meals evaluated | 3,884 |
| Eligible meal windows | 927 |
| Eligibility yield | 23.87% |

Each accepted example has 24 pre-meal CGM points, model-visible prior context, and 24 held-out
future CGM points on a five-minute grid. First-failure rejections remained 771 follow-up meals,
1,281 incomplete histories, 451 incomplete targets, and 454 missing insulin contexts.

### Forecasting feasibility

The final pinned Chronos-2 CPU rerun completed successfully:

| Measure | Closure rerun |
|---|---:|
| Model | `amazon/chronos-2` |
| Revision | `29ec3766d36d6f73f0696f85560a422f50e8498c` |
| Context | CGM-only |
| History points | 24 |
| Forecast points | 24 |
| Quantiles | q10, q50, q90 |
| Model load | 22.609249 s |
| First adapter call | 117.2004 ms |
| Warm calls | 10 |
| Warm latency p50 | 53.93535 ms |
| Warm latency p95 | 80.0512 ms |
| Observed inference peak RSS | 810.91 MiB |
| Validation | Passed |

These machine-specific values refresh the technical smoke evidence. They are not an accuracy
benchmark. The required Milestone 2 benchmark will compare Chronos-2 with persistence across a
participant-aware evaluation split.

### Application and database

- The API and PWA contract carries 24 observed points, 24 forecast points, q10/q50/q90, and
  30/60/120-minute summaries without identifiers or absolute timestamps.
- Three frontend test files passed all five behavior tests.
- ESLint, TypeScript generation/checking, and the Next.js production build passed.
- The local database clean reset passed using Supabase CLI 2.118.0 with generated connection
  details suppressed.
- Database lint found no errors in the `public` or `extensions` schemas.
- All 20 pgTAP database tests passed.
- Four static database/privacy tests also passed as part of the complete Python suite.

The machine's older Supabase CLI 2.31.4 encountered an auxiliary log-collector/Docker health
failure during the closure rerun. The SQL migration still applied and its lint and pgTAP checks
passed. Repeating the full clean-reset gate with the current CLI 2.118.0 passed. Updating the
machine-installed CLI before the next database phase is recommended.

### Simulator feasibility

The explicit real integration suite passed all 11 tests in 11.38 seconds, including two real
executions of the pinned upstream scenario and a byte-for-byte reproducibility comparison.

| Measure | Result |
|---|---:|
| Upstream commit | `b985f8c2ea385d1b2b8480957b730866e07772f1` |
| Model/controller | ExtHovorka / OpenLoop |
| Duration | 1,440 minutes |
| Sampling interval | 5 minutes |
| Samples | 288 |
| Synthetic meal events | 3 |
| Simulated glucose range | 106.62–141.78 mg/dL |
| Mean simulated glucose | 118.62 mg/dL |
| Repeated result | Byte-identical |

This proves deterministic software execution only. It does not validate physiology or treatment.

### Presentation artifact

The final presentation is
[`GlycoLens_Milestone_1_Closure.pptx`](../presentations/GlycoLens_Milestone_1_Closure.pptx).

| Check | Result |
|---|---:|
| Slides | 7 |
| Editable native charts | 2 |
| Editable native tables | 1 |
| Speaker-note sections | 7 |
| File size | 4,236,953 bytes |
| SHA-256 | `bd6a097c837b6f93b485f3af9320b57300a3ae08a39f56dcdf883e5fd53505f2` |
| Package-integrity findings | 0 |
| Layout findings/warnings | 0 / 0 |
| Artifact Tool re-import | Pass |
| Full-slide visual review | Pass |

The deck uses the approved RIT template, retains editable evidence, follows a five-to-six-minute
narrative, and includes explicit research and no-dosing boundaries.

## Final regression and quality record

| Closure gate | Result |
|---|---|
| Ruff format check | Pass: 85 files already formatted |
| Ruff lint | Pass |
| Full Python suite | Pass: 73 passed, 1 explicit simulator opt-in skip |
| Real py-mgipsim integration | Pass: 11 passed |
| Python bytecode compilation | Pass |
| Repository skill validation | Pass: 9 skills, 0 failures |
| Frontend ESLint | Pass |
| Frontend behavior tests | Pass: 3 files, 5 tests |
| TypeScript | Pass |
| Next.js production build | Pass |
| Clean local database reset | Pass with Supabase CLI 2.118.0 |
| Database lint | Pass: no errors |
| Database behavior suite | Pass: 20 pgTAP tests |
| Graphify status | Active: 1,293 nodes, 1,896 edges, 166 communities |
| Graphify closure query | Located data, adapter, API, UI, database-report, and simulator evidence; source-verified |
| Private academic-address domain scan | Pass: 0 files |
| Absolute local-path scan | Pass: 0 files |
| Presentation privacy scan | Pass: 0 address or absolute-path parts |
| `git diff --check` | Pass |

Graphify remains intentionally code-only. Documentation, local datasets, secrets, generated
artifacts, model weights, and local database state were not semantically ingested.

## Safety and scope audit

**Blocking findings:** none.

Verified controls include:

- future CGM truth remains outside model requests;
- post-meal insulin cannot satisfy pre-meal context;
- malformed grids, non-finite values, and crossing quantiles fail closed;
- research and application data boundaries remain explicit;
- public demo data are synthetic and identifier-free;
- database RLS and owner isolation are executable and tested;
- local endpoints, keys, project references, and credentials remain ignored and undisclosed;
- simulator output omits identifiers, absolute timestamps, individual insulin values, and dose
  fields; and
- UI, reports, and presentation state that forecasts are uncertain, non-clinical, and not for
  insulin dosing or treatment decisions.

## Residual limitations carried into Milestone 2

1. The 927 windows establish usable volume, not population representativeness; there are only 17
   participants, with 15 contributing the initial multimodal cohort.
2. Chronos-2 has passed a one-window technical smoke, not a participant-level accuracy benchmark.
3. TimesFM remains an optional comparison and has not been integrated.
4. Nutrition and insulin context are represented in the common contract, but Chronos-2 Phase 3 is
   intentionally CGM-only and rejects unsupported covariates.
5. The API/PWA vertical slice uses synthetic transport data; the real model is not in the request
   path.
6. The simulator is an offline research tool and is not integrated with the app or database.
7. Playwright end-to-end testing remains appropriate when the complete meal-to-forecast workflow
   exists; it is not a Milestone 1 blocker.
8. No hosted Supabase project was linked or modified.

## Milestone 2 entry plan

1. Freeze participant-aware train/validation/test definitions and benchmark persistence versus
   Chronos-2 with MAE, RMSE, horizon-specific error, calibration/probabilistic metrics, latency,
   memory, and unusable-run rate.
2. Run the planned context ablation: CGM-only, CGM plus insulin, and CGM plus insulin and nutrition.
3. Implement meal/nutrition capture and validation while preserving source provenance.
4. Connect validated research outputs to the application boundary without loading research rows
   into the app database.
5. Add a critical Playwright flow once `meal -> nutrition -> forecast -> UI` exists.
6. Ask the advisor to confirm the primary evaluation metric set and whether TimesFM should remain
   optional.

## Documentation governance impact

| Document | Role | Closure action |
|---|---|---|
| `GlycoLens_01_Updated_Project_Summary.md` | Primary scope summary | Updated with final M1 closure |
| `GlycoLens_06_Milestones_and_Schedule.md` | Primary milestone source | Updated from outstanding to complete |
| `GlycoLens_08_Risks_Safety_and_Scope.md` | Primary safety source | Reviewed; controls remain consistent |
| `GlycoLens_09_Project_Specification_Draft.md` | Primary specification | Updated with closure evidence |
| `docs/presentations/README.md` | Artifact inventory | Updated with validated deck |
| `docs/reports/README.md` | Report navigation | Updated with this audit |
| `docs/testing/test-strategy.md` | Validation strategy | Updated with final closure gate |
| Other planning documents | Supporting detail | Reviewed; no closure-specific change required |
