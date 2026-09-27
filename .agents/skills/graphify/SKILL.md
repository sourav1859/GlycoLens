---
name: graphify
description: Use the local Graphify repository knowledge graph for broad GlycoLens exploration, relationship queries, impact analysis, and graph refreshes when Graphify is available.
---

# Graphify

Treat Graphify as an optional developer navigation aid. Never equate it with product GraphRAG, the application database, forecasting, or medical evidence.

## Workflow

1. Run `scripts/graphify/Get-GraphifyStatus.ps1` before a broad scan, unfamiliar-code exploration, impact analysis, or cross-document question.
2. If a current graph exists, ask a scoped question with `scripts/graphify/Invoke-GraphifyQuery.ps1`, then verify important claims against source files.
3. If the graph is missing, stale, or blocked, inspect source normally and state that Graphify was not used or refreshed.
4. After supported files are added, changed, moved, or deleted, run `scripts/graphify/Update-Graphify.ps1`. Run an explicit update for documentation changes.
5. Report graph readiness, freshness, command evidence, and any blocker without fabricating success.

Before building or updating a graph, read [references/compatibility-and-safety.md](references/compatibility-and-safety.md) and verify `.gitignore` plus `.graphifyignore`. Never scan secrets, environment files, ignored health datasets, private CGM exports, local databases, model weights, or generated artifacts.

Do not enable a semantic backend that may transmit documents without explicit approval and verified data boundaries. Do not leave watch mode running after the task.
