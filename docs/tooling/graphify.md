# Graphify Developer Knowledge Graph

## Status

**ACTIVE (code-only) as of September 28, 2026.** Graphify `0.9.69` is installed in an isolated pipx environment using Python `3.12.5`.

The refreshed local graph contains 696 nodes, 746 edges, and 100 communities after an explicit update and deterministic no-label clustering refresh. The wiki export wrote 110 articles. A representative query located the T1D-UOM meal-window implementation in `research/datasets/t1d_uom.py`, which was verified against the source. Post-commit and post-checkout hooks plus the local merge driver are installed. Watch mode is available but is not left running.

Semantic documentation/media extraction is **not active**. The graph was intentionally built with `--code-only`, so no repository documents were sent to a model backend.

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
2. Install a specific verified version with `pipx install graphifyy==<version>` or the equivalent pinned `uv tool install` command. The current installation uses `graphifyy==0.9.69`.
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

- Python: `3.12.5` (64-bit)
- pip: `24.2`
- pipx: `1.7.1`
- Graphify: `0.9.69`
- Readiness and exclusion checks: passed
- Initial code-only extraction and explicit update: passed
- Deterministic clustering refresh: passed with `--no-label`
- Wiki export: passed, 104 articles written
- Query plus source verification: passed
- Hooks and merge driver: installed and verified
- Git merge attribute: `.gitattributes` contains `graphify-out/graph.json merge=graphify`
- Watcher: available, not running
