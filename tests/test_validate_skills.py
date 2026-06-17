"""Tests for scripts/validate_skills.py."""

from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "validate_skills.py"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_skills", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ValidateSkillsTests(unittest.TestCase):
    def test_validator_passes_on_repository(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_baseline_skill_exists(self) -> None:
        baseline = (
            REPO_ROOT
            / "skills"
            / "agent-control-patterns"
            / "apply-laws-of-ai"
            / "SKILL.md"
        )
        self.assertTrue(baseline.is_file())

    def test_missing_baseline_fails(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            skills_dir = Path(tmp) / "skills" / "agent-control-patterns" / "dummy"
            skills_dir.mkdir(parents=True)
            skill_path = skills_dir / "SKILL.md"
            skill_path.write_text(
                "---\n"
                "name: dummy\n"
                "description: test skill for validator baseline check.\n"
                "---\n\n"
                "# Dummy\n\n"
                "## When to use\n\n"
                "Use for testing.\n\n"
                "## Verification\n\n"
                "Report test outcome.\n" + ("word " * 150),
                encoding="utf-8",
            )
            original_root = module.ROOT
            original_baseline = module.BASELINE_SKILL
            try:
                module.ROOT = "skills"
                module.BASELINE_SKILL = os.path.join(
                    "skills", "agent-control-patterns", "apply-laws-of-ai", "SKILL.md"
                )
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 1)


    def test_canonical_headings_on_baseline(self) -> None:
        baseline = (
            REPO_ROOT
            / "skills"
            / "agent-control-patterns"
            / "apply-laws-of-ai"
            / "SKILL.md"
        )
        text = baseline.read_text(encoding="utf-8")
        self.assertIsNotNone(re.search(r"^## When to use\s*$", text, flags=re.M))
        self.assertIsNotNone(re.search(r"^## Verification\s*$", text, flags=re.M))
        self.assertNotIn("## When to use this skill", text)
        self.assertNotIn("## Completion report", text)
        self.assertNotIn("## Output checklist", text)

    def test_description_requires_use_when_trigger(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = (
                Path(tmp)
                / "skills"
                / "agent-control-patterns"
                / "apply-laws-of-ai"
            )
            skill_dir.mkdir(parents=True)
            baseline = skill_dir / "SKILL.md"
            baseline.write_text(
                "---\n"
                "name: apply-laws-of-ai\n"
                "description: Mandatory baseline without trigger phrase.\n"
                "---\n\n"
                "# Apply Laws of AI\n\n"
                "## When to use\n\n"
                "Every session.\n\n"
                "## Verification\n\n"
                "Report gates.\n" + ("word " * 150),
                encoding="utf-8",
            )
            original_root = module.ROOT
            original_baseline = module.BASELINE_SKILL
            try:
                module.ROOT = "skills"
                module.BASELINE_SKILL = os.path.join(
                    "skills", "agent-control-patterns", "apply-laws-of-ai", "SKILL.md"
                )
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 1)

    def test_description_length_bounds(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = (
                Path(tmp)
                / "skills"
                / "agent-control-patterns"
                / "apply-laws-of-ai"
            )
            skill_dir.mkdir(parents=True)
            baseline = skill_dir / "SKILL.md"
            baseline.write_text(
                "---\n"
                "name: apply-laws-of-ai\n"
                "description: Short. Use when testing.\n"
                "---\n\n"
                "# Apply Laws of AI\n\n"
                "## When to use\n\n"
                "Every session.\n\n"
                "## Verification\n\n"
                "Report gates.\n" + ("word " * 150),
                encoding="utf-8",
            )
            original_root = module.ROOT
            original_baseline = module.BASELINE_SKILL
            try:
                module.ROOT = "skills"
                module.BASELINE_SKILL = os.path.join(
                    "skills", "agent-control-patterns", "apply-laws-of-ai", "SKILL.md"
                )
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 1)

    def test_folder_name_must_match_frontmatter_name(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = (
                Path(tmp)
                / "skills"
                / "agent-control-patterns"
                / "wrong-folder-name"
            )
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: apply-laws-of-ai\n"
                "description: "
                + ("x" * 70)
                + ". Use when testing validator folder-name rule.\n"
                "---\n\n"
                "# Apply Laws of AI\n\n"
                "## When to use\n\n"
                "Every session.\n\n"
                "## Verification\n\n"
                "Report gates.\n" + ("word " * 150),
                encoding="utf-8",
            )
            baseline_dir = (
                Path(tmp)
                / "skills"
                / "agent-control-patterns"
                / "apply-laws-of-ai"
            )
            baseline_dir.mkdir(parents=True)
            (baseline_dir / "SKILL.md").write_text(
                "---\n"
                "name: apply-laws-of-ai\n"
                "description: "
                + ("x" * 70)
                + ". Use when testing validator baseline presence.\n"
                "---\n\n"
                "# Apply Laws of AI\n\n"
                "## When to use\n\n"
                "Every session.\n\n"
                "## Verification\n\n"
                "Report gates.\n" + ("word " * 150),
                encoding="utf-8",
            )
            original_root = module.ROOT
            original_baseline = module.BASELINE_SKILL
            try:
                module.ROOT = "skills"
                module.BASELINE_SKILL = os.path.join(
                    "skills", "agent-control-patterns", "apply-laws-of-ai", "SKILL.md"
                )
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 1)

    def test_verification_requires_checklist_item(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = (
                Path(tmp)
                / "skills"
                / "agent-control-patterns"
                / "apply-laws-of-ai"
            )
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: apply-laws-of-ai\n"
                "description: "
                + ("x" * 70)
                + ". Use when testing verification checklist rule.\n"
                "---\n\n"
                "# Apply Laws of AI\n\n"
                "## When to use\n\n"
                "Every session.\n\n"
                "## Verification\n\n"
                "Report gates only in prose without checklist items.\n"
                + ("word " * 150),
                encoding="utf-8",
            )
            original_root = module.ROOT
            original_baseline = module.BASELINE_SKILL
            try:
                module.ROOT = "skills"
                module.BASELINE_SKILL = os.path.join(
                    "skills", "agent-control-patterns", "apply-laws-of-ai", "SKILL.md"
                )
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 1)

    def test_objective_section_is_required(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = (
                Path(tmp)
                / "skills"
                / "agent-control-patterns"
                / "apply-laws-of-ai"
            )
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: apply-laws-of-ai\n"
                "description: "
                + ("x" * 70)
                + ". Use when testing objective section rule.\n"
                "---\n\n"
                "# Apply Laws of AI\n\n"
                "## When to use\n\n"
                "Every session.\n\n"
                "## Verification\n\n"
                "- [ ] Report gates.\n"
                + ("word " * 150),
                encoding="utf-8",
            )
            original_root = module.ROOT
            original_baseline = module.BASELINE_SKILL
            try:
                module.ROOT = "skills"
                module.BASELINE_SKILL = os.path.join(
                    "skills", "agent-control-patterns", "apply-laws-of-ai", "SKILL.md"
                )
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 1)

    def test_legacy_procedure_headings_fail(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = (
                Path(tmp)
                / "skills"
                / "agent-control-patterns"
                / "apply-laws-of-ai"
            )
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: apply-laws-of-ai\n"
                "description: "
                + ("x" * 70)
                + ". Use when testing legacy procedure heading rule.\n"
                "---\n\n"
                "# Apply Laws of AI\n\n"
                "## When to use\n\n"
                "Every session.\n\n"
                "## Objective\n\n"
                "Test objective.\n\n"
                "## Operating procedure\n\n"
                "1. Test.\n\n"
                "## Verification\n\n"
                "- [ ] Report gates.\n"
                + ("word " * 150),
                encoding="utf-8",
            )
            original_root = module.ROOT
            original_baseline = module.BASELINE_SKILL
            try:
                module.ROOT = "skills"
                module.BASELINE_SKILL = os.path.join(
                    "skills", "agent-control-patterns", "apply-laws-of-ai", "SKILL.md"
                )
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 1)


if __name__ == "__main__":
    unittest.main()
