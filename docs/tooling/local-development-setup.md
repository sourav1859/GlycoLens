# Local Development Setup

## Current bootstrap scope

The repository contains architecture and ownership boundaries but no generated Next.js or FastAPI applications. Do not install product dependencies or run nonexistent builds during bootstrap.

## Prerequisites

- Git
- PowerShell 7 preferred; Windows PowerShell can run the current bootstrap wrappers
- Python 3.10 or later for validation, backend work, research, and Graphify
- `pipx` or `uv` for isolated Python command-line tools
- Node.js and a project-selected package manager once the frontend is scaffolded
- Codex when using the repository-scoped skills

Verify tools without installing missing runtimes automatically:

```powershell
git --version
pwsh --version
python --version
pipx --version
node --version
codex --version
```

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

Product test/build commands are intentionally absent until the corresponding toolchains exist.
