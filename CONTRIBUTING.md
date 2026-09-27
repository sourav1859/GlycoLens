# Contributing to GlycoLens

GlycoLens is currently a student capstone project.

## Before making a change

Read `AGENTS.md` and the relevant files in `docs/planning/`. The planning documents are living source-of-truth artifacts and must be updated whenever implementation changes project decisions.

## Suggested workflow

1. Create a focused branch.
2. Define acceptance criteria and inspect the relevant source, tests, and planning documents.
3. Query Graphify first when a current graph is available; otherwise inspect source directly.
4. Implement one small, reversible change and add or update tests.
5. Run only real, documented format, lint, type-check, test, security, and build commands.
6. Update all affected planning, architecture, testing, and operational documents.
7. Refresh Graphify after supported file changes, or disclose why it was not refreshed.
8. Update `docs/impact/impact-ledger.md` when a verified measurable improvement is claimed.
9. Confirm that no secrets, health records, datasets, model weights, caches, or generated graph output are staged.
10. Open a pull request using the repository template only when explicitly authorized.

See `docs/tooling/local-development-setup.md` for current prerequisites and `docs/testing/test-strategy.md` for test-layer selection.

## Local bootstrap validation

The repository-skill validator is invoked with:

```powershell
python scripts/quality/validate_skills.py
```

Python 3.10 or later is required. Product lint, test, and build commands will be documented only after the corresponding application toolchains exist.

## Commit guidance

Use concise, imperative commit messages such as:

- `Add persistence forecasting adapter`
- `Document meal context preprocessing`
- `Update evaluation metrics and tests`

Do not stage, commit, push, or merge on another contributor's behalf without explicit authorization.
