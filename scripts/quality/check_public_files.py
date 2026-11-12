"""Fail on private files/credentials in Git candidates; never print their contents."""

import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
PRIVATE_KEY = re.compile(
    r"\b(?:sb_secret_[A-Za-z0-9_-]{20,}|sk-(?:proj-)?[A-Za-z0-9_-]{30,})|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
)
PRIVATE_SUFFIXES = {
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".safetensors",
    ".ckpt",
    ".pt",
    ".pth",
    ".parquet",
    ".sqlite",
    ".db",
}


def inspect_file(path: Path, relative: str) -> str | None:
    parts = Path(relative).parts
    if (
        path.suffix.lower() in PRIVATE_SUFFIXES
        or any(p in {".cache", "graphify-out", "node_modules"} for p in parts)
        or (path.name.startswith(".env") and path.name != ".env.example")
        or (
            relative.startswith(
                ("data/raw/", "data/interim/", "data/processed/", "artifacts/models/")
            )
            and path.name != ".gitkeep"
        )
    ):
        return "private_or_generated_path"
    try:
        if PRIVATE_KEY.search(path.read_text(encoding="utf-8")):
            return "possible_private_credential"
    except (UnicodeError, OSError):
        pass
    return None


def main() -> int:
    files = (
        subprocess.check_output(
            [
                "git",
                "-c",
                f"safe.directory={ROOT.as_posix()}",
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                "-z",
            ],
            cwd=ROOT,
        )
        .decode()
        .split("\0")
    )
    findings = [
        {"path": f, "reason": reason}
        for f in sorted(set(files))
        if f and (ROOT / f).is_file() and (reason := inspect_file(ROOT / f, f))
    ]
    required = {
        ".env",
        ".env.*",
        "**/.env",
        "**/.env.*",
        ".cache",
        "data",
        "artifacts",
        "graphify-out",
        ".git",
        "*.key",
        "*.pem",
    }
    docker_patterns = set((ROOT / ".dockerignore").read_text().splitlines())
    missing = sorted(required - docker_patterns)
    print(
        json.dumps(
            {
                "files_checked": len(set(files) - {""}),
                "findings": findings,
                "missing_image_exclusions": missing,
            },
            indent=2,
        )
    )
    return 1 if findings or missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
