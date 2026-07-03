"""Tests for tiered evaluation corpus validation."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts import validate_eval_corpus

REPO_ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = REPO_ROOT / "tests" / "fixtures" / "retrieval_evaluation"


class ValidateEvalCorpusTests(unittest.TestCase):
    def test_tiered_corpora_pass_validation(self) -> None:
        result = validate_eval_corpus.validate_all(skills_root=REPO_ROOT / "skills")
        self.assertTrue(result.valid, result.errors)

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


if __name__ == "__main__":
    unittest.main()
