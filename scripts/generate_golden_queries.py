#!/usr/bin/env python3
"""Generate tiered retrieval evaluation corpora from the skills library."""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.extract_skills_graph import extract_skills_graph_records

REPO_ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = REPO_ROOT / "tests" / "fixtures" / "retrieval_evaluation"

CATALOGUE_PATH = EVAL_DIR / "query_catalog.json"
ABSTENTION_PATH = EVAL_DIR / "abstention_probes.json"
CONFUSER_PAIRS_PATH = EVAL_DIR / "confuser_pairs.json"
SMOKE_PATH = EVAL_DIR / "smoke_queries_promoted.json"
REALISTIC_PATH = EVAL_DIR / "realistic_queries.json"
COVERAGE_PATH = EVAL_DIR / "coverage_queries.json"
LEGACY_GOLDEN_PATH = EVAL_DIR / "golden_queries.json"
MATRIX_PATH = EVAL_DIR / "coverage_matrix.json"
BASELINE_PATH = REPO_ROOT / "skills_docs" / "archive" / "planning" / "CORPUS_SHRINK_BASELINE.json"

SHADOW_LEGACY_SAMPLE_SIZE = 100
SHADOW_SEED = 42


def _description_fragment(description: str) -> str:
    fragment = description
    if ". " in fragment:
        fragment = fragment.split(". ", 1)[0]
    fragment = re.sub(r"\s+", " ", fragment).strip()
    return fragment.rstrip(".")


def _skill_id_set(raw: object) -> set[str]:
    if not isinstance(raw, list):
        return set()
    return {str(item) for item in raw if isinstance(item, str)}


def _graph_skills(records: dict[str, object]) -> list[dict[str, object]]:
    skills = records.get("skills")
    if not isinstance(skills, list):
        return []
    return [skill for skill in skills if isinstance(skill, dict)]


def _promotion_tier_for_case(
    case: dict[str, object],
    promoted_ids: frozenset[str],
) -> str:
    expected = _skill_id_set(case.get("expected_skill_ids")) | _skill_id_set(
        case.get("required_skill_ids")
    )
    if case.get("promotion_tier"):
        return str(case["promotion_tier"])
    if not expected:
        return "release"
    if expected <= promoted_ids:
        return "release"
    if expected & promoted_ids:
        return "release"
    return "diagnostic"


def load_cases(path: Path) -> list[dict[str, object]]:
    if not path.is_file():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{path}: expected array")
    return [dict(item) for item in payload if isinstance(item, dict)]


def _skill_aliases(skill_name: str, skills_root: Path) -> tuple[str, ...]:
    path = skills_root / skill_name / "SKILL.md"
    if not path.is_file():
        return ()
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return ()
    end = text.find("\n---\n", 4)
    if end == -1:
        return ()
    frontmatter = text[4:end]
    aliases: list[str] = []
    in_aliases = False
    for line in frontmatter.splitlines():
        if line.startswith("aliases:"):
            in_aliases = True
            continue
        if in_aliases:
            if line.startswith("  - "):
                aliases.append(line[4:].strip().strip("\"'"))
            elif line and not line.startswith(" "):
                in_aliases = False
    return tuple(aliases)


def _confuser_skills_for(skill_id: str, pairs: list[dict[str, object]]) -> tuple[str, ...]:
    confusers: list[str] = []
    for pair in pairs:
        if str(pair.get("preferred_skill_id", "")) == skill_id:
            confusers.append(str(pair.get("confuser_skill_id", "")))
    return tuple(conf for conf in confusers if conf)


def build_coverage_cases(
    skills: list[dict[str, object]],
    *,
    skills_root: Path,
    pairs: list[dict[str, object]],
    promoted_ids: frozenset[str],
) -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    for skill in skills:
        skill_id = str(skill["id"])
        if skill_id not in promoted_ids:
            continue
        name = str(skill["name"])
        description = str(skill["description"])
        fragment = _description_fragment(description)
        slug = name.replace("-", "_")
        aliases = _skill_aliases(name, skills_root)

        if aliases:
            task_query = f"When should I use {aliases[0]} for {fragment.lower()}?"
        else:
            task_query = f"When should I follow the {name} practice for {fragment.lower()}?"
        cases.append(
            {
                "id": f"coverage_{slug}_task",
                "query": task_query,
                "expected_skill_ids": [skill_id],
                "required_skill_ids": [skill_id],
                "excluded_skill_ids": [],
                "expect_uncertain": False,
                "query_source": "archetype",
                "query_archetype": "task",
                "naturalness": "medium",
            }
        )

        if aliases:
            alias = aliases[0]
            cases.append(
                {
                    "id": f"coverage_{slug}_alias",
                    "query": f"When should I use {alias} for this kind of work?",
                    "expected_skill_ids": [skill_id],
                    "required_skill_ids": [skill_id],
                    "excluded_skill_ids": [],
                    "expect_uncertain": False,
                    "query_source": "archetype",
                    "query_archetype": "alias",
                    "naturalness": "medium",
                }
            )
        else:
            cases.append(
                {
                    "id": f"coverage_{slug}_direct",
                    "query": f"I need a practical checklist for applying {name} on a coding task.",
                    "expected_skill_ids": [skill_id],
                    "required_skill_ids": [skill_id],
                    "excluded_skill_ids": [],
                    "expect_uncertain": False,
                    "query_source": "archetype",
                    "query_archetype": "direct",
                    "naturalness": "medium",
                }
            )

        confusers = _confuser_skills_for(skill_id, pairs)
        if confusers:
            cases.append(
                {
                    "id": f"coverage_{slug}_confuser",
                    "query": (
                        f"Choose {name.replace('-', ' ')} (not a related substitute) "
                        f"for: {fragment.lower()}"
                    ),
                    "expected_skill_ids": [skill_id],
                    "required_skill_ids": [skill_id],
                    "excluded_skill_ids": [confusers[0]],
                    "expect_uncertain": False,
                    "query_source": "archetype",
                    "query_archetype": "confuser",
                    "naturalness": "medium",
                }
            )

    for case in cases:
        case["promotion_tier"] = _promotion_tier_for_case(case, promoted_ids)
    return cases


def build_smoke_cases(
    catalogue: list[dict[str, object]],
    abstention: list[dict[str, object]],
    promoted_ids: frozenset[str],
) -> list[dict[str, object]]:
    smoke_ids = {
        "tdd_practice",
        "spec_before_build",
        "post_artefact_review",
        "planning",
        "git_workflow",
        "human_approval",
        "krag_system_design",
        "kg_rag",
        "confuser_guardrails_vs_hitl",
        "apply_laws_baseline",
    }
    cases: list[dict[str, object]] = []
    for case in catalogue:
        if str(case.get("id", "")) in smoke_ids or case.get("smoke"):
            cases.append(dict(case))
    if not cases:
        cases = [dict(case) for case in catalogue[:25]]
    absent = next(
        (dict(case) for case in abstention if case.get("id") == "abstain_nonsense_tokens"), None
    )
    if absent:
        cases.append(absent)
    for case in cases:
        case["promotion_tier"] = _promotion_tier_for_case(case, promoted_ids)
    return cases


# Distinctive query fragments for confuser-pair realistic cases (preferred skill keywords).
_CONFUSER_QUERY_HINTS: dict[str, str] = {
    "skill:threat-modeling": "STRIDE trust boundaries threat model mitigations",
    "skill:guardrails-safety-patterns": "runtime input validation tool allow-lists output filtering",
    "skill:secure-sdlc-and-supply-chain": "NIST SSDF SBOM dependency pinning supply chain",
    "skill:ci-cd-and-automation": "build pipeline jobs deployment automation gates",
    "skill:api-design-and-lifecycle": "OpenAPI HTTP versioning authZ deprecation",
    "skill:data-contract-design": "data product schema quality freshness producer consumer",
    "skill:ai-model-governance": "model inventory risk tier approval kill-switch retirement",
    "skill:evaluation-and-monitoring": "quality metrics baselines regression drift dashboards",
    "skill:solution-architecture": "NFRs options context container views fitness functions",
    "skill:spec-driven-development": "write specification acceptance criteria before coding",
    "skill:test-strategy": "risk-based test pyramid levels automation exit criteria",
    "skill:tdd-practice": "failing test first red green refactor smallest change",
    "skill:risk-management": "risk register likelihood impact treatment residual risk",
    "skill:prioritization": "rank backlog items by urgency and impact only",
    "skill:finops-practice": "FinOps allocation tags unit economics showback spend anomalies",
    "skill:resource-aware-optimization": "agent session token budget model tier context window",
    "skill:cloud-platform-architecture": "landing zone tenancy shared services identity boundaries",
    "skill:performance-engineering": "profile latency throughput load test capacity",
    "skill:slo-error-budget-management": "SLO error budget burn rate release policy",
    "skill:infrastructure-as-code": "declarative plan apply drift secrets infrastructure",
    "skill:technical-debt-management": "debt inventory interest paydown owners remediation",
    "skill:human-in-the-loop": "human approval decision packet before high-risk action",
    "skill:knowledge-retrieval-rag": "document chunk retrieval citations hybrid search",
    "skill:krag-retrieval-answering": "graph traversal hybrid ranking grounded KRAG answer",
    "skill:reflection-and-verification": "critique repair verification loop after draft",
    "skill:krag-system-design": "KRAG architecture graph role retrieval slices",
    "skill:knowledge-graph-rag": "Neo4j GraphRAG text-to-Cypher provenance",
    "skill:ontology-and-knowledge-graph-modeling": "OWL SHACL ontology competency questions",
    "skill:incremental-implementation": "small reversible delivery slices",
    "skill:planning-and-task-decomposition": "ordered executable plan for complex goal",
    "skill:sre-practice": "service reliability operability runbooks ownership",
    "skill:observability-and-telemetry": "metrics logs traces dashboards alerts",
    "skill:event-streaming-platform-design": "Kafka topics partitions retention platform",
    "skill:cdc-and-source-to-stream-ingestion": "change data capture source to stream",
    "skill:ux-design-principles": "user journeys navigation forms information architecture",
    "skill:ui-component-design": "reusable components tables modals forms",
    "skill:krag-ingestion-graph-construction": "evidence anchoring entity resolution graph build",
    "skill:krag-evaluation-governance": "KRAG quality gates release criteria",
    "skill:mcp-server-design": "MCP tools resources prompts least privilege",
    "skill:inter-agent-communication-a2a": "agent cards tasks artefacts A2A hand-off",
}


def _confuser_realistic_cases(pairs: list[dict[str, object]]) -> list[dict[str, object]]:
    """Emit realistic cases that satisfy confuser-pair validation (preferred expected, confuser excluded)."""
    cases: list[dict[str, object]] = []
    seen_pair_ids: set[str] = set()
    for pair in pairs:
        pair_id = str(pair.get("id", "")).strip()
        preferred = str(pair.get("preferred_skill_id", "")).strip()
        confuser = str(pair.get("confuser_skill_id", "")).strip()
        if not pair_id or not preferred or not confuser:
            continue
        if pair_id in seen_pair_ids:
            continue
        seen_pair_ids.add(pair_id)
        hint = _CONFUSER_QUERY_HINTS.get(
            preferred, preferred.removeprefix("skill:").replace("-", " ")
        )
        cases.append(
            {
                "id": f"confuser_{pair_id}",
                "query": hint,
                "expected_skill_ids": [preferred],
                "required_skill_ids": [preferred],
                "excluded_skill_ids": [confuser],
                "expect_uncertain": False,
                "query_source": "confuser_pair",
                "query_archetype": "confuser",
                "naturalness": "medium",
                "promotion_tier": "release",
                "realistic_tier": True,
            }
        )
    return cases


def build_realistic_cases(
    catalogue: list[dict[str, object]],
    journeys_path: Path,
    promoted_ids: frozenset[str],
    *,
    pairs: list[dict[str, object]] | None = None,
) -> list[dict[str, object]]:
    cases = [
        dict(case)
        for case in catalogue
        if case.get("realistic_tier") and not case.get("expect_uncertain")
    ]
    journey_queries: list[tuple[str, list[str]]] = []
    if journeys_path.is_file():
        journeys = json.loads(journeys_path.read_text(encoding="utf-8"))
        if isinstance(journeys, list):
            for journey in journeys:
                if not isinstance(journey, dict):
                    continue
                for step in journey.get("steps", []):
                    if not isinstance(step, dict):
                        continue
                    args = step.get("arguments", {})
                    expect = step.get("expect", {})
                    if not isinstance(args, dict) or not isinstance(expect, dict):
                        continue
                    query = args.get("query")
                    skill_id = expect.get("top_skill_id") or expect.get("resolved_skill_id")
                    if isinstance(query, str) and isinstance(skill_id, str):
                        journey_queries.append((query, [skill_id]))
    seen_queries = {str(case["query"]) for case in cases}
    for index, (query, skill_ids) in enumerate(journey_queries, start=1):
        if query in seen_queries:
            continue
        cases.append(
            {
                "id": f"journey_harvest_{index:02d}",
                "query": query,
                "expected_skill_ids": skill_ids,
                "required_skill_ids": skill_ids[:1],
                "expect_uncertain": False,
                "query_source": "journey",
                "query_archetype": "task",
                "naturalness": "high",
                "promotion_tier": "release",
            }
        )
        seen_queries.add(query)
    pair_rows = pairs if pairs is not None else load_cases(CONFUSER_PAIRS_PATH)
    satisfied_pairs: set[tuple[str, str]] = set()
    seen_ids = {str(case.get("id", "")) for case in cases}
    for case in cases:
        expected_raw = case.get("expected_skill_ids", [])
        excluded_raw = case.get("excluded_skill_ids", [])
        expected_list = expected_raw if isinstance(expected_raw, list) else []
        excluded_list = excluded_raw if isinstance(excluded_raw, list) else []
        expected = {item for item in expected_list if isinstance(item, str)}
        excluded = {item for item in excluded_list if isinstance(item, str)}
        for preferred in expected:
            for confuser in excluded:
                satisfied_pairs.add((preferred, confuser))
    for case in _confuser_realistic_cases(pair_rows):
        case_id = str(case["id"])
        if case_id in seen_ids:
            continue
        expected_ids = case["expected_skill_ids"]
        excluded_ids = case["excluded_skill_ids"]
        if not isinstance(expected_ids, list) or not isinstance(excluded_ids, list):
            continue
        if not expected_ids or not excluded_ids:
            continue
        preferred = str(expected_ids[0])
        confuser = str(excluded_ids[0])
        if (preferred, confuser) in satisfied_pairs:
            continue
        query = str(case["query"])
        if query in seen_queries:
            case = dict(case)
            case["query"] = f"{query} [{case_id}]"
            query = str(case["query"])
        cases.append(case)
        seen_queries.add(query)
        seen_ids.add(case_id)
        satisfied_pairs.add((preferred, confuser))
    for case in cases:
        case.setdefault("query_source", "curated")
        case.setdefault("naturalness", "high")
        case["promotion_tier"] = _promotion_tier_for_case(case, promoted_ids)
    return cases


def write_cases(path: Path, cases: list[dict[str, object]]) -> None:
    path.write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")


def emit_stubs(catalogue_path: Path, skills_root: Path) -> int:
    records = extract_skills_graph_records(skills_root)
    promoted = {
        str(skill["name"])
        for skill in _graph_skills(records)
        if str(skill.get("promotion_status", "")) == "promoted"
    }
    catalogue = load_cases(catalogue_path)
    covered = {
        skill_id.removeprefix("skill:")
        for case in catalogue
        for skill_id in _skill_id_set(case.get("expected_skill_ids"))
    }
    missing = sorted(promoted - covered)
    for name in missing:
        catalogue.append(
            {
                "id": f"TODO_stub_{name.replace('-', '_')}",
                "query": f"TODO: add curated query for {name}",
                "expected_skill_ids": [f"skill:{name}"],
                "required_skill_ids": [f"skill:{name}"],
                "expect_uncertain": False,
                "query_source": "curated",
                "query_archetype": "task",
                "naturalness": "high",
                "promotion_tier": "release",
                "review_status": "TODO",
            }
        )
    write_cases(catalogue_path, catalogue)
    print(f"added {len(missing)} stub(s) to {catalogue_path.relative_to(REPO_ROOT)}")
    return 0


def archive_shadow_baseline(
    *,
    legacy_path: Path,
    new_union: list[dict[str, object]],
) -> None:
    legacy_cases = load_cases(legacy_path)
    positives = [case for case in legacy_cases if case.get("expected_skill_ids")]
    rng = random.Random(SHADOW_SEED)
    sample = (
        rng.sample(positives, min(SHADOW_LEGACY_SAMPLE_SIZE, len(positives))) if positives else []
    )
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_PATH.write_text(
        json.dumps(
            {
                "legacy_template_sample_size": len(sample),
                "legacy_template_sample_ids": [case.get("id") for case in sample],
                "new_tier_union_size": len(new_union),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def generate_tier(
    tier: str,
    *,
    skills_root: Path,
) -> list[dict[str, object]]:
    records = extract_skills_graph_records(skills_root)
    skills = _graph_skills(records)
    promoted_ids = frozenset(
        str(skill["id"]) for skill in skills if str(skill.get("promotion_status", "")) == "promoted"
    )
    skills = sorted(skills, key=lambda skill: str(skill["name"]))
    catalogue = load_cases(CATALOGUE_PATH)
    abstention = load_cases(ABSTENTION_PATH)
    pairs = load_cases(CONFUSER_PAIRS_PATH)

    if tier == "catalogue":
        return catalogue
    if tier == "abstention":
        return abstention
    if tier == "coverage":
        return build_coverage_cases(
            skills, skills_root=skills_root, pairs=pairs, promoted_ids=promoted_ids
        )
    if tier == "smoke":
        return build_smoke_cases(catalogue, abstention, promoted_ids)
    if tier == "realistic":
        return build_realistic_cases(
            catalogue,
            REPO_ROOT / "tests" / "fixtures" / "agent_journeys.json",
            promoted_ids,
            pairs=pairs,
        )
    if tier == "all":
        coverage = build_coverage_cases(
            skills, skills_root=skills_root, pairs=pairs, promoted_ids=promoted_ids
        )
        realistic = build_realistic_cases(
            catalogue,
            REPO_ROOT / "tests" / "fixtures" / "agent_journeys.json",
            promoted_ids,
            pairs=pairs,
        )
        smoke = build_smoke_cases(catalogue, abstention, promoted_ids)
        return smoke + realistic + coverage + abstention
    raise ValueError(f"unknown tier: {tier}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate tiered retrieval evaluation corpora.")
    parser.add_argument(
        "--tier",
        choices=["catalogue", "smoke", "realistic", "coverage", "abstention", "all"],
        default="all",
    )
    parser.add_argument("--skills-root", default=str(REPO_ROOT / "skills"))
    parser.add_argument("--emit-stubs", action="store_true")
    parser.add_argument("--write-legacy-golden", action="store_true")
    args = parser.parse_args(argv)
    skills_root = Path(args.skills_root)

    if args.emit_stubs:
        return emit_stubs(CATALOGUE_PATH, skills_root)

    cases = generate_tier(args.tier, skills_root=skills_root)
    outputs = {
        "catalogue": CATALOGUE_PATH,
        "smoke": SMOKE_PATH,
        "realistic": REALISTIC_PATH,
        "coverage": COVERAGE_PATH,
        "abstention": ABSTENTION_PATH,
    }
    if args.tier == "all":
        smoke = generate_tier("smoke", skills_root=skills_root)
        realistic = generate_tier("realistic", skills_root=skills_root)
        coverage = generate_tier("coverage", skills_root=skills_root)
        abstention = generate_tier("abstention", skills_root=skills_root)
        write_cases(SMOKE_PATH, smoke)
        write_cases(REALISTIC_PATH, realistic)
        write_cases(COVERAGE_PATH, coverage)
        write_cases(ABSTENTION_PATH, abstention)
        union = smoke + realistic + coverage + abstention
        if args.write_legacy_golden:
            write_cases(LEGACY_GOLDEN_PATH, union)
        if LEGACY_GOLDEN_PATH.is_file():
            archive_shadow_baseline(legacy_path=LEGACY_GOLDEN_PATH, new_union=union)
        from scripts.validate_eval_corpus import build_coverage_matrix

        matrix = build_coverage_matrix(coverage)
        MATRIX_PATH.write_text(json.dumps(matrix, indent=2) + "\n", encoding="utf-8")
        print(
            f"wrote smoke={len(smoke)} realistic={len(realistic)} coverage={len(coverage)} abstention={len(abstention)}"
        )
        return 0

    write_cases(outputs[args.tier], cases)
    print(f"wrote {len(cases)} cases to {outputs[args.tier].relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
