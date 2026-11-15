# Local application containers

## November 14 local research exposure

The user requested LightGBM in the current local UI. Its ignored root `.env` now enables the option and the existing `glycolens-local` API was recreated on port 8000, with web 3000 retained. The verified narrow bundle stays read-only; Chronos remains default. Only this private local configuration changed; `.env.example` still defaults to false. Reload the meal/demo page to recheck capabilities. Prepare the 48-hour source and save a new meal before native inference; old short-source meals remain unchanged. Formal acceptance and production exposure remain pending. See [verification](../docs/reports/local-lightgbm-enablement-2026-11-14.md). The November 12 off-state descriptions below are historical.

## Optional native research model — November 12

The root API image now includes frozen `chronos` and `refinement` dependency groups. Chronos remains default. `GLYCOLENS_LIGHTGBM_ENABLED=false` is the ordinary setting. Native loading additionally requires the approved exported serving bundle at `GLYCOLENS_LIGHTGBM_BUNDLE` (host default `artifacts/models/lightgbm`) and its exact `GLYCOLENS_LIGHTGBM_MANIFEST_SHA256`; Compose mounts that narrow directory read-only at server `GLYCOLENS_LIGHTGBM_BUNDLE_DIR`. No research dataset/joblib mount or separate model service is needed. Export only trusted frozen artifacts with `scripts/dev/export_lightgbm_bundle.py`; never substitute an unreviewed digest/model. Missing or corrupt bundles reject native inference without fallback.

The isolated review stack `glycolens-implementation-check` at web 3102/API 8102 uses `.cache/compose-model-validation.env` as a non-secret override after the existing `.env`; it alone enables the research option. Native requests require explicit 48h simulation preparation. Disabling/recreating the API preserves existing owned native reads and default Chronos. No migration runs on container startup. [Actual packaging/performance/recovery](../docs/reports/lightgbm-app-validation-2026-11-12.md). Full Chrome/hosted resource acceptance remains open; do not copy review enablement into normal/public settings.

From the repository root with Docker Desktop's Linux engine running:

```powershell
docker compose up --build -d --wait
```

Open <http://127.0.0.1:3000>; API liveness is <http://127.0.0.1:8000/health>.
Root `compose.yaml` starts web/API together. CPU Chronos and the isolated Linux
simulator remain inside the API image. Auth/database use managed cloud Supabase;
no local Supabase starts. These are local review artifacts, not a deployment.

Prerequisites: existing ignored root `.env` with cloud URL, publishable key and
server key; reviewed pinned model snapshot in `artifacts/models/huggingface`;
internet for the first build and cloud/provider requests. Recipe/USDA features
use existing private runtime keys. No domain/SMTP is required for the approved
development Auth exception. Release email gates remain open.

Stop manually launched apps on 3000/8000 first, or select alternate ports in this
same PowerShell session and rebuild:

```powershell
$env:GLYCOLENS_WEB_PORT = '3100'
$env:GLYCOLENS_API_PORT = '8100'
docker compose up --build -d --wait
```

Then open <http://127.0.0.1:3100>. Next.js public settings are build-time values;
rebuild after changing URL/key/API port. Browser requests use the host loopback
API address; `api` is not a browser hostname. Set exact Auth redirect allowlists
for email flows on the chosen origin. Local CORS allows localhost and 127.0.0.1.

```powershell
docker compose ps
docker compose exec api /app/.venv/bin/python -m scripts.dev.check_container_runtime
docker compose down
```

Healthchecks prove HTTP liveness. The opt-in smoke exercises the real fixed
simulator and one cached CPU forecast using synthetic nutrients, with no cloud
writes or LLM calls. It prints aggregate results and removes scratch files. It
does not establish meal sensitivity/accuracy or cloud/provider acceptance.
This is a built-image runtime; source edits need rebuilding. Weights mount
read-only, with offline model loading. A missing host cache fails startup;
incomplete weights fail the smoke or forecast. Provision the reviewed checkpoint
separately, never in the image. Use `docker compose config --quiet` for syntax;
expanded config output can expose private runtime values.

`docker compose down` retains the existing host `artifacts/simulation` directory.
The local bind mount preserves PowerShell-created replay/source files and keeps
account-deletion workers on the same storage. An empty directory needs **Run new
simulation** before replay; the smoke does not seed a replay. Do not remove source
files as routine cleanup. A custom artifact path must contain the complete source
store and be shared by every cleanup worker. Linux hosts must grant UID 10001 write
access to this dedicated directory; Docker Desktop Windows mounts were validated.
Normal startup resumes the existing deletion-retry worker for already confirmed
deletions. It does not reset/migrate the database or make paid LLM calls. Controlled
runtime tests set `GLYCOLENS_DELETION_CLEANUP_WORKER=0` to avoid queue polling; do
not leave that test override enabled for normal account deletion.

See [ADR 0021](../docs/decisions/0021-local-compose-runtime.md) and
[actual validation](../docs/reports/demo-logout-compose-review-2026-11-12.md).

## Hosting preparation

`infra/compose.yml` remains a separate domain/HTTPS hosting template. Invoke it
explicitly with `docker compose --env-file .env -f infra/compose.yml ...`.
VPS/domain, exact Auth redirects and SMTP are pending.

- `Dockerfile.api` uses the frozen application + Chronos dependency group, one
  API worker and a read-only reviewed Hugging Face cache. No model downloads at
  runtime. Linux uses the CPU wheel; local smoke evidence does not establish
  measured Hostinger resource acceptance.
- `Dockerfile.web` packages standalone Next.js, with only publishable Supabase
  settings and the public API origin supplied at build time. Never supply server
  keys as build arguments. Email delivery remains disabled for this dev image.
- `compose.yml` binds both app ports to host loopback. It requires a domain and
  reviewed model-cache path. The root ignored `.env` supplies API secrets only.
- `Caddyfile` is a host reverse-proxy template for HTTPS and the same-origin API.
  Its automatic certificate/hostname validation has not run.

The API image packages an isolated **Linux** simulator interpreter and verified
upstream commit. Never mount a Windows virtualenv into Linux. Runtime readiness
must be checked with the smoke in addition to HTTP liveness.

Before public hosting: pin audited image digests/CPU dependencies, build and scan
images, inspect layers for private files, mount model and simulator data with the
correct nonroot UID, measure cold/warm inference and memory under one-request
concurrency, verify restart persistence and backup/restore in an authorized
scratch project, then run HTTPS/Auth/camera/manual accessibility UAT. Keep the
source artifacts volume private: it holds synthetic future trajectory data that
must never be served directly or read by model inputs before source-clock advance.

Rollback is a previous immutable application image with compatible schema. Do
not reset managed Supabase or reverse forward migrations blindly. Rehearse data
recovery separately; configured volumes are not backup evidence.

Account deletion uses the same private simulation storage in the API and its
default 30-second cleanup loop. A durable cloud job survives a filesystem outage;
there is no account recovery window while files retry. Keep all API processes on
the same artifact storage and monitor queue age/failures. Test process restart,
storage permissions and deletion-preserving restore before hosting; do not leave
the controlled-test cleanup-worker override enabled. See ADR 0020.
