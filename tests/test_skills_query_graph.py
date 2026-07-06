"""Tests for bounded graph query-family planning and execution."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts/lib/routing/skills_query_graph.py"


def load_module():
    spec = importlib.util.spec_from_file_location("skills_query_graph", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SkillsQueryGraphTests(unittest.TestCase):
    def test_exact_skill_lookup_plan_is_bounded_and_read_only(self) -> None:
        module = load_module()
        plan = module.load_skills_neo4j.build_repository_load_plan(REPO_ROOT / "skills")

        result = module.plan_graph_query(
            plan,
            "tell me about knowledge-graph-rag",
            route="direct_lookup",
            resolved_skill_id="skill:knowledge-graph-rag",
            limit=7,
        )

        self.assertEqual("ok", result["status"])
        self.assertEqual("skill_lookup", result["intent"])
        self.assertEqual("exact_skill_lookup", result["query_family"])
        self.assertTrue(result["read_only"])
        self.assertEqual("skill_lookup_v1", result["cypher_template_id"])
        self.assertIn("MATCH (s:Skill {id: $skill_id})", result["generated_cypher"])
        self.assertIn("LIMIT $limit", result["generated_cypher"])
        self.assertEqual(7, result["result_bounds"]["limit"])

    def test_related_skill_traversal_execution_returns_paths(self) -> None:
        module = load_module()
        retrieval = __import__(
            "scripts.lib.retrieval.retrieve_skills_hybrid", fromlist=["fixture_load_plan"]
        )
        plan = retrieval.fixture_load_plan()
        query_plan = module.plan_graph_query(
            plan,
            "What skills are related to knowledge-graph-rag?",
            route="context",
            resolved_skill_id="skill:knowledge-graph-rag",
            limit=5,
        )

        result = module.execute_planned_query(plan, query_plan)

        self.assertEqual("ok", result["status"])
        self.assertTrue(result["records"])
        self.assertTrue(result["path_summaries"])

    def test_constraint_verification_query_returns_citations(self) -> None:
        module = load_module()
        retrieval = __import__(
            "scripts.lib.retrieval.retrieve_skills_hybrid", fromlist=["fixture_load_plan"]
        )
        plan = retrieval.fixture_load_plan()
        query_plan = module.plan_graph_query(
            plan,
            "Show me the verification checklist for knowledge-graph-rag",
            route="execution_plan",
            resolved_skill_id="skill:knowledge-graph-rag",
            limit=3,
        )

        result = module.execute_planned_query(plan, query_plan)

        self.assertEqual("constraint_verification_retrieval", query_plan["query_family"])
        self.assertEqual("ok", result["status"])
        self.assertTrue(result["citations"])

    def test_pack_membership_lookup_uses_skill_pack_properties(self) -> None:
        module = load_module()
        loader = __import__(
            "scripts.graph.load.load_skills_neo4j", fromlist=["GraphNode", "LoadPlan"]
        )
        plan = loader.LoadPlan(
            nodes=(
                loader.GraphNode(
                    "Skill",
                    "skill:alpha",
                    {
                        "id": "skill:alpha",
                        "name": "alpha",
                        "skill_pack_id": "coding-agent-skill-library",
                        "skill_pack_version": "2026-06-29",
                    },
                ),
            ),
            relationships=(),
        )

        query_plan = module.plan_graph_query(
            plan, "show skills in the coding-agent-skill-library pack"
        )
        result = module.execute_planned_query(plan, query_plan)

        self.assertEqual("pack_skill_membership_lookup", query_plan["query_family"])
        self.assertEqual("ok", result["status"])
        self.assertEqual("coding-agent-skill-library", result["records"][0]["skill_pack_id"])

    def test_unknown_query_family_abstains(self) -> None:
        module = load_module()
        retrieval = __import__(
            "scripts.lib.retrieval.retrieve_skills_hybrid", fromlist=["fixture_load_plan"]
        )
        plan = retrieval.fixture_load_plan()

        result = module.execute_planned_query(
            plan,
            {
                "status": "ok",
                "query_family": "unsafe_family",
                "parameters": {},
                "result_bounds": {},
            },
        )

        self.assertEqual("abstain", result["status"])


if __name__ == "__main__":
    unittest.main()
