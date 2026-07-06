"""Tests for scripts/utils/ci/ci_ingest_gate.py."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.utils.ci.ci_ingest_gate import run_delta_eval_step, run_ingest_gate

REPO_ROOT = Path(__file__).resolve().parents[1]


class CiIngestGateTests(unittest.TestCase):
    def test_ingest_gate_passes_for_repository(self) -> None:
        report = run_ingest_gate(skills_root=REPO_ROOT / "skills")
        self.assertTrue(report.passed, report.steps)
        step_names = {step.name for step in report.steps}
        self.assertIn("validate_skill_trust_l2", step_names)
        self.assertIn("validate_skills_graph", step_names)
        self.assertIn("validate_skills_ontology_shacl", step_names)
        self.assertIn("validate_eval_corpus", step_names)
        self.assertIn("delta_eval_changed_skills", step_names)
        self.assertIn("evaluate_promoted_retrieval_smoke", step_names)
        self.assertIn("dry_run_load", step_names)

    def test_delta_eval_passes_for_touched_skill(self) -> None:
        step = run_delta_eval_step(
            skills_root=REPO_ROOT / "skills",
            retrieval_limit=3,
            changed_skill_names=frozenset({"tdd-practice"}),
        )
        self.assertTrue(step.passed, step.detail)
        self.assertIn("precision@1=1.000", step.detail)


if __name__ == "__main__":
    unittest.main()
