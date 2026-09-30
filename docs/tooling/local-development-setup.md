# Local Development Setup

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

Frontend component tests are now part of the standard validation. Playwright remains future work
for the complete meal-to-forecast flow.
