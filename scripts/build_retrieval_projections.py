#!/usr/bin/env python3
"""Build retrieval projections for promoted skills only."""

from __future__ import annotations

import sys
from collections import Counter
from collections.abc import Mapping
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

PROMOTED_STATUS = "promoted"


def _records_list(records: Mapping[str, object], key: str) -> list[dict[str, object]]:
    value = records.get(key)
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _promoted_skill_ids(records: Mapping[str, object]) -> set[str]:
    return {
        str(skill["id"])
        for skill in _records_list(records, "skills")
        if skill.get("promotion_status") == PROMOTED_STATUS
    }


def filter_promoted_records(records: Mapping[str, object]) -> dict[str, object]:
    """Return promoted skills and their dependent graph records."""

    promoted_ids = _promoted_skill_ids(records)
    filtered: dict[str, object] = dict(records)
    filtered["skills"] = [
        skill for skill in _records_list(records, "skills") if str(skill.get("id")) in promoted_ids
    ]
    filtered["sections"] = [
        section
        for section in _records_list(records, "sections")
        if str(section.get("skill_id")) in promoted_ids
    ]
    filtered["bridges"] = [
        bridge
        for bridge in _records_list(records, "bridges")
        if str(bridge.get("skill_id")) in promoted_ids
    ]
    filtered["references"] = [
        reference
        for reference in _records_list(records, "references")
        if str(reference.get("skill_id")) in promoted_ids
    ]
    filtered["relationships"] = [
        relationship
        for relationship in _records_list(records, "relationships")
        if str(relationship.get("source")) in promoted_ids
        and str(relationship.get("target")) in promoted_ids
    ]
    return filtered


def build_retrieval_projection_records(
    records: Mapping[str, object],
) -> list[dict[str, object]]:
    """Build RetrievalUnit property records for promoted skills only."""

    from scripts import load_skills_neo4j

    promoted_records = filter_promoted_records(records)
    skills_by_id = {str(skill["id"]): skill for skill in _records_list(promoted_records, "skills")}
    units: list[dict[str, object]] = []
    for section in _records_list(promoted_records, "sections"):
        skill_id = str(section.get("skill_id"))
        retrieval_unit = load_skills_neo4j._retrieval_unit_from_section(
            section,
            skills_by_id.get(skill_id, {}),
        )
        units.append({"id": retrieval_unit.id, **dict(retrieval_unit.properties)})
    return units


def build_retrieval_projections(records: Mapping[str, object]) -> dict[str, object]:
    """Return promoted skills, retrieval units and a promotion status summary."""

    promoted_records = filter_promoted_records(records)
    status_counts = Counter(
        str(skill.get("promotion_status", "unknown")) for skill in _records_list(records, "skills")
    )
    return {
        "skills": promoted_records["skills"],
        "retrieval_units": build_retrieval_projection_records(records),
        "promotion_summary": dict(sorted(status_counts.items())),
    }
