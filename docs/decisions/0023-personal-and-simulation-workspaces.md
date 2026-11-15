# ADR 0023: Separate personal and virtual-simulation workspaces

**Date:** November 14, 2026. **Status:** implemented with partial acceptance under [Plan 19](../planning/GlycoLens_19_Personal_and_Simulation_Workspaces.md).

## Context

Creating/replaying a virtual source updates a shared account preference. Normal Home, nutrition, meal saves and history consequently use virtual January 2026 time and the latest simulation partition. Earlier owned meals remain stored but can disappear from default lists. The user requires the ordinary app to use real current time/timezone after leaving simulation, with no data mixing.

## Options

Scores are design judgments (1 poor, 5 strong), not performance measurements. One developer, one repo, shared Auth and existing frozen research results are assumed.

| Criterion | Weight | Display-date fix only | Explicit workspace in existing app | Separate app/account |
|---|---|---|---|---|
| Correctness and provenance | 35 | 1 | 5 | 4 |
| Delivery and operations | 20 | 5 | 4 | 1 |
| Privacy and authorization | 20 | 2 | 4 | 3 |
| Testability and maintainability | 15 | 2 | 5 | 2 |
| Migration and recovery | 10 | 2 | 4 | 2 |
| Weighted score / 5 | 100 | 2.25 | **4.50** | 2.70 |

A date-only fix leaves hidden writes and filtering coupled. Separate applications/accounts multiply identity, deployment and recovery work without inherently preserving provenance. Explicit workspace boundaries require a cross-layer migration but reuse the modular monolith, provider facts, Auth and model adapters. No additional runtime service/cost is justified; latency/resource effects remain to be measured.

## Decision

1. Keep one Supabase Auth session/account and monorepo. Make ordinary app routes personal; `/demo` and its nested routes are the virtual workspace.
2. Personal time is a current UTC instant displayed/grouped in confirmed profile IANA timezone. Simulation retains its deterministic epoch and source clock. No rebasing or rewriting saved histories.
3. Classify meals explicitly and enforce owner/source consistency server-side. Keep ambiguous legacy records labeled outside personal totals. Preserve immutable forecast/revision/receipt evidence.
4. Replace global preference-derived request authority with explicit verified workspace/source scope. New/replayed sources do not change ordinary app context or other tabs.
5. Personal meals and consumed totals work without CGM. Until a separately approved real connector exists, show honest missing glucose/forecast eligibility instead of borrowing simulated data.
6. Preserve discoverable owned simulation history, context-aware links, export and deletion. Exit changes workspace only; logout remains an independent action.

## Consequences and validation

Schema/RPCs, APIs, dates, navigation, caches/drafts, onboarding/settings, notifications and privacy flows must be updated together. [44 tests](../testing/workspace-separation-test-cases.md) cover migration, ownership, clocks/DST, old sources, browser lifecycle and frozen model regression. [Actual results](../testing/workspace-separation-results.json) distinguish completed observations from pending variants/manual review. No new prospective accuracy or Milestone 2 completion claim follows.

Keep compatibility reads during rollout, reject ambiguous old writes, and correct forward rather than deleting/reclassifying history on rollback. Revisit only if a future real connector needs a distinct explicit source contract; it must still not merge synthetic and personal records.
