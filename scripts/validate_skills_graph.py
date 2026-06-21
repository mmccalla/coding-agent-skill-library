#!/usr/bin/env python3
"""Validate exported skills graph records for holistic connectivity."""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict, deque
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import NamedTuple, cast

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.extract_skills_graph import extract_skills_graph_records
from scripts.map_skills_bridges import apply_semantic_bridge_mappings

BRIDGE_FIELDS = (
    "task_shapes",
    "workflow_stages",
    "capabilities",
    "control_themes",
    "knowledge_domains",
)
BRIDGE_FIELD_KINDS = {
    "task_shapes": "task_shape",
    "workflow_stages": "workflow_stage",
    "capabilities": "capability",
    "control_themes": "control_theme",
    "knowledge_domains": "knowledge_domain",
}
ALLOWED_BRIDGE_KINDS = set(BRIDGE_FIELD_KINDS.values())
ALLOWED_RELATIONSHIP_TYPES = {
    "RELATED_TO",
    "PRECEDES",
    "REQUIRES",
    "COMPLEMENTS",
    "REFINES",
    "GOVERNS",
    "VALIDATES",
}
NON_CONNECTIVE_BRIDGE_SOURCES = {
    ("control_theme", "category"),
    ("knowledge_domain", "category"),
}


class GraphValidationResult(NamedTuple):
    """Human-readable validation result for CI and local checks."""

    valid: bool
    errors: tuple[str, ...]


def _string_value(record: Mapping[str, object], key: str) -> str:
    value = record.get(key)
    return value if isinstance(value, str) else ""


def _string_list(record: Mapping[str, object], key: str) -> tuple[str, ...]:
    value = record.get(key)
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str) and item.strip())


def _skill_records(records: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
    skills = records.get("skills")
    if not isinstance(skills, list):
        return ()
    return tuple(cast(Mapping[str, object], skill) for skill in skills if isinstance(skill, dict))


def _relationship_records(records: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
    relationships = records.get("relationships")
    if not isinstance(relationships, list):
        return ()
    return tuple(
        cast(Mapping[str, object], relationship)
        for relationship in relationships
        if isinstance(relationship, dict)
    )


def _bridge_records(records: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
    bridges = records.get("bridges")
    if not isinstance(bridges, list):
        return ()
    return tuple(
        cast(Mapping[str, object], bridge) for bridge in bridges if isinstance(bridge, dict)
    )


def _root_skill_id(
    records: Mapping[str, object],
    skills_by_id: Mapping[str, Mapping[str, object]],
) -> str:
    root = records.get("root_skill", "apply-laws-of-ai")
    root_text = root if isinstance(root, str) else "apply-laws-of-ai"
    if root_text in skills_by_id:
        return root_text
    for skill_id, skill in skills_by_id.items():
        if _string_value(skill, "name") == root_text:
            return skill_id
    return root_text


def _add_edge(graph: dict[str, set[str]], left: str, right: str) -> None:
    if not left or not right:
        return
    graph[left].add(right)
    graph[right].add(left)


def _reachable_nodes(graph: Mapping[str, set[str]], start: str) -> set[str]:
    if start not in graph:
        return set()
    visited = {start}
    queue: deque[str] = deque([start])
    while queue:
        current = queue.popleft()
        for neighbour in graph.get(current, set()):
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)
    return visited


def _valid_confidence(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and 0.0 <= float(value) <= 1.0
    )


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "bridge"


def build_records_from_skills(skills_root: Path) -> dict[str, object]:
    """Build deterministic graph records from repository-local skill files."""
    records = extract_skills_graph_records(skills_root)
    return apply_semantic_bridge_mappings(records)


def validate_graph_records(records: Mapping[str, object]) -> GraphValidationResult:
    """Validate that exported skill records form one connected skills graph.

    Category membership is required metadata but is not counted as proof of
    reachability. This prevents category-only islands from masking outliers.
    """

    errors: list[str] = []
    skills = _skill_records(records)
    if not skills:
        return GraphValidationResult(False, ("no skill records found",))

    skills_by_id = {
        _string_value(skill, "id"): skill for skill in skills if _string_value(skill, "id")
    }
    root_id = _root_skill_id(records, skills_by_id)
    if root_id not in skills_by_id:
        errors.append(f"root skill '{root_id}' is missing from exported records")

    graph: dict[str, set[str]] = defaultdict(set)
    related_skill_ids_by_skill: dict[str, set[str]] = defaultdict(set)
    proven_bridge_sources: dict[tuple[str, str, str], str] = {}
    for bridge in _bridge_records(records):
        bridge_skill_id = _string_value(bridge, "skill_id")
        bridge_kind = _string_value(bridge, "kind")
        bridge_value = _string_value(bridge, "value")
        bridge_source = _string_value(bridge, "source")
        bridge_path = _string_value(bridge, "source_path") or _string_value(bridge, "path")
        bridge_id = _string_value(bridge, "id")
        skill_path = _string_value(skills_by_id.get(bridge_skill_id, {}), "path")
        expected_bridge_id = f"{bridge_skill_id}:bridge:{bridge_kind}:{_slug(bridge_value)}"
        bridge_key = (bridge_skill_id, bridge_kind, bridge_value)
        if (
            bridge_skill_id not in skills_by_id
            or bridge_kind not in ALLOWED_BRIDGE_KINDS
            or not bridge_value
            or not bridge_source
            or not bridge_path
            or not _valid_confidence(bridge.get("confidence"))
            or bridge_id != expected_bridge_id
            or (bool(skill_path) and bridge_path != skill_path)
        ):
            errors.append(
                "invalid bridge provenance for "
                f"{bridge_skill_id or '<missing skill>'}:{bridge_kind or '<missing kind>'}:"
                f"{bridge_value or '<missing value>'}"
            )
            continue
        proven_bridge_sources[bridge_key] = bridge_source

    for relationship in _relationship_records(records):
        source = _string_value(relationship, "source")
        target = _string_value(relationship, "target")
        rel_type = _string_value(relationship, "type")
        source_path = _string_value(relationship, "source_path")
        source_section_id = _string_value(relationship, "source_section_id")
        mapping_rule_id = _string_value(relationship, "mapping_rule_id")
        relationship_valid = (
            source in skills_by_id
            and target in skills_by_id
            and rel_type in ALLOWED_RELATIONSHIP_TYPES
            and bool(source_path)
            and (
                (rel_type == "RELATED_TO" and bool(source_section_id))
                or (rel_type != "RELATED_TO" and bool(mapping_rule_id))
            )
        )
        if not relationship_valid:
            errors.append(
                "invalid relationship provenance for "
                f"{source or '<missing source>'}:{rel_type or '<missing type>'}:"
                f"{target or '<missing target>'}"
            )
            continue
        _add_edge(graph, source, target)
        related_skill_ids_by_skill[source].add(target)
        related_skill_ids_by_skill[target].add(source)

    for skill in skills:
        skill_id = _string_value(skill, "id")
        skill_name = _string_value(skill, "name") or skill_id
        graph.setdefault(skill_id, set())

        if not _string_value(skill, "category"):
            errors.append(f"{skill_name}: missing category bridge")

        has_task_or_capability = bool(
            _string_list(skill, "task_shapes") or _string_list(skill, "capabilities")
        )
        if not has_task_or_capability:
            errors.append(f"{skill_name}: missing task/capability bridge")

        if not _string_list(skill, "workflow_stages"):
            errors.append(f"{skill_name}: missing workflow stage")

        semantic_bridges = (
            _string_list(skill, "control_themes")
            + _string_list(skill, "knowledge_domains")
            + _string_list(skill, "related_skill_ids")
        )
        if not semantic_bridges and not related_skill_ids_by_skill.get(skill_id):
            errors.append(f"{skill_name}: missing semantic bridge")

        for field in BRIDGE_FIELDS:
            for value in _string_list(skill, field):
                bridge_key = (skill_id, BRIDGE_FIELD_KINDS[field], value)
                proven_source = proven_bridge_sources.get(bridge_key)
                if proven_source:
                    if (
                        BRIDGE_FIELD_KINDS[field],
                        proven_source,
                    ) not in NON_CONNECTIVE_BRIDGE_SOURCES:
                        _add_edge(graph, skill_id, f"{field}:{value}")
                else:
                    errors.append(
                        f"{skill_name}: missing bridge provenance for "
                        f"{BRIDGE_FIELD_KINDS[field]} '{value}'"
                    )

        for related_skill_id in _string_list(skill, "related_skill_ids"):
            if related_skill_id in skills_by_id:
                _add_edge(graph, skill_id, related_skill_id)

    reachable = _reachable_nodes(graph, root_id)
    for skill_id, skill in sorted(skills_by_id.items()):
        if skill_id not in reachable:
            skill_name = _string_value(skill, "name") or skill_id
            errors.append(f"{skill_name}: unreachable from root '{root_id}'")

    return GraphValidationResult(not errors, tuple(errors))


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) > 1:
        print("Usage: validate_skills_graph.py [exported-records.json]")
        return 2

    if args:
        path = Path(args[0])
        records = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(records, dict):
            print("FAIL")
            print("- exported records must be a JSON object")
            return 1
        graph_records = cast(Mapping[str, object], records)
    else:
        graph_records = build_records_from_skills(Path("skills"))

    result = validate_graph_records(graph_records)
    if not result.valid:
        print("FAIL")
        for error in result.errors:
            print(f"- {error}")
        return 1

    print("PASS: skills graph has one connected non-exempt skills component.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
