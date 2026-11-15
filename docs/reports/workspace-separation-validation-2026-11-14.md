# Personal application and simulation separation validation

**Date:** November 14, 2026. **Disposition:** Plan 19 engineering implemented locally, approved cloud-development migration applied, automated/API/model/browser evidence recorded. Combined acceptance remains partial where the [44-case ledger](../testing/workspace-separation-results.json) records missing variants/manual review. This is not Milestone 2 or public-release sign-off. Changes are uncommitted; no GitHub push or hosted deployment.

## Resulting behavior

- Ordinary `/home`, `/meals`, `/nutrition` and personal settings use real current/profile-local dates and personal records. Meal logging and consumed nutrition work without preparing a virtual source. Only explicitly eaten personal meals count; unknown nutrients remain unknown.
- `/demo` is the separate virtual workspace, with a banner, Exit simulation, saved sessions, all-session simulated meal/forecast history and labeled legacy history. It keeps the deterministic January 2026 epoch. New runs/replays no longer select account-global application context.
- Existing known virtual meals retain IDs, timestamps, revisions and source relationships; they appear in Simulation meals rather than being relabeled as current personal consumption. Uncertain legacy rows remain read-only and excluded from personal totals.
- New trusted meal writes require explicit personal/simulation scope and an owned virtual source where applicable. Edits cannot reparent records. Scope participates in retry identity. Personal forecast requests cannot borrow simulator glucose.
- Both existing model paths remain in simulation: default Chronos and explicit eligible native LightGBM. Their model inputs, source chronology, calibration, research limitations and frozen results remain unchanged. No new accuracy claim, training, cohort use or paid parsing call.
- Exit/back/refresh and other tabs retain the personal boundary. Exit invalidates pending simulation selection. Requests are identity/workspace/timezone scoped; drafts are owner/workspace/source scoped, held in memory, with separate eviction boundaries and unload warnings. Logout clears both workspaces' private client state.
- Historical owned detail links resolve their true workspace. Notification links distinguish personal/virtual records; exports version 1.1 retain both origins. Immediate password-confirmed account deletion still covers both spaces and private source-file cleanup.
- Profile/settings no longer present a global source selector as the ordinary app's active source. New accounts can start personal logging; historical preference fields remain for compatibility and are not request authority.

## Migration and transition

Applied [20261114173109_personal_simulation_workspaces.sql](../../supabase/migrations/20261114173109_personal_simulation_workspaces.sql) to the already approved dedicated managed cloud development project. A transaction dry run first completed and rolled back. The apply used the Supabase MCP migration operation; the repository filename matches the recorded cloud version.

The migration adds a constrained meal workspace, classifies known virtual sources, preserves uncertain origin, adds scoped indexes/aggregate, and replaces the trusted meal/source functions. It contains a transactional before/after fingerprint assertion for **all original meal fields except the new workspace column**. No recorded/consumed timestamp, nutrient, revision or existing frozen result is intentionally rewritten. Old snapshot JSON and receipt rows are retained.

The old local web/API services were stopped during the schema transition; compatible images were then started. Missing-scope writes fail closed rather than silently creating personal meals. No database reset, broad cleanup, local Supabase replacement or new service was used. Post-apply checks verified the exact migration, zero personal rows carrying virtual sources, browser write-RPC execution denied, scoped aggregate execution allowed, and an empty private-artifact cleanup queue at the observed checkpoint.

This is not independent scratch replay/restore proof. The user's earlier scratch deferral remains in effect. A deliberate failed-migration/deployment rehearsal and ambiguous legacy fixture coverage remain partial in the ledger.

## Observed validation

| Layer | Expected | Observed |
|---|---|---|
| Red baseline | Expose old hidden context and absent personal clock contract | Focused initial suite: 5 expected failures, 3 passes before behavioral changes; corrected suite now passes |
| Backend | Explicit scope, no-source personal nutrition, lifecycle and unchanged model-context guards | **129 tests passed**; final Python lint passed on affected API/workspace/integration code |
| Frontend | Timezone/day rollover, reviewed drafts, models and typed routes | **36 unit tests passed**; lint, type generation/check and production build passed |
| Affected browser fixtures | Desktop/mobile exit/back/reload, previous history, two tabs, stale response, drafts and fail-closed mixed-response handling | **32 distinct affected cases passed across targeted runs**; 29 passed in the broad run, its development-overlay-intercepted mobile case passed after the E2E-only indicator fix, scoped-guard regressions passed, and two new negative cases passed |
| Shell/onboarding fixtures | Navigation, dialog focus, resumed onboarding and protected routes | **6 desktop/mobile cases passed** |
| Real local-browser/cloud journey | Genuine password login, current New York day, personal meal visible, real long-protocol cached replay, earlier virtual meal discoverable, exit restores personal day, logout | **1 passed (12.1 seconds)** against local production web/API and cloud Auth/database; no browser route fulfilled mock responses. One tagged disposable account; credentials stayed in an ignored fixture and were removed during scoped cleanup |
| Real model/API/cloud journey | Short and long live protocols, independently saved personal/virtual meals, both native CPU model paths, exported immutable results | Both models returned **24 persisted forecast points** from their selected virtual sources. Long protocol exposed 288 past samples. Personal forecast rejected with 422; cross-workspace request-key reuse rejected with 409 |
| Real replay isolation | Both cached protocols, unchanged personal preferences, owned timelines and foreign-owner advance denial | Both replays passed; exact preference object unchanged; foreign-owner timeline/advance denied; deletion reported source-file cleanup complete |
| Real permission/lifecycle/privacy follow-up | Invalid workspace/source pairs, reparenting, browser bypass, planned/eaten/cancelled totals, links/export/deletion and unrelated owner preservation | Passed using tagged synthetic owners. 180 kcal known-food oracle matched; unknown fiber stayed null; cancellation removed consumed totals; other-owner sentinel survived deletion; deleted owner lost API access |
| Real aggregate/concurrency | Complete totals across pages, DST and missing facts, bounded duplicate/concurrent behavior | 30 eaten rows totaled 3000 kcal/300 g carbs despite 20-card pagination; planned/cancelled 999-kcal sentinels excluded; 25-hour New York day and UTC regrouping matched; 12 concurrent scenario saves produced exactly 10 rows and two 429 denials |
| Local Compose | One-command runtime, healthy final web/API | Reviewed CPU images rebuilt; web/API readiness healthy. Real UI/API tests used the same cloud target. Final compatible settings/draft/timeline refinements also passed offline/fixture checks and were rebuilt locally |

Model inference, replay, lifecycle and aggregate runs used exact target guards, generated run identifiers, tagged disposable users/foods and scoped cleanup. Each harness stayed within its configured request cap or conservative API reservation; no emails, external nutrition calls, paid LLM calls, research datasets or new model downloads were required. Normal real-user passwords/accounts were not inspected or changed.

## Evidence and corrections

Public traceability: [Plan 19](../planning/GlycoLens_19_Personal_and_Simulation_Workspaces.md), [ADR 0023](../decisions/0023-personal-and-simulation-workspaces.md), [catalog](../testing/workspace-separation-test-cases.md), [actual case ledger](../testing/workspace-separation-results.json), and [source manifest](workspace-separation-manifest-2026-11-14.json). Exact local commands and redacted stage results remain in ignored `.cache/release-checkpoint/workspace-*` logs/JSON; synthetic screenshots are `.cache/workspace-live-personal.png` and `.cache/workspace-live-simulation.png`. These are not production user captures.

Preserved failed attempts are not erased or counted as passes: the first full HTTP harness completed both model/export assertions, then used the wrong deletion response field (`status` instead of existing `deleted`). A focused follow-up validated the actual deletion/export contract. Another negative oracle initially expected 400 instead of the trusted API's documented 422 for a foreign source; corrected follow-up passed. The older aggregate concurrency fixture lacked the now-required ordered 24-point forecast; its corrected synthetic fixture passed without changing the database guard or model. Browser setup first pointed at an absent default Chromium path; the existing ignored repository browser installation was selected. Alert/selector locators and a reload-before-navigation test race were corrected to use actual accessible UI and URL readiness.

An actual UI lifecycle edge was fixed as well: exiting now advances a request generation before navigation, so a pending simulation response cannot restore context while exit is in progress. The delayed-response case passed on desktop/mobile. E2E development indicators are disabled only for isolated tests because the Next development overlay covered a mobile navigation target; production navigation was unchanged.

## Remaining acceptance and limits

The ledger deliberately retains PARTIAL results for incomplete variants: full legacy/provenance baseline coverage, failed-migration rehearsal, multi-page session history, complete scenario/actual/retrieval combined acceptance, all copy/time/focus/draft variants, and actual anonymous-cloud policy. Human Chrome keyboard/zoom review, representative performance/resource gates, transition-failure rehearsal and owner sign-off remain open. Chromium viewport tests and agent inspection of synthetic screenshots are not human Chrome/device acceptance. Physical camera and separate scratch restore/replay remain user-deferred.

Live wall-clock dates do not establish a real glucose connection. Personal glucose/forecast states remain honestly unavailable. Prior Chronos meal-response capability failure and LightGBM carbohydrate-only/interval-transfer limitations are unchanged. This work does not close catalog, email delivery, domain/VPS, clinical accuracy or other release prerequisites.

Implementation reuses the existing Supabase access and private configuration. No additional user credential or architecture decision was needed. Updates to plans 00/01/03/04/06/08/09/10/17/18/19, responsive UI architecture, ADR 0023, test navigation and AGENTS document the correction. Scientific/model/data plans remain unchanged because research methods/results did not change. Graphify is refreshed locally after final supported edits, without external semantic API calls.

Current Supabase behavior was checked against the [official changelog](https://supabase.com/changelog.md) and [RLS documentation](https://supabase.com/docs/guides/database/postgres/row-level-security) before implementation; live project/grant checks, rather than documentation alone, support the migration observations above.
