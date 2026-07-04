#!/usr/bin/env python3
"""Deterministic L3 best-practice and standards-grounding validation for SKILL.md content."""

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
HTTP_URL = re.compile(r"https?://[^\s\)\]]+", re.I)
NUMBERED_BLOCK = re.compile(
    r"(?:^## (?:Procedure|Core pattern)\s*\n)((?:(?:\d+\..+\n)+))",
    re.M,
)

# Skill-folder name → required content markers (all must match, case-insensitive).
# Markers close the standards-validation gaps identified in the library audit.
STANDARDS_GROUNDING: dict[str, tuple[str, ...]] = {
    "accessibility-wcag": (
        r"3\.2\.6",
        r"WCAG\s*2\.2",
        r"https?://www\.w3\.org/TR/WCAG22",
    ),
    "ai-model-governance": (r"AI RMF|NIST", r"inventory|risk tier", r"https?://"),
    "api-design-and-lifecycle": (r"OpenAPI", r"https?://"),
    "business-capability-modeling": (r"BIZBOK", r"https?://"),
    "business-information-concept-modeling": (r"BIZBOK", r"https?://"),
    "capability-maturity-assessment": (r"BIZBOK", r"https?://"),
    "cloud-platform-architecture": (r"landing zone|tenancy", r"https?://"),
    "data-contract-design": (
        r"ODCS|Open Data Contract Standard",
        r"https?://bitol-io\.github\.io/open-data-contract-standard|https?://github\.com/bitol-io/open-data-contract-standard",
    ),
    "data-security-and-privacy-architecture": (
        r"DPIA",
        r"data subject|DSAR|erasure",
        r"https?://",
    ),
    "dora-four-keys": (
        r"rework rate",
        r"throughput",
        r"instability",
        r"https?://dora\.dev",
    ),
    "event-driven-architecture": (
        r"CloudEvents",
        r"AsyncAPI",
        r"https?://",
    ),
    "event-modeling": (r"CloudEvents|AsyncAPI|BIZBOK|event", r"https?://"),
    "event-streaming-platform-design": (r"CloudEvents|AsyncAPI", r"https?://"),
    "finops-practice": (
        r"FinOps",
        r"Inform",
        r"Optimise|Optimize",
        r"unit economics|allocation|showback|chargeback",
        r"https?://www\.finops\.org|https?://",
    ),
    "human-in-the-loop": (
        r"outside the (?:model|LLM)|architectural enforcement|policy engine|dispatcher",
        r"https?://|OWASP",
    ),
    "infrastructure-as-code": (r"declarative|plan/apply|IaC", r"https?://"),
    "integration-message-construction": (
        r"CloudEvents|EIP|Enterprise Integration Patterns",
        r"https?://",
    ),
    "inter-agent-communication-a2a": (
        r"https?://a2a-protocol\.org|https?://github\.com/a2aproject/A2A",
    ),
    "logical-data-modeling": (r"physical", r"index|partition", r"https?://"),
    "operating-model-design": (r"BIZBOK", r"https?://"),
    "organization-and-role-design": (r"BIZBOK|RACI", r"https?://"),
    "performance-engineering": (r"latency|throughput", r"profil", r"https?://"),
    "process-modeling": (r"BPMN|BIZBOK", r"https?://"),
    "risk-management": (r"risk register|treatment", r"https?://"),
    "schema-registry-and-contracts": (
        r"CloudEvents",
        r"AsyncAPI",
        r"https?://",
    ),
    "secure-sdlc-and-supply-chain": (r"SSDF|800-218", r"SBOM", r"https?://"),
    "slo-error-budget-management": (
        r"multi-window|multi window",
        r"burn rate",
        r"https?://sre\.google",
    ),
    "solution-architecture": (r"NFR|non-functional", r"option", r"https?://"),
    "strategy-to-execution-traceability": (r"BIZBOK", r"https?://"),
    "technical-debt-management": (r"debt", r"paydown|pay-down|interest", r"https?://"),
    "test-strategy": (r"test pyramid|risk-based", r"https?://"),
    "threat-modeling": (r"STRIDE|threat model", r"trust boundary", r"OWASP", r"https?://"),
    "value-stream-modeling": (r"BIZBOK", r"https?://"),
}


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


def skill_folder_name(skill_path: str) -> str:
    path = Path(skill_path)
    if path.name == "SKILL.md":
        return path.parent.name
    return path.stem


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


def _normalise_block(block: str) -> str:
    return re.sub(r"\s+", " ", block).strip()


def find_duplicate_procedure_blocks(content: str) -> bool:
    """Return True when Procedure and Core pattern (or two Procedure blocks) share identical steps."""
    blocks = [_normalise_block(match.group(1)) for match in NUMBERED_BLOCK.finditer(content)]
    if len(blocks) < 2:
        return False
    seen: set[str] = set()
    for block in blocks:
        if len(block) < 40:
            continue
        if block in seen:
            return True
        seen.add(block)
    return False


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

    if find_duplicate_procedure_blocks(content):
        issues.append(
            PracticeIssue(
                code="duplicate_procedure_content",
                message=(
                    "Procedure and Core pattern (or repeated Procedure) must not "
                    "duplicate the same numbered steps."
                ),
            )
        )

    skill_id = skill_folder_name(skill_path)
    required_markers = STANDARDS_GROUNDING.get(skill_id)
    if required_markers:
        for marker in required_markers:
            if not re.search(marker, content, flags=re.I):
                issues.append(
                    PracticeIssue(
                        code="missing_standards_grounding",
                        message=(
                            f"Skill '{skill_id}' must include standards grounding "
                            f"matching /{marker}/."
                        ),
                    )
                )
        references = extract_section(content, "References")
        if not references.strip() and not HTTP_URL.search(content):
            issues.append(
                PracticeIssue(
                    code="missing_standards_reference_url",
                    message=(
                        f"Skill '{skill_id}' must include a ## References section "
                        "or at least one http(s) primary-source URL."
                    ),
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


def iter_repository_skill_paths(skills_root: Path | str = "skills") -> list[Path]:
    root = Path(skills_root)
    return sorted(root.glob("*/SKILL.md"))


def validate_all_skills(skills_root: Path | str = "skills") -> list[PracticeValidationResult]:
    return [validate_skill_practice(str(path)) for path in iter_repository_skill_paths(skills_root)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate SKILL.md practice rubric (L3).")
    parser.add_argument(
        "paths",
        nargs="*",
        help="Skill file paths to validate (default: all skills/*/SKILL.md)",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON report")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate every skill under skills/",
    )
    args = parser.parse_args(argv)

    if args.all or not args.paths:
        reports = validate_all_skills()
    else:
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
                    print(f"- {report.skill_path}: [{issue.code}] {issue.message}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
