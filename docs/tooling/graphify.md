# Graphify Developer Knowledge Graph

## Status

**Local code-only graph; use Get-GraphifyStatus for current freshness.** Graphify `0.9.69` is available from the ignored,
repository-local `.cache/graphify-venv` environment using Python `3.12.14`. The wrappers prefer an
explicit `GLYCOLENS_GRAPHIFY_EXECUTABLE`, then the repository-local executable, and finally a
`graphify` command on `PATH`. This fallback keeps the workflow operational if an older global
launcher points to a removed Python installation; no credentials or endpoint values are stored in
the repository.

The historical local graph contained 1,293 nodes, 1,896 edges, and 166 communities after the October
1 Milestone 1 current-state update. The closure query located the final audit, requirement matrix,
test-strategy gate, dataset pipeline, forecast contracts, Chronos-2 runner, and related tests; those
findings were verified against source. The earlier Phase 6 query also located the py-mgipsim
runner, result contract, isolated bridge, exact-commit verification, validators, and
reproducibility test.
Post-commit and post-checkout hooks plus the local merge driver are installed. Watch mode is
available but is not left running.

For each focused task, check status once before the first broad exploration or impact analysis and
reuse that result until relevant files change. Query cross-file relationships; use direct targeted
search for known files and symbols. After final supported edits, check whether a hook refreshed the
graph and perform at most one explicit code-only update if still needed.

Semantic documentation/media extraction is **not active**. The graph was intentionally built with `--code-only`, so no repository documents were sent to a model backend.

M2 delivery uses an explicit code-only update after final implementation/documentation
edits. New modules include evaluation/splits/metrics, covariate adapters, Auth-backed
application routes, nutrition, simulation and numeric retrieval. Graph claims must be
verified against source and the phase ledger; semantic documentation refresh remains
disabled. Graph output/counts are ignored local artifacts, not scientific evidence.

October 16 MetaboNet Phase 2 added native-unit windows, streaming preparation, the
aggregate reporter and acceptance tests. One final code-only update wrote a graph
containing all four modules (1,906 nodes / 3,422 edges); a read-only freshness check
returned ACTIVE. Its PowerShell wrapper exited 1 on the known optional
`tree_sitter_sql` warning, although graph output was written. Seven SQL files were
skipped; no SQL changed in this phase. No retry/semantic extraction or dataset upload.
See the [Phase 2 handoff](metabonet-phase2-handoff-2026-10-16.md) for command evidence.

The subsequent Phase 3 update exited 0 and returned ACTIVE on freshness verification:
1,964 nodes / 3,601 edges / 213 communities, including the inference runner, aggregate
reporter and acceptance tests. The existing optional SQL-parser warning still skips
seven SQL files; no SQL changed in this phase. Some community names are hub-derived
after grouping changes. Semantic relabeling/document extraction remains disabled.
See [Phase 3 evidence](metabonet-phase3-handoff-2026-10-16.md). Ignored predictions,
prepared data and checkpoint files were excluded; no dataset was uploaded.

In installed Graphify `0.9.69`, `query` loads `graph.json` and performs local BFS/DFS traversal; it
does not expose a model-backend option. `graphify query --help` is not a help path in this version:
the token `--help` is treated as the question. Backend use belongs to semantic extraction, not the
query command. This was verified from the installed CLI source without transmitting repository
content.

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

## MetaboNet Phase 6 verification records

The Phase 6 closing workflow checks hook/freshness status and performs at most one
explicit local code-only refresh after the final supported edits. It covers the
independent runner, uncertainty module, aggregate reporter and acceptance tests.
Command/status and graph-content evidence are retained under ignored
`.cache/model-refinement-preflight/phase6-graph-{before,update,after}.log` and
`phase6-graph-verification.json`. Read those records for actual readiness and counts.
The existing seven optional SQL-parser omissions are outside this Python-only change.
Semantic documentation extraction/relabeling remains disabled; planning claims and
cross-links are verified directly against source. No health data, weights, ignored
artifacts or secrets are graph inputs, and no dataset is uploaded.
