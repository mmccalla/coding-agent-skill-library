"""CLI smoke tests for usage reporting scripts."""

from __future__ import annotations

import unittest

from scripts.report_skill_usage import main as report_main
from scripts.rollup_skill_usage import main as rollup_main
from scripts.run_e2e_retrieval_eval import main as e2e_main


class UsageReportCliTests(unittest.TestCase):
    def test_report_skill_usage_json(self) -> None:
        self.assertEqual(report_main(["--json"]), 0)

    def test_rollup_skill_usage_json(self) -> None:
        self.assertEqual(rollup_main(["--json"]), 0)

    def test_run_e2e_retrieval_eval_json(self) -> None:
        self.assertEqual(e2e_main(["--json"]), 0)


if __name__ == "__main__":
    unittest.main()
