"""Export sanitized aggregate tables and cluster intervals, never raw research rows."""

import json
from pathlib import Path

from research.evaluation.statistics import paired_participant_interval


ROOT = Path(__file__).resolve().parents[2]


def main():
    output = [
        "# Milestone 2 model comparison and context ablation",
        "",
        "Generated October 14, 2026 from pinned local T1D-UOM V1.0.4 artifacts.",
        "Research estimates only; no clinical validity or dosing use. The application selection",
        "was frozen as Chronos-2 C3 on validation before held-out test execution.",
        "",
        "## Protocol",
        "",
        "927 windows; per-participant temporal time cuts 60/20/20, crossing targets purged.",
        "536 development, 177 validation, 211 test, three purged. Twelve of fifteen",
        "participants have both validation and test events. Subject-disjoint definitions",
        "are implemented but a subject-disjoint benchmark has not yet been run.",
        "The same requested events enter every model/context; tables use the intersection",
        "of successful events. Failures are not removed from the denominator. Representation:",
        "recorded_events_v1 (ADR 0008). No weights are trained or calibrated.",
        "",
    ]
    for split in ("validation", "test"):
        record = json.loads(
            (ROOT / f"artifacts/evaluation-results/m2-{split}.json").read_text(encoding="utf-8")
        )
        summary = record["summary"]
        output += [
            f"## {split.capitalize()}",
            "",
            f"Requested {summary['requested_event_count']} events; {summary['common_success_event_count']} common successful events.",
            "",
            "| Model/context | Failed | Participant macro MAE (mg/dL) | Event MAE | Event RMSE | Coverage q10-q90 | Width | Wall p95 ms |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for name, run in summary["runs"].items():
            m = run["matched_metrics"]

            def metric(key, aggregation="event_mean"):
                value = m.get(key, {}).get(aggregation)
                return f"{value:.3f}" if value is not None else "N/A"

            output.append(
                f"| {name} | {run['failure_count']} | {metric('mae', 'participant_macro_mean')} | {metric('mae')} | {metric('rmse')} | {metric('interval_coverage')} | {metric('interval_width')} | {run['wall_ms_p95']:.2f} |"
            )
        interval = paired_participant_interval(
            record["rows"]["chronos2:cgm_insulin_nutrition"], record["rows"]["persistence:cgm_only"]
        )
        output += [
            "",
            "Selected Chronos C3 minus persistence, paired participant-average MAE:",
            f"{interval['macro_mae_difference']:.3f} mg/dL; bootstrap 95% interval",
            f"[{interval['bootstrap_95_low']:.3f}, {interval['bootstrap_95_high']:.3f}],",
            f"{interval['participant_count']} participants / {interval['matched_events']} matched events.",
            "This interval uses the pairwise successful set, which can differ from the all-run table intersection.",
            "Negative differences favor Chronos. Participant resampling uses seed 20261014,",
            "2,000 draws; small-cohort intervals are descriptive, not clinical evidence.",
            "",
        ]
    output += [
        "## Interpretation and limitations",
        "",
        "Chronos C3 was the strongest pretrained validation configuration and practical CPU choice.",
        "It did not beat persistence on validation participant-average MAE; input support alone",
        "does not prove meal-aware benefit. Held-out results above must be assessed without reselection.",
        "Filtering retains approximately 24% of loaded meal events. Self-report quality, unknown",
        "source timezone/DST, sparse/missing insulin logs and ambiguous basal source units limit transfer.",
        "Conflicting same-time basal observations fail closed and appear in failure counts.",
        "Recorded-event masks and raw-kind descriptors are not insulin-on-board or physiological models.",
        "Mean event RMSE is the average of per-event RMSE, not a globally pooled RMSE.",
        "Persistence has no calibrated interval. Coverage/width and pinball metrics are available;",
        "exact CRPS is not inferred from only three quantiles. RSS is post-run process RSS, not peak",
        "memory; wall percentiles include adapter conversion/scoring and use the actual event samples.",
        "Live nutrition and recipe-provider checks remain prerequisites until API configuration exists.",
        "",
        "## Reproduction",
        "",
        "Use the locked optional Chronos/TimesFM groups. Build the ignored manifest, run the",
        "full validation benchmark, freeze the explicit selection, then run the test benchmark",
        "with --frozen-selection. Run `python -m research.pipelines.report_m2_results` to",
        "export these aggregates. Raw event rows, timestamps and IDs stay ignored.",
        "",
    ]
    path = ROOT / "docs/reports/milestone-2-model-results.md"
    path.write_text("\n".join(output), encoding="utf-8")
    print("Sanitized model report written; no row-level research data exported.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
