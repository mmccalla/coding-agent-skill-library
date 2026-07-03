"""Tests for scripts/validate_skills.py."""

from __future__ import annotations

import importlib.util
import json
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
        baseline = REPO_ROOT / "skills" / "apply-laws-of-ai" / "SKILL.md"
        self.assertTrue(baseline.is_file())

    def test_pack_metadata_exists_and_covers_repository_skills(self) -> None:
        metadata_path = REPO_ROOT / "skills" / "PACK_METADATA.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

        self.assertEqual("skill-pack-metadata/v1", metadata["schema_version"])
        listed_skills = {
            skill_name for category in metadata["categories"] for skill_name in category["skills"]
        }
        repository_skills = {path.parent.name for path in (REPO_ROOT / "skills").glob("*/SKILL.md")}
        self.assertEqual(repository_skills, listed_skills)

    def test_missing_baseline_fails(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            skills_dir = Path(tmp) / "skills" / "dummy"
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
                module.BASELINE_SKILL = os.path.join("skills", "apply-laws-of-ai", "SKILL.md")
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 1)

    def test_canonical_headings_on_baseline(self) -> None:
        baseline = REPO_ROOT / "skills" / "apply-laws-of-ai" / "SKILL.md"
        text = baseline.read_text(encoding="utf-8")
        self.assertIsNotNone(re.search(r"^## When to use\s*$", text, flags=re.M))
        self.assertIsNotNone(re.search(r"^## Verification\s*$", text, flags=re.M))
        self.assertNotIn("## When to use this skill", text)
        self.assertNotIn("## Completion report", text)
        self.assertNotIn("## Output checklist", text)

    def test_description_requires_use_when_trigger(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skills" / "apply-laws-of-ai"
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
                module.BASELINE_SKILL = os.path.join("skills", "apply-laws-of-ai", "SKILL.md")
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 1)

    def test_description_length_bounds(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skills" / "apply-laws-of-ai"
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
                module.BASELINE_SKILL = os.path.join("skills", "apply-laws-of-ai", "SKILL.md")
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 1)

    def test_folder_name_must_match_frontmatter_name(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skills" / "wrong-folder-name"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: apply-laws-of-ai\n"
                "description: " + ("x" * 70) + ". Use when testing validator folder-name rule.\n"
                "---\n\n"
                "# Apply Laws of AI\n\n"
                "## When to use\n\n"
                "Every session.\n\n"
                "## Verification\n\n"
                "Report gates.\n" + ("word " * 150),
                encoding="utf-8",
            )
            baseline_dir = Path(tmp) / "skills" / "apply-laws-of-ai"
            baseline_dir.mkdir(parents=True)
            (baseline_dir / "SKILL.md").write_text(
                "---\n"
                "name: apply-laws-of-ai\n"
                "description: " + ("x" * 70) + ". Use when testing validator baseline presence.\n"
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
                module.BASELINE_SKILL = os.path.join("skills", "apply-laws-of-ai", "SKILL.md")
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 1)

    def test_verification_requires_checklist_item(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skills" / "apply-laws-of-ai"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: apply-laws-of-ai\n"
                "description: " + ("x" * 70) + ". Use when testing verification checklist rule.\n"
                "---\n\n"
                "# Apply Laws of AI\n\n"
                "## When to use\n\n"
                "Every session.\n\n"
                "## Verification\n\n"
                "Report gates only in prose without checklist items.\n" + ("word " * 150),
                encoding="utf-8",
            )
            original_root = module.ROOT
            original_baseline = module.BASELINE_SKILL
            try:
                module.ROOT = "skills"
                module.BASELINE_SKILL = os.path.join("skills", "apply-laws-of-ai", "SKILL.md")
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 1)

    def test_objective_section_is_required(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skills" / "apply-laws-of-ai"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: apply-laws-of-ai\n"
                "description: " + ("x" * 70) + ". Use when testing objective section rule.\n"
                "---\n\n"
                "# Apply Laws of AI\n\n"
                "## When to use\n\n"
                "Every session.\n\n"
                "## Verification\n\n"
                "- [ ] Report gates.\n" + ("word " * 150),
                encoding="utf-8",
            )
            original_root = module.ROOT
            original_baseline = module.BASELINE_SKILL
            try:
                module.ROOT = "skills"
                module.BASELINE_SKILL = os.path.join("skills", "apply-laws-of-ai", "SKILL.md")
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 1)

    def test_legacy_procedure_headings_fail(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skills" / "apply-laws-of-ai"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: apply-laws-of-ai\n"
                "description: " + ("x" * 70) + ". Use when testing legacy procedure heading rule.\n"
                "---\n\n"
                "# Apply Laws of AI\n\n"
                "## When to use\n\n"
                "Every session.\n\n"
                "## Objective\n\n"
                "Test objective.\n\n"
                "## Operating procedure\n\n"
                "1. Test.\n\n"
                "## Verification\n\n"
                "- [ ] Report gates.\n" + ("word " * 150),
                encoding="utf-8",
            )
            original_root = module.ROOT
            original_baseline = module.BASELINE_SKILL
            try:
                module.ROOT = "skills"
                module.BASELINE_SKILL = os.path.join("skills", "apply-laws-of-ai", "SKILL.md")
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 1)

    def test_product_specific_overlay_content_fails_in_skills(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skills" / "apply-laws-of-ai"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: apply-laws-of-ai\n"
                "description: "
                + ("x" * 70)
                + ". Use when testing product overlay isolation rule.\n"
                "---\n\n"
                "# Apply Laws of AI\n\n"
                "## When to use\n\n"
                "Every session.\n\n"
                "## Objective\n\n"
                "Test objective.\n\n"
                "## Procedure\n\n"
                "1. Test.\n\n"
                "## MAS DataOps MCP guidance\n\n"
                "Product-specific guidance should live in the overlay.\n\n"
                "## Verification\n\n"
                "- [ ] Report gates.\n" + ("word " * 150),
                encoding="utf-8",
            )
            original_root = module.ROOT
            original_baseline = module.BASELINE_SKILL
            try:
                module.ROOT = "skills"
                module.BASELINE_SKILL = os.path.join("skills", "apply-laws-of-ai", "SKILL.md")
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 1)

    def test_unsupported_frontmatter_key_fails(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skills" / "apply-laws-of-ai"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: apply-laws-of-ai\n"
                "description: " + ("x" * 70) + ". Use when testing frontmatter key restrictions.\n"
                "version: 1.0.0\n"
                "---\n\n"
                "# Apply Laws of AI\n\n"
                "## When to use\n\n"
                "Every session.\n\n"
                "## Objective\n\n"
                "Test objective.\n\n"
                "## Procedure\n\n"
                "1. Test.\n\n"
                "## Verification\n\n"
                "- [ ] Report gates.\n" + ("word " * 150),
                encoding="utf-8",
            )
            original_root = module.ROOT
            original_baseline = module.BASELINE_SKILL
            try:
                module.ROOT = "skills"
                module.BASELINE_SKILL = os.path.join("skills", "apply-laws-of-ai", "SKILL.md")
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 1)

    def test_aliases_frontmatter_is_allowed(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skills" / "apply-laws-of-ai"
            skill_dir.mkdir(parents=True)
            (Path(tmp) / "skills" / "PACK_METADATA.json").write_text(
                json.dumps(
                    {
                        "schema_version": "skill-pack-metadata/v1",
                        "skill_pack_id": "test-pack",
                        "display_name": "Test Pack",
                        "version": "1.0.0",
                        "owner": "test",
                        "source_root": "skills",
                        "categories": [
                            {
                                "id": "agent-control-patterns",
                                "title": "Agent Control Patterns",
                                "description": "Test category.",
                                "skills": ["apply-laws-of-ai"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: apply-laws-of-ai\n"
                "description: " + ("x" * 70) + ". Use when testing aliases frontmatter allowance.\n"
                "aliases:\n"
                "  - ai-safety-laws\n"
                "  - baseline-ai-safety\n"
                "---\n\n"
                "# Apply Laws of AI\n\n"
                "## When to use\n\n"
                "Every session.\n\n"
                "## Objective\n\n"
                "Test objective.\n\n"
                "## Procedure\n\n"
                "1. Test.\n\n"
                "## Verification\n\n"
                "- [ ] Report gates.\n" + ("word " * 150),
                encoding="utf-8",
            )
            original_root = module.ROOT
            original_baseline = module.BASELINE_SKILL
            try:
                module.ROOT = "skills"
                module.BASELINE_SKILL = os.path.join("skills", "apply-laws-of-ai", "SKILL.md")
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 0)

    def test_alias_collision_with_existing_skill_name_fails(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            baseline_dir = Path(tmp) / "skills" / "apply-laws-of-ai"
            baseline_dir.mkdir(parents=True)
            (baseline_dir / "SKILL.md").write_text(
                "---\n"
                "name: apply-laws-of-ai\n"
                "description: " + ("x" * 70) + ". Use when testing alias collisions.\n"
                "---\n\n"
                "# Apply Laws of AI\n\n"
                "## When to use\n\n"
                "Every session.\n\n"
                "## Objective\n\n"
                "Test objective.\n\n"
                "## Procedure\n\n"
                "1. Test.\n\n"
                "## Verification\n\n"
                "- [ ] Report gates.\n" + ("baselineword " * 210),
                encoding="utf-8",
            )
            skill_dir = Path(tmp) / "skills" / "test-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: test-skill\n"
                "description: " + ("x" * 70) + ". Use when testing alias collisions.\n"
                "aliases:\n"
                "  - apply-laws-of-ai\n"
                "---\n\n"
                "# Test Skill\n\n"
                "## When to use\n\n"
                "Use when testing.\n\n"
                "## Objective\n\n"
                "Test objective.\n\n"
                "## Procedure\n\n"
                "1. Test.\n\n"
                "## Verification\n\n"
                "- [ ] Report gates.\n" + ("thinword " * 210),
                encoding="utf-8",
            )
            original_root = module.ROOT
            original_baseline = module.BASELINE_SKILL
            try:
                module.ROOT = "skills"
                module.BASELINE_SKILL = os.path.join("skills", "apply-laws-of-ai", "SKILL.md")
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 1)

    def test_skill_over_max_line_limit_fails(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skills" / "apply-laws-of-ai"
            skill_dir.mkdir(parents=True)
            long_body = "\n".join(f"- [ ] Line {idx}" for idx in range(610))
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                "name: apply-laws-of-ai\n"
                "description: " + ("x" * 70) + ". Use when testing skill line count restrictions.\n"
                "---\n\n"
                "# Apply Laws of AI\n\n"
                "## When to use\n\n"
                "Every session.\n\n"
                "## Objective\n\n"
                "Test objective.\n\n"
                "## Procedure\n\n"
                "1. Test.\n\n"
                "## Verification\n\n"
                f"{long_body}\n",
                encoding="utf-8",
            )
            original_root = module.ROOT
            original_baseline = module.BASELINE_SKILL
            try:
                module.ROOT = "skills"
                module.BASELINE_SKILL = os.path.join("skills", "apply-laws-of-ai", "SKILL.md")
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 1)

    def test_non_baseline_skill_under_200_words_fails(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            baseline_dir = Path(tmp) / "skills" / "apply-laws-of-ai"
            baseline_dir.mkdir(parents=True)
            (Path(tmp) / "skills" / "PACK_METADATA.json").write_text(
                json.dumps(
                    {
                        "schema_version": "skill-pack-metadata/v1",
                        "skill_pack_id": "test-pack",
                        "display_name": "Test Pack",
                        "version": "1.0.0",
                        "owner": "test",
                        "source_root": "skills",
                        "categories": [
                            {
                                "id": "agent-control-patterns",
                                "title": "Agent Control Patterns",
                                "description": "Test category.",
                                "skills": ["apply-laws-of-ai"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (baseline_dir / "SKILL.md").write_text(
                "---\n"
                "name: apply-laws-of-ai\n"
                "description: "
                + ("x" * 70)
                + ". Use when testing baseline presence for minimum word validation.\n"
                "---\n\n"
                "# Apply Laws of AI\n\n"
                "## When to use\n\n"
                "Every session.\n\n"
                "## Objective\n\n"
                "Test objective.\n\n"
                "## Procedure\n\n"
                "1. Test.\n\n"
                "## Verification\n\n"
                "- [ ] Report gates.\n" + ("baselineword " * 210),
                encoding="utf-8",
            )

            thin_dir = Path(tmp) / "skills" / "thin-example"
            thin_dir.mkdir(parents=True)
            (thin_dir / "SKILL.md").write_text(
                "---\n"
                "name: thin-example\n"
                "description: "
                + ("x" * 70)
                + ". Use when testing non-baseline minimum word validation.\n"
                "---\n\n"
                "# Thin Example\n\n"
                "## When to use\n\n"
                "Use when testing.\n\n"
                "## Objective\n\n"
                "Test objective.\n\n"
                "## Procedure\n\n"
                "1. Test.\n\n"
                "## Verification\n\n"
                "- [ ] Report gates.\n" + ("thinword " * 150),
                encoding="utf-8",
            )

            original_root = module.ROOT
            original_baseline = module.BASELINE_SKILL
            try:
                module.ROOT = "skills"
                module.BASELINE_SKILL = os.path.join("skills", "apply-laws-of-ai", "SKILL.md")
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 1)

    def test_baseline_skill_is_exempt_from_minimum_word_count(self) -> None:
        module = load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            baseline_dir = Path(tmp) / "skills" / "apply-laws-of-ai"
            baseline_dir.mkdir(parents=True)
            (Path(tmp) / "skills" / "PACK_METADATA.json").write_text(
                json.dumps(
                    {
                        "schema_version": "skill-pack-metadata/v1",
                        "skill_pack_id": "test-pack",
                        "display_name": "Test Pack",
                        "version": "1.0.0",
                        "owner": "test",
                        "source_root": "skills",
                        "categories": [
                            {
                                "id": "agent-control-patterns",
                                "title": "Agent Control Patterns",
                                "description": "Test category.",
                                "skills": ["apply-laws-of-ai"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (baseline_dir / "SKILL.md").write_text(
                "---\n"
                "name: apply-laws-of-ai\n"
                "description: "
                + ("x" * 70)
                + ". Use when testing baseline minimum word count exemption.\n"
                "---\n\n"
                "# Apply Laws of AI\n\n"
                "## When to use\n\n"
                "Every session.\n\n"
                "## Objective\n\n"
                "Test objective.\n\n"
                "## Procedure\n\n"
                "1. Test.\n\n"
                "## Verification\n\n"
                "- [ ] Report gates.\n" + ("baselineword " * 80),
                encoding="utf-8",
            )

            original_root = module.ROOT
            original_baseline = module.BASELINE_SKILL
            try:
                module.ROOT = "skills"
                module.BASELINE_SKILL = os.path.join("skills", "apply-laws-of-ai", "SKILL.md")
                os.chdir(tmp)
                rc = module.main()
            finally:
                module.ROOT = original_root
                module.BASELINE_SKILL = original_baseline
            self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
