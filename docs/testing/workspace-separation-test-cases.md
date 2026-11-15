# Workspace separation acceptance catalog

**Planning date:** November 14, 2026. **44 designed cases; 28 PASS, 16 PARTIAL in the actual ledger.** [Plan 19](../planning/GlycoLens_19_Personal_and_Simulation_Workspaces.md), [ADR 0023](../decisions/0023-personal-and-simulation-workspaces.md), [actual results ledger](workspace-separation-results.json).

This catalog is backed by pytest, frontend unit, Playwright and guarded cloud/integration runners. Actual observations and incomplete variants are recorded per case; a designed expectation is not itself a pass. Record expected/observed outcome, exact build/schema, environment, command and sanitized evidence for each execution. Historical tests do not pass these new cases automatically. PARTIAL/BLOCKED/FAIL remain distinct from PASS.

## Fixtures and implementation targets

Use tagged disposable owners A/B; personal planned/eaten/cancelled meals with known/null nutrients; two owned short/long virtual sources with overlapping virtual dates; a known legacy simulated record and an unclassified null-source record. Keep no real account/meal names or private health data in evidence. Freeze the wall clock for deterministic tests; a real browser smoke must also observe actual current local time.

| Target | Implementation area |
|---|---|
| TIME | Shared backend/frontend clock/local-day utilities; profile timezone handling |
| DB | Forward migrations, owner/source constraints, trusted RPCs and aggregate |
| API | `backend/app/api/{meals,nutrition,account,forecasts,simulation,notifications,privacy}.py` and affected inference/simulation services |
| APP | `NutritionDashboard`, `MealHistory`, `MealComposer`, `OnboardingWizard`, `AccountSettings`, ordinary route layouts |
| SIM | `/demo` layout/routes, `MealWorkflow`, session/history/detail navigation |
| STATE | `AccountProvider`, `use-resource`, `MealDrafts`, identity/workspace/request lifecycle |
| MODEL | Inference registry/builders, scenarios/actuals/retrieval and immutable snapshots |
| RUN | Existing CPU Compose runtime, managed cloud dev, Chrome and release evidence |

## W0 — contracts and baseline

| ID | Risk / scenario | Layer / target | Expected result and evidence |
|---|---|---|---|
| WS-W0-001 | Clock contract with frozen now and independent virtual clock | Unit / TIME | Personal now changes only with wall clock; simulation time changes only with selected source/advance; UTC round-trip exact. |
| WS-W0-002 | Normal and simulation API/route scope schemas | Contract / API | Invalid/missing mutation scope rejected before writes; personal reads cannot implicitly select latest virtual source. |
| WS-W0-003 | Synthetic migration baseline manifest | Integration / DB | Count, IDs, timestamp/revision/forecast/receipt digests captured for tagged fixtures only; unknown legacy classification represented. |
| WS-W0-004 | Reproduce current coupling before fixes | Regression / API+STATE | Tests expose preference-changing run, hidden old-session history and virtual personal default day; record failing baseline then passing corrected run. |

## W1 — classification and preservation

| ID | Risk / scenario | Layer / target | Expected result and evidence |
|---|---|---|---|
| WS-W1-001 | Forward migration on guarded dev target | Cloud / DB | Exact target/version reviewed; migration succeeds once and is recorded; unrelated owners untouched. Scratch replay stays separately deferred. |
| WS-W1-002 | Known simulated and uncertain null-source legacy rows | Cloud / DB | Known rows become simulation; uncertain rows remain labeled legacy, excluded from personal totals and available for review. |
| WS-W1-003 | Preserve old evidence | Cloud / DB | IDs, instants, nutrients, revisions, immutable forecast JSON and existing receipt request/result digests match baseline. |
| WS-W1-004 | Invalid workspace/source combinations | Cloud / DB | Personal+virtual source, simulation without source, foreign owner's source and edit reparenting rejected atomically. |
| WS-W1-005 | RLS, grants and direct Data API bypass attempts | Security / DB | A cannot read/write B; exposed grants remain least privilege, no callable privileged RPC escalation; direct writes cannot bypass consistency. |
| WS-W1-006 | New source creation and replay | Cloud / DB | Creates owned source/data without changing global app selection, personal records or another tab's context. |
| WS-W1-007 | Scoped nutrition aggregate with null facts and state changes | Cloud / DB | Exact known totals; unknown remains unknown; planned/cancelled excluded; edit/log/cancel revises correct scope only. |
| WS-W1-008 | Migration transaction failure and recovery | Cloud synthetic / DB | Controlled synthetic failure leaves no partial classification; forward correction preserves data. No hosted reset or broad cleanup. |

## W2 — explicit backend context

| ID | Risk / scenario | Layer / target | Expected result and evidence |
|---|---|---|---|
| WS-W2-001 | Personal meal lifecycle with no source | API+cloud / API | Save planned, confirm eaten, edit and cancel work; personal history and three shared totals agree, without starting simulation. |
| WS-W2-002 | Short/long source saves with explicit scope | API+cloud / API | Each meal retains its selected owned source regardless of global prefs or another concurrent run. |
| WS-W2-003 | Old mutation client omits scope | Contract / API | Stable actionable validation error; zero rows/revisions/receipts created, no hidden classification as personal. |
| WS-W2-004 | Retry, stale revision and cross-scope key reuse | API+cloud / DB | Exact retry one result; key reused with another scope/body conflicts; stale edit conflicts, no duplicate meals. Historical receipts remain interpretable. |
| WS-W2-005 | Session and meal/forecast history pagination | API+cloud / API | All A's simulated sessions discoverable across pages; optional filters correct; no personal/B rows; overlapping virtual dates labeled by source. |
| WS-W2-006 | Timeline, clock advance and forged source IDs | Security / API | Explicit owned simulation source required; personal/B-source access denied; no global fallback or advancing unrelated sessions. |
| WS-W2-007 | Personal forecast without real glucose | Contract / API+MODEL | Clear unavailable/eligibility response; no simulated history, forecast or private model input silently attached. |
| WS-W2-008 | Forecast/scenario/actual/retrieval scope mismatch | API+cloud / MODEL | Wrong owner/source/workspace denied; one frozen origin/context/model retained; future values excluded from predictors and retrieval. |
| WS-W2-009 | Notification and historical detail links | API+cloud / API | Link resolves true workspace/record/source; old links remain owned/readable, never presented as personal consumption. |
| WS-W2-010 | Export and immediate account deletion | Cloud disposable user / API | Export labels both workspaces/legacy and retains original provenance; password+confirmation deletion removes all owned rows/files, B unchanged. |

## W3 — personal app and current time

| ID | Risk / scenario | Layer / target | Expected result and evidence |
|---|---|---|---|
| WS-W3-001 | Personal Home/Nutrition without source | Component+browser / APP | Current profile-local day shown, useful empty totals and meal action; no simulated reading/run/replay/advance controls. |
| WS-W3-002 | Create, eat, edit and copy timestamps | Unit+browser / APP | New uses now; eaten explicit; edit preserves chosen historical instant; copy is new planned draft with current time and new key. |
| WS-W3-003 | UTC+14, UTC-10 and midnight windows | Unit/property / TIME | Same UTC instant groups into correct local day; half-open boundaries have no omission/double counting. |
| WS-W3-004 | DST spring/fall | Unit / TIME | Real 23h/25h local days and repeated-hour instants handled; no assumed 24h day or timestamp rewrite. |
| WS-W3-005 | Midnight, background resume and profile timezone change | Component+browser / TIME+STATE | Default today refreshes correctly; explicit history date remains labeled history; stored timestamps untouched. |
| WS-W3-006 | New-user onboarding and settings | Browser / APP | Timezone can be confirmed/corrected; ordinary personal use requires no simulation choice or CGM, existing onboarding resumes safely. |
| WS-W3-007 | Planned versus eaten discoverability | Browser / APP | Saved planned meal immediately visible in history; only confirmed eaten contributes to daily totals; state/selected-day explanation clear. |
| WS-W3-008 | Network error/loading and logout/account change | Component+browser / STATE | No old owner's/simulation data flashed; failed request offers retry; private state clears on logout and identity switch. |

## W4 — simulation isolation and navigation

| ID | Risk / scenario | Layer / target | Expected result and evidence |
|---|---|---|---|
| WS-W4-001 | Both protocols run and replay | API+browser / SIM | Distinct owned sources, visible virtual banner/session/clock; deterministic epoch and protocol checksum unchanged. |
| WS-W4-002 | Exit, browser Back, refresh, bookmark and normal deep link | Browser / SIM+STATE | Ordinary routes always use personal now/timezone/data; no exit-server-write dependency; Auth retained. |
| WS-W4-003 | Two tabs, one reruns/advances simulation | Browser / STATE | Personal tab unchanged; explicit source in simulation tab stays consistent; no account-global selection mutation. |
| WS-W4-004 | Slow response arrives after exit or source switch | Browser controlled network / STATE | Aborted/obsolete response cannot repopulate wrong workspace, draft, day or timeline. |
| WS-W4-005 | New simulation and earlier saved history | Browser / SIM | Earlier planned/eaten meals/forecasts remain discoverable via all-session history; selected-session totals exclude other sessions. |
| WS-W4-006 | Legacy detail URL and scope-aware links | Browser / SIM+APP | Owned simulated bookmark opens visibly simulated context and correct origin; forbidden IDs expose no details. |
| WS-W4-007 | Unsaved personal and simulation drafts | Browser / STATE | Keys isolated by owner/workspace/source; enter/exit doesn't overwrite personal draft; unsaved-change choice preserves intended draft. |
| WS-W4-008 | Chronos and eligible native LightGBM regression | Real synthetic inference / MODEL | Existing 24-point outputs ordered, frozen inputs/provenance intact; LightGBM requires 288 pre-origin samples; no synthetic history in personal results. Sensitivity is not accuracy. |
| WS-W4-009 | Anonymous demo session behavior | Auth fixture+cloud where enabled / SIM | Demo remains gated by existing verified session policy; exit reaches ordinary account/onboarding gate without implicit upgrade/logout or data transfer. |

## W5 — combined acceptance and rollout

| ID | Risk / scenario | Layer / target | Expected result and evidence |
|---|---|---|---|
| WS-W5-001 | One-command Compose/cloud integration | Live synthetic / RUN | Exact schema/API/UI versions healthy; personal log then short/long demo then exit work against dedicated cloud dev; no local Supabase needed. |
| WS-W5-002 | Responsive layout and accessibility | Automated viewport + manual Chrome / RUN | 320/390/768/1024/1440/1920 widths, keyboard, focus and 200% zoom keep dates, exit, history controls and graph table usable. Human evidence separate from fixtures. |
| WS-W5-003 | Seeded history, pagination and concurrency | Integration measurement / RUN | Bounded queries/pages and representative seeded row counts recorded; existing runtime limits met, no duplicate/drop/leak under concurrent save/source creation. |
| WS-W5-004 | Controlled transition and recovery | Integration / DB+RUN | Ambiguous old writes blocked during rollout; compatible historic reads available; failure pauses new writes without data rollback or global-context regression. |
| WS-W5-005 | Evidence and human acceptance | Review / RUN | Exact commands/build/schema and sanitized observed results recorded; docs/ADR/UI agree, Graphify current; pending manual/scratch/camera/accuracy gates not marked passed. |

## Exit rules

Migration/ownership/data-loss, synthetic-to-personal mixing, wrong-current-day and stale-response defects block completion. A passing component fixture cannot satisfy real cloud/model/manual layers. Existing credentials/artifacts suffice; no paid parsing/provider calls or consumed-cohort experiments are required for this catalog. Physical camera and independent scratch replay are outside this scope under the prior decisions. The optional explicit cross-workspace copy convenience is deferred; core UI must not offer an untested automatic transfer.
