"""Realistic end-to-end retrieval evaluation across curated use cases."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pytest

from scripts.lib.retrieval.evaluate_skill_retrieval import evaluate_offline, load_cases
from scripts.lib.retrieval.run_e2e_retrieval_eval import REALISTIC_DATASET, run_realistic_e2e

REPO_ROOT = Path(__file__).resolve().parents[1]
COVERAGE_DATASET = REPO_ROOT / "tests/fixtures/retrieval_evaluation/coverage_queries.json"
ABSTENTION_DATASET = REPO_ROOT / "tests/fixtures/retrieval_evaluation/abstention_probes.json"
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
    def _assert_realistic_case_top1(self, case_id: str, expected_skill_id: str) -> None:
        cases = [case for case in load_cases(REALISTIC_DATASET) if case.id == case_id]
        self.assertEqual(1, len(cases), case_id)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / f"{case_id}.json"
            path.write_text(
                json.dumps(
                    [
                        {
                            "id": cases[0].id,
                            "query": cases[0].query,
                            "expected_skill_ids": list(cases[0].expected_skill_ids),
                            "required_skill_ids": list(cases[0].required_skill_ids),
                            "excluded_skill_ids": list(cases[0].excluded_skill_ids),
                            "expect_uncertain": cases[0].expect_uncertain,
                        }
                    ]
                ),
                encoding="utf-8",
            )
            report = evaluate_offline(
                path,
                limit=3,
                recall_threshold=0.0,
                mrr_threshold=0.0,
                source_threshold=0.0,
                uncertainty_threshold=0.0,
                skills_root=REPO_ROOT / "skills",
            )
        self.assertEqual(1, report.cases)
        self.assertGreaterEqual(report.precision_at_1, 1.0, report.case_results)
        top1 = report.case_results[0].ranked_skill_ids[0]
        self.assertEqual(expected_skill_id, top1)

    def test_conceptual_data_model_precision_at_1(self) -> None:
        """Pin confuser: conceptual modelling must not lose to ontology aliases."""
        self._assert_realistic_case_top1(
            "conceptual_data_model",
            "skill:conceptual-data-modeling",
        )

    def test_krag_evaluation_cases_beat_generic_monitoring(self) -> None:
        """Pin confuser: KRAG eval queries must not lose to evaluation-and-monitoring."""
        self._assert_realistic_case_top1(
            "krag_evaluation_governance",
            "skill:krag-evaluation-governance",
        )
        self._assert_realistic_case_top1(
            "krag_eval_vs_monitoring",
            "skill:krag-evaluation-governance",
        )

    def test_sre_confuser_precision_at_1(self) -> None:
        """Pin confuser: broad SRE task must not resolve to incident-response via alias embed."""
        self._assert_realistic_case_top1(
            "sre_vs_observability_confuser",
            "skill:sre-practice",
        )

    def test_journey_harvest_11_fallacy_beats_adr_docs(self) -> None:
        """Pin confuser: fallacy review in an ADR context must top logical-fallacy-review."""
        self._assert_realistic_case_top1(
            "journey_harvest_11",
            "skill:logical-fallacy-review",
        )

    @pytest.mark.eval_pr
    def test_realistic_confuser_dataset_passes(self) -> None:
        report = evaluate_offline(
            REALISTIC_DATASET,
            limit=3,
            recall_threshold=0.0,
            mrr_threshold=0.0,
            source_threshold=0.5,
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

    @pytest.mark.eval_pr
    def test_abstention_probes_pass(self) -> None:
        report = evaluate_offline(
            ABSTENTION_DATASET,
            limit=3,
            recall_threshold=0.0,
            mrr_threshold=0.0,
            source_threshold=0.0,
            uncertainty_threshold=0.0,
            skills_root=REPO_ROOT / "skills",
        )
        self.assertGreaterEqual(report.cases, 10)
        self.assertGreaterEqual(report.uncertainty_accuracy, 0.9)

    @pytest.mark.slow
    def test_coverage_arm_meets_honest_thresholds(self) -> None:
        report = evaluate_offline(
            COVERAGE_DATASET,
            limit=3,
            recall_threshold=0.0,
            mrr_threshold=0.0,
            source_threshold=0.0,
            uncertainty_threshold=0.0,
            case_filter="promoted_eligible",
            skills_root=REPO_ROOT / "skills",
        )
        self.assertGreaterEqual(report.cases, 180)
        self.assertGreaterEqual(report.precision_at_1, RELEASE_PRECISION_AT_1)
        self.assertGreaterEqual(report.recall_at_k, RELEASE_RECALL_AT_K)
        self.assertGreaterEqual(report.citation_coverage, RELEASE_CITATION_COVERAGE)

    def test_golden_union_tagged_with_promotion_tier(self) -> None:
        cases = load_cases(GOLDEN_DATASET)
        tiers = {case.promotion_tier for case in cases}
        self.assertIn("release", tiers)
        self.assertGreaterEqual(sum(1 for case in cases if case.promotion_tier == "release"), 200)

    @pytest.mark.slow
    def test_e2e_runner_reports_all_arms(self) -> None:
        payload = run_realistic_e2e(skills_root=REPO_ROOT / "skills", golden_dataset=GOLDEN_DATASET)
        self.assertGreaterEqual(int(payload["promoted_skill_count"]), 90)
        self.assertIn("release_arm", payload)
        self.assertIn("full_corpus_arm", payload)
        self.assertIn("realistic_confuser_arm", payload)
        self.assertTrue(payload["smoke_promoted_passed"])
        realistic = payload["realistic_confuser_arm"]
        self.assertGreaterEqual(realistic["precision_at_1"], REALISTIC_PRECISION_AT_1)
        self.assertEqual(0, len(realistic["rank_failures"]))


if __name__ == "__main__":
    unittest.main()
