#!/usr/bin/env python3
"""Validate immediate repository-scoped skill directories using the standard library."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PLACEHOLDER_PATTERN = re.compile(r"\b(?:TODO|TBD|FIXME|PLACEHOLDER)\b", re.IGNORECASE)


def parse_frontmatter(text: str) -> tuple[dict[str, str] | None, str | None]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "YAML frontmatter must start on the first line"

    try:
        closing = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        return None, "YAML frontmatter has no closing delimiter"

    fields: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:closing], start=2):
        if not line.strip():
            return None, f"frontmatter line {line_number} is blank"
        if line[:1].isspace() or ":" not in line:
            return None, f"frontmatter line {line_number} is malformed"
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            return None, f"frontmatter line {line_number} requires a key and value"
        if key in fields:
            return None, f"frontmatter field {key!r} is duplicated"
        fields[key] = value

    if set(fields) != {"name", "description"}:
        return None, "frontmatter must contain exactly name and description"
    return fields, None


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        return ["SKILL.md is missing"]

    try:
        text = skill_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [f"SKILL.md could not be read as UTF-8: {exc}"]

    fields, frontmatter_error = parse_frontmatter(text)
    if frontmatter_error:
        errors.append(frontmatter_error)
    else:
        assert fields is not None
        name = fields["name"]
        if not NAME_PATTERN.fullmatch(name):
            errors.append("name must use lowercase letters, digits, and single hyphens")
        if name != skill_dir.name:
            errors.append(f"name {name!r} does not match folder {skill_dir.name!r}")
        if not fields["description"].strip():
            errors.append("description is empty")

    for candidate in sorted(path for path in skill_dir.rglob("*") if path.is_file()):
        try:
            candidate_text = candidate.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        if PLACEHOLDER_PATTERN.search(candidate_text):
            errors.append(f"placeholder marker detected in {candidate.relative_to(skill_dir)}")
    return errors


def main() -> int:
    default_root = Path(__file__).resolve().parents[2] / ".agents" / "skills"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=default_root)
    args = parser.parse_args()
    root = args.root.resolve()

    if not root.is_dir():
        print(f"ERROR: skills root does not exist: {root}", file=sys.stderr)
        return 1

    skill_dirs = sorted(path for path in root.iterdir() if path.is_dir())
    if not skill_dirs:
        print(f"ERROR: no skill directories found under {root}", file=sys.stderr)
        return 1

    failures = 0
    for skill_dir in skill_dirs:
        errors = validate_skill(skill_dir)
        if errors:
            failures += 1
            print(f"FAIL {skill_dir.name}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS {skill_dir.name}")

    print(f"Validated {len(skill_dirs)} skill(s); failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
