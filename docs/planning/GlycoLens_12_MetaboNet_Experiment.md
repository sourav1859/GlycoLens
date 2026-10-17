# MetaboNet Phase 2 preparation protocol

Approved implementation started October 16, 2026. Version `metabonet_phase2_v1`.
This protocol is distinct from the preserved initial UOM/AZT1D refinement. No
model fitting, new accuracy claims, app model switch or deployment in Phase 2.

## Acceptance and fixed preparation choices

- Match the exact audited v1.2 train/test bytes and reviewed dictionary. Record
  their hashes, implementation/package versions and an execution-source snapshot.
- Development sources: **Loop and ReplaceBG** from publisher train only. Give each
  source equal pilot quotas; no source or participant ID becomes a predictor.
- Stratify by source. Stable SHA-256 ordering with seed20261016 assigns subjects
  70/15/15 to training/validation/calibration. Select at most 100/25/25 per source
  before looking at outcomes: a 200/50/50-subject pilot pool. No replacement for
  subjects/events rejected later. Report actual usable subjects and events.
- Primary final test: publisher-test IDs in those sources absent from **all**
  publisher training, not just absent from the selected pilot. Reserve **PEDAP**
  in both publisher files as a separate source test. It is pediatric and must
  be reported separately. Read their provenance/date/split metadata only now;
  eligible test-event counts wait until model/configuration selection is frozen.
- Exclude AZT1D/UOM copies from new development/test evidence; they are consumed.
  OhioT1DM remains out pending current use-rights confirmation. Other sources are
  outside this initial pilot; BrisT1D/CTR3 merged insulin and IOBP2's bolus meaning
  are not silently mapped to ordinary bolus channels.
- Each selected subject contributes at most 100 candidate positive-carb rows,
  chosen by stable event-ID hash, independent of future CGM, history or delay.
  Preserve event identity across 2/6/12/24-hour histories and both timing variants.
- Primary carb availability assumption: five minutes after the recorded bin.
  A zero-minute variant is a **development-only sensitivity**, not a parameter
  chosen to improve held-out scores. The operational task is a two-hour forecast
  from logged-meal availability, not proven prediction at the exact physical meal.
  Actual logging latency is unknown. No full protein/fat/fibre inputs are invented.
- Twenty-four target points at five-minute spacing: require finite positive source
  CGM at every target timestamp, no target imputation or output clipping. History
  uses exact relative grids, permits past-only forward fill up to 10 minutes, and
  requires >=90% finite positive readings at requested history timestamps. Never
  interpolate from a future reading. Source-harmonized values may already have
  unknown upstream processing; record-present is not a raw-sensor guarantee.
- Insulin fields remain IU amounts over trailing five-minute bins; never forward
  fill a dose or add total insulin again to basal+bolus. Preserve finite/nonnegative
  record-presence masks and unknown sparse-event entries. Some zeros may represent
  missing events; masks cannot recover source logging completeness.
- Reject a meal with another positive-carb entry in the preceding 15 minutes, or
  a later positive entry through forecast end. Do not invent a summed/deduplicated
  meal from repeated equal amounts. This is **retrospective isolated-meal selection**;
  later-meal exclusion is not information available to a live forecast. Report
  exclusions and do not generalize scores to all real-world meals.
- Check exact, varied, six-hour finite CGM fingerprints at hourly endpoints among
  selected development IDs. Quarantine all IDs sharing a fingerprint, regardless
  of assigned split. No post-score exclusion. These partial exact checks identify
  duplicate candidates, not verified people, and cannot prove no cross-source aliases.

## Artifact and leakage boundary

Use a bounded DuckDB projection sorted by opaque subject ID/time, then process
one subject at a time. No complete dataset in pandas, no app database imports.
Only source/ID/date/publisher flags are projected from test. Preserve precise source
nanoseconds in artifacts; adapter datetimes have microsecond precision and retain
relative spacing. Source-local ambiguous timezones are not invented as UTC.

Development examples keep context/masks and future truth in separate fields;
conversion returns immutable ForecastRequest and separate ForecastTarget. No
post-origin insulin/glucose/event value may enter a request. Whole-subject splits
and per-file target availability prevent cross-split target borrowing. Original
publisher shared-subject test records are not appended to training or primary test.

Write windows, subject manifests/quality records, projections, hashes and code ZIP
only to ignored artifacts. Build in a separate staging directory; publish the final
directory only after checks. Completed output refuses replay or overwriting. Verify
artifact integrity before consumption; reserved test roles cannot be read through
the development-window iterator. Preserve partial failed builds for diagnosis.

## Phase gate and subsequent experiments

Close Phase 2 after unit/integration leakage checks, a real preparation run, nonempty
primary train/validation/calibration windows, documented source/ID exclusions and a
frozen manifest/protocol with verified hashes. Reserved test **metadata** counts are
reported; their outcome-based eligibility deliberately remains unknown.

Next, Phase 3 compares frozen histories on matched validation events. Phase 4 fits
small direct models on training only; Phase 5 compares frozen-Chronos corrections.
Keep separate calibration outcomes for interval bands. Primary selection is
participant-average trajectory MAE, tie higher within-10. Retain the proposed gate:
>=10% MAE improvement over matched persistence, no lower within-10 rate and no worse
pooled p95 error. Allow persistence to win; +/-10 is aspirational, not a guarantee.
Phase 6 requires frozen model/preprocessing/configuration before test-value access,
and reports tails/failures/calibration plus study/participant subgroups. No full
foundation training is implied. Phase 2 does not claim prediction performance.

## Execution ledger

**Complete, October 16, 2026.** The real build took 281.24 seconds. The subsequent
[Phase 3 experiment](GlycoLens_13_MetaboNet_Frozen_Inference.md) is also complete;
Phase 4 direct-model training is also complete under
[protocol 14](GlycoLens_14_MetaboNet_Direct_Models.md); Phases 5 and 6 subsequently completed; their ledgers/results follow.
Original Phase 2/3 artifacts remain unchanged. LightGBM improved validation macro
MAE 16.03% to 31.17 mg/dL on the same 1,509 meals, passing the gate, but within-10 is
still poor at 26.84%. At Phase 4 completion calibration and reserved outcomes were
untouched; Phase 6 below now records their use. See
[Phase 4 results](../reports/metabonet-phase4-training-2026-10-16.md).
The selected 200/50/50-subject pool yielded the following primary six-hour data:

| Role | Eligible windows | IDs with eligible windows |
|---|---:|---:|
| Training | 8,973 | 197 |
| Validation | 2,000 | 48 |
| Calibration | 1,948 | 48 |

There were 374,898 positive-carb rows in selected subjects, of which 28,852 origins
were hash-sampled. No subjects were substituted after eligibility checks. Rejections
and all 2/6/12/24-hour and timing counts are in the
[aggregate report](../reports/metabonet-phase2-preparation-2026-10-16.md). Partial
fingerprint checks covered 1,474,695 distinct sequences with zero shared-ID candidates.
The primary test reserves 104 identities and PEDAP reserves 65; eligible test windows
are deliberately not yet computed. No model training or inference occurred.

Frozen output: ignored `artifacts/evaluation-results/metabonet-phase2-v1/`, including
protocol SHA-256, artifact hashes, source ZIP, manifests and projections. Full integrity
and disjointness verification passed. Six synthetic acceptance/integration tests
cover units, missingness, causal fill, immutable truth separation, cadence, candidate
identity, subject roles, metadata-only test access, replay and corruption. The reader
also verifies protocol/split-metadata hashes before yielding windows. That final read
guard and verification-before-publication ordering were added after the real build;
its original executed source remains archived and unchanged. The real output passed
full verification after publication and again with the final verifier. No window or
policy changed. See the [handoff](../tooling/metabonet-phase2-handoff-2026-10-16.md).


## MetaboNet Phase 5 completion

**Phase 5 was complete before the Phase 6 evaluation recorded below.** Frozen C2
generated 6,756 training forecasts; 6,756 usable meals / 196 identities supported six CV
configurations / 18 fold fits and four final refits, with exactly matched direct
controls. Neither correction passed the predeclared incremental gate; retain Phase 4
LightGBM. Lowest-MAE eligible option: `ridge_residual_1000`; advancement candidate:
`lightgbm_direct` (macro MAE 31.17 mg/dL, within +/-10 26.84%). These are
reused-validation findings, not independent confirmation. At Phase 5 completion, calibration/reserved outcomes were untouched.
Phase 6 below supersedes that access status; app inference remains unchanged.
See [protocol 15](GlycoLens_15_MetaboNet_Chronos_Correction.md) and [results](../reports/metabonet-phase5-correction-2026-10-16.md).

## MetaboNet Phase 6 completion - current status

**The broader-data model-refinement sequence, Phases 1-6, is complete.** Separate calibration used 48 participant representatives from 1,488 eligible meals. Frozen LightGBM scored 29.91 mg/dL macro trajectory MAE / 28.20% within +/-10 on 3,533 primary-test meals (102 IDs), and 40.92 / 19.57% on 2,177 PEDAP meals (64 IDs). Both predeclared point-improvement gates passed, with zero failed forecasts; tight precision remains poor. Nominal 80% marginal coverage was 79.05% primary and 63.94% PEDAP. Both test cohorts are now consumed; no test-based reselection, point refit, app promotion or full-M2 closure.

All 104 primary and 65 PEDAP reservations were opened only after the calibration freeze. They yielded 102/64 eligible IDs. Hash-sampled origins numbered 10,180/6,332; no participant/candidate replacement or cross-file target borrowing. No duplicate candidate IDs were found among 2,519,890 distinct partial fingerprints; this is not a global identity proof.

See [protocol 16](GlycoLens_16_MetaboNet_Independent_Evaluation.md), [independent results](../reports/metabonet-phase6-independent-2026-10-16.md) and [verification handoff](../tooling/metabonet-phase6-handoff-2026-10-16.md).
