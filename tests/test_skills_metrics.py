"""Tests for scripts/skills_metrics.py and trust metrics."""

from __future__ import annotations

import unittest

from prometheus_client import CollectorRegistry, Counter

from scripts.observability import skills_metrics, skills_trust_metrics, skills_usage


class SkillsMetricsTests(unittest.TestCase):
    def test_combined_metrics_include_usage_and_trust_counters(self) -> None:
        skills_usage.record_skill_hit("skill:tdd-practice", "recommend_skills", rank=1)
        skills_trust_metrics.record_promotion_quarantine(reason="incomplete_mapping", count=2)
        skills_trust_metrics.record_trust_rejection(layer="L2_security", reason="test_rule")

        text = skills_metrics.metrics_text()
        self.assertIn("skills_usage_hits_total", text)
        self.assertIn("skills_quarantined_total", text)
        self.assertIn("skills_trust_rejected_total", text)

    def test_render_all_metrics_includes_api_registry(self) -> None:
        api_registry = CollectorRegistry()
        Counter(
            "skills_api_test_counter_total",
            "Test counter for combined metrics rendering.",
            registry=api_registry,
        ).inc()
        text = skills_metrics.metrics_text(api_registry=api_registry)
        self.assertIn("skills_api_test_counter_total", text)
        self.assertIn("skills_usage_hits_total", text)


if __name__ == "__main__":
    unittest.main()
