"""Tests for tiered evaluation corpus validation."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts import validate_eval_corpus
from scripts.ci_ingest_gate import (
    build_delta_eval_cases,
    discover_changed_skill_names,
    run_delta_eval_step,
)
from scripts.ci_ingest_gate import (
    main as ingest_gate_main,
)
from scripts.generate_golden_queries import generate_tier
from scripts.generate_golden_queries import main as generate_main

REPO_ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = REPO_ROOT / "tests" / "fixtures" / "retrieval_evaluation"


class ValidateEvalCorpusTests(unittest.TestCase):
    def test_tiered_corpora_pass_validation(self) -> None:
        result = validate_eval_corpus.validate_all(skills_root=REPO_ROOT / "skills")
        self.assertTrue(result.valid, result.errors)

    def test_validate_all_with_skill_sync(self) -> None:
        result = validate_eval_corpus.validate_all(
            skills_root=REPO_ROOT / "skills",
            check_sync=True,
        )
        self.assertTrue(result.valid, result.errors)

    def test_cli_json_output_passes(self) -> None:
        self.assertEqual(
            validate_eval_corpus.main(["--check-skill-sync", "--json"]),
            0,
        )

    def test_emit_matrix_writes_file(self) -> None:
        path = EVAL_DIR / "coverage_matrix_test.json"
        try:
            self.assertEqual(validate_eval_corpus.main(["--emit-matrix", str(path)]), 0)
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("skills", payload)
        finally:
            path.unlink(missing_ok=True)

    def test_coverage_matrix_includes_promoted_skills(self) -> None:
        cases = validate_eval_corpus.load_json_cases(EVAL_DIR / "coverage_queries.json")
        promoted = validate_eval_corpus.promoted_skill_ids(REPO_ROOT / "skills")
        matrix = validate_eval_corpus.build_coverage_matrix(cases)
        skills_map = matrix["skills"]
        assert isinstance(skills_map, dict)
        self.assertEqual(len(promoted), len(skills_map))

    def test_token_jaccard_detects_duplicates(self) -> None:
        self.assertGreater(
            validate_eval_corpus.token_jaccard(
                "fix defect failing test first",
                "fixing defect failing test first expectations",
            ),
            0.5,
        )
        self.assertLess(
            validate_eval_corpus.token_jaccard(
                "weather forecast london",
                "graph rag ontology retrieval",
            ),
            0.2,
        )

    def test_validate_tier_file_rejects_missing_path(self) -> None:
        result = validate_eval_corpus.validate_tier_file(
            Path("/tmp/does-not-exist-eval.json"),
            "smoke",
        )
        self.assertFalse(result.valid)

    def test_validate_case_schema_flags_invalid_case(self) -> None:
        errors = validate_eval_corpus.validate_case_schema(
            {"id": "bad", "query": "", "expect_uncertain": "yes", "expected_skill_ids": ()},
            tier="smoke",
            path=Path("smoke.json"),
        )
        self.assertGreaterEqual(len(errors), 2)


class CorpusGeneratorTests(unittest.TestCase):
    def test_generate_smoke_tier(self) -> None:
        cases = generate_tier("smoke", skills_root=REPO_ROOT / "skills")
        self.assertGreaterEqual(len(cases), 8)

    def test_generate_abstention_tier(self) -> None:
        cases = generate_tier("abstention", skills_root=REPO_ROOT / "skills")
        self.assertGreaterEqual(len(cases), 10)

    def test_generate_main_smoke_tier(self) -> None:
        self.assertEqual(generate_main(["--tier", "smoke"]), 0)

    def test_generate_main_realistic_tier(self) -> None:
        self.assertEqual(generate_main(["--tier", "realistic"]), 0)

    def test_generate_coverage_tier_in_memory(self) -> None:
        cases = generate_tier("coverage", skills_root=REPO_ROOT / "skills")
        self.assertGreaterEqual(len(cases), 180)


class CiIngestGateDeltaTests(unittest.TestCase):
    def test_discover_changed_skills_empty_when_forced_empty(self) -> None:
        names = discover_changed_skill_names(changed_skill_names=frozenset())
        self.assertEqual(names, frozenset())

    def test_build_delta_eval_cases_for_skill(self) -> None:
        cases = build_delta_eval_cases(frozenset({"tdd-practice"}))
        self.assertGreaterEqual(len(cases), 1)
        self.assertTrue(
            any("tdd-practice" in str(case.get("expected_skill_ids", [])) for case in cases)
        )

    def test_delta_eval_step_skips_without_changes(self) -> None:
        step = run_delta_eval_step(
            skills_root=REPO_ROOT / "skills",
            retrieval_limit=3,
            changed_skill_names=frozenset(),
        )
        self.assertTrue(step.passed)
        self.assertIn("skipped", step.detail)

    def test_ingest_gate_json_report_passes(self) -> None:
        self.assertEqual(ingest_gate_main(["--json"]), 0)


if __name__ == "__main__":
    unittest.main()
