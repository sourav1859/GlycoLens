# Repository strategy and development readiness

Subsequent confirmed decision: the user selected dedicated **cloud Supabase
development from now on**, email/password verification/reset and staged full-feature
delivery. [Plan 17](../planning/GlycoLens_17_Webapp_Implementation_Plan.md) and
[ADR 0018](../decisions/0018-cloud-supabase-and-staged-webapp-delivery.md) govern
execution; earlier local-DB baseline suggestions in this assessment are superseded
for new app setup/integration. The monorepo recommendation and source findings remain.

**Reviewed:** November 10, 2026. **Status:** advisory assessment supporting the existing modular-monolith and responsive UI decisions; no repository split, runtime refactor, migration or deployment performed.

## 1. Recommendation

Keep **one GlycoLens Git repository**, with the existing `frontend/`, `backend/`, `research/`, `supabase/`, `tests/`, `scripts/` and `docs/` boundaries. Develop the new application incrementally around the working meal-to-forecast prototype. Three repositories are not a prerequisite for professional separation, independent builds or future scaling.

For the current application, use two main application runtimes: Next.js and FastAPI. Forecasting remains a backend-invoked library behind the canonical adapter; py-mgipsim retains its isolated subprocess environment. Managed Supabase remains external. This reaffirms [ADR 0009](../decisions/0009-m2-authenticated-application.md), [ADR 0016](../decisions/0016-initial-hostinger-kvm2-managed-supabase.md), [ADR 0017](../decisions/0017-responsive-webapp-and-figma-reference-boundary.md) and [architecture section 14](../planning/GlycoLens_04_Tech_Stack_and_System_Architecture.md#14-repository-and-developer-tooling-boundaries).

The Figma-inspired UI adds routes and user state, but does not establish a need for microservices or independently governed Git projects. The repository already has distinct frontend and Python toolchains. The important preparation is to make their contracts, test gates and deployment packaging reliable.

## 2. Four different boundaries

| Boundary | Meaning for GlycoLens | Recommended now |
|---|---|---|
| Git repository | Code history, access and change review | One repository; related UI/API/migration changes reviewed together |
| Module/package | Code ownership, imports and dependencies | Distinct frontend features, backend services and reusable forecast adapters |
| Process/container | Memory, dependency and failure isolation | Separate web/API runtimes; isolated simulator; forecast model in one API process initially |
| Deployment/release | Which artifact is built, restarted or scaled | Separate web/API artifacts with an explicit compatibility record, even from the same Git revision |

One repository can produce multiple images and deployment units. Compose supports services, networks and volumes for a multi-container application; it does not require separate Git repositories. [Docker Compose documentation](https://docs.docker.com/compose/).

A separate forecast **service** can also remain in the same repository. A separate Git repository becomes useful for independently managed access, ownership or releases. A model-weight registry/cache is another concern: weights and research datasets remain outside Git, regardless of the source-code arrangement.

## 3. Source evidence and current findings

The scan covered the living architecture/UI plan, deployment and application ADRs, dependency manifests, executable frontend/API/model/simulator paths, migrations/RLS, browser configuration, test strategy and development tooling. Existing uncommitted November 10 UI documentation was retained.

| Evidence | Finding | Consequence |
|---|---|---|
| [Root package scripts](../../package.json), [pnpm workspace](../../pnpm-workspace.yaml), [Python manifest](../../pyproject.toml) | One JS frontend package and a Python project with optional model/research dependency groups | Different languages do not require different repositories; keep runtime dependencies explicit |
| [Application inference](../../backend/app/services/inference/application.py) | Imports `research.models.adapters`, reads owned meal/context records and persists validated forecasts through the DB client | A backend-only checkout is not currently self-contained; splitting would require a versioned library/service contract |
| [Adapter exports](../../research/models/adapters/__init__.py), [converters](../../research/models/adapters/converters.py) | Common exports include dataset-window converters and `ContextConfiguration`; converters import the dataset adapter | Reusable serving code and research conversion code need a deliberate packaging boundary; do not copy adapters into another repo |
| [Chronos adapter](../../research/models/adapters/chronos2.py) | Pinned model/library revision with lazy model dependency loading | Preserve one canonical implementation and tested input/output contract; UI work does not promote another research model |
| [Application API client](../../frontend/src/lib/application-api.ts), [MealWorkflow](../../frontend/src/features/meal/MealWorkflow.tsx) | Anonymous demo Auth, bearer requests and a largely integrated workflow; several domain types are declared locally | Extract shared API schemas/clients and feature state incrementally; permanent accounts and new pages remain work |
| [FastAPI entry](../../backend/app/main.py) | Only GET/POST are allowed by current CORS configuration; `/health` is basic liveness | Planned cross-origin PATCH requests will need explicit method/preflight support; health does not prove model readiness |
| [Inference](../../backend/app/services/inference/application.py), [simulator](../../backend/app/services/simulation/live.py) | Process-local locks, cached model, shared fixed-scenario artifact paths and explicit 429 busy responses | Multiple workers/replicas need coordination and artifact isolation; splitting Git repositories does not solve concurrency |
| [Simulator](../../backend/app/services/simulation/live.py), [Playwright config](../../frontend/playwright.config.ts) | Windows-specific Python executable paths | Linux deployment/CI require portable launch configuration and verification |
| [GitHub workflow directory](../../.github/workflows/README.md) | README only; no executable workflow checked in | Existing tests are not an automated PR gate yet |
| [Deployment readiness](../decisions/0016-initial-hostinger-kvm2-managed-supabase.md#readiness-and-acceptance) and file inventory | No application Dockerfiles, Compose packaging or `.dockerignore` found | Packaging and safe build-context rules are pending; do not assume a deployable stack exists |
| [Initial schema](../../supabase/migrations/20260929000100_initial_application_schema.sql), [M2 RPCs](../../supabase/migrations/20261014000100_m2_application_contract.sql) | Owner RLS plus broad authenticated writes, including forecasts/outcomes; transaction functions use SECURITY INVOKER | Owner isolation is not proof that derived records were generated by trusted code; review grants and RPCs together before expanding permanent-user features |
| [Root environment template](../../.env.example), [browser client](../../frontend/src/lib/application-api.ts) | Browser requires `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`, which are absent from the root template | Standardize frontend/server templates and actual loading locations before new-account implementation |
| [Responsive architecture](../architecture/responsive-webapp-ui.md), [M3 plan](../planning/GlycoLens_06_Milestones_and_Schedule.md#responsive-ui-architecture-and-page-extraction---november-10) | Route/flow design is documented; required schema, pages and acceptance are not all implemented | A finalized design is a development baseline, not evidence of delivery readiness |

The serving imports point into the research **code namespace**; this is not evidence that private datasets are read during inference. Inspection found a transitive dataset-module dependency, not an automatic dataset load. Before building a minimal runtime image, map that source dependency closure. When it materially simplifies packaging, separate lightweight serving contracts/context definitions from dataset converters in a tested change. A new `forecasting/` folder or package is optional; a wholesale move is not a prerequisite to start the UI.

Environment observation is limited to this tool session: Node, pnpm, Docker and Supabase command launchers were discoverable; `python` and `uv` were not on its PATH. Checking the interpreter referenced by `.venv` hit an access restriction, so machine-wide Python availability is **unverified**, not proven absent. Confirm the supported Python 3.12 environment and reproducible commands in the normal development shell before relying on new test results. No tool installation or environment repair was attempted.

## 4. Option comparison

Scores are architecture judgments (1 weak, 5 strong), not measured performance. They reflect the current capstone scale, coupled features and absence of a demonstrated independent forecasting team/access requirement.

| Criterion | Weight | Monorepo, current serving boundary | Monorepo, separate forecast service now | Three repositories now |
|---|---|---|---|---|
| Delivery fit and reuse | 30% | 5 | 3 | 2 |
| Coordinated correctness/change review | 25% | 4 | 4 | 3 |
| Operational simplicity | 20% | 5 | 3 | 2 |
| Integrated testability | 15% | 4 | 4 | 3 |
| Independent growth/releases | 10% | 3 | 4 | 5 |
| Weighted score / 5 | 100% | **4.40** | **3.50** | **2.70** |

Keeping one repo supports a single review containing a preference migration, FastAPI schema and responsive onboarding screen. A three-repo implementation would need compatible package/API versions, coordinated PRs, integration environments and releases for that same change. Separate services introduce serialization, service identity, timeouts, retry/cancellation and observability even when the Git layout is unchanged.

The recommendation is not that a monorepo makes contracts or releases automatic. Frontend and backend may be deployed at different times; maintain backwards-compatible APIs and record web/API revisions, migration version and model/checkpoint identity for each tested release. CI should run affected checks plus cross-boundary integration checks. Different artifacts can have different dependency sets without separate Git histories.

Separate repositories are stronger when code visibility must differ or teams truly own independent releases. Folder ownership/CODEOWNERS can guide review but does not prevent a repository reader from seeing other folders. No such access requirement was established by this request; it would change the tradeoff.

## 5. Preparation before broad feature implementation

Do not delay all UI work until hosting, catalogs and every planned feature are complete. The useful gate is a reproducible baseline and a small set of explicit contracts. Shell/components can proceed against clearly labeled synthetic contracts while independent provider/cloud prerequisites are resolved.

### A. Freeze a reviewable implementation baseline

Review and commit the accepted UI/architecture documentation through the normal workflow when authorized. Work from short-lived feature branches, with small changes covering one complete user journey. Avoid permanent frontend/backend branches and a large directory rename. Keep course dates and original acceptance evidence unchanged; the full page inventory needs prioritization.

Use the existing roots. Add deployment files when implementing packaging, not as an excuse to migrate to a new monorepo framework. Current pnpm/uv configuration is adequate for this layout; neither Turborepo/Nx nor an extra Python workspace is required merely because frontend and backend share a repo.

### B. Confirm environments and establish a green baseline

Verify Python/uv, pinned Node/pnpm and local Docker/Supabase in the normal shell. Reuse the existing development, database and test commands. Record a fresh baseline for the relevant Python/frontend checks, then create executable CI using commands that have actually passed. Standard PR checks should not download model weights, access research cohorts, call paid providers or require production secrets.

Run model/simulator/live-provider acceptance as explicit opt-in jobs, distinct from ordinary offline tests. Start with straightforward Python/frontend/contract jobs. If path filtering is later added, shared contracts, migrations, manifests and lockfiles must trigger dependent checks; use a reliable always-reporting required gate. Skipped required workflows can otherwise remain pending. [GitHub workflow triggering guidance](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow).

### C. Specify session, schema and API contracts before parallel screen work

Keep Supabase as the Auth provider and FastAPI as the owner of domain orchestration. Define the initial Auth method, confirmation/recovery, anonymous-account upgrade and session-refresh behavior. For server-rendered protected pages, select the Supabase server-session pattern deliberately rather than mixing an unrelated second token store into the client. UI routing checks never replace FastAPI verification and RLS.

Create forward local migrations for the first slice: preferences, onboarding and versioned acknowledgements. Define optional goals separately. Specify owner fields, timezone/units, required/optional values and server completion. Review derived-write authority as well as cross-user isolation. Do not simply revoke permissions used by SECURITY INVOKER save functions or switch all user requests to a privileged key.

For new endpoints, agree Pydantic request/response schemas, error envelopes, date/source scope, pagination, idempotency and version-conflict behavior. Generate TypeScript types from a reviewed OpenAPI/schema source or enforce equivalent contract checks; avoid maintaining incompatible handwritten definitions in every page. Keep runtime validation where untrusted data crosses boundaries.

Retain `/api/v1` during UI extraction. Add only required HTTP methods to explicit-origin CORS and test preflight when cross-origin. For initial hosting, prefer a same-origin reverse proxy routing the application API to FastAPI; in local development, keep explicit frontend/API origins. Either choice requires correct client configuration. No new public forecast service is needed.

### D. Settle meal/time/source semantics before dashboard design becomes data logic

Implement planned/logged/cancelled state, consumed timestamps and revision behavior before calling daily totals authoritative. Home, Meal log and Nutrition should share one server aggregate, with timezone/DST, source/session and per-nutrient completeness. Catalog records, favorites, copied drafts and portion scenarios are not consumed meals.

Meal edits must not rewrite what an older forecast used. Current forecast provenance does not yet constitute a complete immutable meal/context revision snapshot; saved forecast reads also obtain history from current owned CGM rows. Implement the planned immutable inputs/references before exposing editing, source replacement and historical comparison as stable evidence. Preserve the two-hour 24-point contract and future-outcome exclusion. Keep the current Chronos C3 application model until a separate promotion decision and validation justify a change.

### E. Create the shared shell while implementing one real vertical slice

Build shared tokens, navigation, loading/error states, adaptive dialogs and chart summaries, then complete **sign in -> onboarding -> authenticated Home shell** with persistence and two-user isolation. This is a coherent first slice, not a collection of disconnected mock screens.

Next extract the working path: **food selection -> portion/source review -> meal save -> forecast -> persisted result/history**. Add daily log and shared nutrition aggregation. Verify representative mobile/tablet/desktop layouts and keyboard behavior throughout, then expand to the full acceptance matrix. Keep the old demonstrable workflow available until replacements pass.

Catalog recipe/product search/detail and favorites follow the corrected-release gate. Reviewed synthetic data can support UI development, clearly labeled; it cannot establish real catalog/provider acceptance. Nonclinical notifications require actual owned events. Portion comparison, actual follow-up and deferred integrations keep their existing scientific/privacy conditions.

## 6. Preparation required before public hosting

These are deployment gates, not reasons to prohibit local feature development:

- Add pinned Linux web/API containers and Compose/reverse-proxy configuration. Choose a documented Next.js build/start mode; `standalone` is an option, not a current feature or universal requirement. Make simulator and browser-test interpreter launches portable. Install the isolated simulator from its reviewed pin, rather than copying a Windows virtual environment.
- Create explicit `.dockerignore`/COPY allowlists. Git exclusions alone do not define the Docker build context. Exclude secret files, local databases, private datasets, virtual environments, caches, Graphify and experimental artifacts; mount model/replay caches deliberately. Keep research **code** needed by the runtime separate from data/experiments. [Docker build-context guidance](https://docs.docker.com/build/concepts/context/#dockerignore-files).
- Standardize public versus server configuration, exact origins and Auth redirects. The existing browser uses `NEXT_PUBLIC_*` values. Those are inlined at build time, so changing a container's environment later will not automatically change them. Decide environment-specific builds or an intentional runtime-config design; never put private secrets in public variables/build arguments. [Next.js self-hosting guidance](https://nextjs.org/docs/app/guides/self-hosting).
- Begin with the selected VPS and managed Supabase topology from ADR 0016. Use one API/model worker initially, bounded simulator execution, readiness for actual model/simulator availability, persistent caches and clear busy/retry behavior. Additional worker processes can load additional model copies; process-local locks do not become distributed locks. [FastAPI deployment concepts](https://fastapi.tiangolo.com/deployment/concepts/).
- Measure cold/warm and concurrent latency, whole-stack memory, CPU, provider quotas, error rates and recovery on the actual host. Define acceptance budgets before interpreting measurements; do not promise a user count from a model smoke test.
- Apply reviewed migrations through one controlled workflow, retain compatible application releases, and test restart and database restore. Keep private API/database ports behind the proxy/network boundary. Complete HTTPS/camera/provider and account/recovery/isolation acceptance with synthetic accounts and accurately labeled data before publication.

## 7. When to extract forecasting, and when to split Git

Consider a separate forecast process/service when measurements show inference competing with ordinary API latency, a GPU/runtime dependency needs a different host, independent model restarts are needed, or additional authorized applications consume the same stable capability. A background worker/job contract may be more appropriate than a synchronous network hop for long-running work. Neither choice requires a new Git repo.

Extraction requires a bounded request/result or job contract, immutable model/input identity, private caller authentication, explicit ownership responsibility, deadlines, retry/idempotency, cancellation where supported, queue limits, readiness and redacted observability. Decide which component reads private context and persists results; do not give a new inference worker unrestricted database access by default. Keep `ForecastTarget` and future outcomes out of inference transport. Test local-adapter versus remote-adapter parity before switching traffic, with a compatible rollback path.

Only then evaluate an independent forecast repository/package if there is a real owning team, restricted source access, reusable external consumers or an independent release lifecycle. Publish and pin its artifact/API versions with compatibility tests. The same reasoning applies to splitting the frontend. Independent hosting or different languages alone are insufficient evidence that three Git repositories would help this project.

## 8. Immediate action order and exit criteria

| Order | Work | Exit evidence |
|---|---|---|
| 0 | Review baseline, verify toolchain, run relevant existing checks, wire CI | Reproducible normal-shell commands and passing PR checks; no scientific/live-provider work hidden in routine CI |
| 1 | Freeze Auth/session and first migration/API contracts; build responsive shell alongside them | Reviewed schemas, synthetic two-owner/RLS tests and keyboard/deep-link shell checks |
| 2 | Complete permanent Auth, minimal onboarding and Home shell | Confirmation/recovery/refresh/logout/resume/skip work; no previous-user cache bleed |
| 3 | Extract meal/forecast workflow and implement consumed-day aggregation | Persisted reviewed meal-to-forecast flow; Home/Log/Nutrition agree across timezones, missingness and edits |
| 4 | Add validated catalog/detail/favorites and owned notifications | Corrected catalog release/provider evidence and clear unavailable states |
| 5 | Finish original scenario/follow-up features and hosted readiness | No future leakage, immutable inputs, portable deployment and recovery/camera/provider evidence |

Packaging work can begin early in parallel; do not leave the first Linux run until release day. This ordering refines the existing implementation phases without changing course deadlines or claiming that every planned page fits the remaining course window.

## 9. Verification and limits of this review

Read-only source/manifest/configuration review and official documentation checks were performed. Graphify reported ACTIVE and was used for cross-file navigation; source verified important claims. Its documentation semantic index has not been refreshed for the recent UI documents, so those were inspected directly.

No application/model/database/provider/browser suites, cloud changes, Auth emails or load tests were run. Findings distinguish static evidence from recommended implementation and future performance measurements. No Git repository was created or split. Existing runtime code, scientific results and model choice are unchanged. See the [handoff](../tooling/repository-strategy-readiness-handoff-2026-11-10.md) for scope and documentation checks.
