"""Tests for deterministic skills graph extraction."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXTRACTOR = REPO_ROOT / "scripts" / "extract_skills_graph.py"


def load_extractor_module():
    spec = importlib.util.spec_from_file_location("extract_skills_graph", EXTRACTOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SkillsGraphExtractorTests(unittest.TestCase):
    def test_extracts_one_stable_skill_record_per_skill_file(self) -> None:
        module = load_extractor_module()

        records = module.extract_skills_graph_records(REPO_ROOT / "skills")
        skill_ids = {skill["id"] for skill in records["skills"]}

        self.assertEqual(len(records["skills"]), 87)
        self.assertIn("skill:apply-laws-of-ai", skill_ids)
        self.assertEqual(records["root_skill"], "apply-laws-of-ai")

    def test_skill_records_conform_to_ontology_property_contract(self) -> None:
        module = load_extractor_module()

        records = module.extract_skills_graph_records(REPO_ROOT / "skills")
        skill = next(
            skill for skill in records["skills"] if skill["id"] == "skill:apply-laws-of-ai"
        )

        for key in (
            "id",
            "name",
            "title",
            "description",
            "path",
            "contentHash",
            "wordCount",
            "lineCount",
            "isBaselineSkill",
        ):
            self.assertIn(key, skill)
        self.assertEqual(skill["path"], "skills/agent-control-patterns/apply-laws-of-ai/SKILL.md")
        self.assertTrue(skill["isBaselineSkill"])
        self.assertGreater(skill["wordCount"], 0)
        self.assertGreater(skill["lineCount"], 0)
        self.assertNotIn("source_path", skill)
        self.assertNotIn("source_hash", skill)

    def test_extracts_canonical_sections_with_stable_hashes(self) -> None:
        module = load_extractor_module()

        records = module.extract_skills_graph_records(REPO_ROOT / "skills")
        sections = [
            section
            for section in records["sections"]
            if section["skill_id"] == "skill:apply-laws-of-ai"
        ]
        headings = {section["heading"] for section in sections}

        self.assertIn("When to use", headings)
        self.assertIn("Verification", headings)
        self.assertTrue(all(section["contentHash"] for section in sections))
        self.assertTrue(all(section["name"] for section in sections))
        self.assertTrue(
            all(section["id"].startswith("skill:apply-laws-of-ai:section:") for section in sections)
        )

    def test_bridge_records_are_provenanced_and_cover_every_skill(self) -> None:
        module = load_extractor_module()

        records = module.extract_skills_graph_records(REPO_ROOT / "skills")
        bridge_skill_ids = {bridge["skill_id"] for bridge in records["bridges"]}

        self.assertEqual(
            bridge_skill_ids,
            {skill["id"] for skill in records["skills"]},
        )
        for bridge in records["bridges"]:
            for key in (
                "id",
                "skill_id",
                "name",
                "kind",
                "value",
                "source",
                "path",
                "source_path",
                "confidence",
            ):
                self.assertIn(key, bridge)
            self.assertNotIn(bridge["value"], {"skill-operation", "skill-use", "skill-governance"})
            self.assertGreaterEqual(bridge["confidence"], 0.0)
            self.assertLessEqual(bridge["confidence"], 1.0)

    def test_section_ids_include_order_to_avoid_duplicate_heading_collisions(self) -> None:
        module = load_extractor_module()
        with tempfile.TemporaryDirectory() as tmp:
            skill_path = Path(tmp) / "skills" / "agentic-patterns" / "duplicate-headings"
            skill_path.mkdir(parents=True)
            (skill_path / "SKILL.md").write_text(
                "\n".join(
                    (
                        "---",
                        "name: duplicate-headings",
                        "description: Use when testing duplicate headings in extraction.",
                        "---",
                        "# Duplicate Headings",
                        "## Notes",
                        "First note.",
                        "## Notes",
                        "Second note.",
                    )
                ),
                encoding="utf-8",
            )

            records = module.extract_skills_graph_records(Path(tmp) / "skills")

        section_ids = [section["id"] for section in records["sections"]]
        self.assertEqual(len(section_ids), len(set(section_ids)))
        self.assertIn("skill:duplicate-headings:section:0-notes", section_ids)
        self.assertIn("skill:duplicate-headings:section:1-notes", section_ids)

    def test_extractor_does_not_emit_universal_connectivity_bridges(self) -> None:
        module = load_extractor_module()

        records = module.extract_skills_graph_records(REPO_ROOT / "skills")

        for skill in records["skills"]:
            self.assertNotIn("skill-operation", skill["task_shapes"])
            self.assertNotIn("skill-use", skill["workflow_stages"])
            self.assertNotIn("skill-governance", skill["control_themes"])

        for field in ("task_shapes", "workflow_stages", "control_themes"):
            counts = Counter(value for skill in records["skills"] for value in skill[field])
            self.assertFalse(
                any(count == len(records["skills"]) for count in counts.values()),
                f"{field} contains a bridge shared by every skill",
            )

    def test_extracts_related_skill_relationships_with_source_evidence(self) -> None:
        module = load_extractor_module()

        records = module.extract_skills_graph_records(REPO_ROOT / "skills")
        relationships = {
            (relationship["source"], relationship["target"]): relationship
            for relationship in records["relationships"]
        }

        for target in (
            "skill:tool-use-function-calling",
            "skill:guardrails-safety-patterns",
            "skill:knowledge-retrieval-rag",
        ):
            relationship = relationships[("skill:mcp-server-design", target)]
            self.assertEqual(relationship["type"], "RELATED_TO")
            self.assertEqual(
                relationship["source_path"], "skills/agentic-patterns/mcp-server-design/SKILL.md"
            )
            self.assertTrue(relationship["source_section_id"].endswith("related-skills"))

    def test_extraction_is_repeatable_without_file_changes(self) -> None:
        module = load_extractor_module()

        first = module.extract_skills_graph_records(REPO_ROOT / "skills")
        second = module.extract_skills_graph_records(REPO_ROOT / "skills")

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
