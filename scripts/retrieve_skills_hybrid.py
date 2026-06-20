#!/usr/bin/env python3
"""Hybrid full-text, vector and graph retrieval for skills."""

from __future__ import annotations

import re
import sys
from argparse import ArgumentParser
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping, NamedTuple, Sequence

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import embed_skill_chunks, load_skills_neo4j
from scripts.embed_skill_chunks import VectorCandidate

MIN_CONFIDENT_SCORE = 0.2
DEFAULT_TOKEN_BUDGET = 1200


class SkillRecommendation(NamedTuple):
    """A ranked skill recommendation with source-backed evidence."""

    skill_id: str
    skill_name: str
    score: float
    graph_score: float
    vector_score: float
    full_text_score: float
    evidence_snippets: tuple[str, ...]
    source_paths: tuple[str, ...]
    section_ids: tuple[str, ...]
    evidence_paths: tuple[str, ...]
    why: str


class HybridRetrievalResult(NamedTuple):
    """Retrieval result safe for agent consumption."""

    query: str
    uncertain: bool
    message: str
    recommendations: tuple[SkillRecommendation, ...]


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2 and token not in {"and", "the", "for", "with"}
    }


def _string(properties: Mapping[str, object], key: str) -> str:
    value = properties.get(key)
    return value if isinstance(value, str) else ""


def _skill_nodes(plan: load_skills_neo4j.LoadPlan) -> dict[str, load_skills_neo4j.GraphNode]:
    return {node.id: node for node in plan.nodes if node.label == "Skill"}


def _chunk_nodes(plan: load_skills_neo4j.LoadPlan) -> tuple[load_skills_neo4j.GraphNode, ...]:
    return tuple(node for node in plan.nodes if node.label == "SkillChunk")


def _text_scores(
    plan: load_skills_neo4j.LoadPlan,
    query_text: str,
) -> tuple[dict[str, float], dict[str, tuple[str, ...]]]:
    query_tokens = _tokens(query_text)
    if not query_tokens:
        return {}, {}
    scores: dict[str, float] = defaultdict(float)
    matched_chunks: dict[str, list[str]] = defaultdict(list)
    for chunk in _chunk_nodes(plan):
        chunk_tokens = _tokens(_string(chunk.properties, "text"))
        overlap = len(query_tokens & chunk_tokens)
        if overlap:
            skill_id = _string(chunk.properties, "skill_id")
            scores[skill_id] = max(scores[skill_id], overlap / len(query_tokens))
            matched_chunks[skill_id].append(chunk.id)
    return scores, {skill_id: tuple(chunk_ids) for skill_id, chunk_ids in matched_chunks.items()}


def _vector_scores(vector_candidates: Sequence[VectorCandidate]) -> dict[str, float]:
    scores: dict[str, float] = defaultdict(float)
    for candidate in vector_candidates:
        scores[candidate.skill_id] = max(scores[candidate.skill_id], candidate.score)
    return scores


def _vector_chunk_ids(vector_candidates: Sequence[VectorCandidate]) -> dict[str, tuple[str, ...]]:
    chunk_ids: dict[str, list[str]] = defaultdict(list)
    for candidate in vector_candidates:
        chunk_ids[candidate.skill_id].append(candidate.chunk_id)
    return {skill_id: tuple(values) for skill_id, values in chunk_ids.items()}


def _graph_evidence(
    plan: load_skills_neo4j.LoadPlan,
    start_skill_ids: set[str],
    max_depth: int,
) -> tuple[dict[str, float], dict[str, tuple[str, ...]]]:
    connected_relationships = {
        "RELATED_TO",
        "PRECEDES",
        "REQUIRES",
        "COMPLEMENTS",
        "REFINES",
        "GOVERNS",
        "VALIDATES",
        "HAS_WORKFLOW_STAGE",
        "HAS_TASK_SHAPE",
        "HAS_CAPABILITY",
    }
    paths: dict[str, list[str]] = defaultdict(list)
    counts: Counter[str] = Counter()
    if max_depth <= 0:
        return {}, {}
    adjacency: dict[str, list[load_skills_neo4j.GraphRelationship]] = defaultdict(list)
    for relationship in plan.relationships:
        if relationship.type not in connected_relationships:
            continue
        if relationship.source_label == "Skill":
            adjacency[relationship.source_id].append(relationship)
        if relationship.target_label == "Skill":
            adjacency[relationship.target_id].append(relationship)
    for start_skill_id in start_skill_ids:
        visited = {start_skill_id}
        queue: list[tuple[str, int]] = [(start_skill_id, 0)]
        while queue:
            current, depth = queue.pop(0)
            if depth >= max_depth:
                continue
            for relationship in adjacency.get(current, []):
                path_text = (
                    f"{relationship.source_id} -[{relationship.type}]-> "
                    f"{relationship.target_id}"
                )
                if path_text not in paths[start_skill_id]:
                    paths[start_skill_id].append(path_text)
                    counts[start_skill_id] += 1
                neighbour = ""
                if relationship.source_label == "Skill" and relationship.source_id != current:
                    neighbour = relationship.source_id
                elif relationship.target_label == "Skill" and relationship.target_id != current:
                    neighbour = relationship.target_id
                if neighbour and neighbour not in visited:
                    visited.add(neighbour)
                    queue.append((neighbour, depth + 1))
    scores = {skill_id: min(1.0, count / 4.0) for skill_id, count in counts.items()}
    return scores, {skill_id: tuple(skill_paths[:5]) for skill_id, skill_paths in paths.items()}


def _chunk_evidence(
    plan: load_skills_neo4j.LoadPlan,
    skill_id: str,
    preferred_chunk_ids: Sequence[str],
    token_budget: int,
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    snippets: list[str] = []
    source_paths: list[str] = []
    section_ids: list[str] = []
    remaining = token_budget
    chunks_by_id = {chunk.id: chunk for chunk in _chunk_nodes(plan)}
    ordered_chunks = [
        chunks_by_id[chunk_id]
        for chunk_id in preferred_chunk_ids
        if chunk_id in chunks_by_id
    ]
    ordered_chunks.extend(
        chunk
        for chunk in _chunk_nodes(plan)
        if chunk.id not in set(preferred_chunk_ids)
    )
    for chunk in ordered_chunks:
        if _string(chunk.properties, "skill_id") != skill_id:
            continue
        text = _string(chunk.properties, "text")
        snippet = text[:240]
        cost = max(1, len(snippet.split()))
        if cost > remaining:
            break
        snippets.append(snippet)
        source_paths.append(_string(chunk.properties, "source_path"))
        section_ids.append(_string(chunk.properties, "section_id"))
        remaining -= cost
    return tuple(snippets[:3]), tuple(sorted(set(source_paths))), tuple(sorted(set(section_ids)))


def retrieve_hybrid_skills(
    plan: load_skills_neo4j.LoadPlan,
    query_text: str,
    vector_candidates: Sequence[VectorCandidate] = (),
    limit: int = 5,
    max_depth: int = 2,
    token_budget: int = DEFAULT_TOKEN_BUDGET,
) -> HybridRetrievalResult:
    """Rank skills using text, vector and graph evidence."""

    limit = max(1, min(limit, 20))
    skills = _skill_nodes(plan)
    text_scores, text_chunk_ids = _text_scores(plan, query_text)
    vector_scores = _vector_scores(vector_candidates)
    vector_chunk_ids = _vector_chunk_ids(vector_candidates)
    candidate_skill_ids = set(text_scores) | set(vector_scores)
    graph_scores, evidence_paths = _graph_evidence(plan, candidate_skill_ids, max_depth)
    recommendation_inputs: list[
        tuple[str, float, float, float, float, tuple[str, ...]]
    ] = []

    for skill_id in candidate_skill_ids:
        skill = skills.get(skill_id)
        if skill is None:
            continue
        full_text_score = text_scores.get(skill_id, 0.0)
        vector_score = max(0.0, vector_scores.get(skill_id, 0.0))
        graph_score = graph_scores.get(skill_id, 0.0)
        score = (0.35 * full_text_score) + (0.35 * vector_score) + (0.55 * graph_score)
        preferred_chunk_ids = tuple(
            dict.fromkeys((*text_chunk_ids.get(skill_id, ()), *vector_chunk_ids.get(skill_id, ())))
        )
        recommendation_inputs.append(
            (skill_id, score, graph_score, vector_score, full_text_score, preferred_chunk_ids)
        )

    recommendations: list[SkillRecommendation] = []
    remaining_budget = token_budget
    for skill_id, score, graph_score, vector_score, full_text_score, preferred_chunk_ids in sorted(
        recommendation_inputs,
        key=lambda item: (-item[1], _string(skills[item[0]].properties, "name")),
    ):
        skill = skills[skill_id]
        snippets, source_paths, section_ids = _chunk_evidence(
            plan,
            skill_id,
            preferred_chunk_ids,
            remaining_budget,
        )
        if not snippets:
            continue
        remaining_budget -= sum(len(snippet.split()) for snippet in snippets)
        recommendations.append(
            SkillRecommendation(
                skill_id=skill_id,
                skill_name=_string(skill.properties, "name"),
                score=round(score, 6),
                graph_score=round(graph_score, 6),
                vector_score=round(vector_score, 6),
                full_text_score=round(full_text_score, 6),
                evidence_snippets=snippets,
                source_paths=source_paths,
                section_ids=section_ids,
                evidence_paths=evidence_paths.get(skill_id, ()),
                why=(
                    "Selected from full-text, vector and graph evidence; "
                    "graph connectivity is weighted to avoid isolated matches."
                ),
            )
        )
        if remaining_budget <= 0:
            break

    ranked = tuple(
        sorted(recommendations, key=lambda item: (-item.score, item.skill_name))[:limit]
    )
    if not ranked or ranked[0].score < MIN_CONFIDENT_SCORE:
        return HybridRetrievalResult(
            query=query_text,
            uncertain=True,
            message="No confident skill match found; provide a narrower task description.",
            recommendations=(),
        )
    return HybridRetrievalResult(
        query=query_text,
        uncertain=False,
        message="Hybrid retrieval returned connected, source-backed skill evidence.",
        recommendations=ranked,
    )


def fixture_load_plan() -> load_skills_neo4j.LoadPlan:
    """Small connected graph fixture used by tests and examples."""

    nodes = (
        load_skills_neo4j.GraphNode(
            "Skill",
            "skill:kg-enabled-rag",
            {"id": "skill:kg-enabled-rag", "name": "kg-enabled-rag"},
        ),
        load_skills_neo4j.GraphNode(
            "Skill",
            "skill:knowledge-retrieval-rag",
            {"id": "skill:knowledge-retrieval-rag", "name": "knowledge-retrieval-rag"},
        ),
        load_skills_neo4j.GraphNode(
            "Skill",
            "skill:generic-documentation",
            {"id": "skill:generic-documentation", "name": "generic-documentation"},
        ),
        load_skills_neo4j.GraphNode(
            "SkillChunk",
            "chunk-kg",
            {
                "id": "chunk-kg",
                "skill_id": "skill:kg-enabled-rag",
                "text": "Use KG-enabled RAG for graph-grounded retrieval.",
                "source_path": "skills/data-architecture/kg-enabled-rag/SKILL.md",
                "section_id": "skill:kg-enabled-rag:section:0-objective",
            },
        ),
        load_skills_neo4j.GraphNode(
            "SkillChunk",
            "chunk-retrieval",
            {
                "id": "chunk-retrieval",
                "skill_id": "skill:knowledge-retrieval-rag",
                "text": "Use retrieval evidence and source-backed context.",
                "source_path": "skills/agentic-patterns/knowledge-retrieval-rag/SKILL.md",
                "section_id": "skill:knowledge-retrieval-rag:section:0-objective",
            },
        ),
        load_skills_neo4j.GraphNode(
            "SkillChunk",
            "chunk-generic",
            {
                "id": "chunk-generic",
                "skill_id": "skill:generic-documentation",
                "text": "General documentation guidance.",
                "source_path": "skills/reference/generic-documentation/SKILL.md",
                "section_id": "skill:generic-documentation:section:0-objective",
            },
        ),
    )
    relationships = (
        load_skills_neo4j.GraphRelationship(
            "COMPLEMENTS",
            "Skill",
            "skill:kg-enabled-rag",
            "Skill",
            "skill:knowledge-retrieval-rag",
            {"mapping_rule_id": "test-rule"},
        ),
        load_skills_neo4j.GraphRelationship(
            "HAS_WORKFLOW_STAGE",
            "Skill",
            "skill:kg-enabled-rag",
            "WorkflowStage",
            "retrieval",
            {},
        ),
        load_skills_neo4j.GraphRelationship(
            "HAS_CAPABILITY",
            "Skill",
            "skill:kg-enabled-rag",
            "Capability",
            "graph-rag",
            {},
        ),
        load_skills_neo4j.GraphRelationship(
            "HAS_TASK_SHAPE",
            "Skill",
            "skill:kg-enabled-rag",
            "TaskShape",
            "ontology-retrieval",
            {},
        ),
    )
    return load_skills_neo4j.LoadPlan(nodes=nodes, relationships=relationships)


def main(argv: Sequence[str] | None = None) -> int:
    parser = ArgumentParser(description="Run local hybrid skill retrieval.")
    parser.add_argument("query", help="Task query to retrieve skills for.")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))

    plan = embed_skill_chunks.build_embedded_repository_load_plan(Path("skills"))
    embedder = embed_skill_chunks.DeterministicEmbeddingProvider(dimension=1536)
    vector_candidates = embed_skill_chunks.query_vector_candidates(plan, args.query, embedder, args.limit)
    result = retrieve_hybrid_skills(plan, args.query, vector_candidates, args.limit)
    print(result.message)
    for recommendation in result.recommendations:
        print(
            f"- {recommendation.skill_name} score={recommendation.score:.3f} "
            f"sources={', '.join(recommendation.source_paths)}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
