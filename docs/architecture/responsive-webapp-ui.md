# Responsive web application and UI architecture

## November 12 implemented UX follow-up

Sign out is discoverable in the shared header on desktop/tablet/mobile and in the
demo account bar. It reuses Supabase logout; anonymous sessions require confirmation.
The demo subtree is keyed by account identity, so another tab signing out discards
drafts, results and camera state. Private routes retain the AccountGate boundary.
Demo controls are **Run new simulation** and **Replay saved simulation**, with an
explicit fixed-clock/server-replay explanation. See [actual validation](../reports/demo-logout-compose-review-2026-11-12.md).

## Implemented development status

See the [November 11 checkpoint](../reports/webapp-implementation-checkpoint-2026-11-11.md) and [ADR 0019](../decisions/0019-trusted-cloud-writes-and-frozen-source-context.md). The route table distinguishes implemented code from catalog/email/manual/hosted acceptance.

Execution now follows [plan 17](../planning/GlycoLens_17_Webapp_Implementation_Plan.md)
and [ADR 0018](../decisions/0018-cloud-supabase-and-staged-webapp-delivery.md): one
repo, dedicated cloud Supabase development and email/password verification/reset,
with full features delivered in stages. Local prototype results are historical;
cloud schema/configuration are implemented; full acceptance remains open. The plan maps
these routes/components/data contracts to named test and evidence gates.

**Date:** November 11, 2026. **Status:** design contract with an implemented development checkpoint; full release acceptance remains open.

The living [product specification](../planning/GlycoLens_03_App_Product_Spec_and_UX.md) owns product scope. This document defines its route, component, data and responsive contracts. [ADR 0017](../decisions/0017-responsive-webapp-and-figma-reference-boundary.md) records the decision. The [Figma review](../reports/figma-reference-review-2026-11-10.md) separates observed designs from these GlycoLens design choices.

## 1. Baseline and constraints

The browser now uses a public entry, account/Auth routes and protected `(app)` layouts. Permanent development Auth, minimal resumable onboarding, shared shell, reviewed meal routes, immutable forecasts, consumed nutrition and owned activity/export are implemented. Catalog release, email delivery, deletion policy and hosted/manual acceptance remain gated. See ADR 0019 and the implementation report for current evidence; reference designs remain reference-only.

## 2. Navigation and route contract

Use one navigation definition, rendered as bottom navigation on compact screens, a compact rail on tablets and a labeled sidebar on wide screens. Primary destinations, in order: **Home, Search, Meal log, Forecasts, Nutrition**. Account controls expose Favorites, Profile, Settings, Notifications and Help on every size. Add meal is a clear action on Home and Meal log; Scan and Analyze recipe are entry methods, not competing primary destinations. Use visible labels, active states and browser back/deep links.

The reference app varies its navigation between frames. GlycoLens must not reproduce that inconsistency. Route groups below are the Next.js organization and target behavior; names in parentheses are internal groups and do not alter URLs.

| Route | Purpose and required behavior | Current state / delivery order |
|---|---|---|
| `/` | Resolve session and onboarding, then redirect to `/home`; keep a working demo entry during migration | Public entry with sign-in/sign-up/demo links; no forced public redirect |
| `/auth/sign-up`, `/auth/sign-in` | Supabase-managed registration/login; confirmation and neutral errors | Implemented for development; real email gate open |
| `/auth/check-email`, `/auth/callback` | Confirmation/provider redirect and expired-link recovery | Implemented UI/callback; live expired-email cases pending |
| `/auth/forgot-password`, `/auth/reset-password` | Recovery initiation and verified recovery session | Implemented recovery UI; delivery disabled pending SMTP |
| `/onboarding` | Versioned, resumable steps; review and completion | Implemented; real cloud resume/version/CAS evidence |
| `/home` | Glucose/source card, latest forecast, daily eaten-meal nutrition, recent meals, catalog discovery when available | Implemented; cloud aggregate and browser fixture evidence |
| `/search?type=recipes\|products&q=...` | Catalog-first tabs, query, validated filters, sort and pagination | Honest unavailable catalog state; corrected release required |
| `/recipes/[id]` | Ingredients, yield, serving basis, nutrition/source and reviewed meal action | Unavailable-state route; real corrected details pending |
| `/products/[id]` | Barcode/brand/pack, per-100-g and serving facts, ingredients and provenance | Unavailable-state route; real corrected details pending |
| `/meals` | Selected local date, meal slots, daily totals, paginated history | Implemented list; date/slot filtering and full validation ongoing |
| `/meals/new`, `/meals/[id]`, `/meals/[id]/edit` | Shared composer, confirmed record and revision-safe edit/remove | Implemented common composer/revisions/cancel; in-memory scoped drafts |
| `/scan` | Camera barcode capture, permission/error states and manual-code fallback | Implemented shared barcode composer/manual fallback; phone test pending |
| `/recipes/analyze` | Editable text extraction, ingredient resolution, confirmed quantities and totals | Implemented common draft/food-grounding composer; live acceptance pending |
| `/forecasts`, `/forecasts/[id]` | History/detail, source/origin, interval, 30/60/120-minute summaries | Implemented scoped history and frozen detail/chart/table |
| `/forecasts/[id]/compare` | Portion scenarios with shared origin/context; no automatic meal logging | Implemented same detail/comparison surface; bounded requested inference |
| `/nutrition` | Daily totals and seven-day history with missingness/coverage | Implemented shared consumed totals/seven-day table |
| `/favorites` | Saved catalog recipes/products; independent of consumed meals | Unavailable catalog state; typed favorites pending corrected catalog |
| `/profile`, `/settings` | Display name/preferences, account recovery/logout, units/timezone and notification preferences | Implemented preferences/profile/logout; broader lifecycle acceptance partial |
| `/settings/connections` | Active data source, simulator/replay state; Dexcom only when implemented | Implemented honest virtual-source/Dexcom availability |
| `/settings/privacy` | Owned export and immediate password-confirmed account deletion; disclose file cleanup/provider limits | Implemented with explicit confirmation and no recovery window; ADR 0020 |
| `/account-deleted` | Public deletion outcome with explicit pending-file state | Implemented; no private identity in URL |
| `/notifications` | Owned nonclinical events, read/unread, pagination and safe deep links | Implemented trusted events and bounded page mark-read |
| `/help`, `/privacy`, `/terms` | Research limitations, data use, source explanations and support information | Implemented development notices; support/retention finalization pending |
| Not-found/error/loading boundaries | Shared recovery with preserved safe drafts | Implemented route recovery; broader manual journeys pending |

Research operations stay local/restricted. Do not expose an unprotected `/research` page or add an HTTP batch-run endpoint just to populate navigation. Similarly, hide unavailable controls or explain a dependency; do not ship dead links to planned pages.

## 3. Onboarding and account state

Adapt the reference's step indicator, short forms and review/edit pattern. GlycoLens steps are **Account -> App preferences -> Data source -> Optional food preferences/goals -> Review**. A returning completed user goes to Home; an incomplete user resumes the next required step. An expired session returns to login with a validated same-origin return path. Optional steps are skippable and editable later.

| Information | Requirement and use |
|---|---|
| Account email and authentication | Supabase Auth; application tables never store passwords |
| Display name | Optional nickname with a safe default; no legal-name requirement |
| Timezone | Required confirmed IANA zone, initially suggested from browser; local-day aggregation |
| Glucose display unit | Required choice/default confirmation; store canonical mg/dL, convert only for display |
| Data-source mode | Required choice of available virtual/replay source; Dexcom sandbox later; do not offer live CGM as connected |
| Research/education acknowledgement and privacy notice version | Required recorded acknowledgement for this flow; separate from optional delivery consent; does not authorize real-patient research |
| Dietary preferences and ingredients to avoid | Optional, removable preference data; no allergy-safety guarantee |
| Nutrition goal | Optional self-entered target, with unit and effective date; no default 2,000 kcal or calculated weight-loss prescription |
| Date of birth, sex, height, weight, diagnosis, medication, insulin regimen, family/child profiles | Not required for this capstone flow; no current validated product need establishes collection |

Persist a versioned step state and submitted values server-side. Completion is a server-validated transition after required preferences/acknowledgements are saved atomically; a browser boolean cannot bypass it. Store only step/progress metadata in onboarding state, not a duplicate health profile. Separate account identity, user preferences and virtual-patient simulation identity. Switching source cannot mix another source's meals, contexts or outcomes.

Existing anonymous demo access must be deliberately retained or migrated. A permanent-account upgrade must preserve the Auth UUID where Supabase supports the chosen flow; otherwise use a reviewed, authenticated migration with owner checks. Do not transfer records by matching email or accept a client-supplied owner. Exercise confirmation, session refresh, logout and recovery before replacing the working demo.

## 4. Page composition and shared components

Organize future routes under `(public)`, `(auth)` and `(app)` layouts. Put reusable UI in `components/ui`, the shell/navigation in `components/layout`, and domain workflows in `features/{auth,onboarding,dashboard,catalog,meal,forecast,nutrition,profile,notifications}` as each is implemented. These directories are a target, not a claim that they exist. Route files compose features and handle loading/error/not-found boundaries; they do not calculate nutrition or run models.

Keep typed clients beside the existing `lib/application-api.ts` and `lib/forecast-api.ts`. Validate responses at the transport boundary. Cache keys include authenticated identity, source/session, selected date/timezone and catalog release where relevant. Clear private caches on logout/account switch; never reuse a prior user's data while loading. Share date/unit formatting and nutrition-basis utilities. Do not put access tokens, CGM, recipe drafts or private health records in URLs, analytics or persistent service-worker caches.

| Shared component | Contract |
|---|---|
| AppShell / PrimaryNavigation / AccountMenu | Same route IDs/order across sizes; skip link, active label and safe-area spacing |
| PageHeader / DateNavigator / SourceBadge | Source, selected date and simulated clock explicit; no silent source fallback |
| GlucoseContextCard / ForecastPanel | Latest reading time, data freshness, origin, model-estimated interval and text/table alternative |
| NutritionSummary / NutrientValue | Units and basis, known/unknown distinction, coverage; goal progress only when a goal exists |
| CatalogCard / SearchControls / FilterPanel | Stable IDs, release/source, accessible favorite control; URL query/filter/sort state |
| MealComposer / PortionControl / IngredientReview | Same quantity validation and confirmed source snapshots for search, scan and recipe paths |
| AdaptiveDialog / ActionSheet / Confirmation | Mobile sheet or full page; desktop dialog; shared content/validation, focus return and cancel |
| AsyncState / EmptyState / ErrorState | Loading, empty, partial, unavailable, denied and retry distinguished; no misleading zero totals |

### Home hierarchy

At all widths, reading order is: source/clock and latest glucose -> recent history plus latest available forecast -> meal action -> today's consumed nutrition and meal list -> recipe discovery. Desktop can place nutrition/recent meals beside the graph, while DOM reading/focus order remains logical. A source without an eligible meal forecast shows history and a prompt to review a meal, rather than a fabricated future line. Recommendations require an identified catalog/source; otherwise show a useful search entry or unavailable state.

### Meal capture and history

Use a quick-add sheet with Search, Favorites, Scan barcode and Enter recipe. Keep a full-page `/meals/new` fallback for long forms, keyboard use and direct links. Selection opens portion/grams, serving basis, slot and timestamp review. Saving a planned meal, forecasting a scenario and logging consumption are separate actions. Show success only after durable server acknowledgement; retries use the same idempotency key. Disable duplicate submission while pending, preserving input on failure.

The daily log groups eaten records by Breakfast/Lunch/Dinner/Snack and displays totals from the same aggregate as Home and Nutrition. Editing/removing requires ownership and concurrency control; deletion is an explicit confirmation, with an undo only if backed by reversible server behavior. Copying a meal creates a new draft/planned instance with a new ID and no outcome/forecast association. Weekly/monthly calendars are deferred enhancements; start with an accessible chronological list and date navigation.

### Catalog detail, search and analyzer

Use photo/title/at-a-glance facts and ingredient/nutrition sections from the reference hierarchy, with text/image fallbacks. Recipe and product actions go through the same meal review. Product facts distinguish pack size, serving and per-100-g basis. Unknown fiber, allergens or preparation times stay unknown; sample Figma numbers are not food facts or fixtures.

Search our published validated catalog first. Preserve query, type, filter and sort in the URL; validate/encode them server-side. Support pagination, result counts and reset filters. Offer only filters supported by catalog metadata, with documented units/basis for nutrient thresholds. Show provider outages separately from genuine zero results. Any approved external fallback is an explicit source choice and is labeled. No location, store price or stock controls without a real authorized data source.

Recipe text extraction is a draft, not nutrition evidence. Resolve each ingredient to a food fact, confirm grams/yield/servings, calculate deterministically, then save a private meal. Keep editing available after partial extraction. Report actual stages and cancellation/retry, not the reference's invented 65% progress. Barcode capture is supported direction; photo-based nutrient inference, arbitrary URL ingestion, public recipe publishing and guided cooking timers are deferred. Finishing cooking never automatically means a meal was eaten.

## 5. Responsive and accessible layout contract

These breakpoints and tokens are GlycoLens implementation choices derived from content needs, not measurements copied from Figma. Reference full-screen frames are chiefly 390 and 1280 pixels wide; there is no supplied tablet design.

| Width in CSS pixels | Layout behavior |
|---|---|
| 320-767 | Single column, five labeled bottom destinations, compact header/account controls; filters and multi-step actions use sheets/full-page forms |
| 768-1199 | Compact navigation rail, one/two columns when content fits; two-column catalog; readable chart plus summaries; portrait and landscape supported |
| 1200+ | Labeled sidebar, main content up to approximately 1360px, chart/summary grid, two/three-column catalog based on available width |

Use fluid Grid/Flex (`minmax(0, 1fr)`, `min-width: 0`), wrapping text and intrinsic image sizing; frame width is not a fixed canvas. Use spacing tokens 4/8/12/16/24/32px, readable rem typography and flexible card heights. Retain the current GlycoLens teal/neutral direction and established history/forecast/interval palette as a starting point; verify contrast before promoting colors into tokens. The Figma lime identity, logos, stock images and exact frame dimensions are not imported. A new CSS framework or chart library is not required for this change.

Required behavior:

- No page-wide horizontal overflow at 320px. Search chips may wrap or scroll within a labeled region. Wide numeric tables have an explicit accessible scroll region or switch to cards without losing values.
- Charts scale to container width, reduce tick density and expose a persistent data table/summary. A user-selected detail view may pan inside its card. Do not shrink labels to illegibility or rely solely on the current `38rem` SVG minimum width. Display history vs prediction, origin, units and interval using text/line styles as well as color; actual outcomes appear only when available.
- Bottom navigation and sticky actions reserve content space plus `env(safe-area-inset-bottom)`. Use viewport units appropriate for mobile browser chrome and test the virtual keyboard. Focused inputs and error messages must remain visible; sticky CTAs must not cover the last rows.
- All controls have names and keyboard operation. Dialogs move/trap focus, close safely with Escape, restore focus and offer a full-page fallback. Announce async completion/errors without moving focus unexpectedly. Provide label-associated field errors and a review summary.
- Target 44px touch controls as a usability goal, meeting at least WCAG 2.2 minimum target requirements and exceptions. Verify contrast, visible focus, reduced motion, 200% text sizing and 400% zoom/reflow. These are acceptance requirements, not a present compliance certification. See [W3C reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) and [target size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html).

## 6. Data semantics and proposed schema changes

Home, Meal log and Nutrition must consume one aggregate contract, not sum whichever records are on screen. Compute local-day boundaries from the user's confirmed IANA timezone, using UTC instants and an exclusive end boundary; handle DST days correctly. A timezone change recomputes grouping without rewriting historical instants. The simulator uses its labeled fixture clock, not wall-clock "today". Keep different sources/sessions partitioned.

Only confirmed **logged/eaten** meal revisions count toward consumed totals. Planned/cancelled meals, recipe browsing, favorites, copied drafts and portion scenarios do not. Distinguish no eaten meals (known empty) from failed/partial retrieval (unknown). Return per-nutrient completeness so a missing fiber value is not silently zero. Source-derived nutrition snapshots remain attached to the consumed meal revision; catalog updates cannot rewrite yesterday's totals. Optional goals have units/effective dates; do not infer deficiency, safe intake or glycemic risk from a ring.

Forward migrations, to be designed and tested before use:

| Area | Proposed record/extension and invariant |
|---|---|
| Identity | Keep `public.users` linked to `auth.users`; no second password/account store |
| Preferences | `user_preferences`: owner, IANA timezone, display units, optional food preferences, source mode; bounded/validated fields |
| Onboarding | `onboarding_state`: owner, flow version, completed steps, completion time; server-validated transition |
| Acknowledgements | Append versioned notice/acknowledgement events with owner/time; distinguish optional consent and withdrawal where applicable |
| Optional goals | `nutrition_goals`: owner, nutrient, target/unit and effective interval; no automatic prescription |
| Catalog | Adopt only the corrected catalog schema/release from ADR 0015; keep canonical products/recipes/ingredients distinct from consumed meal instances |
| Favorites | Separate `favorite_recipes` and `favorite_products` with owner + valid FK + uniqueness; avoid an unvalidated polymorphic ID |
| Meals | Add explicit planned/logged/cancelled state, `consumed_at`, slot, revision/version and immutable source facts; backfill legacy records only from verified semantics |
| Forecasts/outcomes | Reference meal revision and immutable input/context/source snapshot or hashes, forecast origin and availability; editing a meal creates a new forecast candidate and does not relabel the old result |
| Notifications | Owner, event type, safe entity reference, created/read time and deduplication key; server creates system events, owner can mark read |

Every exposed table needs grants, RLS and cross-user tests, including child rows and new catalog policies. Derive owner from the verified session. Audit both direct table grants and existing SECURITY INVOKER RPC dependencies: revoking all writes without redesigning RPC execution can break atomic saves. Derived totals, outcomes, catalog ingestion and forecast results need a reviewed server/SQL write boundary; untrusted browsers cannot author trusted system events or inference evidence. Keep privileged keys server-side and out of URL/logging/UI.

Migrate additively, backfill with evidence, validate constraints, then switch reads/writes. Do not assume old records were eaten or invent missing timestamps. Keep old UI/API compatibility until the new flow passes. Roll back the application via feature flags/previous release; retain compatible columns and do not use destructive down-migrations to undo user records.

## 7. Application API additions and connection boundary

Keep existing `/api/v1` endpoints unchanged during extraction. Browser route names are not API endpoint names. New endpoints below are proposals, not currently callable:

| Module | Proposed endpoints |
|---|---|
| Current user | `GET/PATCH /api/v1/me`, `GET/PATCH /api/v1/me/preferences` |
| Onboarding | `GET/PATCH /api/v1/me/onboarding`, `POST /api/v1/me/onboarding/complete` |
| Dashboard / nutrition | `GET /api/v1/dashboard?date=...`, `GET /api/v1/nutrition/summary?from=...&to=...` |
| Catalog | `GET /api/v1/catalog/recipes`, `GET /api/v1/catalog/recipes/{id}`, corresponding `/products` and detail |
| Meal history / edits | `GET /api/v1/meals`, `PATCH /api/v1/meals/{id}`, `POST /api/v1/meals/{id}/cancel`; revision-aware commands |
| Forecast history / scenarios | `GET /api/v1/forecasts`, `POST /api/v1/forecasts/compare-portions`; preserve current create/read contracts |
| Favorites | Owner-scoped list and idempotent add/remove by typed catalog ID |
| Notifications | Owner-scoped list/read state/mark-all-read; bounded pagination |

Specify schemas, date/range limits, pagination and errors before implementation. Dashboard/summary responses identify selected date, timezone, source/session, server calculation time, coverage and totals. Meals/edits use idempotency and optimistic version checks; stale edits return a conflict with a recoverable review. Resource-not-found/denied responses must not reveal another user's record. Bound expensive requests; the current model/simulator busy states remain explicit. Do not start inference on every slider movement or dashboard refresh.

For managed Supabase setup/testing, obtain the intended development project URL (`https://<project-ref>.supabase.co`), matching publishable/anon client key supported by the chosen SDK, app/API origins, approved Auth redirect URLs, enabled Auth methods, email confirmation/SMTP readiness and synthetic test accounts. A backend secret/service-role key belongs only in server secret configuration when required; migration credentials belong only in migration tooling. Do not paste any private values into this document or chat.

Use Supabase SDK Auth for sign-up, sign-in, confirmation, recovery, refresh and logout. Relevant platform surfaces are `/auth/v1`, `/auth/v1/user` for the current server verification path, and `/rest/v1` for owner-token database access/RPCs. Preserve existing authentication verification until any deliberate JWKS strategy is implemented and tested. Storage `/storage/v1` and realtime are unnecessary for the initial UI; do not create dependencies for unused photos or notifications. Configure exact origins/redirect allowlists, recovery and refresh tests; UI guards supplement API authentication/RLS rather than replacing them. Follow [Supabase Auth](https://supabase.com/docs/guides/auth), [API keys](https://supabase.com/docs/guides/api/api-keys) and [RLS guidance](https://supabase.com/docs/guides/database/postgres/row-level-security) when implementing against the selected SDK/project.

## 8. Delivery and acceptance

The November 10 design expands the documented application experience; it does not move official deadlines or mark the November 7 feature freeze, M2 or M3 complete. Implement in slices, keeping the existing demonstrable workflow available.

| Phase | Slice | Exit gate |
|---|---|---|
| A | Tokens/shell plus permanent Auth and minimal onboarding/preferences; basic profile/settings/help/privacy | Synthetic-user account lifecycle, resume, ownership, source labeling and keyboard flows |
| B | Extract meal/scan/text-analysis/forecast pages; daily log, shared dashboard and nutrition aggregate | Same reviewed meal-to-forecast behavior; totals/timezones/revisions and responsive acceptance |
| C | Validated catalog detail/search, favorites and nonclinical in-app notifications | Corrected release gate; grounded source facts, typed ownership and empty/unavailable states |
| D | Existing planned portion comparison and actual-vs-predicted feedback; deferred integrations/lifecycle tools | No future leakage; immutable scenario/input snapshots; real integration evidence |

Phase labels describe dependency order, not promises to complete the full page inventory by November 13. If catalog correction or cloud configuration is unavailable, retain the reviewed-food/demo path with explicit limitations. Weekly/monthly calendar views, guided cooking, household, grocery/budget, store inventory, social features, AI planning and photo/URL ingestion are outside this UI delivery plan.

Acceptance before each implemented slice is called responsive:

1. Exercise 320/360/390/430, 768/820/1024 and 1280/1440/1920px widths, tablet portrait/landscape, short viewport height, mobile keyboard, safe areas, text resizing and zoom. Dense meals, long names, large unit values and missing data must remain usable. Reuse existing 390/1280 flows as baseline evidence only.
2. Verify keyboard and screen-reader semantics, focus order/dialog recovery, contrast, chart summaries/table and sticky-content clearance. Test actual camera permission/unsupported/denied states on a physical device before declaring scanning complete.
3. Verify registration/confirmation/recovery/expiry/logout, onboarding resume/skip, two-user isolation and no private-cache bleed. Test direct URLs as well as navigation.
4. Verify Home/Meal log/Nutrition agree for eaten meals across pagination, timezone/DST, goal changes, missing nutrients, edits/cancel/retry and source switches. Scenarios/favorites/copies must not inflate totals.
5. Verify catalog unavailable vs empty, extraction partial/retry, safe confirmation, immutable forecast inputs, stale/no CGM, busy/timeout and later outcomes. Do not substitute fixture-provider success for live acceptance.

The detailed validation plan is in [test strategy](../testing/test-strategy.md). This documentation cycle does not rerun application/model tests or certify screens that have not been implemented.

## Immediate deletion lifecycle

`/settings/privacy` offers export and password-confirmed permanent deletion;
`/account-deleted` is the public outcome page. `DELETE /api/v1/me` accepts only
password and exact confirmation, reauthenticates the verified caller and uses
server-only managed Auth hard deletion. It returns confirmed deletion separately
from pending private-file cleanup. The browser clears SDK/cross-tab Auth and
fully navigates to discard private drafts. There is no recovery window.
Migration 14 adds private usage cascade, bounded attempt reservations and a
source-UUID-only cleanup outbox. The API retries failed files every 30 seconds.
See [ADR 0020](../decisions/0020-immediate-account-deletion.md) for role boundaries,
filesystem scope, MFA refusal and provider backup/log/restore release gates.
