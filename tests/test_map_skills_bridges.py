"""Tests for curated semantic bridge mapping."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXTRACTOR = REPO_ROOT / "scripts" / "extract_skills_graph.py"
MAPPER = REPO_ROOT / "scripts" / "map_skills_bridges.py"
MAPPING_RULES = REPO_ROOT / "skills_docs" / "ontology" / "bridge_mapping_rules.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SkillsBridgeMapperTests(unittest.TestCase):
    def test_mapping_rules_are_documented_not_hidden_in_code(self) -> None:
        rules = json.loads(MAPPING_RULES.read_text(encoding="utf-8"))

        self.assertIn("category_rules", rules)
        self.assertIn("skill_rules", rules)
        self.assertIn("engineering-practices", rules["category_rules"])
        self.assertIn("bdd-practice", rules["skill_rules"])

    def test_mapper_adds_traceable_bdd_semantic_bridges(self) -> None:
        extractor = load_module(EXTRACTOR, "extract_skills_graph")
        mapper = load_module(MAPPER, "map_skills_bridges")
        records = extractor.extract_skills_graph_records(REPO_ROOT / "skills")

        mapped = mapper.apply_semantic_bridge_mappings(records, MAPPING_RULES)
        bdd = next(skill for skill in mapped["skills"] if skill["name"] == "bdd-practice")
        bdd_bridges = {
            (bridge["kind"], bridge["value"]): bridge
            for bridge in mapped["bridges"]
            if bridge["skill_id"] == "skill:bdd-practice"
        }

        self.assertIn("acceptance-criteria", bdd["task_shapes"])
        self.assertIn("validation", bdd["workflow_stages"])
        self.assertIn("behaviour-specification", bdd["capabilities"])
        self.assertEqual(
            bdd_bridges[("task_shape", "acceptance-criteria")]["source"],
            "skill-rule:bdd-practice",
        )

    def test_mapper_adds_traceable_skill_relationships(self) -> None:
        extractor = load_module(EXTRACTOR, "extract_skills_graph")
        mapper = load_module(MAPPER, "map_skills_bridges")
        records = extractor.extract_skills_graph_records(REPO_ROOT / "skills")

        mapped = mapper.apply_semantic_bridge_mappings(records, MAPPING_RULES)
        relationships = {
            (relationship["source"], relationship["type"], relationship["target"]): relationship
            for relationship in mapped["relationships"]
        }

        relationship = relationships[
            ("skill:guardrails-safety-patterns", "GOVERNS", "skill:human-in-the-loop")
        ]
        self.assertEqual(relationship["mapping_rule_id"], "skill-rule:guardrails-safety-patterns")
        self.assertEqual(relationship["source_path"], "skills/agent-control-patterns/guardrails-safety-patterns/SKILL.md")

    def test_mapper_is_stable_and_preserves_connectivity_validation(self) -> None:
        extractor = load_module(EXTRACTOR, "extract_skills_graph")
        mapper = load_module(MAPPER, "map_skills_bridges")
        validator = load_module(REPO_ROOT / "scripts" / "validate_skills_graph.py", "validate_skills_graph")
        records = extractor.extract_skills_graph_records(REPO_ROOT / "skills")

        first = mapper.apply_semantic_bridge_mappings(records, MAPPING_RULES)
        second = mapper.apply_semantic_bridge_mappings(records, MAPPING_RULES)
        result = validator.validate_graph_records(first)

        self.assertEqual(first, second)
        self.assertTrue(result.valid, "\n".join(result.errors))


if __name__ == "__main__":
    unittest.main()
