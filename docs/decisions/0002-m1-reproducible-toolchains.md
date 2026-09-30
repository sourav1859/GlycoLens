# ADR 0002: Milestone 1 reproducible toolchains

- **Status:** Accepted
- **Date:** September 29, 2026

## Context

Milestone 1 needs repeatable Python research validation and a buildable mobile-first web
foundation. The repository previously depended on globally installed tools and contained no
project dependency manifests or lockfiles.

## Decision

- Pin Python to 3.12.5 through `.python-version` and manage the environment with uv.
- Keep the initial Python dependency set limited to tools exercised by current code: pytest and
  Ruff. Backend, model, data-science, and simulator dependencies will be added with their
  implementations rather than preinstalling unused packages.
- Use Node.js 22 and pnpm 10.0.0 for the workspace.
- Pin exact frontend package versions and commit the pnpm lockfile.
- Add a minimal Next.js/TypeScript application shell solely to prove that linting, type checking,
  and production builds are reproducible. Forecast UI and API integration remain later M1 work.
- Keep all dependencies in the modular monolith; this decision does not introduce services or a
  product GraphRAG component.

## Alternatives considered

### Continue using global environments

Rejected because successful execution would depend on one workstation and could not be reliably
recreated by reviewers.

### Use npm instead of pnpm

Credible, but pnpm was selected for strict lockfile behavior, workspace support, and efficient
local storage. The choice is reversible because the frontend is currently a single package.

### Add all planned ML and backend packages immediately

Rejected because it would create a large, slow environment before the corresponding code and
compatibility tests exist. Dependencies will be introduced and pinned phase by phase.

## Consequences

- A fresh clone has explicit Python and JavaScript setup commands.
- Lockfiles become required review artifacts.
- Node 22 and Python 3.12 are the supported Milestone 1 development runtimes.
- The initial frontend is a toolchain smoke shell, not evidence that the browser-to-API M1
  requirement is complete.

## Validation and rollback

Validate with `uv sync --frozen`, Python lint/format/tests, `pnpm install --frozen-lockfile`,
frontend lint/type-check, and a production Next.js build. Python formatting targets executable
source and tests rather than code examples embedded in planning Markdown. If pnpm becomes
unsuitable, remove the workspace configuration and regenerate a lockfile with the selected
replacement after recording a new ADR.
