# Milestone 1 T1D-UOM Data Pipeline Implementation

**Date:** September 28, 2026

**Scope:** Dataset provenance, aggregate audit, and first model-ready meal-window pipeline

**Status:** Implemented and verified; Phase 3 pretrained-model smoke also passed

## Objective

Establish the first executable Milestone 1 feasibility path:

```text
T1D-UOM V1.0.4
-> validated core modalities
-> leakage-safe meal event
-> 24-point pre-meal CGM context
-> pre-meal insulin and meal nutrition
-> separate 24-point future CGM target
```

This slice does not train a model, make treatment recommendations, or persist row-level health data.

## Acceptance criteria

| Requirement | Evidence | Result |
|---|---|---|
| Pin the official V1.0.4 release | DOI, release commit, and extracted suffix validation | Passed |
| Audit CGM, meals, basal, and bolus | Aggregate audit command | Passed |
| Generate a two-hour history and target | 24 history and 24 target points at five-minute frequency | Passed |
| Include only insulin available by meal time | Boundary test and required pre-meal insulin context | Passed |
| Prevent post-meal leakage | Strict timestamp assertions | Passed |
| Reject a second meal in the target horizon | Synthetic regression test | Passed |
| Fail closed on long CGM gaps | Synthetic regression test | Passed |
| Avoid committing health data | Synthetic tests and aggregate-only CLI output | Passed |

## Implementation plan and delivered files

1. Pin release provenance in `data/schemas/t1d_uom_v1_0_4.md`.
2. Implement schema validation, aggregate audit, loaders, unit conversion, duplicate handling, and window construction in `research/datasets/t1d_uom.py`.
3. Add privacy-safe CLI commands under `research/pipelines/`.
4. Add deterministic synthetic tests in `tests/research/test_t1d_uom.py`.
5. Run the audit and eligibility scan against the local V1.0.4 extraction.
6. Synchronize planning and repository documentation.

## Reproducible commands

Configure the local extraction without committing its path or contents:

```powershell
$env:GLYCOLENS_T1D_UOM_ROOT = 'C:\path\to\sharpic-ManchesterCSCoordinatedDiabetesStudy-ea52718'
python -m research.pipelines.audit_t1d_uom
python -m research.pipelines.build_meal_windows --limit 1
python -m unittest tests.research.test_t1d_uom -v
```

To count all eligible windows under the default Milestone 1 policy:

```powershell
python -m research.pipelines.build_meal_windows --limit 100000
```

## Aggregate findings

The core-modality audit covered 62 CSV files and 386,564 rows:

| Modality | Files | Rows |
|---|---:|---:|
| CGM | 17 | 356,146 |
| Nutrition | 15 | 4,351 |
| Bolus insulin | 16 | 5,660 |
| Basal insulin | 14 | 20,407 |

- 15 participants contain CGM, nutrition, and at least one insulin modality.
- 13 participants contain all four audited modalities.
- All audited timestamp strings parse under the corrected day-first rule, but four nutrition rows contain only a date and are excluded because they lack meal-time precision.
- No non-finite or malformed numeric values were detected.
- 844 rows have at least one blank required field: 652 nutrition rows and 192 bolus rows.
- 16,099 additional rows repeat a timestamp: 15,915 CGM, 113 bolus, 55 basal, and 16 nutrition.
- 253 CGM timestamp groups contain conflicting values. These timestamps are excluded rather than averaged.
- The source values are day-first even though the upstream README labels them month-first. This was the most consequential audit finding because ambiguous dates could otherwise parse without an error but map to the wrong month and day.

Under the default window policy—two-hour history, two-hour target, five-minute grid, no second meal in the horizon, and at least one insulin event during the previous six hours—the pipeline evaluated 3,884 valid loaded meals and produced 927 eligible windows.

First-failure rejection counts were:

| Reason | Count |
|---|---:|
| Follow-up meal inside horizon | 771 |
| Incomplete CGM history | 1,281 |
| Incomplete future CGM target | 451 |
| Missing six-hour insulin context | 454 |

These categories are sequential first-failure reasons, not independent prevalence estimates.

## Test traceability

| Requirement or risk | Scenario | Layer | Fixture | Evidence |
|---|---|---|---|---|
| Timestamp ambiguity | Ambiguous date parses day-first | Unit | Synthetic | `test_ambiguous_source_date_is_parsed_day_first` |
| Schema drift | Required column is absent | Unit | Synthetic | `test_missing_required_column_fails_validation` |
| Temporal leakage | History is at/before meal; target is after | Unit | Synthetic | `test_window_has_strict_temporal_boundary_and_expected_shape` |
| Future insulin leakage | Only post-meal insulin exists | Unit | Synthetic | `test_future_insulin_does_not_satisfy_required_context` |
| Confounding meal | Another meal occurs inside two hours | Unit | Synthetic | `test_follow_up_meal_inside_horizon_is_rejected` |
| Unsafe interpolation | Target contains a gap over 15 minutes | Unit | Synthetic | `test_long_target_gap_is_rejected` |
| Conflicting CGM duplicates | Same timestamp has different glucose values | Unit | Synthetic | `test_conflicting_duplicate_cgm_timestamp_is_excluded` |
| Multi-row meal logging | Two components share one meal timestamp | Unit | Synthetic | `test_same_timestamp_nutrition_components_are_aggregated` |
| Insufficient meal time | Nutrition row contains a date only | Unit | Synthetic | `test_date_only_meal_is_audited_and_excluded` |
| Audit completeness | Core modalities and rows are counted | Unit | Synthetic | `test_audit_reports_core_participant_and_rows` |

## Verification record

| Check | Result |
|---|---|
| `python -m unittest discover -v` | Passed: 10 tests |
| `python -m compileall -q research tests` | Passed |
| `python scripts/quality/validate_skills.py` | Passed: 9 skills, 0 failures |
| Real V1.0.4 aggregate audit | Passed |
| Full eligibility scan | Passed: 927 windows |
| `git diff --check` | Passed |
| Credential-marker and absolute-local-path scans | Passed |
| Graphify refresh | Passed with Graphify 0.9.69 in code-only mode; semantic documentation extraction remained disabled |

No project formatter, linter, or type checker is configured yet, so those verification layers were not applicable to this standard-library-only slice.

## Limitations and next action

- Timestamps remain timezone-naive because the source release lacks explicit offsets.
- Eligibility rules are an initial feasibility policy and must be sensitivity-tested rather than treated as ground truth.
- Insulin events are aligned and converted into model-independent covariate series; model-specific
  tensor transformation remains adapter work.
- The pinned Chronos-2 checkpoint now runs through the common contract on one eligible CGM-only
  context; this proves technical feasibility but not forecast accuracy.

The common forecast contract and persistence baseline were completed in Phase 2. Phase 3 then
completed a pinned Chronos-2 24-point CPU smoke test. See
`docs/reports/milestone-1-phase-3-chronos2-smoke.md` for runtime, memory, and safety evidence.
Phase 4 added the typed synthetic API, accessible browser forecast chart, and ignored real-model
research graph; see `docs/reports/milestone-1-phase-4-api-visualization.md`.
Phases 5 and 6 then completed the executable local database and deterministic py-mgipsim
feasibility path. The RIT-branded presentation and final closure audit complete Milestone 1; see
`docs/reports/milestone-1-closure-audit.md`.
