# Milestone 1 Phase 1: Reproducible Toolchain Report

**Date:** September 29, 2026
**Scope:** Python and frontend dependency management, buildable application shell, quality gates,
and documentation synchronization.

## Outcome

Phase 1 established reproducible local environments for the current GlycoLens research code and
the planned mobile-first web client. Python and frontend dependencies are now declared and locked,
and the minimal Next.js shell passes linting, strict type checking, and a production build.

This phase does not implement the forecast adapter, FastAPI backend, database schema, simulator,
or browser-to-backend flow.

## Pinned toolchain

| Area | Selection | Reproducibility control |
|---|---|---|
| Python | CPython 3.12.5 | `.python-version` |
| Python environment | uv 0.9.18 used for validation | `pyproject.toml` and `uv.lock` |
| Python quality/test | pytest 9.1.1, Ruff 0.16.9 | exact manifest pins and lockfile |
| Node.js | 22.x; 22.14.0 used for validation | root `engines` constraint |
| JavaScript package manager | pnpm 10.0.0 | root `packageManager` field |
| Web application | Next.js 16.3.7, React 19.3.0 | exact pins and `pnpm-lock.yaml` |
| TypeScript | 6.0.3 | exact pin and strict `tsconfig.json` |

Backend, forecasting-model, data-science, database, and simulator packages remain absent until the
phase that introduces exercised code for them.

## Validation traceability

| Requirement or risk | Validation | Evidence on September 29 | Result |
|---|---|---|---|
| Locked Python environment is installable | `uv sync --frozen` | 7 packages installed from `uv.lock` | Pass |
| Existing research behavior is preserved | `uv run pytest -q` | 12 tests passed | Pass |
| Python imports and syntax remain valid | `uv run python -m compileall -q research tests scripts` | No errors | Pass |
| Python lint rules pass | `uv run ruff check .` | All checks passed | Pass |
| Executable Python paths are formatted | `uv run ruff format --check research tests scripts` | No changes required after normalization | Pass |
| Repository skills contain no literal private addresses | `uv run python scripts/quality/validate_skills.py` | 9 skills, 0 failures | Pass |
| Locked frontend environment is installable | `pnpm install --frozen-lockfile` | Workspace install completed | Pass |
| Frontend lint configuration executes | `pnpm frontend:lint` | Zero warnings/errors | Pass |
| Frontend types are strict and valid | `pnpm frontend:typecheck` | Framework types regenerated and no TypeScript errors after deleting `.next` | Pass |
| Production application shell compiles | `pnpm frontend:build` | Static `/`, `/_not-found`, and manifest routes built | Pass |
| Developer knowledge graph reflects code changes | `Update-Graphify.ps1` in code-only mode | 804 nodes, 852 edges, 121 communities | Pass |

## Boundary and risk notes

- The web page is a toolchain smoke shell, not completion of the M1 browser-to-backend criterion.
- The shell includes the research-only/no-medical-advice boundary, but complete accessibility and
  end-to-end safety tests belong with the interactive forecast UI.
- Next.js 16.3.7 currently resolves lint plugins whose peer ranges support ESLint 9 but not ESLint
  10. ESLint 9.39.5 is therefore pinned despite its registry end-of-support warning. Reassess this
  pin when the Next.js lint dependency chain supports ESLint 10.
- pnpm build-script execution is restricted to the exact native packages required by this
  dependency graph (`sharp` and `unrs-resolver`).
- `NEXT_PUBLIC_API_URL` is safe for the future public backend origin only; credentials must never
  use the `NEXT_PUBLIC_` prefix.
- Documentation semantic extraction remains disabled because it requires an approved external
  backend. The explicit Graphify refresh updated local code nodes only; source documentation is
  authoritative.

## Next implementation step

Proceed to Phase 2: define the common forecast contract, implement the deterministic persistence
baseline, and add leakage, shape, timestamp, quantile, invalid-input, and mutation tests.
