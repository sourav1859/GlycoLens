# GlycoLens

**AI-Assisted Meal Understanding and Personalized Glucose Response Prediction for Type 1 Diabetes**

GlycoLens is an inference-first, application-first capstone project. It combines verified meal nutrition, recent Type 1 Diabetes context, pretrained time-series forecasting, and personal meal-history retrieval to help users understand possible post-meal glucose behavior.

> **Research and education only:** GlycoLens does not recommend insulin doses, change clinician settings, or control an insulin pump. Forecasts are estimates and are not medical advice.

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

The system is designed as a modular monolith with replaceable forecasting-model adapters.

## Repository layout

```text
frontend/              Next.js mobile-first PWA
backend/               FastAPI application and model adapters
research/              Data preparation, experiments, and evaluation
database/              Schema migrations and seed data
data/                  Local data layout; sensitive/raw data is ignored
artifacts/             Local model and experiment artifacts
docs/planning/         Living source-of-truth project documents
docs/presentations/    Capstone presentation and RIT template
docs/architecture/     Architecture diagrams and technical notes
docs/decisions/        Architecture decision records
docs/reports/          Milestone and final reports
.agents/skills/        Repository-scoped Codex workflows
scripts/               Development and research utilities
tests/                 Cross-system integration and end-to-end tests
```

The repository contains an executable T1D-UOM V1.0.4 audit and leakage-safe meal-window generator,
common forecast adapters, a pinned Chronos-2 smoke path, a typed FastAPI demonstration endpoint,
and a mobile-first Next.js forecast chart. A pinned, isolated py-mgipsim scenario also provides a
deterministic virtual-patient feasibility path. The browser flow uses deterministic synthetic data;
real-data and simulator artifacts remain separate local-only commands.

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
and validated [Milestone 1 presentation](docs/presentations/GlycoLens_Milestone_1_Closure.pptx)
are available in the presentation inventory. The
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

Repository initialized from the approved GlycoLens planning pack. The T1D-UOM audit and meal-window
preprocessing slice is implemented and verified. Reproducible Python and frontend toolchains and a
mobile-first Next.js app are implemented. The common forecast contract, leakage-safe T1D-UOM
converter, and persistence baseline are implemented and tested on a real eligible window;
the pinned Chronos-2 model also completes a validated 24-point CPU smoke forecast and produces a
local research graph. A typed FastAPI endpoint and accessible browser forecast chart complete the
dummy browser-to-API criterion. The executable local Supabase migration, constraints, pgvector
extension, synthetic seed, and RLS isolation tests are also complete. The simulator demonstration
is installed through an isolated pinned environment and completes deterministically. The validated
RIT-branded presentation and final closure audit are complete. **Milestone 1 is closed; Milestone 2
benchmarking, context ablation, and nutrition-flow implementation are next.**
