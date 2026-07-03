#!/usr/bin/env python3
import itertools
import json
import os
import re
import sys
from collections import Counter

ROOT = "skills"
BASELINE_SKILL = os.path.join("skills", "apply-laws-of-ai", "SKILL.md")
PACK_METADATA = os.path.join("skills", "PACK_METADATA.json")
MIN_WORDS = 200
MIN_DESC_LEN = 80
MAX_DESC_LEN = 1024
WARN_SKILL_LINES = 500
MAX_SKILL_LINES = 600
SIMILARITY_FAIL = 0.82
WHEN_TRIGGER = re.compile(r"\buse when\b", re.I)
ALLOWED_FRONTMATTER_KEYS = {
    "name",
    "description",
    "aliases",
    "tags",
    "invocation_mode",
    "canonical_terms",
}
LIST_KEYS = {"aliases", "tags", "canonical_terms"}
INVOCATION_MODES = {"auto", "manual", "approval-required"}


def read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def parse_frontmatter(raw: str) -> dict[str, object]:
    data: dict[str, object] = {}
    current_key: str | None = None
    for line in raw.splitlines():
        if not line.strip():
            current_key = None
            continue
        if line.startswith("  - "):
            if current_key in LIST_KEYS:
                items = data.setdefault(current_key, [])
                assert isinstance(items, list)
                items.append(line[4:].strip())
            continue
        if line.startswith("  "):
            continue
        if ":" not in line:
            current_key = None
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key if key in LIST_KEYS and not value else None
        if key in LIST_KEYS:
            data[key] = (
                [] if not value else [item.strip() for item in value.split(",") if item.strip()]
            )
        else:
            data[key] = value
    return data


def tokenise_for_similarity(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [t for t in text.split() if len(t) > 3]


def cosine(counter_a: Counter[str], counter_b: Counter[str]) -> float:
    inter = set(counter_a) & set(counter_b)
    num: float = float(sum(counter_a[t] * counter_b[t] for t in inter))
    den_a: float = float(sum(v * v for v in counter_a.values()) ** 0.5)
    den_b: float = float(sum(v * v for v in counter_b.values()) ** 0.5)
    if not den_a or not den_b:
        return 0.0
    return num / (den_a * den_b)


def validate_pack_metadata(paths: list[str]) -> list[str]:
    errors: list[str] = []
    if not os.path.isfile(PACK_METADATA):
        errors.append(f"missing pack metadata file: {PACK_METADATA}")
        return errors

    try:
        metadata = json.loads(read(PACK_METADATA))
    except json.JSONDecodeError as exc:
        errors.append(f"{PACK_METADATA}: invalid JSON ({exc})")
        return errors

    if not isinstance(metadata, dict):
        errors.append(f"{PACK_METADATA}: root object must be a JSON object")
        return errors

    for key in (
        "schema_version",
        "skill_pack_id",
        "display_name",
        "version",
        "owner",
        "source_root",
        "categories",
    ):
        if key not in metadata:
            errors.append(f"{PACK_METADATA}: missing required field '{key}'")

    if metadata.get("schema_version") != "skill-pack-metadata/v1":
        errors.append(f"{PACK_METADATA}: schema_version must be 'skill-pack-metadata/v1'")
    if metadata.get("source_root") != ROOT:
        errors.append(f"{PACK_METADATA}: source_root must be '{ROOT}'")

    categories = metadata.get("categories", [])
    if not isinstance(categories, list) or not categories:
        errors.append(f"{PACK_METADATA}: categories must be a non-empty array")
        return errors

    expected_skills = {os.path.basename(os.path.dirname(path)) for path in paths}
    seen_category_ids: set[str] = set()
    seen_skills: dict[str, str] = {}

    for index, category in enumerate(categories):
        if not isinstance(category, dict):
            errors.append(f"{PACK_METADATA}: categories[{index}] must be an object")
            continue
        category_id = str(category.get("id", "")).strip()
        if not category_id:
            errors.append(f"{PACK_METADATA}: categories[{index}] missing id")
            continue
        if category_id in seen_category_ids:
            errors.append(f"{PACK_METADATA}: duplicate category id '{category_id}'")
        seen_category_ids.add(category_id)

        skills = category.get("skills", [])
        if not isinstance(skills, list) or not skills:
            errors.append(f"{PACK_METADATA}: category '{category_id}' must list at least one skill")
            continue
        for skill in skills:
            if not isinstance(skill, str) or not skill.strip():
                errors.append(
                    f"{PACK_METADATA}: category '{category_id}' contains an invalid skill entry"
                )
                continue
            skill_name = skill.strip()
            owner = seen_skills.get(skill_name)
            if owner and owner != category_id:
                errors.append(
                    f"{PACK_METADATA}: skill '{skill_name}' assigned to multiple categories "
                    f"('{owner}' and '{category_id}')"
                )
            else:
                seen_skills[skill_name] = category_id

    unknown_skills = sorted(set(seen_skills) - expected_skills)
    missing_skills = sorted(expected_skills - set(seen_skills))
    for skill_name in unknown_skills:
        errors.append(f"{PACK_METADATA}: unknown skill '{skill_name}' in categories")
    for skill_name in missing_skills:
        errors.append(f"{PACK_METADATA}: missing category assignment for skill '{skill_name}'")

    return errors


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not os.path.isfile(BASELINE_SKILL):
        errors.append(f"missing mandatory baseline skill: {BASELINE_SKILL}")

    paths: list[str] = []
    for dirpath, _, files in os.walk(ROOT):
        for name in files:
            if name == "SKILL.md":
                paths.append(os.path.join(dirpath, name))
    paths.sort()
    errors.extend(validate_pack_metadata(paths))

    skill_names = {os.path.basename(os.path.dirname(p)) for p in paths}
    alias_owners: dict[str, str] = {}
    vectors: dict[str, Counter[str]] = {}

    for p in paths:
        text = read(p)
        lines = text.splitlines()

        # Frontmatter checks
        if not text.startswith("---\n"):
            errors.append(f"{p}: missing YAML frontmatter start")
            continue
        fm_end = text.find("\n---\n", 4)
        if fm_end == -1:
            errors.append(f"{p}: missing YAML frontmatter end")
            continue
        fm = text[4:fm_end]
        parsed_fm = parse_frontmatter(fm)
        frontmatter_keys = set(parsed_fm)
        for key in sorted(frontmatter_keys - ALLOWED_FRONTMATTER_KEYS):
            errors.append(f"{p}: unsupported frontmatter key '{key}'")

        if not re.search(r"^name:\s*[-a-z0-9]+\s*$", fm, flags=re.M):
            errors.append(f"{p}: missing or invalid frontmatter name")
        if not re.search(r"^description:\s*.+$", fm, flags=re.M):
            errors.append(f"{p}: missing frontmatter description")
        else:
            desc_match = re.search(r"^description:\s*(.+)$", fm, flags=re.M)
            desc = desc_match.group(1).strip() if desc_match else ""
            if len(desc) < MIN_DESC_LEN:
                errors.append(f"{p}: description too short ({len(desc)} chars < {MIN_DESC_LEN})")
            if len(desc) > MAX_DESC_LEN:
                errors.append(f"{p}: description too long ({len(desc)} chars > {MAX_DESC_LEN})")
            if not WHEN_TRIGGER.search(desc):
                errors.append(f"{p}: description must include 'Use when' trigger phrase")

        folder_name = os.path.basename(os.path.dirname(p))

        aliases = parsed_fm.get("aliases", [])
        if aliases and not isinstance(aliases, list):
            errors.append(f"{p}: aliases must be a YAML list or comma-separated list")
        elif isinstance(aliases, list):
            for alias in aliases:
                if not re.fullmatch(r"[-a-z0-9 ]+", alias):
                    errors.append(
                        f"{p}: alias '{alias}' must use lowercase letters, digits, spaces or hyphens"
                    )
                owner = alias_owners.get(alias)
                if owner and owner != folder_name:
                    errors.append(f"{p}: alias '{alias}' already belongs to skill '{owner}'")
                elif alias in skill_names and alias != folder_name:
                    errors.append(f"{p}: alias '{alias}' collides with existing skill '{alias}'")
                else:
                    alias_owners[alias] = folder_name

        invocation_mode = parsed_fm.get("invocation_mode")
        if invocation_mode and invocation_mode not in INVOCATION_MODES:
            errors.append(
                f"{p}: invocation_mode '{invocation_mode}' must be one of {sorted(INVOCATION_MODES)}"
            )

        name_match = re.search(r"^name:\s*([-a-z0-9]+)\s*$", fm, flags=re.M)
        if name_match and name_match.group(1) != folder_name:
            errors.append(
                f"{p}: frontmatter name '{name_match.group(1)}' "
                f"does not match folder '{folder_name}'"
            )

        # Structural checks
        h1_count = sum(1 for ln in lines if ln.startswith("# "))
        if h1_count < 1:
            errors.append(f"{p}: missing level-1 heading")

        body_lower = text.lower()
        if not re.search(r"^## When to use\s*$", text, flags=re.M):
            errors.append(f"{p}: missing canonical '## When to use' section")
        if re.search(r"^## When to use this skill\s*$", text, flags=re.M):
            errors.append(f"{p}: use canonical heading '## When to use' (not 'this skill')")

        if not re.search(r"^## Objective\s*$", text, flags=re.M):
            errors.append(f"{p}: missing canonical '## Objective' section")
        if re.search(r"^## Goal\s*$", text, flags=re.M):
            errors.append(f"{p}: use canonical heading '## Objective' (not 'Goal')")

        if re.search(r"^## Operating procedure\s*$", text, flags=re.M):
            errors.append(f"{p}: use canonical heading '## Procedure' (not 'Operating procedure')")
        if re.search(r"^## Implementation pattern\s*$", text, flags=re.M):
            errors.append(
                f"{p}: use canonical heading '## Procedure' (not 'Implementation pattern')"
            )
        if re.search(r"^## Additional (guidance|guidelines)\s*$", text, flags=re.M):
            errors.append(f"{p}: remove generic Additional guidance/guidelines section")
        if "MAS DataOps MCP" in text or "DataOps-specific" in text:
            errors.append(f"{p}: move product-specific DataOps/MCP guidance to overlay docs")

        if not re.search(r"^## Verification\s*$", text, flags=re.M):
            errors.append(f"{p}: missing canonical '## Verification' section")
        if re.search(r"^## Completion report\s*$", text, flags=re.M):
            errors.append(f"{p}: use canonical heading '## Verification' (not 'Completion report')")
        if re.search(r"^## Output checklist\s*$", text, flags=re.M):
            errors.append(f"{p}: use canonical heading '## Verification' (not 'Output checklist')")

        ver_match = re.search(r"^## Verification\s*\n(.*?)(?=^## |\Z)", text, flags=re.S | re.M)
        if ver_match and not re.search(r"^- \[ \]", ver_match.group(1), flags=re.M):
            errors.append(f"{p}: Verification section must include at least one checklist item")

        related_match = re.search(
            r"^## Related skills\s*\n(.*?)(?=^## |\Z)", text, flags=re.S | re.M
        )
        if related_match:
            for ref in re.findall(r"`([-a-z0-9]+)`", related_match.group(1)):
                if ref not in skill_names:
                    errors.append(f"{p}: Related skills references unknown skill '{ref}'")

        word_count = len(re.findall(r"\b\w+\b", text))
        if p != BASELINE_SKILL and word_count < MIN_WORDS:
            errors.append(f"{p}: too short ({word_count} words < {MIN_WORDS})")
        if len(lines) > MAX_SKILL_LINES:
            errors.append(f"{p}: too long ({len(lines)} lines > {MAX_SKILL_LINES})")
        elif len(lines) > WARN_SKILL_LINES:
            warnings.append(f"{p}: large skill ({len(lines)} lines > {WARN_SKILL_LINES})")

        if "todo" in body_lower:
            errors.append(f"{p}: contains TODO placeholder")

        vectors[p] = Counter(tokenise_for_similarity(text))

    # Duplication checks
    for a, b in itertools.combinations(paths, 2):
        c = cosine(vectors[a], vectors[b])
        if c >= SIMILARITY_FAIL:
            errors.append(f"duplication risk: {a} <-> {b} similarity={c:.3f}")

    if errors:
        print("FAIL")
        for e in errors:
            print(f"- {e}")
        return 1

    for warning in warnings:
        print(f"WARN: {warning}")
    print(
        f"PASS: validated {len(paths)} skills; no structural or high-similarity duplication issues."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
