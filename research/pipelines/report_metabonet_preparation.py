"""Publish Phase 2 aggregate preparation evidence. Never read raw/test outcomes."""

import json
from pathlib import Path

from research.pipelines.prepare_metabonet import verify_preparation

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "artifacts/evaluation-results/metabonet-phase2-v1"


def main():
    verify_preparation(OUTPUT)
    summary = json.loads((OUTPUT / "summary.json").read_text())
    protocol = json.loads((OUTPUT / "frozen-protocol.json").read_text())
    lines = [
        "# MetaboNet Phase 2 implementation and preparation results - October 16, 2026",
        "",
        "**Phase 2 development preparation is executed. No model was trained, no forecast "
        "was generated and no reserved test outcome was projected.** Counts below describe "
        "data eligibility, not prediction accuracy. The next stage is frozen-inference "
        "validation under this new protocol.",
        "",
        "## Implemented behavior",
        "",
        "The loader uses native mg/dL, grams and previous-five-minute IU amounts. A bounded "
        "DuckDB query projects selected publisher-training rows in subject/time order, then "
        "Python processes one subject at a time. It retains source-qualified IDs and missing "
        "event values, emits record-presence masks, and converts prepared records to immutable "
        "ForecastRequest plus separate ForecastTarget objects. No future CGM/insulin values "
        "enter requests, no full nutrients are invented and total insulin is not added to "
        "its components. The adapter entry point can return CGM-only requests for Chronos.",
        "",
        "Development sources are Loop and ReplaceBG. Stable subject-hash ordering within "
        "each source assigns 70/15/15 to train/validation/calibration. Metadata-only quotas "
        "select up to 100/25/25 subjects per source before seeing targets. Subjects rejected "
        "by quality checks are not replaced. No source/subject identity is a model feature.",
        "",
        "## Selected development pool",
        "",
        "| Source | Split | Selected IDs |",
        "|---|---|---:|",
    ]
    for r in summary["selected_development"]:
        lines.append(f"| {r['source']} | {r['split']} | {r['subject_count']} |")
    lines += [
        "",
        f"Selected subjects contain {summary['positive_carb_rows_in_selected_subjects']:,} "
        f"positive carbohydrate rows. Stable event-hash sampling keeps **{summary['sampled_candidate_count']:,} "
        "candidate origins**, at most 100 per subject, independent of future CGM. The same "
        "origins/IDs are used across histories and timing variants.",
        "",
        "## Eligible development windows",
        "",
        "Primary six-hour totals:",
        "",
        "| Split | Eligible windows | IDs with eligible windows |",
        "|---|---:|---:|",
    ]
    for split in ("train", "validation", "calibration"):
        events = sum(
            v.get("6h_delay5", 0)
            for k, v in summary["eligible_events"].items()
            if k.startswith(split + ":")
        )
        subjects = sum(
            v.get("6h_delay5", 0)
            for k, v in summary["eligible_subjects"].items()
            if k.startswith(split + ":")
        )
        lines.append(f"| {split} | {events:,} | {subjects} |")
    lines += [
        "",
        "Primary timing assumes carbs are available five minutes after their recorded bin. "
        "The zero-minute alternative is development-only sensitivity. Each window forecasts "
        "24 five-minute readings from its availability origin, not a proven exact physical "
        "meal start. Each cell below is eligible events / IDs with at least one eligible event.",
        "",
        "| Split / source | 2 h | 6 h | 12 h | 24 h |",
        "|---|---:|---:|---:|---:|",
    ]
    for group, counts in sorted(summary["eligible_events"].items()):
        cells = []
        for h in (2, 6, 12, 24):
            key = f"{h}h_delay5"
            cells.append(
                f"{counts.get(key, 0):,} / {summary['eligible_subjects'][group].get(key, 0)}"
            )
        lines.append("| " + group + " | " + " | ".join(cells) + " |")
    lines += [
        "",
        "Zero-minute timing sensitivity:",
        "",
        "| Split / source | 2 h | 6 h | 12 h | 24 h |",
        "|---|---:|---:|---:|---:|",
    ]
    for group, counts in sorted(summary["eligible_events"].items()):
        lines.append(
            "| "
            + group
            + " | "
            + " | ".join(f"{counts.get(f'{h}h_delay0', 0):,}" for h in (2, 6, 12, 24))
            + " |"
        )
    lines += [
        "",
        "## Exclusions and source quality",
        "",
        "History uses exact relative grids; up to 10 minutes of last-past-value fill is allowed "
        "with at least 90% positive finite source readings on the requested history grid. "
        "No interpolation uses later CGM. Every target must contain 24 finite positive exact-grid "
        "source values; targets are not imputed. Extreme positive values are retained; no "
        "outcome clipping or error-based deletion. Record-present cannot certify raw sensor "
        "observation or recover upstream harmonization.",
        "",
        "A positive carb entry within the previous 15 minutes, or any later entry through "
        "forecast end, rejects the window. Identical carb amounts are not arbitrarily merged. "
        "This defines a **retrospectively isolated logged-meal benchmark**; future-meal "
        "exclusion is not a live forecast capability. Scores later obtained on this set "
        "must not be presented as performance on all real-world meals.",
        "",
        "| Primary variant | Rejection reason | Candidate origins |",
        "|---|---|---:|",
    ]
    for variant, reasons in sorted(summary["rejection_counts"].items()):
        if variant.endswith("delay5"):
            for reason, count in sorted(reasons.items()):
                lines.append(f"| {variant} | {reason} | {count:,} |")
    lines += [
        "",
        f"Exact varied six-hour CGM fingerprints checked: {summary['distinct_fingerprints_checked']:,}; "
        f"duplicate-candidate IDs quarantined: {summary['duplicate_candidate_subject_count']}. "
        "All selected IDs sharing a fingerprint are excluded, independent of split. Checks "
        "are partial and exact, require at least 20 distinct readings/range 20 mg/dL, and cannot "
        "prove distinct people across studies. Full subject-quality records stay ignored.",
        "",
        "Quality-status counts: `"
        + json.dumps(summary["quality_status_counts"], sort_keys=True)
        + "`.",
        "Here ready means the projected subject passed structural processing; it does not "
        "mean a candidate passed meal-window eligibility. Compare eligible IDs with "
        "selected quotas above; subjects with no eligible windows were not replaced.",
        "",
        "## Reserved testing and untouched values",
        "",
        f"Primary reserved test: **{summary['primary_test_subject_count']} source-qualified IDs** "
        "from publisher test, absent from all publisher-training identities in the same study. "
        f"Source test: **{summary['source_test_subject_count']} PEDAP IDs** across its publisher "
        "files, excluded from all development. PEDAP is a pediatric source shift and will be "
        "reported separately. Hidden aliases remain possible until further provenance checks.",
        "",
        "**Eligible test-event counts are deliberately not computed yet.** Only source/ID/date/"
        "publisher flags were projected from test, and no PEDAP values were included in the "
        "development projection. Future test construction/scoring needs frozen model/history/"
        "preprocessing selection; reuse the fixed window policy and candidate cap, report all "
        "eligibility/failures, and do not tune against those outcomes.",
        "",
        "AZT1D/UOM copies, OhioT1DM and the other nonpilot sources are outside development. "
        "OhioT1DM remains pending current terms confirmation. BrisT1D/CTR3 merged insulin and "
        "IOBP2 all-insulin-as-bolus are not silently substituted into conventional bolus inputs.",
        "",
        "## Frozen artifacts and reproduction",
        "",
        "Ignored output: `artifacts/evaluation-results/metabonet-phase2-v1/`. It includes the "
        "subject manifest, all predeclared assignments/quotas, subject quality/exclusion records, "
        "compressed window records, sorted development projection, summary and code snapshot. "
        "The frozen protocol hashes every retained artifact; a separate SHA-256 file protects "
        "the protocol itself. The build refuses an existing final directory. It uses a separate "
        "staging directory and publishes only after preparation checks. Corrupted data fails "
        "verification; the development iterator rejects reserved test split names. Before "
        "yielding records it checks protocol, split-quality metadata and window hashes. "
        "The final consumer guard and verification-before-publication ordering were added "
        "after the real run; its executed source snapshot remains unchanged. Real artifacts "
        "passed post-publication verification and the final verifier; no policy/window changed. "
        "The report generator verifies frozen artifacts first.",
        "",
        "```powershell",
        "uv sync --all-groups",
        "uv run --no-sync python -m research.pipelines.prepare_metabonet",
        "uv run --no-sync python -m research.pipelines.prepare_metabonet --verify-only",
        "uv run --no-sync python -m research.pipelines.report_metabonet_preparation",
        "```",
        "",
        "Do not rerun preparation into the completed directory. Use verify-only; a changed "
        "scientific policy needs a new version/output, not overwriting the frozen evidence. "
        "Downloaded data, dictionary HTML/resources, projections, windows and all IDs/times "
        "remain ignored and excluded from Graphify. No app DB/schema/frontend/model changed.",
        "",
        f"Preparation elapsed: {summary['elapsed_seconds'] / 60:.2f} minutes. Two query threads, "
        "2GB query memory budget, one streaming reader thread. Input identity:",
        "",
        "| File | SHA-256 |",
        "|---|---|",
    ]
    for name, evidence in protocol["inputs"].items():
        lines.append(f"| {name} | `{evidence['sha256']}` |")
    lines += [
        "",
        "Synthetic acceptance/integration tests cover causal fill, target separation, units, "
        "fractional carbs, fixed-offset cadence, nearby meals, deterministic/source-qualified "
        "splits, stable event IDs, exact fingerprints, metadata-only reserved testing (fixture "
        "test has no numeric outcome columns), replay protection and artifact corruption. "
        "Final regression/integrity evidence is in the "
        "[Phase 2 handoff](../tooling/metabonet-phase2-handoff-2026-10-16.md).",
        "",
        "## Next stage",
        "",
        "Phase 3 runs frozen inference on this validation data, comparing histories on matched "
        "events and reporting all eligible/failure counts. Training/calibration/test roles "
        "remain fixed. The six-hour UOM choice is a candidate, not a guaranteed optimum here. "
        "Small-model training and Chronos corrections follow validation design; no gain toward "
        "+/-10 or clinical accuracy can be claimed from successful data preparation.",
        "",
        "Protocol: [planning document 12](../planning/GlycoLens_12_MetaboNet_Experiment.md). "
        "Prerequisites: [intake audit](metabonet-intake-audit-2026-10-16.md), "
        "[dictionary review](metabonet-dictionary-review-2026-10-16.md).",
        "",
    ]
    destination = ROOT / "docs/reports/metabonet-phase2-preparation-2026-10-16.md"
    destination.write_text("\n".join(lines), encoding="utf-8")
    print("Wrote aggregate report:", destination.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
