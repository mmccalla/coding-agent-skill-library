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
    value = _frontmatter_values(text, key, source_path)
    return value[0] if value else ""


def _frontmatter_values(text: str, key: str, source_path: str) -> tuple[str, ...]:
    if not text.startswith("---\n"):
        raise ValueError(f"{source_path}: missing YAML frontmatter start")
    frontmatter_end = text.find("\n---\n", 4)
    if frontmatter_end == -1:
        raise ValueError(f"{source_path}: missing YAML frontmatter end")
    frontmatter = text[4:frontmatter_end]
    match = re.search(rf"^{re.escape(key)}:[ \t]*([^\n]+)$", frontmatter, flags=re.M)
    if match:
        return _unique(tuple(item.strip() for item in match.group(1).split(",") if item.strip()))
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
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        heading = match.group(2).strip()
        content = text[start:end].strip()
        sections.append(
            SkillSection(
                id=f"{skill_id}:section:{index}-{_slug(heading)}",
                skill_id=skill_id,
                name=heading,
                heading=heading,
                level=len(match.group(1)),
                order=index,
                contentHash=_sha256(content),
                text=content,
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
    category: str,
    description: str,
    aliases: Sequence[str],
) -> tuple[str, ...]:
    alias_tokens: list[str] = []
    for alias in aliases:
        alias_tokens.extend(_slug_tokens(alias))
    return _unique(
        (*_slug_tokens(name), *alias_tokens[:6], *_slug_tokens(category), *_slug_tokens(description)[:4])
    )


def _section_id_for_heading(sections: Sequence[SkillSection], heading: str) -> str:
    for section in sections:
        if section.heading == heading:
            return section.id
    return ""


def _reference_records(
    text: str,
    skill_id: str,
    source_path: str,
) -> list[dict[str, object]]:
    references: list[dict[str, object]] = []
    for index, match in enumerate(re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text)):
        references.append(
            {
                "id": f"{skill_id}:reference:{index}",
                "skill_id": skill_id,
                "label": match.group(1),
                "target": match.group(2),
                "source_path": source_path,
            }
        )
    return references


def _bridge_record(
    skill_id: str,
    kind: str,
    value: str,
    source_path: str,
    source: str,
    confidence: float,
) -> dict[str, object]:
    return {
        "id": f"{skill_id}:bridge:{kind}:{_slug(value)}",
        "skill_id": skill_id,
        "name": value,
        "kind": kind,
        "value": value,
        "source": source,
        "path": source_path,
        "source_path": source_path,
        "confidence": confidence,
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
        ("task_shape", task_shapes, "name_and_description", 0.8),
        ("workflow_stage", workflow_stages, "name_and_description", 0.7),
        ("capability", capabilities, "name_category_description", 0.75),
        ("control_theme", control_themes, "category", 0.9),
        ("knowledge_domain", knowledge_domains, "category", 0.9),
    )
    records: list[dict[str, object]] = []
    for kind, values, source, confidence in bridge_specs:
        for value in values:
            records.append(
                _bridge_record(
                    skill_id=skill_id,
                    kind=kind,
                    value=value,
                    source_path=source_path,
                    source=source,
                    confidence=confidence,
                )
            )
    return records


def extract_skills_graph_records(skills_root: Path) -> dict[str, object]:
    """Extract all `SKILL.md` files under `skills_root` into graph records."""

    resolved_root = skills_root.resolve()
    skill_paths = sorted(resolved_root.rglob("SKILL.md"))
    known_skill_names = {path.parent.name for path in skill_paths}
    skills: list[dict[str, object]] = []
    sections: list[dict[str, object]] = []
    relationships: list[dict[str, object]] = []
    references: list[dict[str, object]] = []
    bridges: list[dict[str, object]] = []

    for path in skill_paths:
        text = path.read_text(encoding="utf-8")
        source_path = _relative_source_path(path, resolved_root)
        name = _frontmatter_value(text, "name", source_path) or path.parent.name
        aliases = _frontmatter_values(text, "aliases", source_path)
        category = path.parent.parent.name
        description = _frontmatter_value(text, "description", source_path)
        skill_id = f"skill:{name}"
        content_hash = _sha256(text)
        lines = text.splitlines()
        skill_sections = _extract_sections(text, skill_id)
        related_names = _related_skill_names(text, known_skill_names)
        related_section_id = _section_id_for_heading(skill_sections, "Related skills")
        task_shapes = _task_shapes(name, description, aliases)
        workflow_stages = _workflow_stages(f"{name} {description}")
        capabilities = _capabilities(name, category, description, aliases)
        control_themes = (category,)
        knowledge_domains = (category,)

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
                "path": source_path,
                "contentHash": content_hash,
                "wordCount": len(re.findall(r"\b\w+\b", text)),
                "lineCount": len(lines),
                "isBaselineSkill": name == "apply-laws-of-ai",
            }
        )
        sections.extend(section._asdict() for section in skill_sections)
        references.extend(_reference_records(text, skill_id, source_path))
        bridges.extend(
            _bridge_records(
                skill_id=skill_id,
                source_path=source_path,
                task_shapes=task_shapes,
                workflow_stages=workflow_stages,
                capabilities=capabilities,
                control_themes=control_themes,
                knowledge_domains=knowledge_domains,
            )
        )

        for related_name in related_names:
            relationships.append(
                {
                    "source": skill_id,
                    "type": "RELATED_TO",
                    "target": f"skill:{related_name}",
                    "source_path": source_path,
                    "source_section_id": related_section_id,
                }
            )

    return {
        "root_skill": "apply-laws-of-ai",
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
