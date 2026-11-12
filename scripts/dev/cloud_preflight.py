"""Cloud-only, credential-redacted readiness and integration target guards.

Default execution is read-only and offline. This module never creates users,
sends email, runs migrations, or starts/resets a local Supabase stack.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import sys
from uuid import uuid4

from scripts.dev.check_m2_prerequisites import tool_version

ROOT = Path(__file__).resolve().parents[2]
APPROVED_PROJECT_REF = "ecynkzptuslkuhjikzfc"
APPROVED_URL = f"https://{APPROVED_PROJECT_REF}.supabase.co"
CONFIG_NAMES = (
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SECRET_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "GLYCOLENS_CLOUD_PROJECT_REF",
    "LLM_API_KEY",
    "LLM_MODEL",
    "USDA_FDC_API_KEY",
    "OPEN_FOOD_FACTS_USER_AGENT",
)


class CloudTargetError(ValueError):
    """Messages intentionally identify requirements, never supplied values."""


@dataclass(frozen=True)
class CloudRun:
    project_ref: str
    url: str
    run_id: str


def new_run_id() -> str:
    return "gl_" + uuid4().hex[:24]


def read_configuration(root: Path = ROOT) -> dict[str, str]:
    values = {}
    path = root / ".env"
    if path.is_file():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if line.strip() and not line.lstrip().startswith("#") and "=" in line:
                name, value = line.split("=", 1)
                values[name.strip()] = value.strip().strip("\"'")
    values.update(os.environ)
    return values


def validate_identity(values: dict[str, str]) -> None:
    if values.get("SUPABASE_URL", "").strip() not in {APPROVED_URL, APPROVED_URL + "/"}:
        raise CloudTargetError("SUPABASE_URL must identify the approved cloud development project")
    if values.get("GLYCOLENS_CLOUD_PROJECT_REF", "").strip() != APPROVED_PROJECT_REF:
        raise CloudTargetError(
            "GLYCOLENS_CLOUD_PROJECT_REF must match the approved development project"
        )


def assert_cloud_run(values: dict[str, str], *, allow_cloud: bool, run_id: str) -> CloudRun:
    """Call before constructing a live test client or dispatching ANY mutation."""
    validate_identity(values)
    if not allow_cloud:
        raise CloudTargetError("Cloud integration requires explicit --allow-cloud intent")
    if not re.fullmatch(r"gl_[a-f0-9]{24}", run_id):
        raise CloudTargetError("Cloud integration requires a generated run-scoped identifier")
    if not values.get("SUPABASE_ANON_KEY", "").strip():
        raise CloudTargetError("A public Supabase client key is required")
    if not (
        values.get("SUPABASE_SECRET_KEY", "").strip()
        or values.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    ):
        raise CloudTargetError("A server-only Supabase key is required")
    return CloudRun(APPROVED_PROJECT_REF, APPROVED_URL, run_id)


def eligible_cloud_job(event: str, ref: str, *, protected: bool, enabled: bool) -> bool:
    return event == "workflow_dispatch" and ref == "refs/heads/main" and protected and enabled


def configuration_report(values: dict[str, str]) -> dict:
    presence = {name: bool(values.get(name, "").strip()) for name in CONFIG_NAMES}
    try:
        validate_identity(values)
        identity_valid = True
    except CloudTargetError:
        identity_valid = False
    return {
        "configuration_present": presence,
        "target_identity_valid": identity_valid,
        "approved_project_ref": APPROVED_PROJECT_REF,
        "cloud_configuration_ready": identity_valid
        and presence["SUPABASE_ANON_KEY"]
        and (presence["SUPABASE_SECRET_KEY"] or presence["SUPABASE_SERVICE_ROLE_KEY"]),
        "local_supabase_required": False,
        "research_dataset_required": False,
        "contains_credentials": False,
        "open_food_facts_contact_ready": bool(
            re.fullmatch(
                r"GlycoLens/[\w.]+ \([^\s()@]+@[^\s()@]+\.[^\s()@]+\)",
                values.get("OPEN_FOOD_FACTS_USER_AGENT", ""),
            )
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = configuration_report(read_configuration())
    tools = {name: tool_version(name) for name in ("uv", "node", "pnpm", "supabase", "docker")}
    report.update(
        {
            "python_version": sys.version.split()[0],
            "supported_python": sys.version_info[:2] == (3, 12),
            "tools": tools,
        }
    )
    report["toolchain_ready"] = (
        report["supported_python"]
        and tools["uv"]["available"]
        and tools["node"]["available"]
        and bool(re.match(r"v22\.", str(tools["node"].get("version", ""))))
        and tools["pnpm"]["available"]
        and bool(re.match(r"10\.", str(tools["pnpm"].get("version", ""))))
    )
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["cloud_configuration_ready"] and report["toolchain_ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
