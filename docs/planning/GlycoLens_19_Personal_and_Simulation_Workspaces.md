# Personal application and virtual simulation separation

**Date:** November 14, 2026. **Status:** engineering implemented; cloud-dev migration `20261114173109` applied and local web/API updated. Combined acceptance remains partial; see [actual validation](../reports/workspace-separation-validation-2026-11-14.md). [ADR 0023](../decisions/0023-personal-and-simulation-workspaces.md) records the decision. This supplements plans 17/18 without declaring Milestone 2 complete.

## 1. Required outcome

The ordinary application uses the real current date/time in the account's confirmed IANA timezone. Virtual-patient runs, replay, meals and forecasts belong to an explicitly separate simulation workspace. Leaving `/demo` for any ordinary app route restores the ordinary clock and personal data immediately. A separate workspace is **not a separate Supabase Auth session or account**.

| Concern | Personal application | Simulation workspace |
|---|---|---|
| Routes | `/home`, `/meals`, `/nutrition`, ordinary account routes | `/demo` and clearly nested simulation history/detail routes |
| Clock | Current UTC instant displayed in profile IANA timezone | Selected owned source's virtual clock, visibly labeled |
| Daily totals | Personal meals explicitly confirmed eaten on that local day | Eaten simulated meals in the selected source/local virtual day |
| Glucose | Honest unconnected state until an approved real-data connector exists | Selected virtual-patient readings |
| Forecast | Unavailable without an eligible real source; no synthetic fallback | Existing Chronos/default and eligible opt-in LightGBM research paths |
| Changing simulation | No effect on personal meals, clock or totals | Creates/selects an owned source; earlier sessions stay discoverable |
| Identity, food facts and preferences | Shared account, provider facts, units and timezone | Same account and shared facts; separate drafts, context and records |

“Current/live” means the real calendar and wall clock here. This work does not invent a live CGM feed or validate forecasts on a person. Keep the deterministic January 2026 epoch inside simulation; do not move old glucose or forecasts onto today's dates.

## 2. Pre-implementation findings (corrected by this delivery)

| Finding | Source and consequence |
|---|---|
| A run/replay selects an account-global source | `app_store_source_context` in migration `20261111084803_source_context_and_forecast_snapshots.sql` updates `user_preferences.source_session_id`. Both app and demo then depend on that pointer. A separate browser tab can change it. |
| New meals inherit this hidden pointer | `app_commit_meal` in migration `20261111084347_meal_lifecycle.sql` chooses the preference source; edit retains the meal's original source. No explicit workspace is in the write contract. |
| Meal history hides earlier sources | `backend/app/api/meals.py` defaults list/timeline to that global source. “All meal history” therefore does not mean all owned saved meals. An empty current session does not establish deletion. |
| Personal nutrition depends on simulation | `backend/app/api/nutrition.py` requires a source and derives default day from its clock. `consumed_nutrition_window` requires an owned non-null source; personal logging without simulation cannot use this aggregate. |
| Fixed epoch is intentional simulator code | `backend/app/services/simulation/live.py` uses January 1, 2026 for creation and advancement. Replacing just one date would misalign history, future observations and frozen forecast origins. |
| Frontend also imports the virtual clock | `MealComposer.tsx` initializes time from `/nutrition` source; `NutritionDashboard.tsx` exposes run/replay/advance in ordinary Home. Copy initialization also retains the old recorded time. |
| Remounts and requests lack a workspace contract | `AccountProvider.tsx` keys app content by global source; `use-resource.ts` dependencies do not encode identity/workspace/timezone. Demo source changes can leave stale app state or disturb unrelated drafts. |
| Save and eat are distinct | Demo save defaults to planned; only logged meals with consumed time count toward eaten totals. Separation must preserve this distinction. |

Current owner/RLS checks and immutable meal/forecast snapshots are useful foundations. A label-only fix, changing the date, or removing a list filter alone would leave hidden writes, aggregate coupling and cross-tab interference unresolved. Existing simulation records must stay synthetic even if the user actually ate similarly named food.

## 3. Target contracts

### Data classification and migration

- Add an explicit server-validated meal origin/workspace: `personal`, `simulation`, and, where provenance is insufficient, `legacy_unclassified`. Use a constrained field rather than inferring personal consumption from a null source alone.
- Personal meals have no virtual source. Simulation meals require a source owned by the same account. Derive child context from the immutable parent and validate owner/source foreign keys; avoid independent child flags that can disagree.
- Classify existing rows attached to known simulation/replay sources as simulation. Preserve uncertain legacy rows in a labeled read-only legacy history until reviewed. Never automatically count them in personal totals or delete them.
- Preserve IDs, revisions, nutrients, recorded/consumed timestamps, frozen inputs/results, forecast calibration and historical idempotency receipts. Do not relabel old forecast snapshot JSON as personal or rewrite past revisions. Resolve legacy scope from the owning record for old reads.
- Stop source creation from updating the global app source pointer. Deprecate that pointer as request authority; do not remove old fields until the new readers/writers and deployment transition are verified.
- Use one reviewed forward migration in dedicated cloud development, with count/invariant checks before/after. No reset or broad cleanup. Fresh scratch replay remains deferred under the existing user decision.

### API and authorization

- Ordinary `/home`, `/nutrition` and `/meals` explicitly mean personal data and must function with no virtual source. Introduce an explicit scope contract for shared internal queries; simulation reads/writes require `workspace=simulation` and a verified owned `source_session_id` where a single source is required.
- New and edited meal writes carry a validated workspace; simulation writes also carry the source. Never silently derive it from account preferences. Reject missing/ambiguous scope in old mutation clients with a stable upgrade-required validation error before any write.
- Scope is a data partition, not an authorization credential: verified identity, ownership and RLS remain mandatory. Trusted RPCs derive owner from the verified backend session, check parent/source consistency, and retain least-privilege grants.
- Bind idempotency to workspace/source and full request body. Identical retries return the same result; reusing a key for another context conflicts. Edits cannot move a record between workspaces/sources. Explicit copies receive new IDs and keys.
- Refactor consumed-nutrition aggregation for owner + workspace + optional simulation source + local-day window. Keep shared logic for Home/Meal log/Nutrition, planned/cancelled exclusion, null nutrient facts, revisions and DST. Never aggregate overlapping simulation sessions into one day by default.
- Add paginated owned simulation-session history and all-session simulated meal/forecast history with explicit source labels and filters. A single-session timeline, clock advance, forecast or retrieval always has one explicit source; details retain the record's original source regardless of selected workspace.
- Forecast execution uses the immutable meal/source/model contract. Personal meals currently fail eligibility with a useful unconnected-source explanation. Never borrow the most recently used simulator context.
- Notifications and deep links carry/resolve record scope. Exports retain both workspaces with provenance; account deletion still removes all owned workspaces and private files under the existing confirmation policy.

### Clock, routes and client lifecycle

- Store instants in UTC. Centralize IANA local-day boundaries and formatting; continue using confirmed profile timezone. Browser timezone can suggest a first-use value, with explicit user correction in onboarding/settings. A timezone change affects display/day grouping, not stored timestamps.
- Personal default day comes from a trusted current instant converted to profile timezone. Update visible clock and default-today views at local midnight, tab focus and timezone change. Explicit history-date selections remain history, clearly labeled. A simulation date must never seed the personal date picker.
- A new personal meal starts at the current instant. Eaten requires explicit confirmation and a real consumed timestamp; saved planned meals appear in personal history without inflating totals. Editing a meal preserves its intended historical time. Copying creates a planned draft with a new current timestamp unless the user deliberately chooses another.
- Keep `/demo` as the canonical virtual entry. Add simulation navigation/history/detail routes under it, a persistent “Virtual simulation” banner, selected protocol/session/virtual clock, and an explicit “Exit simulation” action. Move simulator start/replay/advance and research model selectors out of personal Home into this workspace.
- Ordinary app routes always resolve personal context, even when reached through browser Back, a bookmark, refresh or another tab. Exit is navigation/context cleanup, not logout, record deletion or a required server preference mutation. Anonymous demo users return through the existing account gate; do not silently upgrade or sign them out.
- Keep tab-local simulation selection; a new run in one tab cannot switch another tab's personal context. Scope caches/drafts by owner + workspace + source where applicable + date/timezone. Cancel/discard stale requests on context change. Preserve personal drafts when entering/leaving simulation and clear private state on logout/account switch.
- Existing owned simulation detail URLs in ordinary routes must resolve their true origin and route to or visibly open the simulation workspace. Never display an old simulated record under a personal heading. Saved notification/bookmark links remain useful.
- A deliberate cross-workspace copy may reuse reviewed food facts, but must be labeled and re-reviewed with current personal timing; it must not copy glucose/forecast outcomes or mark a simulated meal eaten automatically. This optional convenience is not needed for the core separation gate.

## 4. Ordered implementation and validation

| Phase | Changes and affected areas | Exit evidence |
|---|---|---|
| W0 — freeze contracts and baseline | Synthetic fixtures for personal/no-source, two old/new simulation protocols, planned/eaten, two owners, timezone edges; route/API schemas and clock helpers. Capture redacted invariant counts and current behavior. | W0 cases; reproducible failing boundary tests before behavioral fixes. |
| W1 — preserve and classify data | Forward migration, constrained origins/ownership, reviewed legacy classification, scoped aggregate/trusted RPC support. Retain old reads and receipts. | W1 cases against guarded dedicated cloud dev synthetic rows; denied writes, unchanged snapshots/counts and atomic failure. |
| W2 — explicit backend context | Meal/timeline/nutrition/home/forecast/scenario/actual/retrieval APIs, session history, scope-aware notifications/export/deletion, stable mutation errors. No global source selection side effect. | W2 API/RPC/ownership/idempotency tests; personal-no-source and old-session histories demonstrated. |
| W3 — ordinary app clock and meals | Home/Nutrition/MealHistory/Composer, onboarding/settings, shared formatting, personal empty glucose state, current-day rollover and isolated drafts/cache. | W3 component/time tests and personal save/edit/eat/cancel journey with no simulator. |
| W4 — isolated simulation UX | Demo layout/navigation, owned session picker/history/details, explicit source transport, exit/back/deep links, stale request and cross-tab protection, existing selector/advance/replay flow. | W4 browser tests showing preserved personal state and earlier simulation records; real synthetic model regression. |
| W5 — acceptance and rollout | Compose web/API + cloud smoke, all affected regressions, Chrome responsive/keyboard/zoom review, exact build/migration/test evidence, docs/Graphify refresh. | W5 cases and result ledger; no planned/fixture-only test recorded as a manual/live pass. |

W1 precedes writes using new scope; W2 precedes W3/W4 integration. Deploy compatible schema/API/UI together behind a controlled transition. Stop old ambiguous writes during rollout; do not run mixed clients against a silently changed default. Work remains in the same repo/Compose runtime and uses existing private prerequisites.

### Acceptance tests and results

[44 designed cases](../testing/workspace-separation-test-cases.md) define inputs, expected outcomes, layer and implementation target. [Result ledger](../testing/workspace-separation-results.json) now records **28 PASS and 16 PARTIAL** with actual observations. Existing Plan 17/18 test results are historical evidence, not proof that this new boundary works. No new model training, test-cohort access or paid LLM call is required.

Critical completion criteria:

1. Log and find a personal meal today with no simulation prepared; eaten totals match all three ordinary pages.
2. Run/replay short and long simulations; older saved simulation meals/forecasts remain reachable, never added to personal totals.
3. Exit/back/refresh/two tabs show current personal date/time in the configured timezone; in-flight simulation responses cannot overwrite it.
4. Both existing models still use only their own frozen pre-origin context; old forecast values and calibration are unchanged.
5. Ownership, retry, export and immediate deletion work across both spaces; no data is reclassified from guesswork.

## 5. Rollout, rollback and risks

The largest risks are silently reclassifying old data, reusing a receipt in another workspace, hidden global-pointer callers, and async UI responses arriving after exit. Treat these as release-blocking correctness issues, with explicit tests rather than visual-only review.

Add indexes for owner/workspace/time and owner/source/time only as justified by actual queries; keep bounded pagination. No extra service or external API call is needed. Performance/latency claims require measurement, including a representative seeded history; the main correctness improvement is explicit context rather than duplicated components.

If validation fails, stop new scoped writes and leave preserved legacy/simulation reads available while correcting forward. Do not roll back by reclassifying rows, dropping history, or restoring the old global-pointer behavior after personal writes exist. Verify a tagged synthetic export/count/snapshot manifest and record the exact schema/API/frontend version together. This is not a backup-restore acceptance substitute.

## 6. Prerequisites, decisions and documentation impact

No new credentials, SMTP, domain, paid model budget or dataset are needed for this scope. Reuse existing dedicated cloud-dev access, ignored configuration and model artifacts with exact target guards. Actual Chrome review remains a human acceptance task; physical-camera and separate scratch replay remain deferred. A genuine real-CGM connector is a separate future decision, not a dependency for personal meal logging.

Reviewed and updated: plans **00/01** (current direction/navigation), **03** (flows), **04** (schema/API/context), **06** (ordered delivery), **08** (synthetic/personal boundary), **09** (deliverable meaning), **10/17/18** (supplemental scope and unchanged acceptance), responsive UI architecture, root README and AGENTS memory. New ADR/catalog/ledger accompany this plan. Model/dataset/scientific plans **02/05/07/11–16** are unaffected: model inputs, research hypotheses, splits, calibration and reported results do not change.

Implementation now switches ordinary app clocks/data independently and exposes simulation history. W0–W4 engineering is delivered; W5 and incomplete case variants remain partial as qualified in the actual ledger. Do not equate engineering delivery with full Milestone 2 or release acceptance.
