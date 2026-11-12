# ADR 0020: Immediate confirmed account deletion

- Status: accepted and implemented for dedicated cloud development
- Date: November 11, 2026
- Decision owner: user; “Delete immediately after explicit confirmation; no recovery window.”

## Behavior

`DELETE /api/v1/me` requires a live managed Auth session, the current password and
exact `DELETE` confirmation. The browser also requires an explicit irreversible
acknowledgement and offers export first. The server obtains the email from managed
Auth, verifies the password through Auth and checks the returned identity against
the verified caller. Body-supplied owner/email fields are rejected. Passwords and
temporary tokens are used only in request memory, excluded from validation error
responses, storage and application logs. Five attempts per 15 minutes per owner
are reserved atomically before password verification; Auth's own limits also apply.
Anonymous identities and MFA-enrolled accounts are refused by this password-only
flow; future MFA support must add a fresh verified challenge rather than bypass it.

The temporary verification session is signed out before the server calls managed
Auth hard deletion (`should_soft_delete=false`). Existing cascading foreign keys
remove owned application rows, revisions, snapshots, notifications and receipts.
Migration `20261111152226` adds the missing private recipe-request ownership FK.
The aggregate live-test spend reservation is retained; deleting an account never
refunds actual or conservatively reserved spend. The existing active-session
checks deny surviving signed JWTs at the API and Data API boundaries once managed
Auth sessions disappear. Repeated requests with deleted credentials receive 401;
there is no recovery endpoint or retained account snapshot.

## Private files and partial failure

Source artifacts live outside PostgreSQL. An invoker cascade trigger queues only
deleted source UUIDs and queue timestamps in `private.deleted_source_artifacts`.
The private table has RLS, no browser grants, and a narrow internal Auth insert
policy for the cascade; only the service cleanup RPC can list/acknowledge jobs.
There is no user ID, email, health payload or undo snapshot in this queue.

The API immediately attempts removal of each exact UUID directory. It validates
the final resolved absolute target, refuses symlinks/junctions and preserves other
sources, shared synthetic replay, public food caches, model caches and research
resources. Failed cleanup leaves a durable job; the API's lifespan worker retries
every 30 seconds while an API process is running, including after process restart.
Successful removal precedes job acknowledgement. Multiple workers can safely
retry missing files. A failed final source DB write also attempts to remove its
new uncommitted synthetic directory, covering a concurrent account deletion.

Auth/database deletion has no grace period even if file removal is pending.
The response distinguishes confirmed account deletion from pending file cleanup;
the browser displays that distinction, clears local Auth and cross-tab state and
performs a full navigation to discard private component/router drafts. An Auth
outage or ambiguous delete timeout does not produce an invented success receipt.
An operator must monitor cleanup backlog and run API workers against the same
private artifact volume. This single-host assumption remains a deployment gate.

## Limits and release gates

This implements active application deletion, not instant erasure from managed
provider backups, security logs or user-downloaded exports. Provider retention
periods, an operational restore process that cannot resurrect deleted accounts,
cleanup monitoring/storage configuration and support contact remain required
before public release. Supabase Storage is currently unused (zero objects); if
introduced, owned Storage objects must be removed before Auth hard deletion.
Do not silently reintroduce a soft-delete recovery window or enable real-patient
records under the current synthetic development authorization.

Supabase references checked: [hard delete](https://supabase.com/docs/reference/javascript/auth-admin-deleteuser),
[user deletion and Storage constraint](https://supabase.com/docs/guides/auth/managing-user-data#deleting-users),
[session revocation checks](https://supabase.com/docs/guides/auth/sessions).
The installed Auth JS 2.117.3 implementation was inspected for local removal and
cross-tab sign-out after the deleted identity returns 401/403/404.

## Acceptance evidence

[Deletion validation](../reports/account-deletion-validation-2026-11-11.md)
maps confirmation, reauthentication, ownership, revocation, FK/file cleanup,
failure/retry and browser cache behavior to GL-P08-006 and related partial cases.
Changes remain local and uncommitted for review. Scratch replay stays deferred.
