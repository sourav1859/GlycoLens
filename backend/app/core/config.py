"""Small environment-backed configuration surface for the local API slice."""

from __future__ import annotations

import os


DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)


def cors_origins() -> tuple[str, ...]:
    """Return explicit browser origins; wildcard CORS is intentionally unsupported."""

    configured = os.environ.get("GLYCOLENS_CORS_ORIGINS", "")
    if not configured.strip():
        return DEFAULT_CORS_ORIGINS
    origins = tuple(
        origin.strip().rstrip("/") for origin in configured.split(",") if origin.strip()
    )
    if not origins or "*" in origins:
        raise ValueError("GLYCOLENS_CORS_ORIGINS must contain explicit origins")
    return origins
