# Verification Ladder

Run only configured commands, progressing from fastest and narrowest to broader checks:

1. Focused unit or behavior test.
2. Formatting and static lint.
3. Type checking.
4. Relevant unit/component suite.
5. Integration, contract, database/RLS, or Playwright coverage.
6. Security and secret checks.
7. Production build or packaging check.
8. Performance or scientific evaluation when acceptance criteria require it.
9. `git diff --check`, changed-file inspection, documentation audit, and Graphify refresh.

Classify each check as passed, failed, blocked, or not applicable. A missing tool is a blocker, not a pass.
