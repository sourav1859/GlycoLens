# ADR 0017: Responsive application shell and Figma reference boundary

**Date:** November 10, 2026

**Status:** Accepted design direction for documentation and incremental implementation; runtime delivery pending.

## Context

The user requested inspection of the supplied Nutri-App Figma designs and updates to GlycoLens documentation/architecture for desktop, tablet and mobile. Authenticated Figma MCP reads succeeded. There are 45 references, 44 unique nodes; the source is principally a 390px mobile and 1280px desktop nutrition/household product. The current GlycoLens application is an executable single-page meal-to-forecast prototype, not that multi-page product.

We need consistent navigation, account/onboarding state, reusable meal review, catalog/detail pages and shared daily nutrition semantics, while preserving the modular monolith, source evidence, common forecast adapters and nonclinical capstone boundary. Corrected catalog and hosted deployment acceptance remain independent dependencies.

## Options

Keep the existing single-page prototype as the entire product; incrementally extract it into a shared responsive shell; or rebuild by porting the reference screens. Scores are design judgments (1 weak, 5 strong), not measured performance. Weights reflect a single-developer capstone.

| Criterion | Weight | Keep one page | Incremental shell | Reference rebuild |
|---|---|---|---|---|
| Delivery/reuse of verified workflow | 30% | 5 | 4 | 1 |
| Correctness and safety/privacy | 25% | 3 | 5 | 2 |
| Requested responsive feature coverage | 20% | 1 | 5 | 4 |
| Maintainability/testability | 15% | 2 | 4 | 2 |
| Migration/rollback | 10% | 5 | 5 | 2 |
| Weighted score / 5 | 100% | 3.25 | 4.55 | 2.10 |

Keeping one page has the lowest immediate effort but leaves missing account/routes and increasingly coupled state. A rebuild scores poorly on reuse and privacy because it adds household/health/shopping concepts without supporting services. An incremental shell adds route/state complexity but preserves verified contracts and permits reversible slices. It avoids new services, a framework migration or extra model costs. Dashboard range bounds, pagination and user-scoped caching contain query costs; actual latency and capacity must be measured when implemented.

## Decision

Adopt the [responsive UI architecture](../architecture/responsive-webapp-ui.md) and update the living product/architecture documents. Use the [Figma review](../reports/figma-reference-review-2026-11-10.md) for evidence and traceability, not copied branding, assets, sample nutrition values or medical claims.

- Use one Next.js route/navigation definition: Home, Search, Meal log, Forecasts, Nutrition; account destinations remain accessible at all widths.
- Adapt step/review onboarding, cards, filter chips, sheets/dialogs, date navigation and detail hierarchy. Design tablet behavior explicitly rather than scaling a fixed screenshot.
- Keep minimal app preferences and source/acknowledgement onboarding. Do not require body metrics, diagnosis or family/child records.
- Share a server aggregate for consumed nutrition and preserve meal revisions/source snapshots. Planned meals, favorites and forecast scenarios do not count as eaten.
- Keep FastAPI `/api/v1`, Supabase verified identity/RLS and current adapter/model behavior; extend them additively as slices are implemented.
- Provide accessible chart summaries/tables, keyboard operation and mobile-safe sticky controls. Do not equate a successful 390px screenshot with responsive acceptance.
- Add permanent Auth, routes and schema only with their own implementation and verification. This ADR creates no tables, endpoints, hosted resources or claim of milestone closure.

## Consequences, failures and recovery

Benefits are consistent routes, one meal composer, auditable data semantics and a gradual migration. Costs are new account/onboarding state, more route-level tests, daily aggregation and revision migrations. Source switching, account switching, stale sessions and partial data require explicit recovery rather than silent defaults.

Retain the old working entry until the new route slices pass. Use additive migrations and feature flags/previous compatible releases for rollback. A failed catalog validation leaves catalog screens unavailable and the reviewed-food path usable. A failed save preserves the draft with an idempotent retry; a stale edit requires conflict review. A forecast failure does not fabricate a successful line or change a logged meal.

Confidence is high in the modular-monolith/shared-component direction and source observations; detailed density and breakpoint choices require browser/user validation. Revisit the shell only if measured navigation/usability problems cannot be fixed within it. Native clients, new medical data collection or household features require separate scope/privacy decisions. No research model promotion follows from this UI work.

## Verification

The subsequent [repository strategy and development-readiness review](../reports/repository-strategy-and-development-readiness-2026-11-10.md)
reaffirms the existing monorepo/modular-monolith boundaries and identifies the
preparation for implementation. It adds no repository split or new accepted
runtime/service decision.

See [responsive acceptance](../architecture/responsive-webapp-ui.md#8-delivery-and-acceptance), [test strategy](../testing/test-strategy.md) and the [session handoff](../tooling/responsive-ui-architecture-handoff-2026-11-10.md). Documentation validation and application validation are recorded separately.
