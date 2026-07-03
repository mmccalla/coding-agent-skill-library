#!/usr/bin/env python3
"""Deterministic agent-facing routing helpers for the Skills KG."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence

from scripts import load_skills_neo4j

ROUTE_DIRECT_LOOKUP = "direct_lookup"
ROUTE_RECOMMENDATION = "recommendation"
ROUTE_CONTEXT = "context"
ROUTE_EXECUTION_PLAN = "execution_plan"
ROUTES = frozenset({ROUTE_DIRECT_LOOKUP, ROUTE_RECOMMENDATION, ROUTE_CONTEXT, ROUTE_EXECUTION_PLAN})

CONTEXT_KEYWORDS = frozenset(
    {
        "context",
        "related",
        "neighbour",
        "neighbouring",
        "neighbor",
        "neighboring",
        "prerequisite",
        "dependency",
        "dependencies",
        "complement",
        "connected",
    }
)
EXECUTION_KEYWORDS = frozenset(
    {
        "apply",
        "execute",
        "execution",
        "guide",
        "checklist",
        "procedure",
        "steps",
        "use",
        "run",
    }
)
RECOMMENDATION_KEYWORDS = frozenset(
    {
        "recommend",
        "which",
        "what skills",
        "what skill",
        "choose",
        "select",
        "should i use",
        "best",
        "task",
    }
)


def route_skill_query(plan: load_skills_neo4j.LoadPlan, query: str) -> dict[str, object]:
    """Classify a natural-language skill query into one of the public routes."""

    clean_query = query.strip()
    lowered_query = clean_query.lower()
    resolved = resolve_skill(plan, clean_query)
    resolved_skill_id = _string(resolved.get("skill_id")) if resolved["status"] == "ok" else ""

    if resolved_skill_id and _contains_any(lowered_query, CONTEXT_KEYWORDS):
        route = ROUTE_CONTEXT
        confidence = 0.9
        rationale = "A known skill and context/relationship wording were both detected."
        suggested_tool = "get_skill_context"
    elif resolved_skill_id and _contains_any(lowered_query, EXECUTION_KEYWORDS):
        route = ROUTE_EXECUTION_PLAN
        confidence = 0.88
        rationale = "A known skill and execution/checklist wording were both detected."
        suggested_tool = "get_skill_execution_guide"
    elif resolved_skill_id:
        route = ROUTE_DIRECT_LOOKUP
        confidence = 0.86
        rationale = "A known skill name or canonical skill id was detected."
        suggested_tool = "get_skill"
    else:
        route = ROUTE_RECOMMENDATION
        confidence = 0.72 if _contains_any(lowered_query, RECOMMENDATION_KEYWORDS) else 0.6
        rationale = "No exact skill was detected; use task-oriented recommendation evidence."
        suggested_tool = "recommend_skills"

    selection_trace = _route_selection_trace(
        plan,
        clean_query,
        route=route,
        confidence=confidence,
        rationale=rationale,
        resolved_skill_id=resolved_skill_id,
        suggested_tool=suggested_tool,
    )
    return {
        "status": "ok",
        "route": route,
        "confidence": confidence,
        "rationale": rationale,
        "resolved_skill_id": resolved_skill_id or None,
        "suggested_tool": suggested_tool,
        "evidence_required": _evidence_required(route),
        "selection_trace": selection_trace,
    }


def resolve_skill(plan: load_skills_neo4j.LoadPlan, name: str) -> dict[str, object]:
    """Map a human skill name, alias or canonical id to a Skills KG skill id."""

    clean_name = name.strip()
    normalised_name = _normalise(clean_name)
    if not normalised_name:
        return {"status": "error", "message": "Skill name is required."}

    matches: list[tuple[int, load_skills_neo4j.GraphNode]] = []
    for skill in _skills(plan):
        aliases = _aliases_for_skill(skill)
        if normalised_name in aliases:
            return _resolved_skill_response(plan, skill, "exact")
        contained_aliases = [
            alias for alias in aliases if alias and _contains_alias_phrase(normalised_name, alias)
        ]
        if contained_aliases:
            matches.append((max(len(alias) for alias in contained_aliases), skill))

    if matches:
        _, skill = sorted(matches, key=lambda item: (-item[0], _skill_name(item[1])))[0]
        return _resolved_skill_response(plan, skill, "embedded")

    return {"status": "error", "message": f"Skill not found: {clean_name}"}


def get_skill_execution_guide(
    plan: load_skills_neo4j.LoadPlan,
    skill_id: str,
    *,
    related_limit: int = 10,
) -> dict[str, object]:
    """Return an agent-actionable execution guide for one skill."""

    skill = _skill_by_id(plan, skill_id)
    if skill is None:
        return {"status": "error", "message": f"Skill not found: {skill_id}"}

    section_texts = _canonical_section_texts(_retrieval_units_for_skill(plan, skill_id))
    related_skill_ids, evidence_paths = _related_skill_ids(plan, skill_id, related_limit)
    evidence = _section_evidence(_retrieval_units_for_skill(plan, skill_id))
    return {
        "status": "ok",
        "skill_id": skill.id,
        "skill_name": _skill_name(skill),
        "source_paths": _source_paths_for_skill(plan, skill.id),
        "when_to_use": section_texts["when_to_use"],
        "objective": section_texts["objective"],
        "procedure": section_texts["procedure"],
        "rules": section_texts["rules"],
        "verification_checklist": _verification_checklist(section_texts["verification"]),
        "related_skill_ids": related_skill_ids,
        "evidence_paths": evidence_paths,
        "evidence": evidence,
    }


def _skills(plan: load_skills_neo4j.LoadPlan) -> tuple[load_skills_neo4j.GraphNode, ...]:
    return tuple(node for node in plan.nodes if node.label == "Skill")


def _skill_by_id(
    plan: load_skills_neo4j.LoadPlan, skill_id: str
) -> load_skills_neo4j.GraphNode | None:
    for skill in _skills(plan):
        if skill.id == skill_id:
            return skill
    return None


def _retrieval_units_for_skill(
    plan: load_skills_neo4j.LoadPlan, skill_id: str
) -> tuple[load_skills_neo4j.GraphNode, ...]:
    return tuple(
        node
        for node in plan.nodes
        if node.label == "RetrievalUnit" and node.properties.get("skill_id") == skill_id
    )


def _aliases_for_skill(skill: load_skills_neo4j.GraphNode) -> set[str]:
    skill_name = _skill_name(skill)
    title = _string(skill.properties.get("title"))
    aliases = {
        _normalise(skill.id),
        _normalise(skill.id.removeprefix("skill:")),
        _normalise(skill_name),
        _normalise(f"skill:{skill_name}"),
    }
    if title:
        aliases.add(_normalise(title))
    raw_aliases = skill.properties.get("aliases")
    if isinstance(raw_aliases, list):
        for alias in raw_aliases:
            if isinstance(alias, str):
                aliases.add(_normalise(alias))
    return {alias for alias in aliases if alias}


def _resolved_skill_response(
    plan: load_skills_neo4j.LoadPlan,
    skill: load_skills_neo4j.GraphNode,
    match_type: str,
) -> dict[str, object]:
    return {
        "status": "ok",
        "skill_id": skill.id,
        "skill_name": _skill_name(skill),
        "match_type": match_type,
        "source_paths": _source_paths_for_skill(plan, skill.id),
    }


def _source_paths_for_skill(plan: load_skills_neo4j.LoadPlan, skill_id: str) -> tuple[str, ...]:
    paths: list[str] = []
    skill = _skill_by_id(plan, skill_id)
    if skill is not None:
        path = _string(skill.properties.get("path"))
        if path:
            paths.append(path)
    for unit in _retrieval_units_for_skill(plan, skill_id):
        path = _string(unit.properties.get("source_path"))
        if path:
            paths.append(path)
    return tuple(dict.fromkeys(paths))


def _canonical_section_texts(
    retrieval_units: Sequence[load_skills_neo4j.GraphNode],
) -> dict[str, str]:
    sections = {
        "when_to_use": "",
        "objective": "",
        "procedure": "",
        "rules": "",
        "verification": "",
    }
    for unit in retrieval_units:
        section_id = _string(unit.properties.get("section_id")).lower()
        text = _string(unit.properties.get("text")).strip()
        if not text:
            continue
        if "when-to-use" in section_id:
            sections["when_to_use"] = text
        elif "objective" in section_id:
            sections["objective"] = text
        elif "procedure" in section_id:
            sections["procedure"] = text
        elif "rules" in section_id or "guardrails" in section_id:
            sections["rules"] = text
        elif "verification" in section_id:
            sections["verification"] = text
    return sections


def _verification_checklist(text: str) -> tuple[str, ...]:
    checks = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- [ ]"):
            checks.append(stripped.removeprefix("- [ ]").strip())
        elif stripped.startswith("- "):
            checks.append(stripped.removeprefix("- ").strip())
    return tuple(check for check in checks if check)


def _section_evidence(
    retrieval_units: Sequence[load_skills_neo4j.GraphNode],
) -> tuple[dict[str, str], ...]:
    evidence: list[dict[str, str]] = []
    for unit in retrieval_units:
        section_id = _string(unit.properties.get("section_id"))
        if any(
            marker in section_id.lower()
            for marker in ("when-to-use", "objective", "procedure", "rules", "verification")
        ):
            evidence.append(
                {
                    "retrieval_unit_id": unit.id,
                    "section_id": section_id,
                    "source_path": _string(unit.properties.get("source_path")),
                    "heading_path": _string(unit.properties.get("heading_path")),
                    "line_start": unit.properties.get("line_start", 0),
                    "line_end": unit.properties.get("line_end", 0),
                }
            )
    return tuple(evidence)


def _related_skill_ids(
    plan: load_skills_neo4j.LoadPlan,
    skill_id: str,
    limit: int,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    related: list[str] = []
    evidence_paths: list[str] = []
    for relationship in plan.relationships:
        if relationship.source_id == skill_id:
            evidence_paths.append(
                f"{relationship.source_id} -[{relationship.type}]-> {relationship.target_id}"
            )
            if relationship.target_label == "Skill":
                related.append(relationship.target_id)
        elif relationship.target_id == skill_id:
            evidence_paths.append(
                f"{relationship.source_id} -[{relationship.type}]-> {relationship.target_id}"
            )
            if relationship.source_label == "Skill":
                related.append(relationship.source_id)
    return tuple(dict.fromkeys(related))[:limit], tuple(evidence_paths[:limit])


def usage_event_id(tool: str, query: str) -> str:
    """Return a deterministic, audit-friendly usage event id for selection traces."""

    digest = hashlib.sha256(f"{tool}:{query.strip()}".encode()).hexdigest()[:16]
    return f"sel-{digest}"


def _route_selection_trace(
    plan: load_skills_neo4j.LoadPlan,
    query: str,
    *,
    route: str,
    confidence: float,
    rationale: str,
    resolved_skill_id: str,
    suggested_tool: str,
) -> dict[str, object]:
    trace: dict[str, object] = {
        "tool": "route_skill_query",
        "query_intent": route,
        "usage_event_id": usage_event_id("route_skill_query", query),
        "route": route,
        "confidence": confidence,
        "rationale": rationale,
        "suggested_tool": suggested_tool,
        "resolved_skill_id": resolved_skill_id or None,
        "filter": {
            "resolved": bool(resolved_skill_id),
            "evidence_required": list(_evidence_required(route)),
        },
    }
    if resolved_skill_id:
        skill = _skill_by_id(plan, resolved_skill_id)
        if skill is not None:
            evidence_anchors = _section_evidence(_retrieval_units_for_skill(plan, resolved_skill_id))
            trace["evidence"] = {
                "skill_id": resolved_skill_id,
                "skill_name": _skill_name(skill),
                "source_paths": list(_source_paths_for_skill(plan, resolved_skill_id)),
                "evidence_anchors": list(evidence_anchors),
            }
            trace["evidence_anchor_ids"] = [
                anchor.get("section_id") or anchor.get("retrieval_unit_id")
                for anchor in evidence_anchors
                if anchor.get("section_id") or anchor.get("retrieval_unit_id")
            ]
    return trace


def _evidence_required(route: str) -> tuple[str, ...]:
    requirements = {
        ROUTE_DIRECT_LOOKUP: ("resolved_skill_id", "retrieval units", "source paths"),
        ROUTE_RECOMMENDATION: ("ranked recommendations", "rationale", "source snippets"),
        ROUTE_CONTEXT: ("resolved_skill_id", "related skills", "evidence paths"),
        ROUTE_EXECUTION_PLAN: (
            "when-to-use",
            "objective",
            "procedure",
            "rules",
            "verification checklist",
            "related skills",
        ),
    }
    return requirements.get(route, ())


def _contains_any(text: str, candidates: frozenset[str]) -> bool:
    return any(candidate in text for candidate in candidates)


def _contains_alias_phrase(normalised_text: str, alias: str) -> bool:
    pattern = rf"(?:^|[-:]){re.escape(alias)}(?:$|[-:])"
    return bool(re.search(pattern, normalised_text))


def _normalise(value: str) -> str:
    return re.sub(r"[^a-z0-9:]+", "-", value.lower()).strip("-")


def _skill_name(skill: load_skills_neo4j.GraphNode) -> str:
    return _string(skill.properties.get("name")) or skill.id.removeprefix("skill:")


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""
