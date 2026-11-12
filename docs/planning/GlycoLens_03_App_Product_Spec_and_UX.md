# GlycoLens App Product Specification and UX

## November 12: demo controls and discoverable logout

The demo uses **Run new simulation** and **Replay saved simulation**. Both keep
the fixed virtual-patient clock; replay requires a simulation saved on this server.
Neither label implies a live CGM connection or a new user-meal simulator protocol.
Sign out is available in the responsive app header and demo account bar, reusing
Supabase Auth logout. Anonymous users must confirm losing identity access. Private
routes and demo drafts clear on identity changes, including another tab signing out.
Meal inputs reaching the model are distinct from validated meal-response quality;
see the [P09 protocol](../testing/meal-response-validation-protocol.md).

## Implementation checkpoint - November 11, 2026

Cloud schema, trusted writes, permanent-account development Auth/onboarding and
the responsive application shell are implemented. Common meal capture/history/
edit/cancel, immutable Chronos forecasts, Home/daily/seven-day consumed nutrition,
owned notifications/export, portion comparisons and genuinely later virtual
observations now have code and scoped test evidence. The original demo moved to
`/demo`; `/` is a public entry and private routes require account/onboarding.

This is a **partial validation checkpoint**, not full phase/release acceptance.
Corrected catalog/search/details/favorites, real email verification/recovery,
verified anonymous upgrade, provider retention/restore, physical-device/manual accessibility,
scratch replay/restore and hosted acceptance remain open. Keep these changes local
for review; scratch replay is explicitly deferred. See the
[implementation report](../reports/webapp-implementation-checkpoint-2026-11-11.md),
[ADR 0019](../decisions/0019-trusted-cloud-writes-and-frozen-source-context.md) and
[actual case ledger](../testing/webapp-validation-results.json). Earlier dated
prototype/preparation evidence below remains historical.

The user confirmed **immediate account deletion after explicit confirmation,
with no recovery window**. Password reauthentication, hard Auth deletion, owned
row cascades and retryable private-file cleanup are implemented and validated with
synthetic accounts. See [ADR 0020](../decisions/0020-immediate-account-deletion.md)
and [deletion evidence](../reports/account-deletion-validation-2026-11-11.md).
Provider backup/log retention, restore reconciliation and a support contact remain
public-release gates; there is no application undo snapshot.

Implementation follows [plan 17](GlycoLens_17_Webapp_Implementation_Plan.md): one
repo, dedicated cloud Supabase development, verified email/password accounts and
the full feature set in staged releases. All routes/flows below map to its phase
and test-case gates. This is the current target; the embedded anonymous/local
prototype remains historical baseline evidence until cloud implementation passes.

November 10 responsive UI design: authenticated Figma inspection covered all 44 unique supplied nodes. The [reference review](../reports/figma-reference-review-2026-11-10.md) records observations and exclusions. The [responsive UI architecture](../architecture/responsive-webapp-ui.md) defines the planned routes, shared components, onboarding, data contracts and acceptance; [ADR 0017](../decisions/0017-responsive-webapp-and-figma-reference-boundary.md) records the decision. This updates the design, not application code or completed milestone evidence.

## 1. Product principle

The app should make the model output **easier, concrete, and useful**.

The primary user should not need to understand:
- foundation models
- covariates
- embeddings
- MAE
- model adapters

The user should see:

1. **What is in my meal?**
2. **What happened after similar meals before?**
3. **What does the model forecast today?**
4. **How uncertain is the forecast?**
5. **How does a portion change affect the model prediction?**

## 2. App form factor decision

### Recommended: mobile-first Progressive Web App (PWA)

Why:

- a T1D meal workflow happens on a phone
- one codebase works on iOS, Android and desktop
- no app-store approval
- installable to home screen
- browser camera access can support barcode scanning
- faster to implement and debug during a three-month capstone
- advisor/panel can open the same URL on a laptop

A native React Native/Expo app is a reasonable alternative only if:
- native device integration becomes a core requirement, or
- the advisor specifically wants a native mobile deliverable

## 3. Personas

October 14 implementation approval prioritizes Persona A with live py-mgipsim.
Dexcom remains later work. Recipe extraction is API-backed; user confirmation and
deterministic nutrition grounding remain mandatory. No M2 screens are claimed
complete by this approval alone.

### Persona A - Demo / virtual patient
Used for capstone development and presentation.

Data source:
- py-mgipsim scenario
- imported historical timeline
- fake demographic profile

### Persona B - Sandbox CGM user
Used to demonstrate Dexcom OAuth and EGV retrieval.

### Persona C - Future real T1D user
Product vision only. Real-user healthcare deployment is not required for the capstone.

## 4. MVP feature set

### October 14 implemented prototype

The default browser page now selects an authenticated virtual-patient session,
runs live py-mgipsim or labeled replay, shows only glucose available by the simulation
clock, captures search/barcode/recipe inputs, confirms grams/servings and food sources,
saves a meal, runs the selected Chronos C3 model, and shows earlier same-session
numeric matches. Two real browser flows and four fixture input contracts pass.
Recipe output remains editable and never supplies nutrition. All required nutrients
must be resolved before saving. Live USDA/recipe-provider validation and physical
camera exercise are still pending; the fixture path is not proof of those integrations.
Forecast summaries round for readability, and mobile chart scrolling stays inside
its card. Under-covered model intervals are not clinical confidence labels.

### F1. Home / glucose context

Display:
- latest glucose
- recent trend chart
- source: historical / virtual / Dexcom sandbox
- recent insulin events when available
- recent meal marker

Do not create clinical alarm logic.

### F2. Add a meal

Three paths:

1. **Scan barcode**
2. **Search food**
3. **Enter recipe**

Stretch:
- meal photo / OCR

### F3. Nutrition resolution

November 6 source proposal: a corrected Azure catalog could support existing recipe
selection, ingredient search and packaged-food lookup. Recipe use is deferred while
upstream corrections continue. The [migration strategy](../reports/azure-to-supabase-catalog-migration-strategy-2026-11-06.md)
preserves explicit serving bases, editable confirmation and provenance; it does not
implement these paths or replace arbitrary recipe-text extraction.

Packaged food:
- search USDA FoodData Central
- fallback to Open Food Facts

Home recipe:
- LLM parses ingredient + quantity
- user confirms
- ingredients resolved to food database
- deterministic math calculates totals

Show:
- serving
- calories
- carbs
- protein
- fat
- fiber
- source/provenance
- source/verification and missing-data state; no medical confidence score

### F4. Forecast

Input:
- structured meal
- recent CGM
- recent insulin
- optional activity/time context

Output:
- 2-hour glucose trajectory
- median prediction
- uncertainty band
- 30/60/120-minute values
- model/version shown in research mode

### F5. Similar Meals / Meal Passport

The current implementation uses same-owner, available-past-outcome filtering and fixed-scale numeric macro distance. Semantic/vector and additional contextual ranking remain planned. The target can consider:

- meal/ingredient semantics
- macros
- pre-meal glucose context
- optional insulin/time context

For each:
- actual post-meal trajectory
- date/time
- portion/nutrition
- outcome summary

### F6. What-if portions

Quick options:
- 50%
- 75%
- 100%
- custom portion

Recalculate nutrition and rerun inference.

Language:
- "model-predicted scenario"
- never "recommended dose" or "safe amount"

### F7. Actual-vs-predicted follow-up

When the two-hour post-meal CGM becomes available:

- overlay predicted trajectory
- overlay actual trajectory
- calculate simple absolute error
- save meal instance/outcome to Meal Passport

This creates a satisfying user feedback loop.

### F8. Research mode

Separate from patient-facing UI.

Functions:
- switch model
- switch context configuration
- run an event
- inspect raw quantiles
- compare model latency
- export results

## 5. End-to-end user experience

### Implementation status and scope

The executable app now has a public entry, permanent-account development Auth, resumable onboarding and an authenticated responsive route shell. The earlier integrated workflow remains at `/demo`. Cloud-backed meals, immutable forecasts, consumed nutrition and account activity have scoped evidence; real email delivery, corrected catalog, physical camera and full release acceptance remain open.

The target page inventory and delivery order are defined in [architecture section 2](../architecture/responsive-webapp-ui.md#2-navigation-and-route-contract). New product pages are planned until their code and acceptance evidence exist.

| Area | Target experience | Current implementation boundary |
|---|---|---|
| Account/onboarding | Registration, confirmation/recovery, resumable preferences/source/review | Dev email/password + resumable cloud onboarding implemented; real email/verified upgrade pending |
| Home | Source/clock, latest glucose, graph/forecast, eaten nutrition, daily meals and recipe discovery | Cloud source/clock, glucose, eligible forecast and eaten aggregates implemented; discovery waits for catalog |
| Search and details | Database recipe/product tabs, filters, details and source facts | Provider composer implemented; database catalog/detail activation pending |
| Meal log | Daily slots/history, reviewed entry, edit/cancel, source snapshots | Owned list/detail/revision-safe edit/cancel and frozen ingredient facts implemented; broader pagination/date acceptance ongoing |
| Scan / analyze | Barcode plus manual fallback; editable recipe text resolved to food facts | Dedicated scan/analyzer routes and common composer implemented; physical camera/live-provider acceptance pending |
| Forecasts | History/detail, uncertainty, summaries, similar outcomes and scenario comparison | Owned list/detail, frozen context, scenario/follow-up implementation; complete UX/timeout matrix pending |
| Nutrition | Shared daily totals, seven-day trend and optional goal display | Shared consumed-day and seven-day aggregate/table implemented; optional-goal editing pending |
| Profile/settings | Account, units/timezone, source, privacy, logout and preferences | Profile/preferences, source/unit/timezone, logout and bounded export implemented; immediate password-confirmed deletion implemented; provider backup/log/restore gates remain |
| Favorites/notifications | Typed saved catalog items and owned nonclinical in-app events | Owned trusted notifications implemented; catalog favorites pending |
| Help/privacy/errors | Accurate research/data explanations and recoverable route states | Public notices and route recovery implemented; support contact and provider backup/log retention detail pending |

### Flow 1 - account and minimal onboarding

`Welcome -> choose demo or permanent-account path -> authenticate -> resume required setup -> review -> Home`.

Adapt the reference's progressive steps and editable review. Confirm timezone, glucose display unit, available data source and research/privacy acknowledgement. Nickname and food preferences/nutrition goals are optional. Do not require DOB, sex, height, weight, diagnosis, medication or family/child records. Complete onboarding server-side with versioned state; optional steps can be skipped. Keep identity separate from the virtual patient. The field and account migration contracts are in [architecture section 3](../architecture/responsive-webapp-ui.md#3-onboarding-and-account-state).

### Flow 2 - home and navigation

Use **Home, Search, Meal log, Forecasts, Nutrition** consistently: bottom navigation on mobile, compact rail on tablet, labeled sidebar on desktop. Favorites, profile/settings, notifications and help are accessible account destinations. Add meal opens the common composer; scan and analyze are methods within that journey.

Read Home in this order: source and simulated/real clock -> glucose history/latest eligible forecast -> meal action -> consumed nutrition and daily meal list -> catalog discovery. Never fabricate a forecast for a source without eligible inputs. Unknown nutrition is distinct from zero; a goal ring appears only with an explicitly configured goal. The reference's household, grocery, budget and AI-planning modules are excluded.

### Flow 3 - search, scan or recipe capture

`Search catalog / Scan barcode / Enter recipe / Favorites -> select source item -> confirm ingredients, grams/servings and provenance -> review meal`.

Recipe and product details have their own routes and lead to the same composer. Search the validated published catalog first; any external fallback is an explicit labeled source. Support filter reset, genuine empty results, unsupported barcode, permission denial, provider outage and partial extraction. Text extraction remains editable; it never supplies nutritional truth. Do not add URL/photo nutrient inference from the reference.

### Flow 4 - review, log or plan

Review meal name, slot, quantity/basis, nutrition, timestamp, source and missing values. Keep **log as eaten**, **save planned meal** and **forecast scenario** distinct. Success follows a durable server acknowledgement, with idempotent retry after failure. Copying creates a new draft/planned instance without copying outcomes or claiming consumption. Editing/removing uses owner/version checks and preserves previous forecast inputs. Weekly/monthly calendar views and guided cooking are deferred.

### Flow 5 - forecast and personal evidence

`Confirmed meal -> available pre-origin context -> selected adapter -> persisted forecast -> chart/summaries -> earlier same-owner outcomes`.

Show history versus prediction, origin/source/freshness, units, q10-q90 interval, 30/60/120-minute estimates and a chart table/summary. The current app uses Chronos C3 and bounded inference; UI work does not promote a research model or manufacture a confidence rating. Under-covered intervals and forecasts remain research estimates. Similar-meal evidence uses only outcomes available at the forecast origin.

### Flow 6 - portions and later feedback

A future portion comparison recalculates grounded nutrition and requests scenarios at the same origin/context, labeled "model-predicted scenario". It never logs a second eaten meal or recommends a safe amount/dose. Later actual-versus-predicted feedback attaches only when genuine post-meal data is available, remains separate from inference inputs and records outcome availability. No future outcome enters retrieval before that time.

### Flow 7 - daily nutrition, saved items and account

Home, Meal log and Nutrition read one timezone/source-scoped server aggregate of confirmed eaten meal revisions. Planned/cancelled entries, copied drafts and scenarios are excluded. Show per-nutrient coverage and optional goal history without inventing clinical targets. Favorites reference catalog items, not meal events. Notifications are private nonclinical application events, with read/unread and safe links; delivery reminders require their own opt-in implementation.

### Responsive acceptance

Use fluid single-column mobile, adaptive one/two-column tablet and sidebar/grid desktop layouts. Reference widths are examples, not fixed canvases. Preserve every datum, unit and primary action at 320px; expose readable chart summaries/tables, handle virtual keyboards and safe areas, and verify focus/zoom/touch behavior. See [responsive rules](../architecture/responsive-webapp-ui.md#5-responsive-and-accessible-layout-contract) and [test strategy](../testing/test-strategy.md). Existing 390/1280 tests are baseline evidence, not proof of the expanded page inventory.

## 6. Personalization design

### Level 1 - current context
Automatically individualized through:
- user's CGM
- user's insulin history
- user's meal

### Level 2 - historical retrieval
Use same user's previous meal instances.

### Level 3 - optional calibration
If enough history exists, learn a small correction to the foundation-model forecast.

Do not build a patient-specific deep model.

## 7. Similar-meal retrieval without GraphRAG

Recommended score:

```text
score =
  w1 * semantic_food_similarity
+ w2 * macro_similarity
+ w3 * premeal_glucose_similarity
+ w4 * recent_insulin_similarity
+ w5 * time_of_day_similarity
```

Current implementation: Postgres owner/chronology filters and fixed-scale numeric macro distance. The score above is a future design, not the shipped ranking.

Potential extensions:

- pgvector for meal text/ingredient embeddings after model/dimension selection
- validated numeric context features with available-at-origin controls

This is more transparent and cheaper than GraphRAG.

## 8. Competitive context

Existing products already provide parts of this experience:

- **Undermyfork** combines meal photos with glucose/insulin and lets users compare responses.
- **Tidepool** combines diabetes-device data with meal/exercise notes.
- **Glooko** aggregates glucose, insulin, food and activity with trends.
- **mySugr** provides logging, meal photos, statistics and reports.

GlycoLens should therefore avoid being only a "diabetes logbook."

Differentiating prototype loop:

> **verified meal composition -> pretrained meal-aware inference -> uncertainty -> personal historical evidence -> portion scenario -> later actual-vs-predicted feedback**

## 9. Explicitly out of scope

- insulin dose calculation
- pump control
- clinical alerts
- diagnostic claims
- medical "safe/unsafe" meal classification
- complex social/community functions
- native app-store release
- GraphRAG as a core dependency
- meal-photo nutrition estimation as a required feature

## References

- Next.js PWA guide: https://nextjs.org/docs/app/guides/progressive-web-apps
- USDA FoodData Central: https://fdc.nal.usda.gov/api-guide/
- Open Food Facts API: https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/
- Undermyfork: https://www.undermyfork.com/
- Tidepool: https://www.tidepool.org/how-it-works
- Glooko: https://glooko.com/patients/
- mySugr: https://www.mysugr.com/diabetes-app
