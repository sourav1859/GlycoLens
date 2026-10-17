# MetaboNet dictionary review - October 16, 2026

The saved `MetaboNet.html` is the complete data dictionary. It documents all **37
local schema fields**. All **15 actual training source labels** match its source
table after case/punctuation normalization. This resolves the earlier provisional
source-name mapping. The table lists 22 possible sources; that does not mean all
22 occur in these downloaded files.

The saved page SHA-256 is
`b5d2ae034449464c1c37c216c616785dac479f5dad46141f13a0ee621650af14`.
The HTML and extracted details remain ignored. Only documentation text was parsed;
no scripts/assets were executed and no test outcomes were read. A source-column-only
training query verified labels; the original train/test files and model results were
not changed. Detailed review evidence is in ignored
`artifacts/evaluation-results/metabonet-audit/dictionary-review.json`.

| Field or issue | Dictionary finding | Implementation implication |
|---|---|---|
| CGM | mg/dL | No additional mmol/L-to-mg/dL multiplication for these source values |
| basal / bolus | IU delivered during the previous five minutes | Amounts per interval; do not treat as U/hour or multiply/divide by 12 |
| insulin | Total previous-five-minute amount, basal plus bolus | Use a deliberate representation; adding total to its components double-counts delivery |
| IOBP2 | All insulin recorded as bolus | That channel does not establish a conventional meal/correction bolus; use source-aware handling |
| carbs | User-reported grams; zero/null conventions differ by source | Preserve availability/missingness; sparse nulls do not prove complete meal logging |
| date | Measurement timestamp; some timezones ambiguous/unknown | Preserve source-local ordering and offsets; no invented UTC localization |
| source_file | Source dataset name | Exact documented labels can replace the provisional substring classifier in the new loader |
| id | Described as unique; cross-study consolidation may occur | Actual audit found reused bare IDs; retain source-qualified identity and alias checks |
| is_test | Test/validation flag | Preserve provenance; it does not itself guarantee a valid unseen-person evaluation |
| subject_split_across_traintest | Subject occurs in both sets | Meaning confirmed; observed 169 overlaps/166 jointly flagged still govern checks |

The dictionary's semantic types are not always the physical Parquet types. For
example, carbs/age are described as integers but stored as DOUBLE. Retain finite
numeric values and missingness; do not silently truncate or reject the file for this.

Its global coverage figures refer to a consolidated 203.4-million-row population,
not necessarily the local 154,880,552-row train/test pair. Do not substitute those
coverage percentages for the measured per-source audit. Full protein/fat/fibre
fields are still absent; this remains a shared-feature dataset.

## What remains unresolved

- **Carbohydrate availability/bin timing:** previous-five-minute timing is explicit
  for insulin. The exact carb-bin endpoint convention and when an entered meal was
  actually available are not specified. Define a conservative origin policy before
  meal-centred features; assess any one-bin timing sensitivity on development only.
- **Zero versus unrecorded:** the dictionary explains source differences but does
  not recover observation masks or prove missing events did not occur.
- **Current source-use rights:** this is a data dictionary, not a licence/DUA grant.
  The previous OhioT1DM terms question remains; preparing other sources can continue.
- **Split integrity:** definitions do not remove the observed shared participants,
  source copies or short boundary gaps. The new protocol still needs subject/source
  separation and target purging. No new training has started.

No additional dataset download, API key or GPU is needed to prepare the loader.
The next action remains streaming shared-feature preprocessing, eligible meal-window
counts and a frozen protocol, followed by the proposed balanced CPU pilot. Save
current data-use terms/README if available; they are the remaining documentation
request, not a blocker for independent preparation work.

Reviewed planning00/01 (status unchanged), 02 (units/source mapping), 05 (causal
timing/split meaning), 08 (source-specific insulin/timezone/privacy risks), and11
(prerequisite status). No product/API/schema/schedule/model-selection change.
Updated those affected sections, research README, intake-report generator and handoff.
Verification uses field/source-label checks and documentation consistency; no new
predictive experiment or model test result is claimed.
