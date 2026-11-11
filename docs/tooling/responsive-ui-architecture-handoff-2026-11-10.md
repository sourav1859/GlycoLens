# Responsive UI architecture handoff - November 10, 2026

## Goal

Inspect every supplied Nutri-App reference and update GlycoLens documentation and
application architecture for responsive mobile/tablet/desktop UI, adapting patterns
to the existing capstone rather than copying the other product.

Acceptance for this documentation cycle: all 45 references/44 unique nodes accounted
for; source observations separated from adaptations; current versus planned pages
identified; routes/components/onboarding/data/responsive contracts specified;
affected living documents synchronized; links, inventory and diff checked. Runtime
UI delivery, migrations and hosted deployment are outside this cycle.

## Accepted decisions

- Incrementally extract the working meal/forecast flow into one responsive shell.
- Primary navigation: Home, Search, Meal log, Forecasts, Nutrition; account
  destinations expose favorites, profile/settings, notifications and help.
- Minimal versioned onboarding; no required body/diagnosis/family questionnaire.
- One consumed-meal aggregate; separate planned/eaten/scenario state, unknown
  nutrients, revisions, source snapshots and simulated clock.
- Keep Next.js/plain CSS/SVG, FastAPI modular monolith, Supabase identity/RLS and
  canonical forecast adapters. No model promotion or clinical-safe claims.
- Retain corrected-catalog, provider/camera and hosted-deployment gates. See
  [ADR 0017](../decisions/0017-responsive-webapp-and-figma-reference-boundary.md).

## Current repository state

Started from main commit `4affade` with a clean working tree. Documentation only;
no runtime source/configuration/migrations changed and no commit/push/deploy made.
Authenticated Figma MCP reads succeeded; no Figma nodes changed. All supplied nodes
were read structurally/content-wise, with representative screenshots rather than
interactive prototype verification. The original external review's blocked-Figma
section was updated to point to the completed repository audit.

## Files changed

- New [UI architecture](../architecture/responsive-webapp-ui.md),
  [Figma audit and node ledger](../reports/figma-reference-review-2026-11-10.md),
  ADR 0017 and this handoff.
- Planning 00/01/03/04/06/08/09/10, root/frontend/backend READMEs,
  architecture/decision/report/tooling indexes and test strategy.
- External `GlycoLens_Webapp_Product_Architecture_Review_2026-11-10.md` in the
  parent workspace: superseded access status and links to living documentation.

## Documentation reviewed/updated

| Planning document | Outcome |
|---|---|
| 00 README | Updated navigation, design status and evidence links |
| 01 Summary | Updated target UI scope, present-versus-planned boundary |
| 03 Product UX | Updated page inventory/flows, minimal onboarding and responsive acceptance; removed obsolete synthetic-only/current-simulator descriptions and unsupported confidence mockup |
| 04 Architecture | Updated actual CSS/SVG/API/source boundaries, target diagram and links to proposed schema/API contracts |
| 06 Schedule | Added staged UI implementation checklist without moving deadlines |
| 08 Risks | Added reference-claim/privacy, totals/revisions and responsive risks |
| 09 Formal specification | Added target UI direction, clarified numeric current retrieval |
| 10 M2 ledger | Recorded documentation-only follow-up; original acceptance evidence retained |
| 02 Models/data, 05 Scientific method, 07 Literature | Impact assessed; unchanged because this UI design changes no models, datasets, experiments or literature claims |
| 11-16 Research protocols | Unaffected; no promotion, fitting, reserved-data access or scientific-result edits |

Mandatory planning/governance and architecture workflows were followed. The source
review also checked SECURITY.md and affected medical/privacy/authorization
checklist sections. A weighted option comparison and rollback are in ADR 0017.

## Checks completed

- Figma ledger: all 44 unique supplied IDs match the 45-reference request; duplicate
  and actual frame/section/dialog classifications recorded. All ten feature groups covered.
- PowerShell validation: 327 local Markdown file/anchor links resolved across
  changed repository documents and the updated external review; no unbalanced
  fenced blocks; required route coverage and new-document secret-pattern checks passed.
- Final diff review: documentation-only scope; `git diff --check` passed. Current
  API paths, authentication boundary and CSS/SVG implementation verified in source.
- Supabase Auth/key/RLS and W3C reflow/target-size references checked against
  official documentation. They support implementation requirements, not a claim
  of present compliance or hosted integration acceptance.
- Graphify 0.9.69 reported ACTIVE before exploration and in the closing pre-refresh
  check; a cross-file query guided navigation, with important claims checked in
  source. Closing maintenance is limited to one explicit code-only update with
  normal exclusions. Documentation semantic extraction is not approved/performed;
  direct source/link verification is the evidence for these new documents.

Application, database, model and browser suites were not rerun for Markdown-only
changes; earlier passes are not relabeled as new evidence. The normal `python`
command is unavailable and the application `.venv` points to a missing interpreter.
PowerShell completed the deterministic documentation checks; no environment repair
or dependency installation was attempted.

## Known failures or blockers

No remaining Figma connection blocker. No implementation acceptance is claimed.
Cloud project/origins/redirects/Auth method/email readiness need private configuration;
catalog pages still depend on corrected release validation. Live provider and
physical camera checks remain open. Tablet/search-desktop/notifications-mobile
compositions must be implemented from the new responsive rules.

## Remaining risks

The full page list exceeds the remaining course window; use phase gates and preserve
the reliable demonstration. Breakpoints/density and accessibility need actual browser
validation. Account upgrade, derived-write grants/RPCs, timezone aggregation and
immutable revisions need careful implementation tests.

## Next action

Implement phase A: shared tokens/shell plus permanent Auth and minimal persisted
preferences/onboarding, retaining anonymous demo access until its upgrade path and
two-owner isolation pass. Follow with extraction of existing meal/forecast routes
and consumed-day aggregation; activate catalog-dependent features only after its gate.
