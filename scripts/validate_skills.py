#!/usr/bin/env python3
import os
import re
import sys
import itertools
from collections import Counter

ROOT = "skills"
MIN_WORDS = 140
SIMILARITY_FAIL = 0.82


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
    paths = []
    for dirpath, _, files in os.walk(ROOT):
        for name in files:
            if name == "SKILL.md":
                paths.append(os.path.join(dirpath, name))
    paths.sort()

    errors = []
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

        # Structural checks
        h1_count = sum(1 for ln in lines if ln.startswith("# "))
        if h1_count < 1:
            errors.append(f"{p}: missing level-1 heading")

        body_lower = text.lower()
        if "## when to use" not in body_lower:
            errors.append(f"{p}: missing 'When to use' section")

        if "## verification" not in body_lower and "## completion report" not in body_lower and "## output checklist" not in body_lower:
            errors.append(f"{p}: missing verification/completion section")

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
