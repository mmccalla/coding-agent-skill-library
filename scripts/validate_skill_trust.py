#!/usr/bin/env python3
"""Orchestrate pre-ingest trust gates (L1–L4) for SKILL.md content."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.validate_skill_practice import PracticeValidationResult, validate_skill_practice
from scripts.validate_skill_security import (
    DEFAULT_ALLOWLIST,
    SecurityValidationResult,
    validate_skill_security,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class LayerResult:
    layer: str
    status: str
    passed: bool
    details: dict[str, object]


@dataclass
class TrustReport:
    skill_path: str
    passed: bool
    layers: dict[str, LayerResult] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "skill_path": self.skill_path,
            "passed": self.passed,
            "layers": {key: asdict(value) for key, value in self.layers.items()},
        }


def _layer_from_security(result: SecurityValidationResult) -> LayerResult:
    return LayerResult(
        layer="L2_security",
        status="pass" if result.passed else "fail",
        passed=result.passed,
        details=result.to_dict(),
    )


def _layer_from_practice(result: PracticeValidationResult) -> LayerResult:
    return LayerResult(
        layer="L3_practice",
        status="pass" if result.passed else "fail",
        passed=result.passed,
        details=result.to_dict(),
    )


def _layer_mapping_stub(skill_path: str) -> LayerResult:
    return LayerResult(
        layer="L4_mapping",
        status="skipped",
        passed=True,
        details={
            "skill_path": skill_path,
            "message": "L4 semantic mapping validation not implemented in Phase 3.",
        },
    )


def validate_skill_trust_file(
    skill_path: str,
    *,
    allowlist_path: str | Path = DEFAULT_ALLOWLIST,
    include_mapping: bool = True,
) -> TrustReport:
    security = validate_skill_security(skill_path, allowlist_path=allowlist_path)
    practice = validate_skill_practice(skill_path)
    layers: dict[str, LayerResult] = {
        "L2_security": _layer_from_security(security),
        "L3_practice": _layer_from_practice(practice),
    }
    if include_mapping:
        layers["L4_mapping"] = _layer_mapping_stub(skill_path)

    blocking_layers = ("L2_security", "L3_practice")
    passed = all(layers[layer].passed for layer in blocking_layers)
    return TrustReport(skill_path=skill_path, passed=passed, layers=layers)


def validate_skill_trust_paths(
    paths: list[str],
    *,
    allowlist_path: str | Path = DEFAULT_ALLOWLIST,
) -> list[TrustReport]:
    return [validate_skill_trust_file(path, allowlist_path=allowlist_path) for path in paths]


def _detail_items(details: dict[str, object], key: str) -> list[object]:
    value = details.get(key, [])
    return value if isinstance(value, list) else []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run pre-ingest trust gates for skill files.")
    parser.add_argument(
        "paths",
        nargs="*",
        help="Skill file paths to validate (omit when using --skills-root)",
    )
    parser.add_argument(
        "--skills-root",
        default="",
        help="Validate all SKILL.md files under this directory",
    )
    parser.add_argument(
        "--allowlist",
        default=str(DEFAULT_ALLOWLIST),
        help="Path to skill security allowlist JSON",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON report")
    args = parser.parse_args(argv)

    paths = list(args.paths)
    if args.skills_root:
        root = Path(args.skills_root)
        paths.extend(str(path) for path in sorted(root.rglob("SKILL.md")))

    if not paths:
        parser.error("provide skill file paths or --skills-root")

    reports = validate_skill_trust_paths(paths, allowlist_path=args.allowlist)
    passed = all(report.passed for report in reports)

    if args.json:
        if len(reports) == 1:
            print(json.dumps(reports[0].to_dict()))
        else:
            print(
                json.dumps(
                    {
                        "passed": passed,
                        "reports": [report.to_dict() for report in reports],
                    }
                )
            )
    else:
        if passed:
            print(f"PASS: trust validation passed for {len(reports)} skill file(s).")
        else:
            print("FAIL")
            for report in reports:
                if report.passed:
                    continue
                print(f"- {report.skill_path}")
                for layer in ("L2_security", "L3_practice"):
                    layer_result = report.layers[layer]
                    if layer_result.passed:
                        continue
                    details = layer_result.details
                    if layer == "L2_security":
                        for violation in _detail_items(details, "violations"):
                            if isinstance(violation, dict):
                                print(f"  - {violation.get('message', violation)}")
                    if layer == "L3_practice":
                        for issue in _detail_items(details, "issues"):
                            if isinstance(issue, dict):
                                print(f"  - {issue.get('message', issue)}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
