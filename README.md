# GlycoLens

## Milestone 3 presentation and advisor report

Prepared November 16 for the November 17 presentation: [PowerPoint](docs/presentations/GlycoLens_Milestone_3_Presentation_2026-11-17.pptx), [timed speaker notes](docs/reports/GlycoLens_Milestone_3_Presentation_Notes.docx), and [advisor report](docs/reports/GlycoLens_Milestone_3_Advisor_Report_2026-11-16.docx). The deck has ten main slides and four hidden backups, with a 7:30 rehearsal target. The package reports core implementation, qualified test evidence and ongoing Kaggle recipe ingestion; preparation does not close outstanding acceptance or constitute a new model-accuracy study.

November 14 catalog review: the [Azure gold assessment](docs/reports/azure-nutrition-catalog-assessment-2026-11-06.md)
and [migration strategy](docs/reports/azure-to-supabase-catalog-migration-strategy-2026-11-06.md)
now cover 33,194 source-ready recipe candidates, 5,429 ingredients, 11,397 products,
dependency closure, quality gates and current cloud capacity. The evidence-bearing
package is estimated at 151.90 MiB CSV / 50.61 MiB gzip. No catalog import or
activation has occurred; source readiness does not establish verified nutrition.

## November 14: personal and simulation workspaces implemented

Personal meal logging and current timezone-aware dates are independent of the `/demo` virtual workspace. Earlier simulated meals remain under Simulation meals/Saved sessions. Cloud-dev migration is applied and local Compose is updated. See [Plan 19](docs/planning/GlycoLens_19_Personal_and_Simulation_Workspaces.md) and [actual validation](docs/reports/workspace-separation-validation-2026-11-14.md); automated evidence is recorded, manual acceptance remains partial.

## Start the local app with Docker

With Docker Desktop running, the existing ignored root `.env` configured and the
reviewed Chronos cache in `artifacts/models/huggingface`, run from this directory:

```powershell
docker compose up --build -d --wait
```

Open <http://127.0.0.1:3000>; the API is <http://127.0.0.1:8000>.
Stop manually launched services on those ports first, or use the documented port
overrides. `docker compose down` stops the stack and retains simulation data.
Cloud Supabase remains external and needs internet. The first build downloads
dependencies; this is a built-image workflow. See [prerequisites, runtime smoke,
replay and troubleshooting](infra/README.md), [ADR 0021](docs/decisions/0021-local-compose-runtime.md)
and [November 12 validation](docs/reports/demo-logout-compose-review-2026-11-12.md).

Current development: **one repo, managed cloud Supabase**, permanent email/password
accounts and minimal resumable onboarding, responsive routes, reviewed meal
capture/history/edit/cancel, frozen Chronos forecasts, Home/nutrition, owned
notifications/export and portion/later-observation workflows. The original demo is
at `/demo`. See the [implementation checkpoint](docs/reports/webapp-implementation-checkpoint-2026-11-11.md),
[phase plan](docs/planning/GlycoLens_17_Webapp_Implementation_Plan.md),
[146-case actual ledger](docs/testing/webapp-validation-results.json) and
[cloud setup](docs/tooling/cloud-supabase-setup.md).

This is a development checkpoint with partial phase acceptance. Corrected catalog,
real email delivery, verified anonymous upgrade, provider retention/restore, physical/manual
UAT, scratch replay/restore and hosted acceptance remain open. The user authorized
[GitHub publication of this checkpoint](docs/reports/github-checkpoint-delivery-2026-11-12.md)
on November 12; the earlier local-review hold is superseded. Public deployment
remains a separate gate.
OpenAI recipe extraction uses server-only `gpt-6-luna`; no new paid calls were made
in these implementation checks. Prior estimated USD 0.00763580 counts against the
approved USD 5 test cap. Figma patterns were adapted to GlycoLens, with no copied
Nutri-App assets/branding or sample nutrition facts.

Immediate password-confirmed account deletion now has no recovery window. See
[ADR 0020](docs/decisions/0020-immediate-account-deletion.md) and
[validation](docs/reports/account-deletion-validation-2026-11-11.md). Provider
backup/log retention and restore reconciliation remain public-release gates.

The [repository strategy and development-readiness review](docs/reports/repository-strategy-and-development-readiness-2026-11-10.md)
recommends retaining the monorepo and identifies the environment, CI, contract,
schema and deployment work to complete as development proceeds.

**AI-Assisted Meal Understanding and Personalized Glucose Response Prediction for Type 1 Diabetes**

GlycoLens is an inference-first, application-first capstone project. It combines verified meal nutrition, recent Type 1 Diabetes context, pretrained time-series forecasting, and personal meal-history retrieval to help users understand possible post-meal glucose behavior.

> **Research and education only:** GlycoLens does not recommend insulin doses, change clinician settings, or control an insulin pump. Forecasts are estimates and are not medical advice.

The user selected **Hostinger KVM 2 with managed Supabase** for initial deployment on
November 7. The VPS will host the PWA, FastAPI, CPU forecasting and simulator;
Supabase remains managed externally. [ADR 0016](docs/decisions/0016-initial-hostinger-kvm2-managed-supabase.md)
records the decision, cost assumptions and readiness gates. Implementation and
hosted verification are pending in the [M3 deployment checklist](docs/planning/GlycoLens_06_Milestones_and_Schedule.md#initial-hostinger-kvm-2-deployment).

The November 6 [Azure to Supabase catalog strategy](docs/reports/azure-to-supabase-catalog-migration-strategy-2026-11-06.md)
records measured storage and a proposed compact food-data copy. The user confirmed that
recipe data is being corrected upstream; recipe use and migration remain deferred until
a corrected release passes validation. No application integration or cloud import is complete.
The [Milestone 3 checklist](docs/planning/GlycoLens_06_Milestones_and_Schedule.md#corrected-nutrition-catalog-migration-from-milestone-2)
tracks migration execution; the completed audit and strategy remain Milestone 2 evidence.

The approved October 16 model-refinement work is tracked in
[protocol and phase ledger](docs/planning/GlycoLens_11_Model_Refinement.md),
[execution results](docs/reports/model-refinement-results-2026-10-16.md) and
[research commands](research/README.md#approved-model-refinement). It compares longer
frozen Chronos histories with small trained direct/residual models and a separately
reserved AZT1D test. +/-10 mg/dL is aspirational. Original M2 results remain intact;
the application model is not automatically replaced. MetaboNet v1.2 files have now
been received and [audited](docs/reports/metabonet-intake-audit-2026-10-16.md);
Small-model training is now complete. The supplied test mixes shared and unseen participants.
The approved [Phase 2 preparation](docs/reports/metabonet-phase2-preparation-2026-10-16.md)
is now complete: fixed Loop/ReplaceBG subject roles, 8,973/2,000/1,948 six-hour
training/validation/calibration windows and metadata-only reserved tests. See the
[new experiment protocol](docs/planning/GlycoLens_12_MetaboNet_Experiment.md) and
[preparation commands](research/README.md#metabonet-phase-2-preparation).
Phase 3 frozen-inference validation is now complete on 1,509 matched events.
Persistence won among failure-free options (macro MAE 37.12 mg/dL; six-hour C2 37.61),
so the improvement gate failed. Longer histories improved conditional point accuracy
but had native-output failures. The original Phase 3 evidence is preserved. See
[the results](docs/reports/metabonet-phase3-inference-2026-10-16.md),
[protocol 13](docs/planning/GlycoLens_13_MetaboNet_Frozen_Inference.md) and
[commands](research/README.md#metabonet-phase-3-frozen-inference). No reserved test
values were used and no app model switch follows from these validation scores.

**Phase 4 is complete.** Training-only CV chose
24-hour event features for Ridge and LightGBM. On the same 1,509 validation meals,
LightGBM reduced macro MAE to **31.17 mg/dL**, 16.03% below persistence, passing the
research gate. Within +/-10 remains poor at **26.84%** (Ridge 28.85%); the maximum
error was 235.38 mg/dL. At Phase 4 completion calibration/reserved tests were untouched; Phase 6 below now records their use. See
[Phase 4 results](docs/reports/metabonet-phase4-training-2026-10-16.md),
[protocol 14](docs/planning/GlycoLens_14_MetaboNet_Direct_Models.md) and
[commands](research/README.md#metabonet-phase-4-direct-training).

**Historical Phase 5 result, before Phase 6 below.** Frozen C2 generated 6,756 training forecasts;
6,756 usable meals / 196 identities supported six CV configurations / 18 fold fits and
four final refits, with exactly matched direct controls. Neither correction passed the
predeclared incremental gate; retain Phase 4 LightGBM. Lowest-MAE eligible option:
`ridge_residual_1000`; advancement candidate: `lightgbm_direct` (macro MAE 31.17 mg/dL,
within +/-10 26.84%). These are reused-validation findings, not independent
confirmation. At Phase 5 completion calibration/reserved outcomes were untouched; Phase 6 below supersedes that access status. App inference is unchanged; +/-10 precision remains weak.
See [Phase 5 results](docs/reports/metabonet-phase5-correction-2026-10-16.md), [protocol 15](docs/planning/GlycoLens_15_MetaboNet_Chronos_Correction.md) and [commands](research/README.md#metabonet-phase-5-chronos-correction).

## Core questions

GlycoLens helps explore:

1. What is in this meal?
2. How did similar meals affect the user previously?
3. Given current CGM and recent context, what is the forecast for the next two hours?
4. How might the predicted trajectory change with a different portion or meal composition?

## Planned stack

- **Frontend:** Next.js, TypeScript, mobile-first PWA
- **Backend:** FastAPI, Python, Pydantic
- **Database:** Supabase PostgreSQL with pgvector
- **Forecasting:** Chronos-2, TimesFM-3, optional CGMformer, persistence baseline
- **Nutrition:** USDA FoodData Central and Open Food Facts
- **CGM integration:** Dexcom Developer Sandbox
- **Simulation:** py-mgipsim
- **Testing:** Pytest and Playwright
- **Packaging:** Docker
- **Initial deployment:** Hostinger KVM 2 for app/inference/simulation; managed Supabase for database/Auth

The system is designed as a modular monolith with replaceable forecasting-model adapters.

## Repository layout

```text
frontend/              Next.js mobile-first PWA
backend/               FastAPI APIs and application service orchestration
research/              Canonical model adapters, data preparation and evaluation
supabase/              Executable app migrations, RLS tests and synthetic seed
database/              Database notes and pointers to the Supabase contract
data/                  Local data layout; sensitive/raw data is ignored
artifacts/             Local model and experiment artifacts
docs/planning/         Living source-of-truth project documents
docs/presentations/    Capstone presentation and RIT template
docs/architecture/     Architecture diagrams and technical notes
docs/decisions/        Architecture decision records
docs/reports/          Milestone and final reports
.agents/skills/        Repository-scoped Codex workflows
.codex/                Project Codex defaults and narrow custom agents
scripts/               Development and research utilities
tests/                 Cross-system integration and end-to-end tests
```

The repository contains an executable T1D-UOM V1.0.4 audit and leakage-safe meal-window generator,
common forecast adapters, a pinned Chronos-2 smoke path, a typed FastAPI demonstration endpoint,
and a mobile-first Next.js forecast chart. A pinned, isolated py-mgipsim scenario also provides a
deterministic virtual-patient path. The browser now supports authenticated live simulation,
confirmed meal persistence, a real Chronos-2 nutrition-context forecast, and numeric historical
retrieval. USDA/barcode and structured recipe adapters are implemented; live nutrition validation
awaits private API configuration. Research datasets/results remain separate from the app database.

## Reproducible development setup

Supported Milestone 1 runtimes are Python 3.12.5, Node.js 22, uv, and pnpm 10.0.0.

```powershell
uv sync --frozen
uv run ruff check .
uv run ruff format --check backend research tests scripts
uv run pytest -q

pnpm install --frozen-lockfile
pnpm frontend:lint
pnpm frontend:test
pnpm frontend:typecheck
pnpm frontend:build
```

The main lockfiles are authoritative. The source-only py-mgipsim tool uses a separate committed
requirements lock and ignored environment so its dependencies cannot change the application stack.

## Documentation policy

The planning documents in `docs/planning/` are living source-of-truth artifacts. Every substantive change to scope, models, datasets, preprocessing, experiments, evaluation, features, UX, architecture, APIs, database design, integrations, safety boundaries, deliverables, or schedule must update all affected planning documents in the same work cycle.

Start with:

- [Planning Pack README](docs/planning/GlycoLens_00_README.md)
- [Updated Project Summary](docs/planning/GlycoLens_01_Updated_Project_Summary.md)
- [Tech Stack and System Architecture](docs/planning/GlycoLens_04_Tech_Stack_and_System_Architecture.md)

See [AGENTS.md](AGENTS.md) for the repository working rules.

Developer setup and workflow documentation:

- [Local development setup](docs/tooling/local-development-setup.md)
- [Repository-scoped Codex skills](docs/tooling/codex-skills.md)
- [Codex token-efficient workflow](docs/tooling/codex-token-efficiency.md)
- [Graphify integration](docs/tooling/graphify.md)
- [Test strategy](docs/testing/test-strategy.md)
- [Measurement protocol](docs/benchmarks/measurement-protocol.md)

## Milestone 1 data pipeline

Set `GLYCOLENS_T1D_UOM_ROOT` to the extracted, ignored T1D-UOM V1.0.4 release and run:

```powershell
python -m research.pipelines.audit_t1d_uom
python -m research.pipelines.build_meal_windows --limit 1
uv run python -m research.pipelines.run_persistence_baseline
uv run --all-groups python -m research.pipelines.run_chronos2_smoke --allow-model-download
uv run --all-groups python -m research.pipelines.render_chronos2_forecast --allow-model-download
./scripts/simulation/Install-PyMgipsim.ps1
uv run python -m research.pipelines.run_pymgipsim_scenario --allow-upstream-execution
uv run pytest -q
```

The commands emit aggregate metadata only; they do not write row-level health data or generated
windows into Git. See the [Milestone 1 data-pipeline report](docs/reports/milestone-1-data-pipeline-implementation.md),
[Phase 2 forecast-contract report](docs/reports/milestone-1-phase-2-forecast-contract.md),
[Phase 3 Chronos-2 smoke report](docs/reports/milestone-1-phase-3-chronos2-smoke.md),
[Phase 4 API and visualization report](docs/reports/milestone-1-phase-4-api-visualization.md),
[Phase 5 local-database report](docs/reports/milestone-1-phase-5-local-database.md), and
[Phase 6 py-mgipsim report](docs/reports/milestone-1-phase-6-pymgipsim-scenario.md). The final
[Milestone 1 closure audit](docs/reports/milestone-1-closure-audit.md) maps every requirement to
evidence. The [project-specification presentation](docs/presentations/Sourav%20Patil-GlycoLens_Project_Specification.pptx)
and revised eight-slide [Milestone 1 presentation](docs/presentations/GlycoLens_Milestone_1_Presentation_v2.pptx)
are available in the presentation inventory. The [detailed presentation notes](docs/reports/GlycoLens_Milestone_1_Presentation_Notes_v2.docx),
[PDF reading copy](docs/reports/GlycoLens_Milestone_1_Presentation_Notes_v2.pdf), and
[Markdown source](docs/reports/GlycoLens_Milestone_1_Presentation_Notes_v2.md) provide the timed speech, detailed preparation, and 22 question answers.
The original closure deck remains available as historical evidence. The
Chronos commands require the local dataset-root environment variable and explicit model-download
acknowledgement. Checkpoints and generated figures remain in ignored artifact directories.

Run the local demonstration flow in two terminals:

```powershell
uv run uvicorn backend.app.main:app --reload
pnpm frontend:dev
```

Open `http://localhost:3000`. The browser calls `GET /api/v1/forecasts/demo`, which deliberately
returns a synthetic, identifier-free 24-point history and 24-point forecast for UI validation.

Validate the local database without printing generated connection details:

```powershell
supabase init  # once per clone; generated config is ignored
./scripts/database/Test-LocalSupabase.ps1
```

## Data and secret handling

Do not commit:

- CGM or health records containing personal information
- Dexcom OAuth tokens or client secrets
- USDA or other API keys
- `.env` files
- downloaded datasets
- model weights or checkpoints
- generated experiment outputs containing sensitive information

Use de-identified/public datasets, virtual-patient data, and the Dexcom sandbox unless the project receives explicit approval for real-user research.

## Status

The additional model-refinement sequence is complete through Phase 6; see the [independent results](docs/reports/metabonet-phase6-independent-2026-10-16.md). LightGBM improves average error, but +/-10 precision and pediatric uncertainty remain poor.

Milestone 2 phasewise implementation is approved and underway. See the
[implementation and evidence ledger](docs/planning/GlycoLens_10_Milestone_2_Implementation.md).
Run `python scripts/dev/check_m2_prerequisites.py` for a read-only report that
shows configuration presence without revealing secret values. Sandbox permission
errors must be distinguished from missing local tools; the normal M1 environments
remain operational. USDA and recipe API configuration are prerequisites for live
nutrition integration.

Repository initialized from the approved GlycoLens planning pack. The T1D-UOM audit and meal-window
preprocessing slice is implemented and verified. Reproducible Python and frontend toolchains and a
mobile-first Next.js app are implemented. The common forecast contract, leakage-safe T1D-UOM
converter, and persistence baseline are implemented and tested on a real eligible window;
the pinned Chronos-2 model also completes a validated 24-point CPU smoke forecast and produces a
local research graph. A typed FastAPI endpoint and accessible browser forecast chart complete the
dummy browser-to-API criterion. The executable local Supabase migration, constraints, pgvector
extension, synthetic seed, and RLS isolation tests are also complete. The simulator demonstration
is installed through an isolated pinned environment and completes deterministically. The validated
RIT-branded presentation and final closure audit are complete. **Milestone 1 is closed. Milestone 2
benchmarks, C0-C3 ablation and the live simulator/pretrained application flow are implemented.
The November 3 presentation draft and timed notes are revised in plain language for a 7–8 minute talk (target 7:30). Full M2 closure still
awaits live nutrition/recipe verification, physical camera testing and final acceptance.**

M2 results and checks:

- [November 3 Milestone 2 PowerPoint draft](docs/presentations/GlycoLens_Milestone_2_Presentation_2026-11-03_v4.pptx)
- [Matching timed speech and question preparation](docs/reports/GlycoLens_Milestone_2_Presentation_Notes.md)
- [October 26 advisor progress and experimentation report](docs/reports/GlycoLens_Milestone_2_Advisor_Report_2026-10-26.md) ([Word](docs/reports/GlycoLens_Milestone_2_Advisor_Report_2026-10-26.docx))
- [Model comparison and limitations](docs/reports/milestone-2-model-results.md)
- [Implementation verification](docs/reports/milestone-2-implementation-verification.md)

Initialize only the local demo configuration with `scripts/dev/Configure-LocalDemo.ps1`
after Supabase is running; restart the local stack to apply anonymous Auth. Keep USDA
and recipe keys in ignored `.env`. Run the real acceptance command from the root:
`python -m scripts.dev.check_m2_application --allow-live-local`.

The additional broader-data model-refinement sequence is complete through Phase 6. Frozen LightGBM's independent primary MAE is 29.91 mg/dL (18.74% below persistence), but only 28.20% of points are within +/-10. PEDAP MAE is 40.92 / within-10 19.57%, with nominal 80% marginal coverage only 63.94%. No app model switch or full-M2 closure. See [independent results](docs/reports/metabonet-phase6-independent-2026-10-16.md) and [current protocol](docs/planning/GlycoLens_16_MetaboNet_Independent_Evaluation.md).
