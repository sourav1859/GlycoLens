from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


VALIDATOR_PATH = Path(__file__).resolve().parents[2] / "scripts" / "quality" / "validate_skills.py"
SPEC = importlib.util.spec_from_file_location("validate_skills", VALIDATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class SkillPrivacyValidationTests(unittest.TestCase):
    def _write_skill(self, root: Path, body: str) -> Path:
        skill_dir = root / "sample-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            "---\n"
            "name: sample-skill\n"
            "description: Exercise the repository skill validator.\n"
            "---\n\n"
            f"{body}\n",
            encoding="utf-8",
        )
        return skill_dir

    def test_literal_email_address_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            skill_dir = self._write_skill(
                Path(temporary_directory),
                "Contact `person@example.invalid`.",
            )

            errors = VALIDATOR.validate_skill(skill_dir)

            self.assertTrue(any("literal email address" in error for error in errors))

    def test_environment_variable_reference_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            skill_dir = self._write_skill(
                Path(temporary_directory),
                "Resolve the address from `GLYCOLENS_ADVISOR_EMAIL_SENDER`.",
            )

            self.assertEqual(VALIDATOR.validate_skill(skill_dir), [])


if __name__ == "__main__":
    unittest.main()
