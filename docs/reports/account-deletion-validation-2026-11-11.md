# Immediate account deletion validation — November 11, 2026

The user selected immediate deletion after explicit confirmation, with no recovery
window. [ADR 0020](../decisions/0020-immediate-account-deletion.md) records the
implementation, failure behavior and public-release limits. This completes the
development deletion lifecycle; it does not close all P08 or release gates.

## Expected and observed behavior

| Requirement | Observed evidence |
|---|---|
| Confirmation and fresh password belong to the verified owner | Missing session denied; incorrect confirmation and supplied foreign ID rejected; B password under A token failed without deleting either account |
| Reauthentication abuse is bounded | Service-only RPCs denied caller JWT; sixth reservation in the 15-minute window returned 429; offline tests check no password/delete call after rate denial |
| Managed Auth and owned records disappear immediately | Hard delete removed A identity and all 17 populated owned public tables/child sets; B remained populated and usable |
| Private request history is removed without resetting spend | MCP inserted one synthetic usage row per verified run owner. During the run A Auth/usage/meal-receipt counts were 0/0/0 while B remained 1/1/1; aggregate reserved spend stayed USD 0.00763580 |
| Existing and future credentials cannot restore access | Original and second-session JWTs denied, active-session RPC false, Data API returned no rows, refresh and fresh password login failed, repeated deletion denied |
| Private file failure is honest and retryable | Injected storage failure returned deleted=true/file_cleanup_pending=true and retained the source-only durable job; retry removed A directory and acknowledged it, preserving B directory and the shared replay hash |
| Browser requires deliberate confirmation and clears private state | Desktop/mobile fixtures verified password + exact DELETE + checkbox; cancel and wrong password cleared password input; success signed out both tabs, removed local Auth storage and redirected protected navigation even during a remote logout outage; anonymous deletion was explicitly unavailable |
| Additional sensitive boundaries | Offline tests cover UUID path escape/link refusal, repeatable removal, Auth failure handling, validation-input redaction, mismatched reauthentication identity, MFA refusal and background retry lifecycle |

## Execution and provenance

- [Cloud run](p08-account-deletion-cloud-2026-11-11.json): 116 bounded HTTP requests,
  two tagged disposable users, no emails, no paid provider calls, cleanup complete.
  Run `gl_ca6939db727a46f6b456bdfb` in the approved development project only.
- Pre-run source digest `36833e06a8a201b8dd3d56ee4a0421c9d4f00ea872d5e729f1ae8997c68a0e5a`
  was captured over nonignored backend/frontend/scripts/config/migration/infra/CI
  files. Base commit is `c36493d9b05ac729c4e66fb03b5ca6a05261d919`. The final
  reviewed manifest is separate: later MFA/outage guards and tests were validated
  offline; the browser locator was corrected during the cloud run. Do not label
  the final worktree digest as the historical cloud execution revision.
- Focused offline deletion suite: 19 passed. The relevant full suite and current
  browser regression totals are recorded in the main checkpoint/validation summary.
- [Schema/cleanup evidence](p08-deletion-schema-2026-11-11.json): 14 canonical
  migration hashes, 18 public RLS tables, zero users/test foods/private usage or
  receipts/attempts/cleanup jobs after scoped cleanup; zero Storage objects.
- [Security advisor](p08-deletion-security-advisors-2026-11-11.json): four INFO
  `rls_enabled_no_policy` findings on intentionally browser-denied private tables;
  no warning/error-level findings. [Explanation](https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy).
- No local Supabase reset, research model run, key rotation, Git commit/push or
  public deployment was performed for this work.

Reproduce offline with `uv run --no-sync python -m pytest -p scripts.quality.offline_pytest backend/tests/test_account_deletion.py -q`.
The guarded cloud runner is `python -m scripts.dev.deletion_integration --allow-cloud --output <report.json>`;
without `--allow-cloud` it performs no network work. Its optional private-fixture
handshake requires a deliberate run-scoped MCP seed, not a generic SQL test helper.

## Failures retained and limits

The first browser run passed two confirmation cases and failed two assertions
because its alert locator also matched Next's route announcer. The locator was
scoped; the following four deletion cases passed. The first broad Python run had
159 passes and one contract drift failure for the intentionally added DELETE
endpoint; the reviewed OpenAPI snapshot was updated with its request schema.
These were corrected without changing expected security behavior.

Review also identified a browser outcome bug when remote logout failed after the
SDK had already cleared local credentials. The handler now checks cleared storage
and still shows the confirmed deletion outcome; the final browser run injects a
503 logout response and verifies both-tab cleanup and protected-route denial.

Hosted cleanup monitoring, shared-volume/restart verification, provider log/backup
retention and a restore reconciliation drill remain P10 gates. MFA deletion is
intentionally refused until a fresh challenge is implemented. A project support
contact, corrected catalog, real email delivery and device/manual acceptance are
still pending; scratch replay remains explicitly deferred.
