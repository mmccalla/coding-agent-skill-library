"""Tests for the idempotent Neo4j skills KG loader."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "load_skills_neo4j.py"


def load_module() -> object:
    spec = importlib.util.spec_from_file_location("load_skills_neo4j", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def fixture_records() -> dict[str, object]:
    records: dict[str, object] = {
        "root_skill": "apply-laws-of-ai",
        "skill_pack": {
            "id": "coding-agent-skill-library",
            "name": "Coding Agent Skill Library",
            "version": "2026-06-29",
            "owner": "tests",
            "source_root": "skills",
            "contentHash": "pack-hash",
            "categories": ["agent-control-patterns", "engineering-practices"],
            "skillCount": 2,
        },
        "skills": [
            {
                "id": "skill:apply-laws-of-ai",
                "name": "apply-laws-of-ai",
                "title": "Apply Laws of AI",
                "description": "Baseline safety skill.",
                "category": "agent-control-patterns",
                "path": "skills/apply-laws-of-ai/SKILL.md",
                "task_shapes": ["safety"],
                "workflow_stages": ["startup"],
                "capabilities": ["governance"],
                "control_themes": ["safety"],
                "knowledge_domains": ["agent-control"],
                "related_skill_ids": ["skill:tdd-practice"],
                "skill_pack_id": "coding-agent-skill-library",
                "skill_pack_version": "2026-06-29",
                "contentHash": "abc",
                "wordCount": 10,
                "lineCount": 4,
                "isBaselineSkill": True,
                "promotion_status": "promoted",
            },
            {
                "id": "skill:tdd-practice",
                "name": "tdd-practice",
                "title": "TDD Practice",
                "description": "Test-driven development skill.",
                "category": "engineering-practices",
                "path": "skills/tdd-practice/SKILL.md",
                "task_shapes": ["testing"],
                "workflow_stages": ["validation"],
                "capabilities": ["test-design"],
                "control_themes": ["quality"],
                "knowledge_domains": ["engineering-practices"],
                "related_skill_ids": ["skill:apply-laws-of-ai"],
                "skill_pack_id": "coding-agent-skill-library",
                "skill_pack_version": "2026-06-29",
                "contentHash": "def",
                "wordCount": 12,
                "lineCount": 5,
                "isBaselineSkill": False,
                "promotion_status": "promoted",
            },
        ],
        "sections": [
            {
                "id": "skill:apply-laws-of-ai:section:0-objective",
                "skill_id": "skill:apply-laws-of-ai",
                "name": "Objective",
                "heading": "Objective",
                "level": 2,
                "order": 0,
                "contentHash": "section-hash",
                "text": "Keep humans safe.",
                "heading_path": "Objective",
                "line_start": 10,
                "line_end": 10,
                "char_start": 120,
                "char_end": 137,
            }
        ],
        "bridges": [],
        "relationships": [
            {
                "source": "skill:apply-laws-of-ai",
                "type": "COMPLEMENTS",
                "target": "skill:tdd-practice",
                "source_path": "skills/apply-laws-of-ai/SKILL.md",
                "mapping_rule_id": (
                    "skill:apply-laws-of-ai:mapping:dependency:complements:tdd-practice"
                ),
                "confidence": 0.7,
                "rationale": "Related skill referenced in Related skills section.",
                "source_scope": "section",
                "source_ref": "Related skills",
                "evidence_line_start": 10,
                "evidence_line_end": 10,
            }
        ],
        "references": [
            {
                "id": "skill:apply-laws-of-ai:reference:0",
                "skill_id": "skill:apply-laws-of-ai",
                "label": "Evidence",
                "target": "docs/evidence.md",
                "source_path": "skills/apply-laws-of-ai/SKILL.md",
            }
        ],
    }
    kind_by_field = {
        "task_shapes": "task_shape",
        "workflow_stages": "workflow_stage",
        "capabilities": "capability",
        "control_themes": "control_theme",
        "knowledge_domains": "knowledge_domain",
    }
    bridges = records["bridges"]
    assert isinstance(bridges, list)
    skills = records["skills"]
    assert isinstance(skills, list)
    for skill in skills:
        assert isinstance(skill, dict)
        skill_id = skill["id"]
        path = skill["path"]
        for field, kind in kind_by_field.items():
            values = skill[field]
            assert isinstance(values, list)
            for value in values:
                assert isinstance(value, str)
                bridge_value = value
                bridge_slug = bridge_value.replace("-", "-")
                bridges.append(
                    {
                        "id": f"{skill_id}:bridge:{kind}:{bridge_slug}",
                        "skill_id": skill_id,
                        "name": bridge_value,
                        "kind": kind,
                        "value": bridge_value,
                        "source": f"test-rule:{skill['name']}",
                        "rule_id": f"test-rule:{skill['name']}",
                        "path": path,
                        "source_path": path,
                        "source_scope": "fixture",
                        "source_ref": str(skill["name"]),
                        "rationale": "Fixture bridge assertion.",
                        "confidence": 1.0,
                    }
                )
    return records


class LoadSkillsNeo4jTests(unittest.TestCase):
    def test_load_plan_contains_skills_sections_retrieval_units_bridges_and_relationships(
        self,
    ) -> None:
        loader = load_module()

        plan = loader.build_load_plan(fixture_records())

        labels = {node.label for node in plan.nodes}
        relationship_types = {relationship.type for relationship in plan.relationships}
        self.assertIn("Skill", labels)
        self.assertIn("SkillSection", labels)
        self.assertIn("RetrievalUnit", labels)
        self.assertNotIn("SkillChunk", labels)
        self.assertIn("BridgeAssertion", labels)
        self.assertIn("SkillPack", labels)
        self.assertIn("SkillCategory", labels)
        self.assertIn("TaskShape", labels)
        self.assertIn("ReferenceDocument", labels)
        self.assertIn("HAS_SECTION", relationship_types)
        self.assertIn("HAS_RETRIEVAL_UNIT", relationship_types)
        self.assertNotIn("HAS_CHUNK", relationship_types)
        self.assertIn("ASSERTS_BRIDGE", relationship_types)
        self.assertIn("CONTAINS_SKILL", relationship_types)
        self.assertIn("COMPLEMENTS", relationship_types)
        retrieval_unit = next(node for node in plan.nodes if node.label == "RetrievalUnit")
        self.assertTrue(retrieval_unit.id.startswith("retrieval:skill:apply-laws-of-ai:section:0:"))
        for field in (
            "id",
            "skill_id",
            "unit_type",
            "retrieval_unit_type",
            "title",
            "text",
            "retrieval_text",
            "source_path",
            "heading_path",
            "line_start",
            "line_end",
            "char_start",
            "char_end",
            "section_heading",
            "ordinal",
            "content_hash",
            "section_id",
            "lexical_boost_terms",
            "semantic_aliases",
            "priority_weight",
            "embedding_model",
            "embedding_version",
            "vector_dimension",
            "retrieval_profile",
        ):
            self.assertIn(field, retrieval_unit.properties)
        self.assertEqual("skill-section", retrieval_unit.properties["retrieval_unit_type"])
        self.assertEqual("not-embedded", retrieval_unit.properties["embedding_model"])
        self.assertEqual("pending", retrieval_unit.properties["embedding_version"])
        self.assertEqual(0, retrieval_unit.properties["vector_dimension"])
        self.assertIsInstance(retrieval_unit.properties["lexical_boost_terms"], list)
        self.assertIsInstance(retrieval_unit.properties["semantic_aliases"], list)

    def test_fake_graph_load_is_idempotent(self) -> None:
        loader = load_module()
        graph = loader.InMemoryNeo4jGraph(loader.REQUIRED_SCHEMA_ITEMS)
        plan = loader.build_load_plan(fixture_records())

        first_report = loader.load_plan(graph, plan, batch_size=2)
        second_report = loader.load_plan(graph, plan, batch_size=2)

        self.assertEqual(first_report.logical_counts, second_report.logical_counts)
        self.assertEqual(first_report.batches, second_report.batches)

    def test_missing_schema_constraint_fails_before_writes(self) -> None:
        loader = load_module()
        missing_skill_name = {
            item for item in loader.REQUIRED_SCHEMA_ITEMS if item != "skill_name_unique"
        }
        graph = loader.InMemoryNeo4jGraph(missing_skill_name)
        plan = loader.build_load_plan(fixture_records())

        with self.assertRaisesRegex(loader.MissingSchemaItemError, "skill_name_unique"):
            loader.load_plan(graph, plan)

        self.assertEqual({}, graph.node_counts())
        self.assertEqual({}, graph.relationship_counts())

    def test_schema_application_allows_empty_graph_load(self) -> None:
        loader = load_module()
        graph = loader.InMemoryNeo4jGraph(set())
        plan = loader.build_load_plan(fixture_records())

        report = loader.load_plan(
            graph,
            plan,
            schema_statements=loader.read_schema_statements(),
        )

        self.assertEqual(2, report.logical_counts["node:Skill"])
        self.assertIn("skill_name_unique", graph.available_schema_items())

    def test_relationship_identity_ignores_metadata_changes(self) -> None:
        loader = load_module()
        graph = loader.InMemoryNeo4jGraph(loader.REQUIRED_SCHEMA_ITEMS)
        first_plan = loader.build_load_plan(fixture_records())
        changed_records = fixture_records()
        relationships = changed_records["relationships"]
        assert isinstance(relationships, list)
        relationship = relationships[0]
        assert isinstance(relationship, dict)
        relationship["source_path"] = "skills/changed/SKILL.md"
        second_plan = loader.build_load_plan(changed_records)

        loader.load_plan(graph, first_plan, batch_size=100)
        loader.load_plan(graph, second_plan, batch_size=100)

        self.assertEqual(1, graph.relationship_counts()["COMPLEMENTS"])

    def test_skill_node_properties_are_neo4j_primitive_safe(self) -> None:
        loader = load_module()
        extract = importlib.util.spec_from_file_location(
            "extract_skills_graph",
            REPO_ROOT / "scripts" / "extract_skills_graph.py",
        )
        assert extract is not None and extract.loader is not None
        extract_module = importlib.util.module_from_spec(extract)
        extract.loader.exec_module(extract_module)
        records = extract_module.extract_skills_graph_records(REPO_ROOT / "skills")
        plan = loader.build_load_plan(records)

        for node in plan.nodes:
            for key, value in node.properties.items():
                self.assertFalse(
                    isinstance(value, dict),
                    f"{node.label}:{node.id}.{key} must not be a nested map",
                )
                if isinstance(value, list):
                    for item in value:
                        self.assertFalse(
                            isinstance(item, dict),
                            f"{node.label}:{node.id}.{key} must not contain nested maps",
                        )

        skill = next(node for node in plan.nodes if node.id == "skill:human-in-the-loop")
        supported = skill.properties.get("supported_task_intents")
        self.assertIsInstance(supported, str)
        self.assertIn("security-hardening", supported)

    def test_dry_run_report_does_not_include_connection_details(self) -> None:
        loader = load_module()
        report = loader.dry_run_report(loader.build_load_plan(fixture_records()))

        self.assertIn("Skills KG dry-run load report", report)
        self.assertNotIn("bolt://", report)
        self.assertNotIn("password", report.lower())

    def test_neo4j_adapter_uses_configured_database_for_sessions(self) -> None:
        loader = load_module()
        driver = RecordingDriver()
        graph = loader.Neo4jMergeGraph(driver, database="skills")

        graph.available_schema_items()

        self.assertEqual(["skills"], driver.databases)

    def test_load_plan_from_neo4j_reads_nodes_and_relationships_from_database(self) -> None:
        loader = load_module()
        settings = type("Settings", (), {"database": "skills"})()
        driver = SnapshotDriver()

        plan = loader.load_plan_from_neo4j(driver, settings)

        self.assertEqual("Skill", plan.nodes[0].label)
        self.assertEqual("skill:example", plan.nodes[0].id)
        self.assertEqual("COMPLEMENTS", plan.relationships[0].type)
        self.assertEqual(["skills"], driver.databases)


class RecordingSession:
    def __enter__(self) -> RecordingSession:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def run(self, _query: str, **_parameters: object) -> list[dict[str, object]]:
        return [{"name": "skill_id_unique"}]


class RecordingDriver:
    def __init__(self) -> None:
        self.databases: list[str | None] = []

    def session(self, database: str | None = None) -> RecordingSession:
        self.databases.append(database)
        return RecordingSession()


class SnapshotSession:
    def __init__(self) -> None:
        self.calls = 0

    def __enter__(self) -> SnapshotSession:
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def run(self, _query: str, **_parameters: object) -> list[dict[str, object]]:
        self.calls += 1
        if self.calls == 1:
            return [
                {
                    "labels": ["Skill"],
                    "id": "skill:example",
                    "properties": {"id": "skill:example", "name": "example"},
                }
            ]
        return [
            {
                "type": "COMPLEMENTS",
                "source_labels": ["Skill"],
                "source_id": "skill:example",
                "target_labels": ["Skill"],
                "target_id": "skill:other",
                "properties": {"source": "test"},
            }
        ]


class SnapshotDriver:
    def __init__(self) -> None:
        self.databases: list[str | None] = []

    def session(self, database: str | None = None) -> SnapshotSession:
        self.databases.append(database)
        return SnapshotSession()


if __name__ == "__main__":
    unittest.main()
