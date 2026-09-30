from __future__ import annotations

import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
MIGRATION = (
    REPOSITORY_ROOT / "supabase" / "migrations" / "20260929000100_initial_application_schema.sql"
)
SEED = REPOSITORY_ROOT / "supabase" / "seed.sql"
SUPABASE_GITIGNORE = REPOSITORY_ROOT / "supabase" / ".gitignore"

EXPECTED_TABLES = {
    "users",
    "cgm_readings",
    "insulin_events",
    "activity_events",
    "foods",
    "meals",
    "meal_items",
    "forecasts",
    "forecast_points",
    "meal_outcomes",
}


def test_migration_declares_expected_tables_and_rls() -> None:
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    for table in EXPECTED_TABLES:
        assert f"create table public.{table}" in sql
        assert f"alter table public.{table} enable row level security" in sql

    assert "create extension if not exists vector" in sql
    assert "auth.uid()" in sql
    assert "revoke all on table public.foods from anon" in sql


def test_committed_database_files_exclude_connection_details_and_credentials() -> None:
    committed_contract = "\n".join(
        (
            MIGRATION.read_text(encoding="utf-8"),
            SEED.read_text(encoding="utf-8"),
        )
    )
    forbidden_patterns = (
        r"postgres(?:ql)?://",
        r"https?://(?:localhost|127\.0\.0\.1)",
        r"\b(?:password|secret|service_role_key)\s*=",
        r"eyJ[A-Za-z0-9_-]{20,}\.",
    )

    for pattern in forbidden_patterns:
        assert re.search(pattern, committed_contract, flags=re.IGNORECASE) is None


def test_local_supabase_runtime_configuration_is_ignored() -> None:
    ignored = {
        line.lstrip("/") for line in SUPABASE_GITIGNORE.read_text(encoding="utf-8").splitlines()
    }

    assert "config.toml" in ignored
    assert ".temp/" in ignored
    assert ".env" in ignored


def test_seed_is_explicitly_synthetic_and_contains_no_contact_address() -> None:
    seed = SEED.read_text(encoding="utf-8").lower()

    assert "synthetic" in seed
    assert "data_mode" in seed
    assert "@" not in seed
