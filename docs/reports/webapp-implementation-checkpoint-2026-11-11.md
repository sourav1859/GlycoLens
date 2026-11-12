# Web application implementation checkpoint - November 11, 2026

Latest follow-up: [November 12 review](demo-logout-compose-review-2026-11-12.md) adds demo/logout/local Compose changes and two planned P09 cases (146 current cases). Dated observations below remain historical.

The cloud-backed core workflow is implemented for development. This checkpoint
does **not** close every phase or authorize public release. Changes remain local,
uncommitted and unpushed for review, based on `c36493d9b05ac729c4e66fb03b5ca6a05261d919`.
The [source manifest](webapp-release-manifest-2026-11-11.json) identifies the local
code, lockfiles, model and migrations; the [144-case ledger](../testing/webapp-validation-results.json)
separates complete observations, partial coverage, blocked prerequisites and tests
not run. No research model was promoted or retrained.

## Delivered development behavior

| Phase | Implemented | Remaining acceptance/dependency |
|---|---|---|
| P00 | Redacted cloud preflight/target guards; offline and opt-in protected CI definitions; OpenAPI snapshot/drift tests; private-file/image exclusions; toolchain and spend envelopes | Hosted GitHub jobs/environment protection have not run; local review only |
| P01 | Atomic cloud bootstrap/hardening; forward migrations; verified JWT/RLS reads; service-only owner-derived writes; two-user run-scoped harness/cleanup | Fresh scratch replay explicitly deferred; full adversarial identity matrix and separate failure rehearsal partial |
| P02 | Original GlycoLens responsive tokens/shell, mobile bottom nav, tablet rail, desktop sidebar, dialogs/loading/errors/deep links | Automated subset passes; screen reader, physical keyboard/safe areas, zoom/contrast and broader device UAT remain |
| P03 | Development email/password UI; server-verified/revocable sessions; minimal resumable/versioned/CAS onboarding; optional-field skip/review; profile/preferences/logout | Real email verification/reset/resend, hosted redirects/password policy, abuse limits and verified anonymous upgrade remain |
| P04 | Common food/scan/recipe composer; deterministic gram/yield/portion math; reviewed planned/eaten save; frozen ingredient facts; idempotent receipts; revisions/edit/cancel/copy; scoped in-memory drafts; date/slot/pagination | Real phone camera, representative extraction/grounding accuracy and broader interrupted-draft/device matrix remain; uncached OFF reads require project contact |
| P05 | Real pinned simulator and cached Chronos C3 cloud pass; distinct source sessions; frozen meal/context/result; owned list/detail/quantiles/chart/table/unit display; scoped past-outcome retrieval | Full timeout/cancellation/failure matrix, model-readiness and hosted cold/warm performance acceptance remain |
| P06 | One consumed-only server aggregate used by Home, Meal log and Nutrition; source clock/local dates; seven-day table; unknown/known coverage; consistent app-timezone labels | Optional goal entry/editing and complete goal-history UI acceptance remain; no default targets are invented |
| P07 | Honest catalog-unavailable states at Search/Favorites/product/recipe detail routes; provider-backed composer remains usable | Corrected catalog release, admission/license/capacity checks, actual database search/detail/favorites remain blocked |
| P08 | Owned profile/settings; bounded no-store export; trusted deduplicated nonclinical notifications; owner-only mark-read/pagination; accurate development notices | Immediate password-confirmed deletion implemented with no recovery window; provider retention/restore and support contact pending; sensitive password/email lifecycle and broader manual acceptance remain |
| P09 | Bounded 10–200% portion requests against frozen origin/context/model; separate scenario persistence; virtual-clock advancement; checksum-verified later observations; error/coverage and eligible outcome save | Full comparison UI/partial-failure/source-collision matrix and manual follow-up usability remain |
| P10 | Local review Docker/Compose/Caddy templates, nonroot/loopback boundaries, portable simulator path settings and explicit hosting/recovery checklist | Complete Linux API/isolated simulator build, CPU-wheel/image audit, readiness/load/restart/recovery, HTTPS/SMTP/domain and hosted UAT pending |

`/` is a public entry; `/demo` retains the earlier labeled virtual workflow.
Private pages require an account and server-validated onboarding. Required setup
collects timezone, glucose unit, source and a versioned research notice only.
Body measurements, diagnosis and medication regimens are not required. No real
patient data, dosing, pump control or clinical-safe portion claims were added.

## Cloud schema and authorization

The approved development target is `ecynkzptuslkuhjikzfc` (`us-west-2`). It was empty
before the first apply. The original four migrations were preserved, bootstrap and
permission hardening applied atomically, and later changes used forward migrations.
All **14 canonical versions/names/normalized-LF SQL hashes** match repo source.
There are **18 public tables with RLS**. No hosted reset was used.

Ordinary reads retain the caller JWT. Authoritative writes go through narrowly
whitelisted invoker RPCs with the verified owner injected by FastAPI. A private
boolean definer checks the exact signed session ID against managed Auth sessions;
restrictive RLS gates also prevent a logged-out JWT from reading Data API rows.
See [ADR 0019](../decisions/0019-trusted-cloud-writes-and-frozen-source-context.md).

The [schema evidence](cloud-schema-checkpoint-2026-11-11.json) records matching
history and **zero remaining app users, tagged Auth test users and synthetic-test
foods** after cleanup. One persistent labeled demo food plus public USDA/OFF
provider cache entries are intentional, not a corrected catalog release. The
[security advisor](p08-deletion-security-advisors-2026-11-11.json) reports four INFO items:
private receipt/budget/attempt tables have RLS and no browser policies/grants, deliberately
denying browser access. These are not a claim of zero findings. See the
[advisor explanation](https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy).

## Test observations and limits

- Initial relevant baseline: 91 Python and 5 frontend unit tests, with frontend
  lint/types/production build. Final counts/commands are recorded in the validation
  summary and ledger; ordinary Python tests deny real network transports.
- Final relevant offline suite: **160 passed** in the minimal locked environment.
  Frontend: **24 unit tests passed**, plus lint/types and production compilation.
  The earlier standalone Linux web image (before the deletion UI follow-up)
  returned HTTP 200 as UID 1000; runtime inspection
  checked 1,676 files with zero private-file/key findings. Its temporary container
  was removed. These checks do not establish API/simulator/hosted readiness.
  [Web image evidence](p10-web-image-2026-11-11.json).
- A separately created minimal offline environment installed 25 locked packages
  without model/research dependencies. Its relevant suite passes after the
  reviewed API snapshot was updated for intentional new endpoints/filters.
- The final structured browser run reports **20 passed, 0 skipped, 0 unexpected,
  0 flaky** across desktop/mobile projects. It covers 320/360/390/430/768/820/1024/
  1280/1440/1920 shell widths, dialog Escape/focus return, protected routes,
  onboarding resume/skip, fractional meals, unknown nutrients, in-app draft
  recovery, populated Home/Nutrition reflow, permanent deletion/cross-tab cleanup
  and retained demo behavior. These use
  explicit browser fixtures, not a substitute for real cloud acceptance or devices.
- Cloud P01: **53 requests** passed revised grants, trusted saves, isolation,
  rollback/idempotency and scoped cleanup. [Evidence](p01-cloud-integration-validated-2026-11-11.json).
- Cloud P03: **84 requests** passed real password/refresh, revoked-session denial,
  resumed onboarding, skip/review/CAS and versioned acknowledgement.
  [Evidence](p03-account-integration-2026-11-11.json).
- Cloud P04: **59 requests** verified 125-g repeated ingredients = 225 kcal /
  37.5-g carbs, unknown fiber, changed-payload retry conflicts, frozen facts on
  edit, atomic failure and cancellation history. [Evidence](p04-meal-integration-2026-11-11.json).
- Cloud P05/P06: **106 requests** included a real pinned py-mgipsim execution and
  real cached Chronos C3 result. Exactly 24 points persisted; retry and B denial
  passed; meal edits/cancellation/same-clock replay left old forecast evidence
  unchanged. A 250-g eaten fixture contributed 450 kcal, then 225 after editing,
  then zero after cancellation. [Evidence](p05-p06-source-integration-2026-11-11.json).
- Cloud P08: **74 requests** passed notification deduplication/ownership/read
  state and own-account export isolation. [Evidence](p08-privacy-integration-2026-11-11.json).
- Cloud P09 validated run: **115 requests** passed real 50/75/100% comparisons
  using identical frozen context/model; 100% matched baseline points exactly.
  Scenarios left eaten totals unchanged. Actuals were unavailable until the clock
  advanced; 24 genuine later virtual samples produced independently recomputed
  errors. A stale clock retry was rejected 409.
  [Evidence](p09-scenario-integration-validated-2026-11-11.json).
- Separate aggregate/concurrency run: **51 requests** verified a 25-hour New York
  day, exact exclusive boundaries, 30 eaten rows = 3000 kcal / 300-g carbs despite
  20-card pagination, one missing-fiber count, UTC regrouping to 29 rows, and 12
  concurrent scenario writes producing exactly 10 rows plus two 429 rejections.
  These direct synthetic oracle rows do not claim model inference or reviewed
  meal-save acceptance. [Evidence](p06-p09-aggregation-integration-2026-11-11.json).
- Bounded provider run: **22 total requests**, at most two USDA reads and one OFF
  read, confirmed live source access and explicit 100-g cache facts. This is
  access/basis evidence, not package-label truth, real camera or representative
  nutrition accuracy. [Evidence](p04-provider-integration-2026-11-11.json).

Every cloud runner used explicit exact-target guards, recorded run-tagged
synthetic identities and scoped teardown. No Auth email was sent. No new paid LLM
call occurred. Prior estimated USD **0.00763580** remains in the conservative USD 5
reservation ledger. Ten-per-day and total-cap tests ran in a rolled-back SQL
transaction and left zero recipe request rows. Published-price estimates are not
invoice reconciliation. CPU Chronos tests are distinct from paid recipe extraction.

## Failures corrected and evidence interpretation

The initial P01 run exposed PostgREST mapping unknown-food `P0002` to HTTP 500.
Known domain errors now become 422; actual storage outages remain 503. Initial
failure/diagnostic reports were retained. An aggregate migration first failed on a
SQL alias and rolled back, then applied after correction. No partial schema was
used as a pass.

The first browser attempts lacked the pinned runtime and installed Chrome failed
to launch. The matching official Playwright browser was installed in ignored cache.
The first working runs found test-selector mistakes (helper text and nutrient
units). Selectors were corrected; final 16-test evidence is clean. An overlapping
second browser invocation was refused because its test port was in use; it was
then run sequentially. A container build caught a draft-state TypeScript optional
type error; that code was corrected and the production build subsequently passed.
Do not interpret these earlier failed attempts as phase acceptance.

Some early harness `case_id` labels were broader or incorrect relative to the
predeclared catalog. The original JSON observations are retained. The ledger maps
the actual observation to the matching catalog case and marks combined/untested
parts PARTIAL; it does not blindly import the harness's PASSED label. For example,
the original source report's GL-P05-010 observation is immutable-history evidence,
not a busy/cancellation test. No observation or model output was changed to fit a
case. [Canonical traceability](webapp-evidence-map-2026-11-11.json).

The manifest hashes the **reviewed current worktree**. Earlier cloud runners
captured run ID/time but did not capture an exact pre-run worktree digest. The
ledger discloses that limit instead of inventing historical revision identity.
Release acceptance requires revalidation from a recorded reviewed revision.

Final nutrition review also found a stale-copy race. The current composer/demo
now send reviewed nutrient facts as a comparison guard: the database compares
them within the calculation transaction and rejects changed facts with 409 and
no partial meal. Existing edits use frozen facts; copied drafts load current
trusted facts separately and require review. A bounded refresh action clears the
confirmation before retry. **37 cloud requests** verified changed-fact rollback,
refresh/review, original frozen nutrition and distinct copied nutrition; the new
browser copy test verifies the fresh preview and planned status.
[Evidence](p04-reviewed-facts-integration-2026-11-11.json).

The attestation field is optional for compatibility with older API callers. Those
callers still calculate from server facts but do not gain stale-review checking;
the current shipped UI entry paths supply it. Versioned API compatibility and
complete catalog acceptance remain explicit release work.

## Immediate deletion follow-up

The user selected immediate deletion with no recovery window. Fresh password
verification and explicit confirmation now hard-delete managed Auth and owned app
records, with source-only durable retry jobs for private files. A 116-request
two-owner cloud test passed, including private usage/receipt cascades, session
revocation, injected file failure/retry and preservation of B/shared replay.
Desktop/mobile browser fixtures cover deliberate confirmation, cancellation,
wrong password, cross-tab sign-out and protected-route cleanup. The full relevant
suite now has 160 Python and 24 frontend unit passes, with 20 browser passes.
See [ADR 0020](../decisions/0020-immediate-account-deletion.md) and
[detailed evidence/provenance](account-deletion-validation-2026-11-11.md).

## Open inputs and release boundaries

1. **Project support contact** is still awaiting the user's answer. Immediate
   confirmed deletion is implemented with no recovery window; provider backup/log
   retention and restore reconciliation remain release gates. Do not publish a
   personal address without authorization.
2. **Open Food Facts project contact** must be configured privately before any
   new uncached read. A repository URL is not the required contact email; the new
   guard returns a useful unavailable response. Cached reviewed facts remain
   readable. The existing v2 adapter is backward compatible but deprecated;
   staging/v3 migration and ODbL reuse/attribution review remain before release.
   [Official OFF requirements](https://openfoodfacts.github.io/openfoodfacts-server/api/).
3. **Corrected catalog release** is not ready. Actual database recipe/product
   search/details/favorites cannot pass admission or live-data acceptance yet.
4. **VPS/domain/SMTP** are pending. Development automatic confirmation is not
   proof of email ownership or recovery. No public deploy or production mutation
   occurred. Hosted redirects, delivery, resource/restart/recovery and device UAT
   remain required.
5. **Scratch replay/restore** remains explicitly deferred; no repeat permission
   request or reset of the development project was used.

USDA's key/search/detail contract and attribution were checked against the
[official API guide](https://fdc.nal.usda.gov/api-guide/). Provider facts stay separate
from the corrected catalog admission gate and frozen saved meal snapshots.

## Reproduction and review

Use root ignored `.env` and frontend ignored `.env.local` for development. Start
the API with `uv run --no-sync python -m uvicorn backend.app.main:app --reload` and
the web app with `pnpm frontend:dev`. Sign in/register at the public entry, complete
minimal setup, run a virtual source from Home, review and save a meal, then request
the forecast. Only synthetic information belongs in this development project.

Offline: `uv run --no-sync python -m pytest -p scripts.quality.offline_pytest backend/tests tests/quality tests/contract tests/database tests/research/models/test_forecast_adapters.py -q`;
`pnpm frontend:check`; `python -m scripts.quality.check_api_contract`;
`python -m scripts.quality.check_public_files`. Browser tests need the matching
Playwright Chromium runtime. On this Windows machine it is in ignored
`.cache/playwright-browsers`; set `PLAYWRIGHT_BROWSERS_PATH` accordingly.

Cloud runners default to dry run; see [runner instructions](../../scripts/dev/README.md).
Do not repeat real-model/provider tests or paid smoke calls without a relevant
change and the same bounded allowance. New GitHub workflow definitions have not
been pushed/run; their hosted acceptance stays open. See [packaging notes](../../infra/README.md)
for remaining Linux/hosting work. Graphify refresh evidence is local, scoped and
separate from product behavior or medical evidence.
