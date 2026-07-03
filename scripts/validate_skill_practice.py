#!/usr/bin/env python3
"""Deterministic L3 best-practice validation for SKILL.md content."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

WHEN_TRIGGER = re.compile(r"\buse when\b", re.I)
NUMBERED_STEP = re.compile(r"^\s*\d+\.\s+\S", re.M)
VERIFICATION_CHECKBOX = re.compile(r"^- \[ \]", re.M)


@dataclass(frozen=True)
class PracticeIssue:
    code: str
    message: str
    line: int | None = None


@dataclass
class PracticeValidationResult:
    skill_path: str
    passed: bool
    issues: list[PracticeIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "skill_path": self.skill_path,
            "passed": self.passed,
            "issues": [asdict(issue) for issue in self.issues],
        }


def read_skill_content(skill_path: str, content: str | None = None) -> str:
    if content is not None:
        return content
    return Path(skill_path).read_text(encoding="utf-8")


def extract_frontmatter_description(content: str) -> str:
    if not content.startswith("---\n"):
        return ""
    end = content.find("\n---\n", 4)
    if end == -1:
        return ""
    frontmatter = content[4:end]
    match = re.search(r"^description:\s*(.+)$", frontmatter, flags=re.M)
    return match.group(1).strip() if match else ""


def extract_section(content: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)",
        content,
        flags=re.S | re.M,
    )
    return match.group(1) if match else ""


def validate_skill_practice_content(content: str, skill_path: str) -> PracticeValidationResult:
    issues: list[PracticeIssue] = []

    description = extract_frontmatter_description(content)
    if not WHEN_TRIGGER.search(description):
        issues.append(
            PracticeIssue(
                code="missing_use_when_trigger",
                message="Frontmatter description must include a 'Use when' trigger phrase.",
            )
        )

    procedure_section = extract_section(content, "Procedure")
    if not procedure_section.strip():
        issues.append(
            PracticeIssue(
                code="missing_procedure_section",
                message="Skill must include a '## Procedure' section.",
            )
        )
    elif not NUMBERED_STEP.search(procedure_section):
        issues.append(
            PracticeIssue(
                code="missing_numbered_procedure",
                message="## Procedure must include at least one numbered step.",
            )
        )

    verification_section = extract_section(content, "Verification")
    if not verification_section.strip():
        issues.append(
            PracticeIssue(
                code="missing_verification_section",
                message="Skill must include a '## Verification' section.",
            )
        )
    elif not VERIFICATION_CHECKBOX.search(verification_section):
        issues.append(
            PracticeIssue(
                code="missing_verification_checkbox",
                message="## Verification must include at least one unchecked checklist item.",
            )
        )

    return PracticeValidationResult(
        skill_path=skill_path,
        passed=not issues,
        issues=issues,
    )


def validate_skill_practice(
    skill_path: str,
    *,
    content: str | None = None,
) -> PracticeValidationResult:
    text = read_skill_content(skill_path, content)
    return validate_skill_practice_content(text, skill_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate SKILL.md practice rubric (L3).")
    parser.add_argument("paths", nargs="+", help="Skill file paths to validate")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON report")
    args = parser.parse_args(argv)

    reports = [validate_skill_practice(path) for path in args.paths]
    passed = all(report.passed for report in reports)

    if args.json:
        print(json.dumps({"passed": passed, "reports": [report.to_dict() for report in reports]}))
    else:
        if passed:
            print(f"PASS: practice validation passed for {len(reports)} skill file(s).")
        else:
            print("FAIL")
            for report in reports:
                for issue in report.issues:
                    print(f"- {report.skill_path}: {issue.message}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
