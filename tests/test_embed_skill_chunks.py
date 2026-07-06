"""Tests for deterministic retrieval unit embeddings and vector candidates."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts/graph/build/embed_skill_chunks.py"


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

    def test_resolve_embedding_provider_defaults_to_production_bge(self) -> None:
        from scripts.lib.config.skills_config import SkillsKgSettings

        embeddings = load_module()
        settings = SkillsKgSettings()

        provider = embeddings.resolve_embedding_provider(settings, environ={})

        self.assertEqual("ollama:bge-m3:567m", provider.provider_name)
        self.assertEqual(1024, provider.dimension)

    def test_resolve_embedding_provider_forces_deterministic_for_ci(self) -> None:
        from scripts.lib.config.skills_config import SkillsKgSettings

        embeddings = load_module()
        settings = SkillsKgSettings()

        provider = embeddings.resolve_embedding_provider(
            settings,
            environ={"SKILLS_EMBEDDING_PROVIDER": "deterministic"},
        )
        forced = embeddings.resolve_embedding_provider(settings, force_deterministic=True)

        self.assertEqual("deterministic-test-embedding", provider.provider_name)
        self.assertEqual("deterministic-test-embedding", forced.provider_name)

    def test_bge_m3_ollama_provider_posts_to_local_embedding_endpoint(self) -> None:
        embeddings = load_module()

        class FakeResponse:
            def raise_for_status(self) -> None:
                return None

            def json(self) -> dict[str, list[float]]:
                return {"embedding": [3.0, 4.0]}

        class FakeClient:
            def __init__(self) -> None:
                self.url = ""
                self.payload: dict[str, object] = {}
                self.timeout = 0.0

            def post(
                self,
                url: str,
                *,
                json: dict[str, object],
                timeout: float,
            ) -> FakeResponse:
                self.url = url
                self.payload = json
                self.timeout = timeout
                return FakeResponse()

        client = FakeClient()
        provider = embeddings.BgeM3OllamaEmbeddingProvider(
            model="bge-m3:567m",
            base_url="http://ollama.local/",
            dimension=2,
            timeout_seconds=12.5,
            http_client=client,
        )

        vector = provider.embed("semantic retrieval query")

        self.assertEqual("http://ollama.local/api/embeddings", client.url)
        self.assertEqual(
            {"model": "bge-m3:567m", "prompt": "semantic retrieval query"}, client.payload
        )
        self.assertEqual(12.5, client.timeout)
        self.assertEqual("ollama:bge-m3:567m", provider.provider_name)
        self.assertAlmostEqual(0.6, vector[0])
        self.assertAlmostEqual(0.8, vector[1])

    def test_bge_m3_ollama_provider_returns_zero_vector_for_blank_text(self) -> None:
        embeddings = load_module()

        class FakeClient:
            def post(
                self,
                _url: str,
                *,
                json: dict[str, object],
                timeout: float,
            ) -> object:
                raise AssertionError("blank text must not call Ollama")

        provider = embeddings.BgeM3OllamaEmbeddingProvider(dimension=3, http_client=FakeClient())

        self.assertEqual((0.0, 0.0, 0.0), provider.embed("   "))

    def test_bge_m3_ollama_provider_rejects_dimension_mismatch(self) -> None:
        embeddings = load_module()

        class FakeResponse:
            def raise_for_status(self) -> None:
                return None

            def json(self) -> dict[str, list[float]]:
                return {"embedding": [1.0]}

        class FakeClient:
            def post(
                self,
                _url: str,
                *,
                json: dict[str, object],
                timeout: float,
            ) -> FakeResponse:
                return FakeResponse()

        provider = embeddings.BgeM3OllamaEmbeddingProvider(dimension=2, http_client=FakeClient())

        with self.assertRaisesRegex(ValueError, "dimension mismatch"):
            provider.embed("semantic retrieval query")

    def test_enriched_retrieval_unit_nodes_include_embeddings_and_provider_metadata(self) -> None:
        embeddings = load_module()
        plan = embeddings.load_skills_neo4j.LoadPlan(
            nodes=(
                embeddings.load_skills_neo4j.GraphNode(
                    label="RetrievalUnit",
                    id="retrieval:skill:example:section:0:abcdef123456",
                    properties={
                        "id": "retrieval:skill:example:section:0:abcdef123456",
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

        enriched = embeddings.embed_retrieval_units(plan, embedder)

        retrieval_unit = enriched.nodes[0]
        self.assertEqual(8, len(retrieval_unit.properties["embedding"]))
        self.assertEqual(
            "deterministic-test-embedding", retrieval_unit.properties["embeddingProvider"]
        )
        self.assertEqual(8, retrieval_unit.properties["embeddingDimensions"])

    def test_vector_candidates_include_provenance_without_raw_vectors(self) -> None:
        embeddings = load_module()
        plan = embeddings.load_skills_neo4j.LoadPlan(
            nodes=(
                embeddings.load_skills_neo4j.GraphNode(
                    label="RetrievalUnit",
                    id="retrieval:skill:human-in-the-loop:section:0:approval",
                    properties={
                        "id": "retrieval:skill:human-in-the-loop:section:0:approval",
                        "text": "approval before destructive command",
                        "source_path": "skills/human-in-the-loop/SKILL.md",
                        "section_id": "skill:human-in-the-loop:section:0-objective",
                        "skill_id": "skill:human-in-the-loop",
                    },
                ),
                embeddings.load_skills_neo4j.GraphNode(
                    label="RetrievalUnit",
                    id="retrieval:skill:design-system-practice:section:0:dashboard",
                    properties={
                        "id": "retrieval:skill:design-system-practice:section:0:dashboard",
                        "text": "dashboard typography and layout",
                        "source_path": "skills/design-system-practice/SKILL.md",
                        "section_id": "skill:design-system-practice:section:0-objective",
                        "skill_id": "skill:design-system-practice",
                    },
                ),
            ),
            relationships=(),
        )
        embedder = embeddings.DeterministicEmbeddingProvider(dimension=8)
        enriched = embeddings.embed_retrieval_units(plan, embedder)

        candidates = embeddings.query_vector_candidates(
            enriched,
            query_text="approval before destructive command",
            embedder=embedder,
            limit=1,
        )

        self.assertEqual(
            "retrieval:skill:human-in-the-loop:section:0:approval",
            candidates[0].retrieval_unit_id,
        )
        self.assertGreaterEqual(candidates[0].score, 0.0)
        self.assertEqual(
            "skills/human-in-the-loop/SKILL.md",
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
                        "retrieval_unit_id": "retrieval:skill:human-in-the-loop:section:0:approval",
                        "score": 0.91,
                        "source_path": "skills/human-in-the-loop/SKILL.md",
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

        self.assertEqual("retrieval_unit_embedding_vector", graph.calls[0]["index_name"])
        self.assertEqual(8, len(graph.calls[0]["embedding"]))
        self.assertEqual(1, graph.calls[0]["limit"])
        self.assertEqual(
            "retrieval:skill:human-in-the-loop:section:0:approval",
            candidates[0].retrieval_unit_id,
        )
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
                        "retrieval_unit_id": "retrieval:skill:human-in-the-loop:section:0:approval",
                        "score": 0.91,
                        "source_path": "skills/human-in-the-loop/SKILL.md",
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
            "retrieval_unit_embedding_vector",
            embedding=(0.1, 0.2),
            limit=1,
        )

        self.assertIn("CALL db.index.vector.queryNodes", driver.session_instance.query)
        self.assertEqual(
            "retrieval_unit_embedding_vector", driver.session_instance.parameters["index_name"]
        )
        self.assertEqual([0.1, 0.2], driver.session_instance.parameters["embedding"])
        self.assertEqual(1, driver.session_instance.parameters["limit"])
        self.assertEqual(
            "retrieval:skill:human-in-the-loop:section:0:approval",
            records[0]["retrieval_unit_id"],
        )
        self.assertEqual("deterministic-test-embedding", records[0]["embedding_provider"])


if __name__ == "__main__":
    unittest.main()
