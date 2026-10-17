"""Publish only aggregate refinement results; never copy row-level artifacts."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "artifacts/evaluation-results/refinement-v1"


def metric_table(summary):
    lines = [
        "| Model | MAE mg/dL | Points within ±10 | Whole curves within ±10 | Point p95 error | Point p99 error | Worst error | Failures |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, run in summary["runs"].items():
        macro, point = run["participant_macro"], run["point_metrics"]
        lines.append(
            f"| {name} | {macro['mae']:.3f} | {100 * macro['within_10']:.2f}% | "
            f"{100 * macro['whole_curve_within_10']:.2f}% | {point['absolute_error_p95']:.2f} | "
            f"{point['absolute_error_p99']:.2f} | {point['max_absolute_error']:.2f} | {run['failure_count']} |"
        )
    return lines


def tolerance_table(summary, names):
    lines = [
        "| Model | Within ±10 at 30 min | At 60 min | At 120 min | Attempted-point ±10 yield | Attempted-event whole-curve yield |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name in names:
        run = summary["runs"][name]
        macro = run["participant_macro"]
        lines.append(
            f"| {name} | {100 * macro['within_10_30']:.2f}% | "
            f"{100 * macro['within_10_60']:.2f}% | {100 * macro['within_10_120']:.2f}% | "
            f"{100 * run['attempted_point_within_10_yield']:.2f}% | "
            f"{100 * run['attempted_event_whole_curve_yield']:.2f}% |"
        )
    return lines


def main():
    results = json.loads((ARTIFACTS / "results.json").read_text())
    history = json.loads((ARTIFACTS / "history-summary.json").read_text())
    validation = json.loads((ARTIFACTS / "validation-summary.json").read_text())
    calibration = json.loads((ARTIFACTS / "validation-calibration.json").read_text())
    provenance = json.loads((ARTIFACTS / "provenance.json").read_text())
    selection = results["selection"]
    external = results["external"]
    lines = [
        "# Model refinement results — October 16, 2026",
        "",
        "Executed locally after user approval. **Research only; ±10 mg/dL is an aspiration, "
        "not a maximum-error guarantee.** The application model was not switched.",
        "",
        "## Decision and interpretation",
        "",
        "**The proposed improvement did not generalize to AZT1D. Do not promote the new "
        "model into the application.** It improved selected UOM validation, but its external "
        "MAE, ±10 rate and error tail were slightly worse than persistence. The external "
        "paired interval includes zero, so this establishes no reliable advantage in either "
        "direction. Performance is far from an 80% within-±10 objective.",
        "",
        f"The frozen shared-feature choice is **{selection['winners']['shared']}**, with "
        f"**{selection['history_hours']} hours** of CGM history. The full-nutrition choice is "
        f"**{selection['winners']['full']}**. Persistence was eligible to win either comparison.",
        "",
        "MAE is the average size of an error, in the same units as glucose. The ±10 rate "
        "counts individual readings close to the recorded value. A whole-curve pass requires "
        "all 24 predictions for a meal to stay within ±10. None of these is an overall "
        "classification accuracy percentage. The p95 error means 95% of evaluated point "
        "errors are at or below that value; it is not a maximum guarantee.",
        "",
        "Model selection uses participant-average full-trajectory MAE, then higher ±10 rate "
        "for ties. Each participant has equal weight. Tail errors are pooled across matched "
        "points. All candidate selection used UOM validation; external predictions were "
        "computed only after writing the immutable selection artifact.",
        "",
        "## Data and exclusions",
        "",
        "The original 927-event M2 manifest and validation/test artifacts remain read-only. "
        "The previously inspected original test is diagnostic in this study. Calibration "
        "uses the final 20% of each participant's original development time interval, with "
        "target-boundary purging. Longer-history survivors retain original split assignments.",
        "",
        "| History | Training | Calibration | Validation | Old test, diagnostic |",
        "|---|---:|---:|---:|---:|",
    ]
    for hours, counts in sorted(
        results["cohort"]["eligible_by_history_split"].items(), key=lambda x: int(x[0])
    ):
        lines.append(
            f"| {hours} h | {counts.get('train', 0)} | {counts.get('calibration', 0)} | "
            f"{counts.get('validation', 0)} | {counts.get('diagnostic', 0)} |"
        )
    lines += [
        "",
        "Longer histories lose meals with insufficient/gapped CGM. These meals were not "
        "removed after seeing prediction errors. Future meals/CGM/insulin are unavailable "
        "to every model request. No glucose clipping or hard-case deletion was used.",
        "",
        "## Frozen Chronos history comparison",
        "",
        f"All-history eligibility: **{history['requested_event_count']} events**; common successful "
        f"validation: **{history['common_success_event_count']} events**. One 24-hour request failed "
        "the forecast contract. Failures stay in attempted yields; metrics use common successes. "
        "The implemented ranking admits failure-free candidates only. Six hours also has the "
        "lowest matched MAE irrespective of that eligibility rule.",
        "",
        *metric_table(history),
        "",
        "Available-event sensitivity (different survivor sets; unsuitable for a direct ranking):",
        "",
        "| History | Available events | MAE mg/dL | Points within ±10 |",
        "|---|---:|---:|---:|",
    ]
    for name, value in history["available_event_summaries"].items():
        run = value["runs"][name]
        lines.append(
            f"| {name} | {value['requested_event_count']} | "
            f"{run['participant_macro']['mae']:.3f} | {100 * run['participant_macro']['within_10']:.2f}% |"
        )
    lines += [
        "",
        "## Small-model and residual validation",
        "",
        f"Selected-history cohort: {selection['training_event_count']} training, "
        f"{selection['calibration_event_count']} separate calibration, "
        f"{selection['validation_event_count']} validation meals. Validation was used to "
        f"choose candidates across {validation['runs']['persistence']['participant_count']} participants, "
        "so selected validation improvements are optimistic. Full-nutrient and shared residual "
        "heads are separate selections; additional nutrient features did not improve the best "
        "validation MAE over the shared head. This is not a controlled causal nutrient ablation.",
        "",
        "Ridge alphas 1/10/100; LightGBM leaves 7/15, 150 trees, learning rate .03, "
        "min_child_samples 20. Standardization and patient-equal fitting weights use training "
        "only. Direct models predict change from the latest glucose; residual models correct "
        "a frozen CGM-only Chronos forecast. The foundation model was never trained. Shared "
        "features use CGM, local clock, recorded bolus and current/earlier carbohydrates. Full "
        "features additionally use recorded protein/fat/fibre. Basal values are omitted because "
        "their units are ambiguous. No participant ID or invented insulin-action estimate is used.",
        "",
        *metric_table(validation),
        "",
        *tolerance_table(
            validation, sorted(set(selection["winners"].values()) | {"persistence", "chronos_c0"})
        ),
        "",
        "Endpoint rates are participant-average. Attempted yields use all requested points/events, "
        "with failures counting as unsuccessful, so they have a different weighting from macro rates.",
        "",
        "Proposed gate: ≥10% lower MAE than matched persistence, no lower ±10 rate, and no "
        "higher pooled p95 error. This is a research improvement gate, not clinical acceptance.",
        "",
    ]
    for feature, gate in results["validation_gate"].items():
        comparison = results["validation_comparisons"][feature]
        lines += [
            f"- {feature}: MAE improvement {100 * gate['mae_improvement_fraction']:.2f}%; "
            f"gate **{'passed' if gate['passes'] else 'failed'}**. Paired MAE delta "
            f"{comparison['mae_delta']:.3f}, participant-bootstrap 95% interval "
            f"[{comparison['ci95'][0]:.3f}, {comparison['ci95'][1]:.3f}] mg/dL."
        ]
    lines += [
        "",
        "Bootstrap: 10,000 participant-cluster draws, seed 20261016. These intervals "
        "are descriptive and do not adjust for candidate selection.",
        "",
        "## Separate calibration",
        "",
        "Symmetric horizon-specific bands use held-out calibration absolute residuals and "
        "a finite-sample corrected empirical 80% quantile. Calibration changes bands, not "
        "point forecasts. Temporal dependence and cohort shift prevent a formal conditional "
        "or clinical coverage claim.",
        "",
        "| Model | Calibration events | Validation coverage | Mean width mg/dL |",
        "|---|---:|---:|---:|",
    ]
    for name, value in calibration.items():
        if value["available"]:
            lines.append(
                f"| {name} | {value['calibration_count']} | "
                f"{100 * value['participant_macro_coverage']:.2f}% | {value['mean_width_mg_dl']:.2f} |"
            )
    lines += ["", "## Independent AZT1D test", ""]
    if external["executed"]:
        audit = external["cohort"]
        lines += [
            f"**{audit['eligible_events']} eligible meals, {audit['eligible_participants']} participants**. "
            "The public V1 archive passed SHA-256 and byte-size checks. Only canonical CGM Records "
            "files were loaded; Visual Statistics exports were excluded. Missing detailed nutrients "
            "were never treated as observed zero inputs. The shared model was not refitted or "
            "retuned on AZT1D. Exact duplicate rows collapse; conflicting same-time glucose values "
            "and nonpositive/nonfinite glucose are removed before windowing. Same CGM gap and "
            "follow-up-meal rules apply. Total bolus is used once; correction dose is not added again.",
            "",
            *metric_table(external["summary"]),
            "",
            *tolerance_table(external["summary"], external["summary"]["runs"]),
            "",
            f"External MAE improvement: {100 * external['gate']['mae_improvement_fraction']:.2f}%; "
            f"proposed gate **{'passed' if external['gate']['passes'] else 'failed'}**. Paired MAE "
            f"delta {external['paired_mae']['mae_delta']:.3f} mg/dL, 95% participant-bootstrap interval "
            f"[{external['paired_mae']['ci95'][0]:.3f}, {external['paired_mae']['ci95'][1]:.3f}].",
            "",
            "| Exclusion reason | Events |",
            "|---|---:|",
        ]
        for reason, count in audit["rejections"].items():
            lines.append(f"| {reason} | {count} |")
        lines += [
            "",
            "External coverage using UOM calibration, without external recalibration:",
            "",
        ]
        for name, value in external["calibrated_intervals"].items():
            lines.append(
                f"- {name}: {100 * value['participant_macro_coverage']:.2f}% coverage, "
                f"{value['mean_width_mg_dl']:.2f} mg/dL mean width."
            )
        lines += [
            "",
            "Two external backbone requests returned crossing quantiles and were rejected by "
            "the existing forecast contract (ModelInferenceError caused by ForecastValidationError). "
            "Both failures reproduced in a separate diagnostic. They remain failed requests; no "
            "quantile sorting, output clipping, replacement prediction or test-based retuning was used. "
            "Matched accuracy uses 2,608 successes; attempted yields use all 2,610 requests.",
            "",
            "Source audit (aggregate):",
            "",
            "```json",
            json.dumps(audit["source_audit"], indent=2),
            "```",
            "",
            "No exact rounded aligned history-plus-target trajectories overlapped with the UOM "
            "cohort or another eligible external event. This cannot prove the absence of shared "
            "people across sources. AZT1D's AID cohort/device modes differ from UOM; mode is "
            "not a shared predictor. The schema of one canonical file is labelled CGM/BGM, "
            "which remains a source modality limitation. The tested AZT1D set is now consumed: "
            "later tuning requires a new untouched test or a declared exploratory analysis.",
        ]
    else:
        lines.append("Not executed; do not claim external generalization.")
    audit = results["legacy_audit"]
    lines += [
        "",
        "## Original-result reproduction and large-error audit",
        "",
        f"Re-ran original Chronos C3 on the 211 diagnostic requests. Matched original "
        f"successful results: {audit['matched_reference_count']}; failures: {audit['failure_count']}. "
        f"Largest per-event MAE reproduction difference: "
        f"{audit['maximum_mae_reproduction_difference']:.6f} mg/dL.",
        "",
        f"Forecast values span {audit['prediction_min']:.2f}–{audit['prediction_max']:.2f} mg/dL; "
        f"recorded targets span {audit['truth_min']:.2f}–{audit['truth_max']:.2f} mg/dL. "
        f"Worst point error: {audit['worst_event']['max_error']:.2f} mg/dL. That event's "
        f"trajectory MAE is {audit['worst_event']['mae']:.2f}, recorded range "
        f"{audit['worst_event']['truth_range']:.2f}, forecast range "
        f"{audit['worst_event']['prediction_range']:.2f} mg/dL. This is a numeric/source/forecast "
        "audit, not a clinical adjudication of the underlying trace. No outlier was removed.",
        "A negative glucose forecast is physically impossible: this is an observed model failure, "
        "not an acceptable glucose estimate. Clipping would conceal it without proving predictive skill. "
        "The all-211 legacy macro MAE below differs from the original all-model-matched 208-event "
        "MAE (37.920); this is a denominator difference, not a replacement of the original result.",
        "",
        *metric_table(audit["summary"]),
        "",
        "## Reproduction and retained evidence",
        "",
        "See `research/README.md` for commands. Private artifacts under "
        "`artifacts/evaluation-results/refinement-v1/` include source/package/protocol hashes, "
        "immutable selection, model state, all attempted row-level predictions/failure types, "
        "calibration residuals and summaries. Never commit those files. Serialized estimators "
        "are trusted-local artifacts only; residual models require the pinned C0 backbone to "
        "be explicitly reattached. Timing includes original cache misses and study work; "
        "cache-hit timings in comparisons are inherited inference measurements, not fresh "
        "serving benchmarks.",
        "The post-run integrity check verified every retained result hash, unchanged original "
        "artifacts/selection, and exact saved-head reload predictions on all 162 validation events "
        "for both heads (maximum difference 0). The protocol hash records the initial execution "
        "snapshot; later ledger status/documentation updates do not change its frozen research rules.",
        "The exact executed research sources and initial protocol are retained in an ignored "
        "39-file ZIP and verified against these hashes. Reporting/verification helpers and a "
        "guard preventing writes into a frozen run were added afterwards; they do not change "
        "the executed prediction code. Use the verification command on this completed run.",
        "",
        f"Execution: {results['elapsed_seconds'] / 60:.2f} minutes, CPU, two Torch threads, "
        f"Python {provenance['python']}; package versions: "
        + ", ".join(f"{k} {v}" for k, v in provenance["packages"].items())
        + ".",
        "",
        f"Frozen selection UTC: {selection['frozen_at_utc']}. "
        f"Original validation SHA-256: `{provenance['original_validation_sha256']}`; "
        f"original test SHA-256: `{provenance['original_test_sha256']}`.",
        "",
        "## Next decision",
        "",
        "The local sequence is executed; the external improvement gate failed. Do not promise "
        "±10 or 80% within tolerance or promote this head. The user chose local data "
        "first; MetaboNet acquisition/training is deferred. A larger genuinely separate "
        "development cohort, retained source/subject provenance, and a new independent test "
        "are the next prerequisites for further tuning. Optional LoRA/TCN work is a later "
        "experiment, not evidence of improvement. Keep the two-hour target and report shorter "
        "horizons separately. M2 live nutrition, physical camera and presentation gates remain separate.",
        "Before more model training, audit event timing/bolus/meal missingness and cohort shifts "
        "using development data. Add a larger source-distinct development cohort; keep a new "
        "independent cohort untouched. Then predeclare a small temporal/subject-validation study "
        "for direct models, a compact glucose-specific network or supported LoRA, with the same "
        "persistence and failure controls. No particular architecture can be promised to reach ±10.",
        "",
        "AZT1D attribution: Saman Khamesian, Asiful Arefeen, Bithika M. Thompson, Adela Grando "
        "and Hassan Ghasemzadeh (2025), V1, DOI 10.17632/gk9m674wcx.1, CC BY 4.0.",
        "",
        "Sources: [AZT1D V1 and CC BY 4.0 licence](https://data.mendeley.com/datasets/gk9m674wcx/1), "
        "[Ridge documentation](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html), "
        "[LightGBM API](https://lightgbm.readthedocs.io/en/stable/Python-API.html).",
        "",
    ]
    destination = ROOT / "docs/reports/model-refinement-results-2026-10-16.md"
    destination.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote aggregate report: {destination.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
