"""Server-only configuration; ignored .env values are never logged."""

import os
from pathlib import Path


def load_local_configuration() -> None:
    env_file = Path(__file__).resolve().parents[3] / ".env"
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.lstrip().startswith("#") and "=" in line:
                name, value = line.split("=", 1)
                name = name.strip()
                if name and name not in os.environ:
                    os.environ[name] = value.strip().strip("\"'")


def required_setting(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing server configuration: {name}")
    return value
