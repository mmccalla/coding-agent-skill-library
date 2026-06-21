#!/usr/bin/env python3
"""Embed skill chunks and return provenance-safe vector candidates."""

from __future__ import annotations

import hashlib
import math
import sys
from argparse import ArgumentParser
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, NamedTuple, Protocol

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import load_skills_neo4j, skills_config

DEFAULT_CONFIG_PATH = skills_config.DEFAULT_CONFIG_PATH
DEFAULT_VECTOR_INDEX = skills_config.Neo4jSettings().vector_index


class EmbeddingProvider(Protocol):
    """Provider contract for deterministic tests and runtime embeddings."""

    provider_name: str
    dimension: int

    def embed(self, text: str) -> tuple[float, ...]:
        """Return an embedding vector for the supplied text."""


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


class VectorCandidate(NamedTuple):
    """A retrieval candidate with provenance but without raw vectors."""

    chunk_id: str
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
                    "RETURN node.id AS chunk_id, score, node.source_path AS source_path, "
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


def embed_skill_chunks(
    plan: load_skills_neo4j.LoadPlan,
    embedder: EmbeddingProvider,
) -> load_skills_neo4j.LoadPlan:
    """Return a load plan with embeddings added to every SkillChunk node."""

    nodes: list[load_skills_neo4j.GraphNode] = []
    for node in plan.nodes:
        if node.label != "SkillChunk":
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
        if node.label != "SkillChunk":
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
                chunk_id=node.id,
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
        sorted(candidates, key=lambda candidate: (-candidate.score, candidate.chunk_id))[:limit]
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
                chunk_id=_string(record, "chunk_id"),
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
) -> load_skills_neo4j.LoadPlan:
    dimension = _embedding_dimension_from_config(config_path)
    plan = load_skills_neo4j.build_repository_load_plan(skills_root)
    return embed_skill_chunks(plan, DeterministicEmbeddingProvider(dimension=dimension))


def main(argv: Sequence[str] | None = None) -> int:  # pragma: no cover
    parser = ArgumentParser(description="Create deterministic SkillChunk embeddings.")
    parser.add_argument("--apply", action="store_true", help="Write embedded chunks to Neo4j.")
    parser.add_argument(
        "--batch-size", type=int, default=500, help="Transactional load batch size."
    )
    parser.add_argument("--query", help="Optional query text for local candidate inspection.")
    parser.add_argument("--limit", type=int, default=5, help="Maximum candidates to print.")
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))

    settings = skills_config.load_settings()
    dimension = settings.neo4j.embedding_dimensions
    embedder = DeterministicEmbeddingProvider(dimension=dimension)
    plan = embed_skill_chunks(load_skills_neo4j.build_repository_load_plan(), embedder)
    chunk_count = sum(1 for node in plan.nodes if node.label == "SkillChunk")
    print(
        "Embedded SkillChunk nodes: "
        f"{chunk_count}; provider={embedder.provider_name}; dimensions={dimension}"
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
                f"- {candidate.chunk_id} score={candidate.score:.6f} "
                f"source={candidate.source_path} section={candidate.section_id}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
