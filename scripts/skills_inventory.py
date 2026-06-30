#!/usr/bin/env python3
"""Shared discovery helpers for the flattened skills library."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILLS_ROOT = REPO_ROOT / "skills"
PACK_METADATA_FILENAME = "PACK_METADATA.json"
DEFAULT_PACK_METADATA_PATH = DEFAULT_SKILLS_ROOT / PACK_METADATA_FILENAME


def iter_skill_files(skills_root: Path = DEFAULT_SKILLS_ROOT) -> tuple[Path, ...]:
    """Return repository skill files in stable order.

    The library contract is a flat one-level layout: `skills/<skill>/SKILL.md`.
    """

    resolved_root = skills_root.resolve()
    return tuple(
        sorted(
            path
            for path in resolved_root.glob("*/SKILL.md")
            if path.is_file()
        )
    )


def _resolved_metadata_path(
    skills_root: Path = DEFAULT_SKILLS_ROOT,
    metadata_path: Path | None = None,
) -> Path:
    resolved_root = skills_root.resolve()
    candidate = metadata_path or (resolved_root / PACK_METADATA_FILENAME)
    return candidate.resolve()


def load_pack_metadata(
    skills_root: Path = DEFAULT_SKILLS_ROOT,
    metadata_path: Path | None = None,
) -> dict[str, object]:
    """Load machine-readable skill-pack metadata for flat-layout ingestion."""

    resolved_metadata_path = _resolved_metadata_path(skills_root, metadata_path)
    return json.loads(resolved_metadata_path.read_text(encoding="utf-8"))


def skill_category_map(
    skills_root: Path = DEFAULT_SKILLS_ROOT,
    metadata_path: Path | None = None,
) -> dict[str, str]:
    """Return a skill-name to semantic-category map from pack metadata."""

    metadata = load_pack_metadata(skills_root, metadata_path)
    mapping: dict[str, str] = {}
    for category in metadata.get("categories", []):
        if not isinstance(category, dict):
            continue
        category_id = str(category.get("id", "")).strip()
        if not category_id:
            continue
        skills = category.get("skills", [])
        if not isinstance(skills, list):
            continue
        for skill_name in skills:
            if isinstance(skill_name, str) and skill_name.strip():
                mapping[skill_name.strip()] = category_id
    return mapping


def category_for_skill_path(
    skill_path: Path,
    *,
    skills_root: Path = DEFAULT_SKILLS_ROOT,
    metadata_path: Path | None = None,
) -> str:
    """Resolve a semantic category for a skill path.

    Flat layouts recover category from explicit pack metadata.
    """

    resolved_root = skills_root.resolve()
    skill_name = skill_path.parent.name
    category = skill_category_map(resolved_root, metadata_path).get(skill_name, "")
    if category:
        return category
    raise ValueError(f"Unable to resolve category for skill '{skill_name}' from {skill_path}")
