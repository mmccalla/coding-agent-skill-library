#!/usr/bin/env python3
"""Apply curated semantic bridge mappings to extracted skills graph records."""

from __future__ import annotations

import json
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Mapping, Sequence, cast

try:
    from extract_skills_graph import extract_skills_graph_records
except ModuleNotFoundError:
    from scripts.extract_skills_graph import extract_skills_graph_records

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAPPING_RULES = REPO_ROOT / "skills_docs" / "ontology" / "bridge_mapping_rules.json"
BRIDGE_KIND_TO_SKILL_FIELD = {
    "task_shape": "task_shapes",
    "workflow_stage": "workflow_stages",
    "capability": "capabilities",
    "control_theme": "control_themes",
    "knowledge_domain": "knowledge_domains",
}
RULE_FIELD_TO_BRIDGE_KIND = {
    "task_shapes": "task_shape",
    "workflow_stages": "workflow_stage",
    "capabilities": "capability",
    "control_themes": "control_theme",
    "knowledge_domains": "knowledge_domain",
}


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "bridge"


def _string_list(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str) and item.strip())


def _rules_mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, dict):
        return {}
    return cast(Mapping[str, object], value)


def _append_unique(values: list[object], new_values: Sequence[str]) -> None:
    existing = {value for value in values if isinstance(value, str)}
    for value in new_values:
        if value not in existing:
            values.append(value)
            existing.add(value)


def _bridge_record(
    skill_id: str,
    kind: str,
    value: str,
    skill_path: str,
    rule_id: str,
) -> dict[str, object]:
    return {
        "id": f"{skill_id}:bridge:{kind}:{_slug(value)}",
        "skill_id": skill_id,
        "name": value,
        "kind": kind,
        "value": value,
        "source": rule_id,
        "path": skill_path,
        "source_path": skill_path,
        "confidence": 1.0,
    }


def _relationship_record(
    skill_id: str,
    relationship: Mapping[str, object],
    skill_path: str,
    rule_id: str,
) -> dict[str, object]:
    target = relationship.get("target")
    rel_type = relationship.get("type")
    if not isinstance(target, str) or not isinstance(rel_type, str):
        raise ValueError(f"{rule_id}: relationship requires string target and type")
    return {
        "source": skill_id,
        "type": rel_type,
        "target": target,
        "source_path": skill_path,
        "source_section_id": "",
        "mapping_rule_id": rule_id,
    }


def _bridge_records_by_id(records: Mapping[str, object]) -> dict[str, dict[str, object]]:
    bridges = records.get("bridges", [])
    if not isinstance(bridges, list):
        return {}
    return {
        bridge["id"]: bridge
        for bridge in bridges
        if isinstance(bridge, dict) and isinstance(bridge.get("id"), str)
    }


def _relationship_key(relationship: Mapping[str, object]) -> tuple[str, str, str]:
    return (
        relationship.get("source") if isinstance(relationship.get("source"), str) else "",
        relationship.get("type") if isinstance(relationship.get("type"), str) else "",
        relationship.get("target") if isinstance(relationship.get("target"), str) else "",
    )


def _apply_rule_to_skill(
    skill: dict[str, object],
    rule: Mapping[str, object],
    rule_id: str,
    bridges_by_id: dict[str, dict[str, object]],
    relationships_by_key: dict[tuple[str, str, str], dict[str, object]],
) -> None:
    skill_id = skill["id"]
    skill_path = skill["path"]
    if not isinstance(skill_id, str) or not isinstance(skill_path, str):
        raise ValueError(f"{rule_id}: skill must include string id and path")

    for field, kind in RULE_FIELD_TO_BRIDGE_KIND.items():
        values = _string_list(rule.get(field))
        if not values:
            continue
        existing_values = skill.get(field)
        if not isinstance(existing_values, list):
            raise ValueError(f"{rule_id}: skill field {field} must be a list")
        _append_unique(existing_values, values)
        for value in values:
            bridge = _bridge_record(skill_id, kind, value, skill_path, rule_id)
            bridges_by_id[bridge["id"]] = bridge

    for relationship_value in rule.get("relationships", []):
        if not isinstance(relationship_value, dict):
            raise ValueError(f"{rule_id}: relationship entries must be objects")
        relationship = _relationship_record(
            skill_id=skill_id,
            relationship=cast(Mapping[str, object], relationship_value),
            skill_path=skill_path,
            rule_id=rule_id,
        )
        relationships_by_key[_relationship_key(relationship)] = relationship


def apply_semantic_bridge_mappings(
    records: Mapping[str, object],
    rules_path: Path = DEFAULT_MAPPING_RULES,
) -> dict[str, object]:
    """Apply documented mapping rules to extracted records without side effects."""

    mapped = deepcopy(dict(records))
    skills = mapped.get("skills")
    relationships = mapped.get("relationships")
    if not isinstance(skills, list) or not isinstance(relationships, list):
        raise ValueError("records must contain skills and relationships lists")

    rules = json.loads(rules_path.read_text(encoding="utf-8"))
    if not isinstance(rules, dict):
        raise ValueError(f"{rules_path}: rules must be a JSON object")

    category_rules = _rules_mapping(rules.get("category_rules"))
    skill_rules = _rules_mapping(rules.get("skill_rules"))
    bridges_by_id = _bridge_records_by_id(mapped)
    relationships_by_key = {
        _relationship_key(cast(Mapping[str, object], relationship)): relationship
        for relationship in relationships
        if isinstance(relationship, dict)
    }

    for skill_value in skills:
        if not isinstance(skill_value, dict):
            continue
        skill = cast(dict[str, object], skill_value)
        category = skill.get("category")
        name = skill.get("name")
        if isinstance(category, str) and category in category_rules:
            _apply_rule_to_skill(
                skill=skill,
                rule=_rules_mapping(category_rules[category]),
                rule_id=f"category-rule:{category}",
                bridges_by_id=bridges_by_id,
                relationships_by_key=relationships_by_key,
            )
        if isinstance(name, str) and name in skill_rules:
            _apply_rule_to_skill(
                skill=skill,
                rule=_rules_mapping(skill_rules[name]),
                rule_id=f"skill-rule:{name}",
                bridges_by_id=bridges_by_id,
                relationships_by_key=relationships_by_key,
            )

    mapped["bridges"] = [bridges_by_id[key] for key in sorted(bridges_by_id)]
    mapped["relationships"] = [
        relationships_by_key[key] for key in sorted(relationships_by_key)
    ]
    return mapped


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) > 2:
        print("Usage: map_skills_bridges.py [skills-root] [rules-json]")
        return 2

    skills_root = Path(args[0]) if args else Path("skills")
    rules_path = Path(args[1]) if len(args) == 2 else DEFAULT_MAPPING_RULES
    records = extract_skills_graph_records(skills_root)
    mapped = apply_semantic_bridge_mappings(records, rules_path)
    print(json.dumps(mapped, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
