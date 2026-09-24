# Contributing to GlycoLens

GlycoLens is currently a student capstone project.

## Before making a change

Read `AGENTS.md` and the relevant files in `docs/planning/`. The planning documents are living source-of-truth artifacts and must be updated whenever implementation changes project decisions.

## Suggested workflow

1. Create a focused branch.
2. Implement one coherent change.
3. Add or update tests.
4. Update all affected planning and architecture documents.
5. Confirm that no secrets, health records, datasets, or model weights are staged.
6. Open a pull request using the repository template.

## Commit guidance

Use concise, imperative commit messages such as:

- `Add persistence forecasting adapter`
- `Document meal context preprocessing`
- `Update evaluation metrics and tests`
