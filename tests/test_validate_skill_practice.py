"""Tests for scripts/validate_skill_practice.py."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "validate_skill_practice.py"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "skill_trust"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_skill_practice", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["validate_skill_practice"] = module
    spec.loader.exec_module(module)
    return module


def _valid_skill_body(*, include_procedure: bool = True, include_verification: bool = True) -> str:
    if include_procedure:
        procedure = "## Procedure\n\n1. First step.\n2. Second step.\n\n"
    else:
        procedure = "## Procedure\n\nFollow the steps in prose without numbering.\n\n"
    if include_verification:
        verification = "## Verification\n\n- [ ] Check outcome.\n\n"
    else:
        verification = "## Verification\n\nConfirm outcome in prose only.\n\n"
    return (
        "---\n"
        "name: practice-fixture\n"
        "description: Use when testing practice validation for procedure and verification rubric checks.\n"
        "---\n\n"
        "# Practice Fixture\n\n"
        "## When to use\n\n"
        "Use for practice tests.\n\n"
        "## Objective\n\n"
        "Validate rubric.\n\n"
        f"{procedure}"
        f"{verification}"
    )


class ValidateSkillPracticeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_validator_module()

    def test_practice_requires_numbered_procedure_steps(self) -> None:
        content = _valid_skill_body(include_procedure=False)
        result = self.module.validate_skill_practice_content(content, "fixture.md")
        self.assertFalse(result.passed)
        codes = {issue.code for issue in result.issues}
        self.assertIn("missing_numbered_procedure", codes)

    def test_practice_requires_verification_checkbox(self) -> None:
        content = _valid_skill_body(include_verification=False)
        result = self.module.validate_skill_practice_content(content, "fixture.md")
        self.assertFalse(result.passed)
        codes = {issue.code for issue in result.issues}
        self.assertIn("missing_verification_checkbox", codes)

    def test_practice_requires_use_when_in_description(self) -> None:
        content = (
            "---\n"
            "name: practice-fixture\n"
            "description: Missing trigger phrase in this description field.\n"
            "---\n\n"
            "# Practice Fixture\n\n"
            "## When to use\n\n"
            "Testing.\n\n"
            "## Objective\n\n"
            "Validate rubric.\n\n"
            "## Procedure\n\n"
            "1. First step.\n\n"
            "## Verification\n\n"
            "- [ ] Check outcome.\n"
        )
        result = self.module.validate_skill_practice_content(content, "fixture.md")
        self.assertFalse(result.passed)
        codes = {issue.code for issue in result.issues}
        self.assertIn("missing_use_when_trigger", codes)

    def test_practice_passes_valid_fixture(self) -> None:
        content = _valid_skill_body()
        result = self.module.validate_skill_practice_content(content, "fixture.md")
        self.assertTrue(result.passed, msg=[issue.message for issue in result.issues])

    def test_practice_passes_guardrails_teaching_fixture(self) -> None:
        path = FIXTURES / "benign" / "guardrails-teaching.md"
        result = self.module.validate_skill_practice(str(path))
        self.assertTrue(result.passed, msg=[issue.message for issue in result.issues])

    def test_practice_result_serialises_to_dict(self) -> None:
        content = _valid_skill_body(include_procedure=False)
        result = self.module.validate_skill_practice_content(content, "fixture.md")
        payload = result.to_dict()
        self.assertIn("passed", payload)
        self.assertIn("issues", payload)
        json.dumps(payload)


if __name__ == "__main__":
    unittest.main()
