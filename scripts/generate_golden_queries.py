#!/usr/bin/env python3
"""Generate a large golden retrieval evaluation dataset from the installed skill library."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.extract_skills_graph import extract_skills_graph_records

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO_ROOT / "tests" / "fixtures" / "retrieval_evaluation" / "golden_queries.json"
MIN_CASES = 500
TEMPLATES = (
    "{name}",
    "tell me about {name}",
    "how do I apply {name}",
    "when should I use {name}",
    "explain {name}",
    "execution guide for {name}",
    "{name} skill overview: {description}",
    "I need the {name} skill. {description}",
    "what does {name} cover? {description}",
    "how to implement {name} based on this guidance: {description}",
    "use {name} when {description_fragment}",
)
NEGATIVE_CASES_PER_SKILL = 2
SEED_CASES = (
    {
        "id": "kg_rag",
        "query": "neo4j-native kg-backed retrieval with text-to-cypher and provenance",
        "expected_skill_ids": ["skill:knowledge-graph-rag"],
        "expect_uncertain": False,
    },
    {
        "id": "krag_system_design",
        "query": "KRAG architecture summary graph schema outline retrieval strategy implementation backlog thin vertical slices",
        "expected_skill_ids": ["skill:krag-system-design"],
        "required_skill_ids": ["skill:krag-system-design"],
        "excluded_skill_ids": [
            "skill:accessibility-wcag",
            "skill:ci-cd-and-automation",
            "skill:knowledge-graph-rag",
            "skill:ontology-and-knowledge-graph-modeling",
        ],
        "expect_uncertain": False,
        "promotion_tier": "release",
    },
    {
        "id": "krag_ingestion_graph_construction",
        "query": "KRAG ingestion design graph schema changes validation rules idempotency strategy failure handling",
        "expected_skill_ids": ["skill:krag-ingestion-graph-construction"],
        "required_skill_ids": ["skill:krag-ingestion-graph-construction"],
        "excluded_skill_ids": ["skill:ux-design-principles", "skill:dora-four-keys"],
        "expect_uncertain": False,
    },
    {
        "id": "krag_retrieval_answering",
        "query": "KRAG retrieval plan queries pseudocode evidence set citations uncertainty follow up data gaps",
        "expected_skill_ids": ["skill:krag-retrieval-answering"],
        "required_skill_ids": ["skill:krag-retrieval-answering"],
        "excluded_skill_ids": [
            "skill:release-engineering-and-progressive-delivery",
            "skill:business-capability-modeling",
        ],
        "expect_uncertain": False,
    },
    {
        "id": "krag_evaluation_governance",
        "query": "KRAG evaluation plan metrics acceptance thresholds release gates monitoring signals remediation actions",
        "expected_skill_ids": ["skill:krag-evaluation-governance"],
        "required_skill_ids": ["skill:krag-evaluation-governance"],
        "excluded_skill_ids": ["skill:ui-component-design", "skill:event-modeling"],
        "expect_uncertain": False,
    },
    {
        "id": "human_approval",
        "query": "approval before destructive command human review",
        "expected_skill_ids": ["skill:human-in-the-loop"],
        "required_skill_ids": ["skill:human-in-the-loop"],
        "excluded_skill_ids": ["skill:agentic-ux-patterns", "skill:git-workflow-and-versioning"],
        "expect_uncertain": False,
        "promotion_tier": "release",
    },
    {
        "id": "confuser_guardrails_vs_hitl",
        "query": "policy enforcement tool restrictions before destructive actions",
        "expected_skill_ids": ["skill:guardrails-safety-patterns"],
        "required_skill_ids": ["skill:guardrails-safety-patterns"],
        "excluded_skill_ids": ["skill:human-in-the-loop"],
        "expect_uncertain": False,
        "promotion_tier": "release",
    },
    {
        "id": "confuser_rag_vs_krag_retrieval",
        "query": "retrieval augmented generation document grounding citations",
        "expected_skill_ids": ["skill:knowledge-retrieval-rag"],
        "required_skill_ids": ["skill:knowledge-retrieval-rag"],
        "excluded_skill_ids": ["skill:krag-retrieval-answering"],
        "expect_uncertain": False,
        "promotion_tier": "release",
    },
    {
        "id": "accessibility",
        "query": "keyboard focus accessible form labels",
        "expected_skill_ids": ["skill:accessibility-wcag"],
        "expect_uncertain": False,
    },
    {
        "id": "event_streaming_iceberg_pipeline",
        "query": "I've been instructed to build an event driven and real time data streaming pipeline that stores data in iceberg tables using apache pulsar and apache flink. How should this be done?",
        "expected_skill_ids": [
            "skill:streaming-operations-and-slos",
            "skill:event-streaming-platform-design",
            "skill:stream-processing-patterns",
            "skill:lakehouse-and-medallion-architecture",
        ],
        "required_skill_ids": [
            "skill:event-streaming-platform-design",
            "skill:stream-processing-patterns",
        ],
        "excluded_skill_ids": [
            "skill:accessibility-wcag",
            "skill:ci-cd-and-automation",
            "skill:ddd-practice",
            "skill:dora-four-keys",
        ],
        "expect_uncertain": False,
    },
    {
        "id": "absent",
        "query": "zzzz qqqq nonsense",
        "expected_skill_ids": [],
        "expect_uncertain": True,
    },
)


def _description_fragment(description: str) -> str:
    fragment = description
    if ". " in fragment:
        fragment = fragment.split(". ", 1)[0]
    fragment = re.sub(r"\s+", " ", fragment).strip()
    return fragment.rstrip(".")


def _promotion_tier_for_case(
    case: dict[str, object],
    promoted_ids: frozenset[str],
) -> str:
    expected = set(case.get("expected_skill_ids", [])) | set(case.get("required_skill_ids", []))
    if case.get("promotion_tier"):
        return str(case["promotion_tier"])
    if not expected:
        return "release"
    if expected <= promoted_ids:
        return "release"
    if expected & promoted_ids:
        return "release"
    return "diagnostic"


def build_cases() -> list[dict[str, object]]:
    records = extract_skills_graph_records(REPO_ROOT / "skills")
    promoted_ids = frozenset(
        str(skill["id"])
        for skill in records["skills"]
        if str(skill.get("promotion_status", "")) == "promoted"
    )
    skills = sorted(records["skills"], key=lambda skill: str(skill["name"]))
    cases: list[dict[str, object]] = [dict(case) for case in SEED_CASES]

    for skill in skills:
        name = str(skill["name"])
        description = str(skill["description"])
        skill_id = str(skill["id"])
        description_fragment = _description_fragment(description)
        for index, template in enumerate(TEMPLATES, start=1):
            query = template.format(
                name=name,
                description=description,
                description_fragment=description_fragment,
            )
            cases.append(
                {
                    "id": f"{name.replace('-', '_')}_generated_{index:02d}",
                    "query": query,
                    "expected_skill_ids": [skill_id],
                    "required_skill_ids": [skill_id],
                    "excluded_skill_ids": [],
                    "expect_uncertain": False,
                }
            )
        for negative_index in range(1, NEGATIVE_CASES_PER_SKILL + 1):
            cases.append(
                {
                    "id": f"{name.replace('-', '_')}_negative_{negative_index:02d}",
                    "query": (
                        f"zzqp qxjv{name.count('-')}{negative_index} "
                        f"blorf{len(name)} "
                        f"nzpt{len(description_fragment)} "
                        f"yqqx{negative_index}{len(skill_id)}"
                    ),
                    "expected_skill_ids": [],
                    "required_skill_ids": [],
                    "excluded_skill_ids": [skill_id],
                    "expect_uncertain": True,
                }
            )

    for case in cases:
        case["promotion_tier"] = _promotion_tier_for_case(case, promoted_ids)

    if len(cases) < MIN_CASES:
        raise ValueError(f"expected at least {MIN_CASES} cases, generated {len(cases)}")
    return cases


def main() -> int:
    cases = build_cases()
    DEFAULT_OUTPUT.write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(cases)} cases to {DEFAULT_OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
