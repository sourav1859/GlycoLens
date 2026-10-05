from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[2] / "scripts" / "quality" / "validate_codex_config.py"
SPEC = importlib.util.spec_from_file_location("validate_codex_config", PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class CodexConfigValidationTests(unittest.TestCase):
    def test_repository_configuration_passes(self) -> None:
        self.assertEqual(VALIDATOR.validate(Path(__file__).resolve().parents[2]), [])

    def test_dangerous_sandbox_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".codex" / "agents").mkdir(parents=True)
            (root / ".agents" / "skills").mkdir(parents=True)
            (root / ".codex" / "config.toml").write_text(
                'model="gpt-6.1-sol"\nmodel_reasoning_effort="medium"\n'
                'tool_output_token_limit=4000\n[agents]\nmax_concurrent_threads_per_session=2\n'
                'default_subagent_model="gpt-6-luna"\ndefault_subagent_reasoning_effort="medium"\n',
                encoding="utf-8",
            )
            (root / ".codex" / "agents" / "bad.toml").write_text(
                'name="bad"\ndescription="bad"\ndeveloper_instructions="bad"\n'
                'model="gpt-6-luna"\nmodel_reasoning_effort="medium"\nsandbox_mode="danger-full-access"\n',
                encoding="utf-8",
            )
            self.assertTrue(any("dangerous sandbox" in error for error in VALIDATOR.validate(root)))


if __name__ == "__main__":
    unittest.main()
