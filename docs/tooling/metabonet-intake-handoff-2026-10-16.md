# MetaboNet intake handoff - October 16, 2026

Subsequent dictionary follow-up: saved MetaboNet.html covers all 37 local fields;
source-only training metadata confirms all 15 labels against its table. Units and
previous-five-minute insulin amounts are established, including the IOBP2 exception.
Split/missingness/timezone caveats remain; carb availability/bin endpoints and current
use rights are not resolved. The [review](../reports/metabonet-dictionary-review-2026-10-16.md)
updates the earlier request below: the dictionary has been supplied; terms/README
remain helpful. No new training or test outcomes. HTML/resources remain ignored.

## Goal and scope

Check the user-downloaded files, identify remaining prerequisites and recommend
next steps. Audit only: no training, new model selection, test outcomes, app changes
or external service mutation. Primary workflow: change-delivery, supported by
documentation governance, scoped safety review and Graphify navigation.

## Evidence

User screenshots show portal release v1.2, October 5, 2026, with SIESTA training only.
Files have valid Parquet headers/footers, matching 37-column schemas and no embedded
release ID. Exact local SHA-256 values and row counts are in the aggregate report;
they are local fingerprints, not publisher-authenticated download checksums.
Training: 132,811,004 rows; test: 22,069,548 rows. Final source matching identifies
15 training cohorts, 1,730 training/351 test source-qualified IDs, 169 overlaps and
182 test-only IDs before source/terms exclusions. Bare IDs repeat across cohorts.
The exploratory 172 overlap figure was superseded after resolving CTR3/ReplaceBG.

164 shared combinations have at most a five-minute forward boundary gap; five have
interleaved/reversed ranges. No exact source/ID/date key overlaps and no duplicate
training keys. Only166 shared combinations carry the flag in both files. No test
CGM/insulin/carbohydrate values were projected. All38,470 SIESTA intervals are five
minutes despite fixed wall-clock offsets; do not discard them for that offset.

AZT1D/UOM copies must be excluded from development. Carbohydrate coverage varies;
Loop/ReplaceBG/PEDAP/CTR3 provide substantial new meal-entry candidates. Positive
entries are not yet eligible meal counts. BrisT1D has merged insulin only. OhioT1DM
appears in the download but is labelled DUA-governed by the August publication;
confirm current terms before training on that source. No wrongdoing was inferred.

## Files and checks

New `audit_metabonet.py` and aggregate-only `report_metabonet_audit.py` pipelines;
two synthetic tests; pinned optional `data-audit` DuckDB1.4.4 dependency/lock update.
Audit used two threads/2GB query memory and completed in99.28 seconds. Tests cover
poisoned test outcomes, reused cross-source IDs, fixed-offset cadence, duplicate keys
and truncated files. Research regression:86 passed, one intentional simulator skip.
The two modified synthetic tests also passed after adding cross-source-ID/cadence
assertions. Lint/format and final exclusion/diff evidence accompany tool logs.

Data, scratch, complete JSON and logs remain ignored. The public report contains
aggregate study counts only. Existing dirty M2/presentation/app work is preserved;
no model/application/database/frontend edits in this cycle.

Planning00/01: intake status/navigation; 02: source/schema/splits; 05: protocol
implications; 06/10: intake versus training/closure status; 07: source evidence/terms;
08: metadata/privacy/leakage; 09: formal status; 11: subsequent intake without changing
refinement_v1. Product/architecture03/04 unchanged because no product/API/schema
decision changed. Root/research READMEs and reports index link the audit.

Graphify was ACTIVE; query evidence was checked against calibration_assignments
and the frozen replay guard in source. Final code-only update log:
`.cache/model-refinement-preflight/metabonet-graphify-update.log`. No semantic backend.

## Next action

The files suffice for preparation; no more downloads/keys/GPU required now. Save
portal data dictionary/use terms/source manifest if available. Prepare a streaming
shared-feature loader, confirm interval timing/units/missingness, build eligible
windows, namespace IDs and check provenance/aliases. Freeze a new train/validation/
calibration/test protocol with horizon purges and genuinely unseen test participants;
reserve a source holdout where feasible. Then run a balanced CPU pilot before scaling.
The pilot is proposed, not executed. Keep old results and consumed AZT1D intact.
