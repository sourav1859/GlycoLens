"""Render aggregate Phase 5 findings from verified completed artifacts."""

import json

from research.evaluation.refinement_metrics import percentile
from research.pipelines.cache_metabonet_backbone import OUTPUT
from research.pipelines.prepare_metabonet import ROOT
from research.pipelines.report_metabonet_inference import number, percent
from research.pipelines.run_metabonet_correction import verify_phase5
from research.pipelines.run_metabonet_inference import read_execution


def render_report(summary, cv, execution, backbone_rows):
    primary = summary["selection_summary"]["runs"]
    point = summary["selected_candidate"]
    advance = summary["advancement_candidate"]
    cohort = summary["training_cohort"]
    backbone = summary["backbone_summary"]
    advanced = advance != "lightgbm_direct"
    lines = [
        "# MetaboNet Phase 5 frozen-Chronos correction results - October 16, 2026",
        "",
        "**Phase 5 is complete. Small correction heads and matched direct controls were "
        "trained; foundation weights remained frozen. Calibration and reserved test "
        "outcomes were not accessed. No application model was replaced.**",
        "",
        f"Lowest-MAE failure-free validation option: **{point}** "
        f"({number(primary[point]['participant_macro']['mae'])} mg/dL). "
        f"Candidate retained for the later final comparison: **{advance}**. "
        + (
            "A correction passed the predeclared incremental development gate."
            if advanced
            else "No correction passed the predeclared incremental gate; retain the Phase 4 incumbent."
        ),
        "",
        "The lowest point estimate and the advancement decision are different rules "
        "fixed before fitting. Passing a development gate is not independent or clinical "
        "confirmation, and a small improvement does not establish dependable +/-10 forecasts.",
        "",
        "## Frozen design and actual training population",
        "",
        "The backbone is the pinned six-hour recorded-context C2 Chronos model, the "
        "best failure-free Chronos variant from Phase 3. Its immutable request contains "
        "only origin-known glucose, separate basal/bolus amounts, previous/current carbs "
        "and presence masks. No merged total-insulin double counting. Checkpoint files "
        "and source/configuration hashes were frozen before calls and verified unchanged.",
        "",
        f"Training backbone attempts: **{backbone['attempts']:,}**; successes "
        f"**{backbone['successes']:,}**. Failure types: "
        f"`{json.dumps(backbone['failures'], sort_keys=True)}`; underlying causes "
        f"`{json.dumps(backbone['failure_causes'], sort_keys=True)}`. Every attempt was "
        "persisted and failed forecasts were not retried or repaired. Raw failed "
        "quantiles were not retained, so cause types do not identify individual invalid values.",
        "",
        f"The original common pool was **{cohort['original_events']:,} meals / "
        f"{cohort['original_subjects']} identities**; usable head/control training was "
        f"**{cohort['usable_events']:,} meals / {cohort['usable_subjects']} identities**. "
        f"Backbone failures excluded **{cohort['excluded_backbone_failures']} training "
        "meals** because their residual labels cannot be defined, not because of "
        "observed errors. All four final models use exactly the same usable events. "
        "Original Phase 4 models used 6,794 meals; matched controls isolate that change.",
        "",
        "Source counts: "
        + ", ".join(f"{k}: {v:,}" for k, v in sorted(cohort["sources"].items()))
        + ".",
        "",
        "The same three whole-subject folds from Phase 4 are used. Fit-fold participant "
        "weights give each identity equal total weight. Transformations use fit-fold "
        "data only. Horizon expansion occurs after splitting. No source, identity or "
        "absolute-time predictor. Validation is read only after training-CV choices "
        "and final model bundles are frozen; no validation early stopping or new history search.",
        "",
        "Correction heads add 24 frozen C2 median changes to the original 127 request "
        "features (24-hour glucose / six-hour recorded events). These future predictions "
        "are not future observations. Ridge fits 24 residual outputs with median "
        "imputation/weighted scaling; LightGBM fits pooled horizons with the unchanged "
        "160-tree/.04-rate/min-child100/max-bin63/lambda1/two-thread budget. Head "
        "weights are saved without a live Chronos model. Corrected quantiles are "
        "deterministic placeholders, not the uncorrected native bands.",
        "",
        "## Training-only cross-validation and refits",
        "",
        "Four correction candidates (two parameters per family), plus two fixed "
        "Phase 4 direct controls, each have three subject folds. Select one correction "
        "per family by OOF macro MAE, tie higher within-10 then stable name. Failed "
        "candidates cannot win. Controls are not retuned. Refit the same usable pool.",
        "",
        "| Candidate | OOF macro MAE | OOF within +/-10 | Failed folds |",
        "|---|---:|---:|---:|",
    ]
    for item in cv["candidates"]:
        lines.append(
            f"| {item['name']} | {number(item['macro_mae'])} | {percent(item['within_10'])} | {item['failure_count']} |"
        )
    lines += [
        "",
        "| Final model | Training meals | Identities | Origin features | Reload equivalent |",
        "|---|---:|---:|---:|---|",
    ]
    for name, item in summary["fit_metadata"].items():
        lines.append(
            f"| {name} | {item['training_events']:,} | {item['training_subjects']} | {item['feature_count']} | {item['reload_prediction_equivalent']} |"
        )
    lines += [
        "",
        "## Primary validation: same 1,509 meals / 48 identities",
        "",
        "Feature counts above describe origin inputs; pooled LightGBM adds one "
        "horizon-fraction column after the subject split.",
        "",
        "Seven original Phase 3 runs, two original Phase 4 direct models, two chosen "
        "corrections and two matched controls are compared. Cached C2 predictions were "
        "reused only after request/identity/target checks; no validation Chronos calls "
        "were repeated. Failure-free selection uses all 1,509 events. The all-history "
        "intersection excludes 621 otherwise two-hour-eligible validation meals; this "
        "remains a retrospectively isolated logged-meal task, not every live meal.",
        "",
        "Macro metrics weight participants equally. Tails pool individual point errors. "
        "No clipping, silent native-band repair or outcome-based exclusions.",
        "",
        "| Eligible option | Macro MAE mg/dL | Within +/-10 | Pooled p95 | Pooled maximum |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, item in sorted(primary.items(), key=lambda item: item[1]["participant_macro"]["mae"]):
        m, p = item["participant_macro"], item["point_metrics"]
        lines.append(
            f"| {name} | {number(m['mae'])} | {percent(m['within_10'])} | {number(p['absolute_error_p95'])} | {number(p['max_absolute_error'])} |"
        )
    lines += [
        "",
        "## Incremental correction decision",
        "",
        "Predeclared correction gate versus original Phase 4 LightGBM: at least 5% "
        "lower macro MAE, no lower within-10, no worse pooled p95, and zero failed "
        "validation attempts. This guards against advancing a more expensive model "
        "for a tiny selected point-estimate gain. It does not prove external benefit.",
        "",
        "| Correction | MAE improvement versus incumbent | Gate |",
        "|---|---:|---|",
    ]
    for name, item in summary["incremental_correction_gates"].items():
        lines.append(
            f"| {name} | {percent(item['mae_improvement_fraction'])} | {'PASS' if item['passes'] else 'FAIL'} |"
        )
    lines += [
        "",
        f"The best eligible option's overall persistence-improvement gate "
        f"{'passes' if summary['selection_gate']['passes'] else 'fails'} "
        f"({percent(summary['selection_gate']['mae_improvement_fraction'])} lower MAE; "
        "also requires nondecreasing within-10 and nonincreasing p95). This "
        "overall gate is separate from correction benefit over the stronger incumbent.",
        "",
        "Participant-cluster bootstrap, 10,000 draws/seed20261016: differences "
        "are correction minus comparator; negative favours correction. Intervals "
        "are descriptive after reused-validation selection, without multiplicity "
        "correction or independent significance claims.",
        "",
        "| Correction | Comparator | Delta MAE | Descriptive 95% interval |",
        "|---|---|---:|---|",
    ]
    for name, comparisons in summary["correction_intervals"].items():
        for comparator, ci in comparisons.items():
            lines.append(
                f"| {name} | {comparator} | {number(ci['macro_mae_difference'])} | [{number(ci['bootstrap_95_low'])}, {number(ci['bootstrap_95_high'])}] |"
            )
    lines += [
        "",
        "## Failure accounting, horizons and tolerance",
        "",
        "Pairwise-success scores have distinct populations; all-attempt yields "
        "retain failed cases. These rows do not replace full-cohort ranking.",
        "",
        "| Option | Attempts | Failures | Paired successes | Paired macro MAE | Attempted-point within-10 yield | Negative predictions |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, pair in summary["pairs"].items():
        item = pair["runs"][name]
        lines.append(
            f"| {name} | {pair['requested_event_count']} | {item['failure_count']} | {pair['common_success_event_count']} | {number(item['participant_macro'].get('mae'))} | {percent(item['attempted_point_within_10_yield'])} | {summary['negative_prediction_points'][name]} |"
        )
    lines += [
        "",
        "Endpoint and whole-curve metrics for full-cohort eligible options:",
        "",
        "| Option | 30 min MAE | 60 min MAE | 120 min MAE | Whole curve within +/-10 | Pooled p99 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, item in primary.items():
        m = item["participant_macro"]
        endpoints = " | ".join(number(m[f"absolute_error_{h}"]) for h in (30, 60, 120))
        lines.append(
            f"| {name} | {endpoints} | {percent(m['whole_curve_within_10'])} | {number(item['point_metrics']['absolute_error_p99'])} |"
        )
    lines += [
        "",
        "## Conditional common-success and source diagnostics",
        "",
        f"All 13 options succeeded on **{summary['all_run_summary']['common_success_event_count']:,} meals**. "
        "This conditional subset excludes failures and is secondary.",
        "",
        "| Option | Common-success macro MAE | Within +/-10 |",
        "|---|---:|---:|",
    ]
    for name, item in summary["all_run_summary"]["runs"].items():
        m = item["participant_macro"]
        lines.append(f"| {name} | {number(m.get('mae'))} | {percent(m.get('within_10'))} |")
    lines += [
        "",
        "Subgroups use all-option common-success meals within each source. "
        "They are descriptive, not a causal study effect or external validation.",
        "",
        "| Source | Common meals | Option | Macro MAE | Within +/-10 |",
        "|---|---:|---|---:|---:|",
    ]
    for source, table in summary["by_source"].items():
        names = ["persistence", "lightgbm_direct", "ridge_direct"] + list(summary["fit_metadata"])
        for name in names:
            m = table["runs"][name]["participant_macro"]
            lines.append(
                f"| {source} | {table['common_success_event_count']} | {name} | {number(m.get('mae'))} | {percent(m.get('within_10'))} |"
            )
    retained = primary[advance]
    m, p = retained["participant_macro"], retained["point_metrics"]
    lines += [
        "",
        "## Critical interpretation and next phase",
        "",
        "The Ridge correction lowers MAE by only 0.03 mg/dL versus original LightGBM "
        "(0.10%); its descriptive delta interval [-0.48,0.43] includes no improvement. "
        "Within-10 rises from 26.84% to 29.12%, but that is only 0.27 percentage points "
        "above the cheaper original Ridge direct model's 28.85%. LightGBM correction "
        "worsens MAE to 31.75 and within-10 to 25.95%. These corrections substantially "
        "improve the frozen C2 backbone itself (37.61 MAE), but add little or no value "
        "beyond the already trained direct models. Retaining the direct incumbent is "
        "the predeclared decision, not a claim that it wins every tolerance metric.",
        "",
        f"The retained option has macro MAE **{number(m['mae'])} mg/dL**, within +/-10 "
        f"**{percent(m['within_10'])}**, whole-curve within-10 "
        f"**{percent(m['whole_curve_within_10'])}**, maximum error "
        f"**{number(p['max_absolute_error'])} mg/dL**. "
        "Average error and within-10 percentages are different objectives. A point "
        "percentage is not classification accuracy, interval coverage or an entire-curve "
        "guarantee. The +/-10 aspiration remains unmet; accuracy is still weak for that goal.",
        "",
        "Matched controls remove the training-population difference. The correction "
        "adds forecast features and changes the target to a residual, so this comparison "
        "does not isolate those two mechanisms individually. The four fixed correction "
        "configurations do not exhaust possible "
        "models, training budgets or representations. A negative gate is evidence about "
        "this bounded design, not proof that all Chronos correction is impossible. "
        "A positive gate remains selected development evidence requiring reserved testing.",
        "",
        "No protein/fat/fibre or physiological IOB/COB was invented. Recorded context "
        "cannot recover missing meals, delivery or unknown latency/upstream processing. "
        "Source-qualified identities are not proof of globally independent people. "
        "Performance on other studies or earlier UOM/AZT1D cohorts is not a paired "
        "before/after improvement. The previously consumed AZT1D set is not untouched.",
        "",
        "Next is Phase 6: freeze the final candidate set and separate calibration/test "
        "protocol, calibrate intervals on reserved development calibration data, then "
        "score the 104 primary-test and 65 PEDAP source-test identity reservations once. "
        "Eligible test-event counts are not yet known. Report all failures, tails, "
        "subgroups and uncertainty. No further tuning on test outcomes, app promotion "
        "or clinical guarantee follows from these scores.",
        "",
        "## Reproduction, runtime and verification",
        "",
        "```powershell",
        "uv run --no-sync python -m research.pipelines.cache_metabonet_backbone",
        "uv run --no-sync python -m research.pipelines.run_metabonet_correction",
        "uv run --no-sync python -m research.pipelines.run_metabonet_correction --verify-only",
        "uv run --no-sync python -m research.pipelines.report_metabonet_correction",
        "```",
        "",
        "Completed stages refuse replay. Matching interrupted stages reuse intact "
        "checksummed work; failures are never retried. Distinct backbone/head source "
        "snapshots, cohort/folds, checkpoint/input hashes, OOF arrays, fitted heads, "
        "predictions and completion manifests remain under ignored local artifacts. "
        "No raw health rows, identities, timestamps, weights or secrets enter this report.",
        "",
        f"Python {execution['configuration']['python']}; head packages: "
        + ", ".join(f"{k} {v}" for k, v in execution["configuration"]["packages"].items())
        + ".",
        f"Backbone stage runtime **{number(backbone['elapsed_seconds'] / 60)} minutes**; "
        f"head CV/refit/validation/summary **{number(summary['elapsed_seconds'] / 60)} minutes**. "
        "The requested CPU limit was two threads. A separate import-order audit found "
        "late-loaded SciPy/OpenMP libraries could retain 16 threads despite that request; "
        "strict two-thread enforcement was not established for the heads. These "
        "measurements exclude preflight/loading and do not predict later-phase effort.",
        "",
    ]
    walls = [row["wall_ms"] for row in backbone_rows]
    lines += [
        f"Training-backbone call wall time: median **{number(percentile(walls, 0.5))} ms**, "
        f"p95 **{number(percentile(walls, 0.95))} ms**. Includes adapter predict but "
        "excludes request construction. A correction still needs this backbone "
        "work at inference; a direct model does not.",
        "",
        "| Model | Head-only batch prediction, 1,509 meals |",
        "|---|---:|",
    ]
    for name, item in summary["validation_metadata"].items():
        lines.append(f"| {name} | {number(item['batch_head_prediction_ms'])} ms |")
    lines += [
        "",
        "Head batch timings exclude feature extraction/backbone generation and "
        "are not per-request latency. Zero row timing placeholders are excluded "
        "from latency claims. Do not compare them directly with Chronos call p95.",
        "",
        "See [protocol 15](../planning/GlycoLens_15_MetaboNet_Chronos_Correction.md) and "
        "[verification handoff](../tooling/metabonet-phase5-handoff-2026-10-16.md).",
        "",
    ]
    if summary.get("execution_audit"):
        lines += [
            "## Launcher interruption and resource-limit audit",
            "",
            "The first head-stage PowerShell launcher treated a retained numerical "
            "RuntimeWarning as a terminating native-command error. It stopped during "
            "the first CV candidate before any completed CV candidate or validation "
            "row was saved. The launcher was corrected to retain stderr warnings in "
            "the log and honor the Python exit code; the unchanged frozen model "
            "sources/configuration resumed. The incomplete candidate was recomputed; "
            "no completed candidate, failed prediction or validation result was retried "
            "to improve a score. Original interrupted logs and an audit JSON were retained.",
            "",
            "The head runtime above is the resumed completion attempt, not cumulative "
            "CPU time including interrupted partial folds. An isolated reproduction "
            "of the runner import order found NumPy BLAS limited to 2 threads but "
            "late-loaded SciPy BLAS/OpenMP at 16. These are requested resource settings, "
            "not proof every library was limited to two threads. Future runners should "
            "import estimator libraries before applying limits. No model settings or "
            "features changed during this run; accuracy was independently reproduced.",
            "",
        ]
    return "\n".join(lines)


def main():
    verify_phase5()
    summary = json.loads((OUTPUT / "heads/summary.json").read_text())
    audit_path = OUTPUT / "heads/launcher-interruption.json"
    if audit_path.exists():
        summary = {**summary, "execution_audit": json.loads(audit_path.read_text())}
    cv = json.loads((OUTPUT / "heads/cv-summary.json").read_text())
    rows = [json.loads(s) for s in (OUTPUT / "backbone/training.jsonl").read_text().splitlines()]
    report = ROOT / "docs/reports/metabonet-phase5-correction-2026-10-16.md"
    report.write_text(
        render_report(summary, cv, read_execution(OUTPUT / "heads"), rows), encoding="utf-8"
    )
    print(json.dumps(dict(report=report.relative_to(ROOT).as_posix(), aggregate_only=True)))


if __name__ == "__main__":
    main()
