"""Create an aggregate Phase 3 report from verified frozen artifacts only."""

import json
from collections import Counter

from research.pipelines.prepare_metabonet import ROOT
from research.pipelines.run_metabonet_inference import read_execution, verify_completed

OUTPUT = ROOT / "artifacts/evaluation-results/metabonet-phase3-v1"


def number(value, digits=2):
    return "n/a" if value is None else f"{value:,.{digits}f}"


def percent(value):
    return "n/a" if value is None else f"{100 * value:.2f}%"


def main():
    verify_completed(OUTPUT)
    execution = read_execution(OUTPUT)
    summary = json.loads((OUTPUT / "summary.json").read_text())
    cohort = json.loads((OUTPUT / "validation-cohort.json").read_text())
    selection = summary["selection_summary"]
    winner = summary["selected_frozen_candidate"]
    best = selection["runs"][winner]
    baseline = selection["runs"]["persistence"]
    macro = best["participant_macro"]
    gate = summary["selection_gate"]
    chronos = [name for name in selection["runs"] if name.startswith("chronos_")]
    best_chronos = (
        min(
            chronos,
            key=lambda n: (
                selection["runs"][n]["participant_macro"]["mae"],
                -selection["runs"][n]["participant_macro"]["within_10"],
                n,
            ),
        )
        if chronos
        else None
    )
    lines = [
        "# MetaboNet Phase 3 frozen-inference results - October 16, 2026",
        "",
        "**Executed on validation only. No model weights were fitted, no calibration "
        "set was consumed and no reserved test values were accessed.** The selected "
        "configuration is a development decision, not independent confirmation or an "
        "application model replacement.",
        "",
        f"Best eligible frozen option: **{winner}**. Participant-average two-hour "
        f"trajectory MAE **{number(macro['mae'])} mg/dL**. Participant-average "
        f"within +/-10: **{percent(macro['within_10'])}**. Research improvement gate: "
        f"**{'PASS' if gate['passes'] else 'FAIL'}**.",
        f"Best eligible Chronos option: **{best_chronos}**, macro MAE "
        f"**{number(selection['runs'][best_chronos]['participant_macro']['mae'])} mg/dL**."
        if best_chronos
        else "No Chronos option met the failure-free eligibility rule.",
        "",
        f"Phase 4 CGM-history choice: **{summary['selected_history_hours']} hours** "
        f"(`{summary['selected_c0_candidate']}`; {summary['history_selection_reason']}). "
        "This is separate from the overall frozen candidate and does not prove the "
        "same history is optimal for every small trained model.",
        "",
        "## Population and fixed design",
        "",
        f"There are **{cohort['matched_event_count']:,} matched meal events** from "
        f"**{cohort['matched_subject_count']} source-qualified identities**. Every run "
        "uses the same event identities, origins and 24 future targets. The matched "
        "population is fixed before model output; failed candidates do not shrink "
        "the failure-free selection table.",
        "",
        "| Available history | Eligible events | Eligible identities |",
        "|---|---:|---:|",
    ]
    for hours, values in sorted(
        cohort["eligible_by_history"].items(), key=lambda item: int(item[0])
    ):
        lines.append(f"| {hours} h | {values['event_count']:,} | {values['subject_count']} |")
    lines += [
        "",
        "Matched events by source: "
        + ", ".join(f"{k}: {v:,}" for k, v in sorted(cohort["matched_sources"].items()))
        + ".",
        f"The matched set excludes {cohort['eligible_by_history']['2']['event_count'] - cohort['matched_event_count']:,} "
        "otherwise two-hour-eligible events because all four histories must qualify. "
        "Results therefore do not cover every eligible validation meal; history "
        "completeness can change the evaluated population.",
        "",
        "Five-minute delayed logged-carb availability is primary. This is the frozen "
        "Phase 2 retrospectively isolated logged-meal task, not unrestricted pre-meal "
        "forecasting. Missing histories use only the prescribed short causal fill; "
        "targets are never imputed or clipped. No zero-delay sensitivity was selected "
        "using these scores.",
        "",
        "C0 is CGM-only at 2/6/12/24 h. C1 uses the predeclared six-hour history plus "
        "recorded bolus/basal IU amounts and source-present masks. C2 additionally "
        "uses previous logged carbs and origin-known current carbs. Total insulin "
        "is omitted when components are used. No protein/fat/fibre or physiological "
        "insulin activity was invented. The unchanged common adapter uses "
        "`recorded_events_v1`, including its observation channels. Masks do not recover "
        "unlogged intake/delivery or unknown upstream interpolation. This study does "
        "not search all history/context combinations.",
        "",
        "## Primary selection: complete matched cohort, failure-free options",
        "",
        "Rank participant-average MAE, tie higher participant-average within +/-10, "
        "then stable name. Each participant has equal weight within these macro metrics. "
        "P95/max below pool all absolute point errors. Persistence can win.",
        "Failure-free means the software contract accepted an output; it does not "
        "establish physiological plausibility or clinical accuracy. Negative medians "
        "remain visible in the native-output table.",
        "",
        "| Option | MAE mg/dL | Within +/-10 | Pooled p95 | Pooled maximum |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, run in sorted(
        selection["runs"].items(), key=lambda item: item[1]["participant_macro"]["mae"]
    ):
        m, p = run["participant_macro"], run["point_metrics"]
        lines.append(
            f"| {name} | {number(m['mae'])} | {percent(m['within_10'])} | {number(p['absolute_error_p95'])} | {number(p['max_absolute_error'])} |"
        )
    lines += [
        "",
        "## All attempts and failures",
        "",
        "The table retains every predeclared option. Its MAE/within-10 are paired with "
        "persistence on that option's successful events, so those rows can have different "
        "populations and are not the primary ranking. Attempted-point yield counts "
        "failed forecasts as unsuccessful, rather than dropping their denominators.",
        "",
        "| Option | Attempts | Failed | Paired events | Paired MAE | Within +/-10 | Attempted-point within-10 yield |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, pair in summary["pairs"].items():
        run = pair["runs"][name]
        m = run["participant_macro"]
        lines.append(
            f"| {name} | {pair['requested_event_count']} | {run['failure_count']} | {pair['common_success_event_count']} | {number(m.get('mae'))} | {percent(m.get('within_10'))} | {percent(run['attempted_point_within_10_yield'])} |"
        )
    lines += [
        "",
        f"All-seven common-success set: **{summary['all_run_summary']['common_success_event_count']:,} events**. Failure counts/types are preserved; quantiles were not repaired, predictions were not clipped and failed model outputs were not retried.",
        "",
        "## Common-success diagnostic comparison",
        "",
        "Every option below is scored on the same all-option common-success subset. "
        "This describes accuracy conditional on all outputs being valid; it excludes "
        "failure cases and therefore does not replace the full-cohort eligibility rule.",
        "",
        "| Option | MAE mg/dL | Within +/-10 | Pooled p95 |",
        "|---|---:|---:|---:|",
    ]
    for name, run in summary["all_run_summary"]["runs"].items():
        m, p = run["participant_macro"], run["point_metrics"]
        lines.append(
            f"| {name} | {number(m.get('mae'))} | {percent(m.get('within_10'))} | {number(p.get('absolute_error_p95'))} |"
        )
    lines += [
        "",
        "## Horizons, whole curves and error tails",
        "",
        "All-option paired-success diagnostics (each row retains its own successful "
        "population; see the failure table):",
        "",
        "| Option | 30 min | 60 min | 120 min | Pooled p95 | Pooled p99 | Pooled max |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, pair in summary["pairs"].items():
        m, p = pair["runs"][name]["participant_macro"], pair["runs"][name]["point_metrics"]
        values = [m.get(f"absolute_error_{h}") for h in (30, 60, 120)]
        values += [
            p.get(k) for k in ("absolute_error_p95", "absolute_error_p99", "max_absolute_error")
        ]
        lines.append("| " + name + " | " + " | ".join(number(v) for v in values) + " |")
    lines += [
        "",
        "The following uses the selected failure-free option on the full matched cohort. "
        "Endpoint errors are participant-average absolute error at that horizon. A "
        "within-10 point percentage is not classification accuracy or the probability "
        "that an entire two-hour curve stays within 10.",
        "",
        "| Measure | Selected | Persistence |",
        "|---|---:|---:|",
    ]
    for h in (30, 60, 120):
        lines.append(
            f"| {h}-minute error mg/dL | {number(macro[f'absolute_error_{h}'])} | {number(baseline['participant_macro'][f'absolute_error_{h}'])} |"
        )
    lines += [
        f"| Whole curve within +/-10, participant-average | {percent(macro['whole_curve_within_10'])} | {percent(baseline['participant_macro']['whole_curve_within_10'])} |",
        f"| Pooled p99 absolute error mg/dL | {number(best['point_metrics']['absolute_error_p99'])} | {number(baseline['point_metrics']['absolute_error_p99'])} |",
        f"| Pooled max absolute error mg/dL | {number(best['point_metrics']['max_absolute_error'])} | {number(baseline['point_metrics']['max_absolute_error'])} |",
        "",
        "## Paired uncertainty and native forecast bands",
        "",
        "MAE deltas below are option minus persistence on their matched successful "
        "events, bootstrapped by participant with 10,000 draws/seed20261016. Negative "
        "favours the option. These validation comparisons were used for selection; "
        "their intervals are descriptive and not adjusted for candidate selection.",
        "",
        "| Option | Delta MAE mg/dL | Descriptive 95% interval |",
        "|---|---:|---|",
    ]
    for name, ci in summary["paired_intervals"].items():
        lines.append(
            f"| {name} | {number(ci['macro_mae_difference'])} | [{number(ci['bootstrap_95_low'])}, {number(ci['bootstrap_95_high'])}] |"
        )
    lines += [
        "",
        "Native q10-q90 intervals have nominal 80% coverage. They have **not been calibrated**. Coverage/width below are pooled over successful native-band points; persistence has no probabilistic band here.",
        "",
        "| Option | Band events | Coverage | Mean width mg/dL | Negative forecast points | Failure types |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for name, band in summary["native_bands"].items():
        lines.append(
            f"| {name} | {band['native_band_event_count']} | {percent(band['coverage'])} | {number(band['mean_width'])} | {band['negative_prediction_points']} | {json.dumps(band['failure_types'], sort_keys=True)} |"
        )
    causes = {}
    for name in summary["pairs"]:
        rows = [json.loads(line) for line in (OUTPUT / f"{name}.jsonl").read_text().splitlines()]
        causes[name] = dict(
            Counter(r.get("error_cause_type") or r["error_type"] for r in rows if r["error_type"])
        )
    lines += [
        "",
        "Underlying failure-cause types: `" + json.dumps(causes, sort_keys=True) + "`. "
        "Cause types distinguish contract/backend categories, not the exact invalid "
        "numeric output. Failed raw quantiles were not retained or rerun for diagnosis.",
    ]
    lines += [
        "",
        "## Source subgroups",
        "",
        "These descriptive source summaries use the all-option common-success set "
        "within each source, rather than pretending failed cases were scored. Source "
        "differences are not independent external validation and must not be read as "
        "a controlled causal effect of study membership.",
        "",
        "| Source | Common events | Option | MAE mg/dL | Within +/-10 |",
        "|---|---:|---|---:|---:|",
    ]
    for source, group in summary["by_source"].items():
        for name, run in group["runs"].items():
            lines.append(
                f"| {source} | {group['common_success_event_count']} | {name} | {number(run['participant_macro'].get('mae'))} | {percent(run['participant_macro'].get('within_10'))} |"
            )
    lines += [
        "",
        "## Interpretation and next phase",
        "",
        f"The selected option changes macro MAE by **{percent(gate['mae_improvement_fraction'])}** "
        "relative to persistence. The gate requires at least 10% lower macro MAE, "
        "no lower macro within-10 and no worse pooled p95. Passing it on validation "
        "would still need independent testing; failing it is evidence to continue "
        "with small trained competitors, not a reason to hide the baseline.",
        "",
        f"The selected option's within-10 rate is {percent(macro['within_10'])}, while "
        f"its observed maximum point error is {number(best['point_metrics']['max_absolute_error'])} mg/dL. "
        "Neither an average improvement nor any point percentage establishes a +/-10 "
        "maximum-error guarantee. More input history or recorded events are useful "
        "only if these held-out development comparisons support them.",
        "The average absolute error still exceeds 10 mg/dL; the frozen approach remains "
        "weak against the +/-10 aspiration."
        if macro["mae"] > 10
        else "Average absolute error is at most 10 mg/dL here; the observed error tails still "
        "determine how far the approach is from consistent +/-10 predictions.",
        "The broader dataset has evaluated the same frozen weights. It has not yet "
        "trained them or automatically improved their accuracy.",
        "These scores are not paired before/after comparisons with the earlier UOM "
        "or AZT1D cohorts, which contain different participants and events.",
        "A C1/C2 forecast difference is not evidence of a causal insulin or nutrient effect.",
        "",
        "The frozen rule selected two hours because it was the only failure-free C0 "
        "candidate, **not because it had the lowest point error**. Longer histories "
        "improved conditional point accuracy but incurred native-output validation "
        "failures. Their useful history signal should not be discarded merely because "
        "the native quantile path failed. Phase 4 should retain the frozen baseline "
        "and consider longer-history features through predeclared training-only "
        "subject-level cross-validation, not relabel this decision after seeing outcomes.",
        "This experiment evaluates a specific recorded-event encoding; it cannot "
        "establish that insulin/carbohydrate context is generally uninformative.",
        "",
        "Next is Phase 4: train modest direct Ridge/LightGBM candidates on training "
        "only, preserve masks and units deliberately, and compare against the frozen "
        "baselines. Chronos corrections follow separately. Calibration remains for "
        "interval calibration; all 104 primary-test and 65 PEDAP source-test identity "
        "reservations remain untouched pending final configuration selection. No "
        "app model switch follows from these validation results.",
        "If Phase 4 uses all events eligible at its chosen history, rerun/reuse frozen "
        "baselines on exactly those IDs and targets; do not compare different cohorts "
        "or overwrite Phase 3 artifacts.",
        "",
        "## Reproduction and provenance",
        "",
        "```powershell",
        "uv sync --all-groups",
        "uv run --no-sync python -m research.pipelines.run_metabonet_inference",
        "uv run --no-sync python -m research.pipelines.run_metabonet_inference --verify-only",
        "uv run --no-sync python -m research.pipelines.report_metabonet_inference",
        "```",
        "",
        "The default output is ignored `artifacts/evaluation-results/metabonet-phase3-v1/`. "
        "An interrupted run resumes only matching frozen input/configuration/source "
        "fingerprints and checksummed rows. A completed run refuses replay; use "
        "verify-only. Corrupt progress requires review, not silent deletion or retry. "
        "Source ZIP, package versions, checkpoint-file hashes, protocol, row attempts, "
        "summary and the history decision are protected by completion hashes. "
        "All rows/identities remain ignored and outside Graphify.",
        "",
        f"Inference/aggregation stage elapsed: {summary['elapsed_seconds'] / 60:.2f} minutes "
        "(excludes validation loading and model initialization). Two Torch threads, "
        "one request per call, offline cached checkpoint. No model-batch speedup or "
        "end-to-end application latency claim. Success-wall p95 includes prediction "
        "and metric scoring, not initialization/request construction.",
        "",
        "| Option | Successful-call wall p95 ms |",
        "|---|---:|",
    ]
    for name, pair in summary["pairs"].items():
        lines.append(f"| {name} | {number(pair['runs'][name]['wall_p95_ms'])} |")
    lines += [
        "",
        f"Python {execution['configuration']['python']}; packages: "
        + ", ".join(f"{k} {v}" for k, v in sorted(execution["configuration"]["packages"].items()))
        + ".",
        "",
        "Protocol: [planning document 13](../planning/GlycoLens_13_MetaboNet_Frozen_Inference.md). "
        "Input preparation: [Phase 2 report](metabonet-phase2-preparation-2026-10-16.md). "
        "Verification and remaining risks: [Phase 3 handoff](../tooling/metabonet-phase3-handoff-2026-10-16.md).",
        "",
    ]
    destination = ROOT / "docs/reports/metabonet-phase3-inference-2026-10-16.md"
    destination.write_text("\n".join(lines), encoding="utf-8")
    print("Wrote aggregate report:", destination.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
