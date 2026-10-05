---
name: glycolens-test-architect
description: Design or implement risk-based GlycoLens tests for requirements, APIs, UI flows, integrations, data pipelines, models, and bug fixes.
---

# GlycoLens Test Architect

1. For isolated bug fixes and small bounded behavior, write a concise requirement-to-test mapping. Use the full traceability matrix for new features, cross-layer changes, scientific experiments, authorization/RLS or medical-safety behavior, and milestone closure.
2. Cover happy paths, boundaries, invalid input, missing data, time zones and DST, concurrency, retries, timeouts, partial failure, external degradation, authorization, privacy, accessibility, and recovery where relevant.
3. Select the lowest effective layers from unit, property, integration, contract, API, database/RLS, Playwright, persona, accessibility, security, performance, regression, and scientific evaluation.
4. Avoid repeating the same assertion at several layers, and reuse passed checks until relevant changes invalidate them.
5. Use deterministic synthetic or demonstrably de-identified fixtures only.
6. Use [references/coverage-requirements.md](references/coverage-requirements.md) for domain-specific coverage.
7. Implement tests with real configured runners and report gaps or blocked prerequisites.

Keep external tests scoped to owned local or sandbox systems. Never use private CGM data as a convenient fixture.
