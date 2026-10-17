"""Publish aggregate Phase 4 evidence from a verified, completed local experiment."""

import json

from research.pipelines.prepare_metabonet import ROOT
from research.pipelines.report_metabonet_inference import number, percent
from research.pipelines.run_metabonet_inference import read_execution
from research.pipelines.run_metabonet_training import verify_training_completed

OUTPUT = ROOT / "artifacts/evaluation-results/metabonet-phase4-v1"


def render_report(summary, cv, execution):
    primary = summary["selection_summary"]
    winner = summary["selected_candidate"]
    selected = primary["runs"][winner]
    macro = selected["participant_macro"]
    cohort = summary["training_cohort"]
    gate = summary["selection_gate"]
    lines = [
        "# MetaboNet Phase 4 direct-model results - October 16, 2026",
        "",
        "**Phase 4 is complete. Small models were trained; Chronos weights stayed frozen. "
        "Calibration and reserved test outcomes were not accessed.** These are development "
        "validation findings, not independent confirmation or an app model replacement.",
        "",
        f"Selected failure-free option: **{winner}**, participant-average MAE "
        f"**{number(macro['mae'])} mg/dL**, within +/-10 **{percent(macro['within_10'])}**. "
        f"Improvement over persistence: **{percent(gate['mae_improvement_fraction'])}**. "
        f"Predeclared improvement gate: **{'PASS' if gate['passes'] else 'FAIL'}**.",
        "",
        "## Training choices and leakage controls",
        "",
        f"The common four-history training pool contains **{cohort['common_event_count']:,} "
        f"events / {cohort['common_subject_count']} source-qualified identities**. "
        "Three source-stratified, stable-hash subject folds keep every identity wholly "
        "inside one fold. Participant weights have equal total weight per identity. "
        "No participant/source identifier, absolute date or clock time is a predictor.",
        "",
        "Histories 2/6/12/24 hours, CGM-only/event profiles and two parameters per family "
        "give 32 candidates / 96 fold fits. Rank training out-of-fold participant-average "
        "MAE, tie higher within-10 then stable name; failed candidates cannot win. "
        "No validation-based early stopping or adaptive search was used. Per-family "
        "choices were frozen and refitted before reading prepared validation outcomes.",
        "",
        "Ridge jointly predicts 24 glucose deltas from current glucose, with median "
        "imputation and weighted scaling fitted only on each training fold/refit. "
        "LightGBM fits one pooled-horizon delta regressor, adding horizon fraction and "
        "expanding rows only after subject splitting. It is not 24 independent boosters. "
        "The fixed tree budget is 160, learning rate 0.04, minimum child size 100, "
        "max_bin63, reg_lambda1, seed20261016 and two threads.",
        "",
        "Features use current glucose, two-hour relative lags/masks, history summaries "
        "and slopes. The selected 24-hour configuration uses 24-hour glucose history; "
        "recorded-event summaries cover the preceding six hours. Event profiles add "
        "origin-known fractional carbs, separate "
        "recorded basal/bolus amounts, prior carbs, presence fractions and mathematical "
        "recency summaries. Units remain mg/dL, grams and previous-five-minute IU. "
        "Merged insulin total is omitted. Missing event amounts are distinguished from "
        "recorded zero; masks cannot recover unlogged meals or delivery. Recency features "
        "are not physiological IOB/COB or causal treatment effects.",
        "",
        "| History | All eligible training events | Identities |",
        "|---|---:|---:|",
    ]
    for hours, item in sorted(cohort["eligible_by_history"].items(), key=lambda x: int(x[0])):
        lines.append(f"| {hours} h | {item['events']:,} | {item['subjects']} |")
    lines += [
        "",
        "Training-only CV grid:",
        "",
        "| Candidate | OOF macro MAE | OOF within +/-10 | Failed folds |",
        "|---|---:|---:|---:|",
    ]
    for row in cv["candidates"]:
        lines.append(
            f"| {row['name']} | {number(row['macro_mae'])} | {percent(row['within_10'])} | "
            f"{row['failure_count']} |"
        )
    lines += [
        "",
        "Chosen refits (all eligible training events at the selected history):",
        "",
        "| Family | Training-CV choice | Refit events | Identities | Features | Reload equivalent |",
        "|---|---|---:|---:|---:|---|",
    ]
    for family, item in summary["fit_metadata"].items():
        lines.append(
            f"| {family} | {item['configuration']['name']} | {item['training_events']:,} | "
            f"{item['training_subjects']} | {item['feature_count']} | "
            f"{item['reload_prediction_equivalent']} |"
        )
    lines += [
        "",
        "Refits can include additional training meals outside the common CV pool; "
        "the table makes that expansion explicit. All imputation/scaling/model state "
        "is frozen before validation. Trusted local bundles are checksummed before "
        "resume deserialization; save/reload prediction equivalence was checked.",
        "",
        "## Primary validation: same 1,509 meals / 48 identities",
        "",
        "Both selected families were compared with the seven verified saved Phase 3 "
        "forecasts on exactly equal origins, identities and targets. No Chronos inference "
        "was rerun. This cohort has 857 Loop and 652 ReplaceBG meals and excludes 621 "
        "otherwise two-hour-eligible validation meals. Five-minute delayed logged-carb "
        "availability, retrospective isolated-meal exclusions and causal short filling "
        "remain unchanged. These are conditional logged-meal forecasts, not all live meals.",
        "",
        "Only failure-free options on the complete cohort enter the primary ranking. "
        "Each identity has equal weight in macro metrics. Pooled error tails weight "
        "individual points equally. No prediction clipping or error-based exclusion.",
        "",
        "| Option | Macro MAE mg/dL | Within +/-10 | Pooled p95 | Pooled maximum |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, item in sorted(
        primary["runs"].items(), key=lambda x: x[1]["participant_macro"]["mae"]
    ):
        m, p = item["participant_macro"], item["point_metrics"]
        lines.append(
            f"| {name} | {number(m['mae'])} | {percent(m['within_10'])} | "
            f"{number(p['absolute_error_p95'])} | {number(p['max_absolute_error'])} |"
        )
    lines += [
        "",
        "All attempts, including failure-prone original options:",
        "",
        "| Option | Attempts | Failures | Paired successful events | Paired macro MAE | Attempted-point within-10 yield | Negative predictions |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, pair in summary["pairs"].items():
        item = pair["runs"][name]
        lines.append(
            f"| {name} | {pair['requested_event_count']} | {item['failure_count']} | "
            f"{pair['common_success_event_count']} | {number(item['participant_macro'].get('mae'))} | "
            f"{percent(item['attempted_point_within_10_yield'])} | "
            f"{summary['negative_prediction_points'][name]} |"
        )
    lines += [
        "",
        "Failed forecasts remain in attempted denominators. Pairwise-success rows "
        "can have different populations and do not replace primary selection.",
        "",
        "## Horizons, tails and descriptive intervals",
        "",
        "Full-cohort eligible options; endpoint errors are participant averages:",
        "",
        "| Option | 30 min MAE | 60 min MAE | 120 min MAE | Whole curve within +/-10 | Pooled p99 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, item in primary["runs"].items():
        m = item["participant_macro"]
        values = [number(m[f"absolute_error_{h}"]) for h in (30, 60, 120)]
        lines.append(
            "| "
            + name
            + " | "
            + " | ".join(values)
            + " | "
            + percent(m["whole_curve_within_10"])
            + " | "
            + number(item["point_metrics"]["absolute_error_p99"])
            + " |"
        )
    lines += [
        "",
        "Option-minus-persistence MAE; negative favours the option. "
        "Participant-cluster bootstrap uses 10,000 draws and seed20261016. "
        "Validation was used for selection, so these are descriptive intervals "
        "without multiplicity correction, not independent significance claims.",
        "",
        "| Option | Delta MAE mg/dL | Descriptive 95% interval |",
        "|---|---:|---|",
    ]
    for name, ci in summary["paired_intervals"].items():
        lines.append(
            f"| {name} | {number(ci['macro_mae_difference'])} | "
            f"[{number(ci['bootstrap_95_low'])}, {number(ci['bootstrap_95_high'])}] |"
        )
    lines += [
        "",
        "## Common-success and source diagnostics",
        "",
        f"All-nine common-success cohort: **{summary['all_run_summary']['common_success_event_count']:,} meals**. "
        "This excludes failures and is secondary to full-cohort selection.",
        "",
        "| Option | Common-success macro MAE | Within +/-10 |",
        "|---|---:|---:|",
    ]
    for name, item in summary["all_run_summary"]["runs"].items():
        m = item["participant_macro"]
        lines.append(f"| {name} | {number(m.get('mae'))} | {percent(m.get('within_10'))} |")
    lines += [
        "",
        "Source rows use all-nine common-success meals within each source; "
        "they are descriptive, not an external test or controlled study effect.",
        "",
        "| Source | Common meals | Option | Macro MAE | Within +/-10 |",
        "|---|---:|---|---:|---:|",
    ]
    for source, table in summary["by_source"].items():
        for name in ("persistence", "chronos_c2_6h", "ridge_direct", "lightgbm_direct"):
            m = table["runs"][name]["participant_macro"]
            lines.append(
                f"| {source} | {table['common_success_event_count']} | {name} | "
                f"{number(m.get('mae'))} | {percent(m.get('within_10'))} |"
            )
    lines += [
        "",
        "## Interpretation and next phase",
        "",
        "**Blunt assessment: average error improved, but tight-tolerance accuracy is "
        "still poor.** The selected model is outside +/-10 for about "
        f"{percent(1 - macro['within_10'])} of points under participant averaging. "
        "This does not support dependable +/-10 forecasting.",
        "",
        "Ridge has higher within-10 than LightGBM despite a slightly higher MAE. "
        "LightGBM wins under the predeclared MAE-first rule; it is not best on every "
        "metric. Keep Ridge as a tolerance challenger for the later frozen comparison. "
        "Both learned models have a lower whole-curve-within-10 rate than persistence. "
        "The gate did not require improving whole-curve success, so passing it does "
        "not imply that metric improved. Do not change the ranking after seeing scores.",
        "",
        "The gate requires at least 10% lower macro MAE than persistence, nondecreasing "
        "macro within-10 and nonincreasing pooled p95. A validation pass still requires "
        "reserved testing. The selected within-10 rate is a fraction of individual "
        "five-minute predictions, not classification accuracy, interval coverage or "
        "the probability an entire two-hour curve stays within 10.",
        "",
        f"The observed selected maximum error is **{number(selected['point_metrics']['max_absolute_error'])} mg/dL**. "
        "The +/-10 aspiration has not been achieved as a maximum-error guarantee. "
        "Training more data or fitting a small model does not guarantee this tolerance. "
        "These results do not isolate causal meal/insulin effects or establish global "
        "identity independence, complete event logging or clinical safety.",
        "",
        "Direct models supply deterministic contract placeholders for quantiles. "
        "They have **no calibrated uncertainty interval**, so placeholder coverage is "
        "not reported. Phase 3 native Chronos undercoverage is preserved in its report.",
        "",
        "Next, Phase 5 compares a small frozen-Chronos correction with the direct "
        "winner using training-only choices and the same validation task. Freeze that "
        "comparison before Phase 6 interval calibration and one-time reserved primary "
        "and PEDAP testing. The 104 primary-test and 65 PEDAP identity reservations "
        "remain metadata-only; eligible test-event counts are not yet known. Earlier "
        "UOM/AZT1D scores are historical, not paired before/after evidence. "
        "No foundation-model fine-tuning or application promotion occurred.",
        "",
        "## Reproduction and provenance",
        "",
        "```powershell",
        ".venv/Scripts/python.exe -m research.pipelines.run_metabonet_training",
        ".venv/Scripts/python.exe -m research.pipelines.run_metabonet_training --verify-only",
        ".venv/Scripts/python.exe -m research.pipelines.report_metabonet_training",
        "```",
        "",
        "The first command refuses completed replay. Matching interrupted work can "
        "reuse only intact checksummed CV/model/validation outputs. Execution config, "
        "protocol, package versions and sources were archived before fitting; later "
        "documentation updates do not rewrite executed source. All IDs, timestamps, "
        "windows, predictions, OOF arrays, source ZIPs and trusted model weights remain "
        "under ignored local artifacts. This report contains aggregate data only.",
        "",
        f"Python {execution['configuration']['python']}; packages: "
        + ", ".join(f"{k} {v}" for k, v in execution["configuration"]["packages"].items())
        + ".",
        f"Measured wall time from the original execution freeze through completion "
        f"(including diagnosis/scoring repair when present): "
        f"{number(summary['elapsed_seconds'] / 60)} minutes, CPU two threads. "
        "This excludes initial input verification and is not a promise for later phases.",
        "",
        "| Direct model | Validation batch prediction time, 1,509 meals |",
        "|---|---:|",
    ]
    for family, item in summary["validation_metadata"].items():
        lines.append(f"| {family} | {number(item['batch_prediction_ms'])} ms |")
    lines += [
        "",
        "Batch timing excludes feature extraction and is not per-request latency. "
        "Per-event p95 was not measured; zero row timing placeholders are excluded "
        "from aggregate latency claims. Do not compare this batch timing directly "
        "with Phase 3 individual Chronos call latency.",
        "",
        "See [protocol 14](../planning/GlycoLens_14_MetaboNet_Direct_Models.md) and "
        "[verification handoff](../tooling/metabonet-phase4-handoff-2026-10-16.md).",
        "",
    ]
    if summary.get("completion_repair"):
        lines += [
            "## Scoring interruption and audited completion",
            "",
            "The original run completed all 96 CV fits and both final refits, then "
            "stopped before its first persisted scored validation row: statistics.mean "
            "cannot average NumPy boolean values. A synthetic regression reproduced "
            "this failure; converting prediction scalars to native Python floats fixed "
            "the metrics/JSON boundary. This was a scoring bug, not a failed fitted model.",
            "",
            "The dedicated complete_metabonet_training command verified original "
            "CV records, choices, model hashes and source ZIP, and checked that the "
            "runner changed only that conversion line. Its own source/configuration "
            "snapshot is archived under completion-repair. No CV candidate or model "
            "was refitted, no choice/parameter/feature changed, and the original "
            "zero-row file was retained as interrupted-validation-ridge.jsonl. "
            "Validation was scored again with identical frozen predictions; there "
            "was no outcome-based retry or exclusion. The completion manifest covers "
            "both execution archives. A completed run still refuses replay.",
            "",
            "Ridge CV emitted weighted-scaling RuntimeWarnings during square roots "
            "of numerical variances. Every OOF prediction was finite, no fold failed, "
            "and the saved scaler/coefficients and predictions were independently "
            "checked. The warning is retained in the local log, not silently suppressed.",
            "",
        ]
    return "\n".join(lines)


def main():
    verify_training_completed(OUTPUT)
    summary = json.loads((OUTPUT / "summary.json").read_text())
    cv = json.loads((OUTPUT / "cv-summary.json").read_text())
    execution = read_execution(OUTPUT)
    destination = ROOT / "docs/reports/metabonet-phase4-training-2026-10-16.md"
    destination.write_text(render_report(summary, cv, execution), encoding="utf-8")
    print(json.dumps({"report": destination.relative_to(ROOT).as_posix(), "aggregate_only": True}))


if __name__ == "__main__":
    main()
