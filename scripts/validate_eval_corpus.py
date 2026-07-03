#!/usr/bin/env python3
"""Validate tiered retrieval evaluation corpora and emit coverage matrices."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.extract_skills_graph import extract_skills_graph_records
from scripts.skills_inventory import skill_category_map

REPO_ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = REPO_ROOT / "tests" / "fixtures" / "retrieval_evaluation"

TIER_BOUNDS: dict[str, tuple[int, int]] = {
    "smoke": (8, 40),
    "realistic": (20, 120),
    "coverage": (180, 320),
    "abstention": (10, 25),
    "catalogue": (20, 200),
}

RELEASE_TIERS = frozenset({"smoke", "realistic", "abstention", "catalogue"})
GENERATED_ID_PATTERN = re.compile(r"_generated_\d{2}$")
MAX_QUERY_JACCARD = 0.85
MIN_CATEGORY_REALISTIC = 1
MIN_ARCHETYPES_PER_SKILL = 2


@dataclass(frozen=True)
class ValidationResult:
    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "valid": self.valid,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
        }


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 2}


def token_jaccard(left: str, right: str) -> float:
    a = _tokens(left)
    b = _tokens(right)
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def load_json_cases(path: Path) -> list[dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{path}: expected JSON array")
    cases: list[dict[str, object]] = []
    for index, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"{path}[{index}]: expected object")
        cases.append(item)
    return cases


def _case_id(case: dict[str, object]) -> str:
    value = case.get("id")
    if not isinstance(value, str) or not value.strip():
        raise ValueError("case missing string id")
    return value.strip()


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def validate_case_schema(case: dict[str, object], *, tier: str, path: Path) -> list[str]:
    errors: list[str] = []
    case_id = _case_id(case)
    if not isinstance(case.get("query"), str) or not str(case["query"]).strip():
        errors.append(f"{path.name}:{case_id}: missing query")
    if not isinstance(case.get("expect_uncertain"), bool):
        errors.append(f"{path.name}:{case_id}: expect_uncertain must be boolean")
    if "expected_skill_ids" not in case:
        errors.append(f"{path.name}:{case_id}: missing expected_skill_ids")
    elif not isinstance(case["expected_skill_ids"], list):
        errors.append(f"{path.name}:{case_id}: expected_skill_ids must be a list")
    promotion_tier = case.get("promotion_tier", "release")
    if tier in RELEASE_TIERS and promotion_tier != "release":
        errors.append(f"{path.name}:{case_id}: release tier file requires promotion_tier=release")
    if tier in RELEASE_TIERS and GENERATED_ID_PATTERN.search(case_id):
        errors.append(f"{path.name}:{case_id}: generated template ids not allowed in {tier}")
    return errors


def validate_tier_file(path: Path, tier: str) -> ValidationResult:
    if not path.is_file():
        return ValidationResult(False, (f"missing file: {path}",), ())
    cases = load_json_cases(path)
    errors: list[str] = []
    warnings: list[str] = []
    seen_ids: set[str] = set()

    lower, upper = TIER_BOUNDS.get(tier, (1, 10_000))
    if not (lower <= len(cases) <= upper):
        errors.append(f"{tier}: expected {lower}..{upper} cases, found {len(cases)}")

    for case in cases:
        case_id = _case_id(case)
        if case_id in seen_ids:
            errors.append(f"{tier}: duplicate id {case_id}")
        seen_ids.add(case_id)
        errors.extend(validate_case_schema(case, tier=tier, path=path))

    return ValidationResult(not errors, tuple(errors), tuple(warnings))


def promoted_skill_ids(skills_root: Path) -> frozenset[str]:
    records = extract_skills_graph_records(skills_root)
    skills = records.get("skills")
    if not isinstance(skills, list):
        return frozenset()
    promoted: list[str] = []
    for skill in skills:
        if not isinstance(skill, dict):
            continue
        if str(skill.get("promotion_status", "")) == "promoted":
            promoted.append(str(skill["id"]))
    return frozenset(promoted)


def build_coverage_matrix(
    coverage_cases: list[dict[str, object]],
) -> dict[str, object]:
    by_skill: dict[str, list[dict[str, object]]] = defaultdict(list)
    for case in coverage_cases:
        if case.get("expect_uncertain"):
            continue
        archetype = str(case.get("query_archetype", "unknown"))
        for skill_id in _string_list(case.get("expected_skill_ids")):
            by_skill[skill_id].append(
                {
                    "case_id": _case_id(case),
                    "query_archetype": archetype,
                    "query_source": case.get("query_source", "unknown"),
                }
            )
    return {
        "skills": {
            skill_id: {
                "case_count": len(rows),
                "archetypes": sorted({str(row["query_archetype"]) for row in rows}),
                "cases": rows,
            }
            for skill_id, rows in sorted(by_skill.items())
        }
    }


def validate_coverage_matrix(
    coverage_cases: list[dict[str, object]],
    promoted_ids: frozenset[str],
) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    matrix = build_coverage_matrix(coverage_cases)
    skills_map = matrix["skills"]
    assert isinstance(skills_map, dict)

    missing = sorted(promoted_ids - set(skills_map))
    if missing:
        errors.append(
            f"coverage: missing promoted skills: {', '.join(missing[:5])} "
            f"({len(missing)} total)"
        )

    queries_by_skill: dict[str, list[str]] = defaultdict(list)
    for case in coverage_cases:
        if case.get("expect_uncertain"):
            continue
        query = str(case.get("query", ""))
        for skill_id in _string_list(case.get("expected_skill_ids")):
            for existing in queries_by_skill[skill_id]:
                if token_jaccard(existing, query) > MAX_QUERY_JACCARD:
                    errors.append(
                        f"coverage: {skill_id} has near-duplicate queries "
                        f"({_case_id(case)} vs existing)"
                    )
                    break
            queries_by_skill[skill_id].append(query)

    for skill_id, rows in skills_map.items():
        if not isinstance(rows, dict):
            continue
        archetypes = rows.get("archetypes")
        if isinstance(archetypes, list) and len(archetypes) < MIN_ARCHETYPES_PER_SKILL:
            errors.append(
                f"coverage: {skill_id} has {len(archetypes)} archetype(s); "
                f"need {MIN_ARCHETYPES_PER_SKILL}"
            )

    return ValidationResult(not errors, tuple(errors), tuple(warnings))


def validate_confuser_pairs(
    pairs: list[dict[str, object]],
    realistic_cases: list[dict[str, object]],
) -> ValidationResult:
    errors: list[str] = []
    for pair in pairs:
        pair_id = str(pair.get("id", ""))
        preferred = str(pair.get("preferred_skill_id", ""))
        confuser = str(pair.get("confuser_skill_id", ""))
        if not pair_id or not preferred or not confuser:
            errors.append("confuser_pairs: each entry needs id, preferred_skill_id, confuser_skill_id")
            continue
        matched = False
        for case in realistic_cases:
            expected = set(_string_list(case.get("expected_skill_ids")))
            excluded = set(_string_list(case.get("excluded_skill_ids")))
            if preferred in expected and confuser in excluded:
                matched = True
                break
        if not matched:
            errors.append(f"confuser_pairs: no realistic case for pair {pair_id}")
    return ValidationResult(not errors, tuple(errors), ())


def validate_category_balance(
    realistic_cases: list[dict[str, object]],
    skills_root: Path,
) -> ValidationResult:
    categories = {category for category in skill_category_map(skills_root).values() if category}
    counts: Counter[str] = Counter()
    skill_to_category = skill_category_map(skills_root)
    for case in realistic_cases:
        if case.get("expect_uncertain"):
            continue
        for skill_id in _string_list(case.get("expected_skill_ids")):
            skill_name = skill_id.removeprefix("skill:")
            category = skill_to_category.get(skill_name, "")
            if category:
                counts[category] += 1
    errors: list[str] = []
    for category in sorted(categories):
        if counts[category] < MIN_CATEGORY_REALISTIC:
            errors.append(
                f"realistic: category {category} has {counts[category]} cases; "
                f"need {MIN_CATEGORY_REALISTIC}"
            )
    return ValidationResult(not errors, tuple(errors), ())


def check_skill_sync(
    coverage_cases: list[dict[str, object]],
    skills_root: Path,
) -> ValidationResult:
    promoted = promoted_skill_ids(skills_root)
    covered = {
        skill_id
        for case in coverage_cases
        if not case.get("expect_uncertain")
        for skill_id in _string_list(case.get("expected_skill_ids"))
    }
    missing = sorted(promoted - covered)
    if missing:
        return ValidationResult(
            False,
            (f"skill sync: {len(missing)} promoted skill(s) missing from coverage",),
            (),
        )
    return ValidationResult(True, (), ())


def validate_all(
    *,
    skills_root: Path,
    check_sync: bool = False,
) -> ValidationResult:
    files = {
        "catalogue": EVAL_DIR / "query_catalog.json",
        "smoke": EVAL_DIR / "smoke_queries_promoted.json",
        "realistic": EVAL_DIR / "realistic_queries.json",
        "coverage": EVAL_DIR / "coverage_queries.json",
        "abstention": EVAL_DIR / "abstention_probes.json",
    }
    errors: list[str] = []
    warnings: list[str] = []

    tier_results: dict[str, list[dict[str, object]]] = {}
    for tier, path in files.items():
        if not path.is_file() and tier == "coverage":
            warnings.append("coverage_queries.json not yet generated")
            continue
        if not path.is_file():
            errors.append(f"missing {path.name}")
            continue
        result = validate_tier_file(path, tier)
        errors.extend(result.errors)
        warnings.extend(result.warnings)
        if path.is_file():
            tier_results[tier] = load_json_cases(path)

    if "coverage" in tier_results:
        promoted = promoted_skill_ids(skills_root)
        cov = validate_coverage_matrix(tier_results["coverage"], promoted)
        errors.extend(cov.errors)
        warnings.extend(cov.warnings)
        if check_sync:
            sync = check_skill_sync(tier_results["coverage"], skills_root)
            errors.extend(sync.errors)

    if "realistic" in tier_results:
        cat = validate_category_balance(tier_results["realistic"], skills_root)
        errors.extend(cat.errors)

    pairs_path = EVAL_DIR / "confuser_pairs.json"
    if pairs_path.is_file() and "realistic" in tier_results:
        pairs = load_json_cases(pairs_path)
        pair_result = validate_confuser_pairs(pairs, tier_results["realistic"])
        errors.extend(pair_result.errors)

    return ValidationResult(not errors, tuple(errors), tuple(warnings))


def emit_matrix(output: Path) -> int:
    coverage_path = EVAL_DIR / "coverage_queries.json"
    if not coverage_path.is_file():
        print(f"FAIL: missing {coverage_path}", file=sys.stderr)
        return 1
    cases = load_json_cases(coverage_path)
    matrix = build_coverage_matrix(cases)
    output.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {output.relative_to(REPO_ROOT)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate tiered retrieval evaluation corpora.")
    parser.add_argument("--skills-root", default=str(REPO_ROOT / "skills"))
    parser.add_argument("--check-skill-sync", action="store_true")
    parser.add_argument("--emit-matrix", metavar="PATH")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.emit_matrix:
        return emit_matrix(Path(args.emit_matrix))

    result = validate_all(
        skills_root=Path(args.skills_root),
        check_sync=args.check_skill_sync,
    )
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        status = "PASS" if result.valid else "FAIL"
        print(status)
        for error in result.errors:
            print(f"- {error}")
        for warning in result.warnings:
            print(f"WARN: {warning}")
    return 0 if result.valid else 1


if __name__ == "__main__":
    sys.exit(main())
