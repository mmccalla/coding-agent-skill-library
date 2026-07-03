"""Phase 8 promoted-release evaluation gate tests."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.evaluate_skill_retrieval import (
    DEFAULT_DATASET,
    evaluate_offline,
    filter_cases_by_promotion,
    load_cases,
    load_promoted_skill_ids,
)
from scripts.report_skill_usage import build_usage_report, zero_hit_promoted_skills

REPO_ROOT = Path(__file__).resolve().parents[1]


class EvaluatePromotedReleaseGateTests(unittest.TestCase):
    def test_promoted_eligible_case_filter_meets_minimum(self) -> None:
        promoted_ids = load_promoted_skill_ids(REPO_ROOT / "skills")
        all_cases = load_cases(DEFAULT_DATASET)
        eligible = filter_cases_by_promotion(
            all_cases,
            promoted_ids,
            case_filter="promoted_eligible",
        )
        self.assertGreaterEqual(len(eligible), 150)

    def test_promoted_release_eval_arm_runs(self) -> None:
        report = evaluate_offline(
            DEFAULT_DATASET,
            limit=3,
            case_filter="promoted_eligible",
            skills_root=REPO_ROOT / "skills",
            recall_threshold=0.0,
            mrr_threshold=0.0,
            source_threshold=0.0,
            uncertainty_threshold=0.0,
        )
        self.assertGreaterEqual(report.cases, 150)
        self.assertGreaterEqual(report.graph_lift_recall_at_k, 0.0)

    def test_usage_report_lists_zero_hit_promoted_skills(self) -> None:
        promoted_ids = load_promoted_skill_ids(REPO_ROOT / "skills")
        zero_hits = zero_hit_promoted_skills(promoted_ids, {})
        self.assertEqual(len(promoted_ids), len(zero_hits))
        report = build_usage_report(skills_root=REPO_ROOT / "skills")
        self.assertGreaterEqual(int(report["promoted_skill_count"]), 30)
        self.assertIn("zero_hit_promoted_skills", report)


if __name__ == "__main__":
    unittest.main()
