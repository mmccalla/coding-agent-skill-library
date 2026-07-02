"""Tests for scripts/validate_skill_mapping.py."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "validate_skill_mapping.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_skill_mapping", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["validate_skill_mapping"] = module
    spec.loader.exec_module(module)
    return module


class ValidateSkillMappingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_validator()

    def test_krag_system_design_predicts_promoted(self) -> None:
        path = str(REPO_ROOT / "skills" / "krag-system-design" / "SKILL.md")
        result = self.module.validate_skill_mapping_file(path)
        self.assertTrue(result.passed)
        self.assertEqual("promoted", result.promotion_prediction)
        self.assertIn("krag-architecture", {item["task_intent_id"] for item in result.task_intents})

    def test_unknown_skill_without_mapping_quarantines(self) -> None:
        markdown = """---
name: empty-skill
description: A skill with no governed mapping signals.
---

# Empty

## When to use
Use for nothing in particular.
"""
        result = self.module.validate_skill_mapping_file("skills/empty-skill/SKILL.md", markdown=markdown)
        self.assertFalse(result.passed)
        self.assertEqual("quarantined", result.promotion_prediction)


if __name__ == "__main__":
    unittest.main()
