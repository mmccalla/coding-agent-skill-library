"""Tests for deterministic skill chunk embeddings and vector candidates."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "embed_skill_chunks.py"


def load_module() -> object:
    spec = importlib.util.spec_from_file_location("embed_skill_chunks", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class EmbedSkillChunksTests(unittest.TestCase):
    def test_deterministic_embedder_returns_configured_dimension(self) -> None:
        embeddings = load_module()
        embedder = embeddings.DeterministicEmbeddingProvider(dimension=8)

        first = embedder.embed("approval before destructive command")
        second = embedder.embed("approval before destructive command")

        self.assertEqual(8, len(first))
        self.assertEqual(first, second)
        self.assertEqual("deterministic-test-embedding", embedder.provider_name)

    def test_enriched_chunk_nodes_include_embeddings_and_provider_metadata(self) -> None:
        embeddings = load_module()
        plan = embeddings.load_skills_neo4j.LoadPlan(
            nodes=(
                embeddings.load_skills_neo4j.GraphNode(
                    label="SkillChunk",
                    id="chunk-1",
                    properties={
                        "id": "chunk-1",
                        "text": "approval before destructive command",
                        "source_path": "skills/example/SKILL.md",
                        "section_id": "skill:example:section:0-objective",
                        "skill_id": "skill:example",
                    },
                ),
            ),
            relationships=(),
        )
        embedder = embeddings.DeterministicEmbeddingProvider(dimension=8)

        enriched = embeddings.embed_skill_chunks(plan, embedder)

        chunk = enriched.nodes[0]
        self.assertEqual(8, len(chunk.properties["embedding"]))
        self.assertEqual("deterministic-test-embedding", chunk.properties["embeddingProvider"])
        self.assertEqual(8, chunk.properties["embeddingDimensions"])

    def test_vector_candidates_include_provenance_without_raw_vectors(self) -> None:
        embeddings = load_module()
        plan = embeddings.load_skills_neo4j.LoadPlan(
            nodes=(
                embeddings.load_skills_neo4j.GraphNode(
                    label="SkillChunk",
                    id="chunk-approval",
                    properties={
                        "id": "chunk-approval",
                        "text": "approval before destructive command",
                        "source_path": "skills/agent-control-patterns/human-in-the-loop/SKILL.md",
                        "section_id": "skill:human-in-the-loop:section:0-objective",
                        "skill_id": "skill:human-in-the-loop",
                    },
                ),
                embeddings.load_skills_neo4j.GraphNode(
                    label="SkillChunk",
                    id="chunk-dashboard",
                    properties={
                        "id": "chunk-dashboard",
                        "text": "dashboard typography and layout",
                        "source_path": "skills/user-experience/design-system-practice/SKILL.md",
                        "section_id": "skill:design-system-practice:section:0-objective",
                        "skill_id": "skill:design-system-practice",
                    },
                ),
            ),
            relationships=(),
        )
        embedder = embeddings.DeterministicEmbeddingProvider(dimension=8)
        enriched = embeddings.embed_skill_chunks(plan, embedder)

        candidates = embeddings.query_vector_candidates(
            enriched,
            query_text="approval before destructive command",
            embedder=embedder,
            limit=1,
        )

        self.assertEqual("chunk-approval", candidates[0].chunk_id)
        self.assertGreaterEqual(candidates[0].score, 0.0)
        self.assertEqual(
            "skills/agent-control-patterns/human-in-the-loop/SKILL.md",
            candidates[0].source_path,
        )
        self.assertEqual(
            "skill:human-in-the-loop:section:0-objective",
            candidates[0].section_id,
        )
        self.assertEqual("deterministic-test-embedding", candidates[0].embedding_provider)
        self.assertEqual(8, candidates[0].embedding_dimensions)
        self.assertFalse(hasattr(candidates[0], "embedding"))

    def test_neo4j_vector_query_uses_named_index_and_preserves_provenance(self) -> None:
        embeddings = load_module()
        embedder = embeddings.DeterministicEmbeddingProvider(dimension=8)

        class FakeVectorGraph:
            def __init__(self) -> None:
                self.calls: list[dict[str, object]] = []

            def query_vector_index(
                self,
                index_name: str,
                embedding: tuple[float, ...],
                limit: int,
            ) -> tuple[dict[str, object], ...]:
                self.calls.append(
                    {
                        "index_name": index_name,
                        "embedding": embedding,
                        "limit": limit,
                    }
                )
                return (
                    {
                        "chunk_id": "chunk-approval",
                        "score": 0.91,
                        "source_path": "skills/agent-control-patterns/human-in-the-loop/SKILL.md",
                        "section_id": "skill:human-in-the-loop:section:0-objective",
                        "skill_id": "skill:human-in-the-loop",
                        "text": "approval before destructive command",
                        "embedding_provider": "deterministic-test-embedding",
                        "embedding_dimensions": 8,
                    },
                )

        graph = FakeVectorGraph()

        candidates = embeddings.query_neo4j_vector_candidates(
            graph,
            query_text="approval before destructive command",
            embedder=embedder,
            limit=1,
        )

        self.assertEqual("skill_chunk_embedding_vector", graph.calls[0]["index_name"])
        self.assertEqual(8, len(graph.calls[0]["embedding"]))
        self.assertEqual(1, graph.calls[0]["limit"])
        self.assertEqual("chunk-approval", candidates[0].chunk_id)
        self.assertEqual("deterministic-test-embedding", candidates[0].embedding_provider)
        self.assertEqual(8, candidates[0].embedding_dimensions)
        self.assertFalse(hasattr(candidates[0], "embedding"))

    def test_driver_backed_vector_adapter_calls_neo4j_vector_index(self) -> None:
        embeddings = load_module()

        class FakeSession:
            def __init__(self) -> None:
                self.query = ""
                self.parameters: dict[str, object] = {}

            def __enter__(self) -> FakeSession:
                return self

            def __exit__(self, *_args: object) -> None:
                return None

            def run(self, query: str, **parameters: object) -> tuple[dict[str, object], ...]:
                self.query = query
                self.parameters = parameters
                return (
                    {
                        "chunk_id": "chunk-approval",
                        "score": 0.91,
                        "source_path": "skills/agent-control-patterns/human-in-the-loop/SKILL.md",
                        "section_id": "skill:human-in-the-loop:section:0-objective",
                        "skill_id": "skill:human-in-the-loop",
                        "text": "approval before destructive command",
                        "embedding_provider": "deterministic-test-embedding",
                        "embedding_dimensions": 8,
                    },
                )

        class FakeDriver:
            def __init__(self) -> None:
                self.session_instance = FakeSession()

            def session(self) -> FakeSession:
                return self.session_instance

        driver = FakeDriver()
        graph = embeddings.Neo4jVectorQueryGraph(driver)

        records = graph.query_vector_index(
            "skill_chunk_embedding_vector",
            embedding=(0.1, 0.2),
            limit=1,
        )

        self.assertIn("CALL db.index.vector.queryNodes", driver.session_instance.query)
        self.assertEqual(
            "skill_chunk_embedding_vector", driver.session_instance.parameters["index_name"]
        )
        self.assertEqual([0.1, 0.2], driver.session_instance.parameters["embedding"])
        self.assertEqual(1, driver.session_instance.parameters["limit"])
        self.assertEqual("chunk-approval", records[0]["chunk_id"])
        self.assertEqual("deterministic-test-embedding", records[0]["embedding_provider"])


if __name__ == "__main__":
    unittest.main()
