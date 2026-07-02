"""Tests for deterministic skills graph extraction."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXTRACTOR = REPO_ROOT / "scripts" / "extract_skills_graph.py"
MAPPING_FIXTURES = REPO_ROOT / "tests" / "fixtures" / "skill_mapping"
MALICIOUS_FIXTURE = (
    REPO_ROOT / "tests" / "fixtures" / "skill_trust" / "malicious" / "instruction-override.md"
)
SECURITY_ALLOWLIST = REPO_ROOT / "tests" / "fixtures" / "skill_security_allowlist.json"
EXPECTED_SKILL_COUNT = len(tuple((REPO_ROOT / "skills").glob("*/SKILL.md")))


def write_minimal_pack_metadata(skills_root: Path, skill_names: tuple[str, ...]) -> None:
    categories = [
        {
            "id": "agentic-patterns",
            "title": "Agentic Patterns",
            "description": "Test category.",
            "skills": list(skill_names),
        }
    ]
    payload = {
        "schema_version": "skill-pack-metadata/v1",
        "skill_pack_id": "test-pack",
        "display_name": "Test Pack",
        "version": "1.0.0",
        "owner": "test",
        "source_root": "skills",
        "categories": categories,
    }
    (skills_root / "PACK_METADATA.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )


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

        self.assertEqual(len(records["skills"]), EXPECTED_SKILL_COUNT)
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
            "skill_pack_id",
            "skill_pack_version",
            "path",
            "contentHash",
            "wordCount",
            "lineCount",
            "isBaselineSkill",
        ):
            self.assertIn(key, skill)
        self.assertEqual(skill["path"], "skills/apply-laws-of-ai/SKILL.md")
        self.assertEqual(skill["skill_pack_id"], "coding-agent-skill-library")
        self.assertEqual(skill["skill_pack_version"], "2026-06-29")
        self.assertTrue(skill["isBaselineSkill"])
        self.assertGreater(skill["wordCount"], 0)
        self.assertGreater(skill["lineCount"], 0)
        self.assertNotIn("source_path", skill)
        self.assertNotIn("source_hash", skill)
        self.assertIn("aliases", skill)
        self.assertIsInstance(skill["aliases"], list)
        self.assertEqual(records["skill_pack"]["id"], "coding-agent-skill-library")

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
        self.assertTrue(all(section["heading_path"] for section in sections))
        self.assertTrue(all(section["line_start"] >= 1 for section in sections))
        self.assertTrue(all(section["line_end"] >= section["line_start"] for section in sections))
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
            skill_path = Path(tmp) / "skills" / "duplicate-headings"
            skill_path.mkdir(parents=True)
            (Path(tmp) / "skills" / "PACK_METADATA.json").write_text(
                "{\n"
                '  "schema_version": "skill-pack-metadata/v1",\n'
                '  "skill_pack_id": "test-pack",\n'
                '  "display_name": "Test Pack",\n'
                '  "version": "1.0.0",\n'
                '  "owner": "test",\n'
                '  "source_root": "skills",\n'
                '  "categories": [\n'
                "    {\n"
                '      "id": "agentic-patterns",\n'
                '      "title": "Agentic Patterns",\n'
                '      "description": "Test category.",\n'
                '      "skills": ["duplicate-headings"]\n'
                "    }\n"
                "  ]\n"
                "}\n",
                encoding="utf-8",
            )
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
            self.assertEqual(skill["control_themes"], skill["knowledge_domains"])
            self.assertTrue(skill["control_themes"])

        for field in ("task_shapes", "workflow_stages", "control_themes"):
            counts = Counter(value for skill in records["skills"] for value in skill[field])
            self.assertFalse(
                any(count == len(records["skills"]) for count in counts.values()),
                f"{field} contains a bridge shared by every skill",
            )

    def test_extracts_typed_related_skill_relationships_with_provenance(self) -> None:
        module = load_extractor_module()

        records = module.extract_skills_graph_records(REPO_ROOT / "skills")
        relationship_types = {relationship["type"] for relationship in records["relationships"]}

        self.assertNotIn("RELATED_TO", relationship_types)

        relationships = {
            (relationship["source"], relationship["target"]): relationship
            for relationship in records["relationships"]
        }

        for target in (
            "skill:tool-use-and-function-calling",
            "skill:guardrails-safety-patterns",
            "skill:knowledge-retrieval-rag",
        ):
            relationship = relationships[("skill:mcp-server-design", target)]
            self.assertIn(
                relationship["type"],
                {"PRECEDES", "VALIDATES", "COMPLEMENTS"},
            )
            self.assertEqual(
                relationship["source_path"], "skills/mcp-server-design/SKILL.md"
            )
            self.assertTrue(relationship["mapping_rule_id"])
            self.assertGreaterEqual(relationship["confidence"], 0.0)
            self.assertTrue(relationship["rationale"])
            self.assertEqual(relationship["source_scope"], "section")
            self.assertEqual(relationship["source_ref"], "Related skills")
            self.assertGreaterEqual(relationship["evidence_line_start"], 1)
            self.assertGreaterEqual(
                relationship["evidence_line_end"],
                relationship["evidence_line_start"],
            )

    def test_unmapped_related_skills_emit_complements_with_provenance(self) -> None:
        module = load_extractor_module()
        with tempfile.TemporaryDirectory() as tmp:
            skills_root = Path(tmp) / "skills"
            primary_dir = skills_root / "primary-skill"
            related_dir = skills_root / "related-skill"
            primary_dir.mkdir(parents=True)
            related_dir.mkdir(parents=True)
            write_minimal_pack_metadata(
                skills_root,
                ("primary-skill", "related-skill"),
            )
            (related_dir / "SKILL.md").write_text(
                "\n".join(
                    (
                        "---",
                        "name: related-skill",
                        "description: Related fixture skill.",
                        "---",
                        "# Related Skill",
                        "## Objective",
                        "Support typed dependency tests.",
                    )
                ),
                encoding="utf-8",
            )
            (primary_dir / "SKILL.md").write_text(
                "\n".join(
                    (
                        "---",
                        "name: primary-skill",
                        "description: Primary fixture skill.",
                        "---",
                        "# Primary Skill",
                        "## Related skills",
                        "",
                        "See also `related-skill` in this section.",
                        "",
                        "## Objective",
                        "Exercise fallback dependency mapping.",
                    )
                ),
                encoding="utf-8",
            )

            records = module.extract_skills_graph_records(
                skills_root,
                trust_gate=False,
            )

        relationship = next(
            relationship
            for relationship in records["relationships"]
            if relationship["source"] == "skill:primary-skill"
            and relationship["target"] == "skill:related-skill"
        )
        self.assertEqual(relationship["type"], "COMPLEMENTS")
        self.assertTrue(relationship["mapping_rule_id"].endswith(":related-skill"))
        self.assertGreaterEqual(relationship["confidence"], 0.0)
        self.assertTrue(relationship["rationale"])
        self.assertEqual(relationship["source_scope"], "section")
        self.assertEqual(relationship["source_ref"], "Related skills")
        self.assertEqual(relationship["evidence_line_start"], 8)

    def test_extraction_is_repeatable_without_file_changes(self) -> None:
        module = load_extractor_module()

        first = module.extract_skills_graph_records(REPO_ROOT / "skills")
        second = module.extract_skills_graph_records(REPO_ROOT / "skills")

        self.assertEqual(first, second)

    def test_extracts_aliases_from_frontmatter_lists(self) -> None:
        module = load_extractor_module()
        records = module.extract_skills_graph_records(REPO_ROOT / "skills")
        skill = next(
            skill for skill in records["skills"] if skill["id"] == "skill:knowledge-graph-rag"
        )

        self.assertIn("kg-enabled-rag", skill["aliases"])
        self.assertIn("graph-rag", skill["aliases"])

    def test_skill_record_includes_promotion_status(self) -> None:
        module = load_extractor_module()
        records = module.extract_skills_graph_records(REPO_ROOT / "skills")

        for skill in records["skills"]:
            self.assertIn(
                skill["promotion_status"],
                {"promoted", "quarantined", "rejected"},
            )

    def test_rejected_skills_when_trust_fails(self) -> None:
        module = load_extractor_module()
        malicious_text = MALICIOUS_FIXTURE.read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            skills_root = Path(tmp) / "skills"
            skill_dir = skills_root / "malicious-instruction-override"
            skill_dir.mkdir(parents=True)
            write_minimal_pack_metadata(skills_root, ("malicious-instruction-override",))
            (skill_dir / "SKILL.md").write_text(malicious_text, encoding="utf-8")

            records = module.extract_skills_graph_records(
                skills_root,
                trust_gate=True,
                grandfather_practice_waiver=False,
                allowlist_path=SECURITY_ALLOWLIST,
            )

        skill = records["skills"][0]
        self.assertEqual(skill["id"], "skill:malicious-instruction-override")
        self.assertEqual(skill["promotion_status"], "rejected")

    def test_mapping_derived_task_intents_attached_when_sections_present(self) -> None:
        module = load_extractor_module()
        excerpt = (MAPPING_FIXTURES / "tdd-practice-excerpt.md").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            skills_root = Path(tmp) / "skills"
            skill_dir = skills_root / "tdd-mapping-fixture"
            skill_dir.mkdir(parents=True)
            write_minimal_pack_metadata(skills_root, ("tdd-mapping-fixture",))
            (skill_dir / "SKILL.md").write_text(
                "\n".join(
                    (
                        "---",
                        "name: tdd-mapping-fixture",
                        "description: Use when adding behaviour, fixing a defect, or refactoring with tests.",
                        "---",
                        excerpt,
                        "",
                        "## Procedure",
                        "1. Write a failing test.",
                        "",
                        "## Verification",
                        "- [ ] Targeted tests pass.",
                    )
                ),
                encoding="utf-8",
            )

            records = module.extract_skills_graph_records(
                skills_root,
                trust_gate=True,
                grandfather_practice_waiver=False,
                allowlist_path=SECURITY_ALLOWLIST,
            )

        skill = records["skills"][0]
        self.assertEqual(skill["promotion_status"], "promoted")
        supported = {item["task_intent_id"] for item in skill["supported_task_intents"]}
        self.assertIn("defect-fix-with-tests", supported)
        self.assertIn("refactor-with-tests", supported)
        self.assertIn("feature-implementation", supported)

        mapping_bridges = [
            bridge
            for bridge in records["bridges"]
            if bridge["skill_id"] == skill["id"] and bridge.get("mapping_source") == "when_to_use"
        ]
        bridge_values = {bridge["value"] for bridge in mapping_bridges}
        self.assertIn("defect-fix-with-tests", bridge_values)
        self.assertTrue(all(bridge["kind"] == "task_shape" for bridge in mapping_bridges))


if __name__ == "__main__":
    unittest.main()
