"""Agent journey fixtures for MCP routing and selection trace coverage."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts/runtime/mcp/skills_mcp_server.py"
JOURNEYS_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "agent_journeys.json"


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("skills_mcp_server", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_journeys() -> list[dict[str, object]]:
    payload = json.loads(JOURNEYS_FIXTURE.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    return payload


def build_server(module: Any, server_mode: str) -> Any:
    if server_mode == "fixture":
        return module.SkillsMcpServer.for_test_fixture()
    if server_mode == "embedded":
        return module.SkillsMcpServer.from_repository(REPO_ROOT / "skills")
    raise AssertionError(f"Unsupported server mode: {server_mode}")


def assert_selection_trace(
    response: dict[str, object],
    expectations: dict[str, object],
) -> None:
    trace = response.get("selection_trace")
    assert isinstance(trace, dict), "selection_trace must be present"

    for key in ("tool", "query_intent"):
        expected = expectations.get(key)
        if expected is not None:
            assert trace.get(key) == expected, f"selection_trace.{key} mismatch"

    if expectations.get("requires_usage_event_id"):
        usage_event_id = trace.get("usage_event_id")
        assert isinstance(usage_event_id, str) and usage_event_id.startswith("sel-")

    if expectations.get("requires_evidence"):
        evidence = trace.get("evidence")
        assert isinstance(evidence, dict)
        assert evidence.get("source_paths")
        assert evidence.get("evidence_anchors")

    if expectations.get("requires_rank"):
        rank = trace.get("rank")
        assert isinstance(rank, list) and rank
        assert rank[0].get("rank") == 1

    if expectations.get("requires_filter"):
        filter_payload = trace.get("filter")
        assert isinstance(filter_payload, dict)
        assert filter_payload.get("promotion_status") == "promoted"

    if expectations.get("requires_evidence_anchor_ids"):
        anchor_ids = trace.get("evidence_anchor_ids")
        assert isinstance(anchor_ids, list)

    if expectations.get("requires_abstention_reason"):
        assert isinstance(trace.get("abstention_reason"), str) and trace["abstention_reason"]

    if expectations.get("requires_selected_evidence"):
        selected = trace.get("selected")
        assert isinstance(selected, dict)
        assert selected.get("evidence_anchors")
        assert selected.get("source_paths")


def assert_lean_recommend_wire(
    response: dict[str, object],
    expectations: dict[str, object],
) -> None:
    """Assert recommend_skills agent-facing JSON omits audit trace but keeps correlation."""

    if expectations.get("omits_selection_trace"):
        assert "selection_trace" not in response, "recommend wire must omit selection_trace"
    if expectations.get("requires_usage_selection_run_id"):
        usage = response.get("usage")
        assert isinstance(usage, dict), "usage metadata must be present on recommend wire"
        run_id = usage.get("selection_run_id")
        assert isinstance(run_id, str) and run_id.startswith("sel_")


class AgentJourneyTests(unittest.TestCase):
    def test_agent_journey_fixtures_execute_with_selection_trace(self) -> None:
        module = load_module()
        journeys = load_journeys()

        self.assertGreaterEqual(len(journeys), 3)
        for journey in journeys:
            journey_id = str(journey["id"])
            server_mode = str(journey.get("server", "fixture"))
            server = build_server(module, server_mode)

            for step in journey["steps"]:
                assert isinstance(step, dict)
                tool_name = str(step["tool"])
                arguments = step.get("arguments", {})
                assert isinstance(arguments, dict)

                response = server.call_tool(tool_name, arguments)
                expectations = step.get("expect", {})
                assert isinstance(expectations, dict)

                for key, expected in expectations.items():
                    if key == "top_skill_id":
                        recommendations = response.get("recommendations", [])
                        assert recommendations, f"{journey_id}: expected recommendations"
                        assert recommendations[0]["skill_id"] == expected
                    elif key == "excludes_skill_ids":
                        recommendations = response.get("recommendations", [])
                        returned_ids = {item["skill_id"] for item in recommendations}
                        for skill_id in expected:
                            assert skill_id not in returned_ids
                    elif key == "recommendation_count":
                        recommendations = response.get("recommendations", [])
                        assert len(recommendations) == expected
                    elif key == "requires_verification_checklist":
                        assert response.get("verification_checklist")
                    else:
                        assert response.get(key) == expected, f"{journey_id} step {tool_name}.{key}"

                trace_expectations = step.get("expect_selection_trace")
                if trace_expectations is not None:
                    assert isinstance(trace_expectations, dict)
                    assert_selection_trace(response, trace_expectations)

                wire_expectations = step.get("expect_wire")
                if wire_expectations is not None:
                    assert isinstance(wire_expectations, dict)
                    assert_lean_recommend_wire(response, wire_expectations)

    def test_route_keeps_selection_trace_recommend_omits_on_wire(self) -> None:
        module = load_module()
        server = module.SkillsMcpServer.for_test_fixture()

        route = server.call_tool("route_skill_query", {"query": "tell me about tdd-practice"})
        recommend = server.call_tool(
            "recommend_skills",
            {
                "query": "fixing a defect with a failing test first",
                "limit": 2,
                "token_budget": 120,
            },
        )

        route_trace = route["selection_trace"]
        self.assertEqual("route_skill_query", route_trace["tool"])
        self.assertEqual("direct_lookup", route_trace["query_intent"])
        self.assertTrue(str(route_trace["usage_event_id"]).startswith("sel-"))
        self.assertIn("evidence", route_trace)
        self.assertIn("evidence_anchor_ids", route_trace)

        self.assertNotIn("selection_trace", recommend)
        usage = recommend["usage"]
        self.assertIsInstance(usage, dict)
        self.assertTrue(str(usage.get("selection_run_id", "")).startswith("sel_"))
        self.assertEqual("recommend_skills", usage.get("tool"))


if __name__ == "__main__":
    unittest.main()
