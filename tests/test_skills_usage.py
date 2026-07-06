"""Tests for shared Skills KG usage instrumentation."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any

from scripts.observability import skills_usage

REPO_ROOT = Path(__file__).resolve().parents[1]
MCP_SCRIPT = REPO_ROOT / "scripts/runtime/mcp/skills_mcp_server.py"


def load_mcp_module() -> Any:
    spec = importlib.util.spec_from_file_location("skills_mcp_server", MCP_SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def metric_value(metrics_text: str, metric_name: str, **labels: str) -> float:
    label_fragment = ",".join(f'{key}="{labels[key]}"' for key in sorted(labels))
    line_prefix = f"{metric_name}{{{label_fragment}}}"
    for line in metrics_text.splitlines():
        if line.startswith(f"{line_prefix} "):
            return float(line.split(" ", 1)[1])
    return 0.0


def parse_log_json(record: str) -> dict[str, object]:
    start = record.find("{")
    assert start != -1
    payload = json.loads(record[start:])
    assert isinstance(payload, dict)
    return payload


class SkillsUsageTests(unittest.TestCase):
    def test_record_skill_hit_increments_hits_total(self) -> None:
        before = metric_value(
            skills_usage.usage_metrics_text(),
            "skills_usage_hits_total",
            skill_id="skill:tdd-practice",
            tool="recommend_skills",
        )
        skills_usage.record_skill_hit("skill:tdd-practice", "recommend_skills")
        after = metric_value(
            skills_usage.usage_metrics_text(),
            "skills_usage_hits_total",
            skill_id="skill:tdd-practice",
            tool="recommend_skills",
        )
        self.assertEqual(before + 1.0, after)

    def test_record_skill_hit_with_rank_increments_rank_total(self) -> None:
        before = metric_value(
            skills_usage.usage_metrics_text(),
            "skills_usage_recommend_rank_total",
            skill_id="skill:knowledge-graph-rag",
            rank_bucket="1",
        )
        skills_usage.record_skill_hit("skill:knowledge-graph-rag", "recommend_skills", rank=1)
        after = metric_value(
            skills_usage.usage_metrics_text(),
            "skills_usage_recommend_rank_total",
            skill_id="skill:knowledge-graph-rag",
            rank_bucket="1",
        )
        self.assertEqual(before + 1.0, after)

    def test_rank_bucket_mapping(self) -> None:
        self.assertEqual("1", skills_usage.rank_bucket(1))
        self.assertEqual("2", skills_usage.rank_bucket(2))
        self.assertEqual("3", skills_usage.rank_bucket(3))
        self.assertEqual("4-5", skills_usage.rank_bucket(4))
        self.assertEqual("4-5", skills_usage.rank_bucket(5))
        self.assertEqual("6+", skills_usage.rank_bucket(6))

    def test_record_execution_guide_increments_counter(self) -> None:
        before = metric_value(
            skills_usage.usage_metrics_text(),
            "skills_usage_execution_guide_total",
            skill_id="skill:knowledge-graph-rag",
            tool="get_skill_execution_guide",
        )
        skills_usage.record_execution_guide(
            "skill:knowledge-graph-rag",
            "get_skill_execution_guide",
        )
        after = metric_value(
            skills_usage.usage_metrics_text(),
            "skills_usage_execution_guide_total",
            skill_id="skill:knowledge-graph-rag",
            tool="get_skill_execution_guide",
        )
        self.assertEqual(before + 1.0, after)

    def test_record_abstention_increments_counter(self) -> None:
        before = metric_value(
            skills_usage.usage_metrics_text(),
            "skills_usage_abstention_total",
            tool="recommend_skills",
            reason="low_confidence",
        )
        skills_usage.record_abstention("recommend_skills", "low_confidence")
        after = metric_value(
            skills_usage.usage_metrics_text(),
            "skills_usage_abstention_total",
            tool="recommend_skills",
            reason="low_confidence",
        )
        self.assertEqual(before + 1.0, after)

    def test_emit_skill_selection_run_strips_raw_query(self) -> None:
        with self.assertLogs(skills_usage.USAGE_LOGGER_NAME, level="INFO") as captured:
            skills_usage.emit_skill_selection_run(
                {
                    "selection_run_id": "sel_test123",
                    "tool": "recommend_skills",
                    "query": "secret user task text",
                    "selection_trace": {
                        "request": {"query": "secret user task text"},
                        "selected": {"skill_id": "skill:tdd-practice"},
                    },
                }
            )

        payload = parse_log_json(captured.output[0])
        serialised = json.dumps(payload)
        self.assertEqual("skill_selection_run", payload["event"])
        self.assertNotIn("secret user task text", serialised)
        self.assertNotIn('"query"', serialised)

    def test_usage_counter_on_recommend_via_mcp_server(self) -> None:
        mcp = load_mcp_module()
        server = mcp.SkillsMcpServer.for_test_fixture()
        before_hits = metric_value(
            skills_usage.usage_metrics_text(),
            "skills_usage_hits_total",
            skill_id="skill:knowledge-graph-rag",
            tool="recommend_skills",
        )
        before_rank = metric_value(
            skills_usage.usage_metrics_text(),
            "skills_usage_recommend_rank_total",
            skill_id="skill:knowledge-graph-rag",
            rank_bucket="1",
        )

        response = server.call_tool(
            "recommend_skills",
            {"query": "graph rag ontology retrieval", "limit": 1, "token_budget": 80},
        )

        self.assertEqual("ok", response["status"])
        self.assertIn("usage", response)
        self.assertTrue(_string(response["usage"].get("selection_run_id")).startswith("sel_"))
        after_hits = metric_value(
            skills_usage.usage_metrics_text(),
            "skills_usage_hits_total",
            skill_id="skill:knowledge-graph-rag",
            tool="recommend_skills",
        )
        after_rank = metric_value(
            skills_usage.usage_metrics_text(),
            "skills_usage_recommend_rank_total",
            skill_id="skill:knowledge-graph-rag",
            rank_bucket="1",
        )
        self.assertEqual(before_hits + 1.0, after_hits)
        self.assertEqual(before_rank + 1.0, after_rank)

    def test_usage_counter_on_execution_guide_via_mcp_server(self) -> None:
        mcp = load_mcp_module()
        server = mcp.SkillsMcpServer.for_test_fixture()
        before = metric_value(
            skills_usage.usage_metrics_text(),
            "skills_usage_execution_guide_total",
            skill_id="skill:knowledge-graph-rag",
            tool="get_skill_execution_guide",
        )

        response = server.call_tool(
            "get_skill_execution_guide",
            {"skill_id": "skill:knowledge-graph-rag"},
        )

        self.assertEqual("ok", response["status"])
        self.assertIn("usage", response)
        after = metric_value(
            skills_usage.usage_metrics_text(),
            "skills_usage_execution_guide_total",
            skill_id="skill:knowledge-graph-rag",
            tool="get_skill_execution_guide",
        )
        self.assertEqual(before + 1.0, after)

    def test_selection_trace_emitted_per_mcp_call(self) -> None:
        mcp = load_mcp_module()
        server = mcp.SkillsMcpServer.for_test_fixture()
        with self.assertLogs(skills_usage.USAGE_LOGGER_NAME, level="INFO") as captured:
            response = server.call_tool(
                "route_skill_query",
                {"query": "tell me about knowledge-graph-rag"},
            )

        self.assertEqual("ok", response["status"])
        self.assertIn("usage", response)
        payload = parse_log_json(captured.output[-1])
        self.assertEqual("skill_selection_run", payload["event"])
        self.assertEqual("route_skill_query", payload["tool"])
        self.assertIn("skill:knowledge-graph-rag", payload["selected"])


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


if __name__ == "__main__":
    unittest.main()
