---
name: glycolens-pr-guardian
description: Review complete GlycoLens diffs and prepare focused local commit messages or pull-request descriptions without creating, pushing, approving, or merging them.
---

# GlycoLens PR Guardian

1. Inspect the complete changed-file list and diff against the intended base.
2. Reuse validation evidence produced after the current diff. Rerun a check only when the diff changed or evidence is incomplete, then assess acceptance criteria, correctness, safety, security, privacy, tests, documentation, performance, maintainability, generated files, secrets, and Graphify freshness.
3. Use [references/review-checklist.md](references/review-checklist.md) and cite file/line evidence for findings.
4. Order findings by severity and distinguish blockers from suggestions. State explicitly when no findings remain and name residual risks or untested areas.
5. Keep substantive review separate from optional commit-message and PR-description drafting. Create either only when requested.
6. Use Luna for mechanical draft wording; use Sol for substantive code, security, privacy, or scientific review. A recommendation here does not switch the active model.

Never stage, commit, create, push, approve, or merge a pull request without explicit authorization.
