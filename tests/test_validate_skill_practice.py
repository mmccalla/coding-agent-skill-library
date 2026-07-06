"""Tests for scripts/validators/validate_skill_practice.py."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts/validators/validate_skill_practice.py"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "skill_trust"
SKILLS_ROOT = REPO_ROOT / "skills"


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

    def test_rejects_duplicate_procedure_and_core_pattern(self) -> None:
        steps = "1. Define the agent card.\n2. Exchange tasks.\n3. Return artefacts.\n"
        content = (
            "---\n"
            "name: inter-agent-communication-a2a\n"
            "description: Use when agents must collaborate across boundaries.\n"
            "---\n\n"
            "# A2A\n\n"
            "## Procedure\n\n"
            f"{steps}\n"
            "## Core pattern\n\n"
            f"{steps}\n"
            "## Verification\n\n"
            "- [ ] Done.\n"
        )
        result = self.module.validate_skill_practice_content(
            content, "skills/inter-agent-communication-a2a/SKILL.md"
        )
        self.assertFalse(result.passed)
        codes = {issue.code for issue in result.issues}
        self.assertIn("duplicate_procedure_content", codes)

    def test_dora_requires_rework_rate_and_primary_source(self) -> None:
        content = (
            "---\n"
            "name: dora-four-keys\n"
            "description: Use when measuring delivery performance with DORA metrics.\n"
            "---\n\n"
            "# DORA\n\n"
            "## Procedure\n\n"
            "1. Measure deployment frequency.\n\n"
            "## Verification\n\n"
            "- [ ] Metrics defined.\n"
        )
        result = self.module.validate_skill_practice_content(
            content, "skills/dora-four-keys/SKILL.md"
        )
        self.assertFalse(result.passed)
        codes = {issue.code for issue in result.issues}
        self.assertIn("missing_standards_grounding", codes)

    def test_dora_passes_when_grounded(self) -> None:
        content = (
            "---\n"
            "name: dora-four-keys\n"
            "description: Use when measuring delivery performance with DORA metrics.\n"
            "---\n\n"
            "# DORA\n\n"
            "## Procedure\n\n"
            "1. Measure throughput and instability metrics including rework rate.\n\n"
            "## References\n\n"
            "- https://dora.dev/insights/dora-metrics-history/\n\n"
            "## Verification\n\n"
            "- [ ] Metrics defined.\n"
        )
        result = self.module.validate_skill_practice_content(
            content, "skills/dora-four-keys/SKILL.md"
        )
        self.assertTrue(result.passed, msg=[issue.message for issue in result.issues])

    def test_data_contract_requires_odcs(self) -> None:
        content = (
            "---\n"
            "name: data-contract-design\n"
            "description: Use when formalising producer-consumer data agreements.\n"
            "---\n\n"
            "# Data contracts\n\n"
            "## Procedure\n\n"
            "1. Define schema.\n\n"
            "## Verification\n\n"
            "- [ ] Contract defined.\n"
        )
        result = self.module.validate_skill_practice_content(
            content, "skills/data-contract-design/SKILL.md"
        )
        codes = {issue.code for issue in result.issues}
        self.assertIn("missing_standards_grounding", codes)

    def test_human_in_the_loop_requires_architectural_enforcement(self) -> None:
        content = (
            "---\n"
            "name: human-in-the-loop\n"
            "description: Use when high-risk actions need human approval.\n"
            "---\n\n"
            "# HITL\n\n"
            "## Procedure\n\n"
            "1. Ask the user before acting.\n\n"
            "## Verification\n\n"
            "- [ ] Approval recorded.\n"
        )
        result = self.module.validate_skill_practice_content(
            content, "skills/human-in-the-loop/SKILL.md"
        )
        codes = {issue.code for issue in result.issues}
        self.assertIn("missing_standards_grounding", codes)

    def test_all_repository_skills_pass_practice_validation(self) -> None:
        reports = self.module.validate_all_skills(SKILLS_ROOT)
        failures = [
            f"{report.skill_path}: {[issue.message for issue in report.issues]}"
            for report in reports
            if not report.passed
        ]
        self.assertEqual(failures, [], msg="\n".join(failures))


if __name__ == "__main__":
    unittest.main()
