"""Tests for promoted-only retrieval projection builders."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECTIONS_SCRIPT = REPO_ROOT / "scripts/graph/build/build_retrieval_projections.py"
LOADER_SCRIPT = REPO_ROOT / "scripts/graph/load/load_skills_neo4j.py"
RETRIEVAL_SCRIPT = REPO_ROOT / "scripts/lib/retrieval/retrieve_skills_hybrid.py"


def load_projections_module() -> object:
    spec = importlib.util.spec_from_file_location("build_retrieval_projections", PROJECTIONS_SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_loader_module() -> object:
    spec = importlib.util.spec_from_file_location("load_skills_neo4j", LOADER_SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_retrieval_module() -> object:
    spec = importlib.util.spec_from_file_location("retrieve_skills_hybrid", RETRIEVAL_SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def promotion_fixture_records() -> dict[str, object]:
    return {
        "skills": [
            {
                "id": "skill:promoted-skill",
                "name": "promoted-skill",
                "description": "Promoted retrieval candidate.",
                "category": "engineering-practices",
                "path": "skills/promoted-skill/SKILL.md",
                "task_shapes": ["testing"],
                "capabilities": ["test-design"],
                "aliases": ["promoted-alias"],
                "promotion_status": "promoted",
                "contentHash": "promoted-hash",
            },
            {
                "id": "skill:quarantined-skill",
                "name": "quarantined-skill",
                "description": "Quarantined skill without task intents.",
                "category": "engineering-practices",
                "path": "skills/quarantined-skill/SKILL.md",
                "task_shapes": [],
                "capabilities": [],
                "aliases": [],
                "promotion_status": "quarantined",
                "contentHash": "quarantined-hash",
            },
            {
                "id": "skill:rejected-skill",
                "name": "rejected-skill",
                "description": "Rejected skill blocked by trust gate.",
                "category": "engineering-practices",
                "path": "skills/rejected-skill/SKILL.md",
                "task_shapes": ["security"],
                "capabilities": ["validation"],
                "aliases": [],
                "promotion_status": "rejected",
                "contentHash": "rejected-hash",
            },
        ],
        "sections": [
            {
                "id": "skill:promoted-skill:section:0-objective",
                "skill_id": "skill:promoted-skill",
                "name": "Objective",
                "heading": "Objective",
                "level": 2,
                "order": 0,
                "contentHash": "promoted-section-hash",
                "text": "Use promoted skill for graph-grounded retrieval.",
                "heading_path": "Objective",
                "line_start": 10,
                "line_end": 10,
                "char_start": 120,
                "char_end": 170,
            },
            {
                "id": "skill:quarantined-skill:section:0-objective",
                "skill_id": "skill:quarantined-skill",
                "name": "Objective",
                "heading": "Objective",
                "level": 2,
                "order": 0,
                "contentHash": "quarantined-section-hash",
                "text": "Quarantined graph-grounded retrieval guidance.",
                "heading_path": "Objective",
                "line_start": 10,
                "line_end": 10,
                "char_start": 120,
                "char_end": 170,
            },
            {
                "id": "skill:rejected-skill:section:0-objective",
                "skill_id": "skill:rejected-skill",
                "name": "Objective",
                "heading": "Objective",
                "level": 2,
                "order": 0,
                "contentHash": "rejected-section-hash",
                "text": "Rejected graph-grounded retrieval guidance.",
                "heading_path": "Objective",
                "line_start": 10,
                "line_end": 10,
                "char_start": 120,
                "char_end": 170,
            },
        ],
        "bridges": [
            {
                "id": "skill:promoted-skill:bridge:task_shape:testing",
                "skill_id": "skill:promoted-skill",
                "kind": "task_shape",
                "value": "testing",
                "source_path": "skills/promoted-skill/SKILL.md",
                "confidence": 1.0,
            },
            {
                "id": "skill:quarantined-skill:bridge:task_shape:testing",
                "skill_id": "skill:quarantined-skill",
                "kind": "task_shape",
                "value": "testing",
                "source_path": "skills/quarantined-skill/SKILL.md",
                "confidence": 1.0,
            },
        ],
        "relationships": [
            {
                "source": "skill:promoted-skill",
                "type": "COMPLEMENTS",
                "target": "skill:quarantined-skill",
                "source_path": "skills/promoted-skill/SKILL.md",
            }
        ],
        "references": [
            {
                "id": "skill:promoted-skill:reference:0",
                "skill_id": "skill:promoted-skill",
                "label": "Evidence",
                "target": "docs/evidence.md",
                "source_path": "skills/promoted-skill/SKILL.md",
            },
            {
                "id": "skill:quarantined-skill:reference:0",
                "skill_id": "skill:quarantined-skill",
                "label": "Evidence",
                "target": "docs/quarantine.md",
                "source_path": "skills/quarantined-skill/SKILL.md",
            },
        ],
    }


class BuildRetrievalProjectionsTests(unittest.TestCase):
    def test_promoted_skill_gets_retrieval_units(self) -> None:
        projections = load_projections_module()
        records = promotion_fixture_records()

        filtered = projections.filter_promoted_records(records)
        units = projections.build_retrieval_projection_records(records)
        payload = projections.build_retrieval_projections(records)

        self.assertEqual(["skill:promoted-skill"], [skill["id"] for skill in filtered["skills"]])
        self.assertEqual(1, len(units))
        self.assertEqual("skill:promoted-skill", units[0]["skill_id"])
        self.assertEqual("skill-section", units[0]["retrieval_unit_type"])
        self.assertIn("graph-grounded retrieval", units[0]["text"])
        self.assertEqual(1, payload["promotion_summary"]["promoted"])
        self.assertEqual(1, len(payload["retrieval_units"]))

    def test_quarantined_and_rejected_skills_excluded_from_projections(self) -> None:
        projections = load_projections_module()
        records = promotion_fixture_records()

        filtered = projections.filter_promoted_records(records)
        units = projections.build_retrieval_projection_records(records)
        payload = projections.build_retrieval_projections(records)

        skill_ids = {unit["skill_id"] for unit in units}
        self.assertNotIn("skill:quarantined-skill", skill_ids)
        self.assertNotIn("skill:rejected-skill", skill_ids)
        self.assertEqual(1, payload["promotion_summary"]["quarantined"])
        self.assertEqual(1, payload["promotion_summary"]["rejected"])
        self.assertEqual(1, len(filtered["bridges"]))
        self.assertEqual("skill:promoted-skill", filtered["bridges"][0]["skill_id"])
        self.assertEqual([], filtered["relationships"])

    def test_load_plan_keeps_non_promoted_skills_but_skips_retrieval_units(self) -> None:
        loader = load_loader_module()
        from tests.test_load_skills_neo4j import fixture_records

        records = fixture_records()
        skills = records["skills"]
        assert isinstance(skills, list)
        skills.append(
            {
                "id": "skill:quarantined-skill",
                "name": "quarantined-skill",
                "title": "Quarantined Skill",
                "description": "Quarantined skill without retrieval projection.",
                "category": "engineering-practices",
                "path": "skills/quarantined-skill/SKILL.md",
                "task_shapes": ["review"],
                "workflow_stages": ["validation"],
                "capabilities": ["quality-review"],
                "control_themes": ["quality"],
                "knowledge_domains": ["engineering-practices"],
                "related_skill_ids": ["skill:apply-laws-of-ai"],
                "skill_pack_id": "coding-agent-skill-library",
                "skill_pack_version": "2026-06-29",
                "contentHash": "quarantined-hash",
                "wordCount": 8,
                "lineCount": 4,
                "isBaselineSkill": False,
                "promotion_status": "quarantined",
            }
        )
        sections = records["sections"]
        assert isinstance(sections, list)
        sections.append(
            {
                "id": "skill:quarantined-skill:section:0-objective",
                "skill_id": "skill:quarantined-skill",
                "name": "Objective",
                "heading": "Objective",
                "level": 2,
                "order": 0,
                "contentHash": "quarantined-section-hash",
                "text": "Quarantined graph-grounded retrieval guidance.",
                "heading_path": "Objective",
                "line_start": 10,
                "line_end": 10,
                "char_start": 120,
                "char_end": 170,
            }
        )
        relationships = records["relationships"]
        assert isinstance(relationships, list)
        relationships.append(
            {
                "source": "skill:apply-laws-of-ai",
                "type": "COMPLEMENTS",
                "target": "skill:quarantined-skill",
                "source_path": "skills/apply-laws-of-ai/SKILL.md",
                "mapping_rule_id": "skill:apply-laws-of-ai:mapping:dependency:complements:quarantined-skill",
                "confidence": 0.95,
                "rationale": "Fixture related skill edge.",
                "source_scope": "section",
                "source_ref": "Related skills",
                "evidence_line_start": 10,
                "evidence_line_end": 10,
            }
        )
        bridges = records["bridges"]
        assert isinstance(bridges, list)
        for kind, value in (
            ("task_shape", "review"),
            ("capability", "quality-review"),
            ("workflow_stage", "validation"),
            ("control_theme", "quality"),
            ("knowledge_domain", "engineering-practices"),
        ):
            bridges.append(
                {
                    "id": f"skill:quarantined-skill:bridge:{kind}:{value}",
                    "skill_id": "skill:quarantined-skill",
                    "name": value,
                    "kind": kind,
                    "value": value,
                    "source": "test-rule:quarantined-skill",
                    "rule_id": "test-rule:quarantined-skill",
                    "path": "skills/quarantined-skill/SKILL.md",
                    "source_path": "skills/quarantined-skill/SKILL.md",
                    "source_scope": "fixture",
                    "source_ref": "quarantined-skill",
                    "rationale": "Fixture bridge assertion.",
                    "confidence": 1.0,
                }
            )
        skills[1]["promotion_status"] = "promoted"

        plan = loader.build_load_plan(records)
        skill_ids = {node.id for node in plan.nodes if node.label == "Skill"}
        retrieval_skill_ids = {
            node.properties["skill_id"] for node in plan.nodes if node.label == "RetrievalUnit"
        }

        self.assertIn("skill:quarantined-skill", skill_ids)
        self.assertEqual({"skill:apply-laws-of-ai"}, retrieval_skill_ids)
        self.assertNotIn(
            "skill:tdd-practice",
            retrieval_skill_ids,
        )

    def test_quarantined_skill_not_retrieved(self) -> None:
        retrieval = load_retrieval_module()
        plan = retrieval.fixture_load_plan()
        quarantined_skill = retrieval.load_skills_neo4j.GraphNode(
            "Skill",
            "skill:quarantined-graph-rag",
            {
                "id": "skill:quarantined-graph-rag",
                "name": "quarantined-graph-rag",
                "promotion_status": "quarantined",
            },
        )
        quarantined_unit = retrieval.load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:quarantined-graph-rag:section:0:quarantined",
            {
                "id": "retrieval:skill:quarantined-graph-rag:section:0:quarantined",
                "skill_id": "skill:quarantined-graph-rag",
                "text": "Quarantined graph-grounded retrieval guidance.",
                "source_path": "skills/quarantined-graph-rag/SKILL.md",
                "heading_path": "Objective",
                "section_id": "skill:quarantined-graph-rag:section:0-objective",
                "line_start": 12,
                "line_end": 12,
            },
        )
        plan = retrieval.load_skills_neo4j.LoadPlan(
            nodes=(quarantined_skill, quarantined_unit, *plan.nodes),
            relationships=plan.relationships,
        )

        result = retrieval.retrieve_hybrid_skills(
            plan,
            query_text="graph rag ontology retrieval",
            vector_candidates=(),
            limit=3,
        )

        self.assertNotIn(
            "skill:quarantined-graph-rag",
            [recommendation.skill_id for recommendation in result.recommendations],
        )
        self.assertTrue(
            any(
                rejected["skill_id"] == "skill:quarantined-graph-rag"
                and "promotion_status" in rejected["reason"]
                for rejected in result.selection_trace["rejected"]
            )
        )


if __name__ == "__main__":
    unittest.main()
