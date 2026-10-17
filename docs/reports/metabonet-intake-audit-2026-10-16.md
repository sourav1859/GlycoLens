# MetaboNet intake audit - October 16, 2026

**Both downloads are readable and sufficient for pipeline preparation. No model was trained and no test glucose, carbohydrate or insulin values were read or scored.** Do not train blindly on the supplied split: prior cohorts, reused IDs, mixed temporal holdouts and variable feature availability need explicit controls.

## Release, files and scope

The user supplied train.parquet and test.parquet and a portal screenshot showing **v1.2, released October 5, 2026**. The screenshot reports five SIESTA participants added to training only. Local metadata confirms five training SIESTA IDs and none in test. Version attribution is screenshot-based; there is no dataset release identifier or publisher checksum embedded in the files. Arrow 22.0.0 is the file writer version, not the MetaboNet version. Hashes identify these exact local bytes.

| File | Bytes | Rows from footer | Columns | SHA-256 |
|---|---:|---:|---:|---|
| train.parquet | 1,278,078,013 | 132,811,004 | 37 | `2a6a3478d0f3f17b660ec88171af1113ff68d422d8ac1e5de325b12e6886dc3a` |
| test.parquet | 275,327,014 | 22,069,548 | 37 | `479b8a614eb3967ea2519e0947906a492a89bdd94de195618328b40664a7aa7c` |

Schemas match in names and types: **True**. Core columns include CGM, date, id, source_file, carbs, bolus, basal, insulin and split flags. Detailed protein/fat/fibre fields are absent.

Only source/subject/date/split fields were projected from test. Training profiles read the core numeric channels; free-text notes, demographics and device identifiers were not read. File hashes stream opaque bytes without interpreting test outcomes. Parquet footer metadata was inspected, not outcome statistics.

## Training sources and meal suitability

| Source | Study-participant IDs | Rows | Finite CGM | Positive carb rows | Missing/nonfinite carbs | Missing/nonfinite bolus |
|---|---:|---:|---:|---:|---:|---:|
| AZT1D | 21 | 241,871 | 98.11% | 3,742 | 93.25% | 93.25% |
| BrisT1D | 18 | 973,326 | 74.66% | 15,042 | 98.45% | 100.00% |
| CTR3 | 30 | 1,962,436 | 56.85% | 11,635 | 99.41% | 100.00% |
| DCLP3 | 101 | 5,175,028 | 93.44% | 0 | 100.00% | 0.12% |
| DCLP5 | 90 | 5,243,288 | 89.58% | 0 | 100.00% | 3.50% |
| FLAIR | 102 | 5,977,590 | 78.77% | 0 | 100.00% | 0.13% |
| HUPA-UCM | 20 | 207,022 | 100.00% | 1,863 | 99.10% | 98.68% |
| IOBP2 | 299 | 8,278,133 | 80.35% | 0 | 100.00% | 12.42% |
| Loop | 761 | 80,989,684 | 88.75% | 1,128,317 | 16.99% | 10.80% |
| OhioT1DM | 12 | 190,966 | 87.21% | 2,160 | 6.07% | 1.44% |
| PEDAP | 59 | 4,699,920 | 91.27% | 90,376 | 0.17% | 0.11% |
| ReplaceBG | 188 | 18,139,804 | 63.67% | 182,681 | 12.28% | 6.59% |
| SIESTA | 5 | 38,475 | 96.89% | 0 | 100.00% | 0.00% |
| ShanghaiT1DM | 11 | 41,666 | 33.35% | 0 | 100.00% | 98.94% |
| T1D-UOM | 13 | 651,795 | 36.34% | 3,197 | 99.50% | 99.34% |

Positive carbohydrate rows are recorded entries, **not** counts of eligible independent meal windows. Window eligibility still needs history/target-gap and later-meal checks. Missing sparse-event values cannot automatically mean a confirmed absence of meals or insulin. Full-nutrient claims cannot be validated from this schema.

The carbohydrate-bearing new sources include Loop, ReplaceBG, PEDAP, CTR3, HUPA-UCM and BrisT1D. BrisT1D and CTR3 lack separate basal/bolus in these training files, despite having merged insulin. DCLP3/5, FLAIR, IOBP2, SIESTA and Shanghai have no recorded carbohydrate values here: useful for a separately labelled CGM/insulin experiment, not directly for identifying the primary meal-centred examples. Loop dominates the row count; sampling/weighting must not allow it to define the whole benchmark.

## Identity and split findings

- 1,730 training and 351 study-participant combinations. These are source-qualified identifiers, not a verified count of distinct people across studies.
- **169** combinations occur in both files; **182** test combinations are absent from training before cohort/terms exclusions.
- 222 bare IDs are reused across training cohorts. Always namespace by source; matching a bare ID can create false overlaps.
- 166 shared combinations are marked shared in both files; the remaining observed overlaps require explicit identity checks, rather than relying on the flag alone.
- 164 shared combinations have a zero-to-five-minute boundary gap; 5 have interleaved or reversed time ranges. None has a full 24-hour forward range gap.
- Exact source/ID/timestamp keys shared across files: 0. Overlapping date ranges are not proof of duplicated rows. However, sliding two-hour targets near a five-minute split can cross the boundary without purging.
- Both files have consistent row-level is_test flags and no missing test IDs/timestamps. Do not describe the whole supplied test as an unseen-person or unseen-study test.

The initial exploratory mapping left CTR3 and ReplaceBG combined as unresolved. The final mapping separates them using published source names, changing the provisional 172 overlap count to 169. All final figures use source-qualified identities. Cohort matching was initially heuristic; a subsequent saved-dictionary review confirmed all 15 actual training source labels. Cross-source aliases/shared people still need provenance and trajectory checks.

## Grid and source-quality findings

Training excess duplicate source/ID/timestamp rows: 0. Off-wall-clock five-minute-grid keys: 38,475.

All 38,470 within-SIESTA intervals are exactly five minutes; each of its five subjects has a fixed timestamp offset. Off-wall-clock-grid does not mean irregular cadence. Preserve the valid relative grid or document a causal alignment rule; do not discard this cohort just because timestamps are not divisible by five minutes.

## Terms and documentation still needed

At initial intake only the two Parquet files were present. The user subsequently saved the complete dictionary; all 37 local fields and 15 training source labels were checked. It confirms glucose/insulin/carbohydrate units, trailing-five-minute insulin amounts and flag definitions, with source-specific exceptions. See the [dictionary review](metabonet-dictionary-review-2026-10-16.md). Current use terms/README and exact carb availability/bin conventions remain unresolved. Preparation can continue.

OhioT1DM appears in training (12 source-qualified IDs). The August 2026 publication lists it as DUA-governed, while this public download includes it. This is a terms question, not a finding that the download was improper. Quarantine that source from training until the current included-use rights are confirmed; proceed with other documented sources. The entire aggregate release must not be assumed CC BY 4.0.

## Recommended next steps

1. Freeze an intake manifest with these hashes/version evidence, source mapping and per-source terms. Exclude AZT1D/UOM copies from new development; leave unresolved sources and OhioT1DM out pending confirmation. Preserve the original research artifacts.
2. Build a streaming shared-feature loader and source-qualified meal-window manifest. Audit event-bin timing before claiming inputs are known at forecast origin. Retain missingness, avoid adding total insulin to basal+bolus, and apply causal CGM gap rules. Report eligible meals/participants rather than raw-row counts.
3. Freeze a new protocol: training-only subject-aware validation/calibration; purge two-hour targets across boundaries; reserve only genuinely test-only participants for the primary supplied-file test. Retain a separately withheld source where feasible. Do not retune against consumed AZT1D or the earlier UOM test.
4. Run a balanced CPU pilot, provisionally 100–200 training participants before scaling, with caps per participant/study. Compare persistence, direct Ridge/LightGBM, frozen Chronos and a residual head on matched events. Use the existing two-hour metrics, inclusive ±10 rates, tails, failures and calibration. Consider small-network/LoRA work only after development evidence justifies it; no GPU/API key is needed for the initial pilot.

These are proposed next steps; no MetaboNet training/model selection/test prediction has occurred. More data improves the experiment design, not a guarantee of ±10 accuracy.

## Reproduction and checks

Install the pinned data-audit dependency group along with existing groups. Run `python -m research.pipelines.audit_metabonet --release-version v1.2`, then `python -m research.pipelines.report_metabonet_audit`. Full aggregate JSON and scratch data stay in ignored artifacts/evaluation-results/metabonet-audit/. Raw downloads stay ignored. Source queries project only metadata from test; no model code or app database changed. Synthetic fixtures cover poisoned test outcome values, reused IDs across sources, fixed-offset cadence, duplicates and truncated footers.

Audit runtime: 99.28 seconds, duckdb 1.4.4, two CPU threads, 2GB query memory budget and ignored spill directory.

Primary reference: [MetaboNet publication, methods/data-format/source table](https://arxiv.org/html/2601.11505v2). Its described benchmark is 30-minute forecasting and uses mixed temporal/subject splits; it is not a promise for this two-hour task. File-specific counts above are observed locally, not copied from the publication. Release 1.2 details come from the user-provided screenshot.
