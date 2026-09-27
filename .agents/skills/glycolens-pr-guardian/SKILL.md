---
name: glycolens-pr-guardian
description: Review complete GlycoLens diffs and prepare focused local commit messages or pull-request descriptions without creating, pushing, approving, or merging them.
---

# GlycoLens PR Guardian

1. Inspect the complete changed-file list and diff against the intended base.
2. Check acceptance criteria, correctness, safety, security, privacy, tests, documentation, performance, maintainability, generated files, secrets, and Graphify freshness.
3. Use [references/review-checklist.md](references/review-checklist.md) and cite file/line evidence for findings.
4. Order findings by severity and distinguish blockers from suggestions. State explicitly when no findings remain and name residual risks or untested areas.
5. Draft a concise imperative commit message consistent with `CONTRIBUTING.md` when requested.
6. Draft a PR description with summary, motivation, verification evidence, screenshots when applicable, risks, rollback, documentation, and measurement.

Never stage, commit, create, push, approve, or merge a pull request without explicit authorization.
