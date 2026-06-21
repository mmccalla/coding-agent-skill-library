"""Tests for retrieval evaluation gates."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.evaluate_skill_retrieval import evaluate_offline, load_cases

DATASET = Path("tests/fixtures/retrieval_evaluation/golden_queries.json")


class EvaluateSkillRetrievalTests(unittest.TestCase):
    def test_load_cases_requires_expected_skill_contract(self) -> None:
        cases = load_cases(DATASET)

        self.assertEqual(5, len(cases))
        self.assertEqual("kg_rag", cases[0].id)
        self.assertEqual(("skill:kg-enabled-rag",), cases[0].expected_skill_ids)
        self.assertEqual("event_streaming_iceberg_pipeline", cases[3].id)
        self.assertIn("skill:event-streaming-platform-design", cases[3].required_skill_ids)
        self.assertIn("skill:accessibility-wcag", cases[3].excluded_skill_ids)

    def test_offline_evaluation_meets_quality_gate(self) -> None:
        report = evaluate_offline(DATASET, limit=3)

        self.assertTrue(report.passed, report.model_dump())
        self.assertGreaterEqual(report.recall_at_k, 1.0)
        self.assertGreaterEqual(report.mean_reciprocal_rank, 1.0)
        self.assertGreaterEqual(report.source_coverage, 1.0)
        self.assertGreaterEqual(report.uncertainty_accuracy, 1.0)


if __name__ == "__main__":
    unittest.main()
