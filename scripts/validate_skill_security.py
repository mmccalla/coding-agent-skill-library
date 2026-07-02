#!/usr/bin/env python3
"""Deterministic L2 security validation for SKILL.md content."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

DEFAULT_ALLOWLIST = (
    Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "skill_security_allowlist.json"
)

NEGATIVE_GUIDANCE = re.compile(
    r"\b(?:never|do not|don't|must not|forbidden|blocked|reject|avoid)\b",
    re.I,
)
ESCALATION_LANGUAGE = re.compile(
    r"\b(?:approval|approve|explicit(?:ly)?|human|reversible|escalat(?:e|ion)|"
    r"guardrail|unless|without\s+approval|pause|confirm)\b",
    re.I,
)

SECURITY_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "instruction_override",
        re.compile(
            r"\bignore\s+(?:all\s+)?previous\s+instructions\b|"
            r"\bdisregard\s+(?:the\s+)?system\s+prompt\b|"
            r"\byou\s+are\s+now\b",
            re.I,
        ),
    ),
    (
        "privilege_escalation",
        re.compile(
            r"\bdisable\s+(?:tests?|lint(?:ing)?|security(?:\s+checks?)?)\b|"
            r"\bskip\s+(?:lint(?:ing)?|tests?|security(?:\s+checks?)?)\b|"
            r"\bbypass\s+(?:approval|security|guardrails?)\b",
            re.I,
        ),
    ),
    (
        "secret_exfiltration",
        re.compile(
            r"-----BEGIN(?:\s+(?:RSA|EC|OPENSSH))?\s+PRIVATE\s+KEY-----|"
            r"\bBEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY\b",
            re.I,
        ),
    ),
    (
        "destructive_commands",
        re.compile(
            r"\brm\s+-rf\s+/\b|"
            r"\brm\s+-rf\s+\*\b|"
            r"\bdrop\s+database\b|"
            r"\bgit\s+push\s+--force\b",
            re.I,
        ),
    ),
)


@dataclass(frozen=True)
class SecurityViolation:
    category: str
    pattern: str
    line: int
    message: str
    text: str


@dataclass
class SecurityValidationResult:
    skill_path: str
    passed: bool
    allowlisted: bool = False
    violations: list[SecurityViolation] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "skill_path": self.skill_path,
            "passed": self.passed,
            "allowlisted": self.allowlisted,
            "violations": [asdict(violation) for violation in self.violations],
        }


def read_skill_content(skill_path: str, content: str | None = None) -> str:
    if content is not None:
        return content
    return Path(skill_path).read_text(encoding="utf-8")


def parse_frontmatter_name(content: str) -> str:
    if not content.startswith("---\n"):
        return ""
    end = content.find("\n---\n", 4)
    if end == -1:
        return ""
    frontmatter = content[4:end]
    match = re.search(r"^name:\s*([-a-z0-9]+)\s*$", frontmatter, flags=re.M)
    return match.group(1) if match else ""


def load_allowlist(allowlist_path: str | Path) -> list[dict[str, object]]:
    path = Path(allowlist_path)
    if not path.is_file():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        return []
    return [entry for entry in entries if isinstance(entry, dict)]


def _path_matches_suffix(skill_path: str, suffixes: object) -> bool:
    if not isinstance(suffixes, list):
        return False
    normalised = skill_path.replace("\\", "/")
    return any(normalised.endswith(str(suffix)) for suffix in suffixes)


def resolve_allowlisted_categories(
    skill_path: str,
    content: str,
    allowlist_entries: list[dict[str, object]],
) -> set[str]:
    skill_name = parse_frontmatter_name(content)
    categories: set[str] = set()
    for entry in allowlist_entries:
        entry_categories = entry.get("categories", [])
        if not isinstance(entry_categories, list):
            continue
        skill_names = entry.get("skill_names", [])
        path_suffixes = entry.get("path_suffixes", [])
        name_match = isinstance(skill_names, list) and skill_name in skill_names
        path_match = _path_matches_suffix(skill_path, path_suffixes)
        if name_match or path_match:
            categories.update(str(category) for category in entry_categories)
    return categories


def _line_is_negative_guidance(line: str) -> bool:
    return bool(NEGATIVE_GUIDANCE.search(line))


def _line_has_escalation_language(line: str) -> bool:
    return bool(ESCALATION_LANGUAGE.search(line))


def scan_security_violations(
    content: str,
    *,
    allowlisted_categories: set[str] | None = None,
) -> list[SecurityViolation]:
    allowlisted_categories = allowlisted_categories or set()
    violations: list[SecurityViolation] = []
    for line_number, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        for category, pattern in SECURITY_RULES:
            if category in allowlisted_categories:
                continue
            match = pattern.search(line)
            if not match:
                continue
            if category == "privilege_escalation" and _line_is_negative_guidance(line):
                continue
            if category == "destructive_commands" and _line_has_escalation_language(line):
                continue
            violations.append(
                SecurityViolation(
                    category=category,
                    pattern=match.group(0),
                    line=line_number,
                    message=(
                        f"L2 security violation ({category}): "
                        f"matched '{match.group(0)}' on line {line_number}"
                    ),
                    text=stripped,
                )
            )
    return violations


def validate_skill_security(
    skill_path: str,
    *,
    content: str | None = None,
    allowlist_path: str | Path = DEFAULT_ALLOWLIST,
) -> SecurityValidationResult:
    text = read_skill_content(skill_path, content)
    allowlist_entries = load_allowlist(allowlist_path)
    allowlisted_categories = resolve_allowlisted_categories(skill_path, text, allowlist_entries)
    violations = scan_security_violations(text, allowlisted_categories=allowlisted_categories)
    return SecurityValidationResult(
        skill_path=skill_path,
        passed=not violations,
        allowlisted=bool(allowlisted_categories),
        violations=violations,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate SKILL.md security policy (L2).")
    parser.add_argument("paths", nargs="+", help="Skill file paths to validate")
    parser.add_argument(
        "--allowlist",
        default=str(DEFAULT_ALLOWLIST),
        help="Path to skill security allowlist JSON",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON report")
    args = parser.parse_args(argv)

    reports = [
        validate_skill_security(path, allowlist_path=args.allowlist) for path in args.paths
    ]
    passed = all(report.passed for report in reports)

    if args.json:
        print(json.dumps({"passed": passed, "reports": [report.to_dict() for report in reports]}))
    else:
        if passed:
            print(f"PASS: security validation passed for {len(reports)} skill file(s).")
        else:
            print("FAIL")
            for report in reports:
                for violation in report.violations:
                    print(f"- {report.skill_path}: {violation.message}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
