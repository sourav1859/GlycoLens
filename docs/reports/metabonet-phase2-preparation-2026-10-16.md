# MetaboNet Phase 2 implementation and preparation results - October 16, 2026

**Phase 2 development preparation is executed. No model was trained, no forecast was generated and no reserved test outcome was projected.** Counts below describe data eligibility, not prediction accuracy. The next stage is frozen-inference validation under this new protocol.

## Implemented behavior

The loader uses native mg/dL, grams and previous-five-minute IU amounts. A bounded DuckDB query projects selected publisher-training rows in subject/time order, then Python processes one subject at a time. It retains source-qualified IDs and missing event values, emits record-presence masks, and converts prepared records to immutable ForecastRequest plus separate ForecastTarget objects. No future CGM/insulin values enter requests, no full nutrients are invented and total insulin is not added to its components. The adapter entry point can return CGM-only requests for Chronos.

Development sources are Loop and ReplaceBG. Stable subject-hash ordering within each source assigns 70/15/15 to train/validation/calibration. Metadata-only quotas select up to 100/25/25 subjects per source before seeing targets. Subjects rejected by quality checks are not replaced. No source/subject identity is a model feature.

## Selected development pool

| Source | Split | Selected IDs |
|---|---|---:|
| Loop | calibration | 25 |
| Loop | train | 100 |
| Loop | validation | 25 |
| ReplaceBG | calibration | 25 |
| ReplaceBG | train | 100 |
| ReplaceBG | validation | 25 |

Selected subjects contain 374,898 positive carbohydrate rows. Stable event-hash sampling keeps **28,852 candidate origins**, at most 100 per subject, independent of future CGM. The same origins/IDs are used across histories and timing variants.

## Eligible development windows

Primary six-hour totals:

| Split | Eligible windows | IDs with eligible windows |
|---|---:|---:|
| train | 8,973 | 197 |
| validation | 2,000 | 48 |
| calibration | 1,948 | 48 |

Primary timing assumes carbs are available five minutes after their recorded bin. The zero-minute alternative is development-only sensitivity. Each window forecasts 24 five-minute readings from its availability origin, not a proven exact physical meal start. Each cell below is eligible events / IDs with at least one eligible event.

| Split / source | 2 h | 6 h | 12 h | 24 h |
|---|---:|---:|---:|---:|
| calibration:Loop | 1,118 / 24 | 1,052 / 24 | 972 / 24 | 812 / 24 |
| calibration:ReplaceBG | 962 / 24 | 896 / 24 | 803 / 24 | 676 / 24 |
| train:Loop | 4,824 / 99 | 4,555 / 99 | 4,129 / 99 | 3,556 / 99 |
| train:ReplaceBG | 4,716 / 98 | 4,418 / 98 | 3,990 / 98 | 3,238 / 98 |
| validation:Loop | 1,148 / 25 | 1,091 / 25 | 1,008 / 25 | 857 / 25 |
| validation:ReplaceBG | 982 / 23 | 909 / 23 | 829 / 23 | 657 / 23 |

Zero-minute timing sensitivity:

| Split / source | 2 h | 6 h | 12 h | 24 h |
|---|---:|---:|---:|---:|
| calibration:Loop | 1,145 | 1,076 | 994 | 831 |
| calibration:ReplaceBG | 971 | 907 | 809 | 680 |
| train:Loop | 4,925 | 4,654 | 4,212 | 3,635 |
| train:ReplaceBG | 4,756 | 4,459 | 4,028 | 3,263 |
| validation:Loop | 1,168 | 1,107 | 1,023 | 869 |
| validation:ReplaceBG | 990 | 915 | 833 | 660 |

## Exclusions and source quality

History uses exact relative grids; up to 10 minutes of last-past-value fill is allowed with at least 90% positive finite source readings on the requested history grid. No interpolation uses later CGM. Every target must contain 24 finite positive exact-grid source values; targets are not imputed. Extreme positive values are retained; no outcome clipping or error-based deletion. Record-present cannot certify raw sensor observation or recover upstream harmonization.

A positive carb entry within the previous 15 minutes, or any later entry through forecast end, rejects the window. Identical carb amounts are not arbitrarily merged. This defines a **retrospectively isolated logged-meal benchmark**; future-meal exclusion is not a live forecast capability. Scores later obtained on this set must not be presented as performance on all real-world meals.

| Primary variant | Rejection reason | Candidate origins |
|---|---|---:|
| 12h_delay5 | clustered_meal | 1,343 |
| 12h_delay5 | follow_up_meal | 7,479 |
| 12h_delay5 | incomplete_history | 6,881 |
| 12h_delay5 | incomplete_target | 1,418 |
| 24h_delay5 | clustered_meal | 1,343 |
| 24h_delay5 | follow_up_meal | 7,479 |
| 24h_delay5 | incomplete_history | 9,183 |
| 24h_delay5 | incomplete_target | 1,051 |
| 2h_delay5 | clustered_meal | 1,343 |
| 2h_delay5 | follow_up_meal | 7,479 |
| 2h_delay5 | incomplete_history | 4,487 |
| 2h_delay5 | incomplete_target | 1,793 |
| 6h_delay5 | clustered_meal | 1,343 |
| 6h_delay5 | follow_up_meal | 7,479 |
| 6h_delay5 | incomplete_history | 5,480 |
| 6h_delay5 | incomplete_target | 1,629 |

Exact varied six-hour CGM fingerprints checked: 1,474,695; duplicate-candidate IDs quarantined: 0. All selected IDs sharing a fingerprint are excluded, independent of split. Checks are partial and exact, require at least 20 distinct readings/range 20 mg/dL, and cannot prove distinct people across studies. Full subject-quality records stay ignored.

Quality-status counts: `{"ready": 300}`.
Here ready means the projected subject passed structural processing; it does not mean a candidate passed meal-window eligibility. Compare eligible IDs with selected quotas above; subjects with no eligible windows were not replaced.

## Reserved testing and untouched values

Primary reserved test: **104 source-qualified IDs** from publisher test, absent from all publisher-training identities in the same study. Source test: **65 PEDAP IDs** across its publisher files, excluded from all development. PEDAP is a pediatric source shift and will be reported separately. Hidden aliases remain possible until further provenance checks.

**Eligible test-event counts are deliberately not computed yet.** Only source/ID/date/publisher flags were projected from test, and no PEDAP values were included in the development projection. Future test construction/scoring needs frozen model/history/preprocessing selection; reuse the fixed window policy and candidate cap, report all eligibility/failures, and do not tune against those outcomes.

AZT1D/UOM copies, OhioT1DM and the other nonpilot sources are outside development. OhioT1DM remains pending current terms confirmation. BrisT1D/CTR3 merged insulin and IOBP2 all-insulin-as-bolus are not silently substituted into conventional bolus inputs.

## Frozen artifacts and reproduction

Ignored output: `artifacts/evaluation-results/metabonet-phase2-v1/`. It includes the subject manifest, all predeclared assignments/quotas, subject quality/exclusion records, compressed window records, sorted development projection, summary and code snapshot. The frozen protocol hashes every retained artifact; a separate SHA-256 file protects the protocol itself. The build refuses an existing final directory. It uses a separate staging directory and publishes only after preparation checks. Corrupted data fails verification; the development iterator rejects reserved test split names. Before yielding records it checks protocol, split-quality metadata and window hashes. The final consumer guard and verification-before-publication ordering were added after the real run; its executed source snapshot remains unchanged. Real artifacts passed post-publication verification and the final verifier; no policy/window changed. The report generator verifies frozen artifacts first.

```powershell
uv sync --all-groups
uv run --no-sync python -m research.pipelines.prepare_metabonet
uv run --no-sync python -m research.pipelines.prepare_metabonet --verify-only
uv run --no-sync python -m research.pipelines.report_metabonet_preparation
```

Do not rerun preparation into the completed directory. Use verify-only; a changed scientific policy needs a new version/output, not overwriting the frozen evidence. Downloaded data, dictionary HTML/resources, projections, windows and all IDs/times remain ignored and excluded from Graphify. No app DB/schema/frontend/model changed.

Preparation elapsed: 4.69 minutes. Two query threads, 2GB query memory budget, one streaming reader thread. Input identity:

| File | SHA-256 |
|---|---|
| test.parquet | `479b8a614eb3967ea2519e0947906a492a89bdd94de195618328b40664a7aa7c` |
| train.parquet | `2a6a3478d0f3f17b660ec88171af1113ff68d422d8ac1e5de325b12e6886dc3a` |

Synthetic acceptance/integration tests cover causal fill, target separation, units, fractional carbs, fixed-offset cadence, nearby meals, deterministic/source-qualified splits, stable event IDs, exact fingerprints, metadata-only reserved testing (fixture test has no numeric outcome columns), replay protection and artifact corruption. Final regression/integrity evidence is in the [Phase 2 handoff](../tooling/metabonet-phase2-handoff-2026-10-16.md).

## Next stage

Phase 3 runs frozen inference on this validation data, comparing histories on matched events and reporting all eligible/failure counts. Training/calibration/test roles remain fixed. The six-hour UOM choice is a candidate, not a guaranteed optimum here. Small-model training and Chronos corrections follow validation design; no gain toward +/-10 or clinical accuracy can be claimed from successful data preparation.

Protocol: [planning document 12](../planning/GlycoLens_12_MetaboNet_Experiment.md). Prerequisites: [intake audit](metabonet-intake-audit-2026-10-16.md), [dictionary review](metabonet-dictionary-review-2026-10-16.md).
