# Local Development Setup

## Current default - local app processes with cloud Supabase

The user selected a dedicated **cloud Supabase development project from now on**.
Follow [cloud setup](cloud-supabase-setup.md), [ADR 0018](../decisions/0018-cloud-supabase-and-staged-webapp-delivery.md)
and [plan 17](../planning/GlycoLens_17_Webapp_Implementation_Plan.md). Local frontend/API
development can use that project; a local Supabase stack is no longer required for
new app integration. Docker remains useful for packaging, not a reason to start a
local DB. The local Supabase start/reset/Configure-LocalDemo commands below are
historical instructions and must not be used to replace cloud configuration.
Cloud-safe setup/test runners are planned, not yet implemented.

## Current implementation scope

The repository contains the research-data pipeline, common forecast adapters, a typed FastAPI
demonstration service, and a Next.js forecast visualization. The pinned Chronos-2 dependency group
supports opt-in model smoke and local plot commands. The local Supabase database migration and RLS
tests are implemented. The source-only py-mgipsim simulator is implemented in a separate pinned,
ignored environment so it does not alter the application/model dependency graph.

## Prerequisites

- Git
- PowerShell 7 preferred; Windows PowerShell can run the current bootstrap wrappers
- Python 3.12.5 for the current research and validation environment
- uv 0.9 or later for Python environment and lockfile management
- Node.js 22
- pnpm 10.0.0, as pinned in the root `package.json`
- Docker Desktop for the local Supabase stack
- Supabase CLI 2.x for migrations, reset, lint, and pgTAP
- Codex when using the repository-scoped skills
- network access for the first py-mgipsim source/dependency installation only

Verify tools without installing missing runtimes automatically:

```powershell
git --version
pwsh --version
python --version
uv --version
node --version
pnpm --version
codex --version
docker --version
supabase --version
```

## Install and validate

From the repository root:

```powershell
uv sync --frozen
uv run ruff check .
uv run ruff format --check backend research tests scripts
uv run pytest -q
uv run python -m compileall -q backend research tests scripts
uv run python scripts/quality/validate_skills.py

pnpm install --frozen-lockfile
pnpm frontend:lint
pnpm frontend:test
pnpm frontend:typecheck
pnpm frontend:build
```

Install the optional pinned pretrained-model group only when working on Chronos-2:

```powershell
uv sync --all-groups --frozen
uv run --all-groups python -m research.pipelines.run_chronos2_smoke --allow-model-download
uv run --all-groups python -m research.pipelines.render_chronos2_forecast --allow-model-download
```

The smoke command stores the checkpoint under ignored `artifacts/models/` and the aggregate
measurement record under ignored `artifacts/benchmarks/`. It never writes row-level health data.

Install and run the isolated virtual-patient simulator:

```powershell
./scripts/simulation/Install-PyMgipsim.ps1
uv run python -m research.pipelines.run_pymgipsim_scenario --allow-upstream-execution
```

The installer verifies official commit `b985f8c2ea385d1b2b8480957b730866e07772f1` and synchronizes
68 exact packages from `research/simulation/pymgipsim-requirements.lock`. Source and environment
stay in ignored `.cache/` directories; validated results stay in ignored `artifacts/simulation/`.
The scenario exports relative-time simulated glucose and aggregate meal metadata only. It is not
clinical evidence or dosing guidance.

Use the lockfiles rather than installing unpinned packages globally. A developer may run only the
Python checks when working solely on the research pipeline, but the full validation runs both
toolchains.

Start the local demonstration in two terminals:

```powershell
uv run uvicorn backend.app.main:app --reload
pnpm frontend:dev
```

The frontend defaults to `http://127.0.0.1:8000` and may be pointed at another public API origin
with `NEXT_PUBLIC_API_URL`. Configure the corresponding explicit server allowlist with
`GLYCOLENS_CORS_ORIGINS`; never use a wildcard or place credentials in a public variable.

## Local database validation

Initialize a generated, ignored local configuration once per clone:

```powershell
supabase init
```

Do not commit `supabase/config.toml` or copy generated local endpoints and keys into project
documents. Start Docker Desktop, then run:

```powershell
./scripts/database/Test-LocalSupabase.ps1
```

The wrapper suppresses generated connection output, rebuilds the local database, applies the
migration and synthetic seed, lints the schema, and runs pgTAP authorization tests. It neither
logs into Supabase nor links, pushes, or changes a hosted project.

The Milestone 1 closure gate passed with Supabase CLI 2.118.0. The older machine-installed 2.31.4
build encountered an auxiliary logging-container health failure with the current Docker Desktop
even though the migration, lint, and pgTAP checks succeeded. If the wrapper reports a local-stack
startup/reset failure on an older 2.x CLI, update the CLI and rerun; do not copy diagnostic
connection output or generated keys into project files.

## Repository workflow

1. Read `AGENTS.md` and affected planning documents.
2. Work on a focused local branch.
3. Define acceptance criteria and relevant test layers.
4. Use Graphify when it is installed and current, then verify source files.
5. Implement and validate the change.
6. Update living documentation and the impact ledger when applicable.
7. Inspect `git diff --check` and `git status --short` before handoff.

Never place credentials, private health records, downloaded datasets, model weights, or generated Graphify output in Git.

## Available bootstrap validation

```powershell
python scripts/quality/validate_skills.py
```

Frontend component tests and executable Playwright desktop/mobile flows are configured.
See the M2 instructions below for opt-in real simulator/model browser checks.

## Milestone 2 local application

After starting local Supabase, run `scripts/dev/Configure-LocalDemo.ps1`. This writes
ignored server `.env` and frontend `.env.local`, preserving unrelated entries, and
enables local anonymous Auth. Restart only the local stack to apply this setting.
Do not copy generated values to documentation or ChatGPT. Configure USDA_FDC_API_KEY,
LLM_API_KEY and LLM_MODEL privately; recipe extraction uses the prepared OpenAI
Responses adapter. No recipe model default or paid call is selected automatically.
OPEN_FOOD_FACTS_USER_AGENT defaults to GlycoLens/0.1; add contact identification privately.
The dataset root may be passed explicitly to research commands without writing a public path.

The working runtimes are Python 3.12.5, Node 22.14.0, pnpm 10.0.0 and uv 0.9.18.
M2 adds timesfm[torch]==3.0.2 in a locked optional group; use `uv sync --all-groups --frozen`.
Normal Python/pnpm access can fail in a restricted execution sandbox even when the
user environment is intact; do not rebuild environments based only on that symptom.

The workspace can use Supabase 2.118.0 from ignored `.cache/local-tools`:
install its npm package there and pass the executable to
`Test-LocalSupabase.ps1 -SupabaseExecutable ./.cache/local-tools/node_modules/.bin/supabase.cmd`.
No global CLI replacement is required. That wrapper resets the local synthetic database.
Back up any non-synthetic local work before deliberately reusing it on such a database.

October 14 Docker restart exposed PostgreSQL collation metadata 153.120 versus 153.121.
The reviewed repair rebuilt indexes and refreshed metadata in template1 as its owner
supabase_admin and in postgres as postgres; the full local stack then started.
Do not repeatedly reinstall tools or delete volumes for this failure. Confirm the
specific mismatch before any metadata repair. The auxiliary Docker vector log shipper
is distinct from PostgreSQL pgvector and from product retrieval.

Run from the repository root:

```powershell
uv run python scripts/dev/check_m2_prerequisites.py
uv run python -m research.pipelines.build_benchmark_manifest
uv run --all-groups python -m research.pipelines.run_m2_benchmark --allow-model-download --contexts cgm_only cgm_insulin cgm_insulin_carbohydrates cgm_insulin_nutrition
uv run --all-groups python -m research.pipelines.summarize_m2_benchmark artifacts/evaluation-results/m2-validation.json --freeze-run chronos2:cgm_insulin_nutrition
uv run --all-groups python -m research.pipelines.run_m2_benchmark --split test --frozen-selection artifacts/evaluation-results/m2-selection.json --contexts cgm_only cgm_insulin cgm_insulin_carbohydrates cgm_insulin_nutrition --output artifacts/evaluation-results/m2-test.json
uv run python -m research.pipelines.report_m2_results
uv run --all-groups python -m scripts.dev.check_m2_application --allow-live-local
```

Set GLYCOLENS_T1D_UOM_ROOT privately or use --dataset-root for research commands.
Test evaluation must follow validation selection; never use test errors to reselect.

The frontend uses local public Supabase configuration for Auth, and the backend verifies
the user token. Launch FastAPI/pnpm dev with the existing commands. The M1 synthetic
endpoint remains available for contract tests; the default page is the real simulated flow.
For browser tests, install Chromium into an ignored workspace cache and set
PLAYWRIGHT_BROWSERS_PATH to that directory. Run `pnpm --dir frontend e2e`; add
GLYCOLENS_LIVE_E2E=1 for real local Auth/simulator/model flows. Playwright starts and
stops its own local servers, uses one worker, and generates ignored screenshots/traces.
