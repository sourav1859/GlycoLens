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

## Working practices

- Keep changes focused and reviewable.
- Add or update tests for behavior changes.
- Record important architectural decisions in `docs/decisions/`.
- Update the root README when setup or repository navigation changes.
