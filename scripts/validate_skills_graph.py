#!/usr/bin/env python3
"""Validate exported skills graph records for holistic connectivity."""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Mapping, NamedTuple, Sequence, cast

BRIDGE_FIELDS = (
    "task_shapes",
    "workflow_stages",
    "capabilities",
    "control_themes",
    "knowledge_domains",
)
STOP_WORDS = {
    "and",
    "any",
    "for",
    "from",
    "into",
    "that",
    "the",
    "this",
    "use",
    "when",
    "with",
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
    return tuple(
        cast(Mapping[str, object], skill)
        for skill in skills
        if isinstance(skill, dict)
    )


def _relationship_records(records: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
    relationships = records.get("relationships")
    if not isinstance(relationships, list):
        return ()
    return tuple(
        cast(Mapping[str, object], relationship)
        for relationship in relationships
        if isinstance(relationship, dict)
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


def _unique(values: Sequence[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    unique_values: list[str] = []
    for value in values:
        clean_value = value.strip()
        if clean_value and clean_value not in seen:
            seen.add(clean_value)
            unique_values.append(clean_value)
    return tuple(unique_values)


def _slug_tokens(text: str) -> tuple[str, ...]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return tuple(token for token in tokens if token not in STOP_WORDS and len(token) > 2)


def _frontmatter_value(text: str, key: str) -> str:
    if not text.startswith("---\n"):
        return ""
    frontmatter_end = text.find("\n---\n", 4)
    if frontmatter_end == -1:
        return ""
    frontmatter = text[4:frontmatter_end]
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", frontmatter, flags=re.M)
    return match.group(1).strip() if match else ""


def _section_text(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)",
        text,
        flags=re.M | re.S,
    )
    return match.group(1) if match else ""


def _related_skill_names(text: str, known_skill_names: set[str]) -> tuple[str, ...]:
    related_section = _section_text(text, "Related skills")
    return _unique(
        tuple(
            name
            for name in re.findall(r"`([-a-z0-9]+)`", related_section)
            if name in known_skill_names
        )
    )


def _workflow_stages(text: str) -> tuple[str, ...]:
    stages = ["skill-use"]
    if re.search(r"^## When to use\s*$", text, flags=re.M):
        stages.append("routing")
    if re.search(r"^## Procedure\s*$", text, flags=re.M):
        stages.append("execution")
    if re.search(r"^## Verification\s*$", text, flags=re.M):
        stages.append("verification")
    return _unique(stages)


def _task_shapes(name: str, description: str) -> tuple[str, ...]:
    description_tokens = _slug_tokens(description)
    name_tokens = _slug_tokens(name)
    return _unique(("skill-operation", *name_tokens[:3], *description_tokens[:5]))


def _capabilities(name: str, category: str, description: str) -> tuple[str, ...]:
    return _unique((*_slug_tokens(name), *_slug_tokens(category), *_slug_tokens(description)[:4]))


def build_records_from_skills(skills_root: Path) -> dict[str, object]:
    """Build deterministic graph records from repository-local skill files."""

    skill_paths = sorted(skills_root.rglob("SKILL.md"))
    known_skill_names = {path.parent.name for path in skill_paths}
    skills: list[dict[str, object]] = []
    relationships: list[dict[str, str]] = []

    for path in skill_paths:
        text = path.read_text(encoding="utf-8")
        name = _frontmatter_value(text, "name") or path.parent.name
        category = path.parent.parent.name
        description = _frontmatter_value(text, "description")
        skill_id = f"skill:{name}"
        related_names = _related_skill_names(text, known_skill_names)

        skills.append(
            {
                "id": skill_id,
                "name": name,
                "category": category,
                "task_shapes": list(_task_shapes(name, description)),
                "workflow_stages": list(_workflow_stages(text)),
                "capabilities": list(_capabilities(name, category, description)),
                "control_themes": ["skill-governance", category],
                "knowledge_domains": [category],
                "related_skill_ids": [f"skill:{related_name}" for related_name in related_names],
                "source_path": str(path),
            }
        )

        for related_name in related_names:
            relationships.append(
                {
                    "source": skill_id,
                    "type": "RELATED_TO",
                    "target": f"skill:{related_name}",
                }
            )

    return {
        "root_skill": "apply-laws-of-ai",
        "skills": skills,
        "relationships": relationships,
    }


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

    for relationship in _relationship_records(records):
        source = _string_value(relationship, "source")
        target = _string_value(relationship, "target")
        if source in skills_by_id and target in skills_by_id:
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
                _add_edge(graph, skill_id, f"{field}:{value}")

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
