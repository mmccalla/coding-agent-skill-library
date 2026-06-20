"""Tests for hybrid skill retrieval with graph evidence."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "retrieve_skills_hybrid.py"


def load_module() -> object:
    spec = importlib.util.spec_from_file_location("retrieve_skills_hybrid", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class HybridRetrievalTests(unittest.TestCase):
    def test_returns_ranked_skills_with_snippets_and_evidence_paths(self) -> None:
        retrieval = load_module()
        plan = retrieval.fixture_load_plan()

        result = retrieval.retrieve_hybrid_skills(
            plan,
            query_text="semantically similar request",
            vector_candidates=(
                retrieval.VectorCandidate(
                    chunk_id="chunk-kg",
                    score=0.72,
                    source_path="skills/data-architecture/kg-enabled-rag/SKILL.md",
                    section_id="skill:kg-enabled-rag:section:0-objective",
                    skill_id="skill:kg-enabled-rag",
                    text="Use KG-enabled RAG for graph-grounded retrieval.",
                    embedding_provider="deterministic-test-embedding",
                    embedding_dimensions=8,
                ),
            ),
            limit=3,
        )

        self.assertFalse(result.uncertain)
        self.assertEqual("skill:kg-enabled-rag", result.recommendations[0].skill_id)
        self.assertIn("graph-grounded retrieval", result.recommendations[0].evidence_snippets[0])
        self.assertIn("skills/data-architecture/kg-enabled-rag/SKILL.md", result.recommendations[0].source_paths)
        self.assertIn("skill:kg-enabled-rag:section:0-objective", result.recommendations[0].section_ids)
        self.assertTrue(result.recommendations[0].evidence_paths)

    def test_connected_skill_outranks_isolated_vector_match(self) -> None:
        retrieval = load_module()
        plan = retrieval.fixture_load_plan()

        result = retrieval.retrieve_hybrid_skills(
            plan,
            query_text="semantically similar request",
            vector_candidates=(
                retrieval.VectorCandidate(
                    chunk_id="chunk-generic",
                    score=0.95,
                    source_path="skills/reference/generic-documentation/SKILL.md",
                    section_id="skill:generic-documentation:section:0-objective",
                    skill_id="skill:generic-documentation",
                    text="General documentation guidance.",
                    embedding_provider="deterministic-test-embedding",
                    embedding_dimensions=8,
                ),
                retrieval.VectorCandidate(
                    chunk_id="chunk-kg",
                    score=0.72,
                    source_path="skills/data-architecture/kg-enabled-rag/SKILL.md",
                    section_id="skill:kg-enabled-rag:section:0-objective",
                    skill_id="skill:kg-enabled-rag",
                    text="KG-enabled RAG connects graph retrieval with ontology evidence.",
                    embedding_provider="deterministic-test-embedding",
                    embedding_dimensions=8,
                ),
            ),
            limit=2,
        )

        self.assertEqual("skill:kg-enabled-rag", result.recommendations[0].skill_id)
        self.assertGreater(
            result.recommendations[0].graph_score,
            result.recommendations[1].graph_score,
        )

    def test_low_confidence_query_returns_uncertainty(self) -> None:
        retrieval = load_module()
        plan = retrieval.fixture_load_plan()

        result = retrieval.retrieve_hybrid_skills(
            plan,
            query_text="zzzz qqqq nonsense",
            vector_candidates=(),
            limit=3,
        )

        self.assertTrue(result.uncertain)
        self.assertIn("narrower task description", result.message)
        self.assertEqual((), result.recommendations)

    def test_results_do_not_expose_raw_vectors_or_cypher(self) -> None:
        retrieval = load_module()
        plan = retrieval.fixture_load_plan()

        result = retrieval.retrieve_hybrid_skills(
            plan,
            query_text="graph rag ontology retrieval",
            vector_candidates=(),
            limit=3,
        )
        serialised = repr(result)

        self.assertNotIn("embedding=", serialised)
        self.assertNotIn("MATCH ", serialised)
        self.assertNotIn("CALL db.index", serialised)

    def test_depth_limit_bounds_graph_evidence_paths(self) -> None:
        retrieval = load_module()
        plan = retrieval.fixture_load_plan()

        without_graph = retrieval.retrieve_hybrid_skills(
            plan,
            query_text="graph rag ontology retrieval",
            vector_candidates=(),
            limit=1,
            max_depth=0,
        )
        with_graph = retrieval.retrieve_hybrid_skills(
            plan,
            query_text="graph rag ontology retrieval",
            vector_candidates=(),
            limit=1,
            max_depth=1,
        )

        self.assertEqual((), without_graph.recommendations[0].evidence_paths)
        self.assertTrue(with_graph.recommendations[0].evidence_paths)
        self.assertGreater(
            with_graph.recommendations[0].graph_score,
            without_graph.recommendations[0].graph_score,
        )

    def test_token_budget_is_shared_across_recommendations(self) -> None:
        retrieval = load_module()
        plan = retrieval.fixture_load_plan()

        result = retrieval.retrieve_hybrid_skills(
            plan,
            query_text="retrieval evidence graph",
            vector_candidates=(),
            limit=3,
            token_budget=8,
        )

        total_words = sum(
            len(snippet.split())
            for recommendation in result.recommendations
            for snippet in recommendation.evidence_snippets
        )
        self.assertLessEqual(total_words, 8)

    def test_query_supported_snippet_precedes_irrelevant_first_chunk(self) -> None:
        retrieval = load_module()
        plan = retrieval.fixture_load_plan()
        irrelevant = retrieval.load_skills_neo4j.GraphNode(
            "SkillChunk",
            "chunk-irrelevant-first",
            {
                "id": "chunk-irrelevant-first",
                "skill_id": "skill:kg-enabled-rag",
                "text": "Unrelated release notes.",
                "source_path": "skills/data-architecture/kg-enabled-rag/SKILL.md",
                "section_id": "skill:kg-enabled-rag:section:9-notes",
            },
        )
        plan = retrieval.load_skills_neo4j.LoadPlan(
            nodes=(irrelevant, *plan.nodes),
            relationships=plan.relationships,
        )

        result = retrieval.retrieve_hybrid_skills(
            plan,
            query_text="graph retrieval",
            vector_candidates=(),
            limit=1,
        )

        self.assertIn("graph-grounded retrieval", result.recommendations[0].evidence_snippets[0])


if __name__ == "__main__":
    unittest.main()
