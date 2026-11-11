# Cloud web application planning handoff - November 10, 2026

## Goal

Draft a detailed staged implementation plan, prerequisites, test cases and validation
gates, and persist the user's cloud-Supabase preference. Acceptance: every agreed
feature maps to a phase/test group; all cases have expected outcomes; result state
is honest; affected living docs and project instructions agree.

## Accepted decisions

One repository; dedicated cloud Supabase development project; email/password with
verification/reset; full agreed features in staged releases. Keep OpenAI, with
model/test budget pending. Corrected catalog is not ready: labeled fixtures/providers
for development, activation after validation. VPS/domain are pending. No fixed new
delivery date or production/scratch budget was supplied.

## Current repository state

Earlier November 10 UI/readiness documentation changes were already present and
retained. This cycle changes project instructions/planning/testing/setup documents
and adds a JSON test-result ledger. No runtime source, dependency, secret file,
migration or external service is changed. No cloud project or schema has been created.

## Files changed

- [Plan 17](../planning/GlycoLens_17_Webapp_Implementation_Plan.md),
  [test-case catalog](../testing/webapp-cloud-test-cases.md),
  [result ledger](../testing/webapp-validation-results.json),
  [ADR 0018](../decisions/0018-cloud-supabase-and-staged-webapp-delivery.md),
  [cloud setup guide](cloud-supabase-setup.md) and this handoff.
- AGENTS.md durable project memory; root/frontend/backend/database READMEs;
  planning 00/01/03/04/06/08/09/10, architecture/test strategy/setup/index links;
  historical local-target ADRs marked with current superseding target.

## Documentation reviewed/updated

Planning 00/01 required context, 03 product, 04 architecture, 06 milestones, 08 risks,
09 specification and 10 evidence ledger are synchronized with the cloud target and
phase plan. Model/data/scientific/literature protocols 02/05/07 and 11-16 remain
unchanged: no model promotion, dataset access, experiment or scientific result changes.
Existing UI architecture/readiness findings, manifests, API/Auth/provider code and
local configuration/test wrappers informed the cloud prerequisites and cases.

## Checks completed

Draft validation covers phase/case/result traceability, unique IDs, expected outcomes,
initial NOT_RUN states, prerequisite coverage, links, fenced Markdown, whitespace
and approved documentation-only file scope. Execution results are recorded at
completion of this documentation cycle; none are application/hosted test passes.

Completed draft checks: 11 phase definitions match the result ledger; 144 unique
catalog cases each have setup/action/expected result and match their ledger/phase
membership; all actual/evidence/run fields remain empty and states NOT_RUN. All
plan case references resolve, estimate arithmetic is 27-46 focused days and the
confirmed cloud/Auth choices match AGENTS.md/ADR 0018. Local file/anchor validation
resolved 450 links across the current changed documentation and earlier external
review, with no broken links or fenced-block errors. Tracked and all six new-file
whitespace checks passed. Changes are documentation/project policy plus the JSON
planning ledger; earlier user work is retained. These are draft consistency checks,
not a Phase P00 implementation pass or any of the 144 application-case executions.

Graphify 0.9.69 reported ACTIVE before exploration; source verified relevant
relationship findings. Closing maintenance is one code-only update with existing
secret/data exclusions. Documentation semantic extraction is not approved/performed;
the planning content is checked directly.

## Known failures or blockers

All 144 designed application cases are initially NOT_RUN; no cloud/application/
provider/model/device tests were executed. Exact cloud project identity/keys,
migration access, SMTP/inboxes, LLM model/budget and provider keys still need private
configuration. Catalog correction, scratch/production targets and hosting remain
external prerequisites. Earlier Python/uv visibility restrictions are not evidence
that a normal-shell baseline passed; P00 verifies it.

## Remaining risks

Cloud tests must never invoke legacy local reset/key-writing scripts or mutate a
production target. Modern API-key header compatibility, trusted derived writes,
immutable forecast inputs, timezone/source aggregation, live email/provider/device
acceptance and portable deployment need real implementation/verification. Estimates
do not revise course dates or imply the full new scope fits the remaining deadline.

## Next action

Obtain non-secret dedicated cloud project identity and configure credentials privately.
Complete P00 baseline/CI and cloud-safe harness, then prepare the concrete P01 schema
diff/target inventory for controlled application. Implement shared UI foundations
alongside the cloud setup; do not claim phase completion from scaffolding or fixtures.
