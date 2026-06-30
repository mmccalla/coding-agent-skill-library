"""Tests for the Phase 7 KRAG cutover acceptance harness."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.krag_cutover_acceptance import run_cutover_acceptance

SMOKE_DATASET = Path("tests/fixtures/retrieval_evaluation/smoke_queries.json")


class KragCutoverAcceptanceTests(unittest.TestCase):
    def test_cutover_acceptance_report_passes_for_smoke_dataset(self) -> None:
        report = run_cutover_acceptance(SMOKE_DATASET, limit=3, token_budget=240)

        self.assertTrue(report.passed, report.model_dump())
        self.assertTrue(report.ontology_validation_passed)
        self.assertTrue(report.minimal_krag_slice_passed)
        self.assertGreater(report.skill_count, 0)
        self.assertGreaterEqual(report.retrieval_unit_count, report.skill_count)
        self.assertGreater(report.mean_manual_loading_token_cost, report.mean_bounded_token_cost)
        self.assertTrue(all(check.passed for check in report.acceptance_checks))
        recommendation = next(
            scenario for scenario in report.runtime_scenarios if scenario.id == "recommendation"
        )
        self.assertEqual("recommendation", recommendation.route)
        self.assertEqual("capability_task_lookup", recommendation.query_family)
        self.assertEqual("ok", recommendation.graph_query_status)
        self.assertEqual("skill:knowledge-graph-rag", recommendation.selected_skill_id)
        self.assertIn("LIMIT $limit", recommendation.generated_cypher)
        self.assertFalse(recommendation.uncertain)


if __name__ == "__main__":
    unittest.main()
