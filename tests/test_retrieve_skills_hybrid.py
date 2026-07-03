"""Tests for hybrid skill retrieval with graph evidence."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

from scripts.skills_config import RetrievalSettings

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "retrieve_skills_hybrid.py"
# Ranking-focused tests use open abstention thresholds so production calibration
# does not mask hybrid scoring behaviour.
OPEN_ABSTENTION = RetrievalSettings(min_confident_score=0.01, min_top1_margin=0.0)


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
            retrieval_settings=OPEN_ABSTENTION,
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
        self.assertTrue(result.recommendations[0].evidence_anchors)
        self.assertEqual("Objective", result.recommendations[0].evidence_anchors[0]["heading_path"])
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
            retrieval_settings=OPEN_ABSTENTION,
        )

        self.assertEqual("skill:knowledge-graph-rag", result.recommendations[0].skill_id)
        self.assertGreater(
            result.recommendations[0].score,
            result.recommendations[1].score,
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

    def test_close_top_scores_abstain_when_margin_required(self) -> None:
        from scripts.skills_config import RetrievalSettings

        retrieval = load_module()
        plan = retrieval.fixture_load_plan()
        settings = RetrievalSettings(min_confident_score=0.01, min_top1_margin=0.5)

        result = retrieval.retrieve_hybrid_skills(
            plan,
            query_text="graph retrieval ontology provenance",
            vector_candidates=(
                retrieval.VectorCandidate(
                    retrieval_unit_id="retrieval:skill:knowledge-graph-rag:section:1:kg",
                    score=0.8,
                    source_path="skills/knowledge-graph-rag/SKILL.md",
                    section_id="skill:knowledge-graph-rag:section:0-objective",
                    skill_id="skill:knowledge-graph-rag",
                    text="Use KG-enabled RAG for graph-grounded retrieval.",
                    embedding_provider="deterministic-test-embedding",
                    embedding_dimensions=8,
                ),
                retrieval.VectorCandidate(
                    retrieval_unit_id="retrieval:skill:knowledge-retrieval-rag:section:0:retrieval",
                    score=0.79,
                    source_path="skills/knowledge-retrieval-rag/SKILL.md",
                    section_id="skill:knowledge-retrieval-rag:section:0-objective",
                    skill_id="skill:knowledge-retrieval-rag",
                    text="Use retrieval evidence and source-backed context.",
                    embedding_provider="deterministic-test-embedding",
                    embedding_dimensions=8,
                ),
            ),
            limit=3,
            retrieval_settings=settings,
        )

        self.assertTrue(result.uncertain)
        self.assertEqual((), result.recommendations)
        self.assertIn("Ambiguous skill match", result.message)

    def test_synthetic_nonce_probe_abstains_without_vector_signal(self) -> None:
        retrieval = load_module()
        plan = retrieval.fixture_load_plan()

        result = retrieval.retrieve_hybrid_skills(
            plan,
            query_text="zzqp qxjv kmtn irrelevant synthetic retrieval probe",
            vector_candidates=(),
            limit=3,
        )

        self.assertTrue(result.uncertain)
        self.assertEqual((), result.recommendations)
        rejected = result.selection_trace.get("rejected", ())
        self.assertTrue(
            any(
                item.get("reason") == "Query lacked task-specific token overlap with top evidence."
                for item in rejected
                if isinstance(item, dict)
            )
            or "narrower task description" in result.message
        )

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

    def test_user_facing_web_application_query_lifts_promoted_engineering_skills(self) -> None:
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

        top_skill_names = {recommendation.skill_name for recommendation in result.recommendations}
        relevant_skills = {
            "tdd-practice",
            "spec-driven-development",
            "planning-and-task-decomposition",
            "incremental-implementation",
            "solid-principles",
            "bdd-practice",
            "ux-design-principles",
            "ui-component-design",
            "design-system-practice",
            "event-streaming-platform-design",
            "stream-processing-patterns",
            "sre-practice",
        }

        self.assertFalse(result.uncertain)
        self.assertTrue(top_skill_names & relevant_skills)
        self.assertGreaterEqual(len(result.recommendations), 3)

    def test_deprecated_skill_is_filtered_from_automatic_selection(self) -> None:
        retrieval = load_module()
        plan = retrieval.fixture_load_plan()
        deprecated_skill = retrieval.load_skills_neo4j.GraphNode(
            "Skill",
            "skill:superseded-graph-rag",
            {
                "id": "skill:superseded-graph-rag",
                "name": "superseded-graph-rag",
                "deprecated": True,
                "promotion_status": "promoted",
            },
        )
        deprecated_unit = retrieval.load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:superseded-graph-rag:section:0:superseded",
            {
                "id": "retrieval:skill:superseded-graph-rag:section:0:superseded",
                "skill_id": "skill:superseded-graph-rag",
                "text": "Deprecated graph rag guidance for graph-grounded retrieval.",
                "source_path": "skills/superseded-graph-rag/SKILL.md",
                "heading_path": "Objective",
                "section_id": "skill:superseded-graph-rag:section:0-objective",
                "line_start": 12,
                "line_end": 12,
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
            "skill:superseded-graph-rag",
            [recommendation.skill_id for recommendation in result.recommendations],
        )
        self.assertTrue(
            any(
                rejected["skill_id"] == "skill:superseded-graph-rag"
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
                                "promotion_status": "promoted",
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
