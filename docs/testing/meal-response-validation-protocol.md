# Meal and portion response validation

## Executed result — November 12

The frozen matrix is now executed; see [actual results](../reports/meal-response-sensitivity-2026-11-12.md). Engineering completion/repeatability passed, but **GL-P09-011 Chronos meal-response capability FAIL_INVARIANT** at the original 0.001 mg/dL tolerance. Native LightGBM shows limited carbohydrate-only synthetic sensitivity. GL-P09-012 matching-outcome accuracy remains NOT_RUN; no consumed cohort was reused. The protocol below is the original pre-execution specification, not a claim that execution is still pending.

Original planning status: **planned, not executed at protocol creation**. Added November 12, 2026 under P09/M3.
This evaluates the application Chronos-2 adapter, not the recipe-extraction LLM.

## Why this gate is separate

Existing tests prove nutrient scaling, frozen context, request wiring and scenario
storage. They do not establish that the model responds usefully to meal changes.
The fixed py-mgipsim replay contains preset meals; adding a user meal does not
replace those meals. Its later trajectory is therefore not a matched outcome for
that user's proposed meal. Do not calculate meal-response accuracy from it.

## A. Controlled sensitivity experiment — GL-P09-011

Before executing, freeze the fixture manifest, code/adapter/checkpoint revision,
feature version, CPU dependencies, quantile levels, seed, tolerances and scoring
script. Use synthetic fixtures only, no cloud writes or paid LLM calls. Keep the
CGM history, synthetic insulin, source, forecast origin and model identical within
each comparison. Use the current `recorded_events_v1` representation: nutrient
events at the origin and zero additional future meal events, not an absorption model.

Predeclare at least three CGM contexts (flat, falling, rising) and four labeled
complete synthetic nutrient profiles (lower carbohydrate, higher carbohydrate,
higher fat/protein, higher fiber). Include a clearly labeled Palak Paneer example
at 100 g and 250 g; its fixture facts must have explicit provenance or be marked
illustrative, never silently treated as a validated catalog recipe.

For each base profile, compare 50%, 75%, 100%, 150% and a custom portion. Add
single-nutrient contrasts while holding all other channels fixed, and repeat an
identical baseline three times per history. The independent oracle computes grams
and all nutrient channels before inference; verify exact approved differences in
the captured model input, not just a meal ID in the database.

Report every requested/completed/failed run, reasons, latency, peak memory, all 24
quantiles and changes in median/interval width at +30/+60/+120 minutes. Report the
maximum and mean absolute trajectory change, repeat spread and proportion of
changed-input comparisons with indistinguishable outputs. Use a predeclared
numerical tolerance of 0.001 mg/dL for identical-run repeat checks; disclose any
platform nondeterminism rather than changing this tolerance after seeing results.
Report direction and portion-response relationships descriptively. Do not assert
that increasing carbohydrate must increase every forecast point.

Acceptance requires a reproducible artifact and complete matrix accounting,
correct input isolation, finite ordered quantiles and explicit review of invariant,
unstable or surprising responses. An all-identical or unstable response is a failed
meal-response capability gate even if input plumbing works. A nonzero change alone
does not establish useful magnitude, accuracy or causality. Record the capability
as limited and retain that limitation in UI/help until evidence supports stronger
wording. No automatic adapter/model switch follows from this experiment.

## B. Accuracy against matching observations — GL-P09-012

Use a separately approved, prospectively frozen protocol and eligible held-out
observational windows with genuinely matching meals/portions and post-meal CGM.
Record meal timing/quantity uncertainty, insulin, missingness and subject/time
split controls. Compare against persistence and CGM-only context. Report trajectory
and +30/+60/+120 MAE/RMSE, q10–q90 coverage/width, failure rate and participant-level
uncertainty, stratified by meal composition/portion where sample sizes permit.
Predeclare selection criteria, minimum sample sizes and any numerical improvement
gates before accessing outcomes; insufficient strata remain inconclusive.

The primary and PEDAP test cohorts in protocol 16 are already consumed. Do not
reuse their outcomes for tuning, reselection or a new independent claim. Development
data may support explicitly exploratory diagnostics; new independent acceptance
requires an untouched approved evaluation target. Keep synthetic sensitivity and
observed-outcome accuracy reports separate. Neither supports dosing advice or a
guaranteed individual response.

## Evidence and milestone handling

Store aggregate, privacy-reviewed reports in `docs/reports/` and detailed generated
artifacts in ignored `artifacts/`. Include the matrix manifest hash, runtime/model
identity, expected/observed assertions, failures and limitations. P09 remains open
until both cases have appropriate evidence; a completed sensitivity experiment
cannot turn blocked outcome accuracy into PASS. No course deadline is changed.
