"""Render aggregate Phase 6 evidence; no raw records, fitting or test-based selection."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from research.pipelines.prepare_metabonet import ROOT
from research.pipelines.run_metabonet_independent import OUTPUT, PRIMARY, verify_phase6_stage


def render(directory):
    for stage in ("calibration", "test"):
        verify_phase6_stage(directory / stage, stage)
    calibration = json.loads((directory / "calibration/summary.json").read_text())
    test = json.loads((directory / "test/summary.json").read_text())
    state = json.loads((directory / "calibration/bands.json").read_text())
    primary = test["cohorts"]["primary_test"]["models"][PRIMARY]
    pediatric = test["cohorts"]["source_test"]["models"][PRIMARY]
    m = calibration["participant_count"]
    rank = math.ceil((m + 1) * 0.8)
    lines = [
        "# MetaboNet Phase 6 independent evaluation — October 16, 2026",
        "",
        "Phase 6 is complete. The primary research candidate was frozen as original Phase 4 "
        "LightGBM before calibration or reserved outcomes. Original Ridge is a diagnostic "
        "challenger; persistence is the baseline. No test-based reselection, point-model "
        "refitting, Chronos calls, clipping, app switch or clinical validation occurred.",
        "",
        f"**Average error improved, but tight precision remains poor.** LightGBM's primary "
        f"trajectory MAE is {primary['participant_macro']['mae']:.2f} mg/dL, with "
        f"{primary['participant_macro']['within_10']:.2%} of points within +/-10. PEDAP MAE is "
        f"{pediatric['participant_macro']['mae']:.2f}, within-10 "
        f"{pediatric['participant_macro']['within_10']:.2%}. The nominal 80% marginal band "
        f"covers {primary['intervals']['marginal']['macro_point_coverage']:.2%} on the primary "
        f"cohort but only {pediatric['intervals']['marginal']['macro_point_coverage']:.2%} on PEDAP. "
        "The average-error gate is confirmed; broad pediatric reliability is not.",
        "",
        "## Calibration and execution",
        "",
        f"There were {calibration['eligible_events']:,} eligible 24-hour calibration meals. "
        f"One hash-selected meal per participant supplied {m} "
        "source-qualified participant representatives; actual independence/exchangeability is unverified. "
        f"The 80% finite-sample rule uses order statistic {rank} out of {m}, separately per horizon "
        "and for maximum whole-curve error. These are empirical symmetric bands; their q10/q90 "
        "labels are not learned conditional quantiles. Calibration does not improve point accuracy.",
        "",
        "| Predictor | Marginal radius 30 min | 60 min | 120 min | Whole-curve radius |",
        "|---|---:|---:|---:|---:|",
    ]
    names = ("persistence", PRIMARY, "ridge_direct")
    for name in names:
        band = state["models"][name]
        lines.append(
            f"| {name} | {band['radii'][5]:.2f} | {band['radii'][11]:.2f} | "
            f"{band['radii'][23]:.2f} | {band['curve_radius']:.2f} |"
        )
    lines += [
        "",
        "Radii and all errors below are mg/dL. Both bands were frozen in a verified "
        "calibration completion before raw reserved CGM/event projection. All four loaded "
        "numerical pools reported two threads. Point-model state and original bundles "
        "were unchanged. Sources, configurations, original inputs, rows and artifacts "
        "are checksummed in separate execution snapshots.",
        "",
        "## Reserved-cohort eligibility",
        "",
        "All 169 reserved identities were screened. Candidate origins were hash-selected "
        "before eligibility, at most 100 per participant across permitted file segments. "
        "PEDAP histories/targets were never borrowed across publisher-file boundaries. "
        "The unchanged isolated-meal rule examines later meal entries retrospectively; "
        "these scores do not represent every live meal.",
        "",
        "| Cohort | Reserved IDs | Eligible IDs | Candidate origins | Eligible meals |",
        "|---|---:|---:|---:|---:|",
    ]
    for role in ("primary_test", "source_test"):
        c = test["cohort"][role]
        lines.append(
            f"| {role} | {c['reserved_identities']} | {c['eligible_identities']} | "
            f"{c['sampled_candidate_count']:,} | {c['eligible_events']:,} |"
        )
    lines += [
        "",
        f"Partial exact fingerprint screening: {test['cohort']['reference_distinct_fingerprints']:,} "
        f"distinct development reference sequences and {test['cohort']['all_distinct_fingerprints']:,} "
        f"distinct sequences overall. {test['cohort']['quarantined_identities']} reserved IDs "
        f"were quarantined; {test['cohort']['contaminated_development_references']} development "
        "references were flagged. These rounded, hourly-endpoint checks cannot prove "
        "global person uniqueness or absence of foundation pretraining overlap.",
        "",
    ]
    for role, title in (
        ("primary_test", "Primary: unseen Loop/ReplaceBG identities"),
        ("source_test", "Source shift: pediatric PEDAP"),
    ):
        cohort = test["cohort"][role]
        summary = test["cohorts"][role]
        lines += [
            f"## {title}",
            "",
            f"Preparation statuses: `{json.dumps(cohort['status_counts'], sort_keys=True)}`. "
            f"Rejections among ready subjects: `{json.dumps(cohort['rejections_ready_subjects'], sort_keys=True)}`.",
            "",
        ]
        if "models" not in summary:
            lines += ["No eligible meals; no accuracy claim.", ""]
            continue
        lines += [
            "Primary accuracy averages each participant's meal-level metrics equally. "
            "Tail errors pool all successful CGM points. All models attempt identical eligible "
            "events; failures remain in attempted-event yields. Common-success summaries "
            "are diagnostic and do not replace per-model denominators.",
            "",
            "| Predictor | MAE | RMSE | Within +/-10 | Whole curve within +/-10 | Pooled p95 | Max | Failed |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for name in names:
            result = summary["models"][name]
            m, p = result["participant_macro"], result["point_metrics"]
            lines.append(
                f"| {name} | {m['mae']:.2f} | {m['rmse']:.2f} | {m['within_10']:.2%} | "
                f"{m['whole_curve_within_10']:.2%} | {p['absolute_error_p95']:.2f} | "
                f"{p['max_absolute_error']:.2f} | {result['failure_count']} |"
            )
        gate = summary["frozen_primary_confirmation_gate"]
        ci = summary["paired_mae_intervals"][PRIMARY + "_minus_persistence"]
        lines += [
            "",
            f"Frozen LightGBM confirmation gate **{'passed' if gate['passes'] else 'failed'}**: "
            f"MAE improvement {gate['mae_improvement_fraction']:.2%}. The rule requires at least "
            "10% lower MAE, within-10 nondecrease, pooled p95 nonincrease and no failed forecasts. "
            f"LightGBM-minus-persistence macro MAE difference {ci['macro_mae_difference']:.2f}, "
            f"descriptive participant-bootstrap 95% interval [{ci['bootstrap_95_low']:.2f}, "
            f"{ci['bootstrap_95_high']:.2f}] (10,000 draws, seed20261016). "
            "No model is selected again using these test scores.",
            "",
            "| Predictor | MAE at 30 min | 60 min | 120 min | Within-10 at 120 min | Attempted whole-curve yield |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for name in names:
            r = summary["models"][name]
            m = r["participant_macro"]
            lines.append(
                f"| {name} | {m['absolute_error_30']:.2f} | {m['absolute_error_60']:.2f} | "
                f"{m['absolute_error_120']:.2f} | {m['within_10_120']:.2%} | "
                f"{r['attempted_event_whole_curve_yield']:.2%} |"
            )
        lines += [
            "",
            "| Predictor | Marginal point coverage | Marginal whole-curve coverage | Mean marginal width | Curve-band whole-curve coverage | Curve-band width | Negative marginal lower points |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
        for name in names:
            m = summary["models"][name]["intervals"]["marginal"]
            c = summary["models"][name]["intervals"]["curve"]
            lines.append(
                f"| {name} | {m['macro_point_coverage']:.2%} | {m['macro_whole_curve_coverage']:.2%} | "
                f"{m['mean_width']:.2f} | {c['macro_whole_curve_coverage']:.2%} | "
                f"{c['mean_width']:.2f} | {m['negative_lower_points']:,} |"
            )
        lines += [
            "",
            "Coverage above is participant-macro. Marginal 80% targets individual "
            "time points, while the separate curve band targets the complete 24-point "
            "trajectory. Broad bands can cover well while point forecasts remain inaccurate. "
            "Coverage under study shift is empirical, with no pediatric or individual guarantee.",
            "",
            "| Predictor | Marginal coverage 30 min | 60 min | 120 min | Lowest horizon coverage |",
            "|---|---:|---:|---:|---:|",
        ]
        for name in names:
            band = summary["models"][name]["intervals"]["marginal"]
            lines.append(
                f"| {name} | {band['macro_coverage_30']:.2%} | "
                f"{band['macro_coverage_60']:.2%} | {band['macro_coverage_120']:.2%} | "
                f"{min(band['macro_coverage_by_horizon']):.2%} |"
            )
        lines += [
            "",
            "An overall coverage average can hide poorly covered horizons. The primary "
            "cohort's near-80% average does not establish 80% coverage at every horizon.",
            "",
            "| Predeclared subgroup | Meals | IDs with primary success | LightGBM MAE | Within +/-10 | Marginal point coverage |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for label, group in summary["subgroups"].items():
            r = group["models"][PRIMARY]
            m = r["participant_macro"]
            if m:
                lines.append(
                    f"| {label} | {group['event_count']:,} | {r['participant_count']} | "
                    f"{m['mae']:.2f} | {m['within_10']:.2%} | "
                    f"{r['intervals']['marginal']['macro_point_coverage']:.2%} |"
                )
        r = summary["models"][PRIMARY]
        lines += [
            "",
            "Participant MAE min / quartile1 / median / quartile3 / max: "
            + " / ".join(f"{v:.2f}" for v in r["participant_mae_percentiles"])
            + ". "
            "Subgroups may overlap; small groups and incomplete record masks do not "
            "establish physiology, logging completeness or causal effects.",
            "",
        ]
    lines += [
        "## Interpretation and next steps",
        "",
        "The +/-10 aspiration remains unmet. Neither MAE nor interval coverage is an "
        "overall percentage accuracy score. Point errors, whole-curve tolerance, tails "
        "and subgroup variation must be considered together. No maximum-error or "
        "clinical claim follows from this experiment.",
        "",
        "Trajectory MAE averages errors across all 24 future time points; the two-hour "
        "endpoint is harder (primary LightGBM MAE 40.90, PEDAP 52.91). Complete-curve "
        "within-10 is only 0.94% and 0.18%, respectively. PEDAP's within-10 improvement "
        "over persistence is effectively negligible (19.57% versus 19.56%), even though "
        "the prespecified nondecrease gate passes. Primary mean marginal width is 96.73 "
        "mg/dL; the separate curve band is 160.70 wide. These widths expose uncertainty "
        "rather than deliver precise predictions. Only 48 calibration representatives "
        "also limit the stability of estimated radii.",
        "",
        "Both reserved cohorts are now consumed. Keep this run as confirmation/diagnostic "
        "evidence; any new model or feature tuning requires fresh confirmation data. "
        "The next research iteration should improve source-appropriate development data, "
        "meal/insulin timing and participant adaptation, using development-only grouped "
        "validation before another locked evaluation. Application integration and "
        "remaining M2 live prerequisites require separate work.",
        "",
        f"Measured calibration stage {calibration['elapsed_seconds']:.2f} seconds; "
        f"test preparation/scoring {test['elapsed_seconds']:.2f} seconds, excluding "
        "initial prior-artifact/raw hashing. Logs preserve all warnings. No data upload.",
        "",
        "## Reproduction",
        "",
        "```powershell",
        ".venv/Scripts/python.exe -m research.pipelines.run_metabonet_independent --stage calibration --verify-only",
        ".venv/Scripts/python.exe -m research.pipelines.run_metabonet_independent --stage test --verify-only",
        ".venv/Scripts/python.exe -m research.pipelines.report_metabonet_independent",
        "```",
        "",
        "Original stages used the same commands without `--verify-only`, "
        "calibration first. Completed outputs refuse replay. Ignored artifacts: "
        "`artifacts/evaluation-results/metabonet-phase6-v1/{calibration,test}/`. "
        "The initial protocol is archived in both source ZIPs; later living-document "
        "completion notes do not change the execution record.",
        "",
        "See [frozen protocol](../planning/GlycoLens_16_MetaboNet_Independent_Evaluation.md), "
        "[decision](../decisions/0014-independent-testing-and-participant-calibration.md) and "
        "[verification handoff](../tooling/metabonet-phase6-handoff-2026-10-16.md).",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=OUTPUT)
    parser.add_argument(
        "--report",
        type=Path,
        default=ROOT / "docs/reports/metabonet-phase6-independent-2026-10-16.md",
    )
    args = parser.parse_args()
    args.report.write_text(render(args.directory), encoding="utf-8")


if __name__ == "__main__":
    main()
