# Architecture Documentation

- [Phase-wise implementation plan](../planning/GlycoLens_17_Webapp_Implementation_Plan.md) and [ADR 0018](../decisions/0018-cloud-supabase-and-staged-webapp-delivery.md): confirmed cloud Supabase development, Auth choices, staged full-feature delivery and named test/evidence gates.

- [Repository strategy and development readiness](../reports/repository-strategy-and-development-readiness-2026-11-10.md): why the existing monorepo fits, how runtime/deployment isolation differs and what to prepare before implementing the responsive application.

- [Responsive web application and UI architecture](responsive-webapp-ui.md): current-versus-target routes, shared shell/components, minimal onboarding, responsive rules, consumed-meal semantics, schema/API proposals and staged acceptance. Design baseline, not delivered runtime UI.
- [ADR 0017](../decisions/0017-responsive-webapp-and-figma-reference-boundary.md): decision and migration/rollback tradeoffs.
- [Figma source review](../reports/figma-reference-review-2026-11-10.md): all 44 unique supplied nodes, classification corrections and adaptation boundaries.

Store implementation-level architecture diagrams, API contracts, database notes, and deployment details here. Major decisions must remain consistent with the planning source of truth.
