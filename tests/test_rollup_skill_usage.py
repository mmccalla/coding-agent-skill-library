"""Tests for scripts/rollup_skill_usage.py."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.rollup_skill_usage import build_weekly_rollup

REPO_ROOT = Path(__file__).resolve().parents[1]


class RollupSkillUsageTests(unittest.TestCase):
    def test_weekly_rollup_includes_zero_hit_promoted_skills(self) -> None:
        rollup = build_weekly_rollup(skills_root=REPO_ROOT / "skills", period_days=7)
        self.assertEqual("weekly_skill_usage", rollup["rollup_type"])
        self.assertEqual(7, rollup["period_days"])
        self.assertGreaterEqual(int(rollup["promoted_skill_count"]), 30)
        self.assertIn("zero_hit_promoted_skills", rollup)


if __name__ == "__main__":
    unittest.main()
