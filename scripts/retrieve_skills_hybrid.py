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

from scripts import embed_skill_chunks, load_skills_neo4j, skills_config, skills_mcp_perf
from scripts.embed_skill_chunks import VectorCandidate

DEFAULT_RETRIEVAL_SETTINGS = skills_config.load_settings().retrieval
DEFAULT_TOKEN_BUDGET = DEFAULT_RETRIEVAL_SETTINGS.default_token_budget
CONNECTED_RELATIONSHIP_TYPES = frozenset(
    {
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
    evidence_anchors: tuple[dict[str, object], ...]
    evidence_paths: tuple[str, ...]
    why: str


class HybridRetrievalResult(NamedTuple):
    """Retrieval result safe for agent consumption."""

    query: str
    uncertain: bool
    message: str
    recommendations: tuple[SkillRecommendation, ...]
    selection_trace: Mapping[str, object]


GENERIC_DOMAIN_TOKENS = frozenset(
    {
        "agent",
        "agents",
        "and",
        "building",
        "data",
        "for",
        "graph",
        "guide",
        "implement",
        "implementation",
        "irrelevant",
        "knowledge",
        "practice",
        "probe",
        "retrieval",
        "skill",
        "skills",
        "synthetic",
        "the",
        "use",
        "when",
        "with",
    }
)


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9]+", text.lower())
        if len(token) > 2 and token not in {"and", "the", "for", "with"}
    }


def _specific_tokens(text: str) -> set[str]:
    return _tokens(text) - GENERIC_DOMAIN_TOKENS


def _has_specific_evidence(
    *,
    specific_tokens: set[str],
    skill_name: str,
    skill_properties: Mapping[str, object],
    retrieval_texts: tuple[str, ...],
) -> bool:
    if not specific_tokens:
        return True
    metadata_text = " ".join(
        [
            skill_name,
            _string(skill_properties, "description"),
            " ".join(_string_list(skill_properties, "aliases")),
        ]
    )
    metadata_tokens = _tokens(metadata_text)
    if specific_tokens & metadata_tokens:
        return True
    for text in retrieval_texts:
        if specific_tokens & _tokens(text):
            return True
    return False


def _string(properties: Mapping[str, object], key: str) -> str:
    value = properties.get(key)
    return value if isinstance(value, str) else ""


def _bool(properties: Mapping[str, object], key: str) -> bool:
    value = properties.get(key)
    return isinstance(value, bool) and value


def _string_list(properties: Mapping[str, object], key: str) -> tuple[str, ...]:
    value = properties.get(key)
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str) and item.strip())


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


def _policy_exclusion_reason(
    skill: load_skills_neo4j.GraphNode,
    query_tokens: set[str],
) -> str:
    promotion_status = _string(skill.properties, "promotion_status")
    if promotion_status != "promoted":
        status_label = promotion_status or "missing"
        return f"Non-promoted skill filtered from retrieval (promotion_status={status_label})."
    if _bool(skill.properties, "deprecated"):
        return "Deprecated skill filtered from automatic selection."
    superseded_by = _string(skill.properties, "superseded_by")
    if superseded_by:
        return f"Superseded skill filtered in favour of '{superseded_by}'."
    excluded_terms = {
        token
        for value in _string_list(skill.properties, "excluded_when")
        for token in _tokens(value)
    }
    if excluded_terms and query_tokens & excluded_terms:
        return "Excluded by skill runtime conditions matching the current query."
    forbidden_task_terms = {
        token
        for value in _string_list(skill.properties, "not_for_task_shapes")
        for token in _tokens(value)
    }
    if forbidden_task_terms and query_tokens & forbidden_task_terms:
        return "Rejected because the query matches a forbidden task shape for this skill."
    return ""


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


def _metadata_scores(
    plan: load_skills_neo4j.LoadPlan,
    query_text: str,
) -> dict[str, float]:
    query_tokens = _tokens(query_text)
    if not query_tokens:
        return {}
    normalised_query = " ".join(sorted(query_tokens))
    scores: dict[str, float] = {}
    for skill_id, skill in _skill_nodes(plan).items():
        name = _string(skill.properties, "name")
        aliases = _string_list(skill.properties, "aliases")
        description = _string(skill.properties, "description")
        metadata_tokens = _tokens(" ".join((name, *aliases, description)))
        if not metadata_tokens:
            continue
        overlap_score = len(query_tokens & metadata_tokens) / len(query_tokens)
        exact_candidates = {
            " ".join(sorted(_tokens(name))),
            *(" ".join(sorted(_tokens(alias))) for alias in aliases),
        }
        exact_bonus = 0.35 if normalised_query in exact_candidates else 0.0
        scores[skill_id] = min(1.0, overlap_score + exact_bonus)
    return scores


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
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[dict[str, object], ...]]:
    snippets: list[str] = []
    source_paths: list[str] = []
    section_ids: list[str] = []
    evidence_anchors: list[dict[str, object]] = []
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
        evidence_anchors.append(
            {
                "retrieval_unit_id": unit.id,
                "source_path": _string(unit.properties, "source_path"),
                "heading_path": _string(unit.properties, "heading_path"),
                "section_id": _string(unit.properties, "section_id"),
                "line_start": unit.properties.get("line_start", 0),
                "line_end": unit.properties.get("line_end", 0),
            }
        )
        remaining -= cost
    return (
        tuple(snippets[:3]),
        tuple(sorted(set(source_paths))),
        tuple(sorted(set(section_ids))),
        tuple(evidence_anchors[:3]),
    )


def retrieve_hybrid_skills(
    plan: load_skills_neo4j.LoadPlan,
    query_text: str,
    vector_candidates: Sequence[VectorCandidate] = (),
    limit: int = 5,
    max_depth: int = 2,
    token_budget: int = DEFAULT_TOKEN_BUDGET,
    retrieval_settings: skills_config.RetrievalSettings | None = None,
) -> HybridRetrievalResult:
    """Rank skills using text, vector and graph evidence."""

    settings = retrieval_settings or skills_config.load_settings().retrieval
    limit = max(1, min(limit, settings.max_limit))
    max_depth = max(0, min(max_depth, settings.max_depth))
    query_tokens = _tokens(query_text)
    specific_query_tokens = _specific_tokens(query_text)
    skills = _skill_nodes(plan)
    text_scores, text_unit_ids = _text_scores(plan, query_text)
    metadata_scores = _metadata_scores(plan, query_text)
    vector_scores = _vector_scores(vector_candidates, settings.min_vector_candidate_score)
    vector_unit_ids = _vector_retrieval_unit_ids(
        vector_candidates, settings.min_vector_candidate_score
    )
    bridge_scores, bridge_evidence_paths = _bridge_scores(plan, query_text)
    candidate_skill_ids = (
        set(text_scores) | set(metadata_scores) | set(vector_scores) | set(bridge_scores)
    )
    graph_scores, evidence_paths = _graph_evidence(plan, candidate_skill_ids, max_depth)
    recommendation_inputs: list[tuple[str, float, float, float, float, tuple[str, ...]]] = []

    for skill_id in candidate_skill_ids:
        skill = skills.get(skill_id)
        if skill is None:
            continue
        full_text_score = text_scores.get(skill_id, 0.0)
        metadata_score = metadata_scores.get(skill_id, 0.0)
        vector_score = max(0.0, vector_scores.get(skill_id, 0.0))
        graph_score = max(graph_scores.get(skill_id, 0.0), bridge_scores.get(skill_id, 0.0))
        score = (
            (0.45 * full_text_score)
            + (0.40 * metadata_score)
            + (0.10 * vector_score)
            + (0.15 * graph_scores.get(skill_id, 0.0))
            + (0.60 * bridge_scores.get(skill_id, 0.0))
        )
        preferred_unit_ids = tuple(
            dict.fromkeys((*text_unit_ids.get(skill_id, ()), *vector_unit_ids.get(skill_id, ())))
        )
        recommendation_inputs.append(
            (skill_id, score, graph_score, vector_score, full_text_score, preferred_unit_ids)
        )

    recommendations: list[SkillRecommendation] = []
    rejected_candidates: list[dict[str, object]] = []
    remaining_budget = token_budget
    for skill_id, score, graph_score, vector_score, full_text_score, preferred_unit_ids in sorted(
        recommendation_inputs,
        key=lambda item: (-item[1], _string(skills[item[0]].properties, "name")),
    ):
        skill = skills[skill_id]
        exclusion_reason = _policy_exclusion_reason(skill, query_tokens)
        if exclusion_reason:
            rejected_candidates.append(
                {
                    "skill_id": skill_id,
                    "skill_name": _string(skill.properties, "name"),
                    "score": round(score, 6),
                    "reason": exclusion_reason,
                }
            )
            continue
        snippets, source_paths, section_ids, evidence_anchors = _retrieval_unit_evidence(
            plan,
            skill_id,
            preferred_unit_ids,
            remaining_budget,
        )
        if not snippets:
            rejected_candidates.append(
                {
                    "skill_id": skill_id,
                    "skill_name": _string(skill.properties, "name"),
                    "score": round(score, 6),
                    "reason": "No bounded evidence snippets were available for this candidate.",
                }
            )
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
                evidence_anchors=evidence_anchors,
                evidence_paths=tuple(
                    dict.fromkeys(
                        (
                            *bridge_evidence_paths.get(skill_id, ()),
                            *evidence_paths.get(skill_id, ()),
                        )
                    )
                ),
                why=(
                    "Selected from explicit bridge assertions, skill metadata, full-text, "
                    "vector and graph evidence; repository-native evidence outranks isolated "
                    "vector or graph matches."
                ),
            )
        )
        if remaining_budget <= 0:
            break

    ranked = tuple(sorted(recommendations, key=lambda item: (-item.score, item.skill_name))[:limit])
    selected_trace: dict[str, object] = {}
    if ranked:
        selected = ranked[0]
        selected_trace = {
            "skill_id": selected.skill_id,
            "skill_name": selected.skill_name,
            "score": selected.score,
            "selection_reason": selected.why,
            "source_paths": list(selected.source_paths),
            "section_ids": list(selected.section_ids),
            "evidence_anchors": list(selected.evidence_anchors),
            "evidence_paths": list(selected.evidence_paths),
        }
        for rejected in ranked[1:]:
            rejected_candidates.append(
                {
                    "skill_id": rejected.skill_id,
                    "skill_name": rejected.skill_name,
                    "score": rejected.score,
                    "reason": "Lower-ranked than the selected skill after hybrid scoring.",
                }
            )
    selection_trace = {
        "request": {"query": query_text},
        "selected": selected_trace,
        "rejected": tuple(rejected_candidates),
    }
    min_confident_score = settings.min_confident_score
    min_top1_margin = settings.min_top1_margin
    if not ranked or ranked[0].score < min_confident_score:
        selection_trace = {
            "request": {"query": query_text},
            "selected": {},
            "rejected": tuple(rejected_candidates),
        }
        return HybridRetrievalResult(
            query=query_text,
            uncertain=True,
            message="No confident skill match found; provide a narrower task description.",
            recommendations=(),
            selection_trace=selection_trace,
        )
    if (
        len(ranked) >= 2
        and min_top1_margin > 0.0
        and (ranked[0].score - ranked[1].score) < min_top1_margin
    ):
        selection_trace = {
            "request": {"query": query_text},
            "selected": {},
            "rejected": tuple(
                [
                    *rejected_candidates,
                    {
                        "skill_id": ranked[0].skill_id,
                        "skill_name": ranked[0].skill_name,
                        "score": ranked[0].score,
                        "reason": (
                            f"Top hybrid candidates are too close (margin < {min_top1_margin:.3f})."
                        ),
                    },
                ]
            ),
        }
        return HybridRetrievalResult(
            query=query_text,
            uncertain=True,
            message="Ambiguous skill match; provide a narrower task description.",
            recommendations=(),
            selection_trace=selection_trace,
        )
    top = ranked[0]
    top_skill = skills.get(top.skill_id)
    if (
        specific_query_tokens
        and top_skill is not None
        and top.vector_score <= 0.0
        and not _has_specific_evidence(
            specific_tokens=specific_query_tokens,
            skill_name=top.skill_name,
            skill_properties=top_skill.properties,
            retrieval_texts=top.evidence_snippets,
        )
    ):
        selection_trace = {
            "request": {"query": query_text},
            "selected": {},
            "rejected": tuple(
                [
                    *rejected_candidates,
                    {
                        "skill_id": top.skill_id,
                        "skill_name": top.skill_name,
                        "score": top.score,
                        "reason": "Query lacked task-specific token overlap with top evidence.",
                    },
                ]
            ),
        }
        return HybridRetrievalResult(
            query=query_text,
            uncertain=True,
            message="No task-specific evidence match found; provide a narrower task description.",
            recommendations=(),
            selection_trace=selection_trace,
        )
    return HybridRetrievalResult(
        query=query_text,
        uncertain=False,
        message="Hybrid retrieval returned connected, source-backed skill evidence.",
        recommendations=ranked,
        selection_trace=selection_trace,
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

        with skills_mcp_perf.database_io() as io:
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
            io.add_payload(skill_ids)
        return tuple(dict.fromkeys(skill_ids))

    def vector_candidates(
        self,
        query_text: str,
        embedder: embed_skill_chunks.EmbeddingProvider,
        limit: int,
    ) -> tuple[VectorCandidate, ...]:
        """Return vector candidates from Neo4j's named vector index."""

        embedding = embedder.embed(query_text)
        with skills_mcp_perf.database_io() as io:
            with self._driver.session(database=self._settings.neo4j.database) as session:
                records = list(
                    session.run(
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
                )
            candidates = embed_skill_chunks.vector_candidates_from_records(records)
            io.add_payload(
                [
                    {
                        "retrieval_unit_id": candidate.retrieval_unit_id,
                        "skill_id": candidate.skill_id,
                        "text": candidate.text,
                        "score": candidate.score,
                    }
                    for candidate in candidates
                ]
            )
        return candidates

    def fetch_retrieval_plan(self, skill_ids: Sequence[str]) -> load_skills_neo4j.LoadPlan:
        """Fetch a bounded candidate subgraph for ranking and evidence formatting."""

        unique_skill_ids = tuple(dict.fromkeys(skill_ids))
        if not unique_skill_ids:
            return load_skills_neo4j.LoadPlan(nodes=(), relationships=())
        with skills_mcp_perf.database_io() as io:
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
            io.add_payload({"skills": list(unique_skill_ids), "nodes": len(nodes)})
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
    runtime_embedder = embedder or embed_skill_chunks.resolve_embedding_provider(settings)
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
            "skill:knowledge-graph-rag",
            {
                "id": "skill:knowledge-graph-rag",
                "name": "knowledge-graph-rag",
                "aliases": ["kg-enabled-rag", "graph-rag"],
                "promotion_status": "promoted",
            },
        ),
        load_skills_neo4j.GraphNode(
            "Skill",
            "skill:knowledge-retrieval-rag",
            {
                "id": "skill:knowledge-retrieval-rag",
                "name": "knowledge-retrieval-rag",
                "aliases": ["rag", "retrieval-augmented-generation"],
                "promotion_status": "promoted",
            },
        ),
        load_skills_neo4j.GraphNode(
            "Skill",
            "skill:generic-documentation",
            {
                "id": "skill:generic-documentation",
                "name": "generic-documentation",
                "promotion_status": "promoted",
            },
        ),
        load_skills_neo4j.GraphNode(
            "Skill",
            "skill:tdd-practice",
            {
                "id": "skill:tdd-practice",
                "name": "tdd-practice",
                "aliases": ["test-driven-development", "tdd"],
                "promotion_status": "promoted",
            },
        ),
        load_skills_neo4j.GraphNode(
            "Skill",
            "skill:reflection-and-verification",
            {
                "id": "skill:reflection-and-verification",
                "name": "reflection-and-verification",
                "promotion_status": "promoted",
            },
        ),
        load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:knowledge-graph-rag:section:0:kg-when",
            {
                "id": "retrieval:skill:knowledge-graph-rag:section:0:kg-when",
                "skill_id": "skill:knowledge-graph-rag",
                "text": "Use this skill when building graph-grounded retrieval with provenance.",
                "source_path": "skills/knowledge-graph-rag/SKILL.md",
                "heading_path": "When to use",
                "section_id": "skill:knowledge-graph-rag:section:0-when-to-use",
                "line_start": 8,
                "line_end": 9,
            },
        ),
        load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:knowledge-graph-rag:section:1:kg",
            {
                "id": "retrieval:skill:knowledge-graph-rag:section:1:kg",
                "skill_id": "skill:knowledge-graph-rag",
                "text": "Use KG-enabled RAG for graph-grounded retrieval.",
                "source_path": "skills/knowledge-graph-rag/SKILL.md",
                "heading_path": "Objective",
                "section_id": "skill:knowledge-graph-rag:section:0-objective",
                "line_start": 12,
                "line_end": 12,
            },
        ),
        load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:knowledge-graph-rag:section:2:kg-procedure",
            {
                "id": "retrieval:skill:knowledge-graph-rag:section:2:kg-procedure",
                "skill_id": "skill:knowledge-graph-rag",
                "text": "1. Inspect graph and retrieval code. 2. Add tests. 3. Return evidence.",
                "source_path": "skills/knowledge-graph-rag/SKILL.md",
                "heading_path": "Procedure",
                "section_id": "skill:knowledge-graph-rag:section:0-procedure",
                "line_start": 16,
                "line_end": 17,
            },
        ),
        load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:knowledge-graph-rag:section:3:kg-rules",
            {
                "id": "retrieval:skill:knowledge-graph-rag:section:3:kg-rules",
                "skill_id": "skill:knowledge-graph-rag",
                "text": "Never expose raw Cypher, raw embeddings or answers without evidence.",
                "source_path": "skills/knowledge-graph-rag/SKILL.md",
                "heading_path": "Rules",
                "section_id": "skill:knowledge-graph-rag:section:0-rules",
                "line_start": 20,
                "line_end": 20,
            },
        ),
        load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:knowledge-graph-rag:section:4:kg-verification",
            {
                "id": "retrieval:skill:knowledge-graph-rag:section:4:kg-verification",
                "skill_id": "skill:knowledge-graph-rag",
                "text": "- [ ] Retrieval returns typed evidence.\n- [ ] Answers cite source paths.",
                "source_path": "skills/knowledge-graph-rag/SKILL.md",
                "heading_path": "Verification",
                "section_id": "skill:knowledge-graph-rag:section:0-verification",
                "line_start": 24,
                "line_end": 25,
            },
        ),
        load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:knowledge-retrieval-rag:section:0:retrieval",
            {
                "id": "retrieval:skill:knowledge-retrieval-rag:section:0:retrieval",
                "skill_id": "skill:knowledge-retrieval-rag",
                "text": "Use retrieval evidence and source-backed context.",
                "source_path": "skills/knowledge-retrieval-rag/SKILL.md",
                "heading_path": "Objective",
                "section_id": "skill:knowledge-retrieval-rag:section:0-objective",
                "line_start": 12,
                "line_end": 12,
            },
        ),
        load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:generic-documentation:section:0:generic",
            {
                "id": "retrieval:skill:generic-documentation:section:0:generic",
                "skill_id": "skill:generic-documentation",
                "text": "General documentation guidance.",
                "source_path": "skills/generic-documentation/SKILL.md",
                "heading_path": "Objective",
                "section_id": "skill:generic-documentation:section:0-objective",
                "line_start": 12,
                "line_end": 12,
            },
        ),
        load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:tdd-practice:section:0:tdd-when",
            {
                "id": "retrieval:skill:tdd-practice:section:0:tdd-when",
                "skill_id": "skill:tdd-practice",
                "text": (
                    "Use this skill when adding behaviour, fixing a defect, refactoring risky code, "
                    "or improving code where expected behaviour can be specified with executable tests."
                ),
                "source_path": "skills/tdd-practice/SKILL.md",
                "heading_path": "When to use",
                "section_id": "skill:tdd-practice:section:0-when-to-use",
                "line_start": 11,
                "line_end": 13,
            },
        ),
        load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:tdd-practice:section:1:tdd-procedure",
            {
                "id": "retrieval:skill:tdd-practice:section:1:tdd-procedure",
                "skill_id": "skill:tdd-practice",
                "text": (
                    "Write the smallest failing test that proves the behaviour is missing or broken. "
                    "Implement the smallest production change that makes the test pass."
                ),
                "source_path": "skills/tdd-practice/SKILL.md",
                "heading_path": "Procedure",
                "section_id": "skill:tdd-practice:section:0-procedure",
                "line_start": 21,
                "line_end": 24,
            },
        ),
        load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:tdd-practice:section:2:tdd-verification",
            {
                "id": "retrieval:skill:tdd-practice:section:2:tdd-verification",
                "skill_id": "skill:tdd-practice",
                "text": "- [ ] Failing test added before production change.\n- [ ] Production change made and targeted tests pass.",
                "source_path": "skills/tdd-practice/SKILL.md",
                "heading_path": "Verification",
                "section_id": "skill:tdd-practice:section:0-verification",
                "line_start": 55,
                "line_end": 56,
            },
        ),
        load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:reflection-and-verification:section:0:reflection-when",
            {
                "id": "retrieval:skill:reflection-and-verification:section:0:reflection-when",
                "skill_id": "skill:reflection-and-verification",
                "text": (
                    "Use this skill after an initial implementation, plan or generated artefact exists "
                    "and quality matters."
                ),
                "source_path": "skills/reflection-and-verification/SKILL.md",
                "heading_path": "When to use",
                "section_id": "skill:reflection-and-verification:section:0-when-to-use",
                "line_start": 8,
                "line_end": 10,
            },
        ),
        load_skills_neo4j.GraphNode(
            "RetrievalUnit",
            "retrieval:skill:reflection-and-verification:section:1:reflection-procedure",
            {
                "id": "retrieval:skill:reflection-and-verification:section:1:reflection-procedure",
                "skill_id": "skill:reflection-and-verification",
                "text": (
                    "Evaluate the artefact against explicit criteria and apply targeted fixes after "
                    "deterministic checks fail."
                ),
                "source_path": "skills/reflection-and-verification/SKILL.md",
                "heading_path": "Procedure",
                "section_id": "skill:reflection-and-verification:section:0-procedure",
                "line_start": 18,
                "line_end": 25,
            },
        ),
    )
    relationships = (
        load_skills_neo4j.GraphRelationship(
            "COMPLEMENTS",
            "Skill",
            "skill:knowledge-graph-rag",
            "Skill",
            "skill:knowledge-retrieval-rag",
            {"mapping_rule_id": "test-rule"},
        ),
        load_skills_neo4j.GraphRelationship(
            "HAS_WORKFLOW_STAGE",
            "Skill",
            "skill:knowledge-graph-rag",
            "WorkflowStage",
            "retrieval",
            {},
        ),
        load_skills_neo4j.GraphRelationship(
            "HAS_CAPABILITY",
            "Skill",
            "skill:knowledge-graph-rag",
            "Capability",
            "graph-rag",
            {},
        ),
        load_skills_neo4j.GraphRelationship(
            "HAS_TASK_SHAPE",
            "Skill",
            "skill:knowledge-graph-rag",
            "TaskShape",
            "ontology-retrieval",
            {},
        ),
        load_skills_neo4j.GraphRelationship(
            "VALIDATES",
            "Skill",
            "skill:reflection-and-verification",
            "Skill",
            "skill:tdd-practice",
            {"mapping_rule_id": "test-rule"},
        ),
    )
    return load_skills_neo4j.LoadPlan(nodes=nodes, relationships=relationships)


def main(argv: Sequence[str] | None = None) -> int:  # pragma: no cover
    parser = ArgumentParser(description="Run local hybrid skill retrieval.")
    parser.add_argument("query", help="Task query to retrieve skills for.")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))

    settings = skills_config.load_settings()
    embedder = embed_skill_chunks.resolve_embedding_provider(settings)
    plan = embed_skill_chunks.build_embedded_repository_load_plan(
        Path("skills"),
        embedder=embedder,
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
