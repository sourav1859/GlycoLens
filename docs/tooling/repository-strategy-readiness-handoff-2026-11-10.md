# Repository strategy and readiness handoff - November 10, 2026

## Goal

Assess whether the finalized responsive UI requires separate frontend/backend/forecast
repositories, and define the preparation and implementation order. Acceptance:
source-backed recommendation, credible alternatives, immediate versus deployment
gates, future extraction criteria and preserved existing project boundaries.

## Accepted decisions

This review reaffirms the existing one-repository modular-monolith and managed
Supabase decisions. It does not authorize a repository split, model promotion,
runtime migration or hosted action. The recommended path is shared source control,
separate module/build boundaries and staged user journeys. A future forecast
service can remain in the monorepo; code-access/team/release requirements would
justify revisiting Git boundaries.

## Current repository state

The prior November 10 responsive-UI documentation changes were already present
and retained. This cycle adds an advisory report and navigation/decision links.
Runtime sources, dependency manifests, migrations and external services are unchanged.

## Files changed

- [Repository strategy and readiness report](../reports/repository-strategy-and-development-readiness-2026-11-10.md).
- This handoff; report/architecture/tooling indexes, root README and planning 00/04.
- ADR 0017 gains a related-review link; its accepted decision is unchanged.

## Documentation reviewed/updated

Planning 00/01 and relevant 02/03/04/06/08 sections, the responsive UI architecture,
ADRs 0009/0016/0017, SECURITY.md, test strategy, manifests, development tooling and
actual application/adapter/simulator/SQL boundaries informed the assessment.
Planning 00/04 receive navigation/clarification. Other planning/research documents
remain unchanged because this assessment adds no feature, scientific protocol,
model, hosting choice or deadline. No new architecture approval is implied.

## Checks completed

Graphify 0.9.69 reported ACTIVE before exploration; a relationship query guided
navigation and important findings were verified against source. Official Docker,
Next.js, FastAPI and GitHub documentation supports the report's operational advice.
Closing checks cover local file/anchor links, required review coverage, whitespace
and documentation-only changes. No application test result is claimed by this review.

Validation passed: 362 local file/anchor links across the current changed Markdown
set and external architecture review; all 22 changed repository files are Markdown
(including the retained prior UI work). Tracked-diff and both new review-document
whitespace checks passed. Required recommendation, findings and implementation-order
coverage was checked against the report; the existing 44-node Figma ledger remains intact.

Closing graph maintenance is limited to one explicit code-only update with normal
exclusions. Semantic extraction of new documentation is not approved/performed;
direct source and link checks remain the documentation evidence.

## Known failures or blockers

The current tool PATH does not expose Python/uv, while a check of the application
venv's base interpreter hit a filesystem access restriction. Machine-wide Python
availability is unverified. Use the normal shell for a fresh supported-toolchain
baseline; do not treat PATH presence alone as validated tools/daemon operation.

No CI workflow or deployment packaging exists yet. Permanent-account/onboarding
and daily aggregate schema/API implementation, provider/camera verification and
corrected catalog readiness remain pending. This is an assessment, not new test
or live-integration evidence.

## Remaining risks

Derived-write grants versus trusted system records, immutable forecast inputs,
process-local concurrency/artifact paths, Windows-specific launch configuration,
client build-time configuration and UI/API/schema drift require implementation
work. The report separates these concrete concerns from hypothetical scaling.

## Next action

Verify the existing normal-shell baseline and establish executable CI. Define the
first Auth/preferences/onboarding migration/API contract, then implement that
vertical slice with the shared responsive shell while retaining demo compatibility.
Do not begin with a repository split or broad code relocation.
