"""Realistic end-to-end retrieval evaluation across curated use cases."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.evaluate_skill_retrieval import evaluate_offline, load_cases
from scripts.run_e2e_retrieval_eval import REALISTIC_DATASET, run_realistic_e2e

REPO_ROOT = Path(__file__).resolve().parents[1]
GOLDEN_DATASET = REPO_ROOT / "tests/fixtures/retrieval_evaluation/golden_queries.json"

# Honest realistic thresholds: precision@1 is the primary gate. Exclusion of related
# skills at ranks 2-3 is measured but not required to be perfect because the graph
# deliberately links complement skills.
REALISTIC_PRECISION_AT_1 = 1.0
REALISTIC_EXCLUSION_ACCURACY = 0.5
RELEASE_PRECISION_AT_1 = 0.98
RELEASE_RECALL_AT_K = 0.98
RELEASE_CITATION_COVERAGE = 0.95


class RealisticE2eRetrievalTests(unittest.TestCase):
    def test_realistic_confuser_dataset_passes(self) -> None:
        report = evaluate_offline(
            REALISTIC_DATASET,
            limit=3,
            recall_threshold=0.0,
            mrr_threshold=0.0,
            source_threshold=0.0,
            uncertainty_threshold=0.0,
            skills_root=REPO_ROOT / "skills",
        )
        self.assertGreaterEqual(report.cases, 8)
        self.assertGreaterEqual(report.precision_at_1, REALISTIC_PRECISION_AT_1)
        self.assertGreaterEqual(report.recall_at_k, REALISTIC_PRECISION_AT_1)
        self.assertGreaterEqual(report.exclusion_accuracy, REALISTIC_EXCLUSION_ACCURACY)
        self.assertGreaterEqual(report.uncertainty_accuracy, 1.0)
        rank_failures = [
            result
            for result in report.case_results
            if any("expected one of" in failure for failure in result.failures)
        ]
        self.assertEqual([], rank_failures, [item.failures for item in rank_failures])

    def test_release_arm_meets_honest_thresholds(self) -> None:
        report = evaluate_offline(
            GOLDEN_DATASET,
            limit=3,
            recall_threshold=0.0,
            mrr_threshold=0.0,
            source_threshold=0.0,
            uncertainty_threshold=0.0,
            case_filter="promoted_eligible",
            skills_root=REPO_ROOT / "skills",
        )
        self.assertGreaterEqual(report.cases, 550)
        self.assertGreaterEqual(report.precision_at_1, RELEASE_PRECISION_AT_1)
        self.assertGreaterEqual(report.recall_at_k, RELEASE_RECALL_AT_K)
        self.assertGreaterEqual(report.citation_coverage, RELEASE_CITATION_COVERAGE)

    def test_golden_cases_tagged_with_promotion_tier(self) -> None:
        cases = load_cases(GOLDEN_DATASET)
        tiers = {case.promotion_tier for case in cases}
        self.assertIn("release", tiers)
        self.assertGreaterEqual(sum(1 for case in cases if case.promotion_tier == "release"), 550)

    def test_e2e_runner_reports_all_arms(self) -> None:
        payload = run_realistic_e2e(skills_root=REPO_ROOT / "skills", golden_dataset=GOLDEN_DATASET)
        self.assertGreaterEqual(int(payload["promoted_skill_count"]), 90)
        self.assertIn("release_arm", payload)
        self.assertIn("full_corpus_arm", payload)
        self.assertIn("realistic_confuser_arm", payload)
        self.assertTrue(payload["cutover_acceptance_passed"])
        realistic = payload["realistic_confuser_arm"]
        self.assertGreaterEqual(realistic["precision_at_1"], REALISTIC_PRECISION_AT_1)
        self.assertEqual(0, len(realistic["rank_failures"]))


if __name__ == "__main__":
    unittest.main()
