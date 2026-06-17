#!/usr/bin/env python3
import os
import re
import sys
import itertools
from collections import Counter

ROOT = "skills"
BASELINE_SKILL = os.path.join("skills", "agent-control-patterns", "apply-laws-of-ai", "SKILL.md")
MIN_WORDS = 140
MIN_DESC_LEN = 80
MAX_DESC_LEN = 1024
SIMILARITY_FAIL = 0.82
WHEN_TRIGGER = re.compile(r"\buse when\b", re.I)


def read(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def tokenise_for_similarity(text: str):
    text = text.lower()
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [t for t in text.split() if len(t) > 3]


def cosine(counter_a: Counter, counter_b: Counter) -> float:
    inter = set(counter_a) & set(counter_b)
    num = sum(counter_a[t] * counter_b[t] for t in inter)
    den_a = sum(v * v for v in counter_a.values()) ** 0.5
    den_b = sum(v * v for v in counter_b.values()) ** 0.5
    if not den_a or not den_b:
        return 0.0
    return num / (den_a * den_b)


def main() -> int:
    errors = []

    if not os.path.isfile(BASELINE_SKILL):
        errors.append(f"missing mandatory baseline skill: {BASELINE_SKILL}")

    paths = []
    for dirpath, _, files in os.walk(ROOT):
        for name in files:
            if name == "SKILL.md":
                paths.append(os.path.join(dirpath, name))
    paths.sort()

    skill_names = {os.path.basename(os.path.dirname(p)) for p in paths}
    vectors = {}

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

        if not re.search(r"^name:\s*[-a-z0-9]+\s*$", fm, flags=re.M):
            errors.append(f"{p}: missing or invalid frontmatter name")
        if not re.search(r"^description:\s*.+$", fm, flags=re.M):
            errors.append(f"{p}: missing frontmatter description")
        else:
            desc_match = re.search(r"^description:\s*(.+)$", fm, flags=re.M)
            desc = desc_match.group(1).strip() if desc_match else ""
            if len(desc) < MIN_DESC_LEN:
                errors.append(
                    f"{p}: description too short ({len(desc)} chars < {MIN_DESC_LEN})"
                )
            if len(desc) > MAX_DESC_LEN:
                errors.append(
                    f"{p}: description too long ({len(desc)} chars > {MAX_DESC_LEN})"
                )
            if not WHEN_TRIGGER.search(desc):
                errors.append(
                    f"{p}: description must include 'Use when' trigger phrase"
                )

        folder_name = os.path.basename(os.path.dirname(p))
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
            errors.append(f"{p}: use canonical heading '## Procedure' (not 'Implementation pattern')")
        if re.search(r"^## Additional (guidance|guidelines)\s*$", text, flags=re.M):
            errors.append(f"{p}: remove generic Additional guidance/guidelines section")

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
        if word_count < MIN_WORDS:
            errors.append(f"{p}: too short ({word_count} words < {MIN_WORDS})")

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

    print(f"PASS: validated {len(paths)} skills; no structural or high-similarity duplication issues.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
