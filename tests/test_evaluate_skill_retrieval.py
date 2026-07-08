"""Tests for retrieval evaluation gates."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.lib.retrieval.evaluate_skill_retrieval import (
    EvaluationCase,
    _is_alias_lookup_case,
    evaluate_offline,
    load_cases,
)
from scripts.validators.validate_skills import parse_frontmatter

DATASET = Path("tests/fixtures/retrieval_evaluation/golden_queries.json")
COVERAGE_DATASET = Path("tests/fixtures/retrieval_evaluation/coverage_queries.json")
ABSTENTION_DATASET = Path("tests/fixtures/retrieval_evaluation/abstention_probes.json")
FULL_SMOKE_DATASET = Path("tests/fixtures/retrieval_evaluation/smoke_queries.json")
PROMOTED_SMOKE_DATASET = Path("tests/fixtures/retrieval_evaluation/smoke_queries_promoted.json")
SMOKE_DATASET = PROMOTED_SMOKE_DATASET
SKILLS_ROOT = Path("skills")


def _expected_skill_ids() -> set[str]:
    skill_ids: set[str] = set()
    for path in sorted(SKILLS_ROOT.glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        frontmatter_end = text.find("\n---\n", 4)
        frontmatter = parse_frontmatter(text[4:frontmatter_end])
        skill_ids.add(f"skill:{frontmatter['name']}")
    return skill_ids


class EvaluateSkillRetrievalTests(unittest.TestCase):
    def test_tiered_corpora_contract(self) -> None:
        golden = load_cases(DATASET)
        coverage = load_cases(COVERAGE_DATASET)
        abstention = load_cases(ABSTENTION_DATASET)
        smoke = load_cases(SMOKE_DATASET)

        self.assertGreaterEqual(len(golden), 200)
        self.assertLessEqual(len(golden), 360)
        self.assertGreaterEqual(len(coverage), 180)
        self.assertGreaterEqual(len(abstention), 10)
        self.assertGreaterEqual(len(smoke), 8)

        case_ids = {case.id for case in golden}
        self.assertIn("kg_rag", case_ids)
        self.assertIn("krag_system_design", case_ids)

        positives = [case for case in coverage if case.expected_skill_ids]
        covered_skill_ids = {
            skill_id for case in positives for skill_id in case.expected_skill_ids if skill_id
        }
        self.assertEqual(_expected_skill_ids(), covered_skill_ids)

        for case in abstention:
            self.assertTrue(case.expect_uncertain)
            self.assertEqual((), case.expected_skill_ids)

    def test_smoke_dataset_preserves_curated_cases(self) -> None:
        cases = load_cases(SMOKE_DATASET)

        self.assertGreaterEqual(len(cases), 8)
        case_ids = {case.id for case in cases}
        self.assertIn("tdd_practice", case_ids)
        self.assertIn("krag_system_design", case_ids)
        self.assertIn("abstain_nonsense_tokens", case_ids)

    def test_alias_lookup_case_detects_embedded_alias_phrases(self) -> None:
        case = EvaluationCase(
            id="alias_embedded_phrase",
            query="when should I use ai-safety-laws",
            expected_skill_ids=("skill:apply-laws-of-ai",),
        )
        alias_map = {
            "skill:apply-laws-of-ai": (
                "ai-safety-laws",
                "asimov-inspired-ai-laws",
            )
        }

        self.assertTrue(_is_alias_lookup_case(case, alias_map))

    def test_offline_evaluation_meets_quality_gate(self) -> None:
        report = evaluate_offline(SMOKE_DATASET, limit=3, source_threshold=0.5)

        self.assertTrue(report.passed, report.model_dump())
        self.assertGreaterEqual(report.cases, 8)
        self.assertGreaterEqual(report.precision_at_1, 1.0)
        self.assertGreaterEqual(report.recall_at_k, 1.0)
        self.assertGreaterEqual(report.mean_reciprocal_rank, 1.0)
        self.assertGreaterEqual(report.ndcg_at_k, 1.0)
        self.assertGreaterEqual(report.source_coverage, 1.0)
        self.assertGreaterEqual(report.citation_coverage, 1.0)
        self.assertGreaterEqual(report.exclusion_accuracy, 0.5)
        self.assertGreaterEqual(report.uncertainty_accuracy, 1.0)
        self.assertGreaterEqual(report.selection_trace_coverage, 1.0)
        self.assertGreaterEqual(report.query_plan_coverage, 1.0)
        self.assertGreaterEqual(report.graph_lift_recall_at_k, 0.0)
        self.assertGreaterEqual(report.p95_latency_ms, 0.0)
        self.assertGreaterEqual(len(report.case_results), 8)
        self.assertTrue(all(result.graph_query_plan_present for result in report.case_results))
        self.assertTrue(all(result.selection_trace_present for result in report.case_results))


if __name__ == "__main__":
    unittest.main()
