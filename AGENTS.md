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

- Preserve the modular-monolith architecture unless the planning documents are deliberately revised.
- Keep forecasting models behind a common adapter interface.
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
