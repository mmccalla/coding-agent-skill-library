#!/usr/bin/env python3
"""Apply curated semantic bridge mappings to extracted skills graph records."""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Mapping, Sequence
from copy import deepcopy
from pathlib import Path
from typing import cast

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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
ALLOWED_SCOPES = frozenset({"category", "skill"})
RELATIONSHIP_BRIDGE_KIND = "relationship"
REQUIRED_RULE_FIELDS = frozenset(
    {
        "id",
        "scope",
        "source",
        "bridge_kind",
        "bridge_value",
        "confidence",
        "rationale",
    }
)


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "bridge"


def _string_list(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str) and item.strip())


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
    confidence: float,
    rationale: str,
    source_scope: str,
    source_ref: str,
) -> dict[str, object]:
    return {
        "id": f"{skill_id}:bridge:{kind}:{_slug(value)}",
        "skill_id": skill_id,
        "name": value,
        "kind": kind,
        "value": value,
        "source": rule_id,
        "rule_id": rule_id,
        "path": skill_path,
        "source_path": skill_path,
        "confidence": confidence,
        "rationale": rationale,
        "source_scope": source_scope,
        "source_ref": source_ref,
    }


def _relationship_record(
    skill_id: str,
    rel_type: str,
    target: str,
    skill_path: str,
    rule_id: str,
    confidence: float,
    rationale: str,
    source_scope: str,
    source_ref: str,
) -> dict[str, object]:
    return {
        "source": skill_id,
        "type": rel_type,
        "target": target,
        "source_path": skill_path,
        "source_section_id": "",
        "mapping_rule_id": rule_id,
        "confidence": confidence,
        "rationale": rationale,
        "source_scope": source_scope,
        "source_ref": source_ref,
    }


def _relationship_key(relationship: Mapping[str, object]) -> tuple[str, str, str]:
    source = relationship.get("source")
    rel_type = relationship.get("type")
    target = relationship.get("target")
    return (
        source if isinstance(source, str) else "",
        rel_type if isinstance(rel_type, str) else "",
        target if isinstance(target, str) else "",
    )


def _required_string(rule: Mapping[str, object], field: str) -> str:
    value = rule.get(field)
    if not isinstance(value, str) or not value.strip():
        rule_id = rule.get("id") if isinstance(rule.get("id"), str) else "<unknown rule>"
        raise ValueError(f"{rule_id}: rule field {field} must be a non-empty string")
    return value.strip()


def _required_confidence(rule: Mapping[str, object]) -> float:
    value = rule.get("confidence")
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        rule_id = rule.get("id") if isinstance(rule.get("id"), str) else "<unknown rule>"
        raise ValueError(f"{rule_id}: confidence must be a number between 0 and 1")
    confidence = float(value)
    if not 0.0 <= confidence <= 1.0:
        rule_id = rule.get("id") if isinstance(rule.get("id"), str) else "<unknown rule>"
        raise ValueError(f"{rule_id}: confidence must be a number between 0 and 1")
    return confidence


def _validated_rules(
    rules: Mapping[str, object], rules_path: Path
) -> tuple[Mapping[str, object], ...]:
    if "category_rules" in rules or "skill_rules" in rules:
        raise ValueError(f"{rules_path}: legacy anonymous bridge rule maps are not supported")
    rule_values = rules.get("rules")
    if not isinstance(rule_values, list):
        raise ValueError(f"{rules_path}: rules must contain a JSON array named 'rules'")

    seen_ids: set[str] = set()
    validated: list[Mapping[str, object]] = []
    for index, rule_value in enumerate(rule_values):
        if not isinstance(rule_value, dict):
            raise ValueError(f"{rules_path}: rule at index {index} must be an object")
        rule = cast(Mapping[str, object], rule_value)
        missing = sorted(REQUIRED_RULE_FIELDS - set(rule))
        if missing:
            raise ValueError(f"{rules_path}: rule at index {index} missing {', '.join(missing)}")
        rule_id = _required_string(rule, "id")
        if rule_id in seen_ids:
            raise ValueError(f"{rules_path}: duplicate rule id {rule_id}")
        seen_ids.add(rule_id)
        scope = _required_string(rule, "scope")
        if scope not in ALLOWED_SCOPES:
            raise ValueError(f"{rule_id}: scope must be one of {sorted(ALLOWED_SCOPES)}")
        bridge_kind = _required_string(rule, "bridge_kind")
        if bridge_kind not in {*BRIDGE_KIND_TO_SKILL_FIELD, RELATIONSHIP_BRIDGE_KIND}:
            raise ValueError(f"{rule_id}: unsupported bridge_kind {bridge_kind}")
        _required_string(rule, "source")
        _required_string(rule, "bridge_value")
        _required_string(rule, "rationale")
        _required_confidence(rule)
        if bridge_kind == RELATIONSHIP_BRIDGE_KIND:
            _required_string(rule, "relationship_type")
        validated.append(rule)
    return tuple(validated)


def _apply_rule_to_skill(
    skill: dict[str, object],
    rule: Mapping[str, object],
    bridges_by_id: dict[str, dict[str, object]],
    relationships_by_key: dict[tuple[str, str, str], dict[str, object]],
) -> None:
    skill_id = skill["id"]
    skill_path = skill["path"]
    if not isinstance(skill_id, str) or not isinstance(skill_path, str):
        raise ValueError("skill must include string id and path")

    rule_id = _required_string(rule, "id")
    source_scope = _required_string(rule, "scope")
    source_ref = _required_string(rule, "source")
    bridge_kind = _required_string(rule, "bridge_kind")
    bridge_value = _required_string(rule, "bridge_value")
    confidence = _required_confidence(rule)
    rationale = _required_string(rule, "rationale")

    if bridge_kind == RELATIONSHIP_BRIDGE_KIND:
        relationship = _relationship_record(
            skill_id=skill_id,
            rel_type=_required_string(rule, "relationship_type"),
            target=bridge_value,
            skill_path=skill_path,
            rule_id=rule_id,
            confidence=confidence,
            rationale=rationale,
            source_scope=source_scope,
            source_ref=source_ref,
        )
        relationships_by_key[_relationship_key(relationship)] = relationship
        return

    field = BRIDGE_KIND_TO_SKILL_FIELD[bridge_kind]
    existing_values = skill.get(field)
    if not isinstance(existing_values, list):
        raise ValueError(f"{rule_id}: skill field {field} must be a list")
    _append_unique(existing_values, (bridge_value,))
    bridge = _bridge_record(
        skill_id=skill_id,
        kind=bridge_kind,
        value=bridge_value,
        skill_path=skill_path,
        rule_id=rule_id,
        confidence=confidence,
        rationale=rationale,
        source_scope=source_scope,
        source_ref=source_ref,
    )
    bridges_by_id[cast(str, bridge["id"])] = bridge


def _rule_applies_to_skill(skill: Mapping[str, object], rule: Mapping[str, object]) -> bool:
    source_scope = _required_string(rule, "scope")
    source_ref = _required_string(rule, "source")
    source_field = "category" if source_scope == "category" else "name"
    return skill.get(source_field) == source_ref


def _rules_for_skill(
    skill: Mapping[str, object],
    rules: Sequence[Mapping[str, object]],
) -> tuple[Mapping[str, object], ...]:
    return tuple(rule for rule in rules if _rule_applies_to_skill(skill, rule))


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

    explicit_rules = _validated_rules(cast(Mapping[str, object], rules), rules_path)
    bridges_by_id: dict[str, dict[str, object]] = {}
    relationships_by_key = {
        _relationship_key(cast(Mapping[str, object], relationship)): relationship
        for relationship in relationships
        if isinstance(relationship, dict)
    }

    for skill_value in skills:
        if not isinstance(skill_value, dict):
            continue
        skill = cast(dict[str, object], skill_value)
        for field in BRIDGE_KIND_TO_SKILL_FIELD.values():
            skill[field] = []
        for rule in _rules_for_skill(skill, explicit_rules):
            _apply_rule_to_skill(
                skill=skill,
                rule=rule,
                bridges_by_id=bridges_by_id,
                relationships_by_key=relationships_by_key,
            )

    mapped["bridges"] = [bridges_by_id[key] for key in sorted(bridges_by_id)]
    mapped["relationships"] = [relationships_by_key[key] for key in sorted(relationships_by_key)]
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
