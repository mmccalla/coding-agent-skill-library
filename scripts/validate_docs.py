#!/usr/bin/env python3
"""Validate active documentation for stale planning language."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DOCS = REPO_ROOT / "skills_docs"
ARCHIVE_PREFIX = SKILLS_DOCS / "archive"

STALE_PHRASES: tuple[tuple[str, str], ...] = (
    ("phase 0 only", "KRAG cutover is complete; use krag/STATUS.md"),
    ("does not yet prescribe code", "implementation is shipped; use krag/CONTRACTS.md"),
    ("bridge-heavy recommender", "legacy pre-cutover framing"),
    ("85/91", "promotion remediation completed (91/91)"),
    ("≥ 150 / 614", "golden corpus is 1,194 cases"),
    ("150 / 614", "golden corpus is 1,194 cases"),
    ("current recommender", "KRAG v2 is the live runtime"),
)


@dataclass(frozen=True)
class DocViolation:
    path: Path
    phrase: str
    hint: str


def iter_active_markdown(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*.md"):
        if "node_modules" in path.parts:
            continue
        try:
            path.relative_to(ARCHIVE_PREFIX)
            continue
        except ValueError:
            pass
        if path.name == "CHANGELOG.md":
            continue
        files.append(path)
    return sorted(files)


def scan_docs(root: Path = SKILLS_DOCS) -> list[DocViolation]:
    violations: list[DocViolation] = []
    for path in iter_active_markdown(root):
        text = path.read_text(encoding="utf-8").lower()
        for phrase, hint in STALE_PHRASES:
            if phrase in text:
                violations.append(DocViolation(path=path, phrase=phrase, hint=hint))
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)

    violations = scan_docs()
    if not violations:
        print("validate_docs: OK (no stale phrases in active skills_docs markdown)")
        return 0

    print("validate_docs: FAIL — stale planning language in active docs", file=sys.stderr)
    for item in violations:
        rel = item.path.relative_to(REPO_ROOT)
        print(f"  {rel}: '{item.phrase}' — {item.hint}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
