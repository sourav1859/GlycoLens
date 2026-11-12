"""GL-P00-004/007: real network and private release contents are rejected."""

from pathlib import Path

import httpx
import pytest

from scripts.quality.check_public_files import inspect_file


def test_private_key_canary_is_detected_without_returning_contents(tmp_path):
    file = tmp_path / "source.py"
    file.write_text("sb_secret_" + "x" * 32)
    assert inspect_file(file, "source.py") == "possible_private_credential"


@pytest.mark.parametrize(
    "relative", [".env", "frontend/.env.local", ".cache/source.py", "artifacts/models/weights.pt"]
)
def test_private_paths_are_rejected(tmp_path, relative):
    assert inspect_file(tmp_path / Path(relative).name, relative) == "private_or_generated_path"


def test_public_template_is_allowed(tmp_path):
    file = tmp_path / ".env.example"
    file.write_text("SUPABASE_SECRET_KEY=\nLLM_MODEL=gpt-6-luna\n")
    assert inspect_file(file, ".env.example") is None


def test_offline_transport_guard_is_installed(request):
    if not request.config.pluginmanager.hasplugin("scripts.quality.offline_pytest"):
        pytest.skip("Network-denial check is run explicitly in the offline CI command")
    with pytest.raises(AssertionError, match="network access is disabled"):
        httpx.get("https://network-must-not-be-contacted.invalid")
