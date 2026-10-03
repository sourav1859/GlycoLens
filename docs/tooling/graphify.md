# Graphify Developer Knowledge Graph

## Status

**ACTIVE (code-only) as of October 1, 2026.** Graphify `0.9.69` is available from the ignored,
repository-local `.cache/graphify-venv` environment using Python `3.12.14`. The wrappers prefer an
explicit `GLYCOLENS_GRAPHIFY_EXECUTABLE`, then the repository-local executable, and finally a
`graphify` command on `PATH`. This fallback keeps the workflow operational if an older global
launcher points to a removed Python installation; no credentials or endpoint values are stored in
the repository.

The refreshed local graph contains 1,293 nodes, 1,896 edges, and 166 communities after the October
1 Milestone 1 current-state update. The closure query located the final audit, requirement matrix,
test-strategy gate, dataset pipeline, forecast contracts, Chronos-2 runner, and related tests; those
findings were verified against source. The earlier Phase 6 query also located the py-mgipsim
runner, result contract, isolated bridge, exact-commit verification, validators, and
reproducibility test.
Post-commit and post-checkout hooks plus the local merge driver are installed. Watch mode is
available but is not left running.

Semantic documentation/media extraction is **not active**. The graph was intentionally built with `--code-only`, so no repository documents were sent to a model backend.

The Phase 5 refresh reported that SQL AST extraction requires the optional `tree_sitter_sql`
dependency. The migration and pgTAP files were therefore validated directly by Supabase reset,
lint, and database tests rather than treated as Graphify evidence.

## Upstream findings

- Source: <https://github.com/Graphify-Labs/graphify>
- Inspected ref: `v8` documentation on September 27, 2026
- Official Python package: `graphifyy`; command: `graphify`
- Installed package version: `0.9.69` (pinned)
- Python requirement: 3.10 or later
- License metadata: MIT, with upstream repository license/notice files also present; recheck the selected release before installation
- Windows and Codex are documented platforms
- Code extraction uses local tree-sitter AST processing; documentation/media semantic extraction can use an assistant or configured model backend and may transmit content
- `.gitignore` is respected and `.graphifyignore` adds exclusions

No upstream skill or source text is vendored here. The GlycoLens skill and wrappers are original project workflows based on documented CLI behavior.

## Safe installation procedure

1. Recheck the official repository, package name, version, license, Python requirement, Windows notes, and `graphify --help`.
2. Install a specific verified version with `pipx install graphifyy==<version>` or the equivalent pinned `uv tool install` command. A repository-local virtual environment is also supported. The current installation uses `graphifyy==0.9.69` in `.cache/graphify-venv`, which is ignored by Git.
3. Do not run `graphify install --project` without reviewing its proposed changes; it can write `.agents/skills/graphify/SKILL.md` and `AGENTS.md`, which are maintained by GlycoLens.
4. Run `scripts/graphify/Test-GraphifyReadiness.ps1` and inspect `.gitignore` plus `.graphifyignore`.
5. Build a local code-only graph first. Enable semantic document extraction only with explicit approval and a verified backend/data boundary.

## Lifecycle commands

```powershell
./scripts/graphify/Test-GraphifyReadiness.ps1
./scripts/graphify/Initialize-Graphify.ps1
./scripts/graphify/Get-GraphifyStatus.ps1
./scripts/graphify/Invoke-GraphifyQuery.ps1 -Question "How are forecast adapters isolated?"
./scripts/graphify/Update-Graphify.ps1
# Only after explicit backend approval:
./scripts/graphify/Update-Graphify.ps1 -IncludeDocumentation -Backend openai
./scripts/graphify/Start-GraphifyWatch.ps1
```

The watcher remains in the foreground. Stop it with `Ctrl+C`; the bootstrap never leaves it running.

Inspect any generated Git hook before installation, preserve existing hooks, and confirm with `graphify hook status`. Documentation changes need an explicit update even when code hooks are installed.

Graphify output is local and ignored. Never scan secrets, health data, private CGM exports, model weights, local databases, generated artifacts, or ignored datasets. Graph results are navigation aids; verify important claims against source files and never treat the graph as medical evidence.

## Installation evidence

- Python: `3.12.14` (64-bit, repository-local virtual environment)
- Graphify executable resolution: repository-local launcher verified; environment-variable and
  `PATH` fallbacks remain available
- Graphify: `0.9.69`
- Readiness and exclusion checks: passed
- Initial code-only extraction and Phase 1 explicit update: passed
- Phase 2 through Phase 6 explicit code-only updates: passed
- Deterministic clustering refresh: passed with `--no-label`
- Wiki export: passed, 175 generated articles plus the wiki index
- Query plus source verification: passed
- Hooks and merge driver: installed and verified
- Git merge attribute: `.gitattributes` contains `graphify-out/graph.json merge=graphify`
- Watcher: available, not running
