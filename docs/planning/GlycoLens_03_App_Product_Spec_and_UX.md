# GlycoLens App Product Specification and UX

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
- confidence/verification state

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

Show same user's past meal instances that are similar by:
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

### Flow 1 - first launch

```text
Welcome to GlycoLens
        |
        +-- Demo with virtual patient
        |
        +-- Connect Dexcom Sandbox
        |
        +-- Import/research mode
```

For capstone demos, default to **Demo with virtual patient**.

### Flow 2 - home

```text
------------------------------------------------
GlycoLens

Current glucose        112 mg/dL
Trend                  slowly rising
[ 2-hour CGM chart                         ]

Recent context
- insulin event: available
- last meal: 3h 10m ago
- activity: light

[ + Plan / Log Meal ]
------------------------------------------------
```

### Flow 3 - meal capture

```text
How do you want to add the meal?

[ Scan barcode ]
[ Search food ]
[ Enter home recipe ]
```

### Flow 4 - recipe

```text
"I made 2 cups basmati rice, 500 g chicken,
one onion, 100 g yogurt and 2 tbsp olive oil"

               |
               v

Parsed ingredients
[✓] basmati rice     2 cups
[✓] chicken          500 g
[?] onion            1 large
[✓] yogurt           100 g
[✓] olive oil        2 tbsp

[ Edit ] [ Confirm ]
```

### Flow 5 - nutrition review

```text
Chicken rice recipe
1 serving

Calories       510 kcal
Carbs           55 g
Protein         29 g
Fat             16 g
Fiber            6 g

Sources:
USDA: 4 ingredients
Open Food Facts: 1 ingredient

[ Save meal ] [ Forecast this meal ]
```

### Flow 6 - context confirmation

```text
Forecast context

Current glucose       112
CGM history           12h
Recent insulin        included
Activity              included
Meal                  confirmed

[ Run Forecast ]
```

### Flow 7 - result

```text
2-hour model forecast

180 |                ...
160 |             ...
140 |         ....
120 |_____....

      now  30  60  90  120 min

30 min      127
60 min      149
120 min     136

Prediction interval shown as shaded band

Model confidence: Moderate

[ Compare portion ]
[ Similar meals ]
[ Save ]
```

### Flow 8 - similar meals

```text
Similar meals from your history: 6

Chicken rice bowl       0.91
Actual +60m change      +31
Date                    ...

Burrito bowl            0.85
Actual +60m change      +38
...
```

### Flow 9 - portion comparison

```text
              100%       75%        50%
Carbs          55         41         28

Forecast       [line A]   [line B]   [line C]

This is a model-based comparison, not treatment advice.
```

### Flow 10 - later feedback

```text
Your actual response is now available.

Predicted vs actual
[overlaid chart]

60-min error: 8 mg/dL
Full 2h MAE: 10.4 mg/dL

[ Add note ]
[ Save to Meal Passport ]
```

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

Implementation:
- Postgres filters
- pgvector for meal text/ingredient embeddings
- numeric standardized distance for macros/context

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
