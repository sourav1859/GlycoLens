#!/usr/bin/env python3
"""Validate repository-scoped Codex configuration using the standard library."""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
FORBIDDEN = ("danger-full-access", "service_tier = \"fast\"", "service_tier = \"ultrafast\"")


def load_toml(path: Path) -> tuple[dict, list[str]]:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8")), []
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        return {}, [f"{path}: cannot parse TOML: {exc}"]


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    config_path = root / ".codex" / "config.toml"
    config, parse_errors = load_toml(config_path)
    errors.extend(parse_errors)
    if parse_errors:
        return errors
    if config.get("model") != "gpt-6.1-sol" or config.get("model_reasoning_effort") != "medium":
        errors.append("project default must be gpt-6.1-sol with medium reasoning")
    if not isinstance(config.get("tool_output_token_limit"), int) or config["tool_output_token_limit"] > 4000:
        errors.append("tool_output_token_limit must be an integer no greater than 4000")
    if "profiles" in config or "profile" in config:
        errors.append("deprecated repository profile structures are not allowed")
    agents = config.get("agents", {})
    if agents.get("max_concurrent_threads_per_session", 99) > 2:
        errors.append("agent concurrency must not exceed 2")
    if agents.get("default_subagent_model") != "gpt-6-luna" or agents.get("default_subagent_reasoning_effort") != "medium":
        errors.append("bounded subagents must default to gpt-6-luna with medium reasoning")

    names: set[str] = set()
    agent_dir = root / ".codex" / "agents"
    for path in sorted(agent_dir.glob("*.toml")):
        data, agent_errors = load_toml(path)
        errors.extend(agent_errors)
        if agent_errors:
            continue
        for field in ("name", "description", "developer_instructions", "model", "model_reasoning_effort"):
            if not isinstance(data.get(field), str) or not data[field].strip():
                errors.append(f"{path}: missing non-empty {field}")
        name = data.get("name")
        if name in names:
            errors.append(f"{path}: duplicate custom-agent name {name!r}")
        names.add(name)
        text = path.read_text(encoding="utf-8")
        if EMAIL.search(text):
            errors.append(f"{path}: literal private email address is not allowed")
        lowered = text.lower()
        if any(value in lowered for value in FORBIDDEN):
            errors.append(f"{path}: dangerous sandbox or fast service tier is not allowed")

    for path in [config_path, *sorted(agent_dir.glob("*.toml"))]:
        lowered = path.read_text(encoding="utf-8").lower()
        if any(value in lowered for value in FORBIDDEN):
            errors.append(f"{path}: dangerous sandbox or fast service tier is not allowed")

    skill_root = root / ".agents" / "skills"
    for skill in sorted(skill_root.glob("*/SKILL.md")):
        match = re.search(r"^description:\s*(.+)$", skill.read_text(encoding="utf-8"), re.M)
        if match and len(match.group(1).strip()) > 240:
            errors.append(f"{skill}: skill description exceeds 240 characters")
    return errors


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
    errors = validate(root)
    if errors:
        print("Codex configuration validation: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Codex configuration validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
