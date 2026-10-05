---
name: glycolens-architecture-review
description: Review consequential GlycoLens system design, data model, API, model-serving, deployment, integration, dependency, or scalability decisions before implementation.
---

# GlycoLens Architecture Review

Use this workflow only for consequential design choices. Routine implementation inside an approved architecture does not require a full option comparison.

1. Restate requirements, constraints, assumptions, non-goals, and current capstone scale.
2. Query Graphify when current; otherwise inspect relevant source and planning documents directly.
3. Enumerate credible options, including retaining the current design.
4. Analyze normal cases, boundaries, failure modes, abuse cases, operational risks, and recovery.
5. Compare scalability, latency, cost, reliability, security, privacy, observability, maintainability, testability, and delivery time.
6. When multiple credible options remain after reusing current ADR and planning evidence, use the weighted matrix in [references/decision-framework.md](references/decision-framework.md).
7. Recommend one option, explain rejected alternatives, and define rollback or migration.
8. Create or update an ADR and all affected living documents.

Preserve the modular monolith and common forecast-adapter boundary unless evidence and revised planning documents justify a change. Distinguish current capstone needs from hypothetical production scale. Use Sol with high reasoning for actual consequential decisions; never claim that this skill changed models.
