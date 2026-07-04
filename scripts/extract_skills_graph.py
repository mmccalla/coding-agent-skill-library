#!/usr/bin/env python3
"""Extract repository skills into deterministic graph-ready records."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import skills_inventory, skills_mcp_perf
from scripts.skill_section_mapping import (
    ConstraintMapping,
    SkillDependencyMapping,
    SkillSectionMapping,
    TaskIntentMapping,
    extract_section,
    map_skill_sections,
    promotion_ready_task_intents,
)
from scripts.validate_skill_security import DEFAULT_ALLOWLIST
from scripts.validate_skill_trust import TrustReport, validate_skill_trust_file

PROMOTION_STATUSES = frozenset({"promoted", "quarantined", "rejected"})
DEPENDENCY_TYPE_TO_RELATIONSHIP = {
    "precedes": "PRECEDES",
    "validates": "VALIDATES",
    "complements": "COMPLEMENTS",
}
# Phase 9 will wire full CI trust gates for all library skills. Until then,
# grandfather_practice_waiver=True keeps legacy L3 practice failures quarantined
# rather than rejected so existing graph extraction tests remain stable.
DEFAULT_GRANDFATHER_PRACTICE_WAIVER = True

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


class SkillSection(NamedTuple):
    """A canonical markdown section extracted from a skill."""

    id: str
    skill_id: str
    name: str
    heading: str
    level: int
    order: int
    contentHash: str
    text: str
    heading_path: str
    line_start: int
    line_end: int
    char_start: int
    char_end: int


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "section"


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


def _relative_source_path(path: Path, skills_root: Path) -> str:
    return path.relative_to(skills_root.parent).as_posix()


def _frontmatter_value(text: str, key: str, source_path: str) -> str:
    if not text.startswith("---\n"):
        raise ValueError(f"{source_path}: missing YAML frontmatter start")
    frontmatter_end = text.find("\n---\n", 4)
    if frontmatter_end == -1:
        raise ValueError(f"{source_path}: missing YAML frontmatter end")
    frontmatter = text[4:frontmatter_end]
    match = re.search(rf"^{re.escape(key)}:[ \t]*([^\n]+)$", frontmatter, flags=re.M)
    return match.group(1).strip() if match else ""


def _frontmatter_values(text: str, key: str, source_path: str) -> tuple[str, ...]:
    if not text.startswith("---\n"):
        raise ValueError(f"{source_path}: missing YAML frontmatter start")
    frontmatter_end = text.find("\n---\n", 4)
    if frontmatter_end == -1:
        raise ValueError(f"{source_path}: missing YAML frontmatter end")
    frontmatter = text[4:frontmatter_end]
    match = re.search(rf"^{re.escape(key)}:[ \t]*([^\n]+)$", frontmatter, flags=re.M)
    if match:
        raw_value = match.group(1).strip()
        return (raw_value,) if raw_value else ()
    block_match = re.search(
        rf"^{re.escape(key)}:\s*$\n((?:  - .+\n?)*)",
        frontmatter,
        flags=re.M,
    )
    if not block_match:
        return ()
    return _unique(
        tuple(
            line.strip()[2:].strip()
            for line in block_match.group(1).splitlines()
            if line.strip().startswith("- ")
        )
    )


def _section_text(text: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)",
        text,
        flags=re.M | re.S,
    )
    return match.group(1) if match else ""


def _title(text: str) -> str:
    match = re.search(r"^#\s+(.+?)\s*$", text, flags=re.M)
    return match.group(1).strip() if match else ""


def _extract_sections(text: str, skill_id: str) -> tuple[SkillSection, ...]:
    matches = list(re.finditer(r"^(#{2,6})\s+(.+?)\s*$", text, flags=re.M))
    sections: list[SkillSection] = []
    heading_stack: list[str] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        heading = match.group(2).strip()
        level = len(match.group(1))
        content = text[start:end].strip()
        stack_index = max(0, level - 2)
        heading_stack = heading_stack[:stack_index]
        heading_stack.append(heading)
        content_start = start
        while content_start < len(text) and text[content_start] in {"\n", "\r"}:
            content_start += 1
        content_end = end
        while content_end > content_start and text[content_end - 1] in {"\n", "\r"}:
            content_end -= 1
        anchor_start = content_start if content else match.start()
        anchor_end = max(anchor_start, content_end if content else match.end())
        line_start = text.count("\n", 0, anchor_start) + 1
        line_end = text.count("\n", 0, max(anchor_start, anchor_end - 1)) + 1
        sections.append(
            SkillSection(
                id=f"{skill_id}:section:{index}-{_slug(heading)}",
                skill_id=skill_id,
                name=heading,
                heading=heading,
                level=level,
                order=index,
                contentHash=_sha256(content),
                text=content,
                heading_path=" > ".join(heading_stack),
                line_start=line_start,
                line_end=line_end,
                char_start=anchor_start,
                char_end=anchor_end,
            )
        )
    return tuple(sections)


def _related_skill_names(text: str, known_skill_names: set[str]) -> tuple[str, ...]:
    related_section = _section_text(text, "Related skills")
    return _unique(
        tuple(
            name
            for name in re.findall(r"`([-a-z0-9]+)`", related_section)
            if name in known_skill_names
        )
    )


def _workflow_stages(profile_text: str) -> tuple[str, ...]:
    lowered = profile_text.lower()
    stages: list[str] = []
    stage_keywords = (
        ("startup", ("session start", "startup", "baseline", "mandatory")),
        ("routing", ("routing", "discover", "select", "choose")),
        ("planning", ("plan", "spec", "decomposition", "roadmap")),
        ("design", ("design", "model", "architecture", "schema")),
        ("implementation", ("implement", "build", "create", "refactor", "code")),
        ("validation", ("test", "validate", "verification", "review", "evaluate")),
        ("release", ("release", "ship", "deploy", "ci/cd", "launch")),
        ("operations", ("monitor", "incident", "observability", "slo", "toil")),
    )
    for stage, keywords in stage_keywords:
        if any(keyword in lowered for keyword in keywords):
            stages.append(stage)
    if not stages:
        stages.append("execution")
    return _unique(stages)


def _task_shapes(name: str, description: str, aliases: Sequence[str]) -> tuple[str, ...]:
    description_tokens = _slug_tokens(description)
    name_tokens = _slug_tokens(name)
    alias_tokens: list[str] = []
    for alias in aliases:
        alias_tokens.extend(_slug_tokens(alias))
    return _unique((*name_tokens[:3], *alias_tokens[:4], *description_tokens[:6]))


def _capabilities(
    name: str,
    description: str,
    aliases: Sequence[str],
) -> tuple[str, ...]:
    alias_tokens: list[str] = []
    for alias in aliases:
        alias_tokens.extend(_slug_tokens(alias))
    return _unique(
        (
            *_slug_tokens(name),
            *alias_tokens[:6],
            *_slug_tokens(description)[:4],
        )
    )


def _reference_records(
    text: str,
    skill_id: str,
    source_path: str,
) -> list[dict[str, object]]:
    references: list[dict[str, object]] = []
    seen_targets: set[str] = set()
    index = 0
    for match in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
        target = match.group(2).strip()
        if target in seen_targets:
            continue
        seen_targets.add(target)
        references.append(
            {
                "id": f"{skill_id}:reference:{index}",
                "skill_id": skill_id,
                "label": match.group(1),
                "target": target,
                "source_path": source_path,
            }
        )
        index += 1
    for match in re.finditer(r"(?<!\()(https?://[^\s\)\]]+)", text):
        target = match.group(1).rstrip(".,;")
        if target in seen_targets:
            continue
        seen_targets.add(target)
        references.append(
            {
                "id": f"{skill_id}:reference:{index}",
                "skill_id": skill_id,
                "label": target,
                "target": target,
                "source_path": source_path,
            }
        )
        index += 1
    return references


def _standards_references(text: str) -> list[str]:
    """Extract primary-source http(s) URLs for ontology skills:standardsReference."""
    urls: list[str] = []
    seen: set[str] = set()
    for match in re.finditer(r"https?://[^\s\)\]]+", text):
        url = match.group(0).rstrip(".,;")
        if url in seen:
            continue
        seen.add(url)
        urls.append(url)
    return urls


def _bridge_record(
    skill_id: str,
    kind: str,
    value: str,
    source_path: str,
    source: str,
    confidence: float,
    rationale: str,
    source_scope: str,
    source_ref: str,
    *,
    mapping_source: str = "",
    evidence_line_start: int | None = None,
    evidence_line_end: int | None = None,
) -> dict[str, object]:
    bridge_id = f"{skill_id}:bridge:{kind}:{_slug(value)}"
    record: dict[str, object] = {
        "id": bridge_id,
        "skill_id": skill_id,
        "name": value,
        "kind": kind,
        "value": value,
        "source": bridge_id,
        "rule_id": bridge_id,
        "path": source_path,
        "source_path": source_path,
        "confidence": confidence,
        "rationale": rationale,
        "source_scope": source_scope,
        "source_ref": source_ref,
    }
    if mapping_source:
        record["mapping_source"] = mapping_source
    if evidence_line_start is not None:
        record["evidence_line_start"] = evidence_line_start
    if evidence_line_end is not None:
        record["evidence_line_end"] = evidence_line_end
    return record


def _mapping_task_intent_bridge(
    skill_id: str,
    mapping: TaskIntentMapping,
    source_path: str,
) -> dict[str, object]:
    return _bridge_record(
        skill_id=skill_id,
        kind="task_shape",
        value=mapping.task_intent_id,
        source_path=source_path,
        source=f"{skill_id}:mapping:task_intent:{mapping.task_intent_id}",
        confidence=mapping.confidence,
        rationale=(
            f"Mapped from '{mapping.section_heading}' via phrase '{mapping.matched_phrase}' "
            f"(source={mapping.mapping_source})."
        ),
        source_scope="section" if mapping.section_heading != "skill_registry" else "skill",
        source_ref=mapping.section_heading,
        mapping_source=mapping.mapping_source,
        evidence_line_start=mapping.evidence.line_start,
        evidence_line_end=mapping.evidence.line_end,
    )


def _mapping_constraint_bridge(
    skill_id: str,
    mapping: ConstraintMapping,
    source_path: str,
) -> dict[str, object]:
    return _bridge_record(
        skill_id=skill_id,
        kind="invocation_condition",
        value=mapping.constraint_id,
        source_path=source_path,
        source=f"{skill_id}:mapping:constraint:{mapping.constraint_id}",
        confidence=0.95,
        rationale=(
            f"Mapped from '{mapping.section_heading}' via phrase '{mapping.matched_phrase}'."
        ),
        source_scope="section",
        source_ref=mapping.section_heading,
        mapping_source="when_not_to_use",
        evidence_line_start=mapping.evidence.line_start,
        evidence_line_end=mapping.evidence.line_end,
    )


def _task_intent_records(
    mappings: Sequence[TaskIntentMapping],
) -> list[dict[str, object]]:
    return [
        {
            "task_intent_id": mapping.task_intent_id,
            "matched_phrase": mapping.matched_phrase,
            "section_heading": mapping.section_heading,
            "evidence_line_start": mapping.evidence.line_start,
            "evidence_line_end": mapping.evidence.line_end,
            "mapping_source": mapping.mapping_source,
            "confidence": mapping.confidence,
        }
        for mapping in mappings
    ]


def _constraint_records(
    mappings: Sequence[ConstraintMapping],
) -> list[dict[str, object]]:
    return [
        {
            "constraint_id": mapping.constraint_id,
            "matched_phrase": mapping.matched_phrase,
            "section_heading": mapping.section_heading,
            "evidence_line_start": mapping.evidence.line_start,
            "evidence_line_end": mapping.evidence.line_end,
        }
        for mapping in mappings
    ]


def _resolve_promotion_status(
    trust_report: TrustReport | None,
    section_mapping: SkillSectionMapping,
    *,
    trust_gate: bool,
    grandfather_practice_waiver: bool,
) -> str:
    if not trust_gate:
        if promotion_ready_task_intents(section_mapping.task_intents):
            return "promoted"
        return "quarantined"

    assert trust_report is not None
    if not trust_report.layers["L2_security"].passed:
        return "rejected"
    if not trust_report.layers["L3_practice"].passed:
        if grandfather_practice_waiver:
            return "quarantined"
        return "rejected"
    if not promotion_ready_task_intents(section_mapping.task_intents):
        return "quarantined"
    return "promoted"


def _mapping_bridge_records(
    skill_id: str,
    source_path: str,
    section_mapping: SkillSectionMapping,
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for task_mapping in section_mapping.task_intents:
        records.append(_mapping_task_intent_bridge(skill_id, task_mapping, source_path))
    for constraint_mapping in section_mapping.constraints:
        records.append(_mapping_constraint_bridge(skill_id, constraint_mapping, source_path))
    return records


def _mapping_relationship_records(
    skill_id: str,
    source_path: str,
    dependencies: Sequence[SkillDependencyMapping],
) -> list[dict[str, object]]:
    relationships: list[dict[str, object]] = []
    for dependency in dependencies:
        relationship_type = DEPENDENCY_TYPE_TO_RELATIONSHIP.get(
            dependency.dependency_type,
            "COMPLEMENTS",
        )
        mapping_rule_id = (
            f"{skill_id}:mapping:dependency:{dependency.dependency_type}:"
            f"{dependency.target_skill_id}"
        )
        relationships.append(
            {
                "source": skill_id,
                "type": relationship_type,
                "target": f"skill:{dependency.target_skill_id}",
                "source_path": source_path,
                "mapping_rule_id": mapping_rule_id,
                "confidence": 0.95,
                "rationale": dependency.rationale,
                "source_scope": "section",
                "source_ref": dependency.section_heading,
                "evidence_line_start": dependency.evidence.line_start,
                "evidence_line_end": dependency.evidence.line_end,
            }
        )
    return relationships


def _unmapped_dependency_relationship(
    skill_id: str,
    related_name: str,
    source_path: str,
    markdown: str,
) -> dict[str, object]:
    section = extract_section(markdown, "Related skills")
    line_start = section.line_start if section else 1
    line_end = line_start
    rationale = f"Related skill `{related_name}` referenced in Related skills."
    if section and section.text:
        match = re.search(rf"`{re.escape(related_name)}`", section.text)
        if match:
            line_start = section.line_start + section.text[: match.start()].count("\n")
            line_end = section.line_start + section.text[: match.end()].count("\n")
            for line in section.text.splitlines():
                if f"`{related_name}`" in line:
                    cleaned = line.strip()
                    if cleaned.startswith("|"):
                        cleaned = cleaned.strip("|").strip()
                    elif cleaned.startswith("-"):
                        cleaned = cleaned.lstrip("-").strip()
                    if cleaned:
                        rationale = cleaned
                    break

    return {
        "source": skill_id,
        "type": "COMPLEMENTS",
        "target": f"skill:{related_name}",
        "source_path": source_path,
        "mapping_rule_id": f"{skill_id}:mapping:dependency:complements:{related_name}",
        "confidence": 0.7,
        "rationale": rationale,
        "source_scope": "section",
        "source_ref": "Related skills",
        "evidence_line_start": line_start,
        "evidence_line_end": line_end,
    }


def _bridge_records(
    skill_id: str,
    source_path: str,
    task_shapes: Sequence[str],
    workflow_stages: Sequence[str],
    capabilities: Sequence[str],
    control_themes: Sequence[str],
    knowledge_domains: Sequence[str],
) -> list[dict[str, object]]:
    bridge_specs = (
        (
            "task_shape",
            task_shapes,
            "name_and_description",
            0.8,
            "Derived from the skill name, aliases and description.",
            "skill",
        ),
        (
            "workflow_stage",
            workflow_stages,
            "name_and_description",
            0.7,
            "Derived from workflow-stage keywords in the skill name and description.",
            "skill",
        ),
        (
            "capability",
            capabilities,
            "name_and_description",
            0.75,
            "Derived from the skill name, aliases and description.",
            "skill",
        ),
        (
            "control_theme",
            control_themes,
            "category",
            0.9,
            "Derived from explicit pack metadata category assignment.",
            "category",
        ),
        (
            "knowledge_domain",
            knowledge_domains,
            "category",
            0.9,
            "Derived from explicit pack metadata category assignment.",
            "category",
        ),
    )
    records: list[dict[str, object]] = []
    for kind, values, source, confidence, rationale, source_scope in bridge_specs:
        for value in values:
            records.append(
                _bridge_record(
                    skill_id=skill_id,
                    kind=kind,
                    value=value,
                    source_path=source_path,
                    source=source,
                    confidence=confidence,
                    rationale=rationale,
                    source_scope=source_scope,
                    source_ref=skill_id.removeprefix("skill:")
                    if source_scope == "skill"
                    else value,
                )
            )
    return records


def extract_skills_graph_records(
    skills_root: Path,
    *,
    trust_gate: bool = True,
    grandfather_practice_waiver: bool = DEFAULT_GRANDFATHER_PRACTICE_WAIVER,
    allowlist_path: str | Path = DEFAULT_ALLOWLIST,
) -> dict[str, object]:
    """Extract all `SKILL.md` files under `skills_root` into graph records."""

    resolved_root = skills_root.resolve()
    skill_paths = list(skills_inventory.iter_skill_files(resolved_root))
    pack_metadata_path = resolved_root / skills_inventory.PACK_METADATA_FILENAME
    pack_metadata = (
        skills_inventory.load_pack_metadata(resolved_root, pack_metadata_path)
        if pack_metadata_path.is_file()
        else None
    )
    known_skill_names = {path.parent.name for path in skill_paths}
    skills: list[dict[str, object]] = []
    sections: list[dict[str, object]] = []
    relationships: list[dict[str, object]] = []
    references: list[dict[str, object]] = []
    bridges: list[dict[str, object]] = []
    pack_hash_inputs: list[str] = []

    for path in skill_paths:
        with skills_mcp_perf.disk_io() as io:
            text = path.read_text(encoding="utf-8")
            io.add(len(text.encode("utf-8")))
        source_path = _relative_source_path(path, resolved_root)
        pack_hash_inputs.append(f"{source_path}\n{text}")
        name = _frontmatter_value(text, "name", source_path) or path.parent.name
        aliases = _frontmatter_values(text, "aliases", source_path)
        category = skills_inventory.category_for_skill_path(
            path,
            skills_root=resolved_root,
            metadata_path=pack_metadata_path if pack_metadata_path.is_file() else None,
        )
        description = _frontmatter_value(text, "description", source_path)
        skill_id = f"skill:{name}"
        content_hash = _sha256(text)
        lines = text.splitlines()
        skill_sections = _extract_sections(text, skill_id)
        section_mapping = map_skill_sections(
            text, skill_name=name, known_skill_ids=known_skill_names
        )
        mapped_dependencies = section_mapping.dependencies
        mapped_dependency_targets = {
            f"skill:{dependency.target_skill_id}" for dependency in mapped_dependencies
        }
        related_names = _related_skill_names(text, known_skill_names)
        mapped_task_intent_ids = tuple(
            mapping.task_intent_id for mapping in section_mapping.task_intents
        )
        task_shapes = _unique((*mapped_task_intent_ids, *_task_shapes(name, description, aliases)))
        workflow_stages = _workflow_stages(f"{name} {description}")
        capabilities = _capabilities(name, description, aliases)
        control_themes = (category,) if category else ()
        knowledge_domains = (category,) if category else ()
        trust_report = (
            validate_skill_trust_file(str(path), allowlist_path=allowlist_path)
            if trust_gate
            else None
        )
        promotion_status = _resolve_promotion_status(
            trust_report,
            section_mapping,
            trust_gate=trust_gate,
            grandfather_practice_waiver=grandfather_practice_waiver,
        )

        skills.append(
            {
                "id": skill_id,
                "name": name,
                "aliases": list(aliases),
                "title": _title(text),
                "description": description,
                "category": category,
                "task_shapes": list(task_shapes),
                "workflow_stages": list(workflow_stages),
                "capabilities": list(capabilities),
                "control_themes": list(control_themes),
                "knowledge_domains": list(knowledge_domains),
                "related_skill_ids": [f"skill:{related_name}" for related_name in related_names],
                "supported_task_intents": _task_intent_records(section_mapping.task_intents),
                "excluded_constraints": _constraint_records(section_mapping.constraints),
                "promotion_status": promotion_status,
                "path": source_path,
                "skill_pack_id": str(pack_metadata.get("skill_pack_id", "")).strip()
                if isinstance(pack_metadata, dict)
                else "",
                "skill_pack_version": str(pack_metadata.get("version", "")).strip()
                if isinstance(pack_metadata, dict)
                else "",
                "contentHash": content_hash,
                "wordCount": len(re.findall(r"\b\w+\b", text)),
                "lineCount": len(lines),
                "isBaselineSkill": name == "apply-laws-of-ai",
                "standardsReferences": _standards_references(text),
            }
        )
        sections.extend(section._asdict() for section in skill_sections)
        references.extend(_reference_records(text, skill_id, source_path))
        mapping_bridges = _mapping_bridge_records(skill_id, source_path, section_mapping)
        heuristic_bridges = _bridge_records(
            skill_id=skill_id,
            source_path=source_path,
            task_shapes=task_shapes,
            workflow_stages=workflow_stages,
            capabilities=capabilities,
            control_themes=control_themes,
            knowledge_domains=knowledge_domains,
        )
        mapped_bridge_ids = {str(bridge["id"]) for bridge in mapping_bridges}
        bridges.extend(mapping_bridges)
        bridges.extend(
            bridge for bridge in heuristic_bridges if str(bridge["id"]) not in mapped_bridge_ids
        )

        relationships.extend(
            _mapping_relationship_records(skill_id, source_path, mapped_dependencies)
        )
        for related_name in related_names:
            related_target = f"skill:{related_name}"
            if related_target in mapped_dependency_targets:
                continue
            relationships.append(
                _unmapped_dependency_relationship(
                    skill_id,
                    related_name,
                    source_path,
                    text,
                )
            )

    skill_pack: dict[str, object] | None = None
    if isinstance(pack_metadata, dict):
        with skills_mcp_perf.disk_io() as io:
            metadata_text = pack_metadata_path.read_text(encoding="utf-8")
            io.add(len(metadata_text.encode("utf-8")))
        pack_content_hash = _sha256("\n".join((metadata_text, *sorted(pack_hash_inputs))))
        category_ids: list[str] = []
        categories_raw = pack_metadata.get("categories", [])
        if isinstance(categories_raw, list):
            for category in categories_raw:
                if isinstance(category, dict) and isinstance(category.get("id"), str):
                    category_ids.append(category["id"])
        skill_pack = {
            "id": str(pack_metadata.get("skill_pack_id", "")).strip(),
            "name": str(pack_metadata.get("display_name", "")).strip(),
            "version": str(pack_metadata.get("version", "")).strip(),
            "owner": str(pack_metadata.get("owner", "")).strip(),
            "source_root": str(pack_metadata.get("source_root", "")).strip(),
            "contentHash": pack_content_hash,
            "categories": category_ids,
            "skillCount": len(skills),
        }

    return {
        "root_skill": "apply-laws-of-ai",
        "skill_pack": skill_pack,
        "skills": skills,
        "sections": sections,
        "relationships": relationships,
        "references": references,
        "bridges": bridges,
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) > 1:
        print("Usage: extract_skills_graph.py [skills-root]")
        return 2

    skills_root = Path(args[0]) if args else Path("skills")
    records = extract_skills_graph_records(skills_root)
    print(json.dumps(records, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
