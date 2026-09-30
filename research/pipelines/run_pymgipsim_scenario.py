"""Run the pinned Milestone 1 py-mgipsim feasibility scenario."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from research.simulation.adapter import PyMgipsimError, run_pymgipsim_scenario

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = REPOSITORY_ROOT / ".cache" / "pymgipsim-source"
DEFAULT_PYTHON = REPOSITORY_ROOT / ".cache" / "pymgipsim-venv" / "Scripts" / "python.exe"
DEFAULT_OUTPUT = REPOSITORY_ROOT / "artifacts" / "simulation" / "m1-pymgipsim-scenario.json"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-upstream-execution", action="store_true")
    parser.add_argument("--source-directory", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--python-executable", type=Path, default=DEFAULT_PYTHON)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if not args.allow_upstream_execution:
        raise SystemExit(
            "Refusing to run external simulator code without --allow-upstream-execution"
        )
    try:
        result = run_pymgipsim_scenario(
            source_directory=args.source_directory,
            python_executable=args.python_executable,
            output_json=args.output_json,
        )
    except PyMgipsimError as exc:
        raise SystemExit(str(exc)) from exc

    summary = asdict(result)
    summary.pop("trajectory")
    summary["output_json"] = str(args.output_json.resolve().relative_to(REPOSITORY_ROOT))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
