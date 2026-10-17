"""Read-only milestone preflight; never print configuration values or health records."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG_KEYS = (
    "GLYCOLENS_T1D_UOM_ROOT",
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "USDA_FDC_API_KEY",
    "OPEN_FOOD_FACTS_USER_AGENT",
    "LLM_API_KEY",
    "LLM_MODEL",
)


def configuration_presence() -> dict[str, bool]:
    """Inspect only named configuration entries; values never leave this function."""
    values = {key: os.environ.get(key, "").strip() for key in CONFIG_KEYS}
    env_file = ROOT / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.lstrip().startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if key in values and not values[key]:
                values[key] = value.strip().strip("\"'")
    return {key: bool(value) for key, value in values.items()}


def tool_version(name: str) -> dict[str, object]:
    executable = shutil.which(name)
    if not executable:
        return {"available": False}
    try:
        result = subprocess.run(
            [executable, "--version"], capture_output=True, text=True, timeout=20, check=False
        )
        # Only version commands are invoked, never status/configuration commands.
        return {"available": result.returncode == 0, "version": result.stdout.strip()[:100]}
    except (OSError, subprocess.TimeoutExpired):
        return {"available": False, "error": "version_check_failed"}


def main() -> int:
    tools = {name: tool_version(name) for name in ("uv", "node", "pnpm", "docker", "supabase")}
    supported_python = sys.version_info[:2] == (3, 12)
    report = {
        "python_version": sys.version.split()[0],
        "supported_python": supported_python,
        "tools": tools,
        "configuration_present": configuration_presence(),
        "local_supabase_config_present": (ROOT / "supabase/config.toml").is_file(),
        "simulator_source_present": (ROOT / ".cache/pymgipsim-source/pymgipsim").is_dir(),
        "simulator_python_present": (ROOT / ".cache/pymgipsim-venv/Scripts/python.exe").is_file(),
        "contains_secrets_or_health_records": False,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if supported_python and all(item["available"] for item in tools.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
