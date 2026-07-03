"""Tests for retrieval evaluation gates."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.evaluate_skill_retrieval import (
    _is_alias_lookup_case,
    EvaluationCase,
    evaluate_offline,
    load_cases,
)
from scripts.validate_skills import parse_frontmatter

DATASET = Path("tests/fixtures/retrieval_evaluation/golden_queries.json")
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
    def test_load_cases_requires_large_golden_query_contract(self) -> None:
        cases = load_cases(DATASET)

        self.assertGreaterEqual(len(cases), 500)
        case_ids = {case.id for case in cases}
        self.assertIn("kg_rag", case_ids)
        self.assertIn("krag_system_design", case_ids)
        self.assertIn("krag_ingestion_graph_construction", case_ids)
        self.assertIn("krag_retrieval_answering", case_ids)
        self.assertIn("krag_evaluation_governance", case_ids)
        positives = [case for case in cases if case.expected_skill_ids]
        negatives = [case for case in cases if case.expect_uncertain]
        self.assertGreaterEqual(len(positives), 500)
        self.assertGreaterEqual(len(negatives), 50)
        self.assertTrue(any(case.id == "library_negative_01" for case in negatives))

        covered_skill_ids = {
            skill_id for case in positives for skill_id in case.expected_skill_ids if skill_id
        }
        self.assertEqual(_expected_skill_ids(), covered_skill_ids)

        for case in negatives:
            self.assertEqual((), case.expected_skill_ids)
            self.assertEqual((), case.required_skill_ids)

        self.assertTrue(any(case.required_skill_ids for case in positives))
        for case in positives:
            if case.required_skill_ids:
                self.assertTrue(set(case.required_skill_ids).issubset(set(case.expected_skill_ids)))

    def test_smoke_dataset_preserves_curated_cases(self) -> None:
        cases = load_cases(FULL_SMOKE_DATASET)

        self.assertEqual(9, len(cases))
        self.assertEqual("kg_rag", cases[0].id)
        self.assertEqual(("skill:knowledge-graph-rag",), cases[0].expected_skill_ids)
        self.assertEqual("krag_system_design", cases[1].id)
        self.assertEqual(("skill:krag-system-design",), cases[1].required_skill_ids)
        self.assertEqual("krag_evaluation_governance", cases[4].id)
        self.assertEqual(("skill:krag-evaluation-governance",), cases[4].expected_skill_ids)
        self.assertEqual("event_streaming_iceberg_pipeline", cases[7].id)
        self.assertIn("skill:event-streaming-platform-design", cases[7].required_skill_ids)
        self.assertIn("skill:accessibility-wcag", cases[7].excluded_skill_ids)

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
        report = evaluate_offline(SMOKE_DATASET, limit=3)

        self.assertTrue(report.passed, report.model_dump())
        self.assertEqual(6, report.cases)
        self.assertGreaterEqual(report.precision_at_1, 1.0)
        self.assertGreaterEqual(report.recall_at_k, 1.0)
        self.assertGreaterEqual(report.mean_reciprocal_rank, 1.0)
        self.assertGreaterEqual(report.ndcg_at_k, 1.0)
        self.assertGreaterEqual(report.source_coverage, 1.0)
        self.assertGreaterEqual(report.citation_coverage, 1.0)
        self.assertGreaterEqual(report.exclusion_accuracy, 1.0)
        self.assertGreaterEqual(report.uncertainty_accuracy, 1.0)
        self.assertGreaterEqual(report.selection_trace_coverage, 1.0)
        self.assertGreaterEqual(report.query_plan_coverage, 1.0)
        self.assertGreaterEqual(report.graph_lift_recall_at_k, 0.0)
        self.assertGreaterEqual(report.p95_latency_ms, 0.0)
        self.assertEqual(6, len(report.case_results))
        self.assertTrue(all(result.graph_query_plan_present for result in report.case_results))
        self.assertTrue(all(result.selection_trace_present for result in report.case_results))


if __name__ == "__main__":
    unittest.main()
