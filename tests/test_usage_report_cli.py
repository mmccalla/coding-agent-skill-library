"""CLI smoke tests for operator evaluation scripts."""

from __future__ import annotations

import unittest

from scripts.lib.retrieval.run_e2e_retrieval_eval import main as e2e_main


class UsageReportCliTests(unittest.TestCase):
    def test_run_e2e_retrieval_eval_json(self) -> None:
        self.assertEqual(e2e_main(["--json"]), 0)


if __name__ == "__main__":
    unittest.main()
