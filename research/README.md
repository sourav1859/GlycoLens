# Research Pipeline

This area will contain reproducible preprocessing, model-comparison, context-ablation, context-length, retrieval-personalization, and evaluation workflows.

Downloaded datasets and derived health-data files belong under `data/` and are excluded from Git. Commit code, small sanitized fixtures, configurations, and aggregate non-sensitive results only.

## Implemented Milestone 1 slice

The repository includes a dependency-free T1D-UOM V1.0.4 adapter, aggregate audit, meal-window
generator, common forecast contract, persistence baseline, pinned Chronos-2 CPU adapter, and an
isolated pinned py-mgipsim virtual-patient feasibility scenario.
Configure
`GLYCOLENS_T1D_UOM_ROOT`; do not copy or commit the downloaded dataset unless it remains inside an
ignored raw-data directory.

```powershell
python -m research.pipelines.audit_t1d_uom
python -m research.pipelines.build_meal_windows --limit 1
uv run python -m research.pipelines.run_persistence_baseline
uv run --all-groups python -m research.pipelines.run_chronos2_smoke --allow-model-download
./scripts/simulation/Install-PyMgipsim.ps1
uv run python -m research.pipelines.run_pymgipsim_scenario --allow-upstream-execution
```

The persistence command converts one real eligible window while keeping future CGM in a separate
evaluation target. Its output is aggregate and contains no participant ID, timestamp, glucose
value, or held-out target value.

The Chronos-2 smoke command runs the C0/CGM-only path, requires explicit checkpoint-download
consent, and writes timing/memory evidence under ignored `artifacts/benchmarks/`. M2 adds
tested recorded-event C0-C3 covariate alignment; see ADR 0008 and the original M2 results.

The simulator command runs one fixed synthetic ExtHovorka/OpenLoop day and writes a validated
relative-time trajectory under ignored `artifacts/simulation/`. It is not a clinical result and
does not expose individual insulin values or dose guidance.

## Approved model refinement

The user approved the local refinement study on October 16. Follow the frozen rules in
[planning document 11](../docs/planning/GlycoLens_11_Model_Refinement.md) and
[ADR 0010](../docs/decisions/0010-model-refinement-and-external-test-boundary.md).
It requires the original M2 validation/test artifacts and locally cached pinned Chronos
weights. Set the private dataset path without placing secrets or downloaded records in Git.

```powershell
uv sync --group chronos --group timesfm --group plotting --group refinement
# Downloads the public ~776 MB V1 archive, verifies checksum/size, extracts only CSVs.
uv run --no-sync python -m research.pipelines.acquire_azt1d
# Explicit path to the directory containing Glucose Data, Nutrition Data and Insulin Data:
uv run --no-sync python -m research.pipelines.run_refinement --uom-root $env:GLYCOLENS_T1D_UOM_ROOT
uv run --no-sync python -m research.pipelines.report_refinement
# Audit a completed run without reselecting or scoring external data again:
uv run --no-sync python -m research.pipelines.verify_refinement --uom-root $env:GLYCOLENS_T1D_UOM_ROOT
```

`--skip-external` permits development-only execution. The default study writes an immutable
selection before AZT1D predictions. A frozen output directory refuses replay before
any artifact writes; use the verification command on the completed run. It refuses
to replace a different frozen selection;
do not delete that guard to retune against consumed external results. A new protocol/test
is needed for later tuning. Offline Chronos inference uses two CPU threads and a pinned
checkpoint. No API key, GPU or paid service is required for this study.

Samples/requests are constructed in memory. Row-level predictions, source hashes and
trusted-local joblib estimator states are written only under ignored
`artifacts/evaluation-results/refinement-v1/`. Downloaded AZT1D stays
under ignored `data/raw/azt1d-v1/`. Never load joblib from an untrusted source. Saved state
contains scaler, regressor, interval radius, feature version and backbone requirements;
reattach the exact pinned C0 backbone for residual predictions. These are research artifacts,
not a new production model registry. The public report contains aggregates only.

The runner preserves the original 927-event manifest, subdivides development into training
and calibration, retains all attempted prediction failures and distinguishes shared from
full-nutrient inputs. The original test is now diagnostic. AZT1D lacks the full nutrition
fields and cannot validate protein/fat/fibre effects. +/-10 mg/dL is an aspirational tolerance,
not a guarantee. See [the execution report](../docs/reports/model-refinement-results-2026-10-16.md).

## MetaboNet intake audit

The user supplied v1.2 train/test Parquet files under ignored `data/raw/metabonet/`.
The audit profiles training values and explicitly projects only provenance/split/date
metadata from test. It does not train, forecast or profile test outcomes. It namespaces
IDs by source, checks temporal overlaps and duplicates, and reports core-field coverage.

```powershell
uv sync --all-groups
uv run --no-sync python -m research.pipelines.audit_metabonet --release-version v1.2
uv run --no-sync python -m research.pipelines.report_metabonet_audit
uv run --no-sync pytest -q tests/research/test_metabonet_audit.py
```

`data-audit` pins DuckDB1.4.4; queries use two threads, 2GB memory and ignored scratch.
`--skip-duplicate-audit` omits only the expensive training-key group, not split checks.
Full aggregate JSON stays ignored; the public
[intake report](../docs/reports/metabonet-intake-audit-2026-10-16.md) contains no patient
IDs/timestamps/free text. Local checksums identify exact files; portal v1.2 attribution
is user screenshot evidence. The schema writer version is not the release version.
The subsequently saved dictionary covers all 37 fields and confirms all 15 training
source labels. See the [review](../docs/reports/metabonet-dictionary-review-2026-10-16.md).
Insulin fields are previous-five-minute IU amounts, not hourly rates; IOBP2 records
all insulin as bolus. Preserve source-specific missingness, ambiguous timezone handling
and source-qualified identity. Current use terms and precise carb availability/bin
conventions remain unresolved. Exclude AZT1D/UOM
copies from new development; quarantine OhioT1DM pending current terms confirmation.
Proposed next experiments need explicit source mapping, causal interval semantics,
subject-qualified splits and two-hour target purging before training. The old frozen
study/consumed AZT1D test must not be overwritten or relabelled untouched.

## MetaboNet Phase 2 preparation

Implemented and executed under [protocol 12](../docs/planning/GlycoLens_12_MetaboNet_Experiment.md)
and [ADR 0011](../docs/decisions/0011-metabonet-development-and-reserved-tests.md).
The default bounded CPU pilot uses Loop/ReplaceBG, subject-disjoint 200/50/50
metadata quotas, at most 100 deterministic candidate meals each, and histories of
2/6/12/24 hours. Five-minute delayed carb availability is primary; zero is a
development sensitivity. Preserve unknown event values and masks; history fill is
causal and short, targets complete. Isolated-meal eligibility is retrospective.

```powershell
uv sync --all-groups
# One fresh build only; first run requires matching audited files/dictionary.
uv run --no-sync python -m research.pipelines.prepare_metabonet
# Existing completed output: verify it, do not rerun preparation.
uv run --no-sync python -m research.pipelines.prepare_metabonet --verify-only
uv run --no-sync python -m research.pipelines.report_metabonet_preparation
uv run --no-sync pytest -q tests/research/test_metabonet_preparation.py
```

Default output is ignored `artifacts/evaluation-results/metabonet-phase2-v1/`.
The frozen protocol hashes artifacts and executed sources; a source ZIP preserves
the real build. Do not edit/overwrite completed output. The later read-integrity
and pre-publication checks leave that original snapshot unchanged; no policy/window
changed. Real artifacts passed both the build and final verifier. For a changed scientific policy,
create a separately versioned protocol/output and document the change.

Six-hour eligible windows: **8,973 train / 2,000 validation / 1,948 calibration**,
on 197/48/48 usable identities. The development iterator rejects reserved-test roles,
verifies protocol/split metadata/window hashes, and yields records convertible with
`window_to_example` to CGM-only or shared-context immutable requests plus separate
targets. No app database use. The 104 primary-test and 65 PEDAP source-test identities
are metadata reservations only; their event eligibility waits until selection freezes.
No training/inference in this stage. [Full results and exclusions](../docs/reports/metabonet-phase2-preparation-2026-10-16.md).

## MetaboNet Phase 3 frozen inference

Follow [protocol 13](../docs/planning/GlycoLens_13_MetaboNet_Frozen_Inference.md).
This experiment consumes prepared validation only, at five-minute carb availability.
It compares persistence, four CGM histories and two fixed six-hour recorded-context
variants on 1,509 matched events. The common Chronos adapter/checkpoint stays frozen;
no app model changes, fitting, calibration or reserved-test scoring.

```powershell
uv sync --all-groups
# A fresh run, or resume matching incomplete output without retrying failed forecasts.
uv run --no-sync python -m research.pipelines.run_metabonet_inference
# After completion, only verify; completed runs refuse replay.
uv run --no-sync python -m research.pipelines.run_metabonet_inference --verify-only
uv run --no-sync python -m research.pipelines.report_metabonet_inference
uv run --no-sync pytest -q tests/research/test_metabonet_inference.py
```

Output: ignored `artifacts/evaluation-results/metabonet-phase3-v1/`. Execution-source
ZIP, configuration, environment and checkpoint-file hashes are frozen before inference.
An interrupted run resumes only matching sources/inputs/configuration, request hashes
and checksummed rows. Corrupt progress requires review, not silent deletion. Failure
attempts stay in denominators and are not retried. Only failure-free options can enter
the full matched-cohort selection; all candidates remain in attempted/pairwise tables.
`history-decision.json` is a Phase 4 history choice, not final test/model authorization.

The report documents eligible attrition, comparison populations, native-band coverage,
tails and source subgroups. C1/C2 use recorded amounts/masks, not physiological activity;
total insulin is omitted when basal/bolus are supplied. Conditional isolated logged meals
and unknown reporting latency remain limitations. No +/-10 guarantee follows from ranking.

Executed result: persistence won among failure-free options (macro MAE 37.12 mg/dL;
six-hour C2 37.61); the improvement gate failed. The frozen two-hour C0 history choice
reflects reliability, not the lowest conditional point error. Longer histories improved
conditional accuracy but had native contract failures. Nominal 80% bands undercovered
and negative medians occurred. Phase 4 subsequently assessed longer-history features
through training-only CV while preserving this frozen decision (see below).
See the [full report](../docs/reports/metabonet-phase3-inference-2026-10-16.md) and
[handoff](../docs/tooling/metabonet-phase3-handoff-2026-10-16.md).

## MetaboNet Phase 4 direct training

Follow [protocol 14](../docs/planning/GlycoLens_14_MetaboNet_Direct_Models.md).
The dedicated native-unit/mask feature adapter compares Ridge and pooled-horizon
LightGBM using three subject-separated training folds across a fixed 32-candidate
grid. Histories/profiles/parameters are chosen on training only. Freeze one CV winner
per family, refit all eligible training events at that history, and score the same
1,509 validation meals as Phase 3. Saved baseline forecasts are verified and reused;
Chronos was not rerun or fitted in Phase 4. Calibration and reserved tests were
untouched at that stage; Phase 6 below now records their use.

```powershell
uv sync --all-groups
uv run --no-sync python -m research.pipelines.run_metabonet_training
uv run --no-sync python -m research.pipelines.run_metabonet_training --verify-only
uv run --no-sync python -m research.pipelines.report_metabonet_training
uv run --no-sync pytest -q tests/research/test_metabonet_models.py
```

Output: ignored `artifacts/evaluation-results/metabonet-phase4-v1/`. Executed sources,
environment/configuration/input hashes are frozen before fitting. OOF arrays, fitted
bundles, per-family choices and validation rows are checksummed. Resume requires
matching configuration/sources and intact completed work; corrupt/partial progress
requires review. Completed runs refuse replay. Load only these trusted local models
after hash verification; never deserialize arbitrary downloaded joblib files.

Ridge predicts 24 glucose deltas with train-only imputation/scaling. LightGBM pools
horizons with an explicit horizon feature after subject splitting. Participant weights
are equal in total; source/identity/date are not predictors. Recorded event units and
presence masks are preserved; total insulin is not added to components. Deterministic
quantile placeholders are not calibrated bands. No research result automatically
replaces the app model. See [results](../docs/reports/metabonet-phase4-training-2026-10-16.md)
and [handoff](../docs/tooling/metabonet-phase4-handoff-2026-10-16.md).

Executed result: LightGBM macro MAE 31.17 versus 37.12 persistence (16.03% lower),
within-10 26.84%, research gate passes. Ridge has MAE 31.36 and higher within-10
28.85%; preserve it as a tolerance challenger. Both learned models have worse
whole-curve-within-10 rates than persistence. Accuracy remains poor for +/-10.
At Phase 4 completion there were no calibrated bands/reserved-test results; Phase 6 below now records both.

The first execution completed all fits, then hit a NumPy-scalar scoring error before
its first persisted scored row. The tested conversion fix was applied through an
audited scoring-only completion command:
`python -m research.pipelines.complete_metabonet_training`. It verifies the original
source archive, all CV choices and both model hashes, requires that only the numeric
conversion line changed, archives its own execution and never fits a model. The
original zero-row file is retained. Both archives are covered by completion hashes;
the normal `--verify-only` command validates final output. This repair command is
specific to this interrupted run, not a way to bypass source freezes or rerun a
completed experiment. No model/feature/parameter change or outcome-based retry.

## MetaboNet Phase 5 Chronos correction

Follow [protocol 15](../docs/planning/GlycoLens_15_MetaboNet_Chronos_Correction.md).
First cache frozen six-hour C2 forecasts on the 6,756 common training meals. Persist
every attempt; never retry failed native forecasts. Then compare four fixed small
correction configurations with two fixed direct controls using the same usable
training meals, subject folds and participant weights. Freeze correction CV choices
and all refits before validation. Reuse the original 1,509-event validation C2
forecasts and Phase 3/4 baselines; no new validation Chronos calls.

```powershell
uv sync --all-groups
uv run --no-sync python -m research.pipelines.cache_metabonet_backbone
uv run --no-sync python -m research.pipelines.cache_metabonet_backbone --verify-only
uv run --no-sync python -m research.pipelines.run_metabonet_correction
uv run --no-sync python -m research.pipelines.run_metabonet_correction --verify-only
uv run --no-sync python -m research.pipelines.report_metabonet_correction
uv run --no-sync pytest -q tests/research/test_metabonet_correction.py
```

Output: ignored `artifacts/evaluation-results/metabonet-phase5-v1/`, separate
`backbone/` and `heads/` source/configuration freezes and a root completion manifest.
Completed stages refuse replay. An interrupted stage resumes only matching sources,
inputs and checksummed outputs. Labels are absent from the training forecast cache.
Saved small heads contain no live foundation model; verify local bytes before load.

Correction features combine 24-hour glucose/six-hour events with 24 frozen C2
changes. Train-only transformations and whole-subject splitting precede horizon
expansion. The fixed advancement gate requires at least 5% lower macro MAE than
Phase 4 LightGBM with no lower within-10, no worse p95 and no failures. Rank point
accuracy separately; retain the incumbent if no correction passes. Direct controls
isolate training-population effects. Placeholder quantiles are not calibrated bands.
Calibration/reserved tests and application inference remain separate.

**Phase 5 was complete before the Phase 6 evaluation recorded below.** Frozen C2
generated 6,756 training forecasts; 6,756 usable meals / 196 identities supported six CV
configurations / 18 fold fits and four final refits, with exactly matched direct
controls. Neither correction passed the predeclared incremental gate; retain Phase 4
LightGBM. Lowest-MAE eligible option: `ridge_residual_1000`; advancement candidate:
`lightgbm_direct` (macro MAE 31.17 mg/dL, within +/-10 26.84%). These are
reused-validation findings, not independent confirmation. At Phase 5 completion, calibration/reserved outcomes were untouched.
Phase 6 below supersedes that access status; app inference remains unchanged.
See [results](../docs/reports/metabonet-phase5-correction-2026-10-16.md) and [handoff](../docs/tooling/metabonet-phase5-handoff-2026-10-16.md).

## MetaboNet Phase 6: separate calibration and independent testing

```powershell
.venv/Scripts/python.exe -m research.pipelines.run_metabonet_independent --stage calibration --verify-only
.venv/Scripts/python.exe -m research.pipelines.run_metabonet_independent --stage test --verify-only
.venv/Scripts/python.exe -m research.pipelines.report_metabonet_independent
```

Original execution omitted `--verify-only`, calibration first. Completed stages refuse replay; partial attempts require review. Output is ignored `artifacts/evaluation-results/metabonet-phase6-v1/`. Calibration freezes one hash-selected eligible meal per participant and separate marginal/whole-curve 80% bands; a verified completion gate precedes reserved projection. Point-model state stays unchanged. PEDAP publisher segments stay separate. Model selection is fixed before outcomes.

**The broader-data model-refinement sequence, Phases 1-6, is complete.** Separate calibration used 48 participant representatives from 1,488 eligible meals. Frozen LightGBM scored 29.91 mg/dL macro trajectory MAE / 28.20% within +/-10 on 3,533 primary-test meals (102 IDs), and 40.92 / 19.57% on 2,177 PEDAP meals (64 IDs). Both predeclared point-improvement gates passed, with zero failed forecasts; tight precision remains poor. Nominal 80% marginal coverage was 79.05% primary and 63.94% PEDAP. Both test cohorts are now consumed; no test-based reselection, point refit, app promotion or full-M2 closure.

See [results](../docs/reports/metabonet-phase6-independent-2026-10-16.md) and [handoff](../docs/tooling/metabonet-phase6-handoff-2026-10-16.md).
