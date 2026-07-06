"""Tests for scripts/validate_skill_security.py."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts/validators/validate_skill_security.py"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "skill_trust"
ALLOWLIST = REPO_ROOT / "tests" / "fixtures" / "skill_security_allowlist.json"
GUARDRAILS_SKILL = REPO_ROOT / "skills" / "guardrails-safety-patterns" / "SKILL.md"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_skill_security", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["validate_skill_security"] = module
    spec.loader.exec_module(module)
    return module


class ValidateSkillSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_validator_module()

    def test_security_blocks_instruction_override(self) -> None:
        path = FIXTURES / "malicious" / "instruction-override.md"
        result = self.module.validate_skill_security(str(path), allowlist_path=str(ALLOWLIST))
        self.assertFalse(result.passed)
        categories = {violation.category for violation in result.violations}
        self.assertIn("instruction_override", categories)

    def test_security_blocks_disable_checks(self) -> None:
        path = FIXTURES / "malicious" / "disable-checks.md"
        result = self.module.validate_skill_security(str(path), allowlist_path=str(ALLOWLIST))
        self.assertFalse(result.passed)
        categories = {violation.category for violation in result.violations}
        self.assertIn("privilege_escalation", categories)

    def test_security_blocks_secrets(self) -> None:
        path = FIXTURES / "malicious" / "fake-pem-key.md"
        result = self.module.validate_skill_security(str(path), allowlist_path=str(ALLOWLIST))
        self.assertFalse(result.passed)
        categories = {violation.category for violation in result.violations}
        self.assertIn("secret_exfiltration", categories)

    def test_security_blocks_destructive_without_escalation(self) -> None:
        path = FIXTURES / "malicious" / "destructive-rm.md"
        result = self.module.validate_skill_security(str(path), allowlist_path=str(ALLOWLIST))
        self.assertFalse(result.passed)
        categories = {violation.category for violation in result.violations}
        self.assertIn("destructive_commands", categories)

    def test_security_allowlist_guardrails_teaching_fixture(self) -> None:
        path = FIXTURES / "benign" / "guardrails-teaching.md"
        result = self.module.validate_skill_security(str(path), allowlist_path=str(ALLOWLIST))
        self.assertTrue(result.passed, msg=[v.message for v in result.violations])
        self.assertTrue(result.allowlisted)

    def test_security_allowlist_guardrails_skill(self) -> None:
        result = self.module.validate_skill_security(
            str(GUARDRAILS_SKILL), allowlist_path=str(ALLOWLIST)
        )
        self.assertTrue(result.passed, msg=[v.message for v in result.violations])

    def test_security_policy_extensible_via_fixture(self) -> None:
        malicious_dir = FIXTURES / "malicious"
        fixture_names = sorted(path.name for path in malicious_dir.glob("*.md"))
        self.assertGreaterEqual(len(fixture_names), 4)
        for fixture_name in fixture_names:
            with self.subTest(fixture=fixture_name):
                path = malicious_dir / fixture_name
                result = self.module.validate_skill_security(
                    str(path), allowlist_path=str(ALLOWLIST)
                )
                self.assertFalse(result.passed, msg=f"{fixture_name} should be blocked")

    def test_security_result_serialises_to_dict(self) -> None:
        path = FIXTURES / "malicious" / "instruction-override.md"
        result = self.module.validate_skill_security(str(path), allowlist_path=str(ALLOWLIST))
        payload = result.to_dict()
        self.assertIn("passed", payload)
        self.assertIn("violations", payload)
        json.dumps(payload)


if __name__ == "__main__":
    unittest.main()
