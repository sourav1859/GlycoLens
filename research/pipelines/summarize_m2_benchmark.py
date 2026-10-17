"""Display sanitized aggregates; optionally freeze an explicit validation selection."""

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result", type=Path)
    parser.add_argument("--freeze-run")
    args = parser.parse_args()
    path = args.result.resolve()
    if not path.is_relative_to((ROOT / "artifacts/evaluation-results").resolve()):
        raise SystemExit("Read only ignored research result artifacts.")
    summary = json.loads(path.read_text(encoding="utf-8"))["summary"]
    print(
        json.dumps(
            {
                "split": summary["split"],
                "limited_pilot": summary["limited_pilot"],
                "requested_events": summary["requested_event_count"],
                "common_success_events": summary["common_success_event_count"],
                "runs": {
                    name: {
                        "failures": run["failure_count"],
                        "participant_macro_mae": run["matched_metrics"]
                        .get("mae", {})
                        .get("participant_macro_mean"),
                        "wall_p95_ms": run["wall_ms_p95"],
                    }
                    for name, run in summary["runs"].items()
                },
            },
            indent=2,
        )
    )
    if args.freeze_run:
        if summary["split"] != "validation" or summary["limited_pilot"]:
            raise SystemExit("Selection requires a full validation run.")
        if args.freeze_run not in summary["runs"] or args.freeze_run.startswith("persistence:"):
            raise SystemExit("Choose an evaluated pretrained model/configuration.")
        model, context = args.freeze_run.split(":", 1)
        if not summary["runs"][args.freeze_run]["matched_metrics"]:
            raise SystemExit("Selected configuration has no usable matched results.")
        selection = {
            "split": "validation",
            "selection_frozen": True,
            "model": model,
            "context": context,
            "feature_version": summary["feature_version"],
            "model_identity": summary["model_identities"][model],
            "validation_artifact": path.name,
        }
        target = path.parent / "m2-selection.json"
        target.write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")
        print("Validation selection frozen in ignored artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
