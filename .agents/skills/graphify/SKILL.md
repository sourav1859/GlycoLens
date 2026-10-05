---
name: graphify
description: Use the local Graphify repository knowledge graph for broad GlycoLens exploration, relationship queries, impact analysis, and graph refreshes when Graphify is available.
---

# Graphify

Treat Graphify as an optional developer navigation aid. Never equate it with product GraphRAG, the application database, forecasting, or medical evidence.

## Workflow

1. Check status once before the first eligible broad exploration or impact-analysis step; reuse it until relevant repository files change.
2. Query a current graph for cross-file relationships and impact questions. Use direct targeted source search for a known file or single symbol, and do not query merely to confirm the current diff. Verify important findings against source.
3. If the graph is missing, stale, or blocked, inspect source normally and state that Graphify was not used or refreshed.
4. After final supported edits, check whether a hook already refreshed the graph, then update once if needed. Documentation changes require an explicit update.
5. Report graph readiness, freshness, command evidence, and any blocker without fabricating success.

Before building or updating a graph, read [references/compatibility-and-safety.md](references/compatibility-and-safety.md) and verify `.gitignore` plus `.graphifyignore`. Never scan secrets, environment files, ignored health datasets, private CGM exports, local databases, model weights, or generated artifacts.

Do not enable a semantic backend that may transmit documents without explicit approval and verified data boundaries. Do not leave watch mode running after the task.
