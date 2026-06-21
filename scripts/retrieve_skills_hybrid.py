#!/usr/bin/env python3
"""Hybrid full-text, vector and graph retrieval for skills."""

from __future__ import annotations

import re
import sys
from argparse import ArgumentParser
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, NamedTuple

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import embed_skill_chunks, load_skills_neo4j, skills_config
from scripts.embed_skill_chunks import VectorCandidate

DEFAULT_RETRIEVAL_SETTINGS = skills_config.load_settings().retrieval
MIN_CONFIDENT_SCORE = DEFAULT_RETRIEVAL_SETTINGS.min_confident_score
DEFAULT_TOKEN_BUDGET = DEFAULT_RETRIEVAL_SETTINGS.default_token_budget
CONNECTED_RELATIONSHIP_TYPES = frozenset(
    {
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
)


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


def _retrieval_unit_nodes(
    plan: load_skills_neo4j.LoadPlan,
) -> tuple[load_skills_neo4j.GraphNode, ...]:
    return tuple(node for node in plan.nodes if node.label == "RetrievalUnit")


def _bridge_assertion_nodes(
    plan: load_skills_neo4j.LoadPlan,
) -> tuple[load_skills_neo4j.GraphNode, ...]:
    return tuple(node for node in plan.nodes if node.label == "BridgeAssertion")


def _text_scores(
    plan: load_skills_neo4j.LoadPlan,
    query_text: str,
) -> tuple[dict[str, float], dict[str, tuple[str, ...]]]:
    query_tokens = _tokens(query_text)
    if not query_tokens:
        return {}, {}
    scores: dict[str, float] = defaultdict(float)
    matched_units: dict[str, list[str]] = defaultdict(list)
    for unit in _retrieval_unit_nodes(plan):
        unit_tokens = _tokens(_string(unit.properties, "text"))
        overlap = len(query_tokens & unit_tokens)
        if overlap:
            skill_id = _string(unit.properties, "skill_id")
            scores[skill_id] = max(scores[skill_id], overlap / len(query_tokens))
            matched_units[skill_id].append(unit.id)
    return scores, {skill_id: tuple(unit_ids) for skill_id, unit_ids in matched_units.items()}


def _vector_scores(
    vector_candidates: Sequence[VectorCandidate],
    min_score: float,
) -> dict[str, float]:
    scores: dict[str, float] = defaultdict(float)
    for candidate in vector_candidates:
        if candidate.score < min_score:
            continue
        scores[candidate.skill_id] = max(scores[candidate.skill_id], candidate.score)
    return scores


def _vector_retrieval_unit_ids(
    vector_candidates: Sequence[VectorCandidate],
    min_score: float,
) -> dict[str, tuple[str, ...]]:
    unit_ids: dict[str, list[str]] = defaultdict(list)
    for candidate in vector_candidates:
        if candidate.score < min_score:
            continue
        unit_ids[candidate.skill_id].append(candidate.retrieval_unit_id)
    return {skill_id: tuple(values) for skill_id, values in unit_ids.items()}


def _graph_evidence(
    plan: load_skills_neo4j.LoadPlan,
    start_skill_ids: set[str],
    max_depth: int,
) -> tuple[dict[str, float], dict[str, tuple[str, ...]]]:
    paths: dict[str, list[str]] = defaultdict(list)
    counts: Counter[str] = Counter()
    if max_depth <= 0:
        return {}, {}
    adjacency: dict[str, list[load_skills_neo4j.GraphRelationship]] = defaultdict(list)
    for relationship in plan.relationships:
        if relationship.type not in CONNECTED_RELATIONSHIP_TYPES:
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
                    f"{relationship.source_id} -[{relationship.type}]-> {relationship.target_id}"
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


def _confidence(value: object) -> float:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return max(0.0, min(1.0, float(value)))
    return 1.0


def _bridge_scores(
    plan: load_skills_neo4j.LoadPlan,
    query_text: str,
) -> tuple[dict[str, float], dict[str, tuple[str, ...]]]:
    query_tokens = _tokens(query_text)
    if not query_tokens:
        return {}, {}
    scores: dict[str, float] = defaultdict(float)
    evidence_paths: dict[str, list[str]] = defaultdict(list)
    for bridge in _bridge_assertion_nodes(plan):
        properties = bridge.properties
        skill_id = _string(properties, "skill_id")
        bridge_kind = _string(properties, "kind")
        bridge_value = _string(properties, "value")
        rule_id = _string(properties, "rule_id") or _string(properties, "source")
        rationale = _string(properties, "rationale")
        source_ref = _string(properties, "source_ref")
        bridge_tokens = _tokens(" ".join((bridge_kind, bridge_value, rationale, source_ref)))
        if not skill_id or not bridge_tokens:
            continue
        overlap = len(query_tokens & bridge_tokens)
        if not overlap:
            continue
        specificity = overlap / len(bridge_tokens)
        score = min(1.0, specificity * _confidence(properties.get("confidence")))
        scores[skill_id] = max(scores[skill_id], score)
        evidence_text = f"{rule_id} ({bridge_kind}:{bridge_value})"
        if evidence_text not in evidence_paths[skill_id]:
            evidence_paths[skill_id].append(evidence_text)
    return scores, {skill_id: tuple(paths[:5]) for skill_id, paths in evidence_paths.items()}


def _retrieval_unit_evidence(
    plan: load_skills_neo4j.LoadPlan,
    skill_id: str,
    preferred_unit_ids: Sequence[str],
    token_budget: int,
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    snippets: list[str] = []
    source_paths: list[str] = []
    section_ids: list[str] = []
    remaining = token_budget
    units_by_id = {unit.id: unit for unit in _retrieval_unit_nodes(plan)}
    ordered_units = [
        units_by_id[unit_id] for unit_id in preferred_unit_ids if unit_id in units_by_id
    ]
    ordered_units.extend(
        unit for unit in _retrieval_unit_nodes(plan) if unit.id not in set(preferred_unit_ids)
    )
    for unit in ordered_units:
        if _string(unit.properties, "skill_id") != skill_id:
            continue
        text = _string(unit.properties, "text")
        snippet = text[:240]
        cost = max(1, len(snippet.split()))
        if cost > remaining:
            break
        snippets.append(snippet)
        source_paths.append(_string(unit.properties, "source_path"))
        section_ids.append(_string(unit.properties, "section_id"))
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

    settings = skills_config.load_settings().retrieval
    limit = max(1, min(limit, settings.max_limit))
    max_depth = max(0, min(max_depth, settings.max_depth))
    skills = _skill_nodes(plan)
    text_scores, text_unit_ids = _text_scores(plan, query_text)
    vector_scores = _vector_scores(vector_candidates, settings.min_vector_candidate_score)
    vector_unit_ids = _vector_retrieval_unit_ids(
        vector_candidates, settings.min_vector_candidate_score
    )
    bridge_scores, bridge_evidence_paths = _bridge_scores(plan, query_text)
    candidate_skill_ids = set(text_scores) | set(vector_scores) | set(bridge_scores)
    graph_scores, evidence_paths = _graph_evidence(plan, candidate_skill_ids, max_depth)
    recommendation_inputs: list[tuple[str, float, float, float, float, tuple[str, ...]]] = []

    for skill_id in candidate_skill_ids:
        skill = skills.get(skill_id)
        if skill is None:
            continue
        full_text_score = text_scores.get(skill_id, 0.0)
        vector_score = max(0.0, vector_scores.get(skill_id, 0.0))
        graph_score = max(graph_scores.get(skill_id, 0.0), bridge_scores.get(skill_id, 0.0))
        score = (
            (0.45 * full_text_score)
            + (0.10 * vector_score)
            + (0.15 * graph_scores.get(skill_id, 0.0))
            + (0.80 * bridge_scores.get(skill_id, 0.0))
        )
        preferred_unit_ids = tuple(
            dict.fromkeys((*text_unit_ids.get(skill_id, ()), *vector_unit_ids.get(skill_id, ())))
        )
        recommendation_inputs.append(
            (skill_id, score, graph_score, vector_score, full_text_score, preferred_unit_ids)
        )

    recommendations: list[SkillRecommendation] = []
    remaining_budget = token_budget
    for skill_id, score, graph_score, vector_score, full_text_score, preferred_unit_ids in sorted(
        recommendation_inputs,
        key=lambda item: (-item[1], _string(skills[item[0]].properties, "name")),
    ):
        skill = skills[skill_id]
        snippets, source_paths, section_ids = _retrieval_unit_evidence(
            plan,
            skill_id,
            preferred_unit_ids,
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
                evidence_paths=tuple(
                    dict.fromkeys(
                        (
                            *bridge_evidence_paths.get(skill_id, ()),
                            *evidence_paths.get(skill_id, ()),
                        )
                    )
                ),
                why=(
                    "Selected from explicit bridge rules, full-text, vector and graph evidence; "
                    "curated bridge evidence outranks isolated vector or graph matches."
                ),
            )
        )
        if remaining_budget <= 0:
            break

    ranked = tuple(sorted(recommendations, key=lambda item: (-item.score, item.skill_name))[:limit])
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


def _record_mapping(record: Mapping[str, object]) -> Mapping[str, object]:
    return dict(record)


class Neo4jHybridRetrievalGraph:
    """Neo4j-backed candidate and evidence fetcher for production retrieval."""

    def __init__(self, driver: Any, settings: skills_config.SkillsKgSettings) -> None:
        self._driver = driver
        self._settings = settings

    def fulltext_skill_ids(self, query_text: str, limit: int) -> tuple[str, ...]:
        """Return skill IDs matched by Neo4j full-text indexes."""

        with self._driver.session(database=self._settings.neo4j.database) as session:
            records = session.run(
                (
                    "CALL db.index.fulltext.queryNodes($chunk_index, $query_text, {limit: $limit}) "
                    "YIELD node, score "
                    "RETURN node.skill_id AS skill_id "
                    "UNION "
                    "CALL db.index.fulltext.queryNodes($metadata_index, $query_text, {limit: $limit}) "
                    "YIELD node, score "
                    "RETURN node.id AS skill_id"
                ),
                chunk_index=self._settings.neo4j.retrieval_unit_fulltext_index,
                metadata_index=self._settings.neo4j.metadata_fulltext_index,
                query_text=query_text,
                limit=limit,
            )
            skill_ids = [
                str(record["skill_id"])
                for record in records
                if isinstance(_record_mapping(record).get("skill_id"), str)
            ]
        return tuple(dict.fromkeys(skill_ids))

    def vector_candidates(
        self,
        query_text: str,
        embedder: embed_skill_chunks.EmbeddingProvider,
        limit: int,
    ) -> tuple[VectorCandidate, ...]:
        """Return vector candidates from Neo4j's named vector index."""

        embedding = embedder.embed(query_text)
        with self._driver.session(database=self._settings.neo4j.database) as session:
            records = session.run(
                (
                    "CALL db.index.vector.queryNodes($index_name, $limit, $embedding) "
                    "YIELD node, score "
                    "RETURN node.id AS retrieval_unit_id, score, node.source_path AS source_path, "
                    "node.section_id AS section_id, node.skill_id AS skill_id, "
                    "node.text AS text, node.embeddingProvider AS embedding_provider, "
                    "node.embeddingDimensions AS embedding_dimensions"
                ),
                index_name=self._settings.neo4j.vector_index,
                limit=limit,
                embedding=list(embedding),
            )
            return embed_skill_chunks.vector_candidates_from_records(records)

    def fetch_retrieval_plan(self, skill_ids: Sequence[str]) -> load_skills_neo4j.LoadPlan:
        """Fetch a bounded candidate subgraph for ranking and evidence formatting."""

        unique_skill_ids = tuple(dict.fromkeys(skill_ids))
        if not unique_skill_ids:
            return load_skills_neo4j.LoadPlan(nodes=(), relationships=())
        with self._driver.session(database=self._settings.neo4j.database) as session:
            skill_records = tuple(
                _record_mapping(record)
                for record in session.run(
                    (
                        "MATCH (s:Skill) "
                        "WHERE s.id IN $skill_ids "
                        "RETURN s.id AS id, properties(s) AS properties"
                    ),
                    skill_ids=list(unique_skill_ids),
                )
            )
            chunk_records = tuple(
                _record_mapping(record)
                for record in session.run(
                    (
                        "MATCH (s:Skill)-[:HAS_SECTION]->(:SkillSection)-[:HAS_RETRIEVAL_UNIT]->"
                        "(unit:RetrievalUnit) "
                        "WHERE s.id IN $skill_ids "
                        "RETURN unit.id AS id, properties(unit) AS properties"
                    ),
                    skill_ids=list(unique_skill_ids),
                )
            )
            relationship_records = tuple(
                _record_mapping(record)
                for record in session.run(
                    (
                        "MATCH (source:Skill)-[r]->(target) "
                        "WHERE source.id IN $skill_ids AND type(r) IN $relationship_types "
                        "RETURN type(r) AS type, labels(source)[0] AS source_label, "
                        "source.id AS source_id, labels(target)[0] AS target_label, "
                        "target.id AS target_id, properties(r) AS properties"
                    ),
                    skill_ids=list(unique_skill_ids),
                    relationship_types=sorted(CONNECTED_RELATIONSHIP_TYPES),
                )
            )
        nodes = [
            load_skills_neo4j.GraphNode("Skill", str(record["id"]), _properties(record))
            for record in skill_records
        ]
        nodes.extend(
            load_skills_neo4j.GraphNode("RetrievalUnit", str(record["id"]), _properties(record))
            for record in chunk_records
        )
        relationships = [
            load_skills_neo4j.GraphRelationship(
                type=str(record["type"]),
                source_label=str(record["source_label"]),
                source_id=str(record["source_id"]),
                target_label=str(record["target_label"]),
                target_id=str(record["target_id"]),
                properties=_properties(record),
            )
            for record in relationship_records
            if isinstance(record.get("target_id"), str)
        ]
        return load_skills_neo4j.LoadPlan(nodes=tuple(nodes), relationships=tuple(relationships))


def _properties(record: Mapping[str, object]) -> Mapping[str, object]:
    value = record.get("properties")
    return dict(value) if isinstance(value, dict) else {}


def retrieve_hybrid_skills_from_neo4j(
    driver: Any,
    settings: skills_config.SkillsKgSettings,
    query_text: str,
    embedder: embed_skill_chunks.EmbeddingProvider | None = None,
    limit: int = 5,
    max_depth: int = 2,
    token_budget: int = DEFAULT_TOKEN_BUDGET,
) -> HybridRetrievalResult:
    """Run production retrieval from live Neo4j full-text, vector and graph evidence."""

    bounded_limit = max(1, min(limit, settings.retrieval.max_limit))
    runtime_embedder = embedder or embed_skill_chunks.DeterministicEmbeddingProvider(
        dimension=settings.neo4j.embedding_dimensions
    )
    graph = Neo4jHybridRetrievalGraph(driver, settings)
    vector_candidates = graph.vector_candidates(query_text, runtime_embedder, bounded_limit)
    candidate_skill_ids = tuple(
        dict.fromkeys(
            (
                *graph.fulltext_skill_ids(query_text, bounded_limit),
                *(candidate.skill_id for candidate in vector_candidates),
            )
        )
    )
    plan = graph.fetch_retrieval_plan(candidate_skill_ids)
    return retrieve_hybrid_skills(
        plan,
        query_text,
        vector_candidates=vector_candidates,
        limit=bounded_limit,
        max_depth=max_depth,
        token_budget=token_budget,
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
            "RetrievalUnit",
            "retrieval:skill:kg-enabled-rag:section:0:kg-when",
            {
                "id": "retrieval:skill:kg-enabled-rag:section:0:kg-when",
                "skill_id": "skill:kg-enabled-rag",
                "text": "Use this skill when building graph-grounded retrieval with provenance.",
                "source_path": "skills/data-architecture/kg-enabled-rag/SKILL.md",
                "section_id": "skill:kg-enabled-rag:section:0-when-to-use",
            },
        ),
        load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:kg-enabled-rag:section:1:kg",
            {
                "id": "retrieval:skill:kg-enabled-rag:section:1:kg",
                "skill_id": "skill:kg-enabled-rag",
                "text": "Use KG-enabled RAG for graph-grounded retrieval.",
                "source_path": "skills/data-architecture/kg-enabled-rag/SKILL.md",
                "section_id": "skill:kg-enabled-rag:section:0-objective",
            },
        ),
        load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:kg-enabled-rag:section:2:kg-procedure",
            {
                "id": "retrieval:skill:kg-enabled-rag:section:2:kg-procedure",
                "skill_id": "skill:kg-enabled-rag",
                "text": "1. Inspect graph and retrieval code. 2. Add tests. 3. Return evidence.",
                "source_path": "skills/data-architecture/kg-enabled-rag/SKILL.md",
                "section_id": "skill:kg-enabled-rag:section:0-procedure",
            },
        ),
        load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:kg-enabled-rag:section:3:kg-rules",
            {
                "id": "retrieval:skill:kg-enabled-rag:section:3:kg-rules",
                "skill_id": "skill:kg-enabled-rag",
                "text": "Never expose raw Cypher, raw embeddings or answers without evidence.",
                "source_path": "skills/data-architecture/kg-enabled-rag/SKILL.md",
                "section_id": "skill:kg-enabled-rag:section:0-rules",
            },
        ),
        load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:kg-enabled-rag:section:4:kg-verification",
            {
                "id": "retrieval:skill:kg-enabled-rag:section:4:kg-verification",
                "skill_id": "skill:kg-enabled-rag",
                "text": "- [ ] Retrieval returns typed evidence.\n- [ ] Answers cite source paths.",
                "source_path": "skills/data-architecture/kg-enabled-rag/SKILL.md",
                "section_id": "skill:kg-enabled-rag:section:0-verification",
            },
        ),
        load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:knowledge-retrieval-rag:section:0:retrieval",
            {
                "id": "retrieval:skill:knowledge-retrieval-rag:section:0:retrieval",
                "skill_id": "skill:knowledge-retrieval-rag",
                "text": "Use retrieval evidence and source-backed context.",
                "source_path": "skills/agentic-patterns/knowledge-retrieval-rag/SKILL.md",
                "section_id": "skill:knowledge-retrieval-rag:section:0-objective",
            },
        ),
        load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:generic-documentation:section:0:generic",
            {
                "id": "retrieval:skill:generic-documentation:section:0:generic",
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


def main(argv: Sequence[str] | None = None) -> int:  # pragma: no cover
    parser = ArgumentParser(description="Run local hybrid skill retrieval.")
    parser.add_argument("query", help="Task query to retrieve skills for.")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))

    settings = skills_config.load_settings()
    plan = embed_skill_chunks.build_embedded_repository_load_plan(Path("skills"))
    embedder = embed_skill_chunks.DeterministicEmbeddingProvider(
        dimension=settings.neo4j.embedding_dimensions
    )
    vector_candidates = embed_skill_chunks.query_vector_candidates(
        plan, args.query, embedder, args.limit
    )
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
