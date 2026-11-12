# ADR 0021: One-command local application runtime

Date: November 12, 2026. Status: accepted for local development review.

## Decision

Use root `compose.yaml` for local startup: `docker compose up --build -d --wait`.
Run Next.js and one FastAPI worker in two containers. Keep CPU Chronos inference
behind the existing API adapter and py-mgipsim in a separate interpreter inside
the API image. A service/repository split is unnecessary for local orchestration.
Application Auth/database remain the dedicated managed cloud Supabase project.

The API uses the frozen uv dependency graph with Linux CPU PyTorch; the simulator
uses its own frozen dependency lock and verified upstream Git commit. Images run
as nonroot users. Only loopback ports are published. Web waits for API liveness;
this is not proof of model or cloud readiness. The smoke report must verify those
dependencies separately. First builds need registry/package/upstream network access.

Mount the existing reviewed model cache read-only, offline at runtime. Persist
private simulation/replay artifacts in the existing host `artifacts/simulation` bind mount,
including the deletion-cleanup source paths. This keeps host and Docker runtimes on the same source files and prevents the
cloud deletion queue being acknowledged by a runtime with a different empty store.
An empty artifact directory has no replay until a new simulation runs. Do not copy host virtual environments, research
datasets, secrets or weights into images. No local Supabase/Postgres is started.

Only the API receives the ignored `.env` at runtime. The frontend receives the
public URL/publishable key/API origin at build time. Private secrets must not be
build arguments, frontend environment or printed by expanded Compose diagnostics.
Changing public configuration requires a web rebuild.

## Limits

This is a built-image local runtime, not hot reload or a public deployment.
Supabase/provider features still need internet. Stop manually launched listeners
on 3000/8000 before using defaults, or select alternate local ports and rebuild.
Do not kill an existing process automatically. `docker compose down` retains the
host simulation directory. Never remove private source artifacts as routine cleanup.
If overriding the bind path, migrate the complete private source store and ensure
all API cleanup workers use it. Linux hosts must grant UID 10001 write access to
that dedicated directory. Docker Desktop Windows mounts were validated.
Normal startup resumes the existing account-deletion retry worker; controlled
runtime tests explicitly disable it to avoid incidental cloud queue polling.

`infra/compose.yml` remains the explicit domain/HTTPS hosting template. Domain,
proxy, email, restore, hosted capacity and release acceptance are separate gates.
Docker does not remove them. No public deployment, cloud schema mutation or paid
provider test is authorized by this runtime change.
