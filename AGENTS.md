# GlycoLens Repository Instructions

## Living documentation rule

The files in `docs/planning/` are the project source of truth.

Before any substantive project decision or implementation change:

1. Read `docs/planning/GlycoLens_00_README.md`.
2. Read `docs/planning/GlycoLens_01_Updated_Project_Summary.md`.
3. Read every specialized planning document affected by the proposed work.

In the same work cycle as the implementation, update every affected planning document when work changes any of the following:

- project scope or deliverables
- research questions or hypotheses
- model candidates, adapters, or inference behavior
- datasets, splits, preprocessing, or leakage controls
- experiments, metrics, evaluation, or statistical analysis
- product features, user flows, or UX
- architecture, APIs, database schema, or deployment
- third-party integrations
- safety boundaries, privacy, or risk controls
- milestones or schedule

Implementation and documentation must not diverge. Documentation-only wording corrections that do not change project meaning do not require unrelated document updates.

## Architecture constraints

### Current web application decisions - November 10, 2026

- November 14 approved direction: separate personal app and virtual simulation workspaces under the same Auth/account. Read Plan 19 and ADR 0023 before implementation. Personal routes use actual now in confirmed IANA timezone and work without a virtual source; `/demo` retains deterministic virtual time/history. Never mix synthetic records into personal totals, silently borrow simulator glucose for personal forecasts, or rewrite old timestamps. Global account source selection is not the new request authority. Plan 19 engineering implemented November 14; cloud migration 20261114173109 applied and local Compose updated. Read the actual 44-case ledger and validation report; pending variants/manual Chrome are not passes. Preserve separate workspace drafts/history/clock boundaries when extending the app.

- Keep one repository for frontend, backend and forecasting code.
- Use **managed cloud Supabase from now on**, with a **dedicated GlycoLens cloud development project** for application PostgreSQL/Auth and integration acceptance. Local web/API processes may connect to it; a local Supabase stack is not the new default or a required integration-test environment.
- First-release Auth is email/password with verification and password reset. Deliver the full agreed feature set in staged releases.
- Temporary development Auth exception, confirmed November 11: the user disabled email confirmation in the dedicated cloud development project. Live settings verified email/password and public signup enabled, with automatic email confirmation. Development can proceed without SMTP; this does not prove email ownership or waive verification/recovery delivery before public release. Keep tests synthetic and do not copy this exception to production.
- Read `docs/planning/GlycoLens_17_Webapp_Implementation_Plan.md` and its linked test catalog/result ledger before current webapp implementation. Record actual expected/observed test results; planned, skipped or blocked tests are not passes.
- Keep OpenAI Responses recipe extraction; the user selected `gpt-6-luna` on November 11, replacing `gpt-5-mini`. Keep the selected model in private server configuration and the environment template. The user approved a **USD 5 total live-test budget**; the bounded 16-call synthetic comparison has estimated token charges of USD 0.00763580. November 12 checkpoint: known token estimate is USD 0.00769040 plus USD 0.01 unresolved-call reserve; cloud conservative reservations total USD 0.02763580. See `docs/reports/m2-closure-validation-2026-11-12.md`. Account for prior spend and unresolved reservations before further paid tests; approval is not a fresh USD 5 allowance per run. Live access and smoke checks are verified; representative accuracy remains unproven. See `docs/reports/recipe-model-validation-2026-11-11.md`. Corrected catalog is not ready: use labeled fixtures/providers for development and activate only after validation. VPS/domain are pending.
- Preserve versioned migrations under `supabase/migrations/`; inspect the exact cloud target and preview reviewed changes before controlled apply. Never reset a hosted database or run broad test cleanup. Use run-scoped synthetic fixtures and explicit cloud-target guards.
- Historical local Supabase instructions/results remain historical. Do not run `Configure-LocalDemo.ps1`, local start/reset wrappers or overwrite cloud keys with local values as the new workflow. Offline unit/fixture tests remain allowed; they do not prove cloud integration acceptance.
- Keep secret values in ignored/private configuration. No credentials or cloud schema are created merely by the plan. See ADR 0018 and the cloud setup guide for current prerequisites.
- Account deletion decision, November 11: delete immediately after fresh password verification and explicit confirmation, with no recovery window. Hard-delete managed Auth and owned app data; retry scoped private source-file cleanup without retaining an account snapshot. Do not promise instant provider backup/log erasure. See ADR 0020; test only tagged disposable accounts.

- Preserve the modular-monolith architecture unless the planning documents are deliberately revised.
- Keep forecasting models behind a common adapter interface. Plan 18 native LightGBM/48h/v2 integration is implemented; Chronos remains default. On November 14 the user requested local UI access: the existing local native option is enabled for research/manual testing with verified artifacts and history checks. This local exposure does not waive pending Chrome/manual, accuracy or release acceptance; the shipped template stays disabled by default. The synthetic Chronos meal-response capability gate failed; do not claim useful meal effects or matching-outcome accuracy. Read the actual Plan 18 result ledger before further implementation.
- Keep research datasets separate from the application database.
- Do not introduce GraphRAG into the MVP without an explicit scope decision.
- Do not add insulin-dose recommendations, clinician-setting changes, or pump control.

## Data and security

Never commit secrets, OAuth tokens, API keys, identifiable health data, private CGM exports, downloaded research datasets, or model weights. Use environment variables and sanitized fixtures.

Keep personal contact addresses in ignored environment configuration. Repository skills must reference environment-variable names rather than literal addresses; `scripts/quality/validate_skills.py` enforces this boundary.

## Working practices

- Keep changes focused and reviewable.
- Define acceptance criteria before editing and verify them before completion.
- Add or update tests for behavior changes.
- Record important architectural decisions in `docs/decisions/`.
- Update the root README when setup or repository navigation changes.
- Never push, merge, deploy, rotate credentials, or change external services without explicit authorization.

## Repository skills

Shared workflows live in `.agents/skills/`. Use the relevant skill for documentation governance, architecture review, change delivery, testing, pull-request review, impact measurement, or medical/data safety. Skill instructions supplement rather than replace this file and the planning source of truth.

## Model and token-use discipline

### Task boundaries and handoff

- Before broad exploration, define the goal, acceptance criteria, affected files, and necessary checks.
- Keep a session focused on one milestone, feature, defect, or review domain. Start a fresh session after completion or when switching to an unrelated subsystem.
- Carry forward a concise handoff containing the goal, accepted decisions, affected files, completed checks, unresolved risks, and next action. Use `docs/tooling/templates/codex-session-handoff.md`.

### Reading and context reuse

- The planning README and Updated Project Summary remain mandatory before substantive decisions or implementation. Within a focused session, reuse an already-read, unchanged file when the required section remains in context.
- Reopen a file when it changed, relevant content is missing, a new decision depends on it, or verification requires the current version. Read affected sections with targeted searches and ranges.
- Avoid repeated full reads of planning documents, lockfiles, generated files, logs, and large datasets. Never skip an affected planning document to save tokens.

### Tool output, verification, and retries

- Prefer `rg`, bounded ranges, filtered commands, quiet test modes, and ignored local logs. Return concise summaries and relevant failures; do not emit full lockfiles, large JSON, database dumps, complete test logs, Graphify exports, dataset rows, or generated artifacts.
- Follow the narrow-to-broad verification ladder. Reuse a passed check unless a relevant file or environment changed or another result calls it into question. Run full regression, database, model, presentation, and milestone validation only when required. Use local scripts for deterministic validation and aggregation.
- Do not repeat a failed command without changing a prerequisite, hypothesis, input, or diagnostic scope. After two materially different failed approaches, summarize the evidence and reassess. Avoid installation, environment, and Graphify retry loops.

### Skill and subagent coordination

- One primary workflow owns the task. Supporting skills provide focused evidence or checks; reuse their planning, test, documentation, diff, and Graphify evidence rather than rerunning it.
- A skill recommendation does not switch models. Model selection belongs in configuration, custom agents, or explicit invocation. Do not spawn an agent solely to invoke a skill when the primary agent can do the work efficiently.
- Use subagents only for independent bounded work that benefits from context isolation or parallel execution. Do not delegate trivial edits, sequential tasks, repeated reading, or overlapping reviews. Require concise summaries, reuse their evidence, and never exceed the configured concurrency limit.
- Default bounded exploration and routine work to Luna. Use Sol for consequential architecture, scientific, authorization, security, privacy, and medical-safety work.

### Model escalation

| Work | Starting model/effort |
|---|---|
| Deterministic parsing, formatting, aggregation, schema checks | Local script first |
| Exact wording changes, simple extraction, narrow configuration edits | Luna low or medium |
| Bounded code navigation and routine implementation | Luna medium or high |
| Normal multi-file implementation and test design | Sol medium |
| Architecture, leakage, medical safety, privacy, RLS/auth, conflicting evidence | Sol high |
| Extremely demanding unresolved analysis | Explicit escalation only |

Retain a lighter model only when it meets the quality bar without repeated repairs. See `docs/tooling/codex-token-efficiency.md` for operational guidance.

## Graphify lifecycle

Graphify is an optional developer knowledge graph, not product GraphRAG, a product database, or a forecasting component.

- Before the first eligible broad scan, unfamiliar-code exploration, impact analysis, or cross-document question, run `scripts/graphify/Get-GraphifyStatus.ps1`; reuse that result until relevant files change.
- Use a current graph for cross-file relationships and impact questions. Use direct targeted search for a known file or symbol, and verify important graph claims against source.
- After final supported edits, check whether a hook already refreshed the graph, then run at most one explicit `scripts/graphify/Update-Graphify.ps1` if needed. Documentation changes require an explicit update.
- If Graphify is unavailable or stale, inspect source directly and disclose that the graph was not refreshed.
- Never scan ignored secrets, health datasets, private CGM exports, model weights, databases, or generated artifacts. Preserve `.gitignore` and `.graphifyignore` exclusions.
- Do not run semantic extraction that can send document content to a configured model backend without explicit approval and verified data boundaries.
