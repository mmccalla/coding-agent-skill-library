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
                    retrieval_unit_id="retrieval:skill:knowledge-graph-rag:section:1:kg",
                    score=0.72,
                    source_path="skills/knowledge-graph-rag/SKILL.md",
                    section_id="skill:knowledge-graph-rag:section:0-objective",
                    skill_id="skill:knowledge-graph-rag",
                    text="Use KG-enabled RAG for graph-grounded retrieval.",
                    embedding_provider="deterministic-test-embedding",
                    embedding_dimensions=8,
                ),
            ),
            limit=3,
        )

        self.assertFalse(result.uncertain)
        self.assertEqual("skill:knowledge-graph-rag", result.recommendations[0].skill_id)
        self.assertIn("graph-grounded retrieval", result.recommendations[0].evidence_snippets[0])
        self.assertEqual(
            "skill:knowledge-graph-rag", result.selection_trace["selected"]["skill_id"]
        )
        self.assertIn(
            "skills/knowledge-graph-rag/SKILL.md",
            result.recommendations[0].source_paths,
        )
        self.assertIn(
            "skill:knowledge-graph-rag:section:0-objective", result.recommendations[0].section_ids
        )
        self.assertTrue(result.recommendations[0].evidence_paths)

    def test_connected_skill_outranks_isolated_vector_match(self) -> None:
        retrieval = load_module()
        plan = retrieval.fixture_load_plan()

        result = retrieval.retrieve_hybrid_skills(
            plan,
            query_text="semantically similar request",
            vector_candidates=(
                retrieval.VectorCandidate(
                    retrieval_unit_id="retrieval:skill:generic-documentation:section:0:generic",
                    score=0.95,
                    source_path="skills/generic-documentation/SKILL.md",
                    section_id="skill:generic-documentation:section:0-objective",
                    skill_id="skill:generic-documentation",
                    text="General documentation guidance.",
                    embedding_provider="deterministic-test-embedding",
                    embedding_dimensions=8,
                ),
                retrieval.VectorCandidate(
                    retrieval_unit_id="retrieval:skill:knowledge-graph-rag:section:1:kg",
                    score=0.72,
                    source_path="skills/knowledge-graph-rag/SKILL.md",
                    section_id="skill:knowledge-graph-rag:section:0-objective",
                    skill_id="skill:knowledge-graph-rag",
                    text="KG-enabled RAG connects graph retrieval with ontology evidence.",
                    embedding_provider="deterministic-test-embedding",
                    embedding_dimensions=8,
                ),
            ),
            limit=2,
        )

        self.assertEqual("skill:knowledge-graph-rag", result.recommendations[0].skill_id)
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
        self.assertEqual({}, result.selection_trace["selected"])

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
            "RetrievalUnit",
            "retrieval:skill:knowledge-graph-rag:section:9:irrelevant",
            {
                "id": "retrieval:skill:knowledge-graph-rag:section:9:irrelevant",
                "skill_id": "skill:knowledge-graph-rag",
                "text": "Unrelated release notes.",
                "source_path": "skills/knowledge-graph-rag/SKILL.md",
                "section_id": "skill:knowledge-graph-rag:section:9-notes",
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

    def test_user_facing_web_application_query_lifts_ux_and_accessibility_skills(self) -> None:
        retrieval = load_module()
        plan = retrieval.embed_skill_chunks.build_embedded_repository_load_plan(
            REPO_ROOT / "skills"
        )

        result = retrieval.retrieve_hybrid_skills(
            plan,
            query_text=(
                "Tell me about designing and building a user facing web application, "
                "using best practice software engineering principles, with separate front "
                "and back ends that leverage real time streaming for communication between "
                "components. How should I best architect the solution?"
            ),
            vector_candidates=(),
            limit=10,
            max_depth=2,
            token_budget=1200,
        )

        top_skill_names = [recommendation.skill_name for recommendation in result.recommendations]

        self.assertIn("accessibility-wcag", top_skill_names)
        self.assertIn("ux-design-principles", top_skill_names)

    def test_deprecated_skill_is_filtered_from_automatic_selection(self) -> None:
        retrieval = load_module()
        plan = retrieval.fixture_load_plan()
        deprecated_skill = retrieval.load_skills_neo4j.GraphNode(
            "Skill",
            "skill:legacy-graph-rag",
            {
                "id": "skill:legacy-graph-rag",
                "name": "legacy-graph-rag",
                "deprecated": True,
            },
        )
        deprecated_unit = retrieval.load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:legacy-graph-rag:section:0:legacy",
            {
                "id": "retrieval:skill:legacy-graph-rag:section:0:legacy",
                "skill_id": "skill:legacy-graph-rag",
                "text": "Graph rag legacy guidance for graph-grounded retrieval.",
                "source_path": "skills/legacy-graph-rag/SKILL.md",
                "section_id": "skill:legacy-graph-rag:section:0-objective",
            },
        )
        plan = retrieval.load_skills_neo4j.LoadPlan(
            nodes=(deprecated_skill, deprecated_unit, *plan.nodes),
            relationships=plan.relationships,
        )

        result = retrieval.retrieve_hybrid_skills(
            plan,
            query_text="graph rag ontology retrieval",
            vector_candidates=(),
            limit=3,
        )

        self.assertNotIn(
            "skill:legacy-graph-rag",
            [recommendation.skill_id for recommendation in result.recommendations],
        )
        self.assertTrue(
            any(
                rejected["skill_id"] == "skill:legacy-graph-rag"
                and "Deprecated skill filtered" in rejected["reason"]
                for rejected in result.selection_trace["rejected"]
            )
        )

    def test_neo4j_hybrid_adapter_uses_fulltext_vector_and_fetches_plan(self) -> None:
        retrieval = load_module()

        class FakeSession:
            def __init__(self) -> None:
                self.queries: list[tuple[str, dict[str, object]]] = []

            def __enter__(self) -> FakeSession:
                return self

            def __exit__(self, *_args: object) -> None:
                return None

            def run(self, query: str, **parameters: object) -> tuple[dict[str, object], ...]:
                self.queries.append((query, parameters))
                if "db.index.fulltext.queryNodes" in query:
                    return ({"skill_id": "skill:knowledge-graph-rag"},)
                if "db.index.vector.queryNodes" in query:
                    return (
                        {
                            "retrieval_unit_id": "retrieval:skill:knowledge-graph-rag:section:1:kg",
                            "score": 0.91,
                            "source_path": "skills/knowledge-graph-rag/SKILL.md",
                            "section_id": "skill:knowledge-graph-rag:section:0-objective",
                            "skill_id": "skill:knowledge-graph-rag",
                            "text": "Use KG-enabled RAG for graph-grounded retrieval.",
                            "embedding_provider": "deterministic-test-embedding",
                            "embedding_dimensions": 8,
                        },
                    )
                if "RETURN s.id AS id" in query:
                    return (
                        {
                            "id": "skill:knowledge-graph-rag",
                            "properties": {
                                "id": "skill:knowledge-graph-rag",
                                "name": "knowledge-graph-rag",
                            },
                        },
                    )
                if "RETURN unit.id AS id" in query:
                    return (
                        {
                            "id": "retrieval:skill:knowledge-graph-rag:section:1:kg",
                            "properties": {
                                "id": "retrieval:skill:knowledge-graph-rag:section:1:kg",
                                "skill_id": "skill:knowledge-graph-rag",
                                "text": "Use KG-enabled RAG for graph-grounded retrieval.",
                                "source_path": "skills/knowledge-graph-rag/SKILL.md",
                                "section_id": "skill:knowledge-graph-rag:section:0-objective",
                            },
                        },
                    )
                if "RETURN type(r) AS type" in query:
                    return (
                        {
                            "type": "HAS_CAPABILITY",
                            "source_label": "Skill",
                            "source_id": "skill:knowledge-graph-rag",
                            "target_label": "Capability",
                            "target_id": "graph-rag",
                            "properties": {},
                        },
                    )
                raise AssertionError(f"Unexpected query: {query}")

        class FakeDriver:
            def __init__(self) -> None:
                self.session_instance = FakeSession()
                self.database = ""

            def session(self, *, database: str) -> FakeSession:
                self.database = database
                return self.session_instance

        settings = retrieval.skills_config.load_settings(environ={})
        driver = FakeDriver()
        result = retrieval.retrieve_hybrid_skills_from_neo4j(
            driver,
            settings,
            "graph rag retrieval",
            embedder=retrieval.embed_skill_chunks.DeterministicEmbeddingProvider(dimension=8),
            limit=1,
        )

        self.assertFalse(result.uncertain)
        self.assertEqual("skill:knowledge-graph-rag", result.recommendations[0].skill_id)
        queries = "\n".join(query for query, _parameters in driver.session_instance.queries)
        self.assertIn("db.index.fulltext.queryNodes", queries)
        self.assertIn("db.index.vector.queryNodes", queries)
        self.assertEqual("neo4j", driver.database)


if __name__ == "__main__":
    unittest.main()
