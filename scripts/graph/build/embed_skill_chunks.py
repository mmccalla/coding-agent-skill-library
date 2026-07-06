#!/usr/bin/env python3
"""Embed retrieval units and return provenance-safe vector candidates."""

from __future__ import annotations

import hashlib
import math
import os
import sys
from argparse import ArgumentParser
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, NamedTuple, Protocol

import httpx

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from scripts.graph.load import load_skills_neo4j
from scripts.lib.config import skills_config

DEFAULT_CONFIG_PATH = skills_config.DEFAULT_CONFIG_PATH
DEFAULT_VECTOR_INDEX = skills_config.Neo4jSettings().vector_index


class EmbeddingProvider(Protocol):
    """Provider contract for deterministic tests and runtime embeddings."""

    provider_name: str
    dimension: int

    def embed(self, text: str) -> tuple[float, ...]:
        """Return an embedding vector for the supplied text."""


class EmbeddingHttpClient(Protocol):
    """Small HTTP client contract for embedding providers."""

    def post(
        self,
        url: str,
        *,
        json: Mapping[str, object],
        timeout: float,
    ) -> httpx.Response:
        """POST JSON to an embedding endpoint."""


class DeterministicEmbeddingProvider:
    """Hash-based deterministic embedding provider for CI and offline tests."""

    provider_name = "deterministic-test-embedding"

    def __init__(self, dimension: int) -> None:
        if dimension <= 0:
            raise ValueError("embedding dimension must be positive")
        self.dimension = dimension

    def embed(self, text: str) -> tuple[float, ...]:
        values: list[float] = []
        counter = 0
        while len(values) < self.dimension:
            digest = hashlib.sha256(f"{counter}:{text}".encode()).digest()
            for byte in digest:
                values.append((byte / 127.5) - 1.0)
                if len(values) == self.dimension:
                    break
            counter += 1
        return _normalise(tuple(values))


class BgeM3OllamaEmbeddingProvider:
    """Ollama-backed BGE-M3 embedding provider for production vector embeddings."""

    def __init__(
        self,
        *,
        model: str = "bge-m3:567m",
        base_url: str = "http://127.0.0.1:11434",
        dimension: int = 1024,
        timeout_seconds: float = 30.0,
        http_client: EmbeddingHttpClient | None = None,
    ) -> None:
        if dimension <= 0:
            raise ValueError("embedding dimension must be positive")
        if not model.strip():
            raise ValueError("embedding model must be non-empty")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.dimension = dimension
        self.timeout_seconds = timeout_seconds
        self.provider_name = f"ollama:{model}"
        self._http_client = http_client or httpx.Client()

    def embed(self, text: str) -> tuple[float, ...]:
        """Return a normalised BGE-M3 embedding from a local Ollama endpoint."""

        if not text.strip():
            # Ollama returns an empty list for blank prompts; keep plan embedding valid.
            return tuple(0.0 for _ in range(self.dimension))

        response = self._http_client.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.model, "prompt": text},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        embedding = payload.get("embedding") if isinstance(payload, dict) else None
        if not isinstance(embedding, list):
            raise ValueError("Ollama embedding response did not include an embedding list")
        vector = tuple(float(value) for value in embedding)
        if len(vector) != self.dimension:
            raise ValueError(
                f"embedding dimension mismatch: expected {self.dimension}, got {len(vector)}"
            )
        return _normalise(vector)


class VectorCandidate(NamedTuple):
    """A retrieval candidate with provenance but without raw vectors."""

    retrieval_unit_id: str
    score: float
    source_path: str
    section_id: str
    skill_id: str
    text: str
    embedding_provider: str
    embedding_dimensions: int


class VectorQueryGraph(Protocol):
    """Graph contract for Neo4j vector index candidate retrieval."""

    def query_vector_index(
        self,
        index_name: str,
        embedding: tuple[float, ...],
        limit: int,
    ) -> Sequence[Mapping[str, object]]:
        """Query a named vector index and return candidate mappings."""


class Neo4jVectorQueryGraph:
    """Neo4j driver-backed vector index query adapter."""

    def __init__(self, driver: Any) -> None:
        self._driver = driver

    def query_vector_index(
        self,
        index_name: str,
        embedding: tuple[float, ...],
        limit: int,
    ) -> Sequence[Mapping[str, object]]:
        with self._driver.session() as session:
            records = session.run(
                (
                    "CALL db.index.vector.queryNodes($index_name, $limit, $embedding) "
                    "YIELD node, score "
                    "RETURN node.id AS retrieval_unit_id, score, node.source_path AS source_path, "
                    "node.section_id AS section_id, node.skill_id AS skill_id, "
                    "node.text AS text, node.embeddingProvider AS embedding_provider, "
                    "node.embeddingDimensions AS embedding_dimensions"
                ),
                index_name=index_name,
                limit=limit,
                embedding=list(embedding),
            )
            return tuple(dict(record) for record in records)


def _normalise(vector: Sequence[float]) -> tuple[float, ...]:
    magnitude = math.sqrt(sum(value * value for value in vector))
    if magnitude == 0.0:
        return tuple(0.0 for _ in vector)
    return tuple(value / magnitude for value in vector)


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("vectors must use the same dimension")
    return sum(
        left_value * right_value for left_value, right_value in zip(left, right, strict=True)
    )


def _string(properties: Mapping[str, object], key: str) -> str:
    value = properties.get(key)
    return value if isinstance(value, str) else ""


def _integer(properties: Mapping[str, object], key: str) -> int:
    value = properties.get(key)
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _float(value: object) -> float:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return 0.0


def _embedding_dimension_from_config(config_path: Path = DEFAULT_CONFIG_PATH) -> int:
    return skills_config.load_settings(config_path).neo4j.embedding_dimensions


def resolve_embedding_provider(
    settings: skills_config.SkillsKgSettings | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    force_deterministic: bool = False,
    http_client: EmbeddingHttpClient | None = None,
) -> EmbeddingProvider:
    """Resolve the embedding provider for production, CI, or explicit overrides.

    Production defaults to pinned Ollama BGE-M3. PR CI and offline evaluation force
    deterministic embeddings via ``force_deterministic=True`` or
    ``SKILLS_EMBEDDING_PROVIDER=deterministic``.
    """

    runtime_settings = settings or skills_config.load_settings(environ=environ)
    env = os.environ if environ is None else environ
    provider = env.get("SKILLS_EMBEDDING_PROVIDER", runtime_settings.neo4j.embedding_provider)
    dimension = runtime_settings.neo4j.embedding_dimensions
    if force_deterministic or provider in {"deterministic", "deterministic-test-embedding"}:
        return DeterministicEmbeddingProvider(dimension=dimension)
    if provider == "ollama-bge-m3" or provider.startswith("ollama:"):
        model = runtime_settings.neo4j.ollama_model
        if provider.startswith("ollama:") and provider != "ollama-bge-m3":
            model = provider.removeprefix("ollama:")
        return BgeM3OllamaEmbeddingProvider(
            model=model,
            base_url=runtime_settings.neo4j.ollama_base_url,
            dimension=dimension,
            http_client=http_client,
        )
    raise ValueError(
        "Unsupported embedding provider "
        f"'{provider}'. Expected deterministic, deterministic-test-embedding, "
        "ollama-bge-m3, or ollama:<model>."
    )


def embed_retrieval_units(
    plan: load_skills_neo4j.LoadPlan,
    embedder: EmbeddingProvider,
) -> load_skills_neo4j.LoadPlan:
    """Return a load plan with embeddings added to every RetrievalUnit node."""

    nodes: list[load_skills_neo4j.GraphNode] = []
    for node in plan.nodes:
        if node.label != "RetrievalUnit":
            nodes.append(node)
            continue
        properties = dict(node.properties)
        text = _string(properties, "text")
        properties["embedding"] = list(embedder.embed(text))
        properties["embeddingProvider"] = embedder.provider_name
        properties["embeddingDimensions"] = embedder.dimension
        nodes.append(
            load_skills_neo4j.GraphNode(
                label=node.label,
                id=node.id,
                properties=properties,
            )
        )
    return load_skills_neo4j.LoadPlan(
        nodes=tuple(nodes),
        relationships=plan.relationships,
    )


def query_vector_candidates(
    plan: load_skills_neo4j.LoadPlan,
    query_text: str,
    embedder: EmbeddingProvider,
    limit: int = 10,
) -> tuple[VectorCandidate, ...]:
    """Return top vector candidates with source and section provenance."""

    query_embedding = embedder.embed(query_text)
    candidates: list[VectorCandidate] = []
    for node in plan.nodes:
        if node.label != "RetrievalUnit":
            continue
        embedding = node.properties.get("embedding")
        if not isinstance(embedding, list):
            continue
        vector = tuple(value for value in embedding if isinstance(value, float))
        if len(vector) != embedder.dimension:
            continue
        score = _cosine(query_embedding, vector)
        candidates.append(
            VectorCandidate(
                retrieval_unit_id=node.id,
                score=score,
                source_path=_string(node.properties, "source_path"),
                section_id=_string(node.properties, "section_id"),
                skill_id=_string(node.properties, "skill_id"),
                text=_string(node.properties, "text"),
                embedding_provider=_string(node.properties, "embeddingProvider"),
                embedding_dimensions=_integer(node.properties, "embeddingDimensions"),
            )
        )
    return tuple(
        sorted(candidates, key=lambda candidate: (-candidate.score, candidate.retrieval_unit_id))[
            :limit
        ]
    )


def query_neo4j_vector_candidates(
    graph: VectorQueryGraph,
    query_text: str,
    embedder: EmbeddingProvider,
    limit: int = 10,
    index_name: str = DEFAULT_VECTOR_INDEX,
) -> tuple[VectorCandidate, ...]:
    """Query Neo4j's vector index and return provenance-safe candidates."""

    records = graph.query_vector_index(index_name, embedder.embed(query_text), limit)
    return vector_candidates_from_records(records)


def vector_candidates_from_records(
    records: Sequence[Mapping[str, object]],
) -> tuple[VectorCandidate, ...]:
    """Convert Neo4j vector result records into provenance-safe candidates."""

    candidates = []
    for record in records:
        candidates.append(
            VectorCandidate(
                retrieval_unit_id=_string(record, "retrieval_unit_id"),
                score=_float(record.get("score", 0.0)),
                source_path=_string(record, "source_path"),
                section_id=_string(record, "section_id"),
                skill_id=_string(record, "skill_id"),
                text=_string(record, "text"),
                embedding_provider=_string(record, "embedding_provider"),
                embedding_dimensions=_integer(record, "embedding_dimensions"),
            )
        )
    return tuple(candidates)


def build_embedded_repository_load_plan(
    skills_root: Path = Path("skills"),
    config_path: Path = DEFAULT_CONFIG_PATH,
    *,
    embedder: EmbeddingProvider | None = None,
    force_deterministic: bool = False,
) -> load_skills_neo4j.LoadPlan:
    """Build an embedded load plan using production or CI embedding policy."""

    settings = skills_config.load_settings(config_path)
    runtime_embedder = embedder or resolve_embedding_provider(
        settings,
        force_deterministic=force_deterministic,
    )
    plan = load_skills_neo4j.build_repository_load_plan(skills_root)
    return embed_retrieval_units(plan, runtime_embedder)


def main(argv: Sequence[str] | None = None) -> int:  # pragma: no cover
    parser = ArgumentParser(description="Create RetrievalUnit embeddings for the Skills KG.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Idempotently write embedded retrieval units to Neo4j.",
    )
    parser.add_argument(
        "--batch-size", type=int, default=500, help="Transactional load batch size."
    )
    parser.add_argument(
        "--provider",
        choices=("auto", "deterministic", "ollama-bge-m3"),
        default="auto",
        help="Embedding provider override. auto uses config/env (production BGE, CI deterministic).",
    )
    parser.add_argument(
        "--ollama-url",
        default=None,
        help="Base URL for the local Ollama embedding endpoint.",
    )
    parser.add_argument(
        "--ollama-model",
        default=None,
        help="Ollama embedding model for --provider ollama-bge-m3.",
    )
    parser.add_argument(
        "--embedding-dimensions",
        type=int,
        default=None,
        help="Override embedding dimensions for the selected provider.",
    )
    parser.add_argument("--query", help="Optional query text for local candidate inspection.")
    parser.add_argument("--limit", type=int, default=5, help="Maximum candidates to print.")
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))

    environ = dict(os.environ)
    if args.provider != "auto":
        environ["SKILLS_EMBEDDING_PROVIDER"] = args.provider
    if args.ollama_url:
        environ["SKILLS_OLLAMA_BASE_URL"] = args.ollama_url
    if args.ollama_model:
        environ["SKILLS_OLLAMA_MODEL"] = args.ollama_model
    if isinstance(args.embedding_dimensions, int):
        environ["SKILLS_EMBEDDING_DIMENSIONS"] = str(args.embedding_dimensions)

    settings = skills_config.load_settings(environ=environ)
    embedder = resolve_embedding_provider(settings, environ=environ)
    plan = embed_retrieval_units(load_skills_neo4j.build_repository_load_plan(), embedder)
    retrieval_unit_count = sum(1 for node in plan.nodes if node.label == "RetrievalUnit")
    print(
        "Embedded RetrievalUnit nodes: "
        f"{retrieval_unit_count}; provider={embedder.provider_name}; "
        f"dimensions={embedder.dimension}"
    )
    if args.apply:
        graph = load_skills_neo4j.neo4j_graph_from_env()
        report = load_skills_neo4j.load_plan(
            graph,
            plan,
            batch_size=args.batch_size,
            schema_statements=load_skills_neo4j.read_schema_statements(),
            schema_parameters={"embedding_dimensions": settings.neo4j.embedding_dimensions},
        )
        print("Skills KG embedded load report")
        for key, value in report.logical_counts.items():
            print(f"- {key}: {value}")
        print(f"- batches: {report.batches}")
    if args.query:
        for candidate in query_vector_candidates(plan, args.query, embedder, args.limit):
            print(
                f"- {candidate.retrieval_unit_id} score={candidate.score:.6f} "
                f"source={candidate.source_path} section={candidate.section_id}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
