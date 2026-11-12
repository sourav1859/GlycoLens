# Demo, logout, meal-response validation and local Compose review

November 12, 2026 development checkpoint. The user subsequently authorized
[committing and pushing this source](github-checkpoint-delivery-2026-11-12.md);
public deployment remains unauthorized.

## Findings and resulting changes

1. **Demo names were misleading.** Replaced “Run live scenario” / “Use cached
   replay” with **Run new simulation** / **Replay saved simulation**, including
   progress/result text. Added a fixed-scenario/clock and server-replay explanation.
   The request still sends `replay: false/true`; simulation and forecasting behavior
   are unchanged.
2. **Logout existed but was buried in Profile.** The shared responsive header and
   demo now expose one reusable Sign out control. It calls the existing managed
   Supabase sign-out flow (SDK default global scope), clears private UI state and
   navigates to sign-in. Anonymous users must confirm losing identity access.
   The demo subtree is keyed by account identity, which discards drafts/results
   and camera state after cross-tab logout or account change. Private routes keep
   the existing AccountGate and independent revoked-session API/RLS checks. No
   new logout/password endpoint or schema change was needed.
3. **The plan had portion arithmetic and comparable scenarios, but lacked an
   explicit application meal-response sensitivity gate.** Added GL-P09-011 and
   GL-P09-012, raising the current catalog to 146 cases. The
   [protocol](../testing/meal-response-validation-protocol.md) separates controlled
   meal/portion sensitivity from accuracy on genuinely matching outcomes. Both
   remain unexecuted. The fixed simulator's preset meal trajectory cannot prove
   accuracy for an arbitrary added meal; consumed research test cohorts cannot be
   reused for a new independent claim. No model promotion or clinical claim.
4. **Existing Compose was a domain-dependent hosting template.** Added root
   `compose.yaml` for one-command local web/API startup. CPU Chronos remains inside
   the modular API, and the pinned simulator uses its own Linux interpreter inside
   that image. Managed cloud Supabase remains external. No extra repository,
   forecasting service or local Supabase is necessary. See [ADR 0021](../decisions/0021-local-compose-runtime.md).

## Local command and operational implications

From the repository root, with Docker Desktop, existing ignored `.env` and the
reviewed model cache available:

```powershell
docker compose up --build -d --wait
```

Open `http://127.0.0.1:3000`. Stop manually launched listeners on 3000/8000 first,
or select the documented alternate ports and rebuild. The first build downloads
dependencies; subsequent source/public-config changes require rebuilding. Cloud
features still need internet. No domain or SMTP is needed for the approved dev
Auth exception. Details and the explicit runtime smoke are in [infra/README](../../infra/README.md).

Only the API receives private runtime configuration. Web gets public settings at
build time. Model weights mount read-only; simulation snapshots/replay use a
persistent bind mount of the existing host artifact directory. This preserves
PowerShell-created replay/source files and keeps deletion workers on the same
complete source store. An empty directory needs **Run new simulation** before
replay. Shutdown retains data; do not remove source files as routine cleanup.
Custom storage must be shared by every deletion worker. Normal app startup resumes
the existing retry worker for already confirmed deletions; controlled runtime
validation disables that worker to avoid incidental cloud queue polling.

Docker [documents health-conditioned dependencies](https://docs.docker.com/compose/how-tos/startup-order/);
the web waits for API liveness. Liveness is not model/cloud readiness, so the
opt-in smoke exercises the real simulator and cached model separately. Public
configuration uses [Compose interpolation](https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/).
The explicit Linux CPU source follows [uv's PyTorch guidance](https://docs.astral.sh/uv/guides/integration/pytorch/).
Logout preserves [Supabase SDK behavior](https://supabase.com/docs/reference/javascript/auth-signout).

## Actual validation

- **171 offline Python tests passed**, one pre-existing opt-in two-run simulator
  reproducibility test skipped. The single real Linux simulator/model smoke below
  is separate evidence and does not turn that skipped test into a pass.
- **24 frontend unit tests passed**; lint, type checking and Next production build
  passed. OpenAPI matches the existing reviewed contract.
- **26 desktop/mobile Playwright journeys passed**, including both simulation
  request modes, shared-header logout, anonymous confirm/cancel, cross-tab draft
  clearing and protected navigation after logout. All use isolated synthetic
  HTTP fixtures; no new live cloud Auth journey is claimed. Existing independent
  cloud session-revocation evidence remains in the prior checkpoint.
- Built both Linux images and started the complete stack with one Compose command
  on alternate loopback ports 3100/8100, leaving manually launched services alone.
  Both became healthy. Public entry/demo/sign-in returned 200; private API without
  credentials returned 401; allowed CORS preflight returned 200 and an unapproved
  origin 400.
- Real isolated Linux simulator produced **288 samples**; cached Chronos produced
  **24 forecast points**, using `torch 2.14.0+cpu`, model revision
  `29ec3766d36d6f73f0696f85560a422f50e8498c`. Combined smoke took **28.66 seconds**
  on this local Docker engine. This is one execution, not a p95/capacity result.
- Restarted the validation containers; HTTP recovered and a scoped synthetic
  artifact sentinel survived. Confirmed read-only model mount and writable shared
  simulation bind mount. This does not prove cloud backup/restore or full source replay.
- Scanned **1,687 web runtime files**, finding zero private credentials or prohibited
  environment/model/key files; server secrets were absent from web configuration,
  image metadata and build history. Both images run nonroot. This is a scoped local
  image review, not a complete vulnerability/layer supply-chain audit.
- Temporary containers were stopped; host artifacts were retained. **Zero paid
  LLM calls**. Foreground validation makes no cloud requests. Earlier startup with
  the normal deletion worker may have polled the managed queue; those background
  requests were not counted. The final controlled run disables this worker.

The first container smoke exposed a portability bug: resolving `venv/bin/python`
followed its Linux symlink to system Python and bypassed isolated dependencies.
A failing regression reproduced this, then passed after preserving the absolute
venv entry-point path. The real Linux smoke subsequently passed. Linux now uses a
CPU wheel of the same PyTorch version; Windows/macOS package sources and model
checkpoint/feature semantics are unchanged. The earlier browser attempt was blocked
by a running Next development output lock, not counted as a feature-test result;
the fixture server now uses its own ignored `.next-e2e` output directory.

Sanitized [machine-readable evidence](demo-logout-compose-validation-2026-11-12.json)
and [source manifest](webapp-release-manifest-2026-11-12.json) record this checkpoint.
The [case ledger](../testing/webapp-validation-results.json) preserves partial and
blocked gates. No complete phase or public release is closed by these results.

## Documentation review and remaining gates

Updated planning 00/01 (summary/navigation), 03 (UX), 04 (runtime architecture),
05 (evaluation), 06 (milestones), 08 (risk), 09 (formal summary), 10 (implementation
checkpoint) and 17 (phase work/cases), plus UI architecture, README, infra guide,
test catalog/ledger and ADR 0021. Reviewed plan 02's model/adapter strategy and
existing protocol-16 boundary; model candidates, real-data splits and consumed
research tests are unchanged, so those protocols were not rewritten.

P09 sensitivity execution and independent matching-outcome accuracy remain open.
P10 still needs dependency-readiness/outage/concurrency/resource envelopes, hosted
HTTPS/domain/Auth/email acceptance, complete image audit, scratch restore and
physical/manual UAT. Corrected catalog and verified anonymous upgrade remain
separate gates. GitHub publication of this checkpoint is now authorized; historical
validation below the publication decision remains development-only evidence.
