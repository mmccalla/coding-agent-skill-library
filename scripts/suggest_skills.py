#!/usr/bin/env python3
"""Suggest local skills for a natural-language task description."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import NamedTuple

TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9-]{2,}")
DEFAULT_ROOT = Path(__file__).resolve().parents[1]


class SkillSuggestion(NamedTuple):
    """A ranked skill match."""

    name: str
    path: Path
    score: int
    matched_terms: tuple[str, ...]
    description: str


def tokenise(text: str) -> set[str]:
    """Return normalised searchable terms."""

    terms: set[str] = set()
    for token in TOKEN_RE.findall(text.lower()):
        parts = token.split("-")
        terms.add(token)
        terms.update(parts)
        for part in parts:
            if len(part) > 3 and part.endswith("s"):
                terms.add(part[:-1])
    return terms


def read_description(text: str) -> str:
    """Extract a single-line YAML frontmatter description."""

    match = re.search(r"^description:\s*(.+)$", text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def iter_skill_files(repo_root: Path) -> list[Path]:
    """List skill files in a stable order."""

    return sorted((repo_root / "skills").glob("*/*/SKILL.md"))


def suggest_skills(
    query: str,
    *,
    repo_root: Path = DEFAULT_ROOT,
    limit: int = 10,
) -> list[SkillSuggestion]:
    """Rank skills by simple keyword overlap with name, description and body."""

    query_terms = tokenise(query)
    if not query_terms:
        return []

    suggestions: list[SkillSuggestion] = []
    for path in iter_skill_files(repo_root):
        text = path.read_text(encoding="utf-8")
        description = read_description(text)
        primary_terms = tokenise(" ".join((path.parent.name, description)))
        body_terms = tokenise(text)
        matched_terms = tuple(sorted(query_terms & (primary_terms | body_terms)))
        if not matched_terms:
            continue
        score = len(query_terms & body_terms) + (2 * len(query_terms & primary_terms))
        suggestions.append(
            SkillSuggestion(
                name=path.parent.name,
                path=path.relative_to(repo_root),
                score=score,
                matched_terms=matched_terms,
                description=description,
            )
        )

    return sorted(
        suggestions,
        key=lambda suggestion: (-suggestion.score, suggestion.name),
    )[:limit]


def main() -> int:
    """CLI entry point."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Task description to match against local skills")
    parser.add_argument("--limit", type=int, default=10, help="Maximum suggestions")
    args = parser.parse_args()

    for suggestion in suggest_skills(args.query, limit=args.limit):
        terms = ", ".join(suggestion.matched_terms)
        print(f"{suggestion.name}\t{suggestion.score}\t{terms}\t{suggestion.path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
