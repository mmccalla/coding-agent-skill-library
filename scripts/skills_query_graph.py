#!/usr/bin/env python3
"""Bounded graph query-family planning and safe read-only execution."""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import NamedTuple

from scripts import load_skills_neo4j, skills_router

QUERY_INTENT_SKILL_LOOKUP = "skill_lookup"
QUERY_INTENT_SKILL_PACK_DISCOVERY = "skill_pack_discovery"
QUERY_INTENT_ALIAS_RESOLUTION = "alias_resolution"
QUERY_INTENT_RELATIONSHIP_TRAVERSAL = "relationship_traversal"
QUERY_INTENT_EXECUTION_CONTEXT = "execution_context"
QUERY_INTENT_GOVERNANCE_VALIDATION_LOOKUP = "governance_validation_lookup"
QUERY_INTENT_MULTI_SKILL_SYNTHESIS = "multi_skill_synthesis"
QUERY_INTENT_MISSING_EVIDENCE_ABSTENTION = "missing_evidence_abstention"

QUERY_FAMILY_EXACT_SKILL_LOOKUP = "exact_skill_lookup"
QUERY_FAMILY_RELATED_SKILL_TRAVERSAL = "related_skill_traversal"
QUERY_FAMILY_CAPABILITY_TASK_LOOKUP = "capability_task_lookup"
QUERY_FAMILY_CONSTRAINT_VERIFICATION_RETRIEVAL = "constraint_verification_retrieval"
QUERY_FAMILY_PACK_SKILL_MEMBERSHIP_LOOKUP = "pack_skill_membership_lookup"
QUERY_FAMILY_EVIDENCE_FRAGMENT_RETRIEVAL = "evidence_fragment_retrieval"

APPROVED_QUERY_FAMILIES = frozenset(
    {
        QUERY_FAMILY_EXACT_SKILL_LOOKUP,
        QUERY_FAMILY_RELATED_SKILL_TRAVERSAL,
        QUERY_FAMILY_CAPABILITY_TASK_LOOKUP,
        QUERY_FAMILY_CONSTRAINT_VERIFICATION_RETRIEVAL,
        QUERY_FAMILY_PACK_SKILL_MEMBERSHIP_LOOKUP,
        QUERY_FAMILY_EVIDENCE_FRAGMENT_RETRIEVAL,
    }
)
ALLOWED_RELATIONSHIP_TYPES = frozenset(
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
        "BELONGS_TO_CATEGORY",
        "CONTAINS_SKILL",
        "HAS_SECTION",
        "HAS_RETRIEVAL_UNIT",
        "DERIVED_FROM",
    }
)
TOKEN_RE = re.compile(r"[a-z0-9]+")
PACK_TERMS = frozenset({"pack", "library", "catalog", "catalogue"})
RELATIONSHIP_TERMS = frozenset(
    {"related", "relationship", "relationships", "dependency", "dependencies", "connected"}
)
CONSTRAINT_TERMS = frozenset(
    {"verification", "verify", "constraints", "constraint", "rules", "guardrails", "checklist"}
)
EVIDENCE_TERMS = frozenset({"evidence", "citation", "citations", "source", "sources", "proof"})

QUERY_TEMPLATES = {
    QUERY_FAMILY_EXACT_SKILL_LOOKUP: {
        "cypher_template_id": "skill_lookup_v1",
        "read_only": True,
        "labels": ("Skill", "SkillSection", "RetrievalUnit"),
        "relationship_types": ("HAS_SECTION", "HAS_RETRIEVAL_UNIT"),
        "max_depth": 2,
    },
    QUERY_FAMILY_RELATED_SKILL_TRAVERSAL: {
        "cypher_template_id": "related_skill_traversal_v1",
        "read_only": True,
        "labels": ("Skill",),
        "relationship_types": (
            "RELATED_TO",
            "PRECEDES",
            "REQUIRES",
            "COMPLEMENTS",
            "REFINES",
            "GOVERNS",
            "VALIDATES",
        ),
        "max_depth": 1,
    },
    QUERY_FAMILY_CAPABILITY_TASK_LOOKUP: {
        "cypher_template_id": "capability_task_lookup_v1",
        "read_only": True,
        "labels": ("Skill", "Capability", "TaskShape"),
        "relationship_types": ("HAS_CAPABILITY", "HAS_TASK_SHAPE"),
        "max_depth": 1,
    },
    QUERY_FAMILY_CONSTRAINT_VERIFICATION_RETRIEVAL: {
        "cypher_template_id": "constraint_verification_lookup_v1",
        "read_only": True,
        "labels": ("Skill", "SkillSection", "RetrievalUnit"),
        "relationship_types": ("HAS_SECTION", "HAS_RETRIEVAL_UNIT"),
        "max_depth": 2,
    },
    QUERY_FAMILY_PACK_SKILL_MEMBERSHIP_LOOKUP: {
        "cypher_template_id": "pack_membership_lookup_v1",
        "read_only": True,
        "labels": ("SkillPack", "Skill"),
        "relationship_types": ("CONTAINS_SKILL",),
        "max_depth": 1,
    },
    QUERY_FAMILY_EVIDENCE_FRAGMENT_RETRIEVAL: {
        "cypher_template_id": "evidence_fragment_lookup_v1",
        "read_only": True,
        "labels": ("Skill", "SkillSection", "RetrievalUnit"),
        "relationship_types": ("HAS_SECTION", "HAS_RETRIEVAL_UNIT"),
        "max_depth": 2,
    },
}

QUERY_FAMILY_RENDERED_CYPHER = {
    QUERY_FAMILY_EXACT_SKILL_LOOKUP: (
        "MATCH (s:Skill {id: $skill_id})-[:HAS_SECTION]->(section:SkillSection)"
        "-[:HAS_RETRIEVAL_UNIT]->(unit:RetrievalUnit) "
        "RETURN s.id AS skill_id, s.name AS skill_name, section.id AS section_id, "
        "unit.id AS retrieval_unit_id, unit.source_path AS source_path "
        "LIMIT $limit"
    ),
    QUERY_FAMILY_RELATED_SKILL_TRAVERSAL: (
        "MATCH (s:Skill {id: $skill_id})-[r:RELATED_TO|PRECEDES|REQUIRES|COMPLEMENTS|REFINES|GOVERNS|VALIDATES]"
        "-(related:Skill) "
        "RETURN s.id AS skill_id, type(r) AS relationship_type, related.id AS related_skill_id "
        "LIMIT $limit"
    ),
    QUERY_FAMILY_CAPABILITY_TASK_LOOKUP: (
        "MATCH (s:Skill)-[r:HAS_CAPABILITY|HAS_TASK_SHAPE]->(concept) "
        "WHERE any(token IN $query_tokens WHERE toLower(coalesce(concept.id, '')) CONTAINS token) "
        "RETURN s.id AS skill_id, s.name AS skill_name, type(r) AS relationship_type, "
        "concept.id AS concept_id "
        "LIMIT $limit"
    ),
    QUERY_FAMILY_CONSTRAINT_VERIFICATION_RETRIEVAL: (
        "MATCH (s:Skill {id: $skill_id})-[:HAS_SECTION]->(section:SkillSection)"
        "-[:HAS_RETRIEVAL_UNIT]->(unit:RetrievalUnit) "
        "WHERE toLower(unit.section_id) CONTAINS 'verification' "
        "   OR toLower(unit.section_id) CONTAINS 'rules' "
        "   OR toLower(unit.section_id) CONTAINS 'guardrails' "
        "   OR toLower(unit.section_id) CONTAINS 'constraint' "
        "RETURN unit.id AS retrieval_unit_id, unit.source_path AS source_path, unit.section_id AS section_id "
        "LIMIT $limit"
    ),
    QUERY_FAMILY_PACK_SKILL_MEMBERSHIP_LOOKUP: (
        "MATCH (pack:SkillPack)-[:CONTAINS_SKILL]->(skill:Skill) "
        "WHERE any(token IN $query_tokens WHERE toLower(pack.id) CONTAINS token OR toLower(pack.name) CONTAINS token) "
        "RETURN pack.id AS skill_pack_id, skill.id AS skill_id, skill.name AS skill_name "
        "LIMIT $limit"
    ),
    QUERY_FAMILY_EVIDENCE_FRAGMENT_RETRIEVAL: (
        "MATCH (s:Skill {id: $skill_id})-[:HAS_SECTION]->(section:SkillSection)"
        "-[:HAS_RETRIEVAL_UNIT]->(unit:RetrievalUnit) "
        "RETURN unit.id AS retrieval_unit_id, unit.source_path AS source_path, unit.section_id AS section_id "
        "LIMIT $limit"
    ),
}


class GraphQueryPlan(NamedTuple):
    intent: str
    strategy: str
    query_family: str
    rationale: str
    parameters: Mapping[str, object]
    result_bounds: Mapping[str, int]
    cypher_template_id: str
    generated_cypher: str


def _tokens(text: str) -> set[str]:
    return {token for token in TOKEN_RE.findall(text.lower()) if len(token) > 2}


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


def _skill_nodes(plan: load_skills_neo4j.LoadPlan) -> tuple[load_skills_neo4j.GraphNode, ...]:
    return tuple(node for node in plan.nodes if node.label == "Skill")


def _retrieval_units_for_skill(
    plan: load_skills_neo4j.LoadPlan, skill_id: str
) -> tuple[load_skills_neo4j.GraphNode, ...]:
    return tuple(
        node
        for node in plan.nodes
        if node.label == "RetrievalUnit" and _string(node.properties.get("skill_id")) == skill_id
    )


def _resolve_skill_id(plan: load_skills_neo4j.LoadPlan, query: str) -> str:
    resolved = skills_router.resolve_skill(plan, query)
    if resolved.get("status") == "ok":
        return _string(resolved.get("skill_id"))
    return ""


def plan_graph_query(
    plan: load_skills_neo4j.LoadPlan,
    query: str,
    *,
    route: str = "",
    resolved_skill_id: str = "",
    limit: int = 5,
) -> Mapping[str, object]:
    """Map a natural-language query to an approved query family and safe parameters."""

    clean_query = query.strip()
    query_tokens = _tokens(clean_query)
    bounded_limit = max(1, min(limit, 10))
    skill_id = resolved_skill_id or _resolve_skill_id(plan, clean_query)

    if skill_id and query_tokens & EVIDENCE_TERMS:
        plan_result = GraphQueryPlan(
            intent=QUERY_INTENT_EXECUTION_CONTEXT,
            strategy="graph-first",
            query_family=QUERY_FAMILY_EVIDENCE_FRAGMENT_RETRIEVAL,
            rationale="Known skill plus evidence wording requires bounded evidence fragments.",
            parameters={"skill_id": skill_id},
            result_bounds={"limit": bounded_limit, "max_depth": 2},
            cypher_template_id=QUERY_TEMPLATES[QUERY_FAMILY_EVIDENCE_FRAGMENT_RETRIEVAL][
                "cypher_template_id"
            ],
            generated_cypher=_render_bounded_cypher(
                QUERY_FAMILY_EVIDENCE_FRAGMENT_RETRIEVAL,
            ),
        )
    elif skill_id and (route == "context" or query_tokens & RELATIONSHIP_TERMS):
        plan_result = GraphQueryPlan(
            intent=QUERY_INTENT_RELATIONSHIP_TRAVERSAL,
            strategy="graph-first",
            query_family=QUERY_FAMILY_RELATED_SKILL_TRAVERSAL,
            rationale="Known skill plus relationship wording maps to typed skill traversal.",
            parameters={"skill_id": skill_id},
            result_bounds={"limit": bounded_limit, "max_depth": 1},
            cypher_template_id=QUERY_TEMPLATES[QUERY_FAMILY_RELATED_SKILL_TRAVERSAL][
                "cypher_template_id"
            ],
            generated_cypher=_render_bounded_cypher(QUERY_FAMILY_RELATED_SKILL_TRAVERSAL),
        )
    elif skill_id and (route == "execution_plan" or query_tokens & CONSTRAINT_TERMS):
        plan_result = GraphQueryPlan(
            intent=QUERY_INTENT_GOVERNANCE_VALIDATION_LOOKUP,
            strategy="graph-first",
            query_family=QUERY_FAMILY_CONSTRAINT_VERIFICATION_RETRIEVAL,
            rationale="Known skill plus rules or verification wording maps to bounded section retrieval.",
            parameters={"skill_id": skill_id},
            result_bounds={"limit": bounded_limit, "max_depth": 2},
            cypher_template_id=QUERY_TEMPLATES[QUERY_FAMILY_CONSTRAINT_VERIFICATION_RETRIEVAL][
                "cypher_template_id"
            ],
            generated_cypher=_render_bounded_cypher(
                QUERY_FAMILY_CONSTRAINT_VERIFICATION_RETRIEVAL,
            ),
        )
    elif skill_id:
        plan_result = GraphQueryPlan(
            intent=QUERY_INTENT_SKILL_LOOKUP,
            strategy="graph-first",
            query_family=QUERY_FAMILY_EXACT_SKILL_LOOKUP,
            rationale="Known skill or alias resolves to exact skill lookup.",
            parameters={"skill_id": skill_id},
            result_bounds={"limit": bounded_limit, "max_depth": 2},
            cypher_template_id=QUERY_TEMPLATES[QUERY_FAMILY_EXACT_SKILL_LOOKUP][
                "cypher_template_id"
            ],
            generated_cypher=_render_bounded_cypher(QUERY_FAMILY_EXACT_SKILL_LOOKUP),
        )
    elif query_tokens & PACK_TERMS:
        plan_result = GraphQueryPlan(
            intent=QUERY_INTENT_SKILL_PACK_DISCOVERY,
            strategy="keyword-first",
            query_family=QUERY_FAMILY_PACK_SKILL_MEMBERSHIP_LOOKUP,
            rationale="Pack or library wording maps to pack membership lookup.",
            parameters={"query_tokens": sorted(query_tokens)},
            result_bounds={"limit": bounded_limit, "max_depth": 1},
            cypher_template_id=QUERY_TEMPLATES[QUERY_FAMILY_PACK_SKILL_MEMBERSHIP_LOOKUP][
                "cypher_template_id"
            ],
            generated_cypher=_render_bounded_cypher(QUERY_FAMILY_PACK_SKILL_MEMBERSHIP_LOOKUP),
        )
    elif route == "recommendation" or query_tokens:
        plan_result = GraphQueryPlan(
            intent=QUERY_INTENT_MULTI_SKILL_SYNTHESIS,
            strategy="hybrid",
            query_family=QUERY_FAMILY_CAPABILITY_TASK_LOOKUP,
            rationale="Task-oriented wording maps to capability and task-shape lookup.",
            parameters={"query_tokens": sorted(query_tokens)},
            result_bounds={"limit": bounded_limit, "max_depth": 1},
            cypher_template_id=QUERY_TEMPLATES[QUERY_FAMILY_CAPABILITY_TASK_LOOKUP][
                "cypher_template_id"
            ],
            generated_cypher=_render_bounded_cypher(QUERY_FAMILY_CAPABILITY_TASK_LOOKUP),
        )
    else:
        return {
            "status": "abstain",
            "reason": "Query could not be mapped to an approved read-only graph query family.",
        }

    return {
        "status": "ok",
        "intent": plan_result.intent,
        "strategy": plan_result.strategy,
        "query_family": plan_result.query_family,
        "cypher_template_id": plan_result.cypher_template_id,
        "parameters": dict(plan_result.parameters),
        "result_bounds": dict(plan_result.result_bounds),
        "rationale": plan_result.rationale,
        "generated_cypher": plan_result.generated_cypher,
        "read_only": True,
        "allowed_labels": list(QUERY_TEMPLATES[plan_result.query_family]["labels"]),
        "allowed_relationship_types": list(
            QUERY_TEMPLATES[plan_result.query_family]["relationship_types"]
        ),
    }


def _render_bounded_cypher(query_family: str) -> str:
    return QUERY_FAMILY_RENDERED_CYPHER[query_family]


def execute_planned_query(
    plan: load_skills_neo4j.LoadPlan,
    graph_query_plan: Mapping[str, object],
) -> Mapping[str, object]:
    """Execute one approved query family against the in-memory graph snapshot."""

    if graph_query_plan.get("status") != "ok":
        return {"status": "abstain", "reason": _string(graph_query_plan.get("reason"))}
    query_family = _string(graph_query_plan.get("query_family"))
    if query_family not in APPROVED_QUERY_FAMILIES:
        return {"status": "abstain", "reason": "Query family is not approved for execution."}
    parameters = (
        graph_query_plan.get("parameters")
        if isinstance(graph_query_plan.get("parameters"), dict)
        else {}
    )
    limit = (
        graph_query_plan.get("result_bounds")
        if isinstance(graph_query_plan.get("result_bounds"), dict)
        else {}
    ).get("limit", 5)
    bounded_limit = int(limit) if isinstance(limit, int) and limit > 0 else 5

    if query_family == QUERY_FAMILY_EXACT_SKILL_LOOKUP:
        return _execute_exact_skill_lookup(plan, parameters, bounded_limit)
    if query_family == QUERY_FAMILY_RELATED_SKILL_TRAVERSAL:
        return _execute_related_skill_traversal(plan, parameters, bounded_limit)
    if query_family == QUERY_FAMILY_CAPABILITY_TASK_LOOKUP:
        return _execute_capability_task_lookup(plan, parameters, bounded_limit)
    if query_family == QUERY_FAMILY_CONSTRAINT_VERIFICATION_RETRIEVAL:
        return _execute_constraint_verification_retrieval(plan, parameters, bounded_limit)
    if query_family == QUERY_FAMILY_PACK_SKILL_MEMBERSHIP_LOOKUP:
        return _execute_pack_membership_lookup(plan, parameters, bounded_limit)
    if query_family == QUERY_FAMILY_EVIDENCE_FRAGMENT_RETRIEVAL:
        return _execute_evidence_fragment_retrieval(plan, parameters, bounded_limit)
    return {"status": "abstain", "reason": "No safe executor exists for the selected query family."}


def _execute_exact_skill_lookup(
    plan: load_skills_neo4j.LoadPlan, parameters: Mapping[str, object], limit: int
) -> Mapping[str, object]:
    skill_id = _string(parameters.get("skill_id"))
    for skill in _skill_nodes(plan):
        if skill.id != skill_id:
            continue
        retrieval_units = _retrieval_units_for_skill(plan, skill_id)[:limit]
        return {
            "status": "ok",
            "records": [
                {
                    "skill_id": skill.id,
                    "skill_name": _string(skill.properties.get("name")),
                    "aliases": skill.properties.get("aliases", []),
                    "skill_pack_id": _string(skill.properties.get("skill_pack_id")),
                }
            ],
            "citations": _citations_for_units(retrieval_units),
            "path_summaries": [],
        }
    return {"status": "abstain", "reason": f"Skill not found for bounded lookup: {skill_id}"}


def _execute_related_skill_traversal(
    plan: load_skills_neo4j.LoadPlan, parameters: Mapping[str, object], limit: int
) -> Mapping[str, object]:
    skill_id = _string(parameters.get("skill_id"))
    related: list[dict[str, object]] = []
    paths: list[str] = []
    seen: set[str] = set()
    for relationship in plan.relationships:
        if relationship.type not in ALLOWED_RELATIONSHIP_TYPES:
            continue
        neighbour = ""
        if relationship.source_id == skill_id and relationship.target_label == "Skill":
            neighbour = relationship.target_id
        elif relationship.target_id == skill_id and relationship.source_label == "Skill":
            neighbour = relationship.source_id
        if not neighbour or neighbour in seen:
            continue
        seen.add(neighbour)
        paths.append(f"{relationship.source_id} -[{relationship.type}]-> {relationship.target_id}")
        related.append({"skill_id": neighbour, "relationship_type": relationship.type})
        if len(related) >= limit:
            break
    if not related:
        return {"status": "abstain", "reason": "No related skills found for bounded traversal."}
    return {"status": "ok", "records": related, "citations": [], "path_summaries": paths}


def _execute_capability_task_lookup(
    plan: load_skills_neo4j.LoadPlan, parameters: Mapping[str, object], limit: int
) -> Mapping[str, object]:
    query_tokens = {
        token for token in parameters.get("query_tokens", []) if isinstance(token, str) and token
    }
    matches: list[dict[str, object]] = []
    evidence_paths: list[str] = []
    scores: defaultdict[str, int] = defaultdict(int)
    skill_names: dict[str, str] = {}
    for relationship in plan.relationships:
        if relationship.type not in {"HAS_CAPABILITY", "HAS_TASK_SHAPE"}:
            continue
        tokens = _tokens(f"{relationship.target_id} {relationship.properties}")
        overlap = query_tokens & tokens
        if not overlap:
            continue
        scores[relationship.source_id] += len(overlap)
        evidence_paths.append(
            f"{relationship.source_id} -[{relationship.type}]-> {relationship.target_id}"
        )
    for skill in _skill_nodes(plan):
        skill_names[skill.id] = _string(skill.properties.get("name"))
    for skill_id, score in sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:limit]:
        matches.append(
            {"skill_id": skill_id, "skill_name": skill_names.get(skill_id, skill_id), "score": score}
        )
    if not matches:
        return {"status": "abstain", "reason": "No capability or task-shape matches were found."}
    return {"status": "ok", "records": matches, "citations": [], "path_summaries": evidence_paths[:limit]}


def _execute_constraint_verification_retrieval(
    plan: load_skills_neo4j.LoadPlan, parameters: Mapping[str, object], limit: int
) -> Mapping[str, object]:
    skill_id = _string(parameters.get("skill_id"))
    matched_units = [
        unit
        for unit in _retrieval_units_for_skill(plan, skill_id)
        if any(
            marker in _string(unit.properties.get("section_id")).lower()
            for marker in ("verification", "rules", "guardrails", "constraint")
        )
    ][:limit]
    if not matched_units:
        return {
            "status": "abstain",
            "reason": "No verification or constraint evidence was available for this skill.",
        }
    return {"status": "ok", "records": [], "citations": _citations_for_units(matched_units), "path_summaries": []}


def _execute_pack_membership_lookup(
    plan: load_skills_neo4j.LoadPlan, parameters: Mapping[str, object], limit: int
) -> Mapping[str, object]:
    query_tokens = {
        token for token in parameters.get("query_tokens", []) if isinstance(token, str) and token
    }
    matches: list[dict[str, object]] = []
    for skill in _skill_nodes(plan):
        pack_id = _string(skill.properties.get("skill_pack_id"))
        if not pack_id:
            continue
        match_terms = _tokens(f"{pack_id} {_string(skill.properties.get('skill_pack_version'))}")
        if query_tokens and not (query_tokens & match_terms):
            continue
        matches.append(
            {
                "skill_pack_id": pack_id,
                "skill_id": skill.id,
                "skill_name": _string(skill.properties.get("name")),
            }
        )
        if len(matches) >= limit:
            break
    if not matches:
        return {"status": "abstain", "reason": "No skill-pack membership matches were found."}
    return {"status": "ok", "records": matches, "citations": [], "path_summaries": []}


def _execute_evidence_fragment_retrieval(
    plan: load_skills_neo4j.LoadPlan, parameters: Mapping[str, object], limit: int
) -> Mapping[str, object]:
    skill_id = _string(parameters.get("skill_id"))
    units = _retrieval_units_for_skill(plan, skill_id)[:limit]
    if not units:
        return {"status": "abstain", "reason": "No evidence fragments were available for this skill."}
    return {"status": "ok", "records": [], "citations": _citations_for_units(units), "path_summaries": []}


def _citations_for_units(
    units: Sequence[load_skills_neo4j.GraphNode],
) -> list[dict[str, object]]:
    citations: list[dict[str, object]] = []
    for unit in units:
        citations.append(
            {
                "retrieval_unit_id": unit.id,
                "source_path": _string(unit.properties.get("source_path")),
                "section_id": _string(unit.properties.get("section_id")),
                "text": _string(unit.properties.get("text"))[:320],
            }
        )
    return citations
