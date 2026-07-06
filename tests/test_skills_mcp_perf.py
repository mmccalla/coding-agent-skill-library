"""Tests for MCP tool performance instrumentation."""

from __future__ import annotations

import time
import unittest

from scripts.observability import skills_metrics
from scripts.runtime.mcp import skills_mcp_perf
from scripts.runtime.mcp.skills_mcp_server import SkillsMcpServer


class SkillsMcpPerfTests(unittest.TestCase):
    def test_record_tool_timing_emits_prometheus_metrics(self) -> None:
        timing = skills_mcp_perf.build_timing_metadata(
            duration_seconds=0.012,
            payload_construction_seconds=0.003,
            database_io_seconds=0.004,
            disk_io_seconds=0.001,
            request_bytes=64,
            response_bytes=256,
            database_bytes_read=512,
            disk_bytes_read=128,
        )
        skills_mcp_perf.record_tool_timing(
            tool="search_skills",
            status="ok",
            timing=timing,
        )

        text = skills_mcp_perf.metrics_text()
        self.assertIn("skills_mcp_tool_calls_total", text)
        self.assertIn('tool="search_skills"', text)
        self.assertIn('status="ok"', text)
        self.assertIn("skills_mcp_tool_duration_seconds", text)
        self.assertIn("skills_mcp_tool_handler_seconds", text)
        self.assertIn("skills_mcp_tool_payload_construction_seconds", text)
        self.assertIn("skills_mcp_tool_database_io_seconds", text)
        self.assertIn("skills_mcp_tool_disk_io_seconds", text)
        self.assertIn("skills_mcp_tool_request_bytes", text)
        self.assertIn("skills_mcp_tool_response_bytes", text)
        self.assertIn("skills_mcp_tool_database_bytes_read", text)
        self.assertIn("skills_mcp_tool_disk_bytes_read", text)

    def test_attach_timing_metadata_preserves_payload_and_adds_timing(self) -> None:
        result = {"status": "ok", "results": [{"skill_id": "skill:tdd-practice"}]}
        timing = skills_mcp_perf.build_timing_metadata(
            duration_seconds=0.02,
            payload_construction_seconds=0.005,
            database_io_seconds=0.0,
            disk_io_seconds=0.0,
            request_bytes=32,
            response_bytes=128,
            database_bytes_read=0,
            disk_bytes_read=0,
        )
        timed = skills_mcp_perf.attach_timing_metadata(result, timing=timing)

        self.assertEqual("ok", timed["status"])
        self.assertEqual([{"skill_id": "skill:tdd-practice"}], timed["results"])
        attached = timed["timing"]
        assert isinstance(attached, dict)
        self.assertEqual(20.0, attached["duration_ms"])
        self.assertEqual(15.0, attached["handler_ms"])
        self.assertEqual(5.0, attached["payload_construction_ms"])
        self.assertEqual(128, attached["response_bytes"])
        self.assertEqual(32, attached["request_bytes"])

    def test_response_byte_size_is_stable_for_same_payload(self) -> None:
        payload = {"status": "ok", "message": "hello"}
        first = skills_mcp_perf.response_byte_size(payload)
        second = skills_mcp_perf.response_byte_size(payload)
        self.assertEqual(first, second)
        self.assertGreater(first, 0)

    def test_call_tool_includes_phase_and_size_metadata(self) -> None:
        server = SkillsMcpServer.for_test_fixture()
        response = server.call_tool("search_skills", {"query": "knowledge", "limit": 3})

        self.assertEqual("ok", response["status"])
        timing = response["timing"]
        assert isinstance(timing, dict)
        for key in (
            "duration_ms",
            "handler_ms",
            "payload_construction_ms",
            "database_io_ms",
            "disk_io_ms",
            "request_bytes",
            "response_bytes",
            "database_bytes_read",
            "disk_bytes_read",
        ):
            self.assertIn(key, timing)
        self.assertGreaterEqual(timing["duration_ms"], 0.0)
        self.assertGreaterEqual(timing["payload_construction_ms"], 0.0)
        self.assertEqual(0.0, timing["database_io_ms"])
        self.assertEqual(0.0, timing["disk_io_ms"])
        self.assertGreater(timing["request_bytes"], 0)
        self.assertGreater(timing["response_bytes"], 0)
        self.assertEqual(0, timing["database_bytes_read"])
        self.assertEqual(0, timing["disk_bytes_read"])

    def test_unsupported_tool_still_records_timing(self) -> None:
        server = SkillsMcpServer.for_test_fixture()
        response = server.call_tool("not_a_tool", {})

        self.assertEqual("error", response["status"])
        timing = response["timing"]
        assert isinstance(timing, dict)
        self.assertGreaterEqual(timing["duration_ms"], 0.0)
        self.assertGreater(timing["response_bytes"], 0)

    def test_phase_context_managers_accumulate_on_active_span(self) -> None:
        with skills_mcp_perf.tool_span("recommend_skills", {"query": "tdd"}) as span:
            with skills_mcp_perf.payload_construction():
                time.sleep(0.001)
            with skills_mcp_perf.database_io() as db_io:
                time.sleep(0.001)
                db_io.add(128)
            with skills_mcp_perf.disk_io() as disk:
                time.sleep(0.001)
                disk.add(64)
            result = span.finish({"status": "ok", "value": 1})

        timing = result["timing"]
        assert isinstance(timing, dict)
        self.assertGreater(timing["payload_construction_ms"], 0.0)
        self.assertGreater(timing["database_io_ms"], 0.0)
        self.assertGreater(timing["disk_io_ms"], 0.0)
        self.assertEqual(128, timing["database_bytes_read"])
        self.assertEqual(64, timing["disk_bytes_read"])
        self.assertGreater(timing["request_bytes"], 0)
        self.assertGreater(timing["response_bytes"], 0)

    def test_combined_metrics_include_mcp_perf_counters(self) -> None:
        timing = skills_mcp_perf.build_timing_metadata(
            duration_seconds=0.05,
            payload_construction_seconds=0.01,
            database_io_seconds=0.0,
            disk_io_seconds=0.0,
            request_bytes=40,
            response_bytes=1024,
            database_bytes_read=0,
            disk_bytes_read=0,
        )
        skills_mcp_perf.record_tool_timing(
            tool="recommend_skills",
            status="ok",
            timing=timing,
        )
        text = skills_metrics.metrics_text()
        self.assertIn("skills_mcp_tool_calls_total", text)
        self.assertIn("skills_mcp_tool_payload_construction_seconds", text)

    def test_summarise_timings_reports_phase_percentiles(self) -> None:
        summary = skills_mcp_perf.summarise_timings(
            [
                {
                    "duration_ms": 10.0,
                    "handler_ms": 6.0,
                    "payload_construction_ms": 3.0,
                    "database_io_ms": 1.0,
                    "disk_io_ms": 0.0,
                    "request_bytes": 10,
                    "response_bytes": 100,
                    "database_bytes_read": 50,
                    "disk_bytes_read": 0,
                },
                {
                    "duration_ms": 20.0,
                    "handler_ms": 12.0,
                    "payload_construction_ms": 6.0,
                    "database_io_ms": 2.0,
                    "disk_io_ms": 0.0,
                    "request_bytes": 20,
                    "response_bytes": 200,
                    "database_bytes_read": 100,
                    "disk_bytes_read": 0,
                },
            ]
        )
        self.assertEqual(2, summary["count"])
        duration = summary["duration_ms"]
        assert isinstance(duration, dict)
        self.assertEqual(10.0, duration["min"])
        self.assertEqual(20.0, duration["max"])
        payload = summary["payload_construction_ms"]
        assert isinstance(payload, dict)
        self.assertEqual(3.0, payload["min"])
        response_bytes = summary["response_bytes"]
        assert isinstance(response_bytes, dict)
        self.assertEqual(100, response_bytes["min"])

    def test_tool_span_records_phase_timings(self) -> None:
        from scripts.runtime.mcp.skills_mcp_server import SkillsMcpServer

        server = SkillsMcpServer.for_test_fixture()
        cases = (
            ("search_skills", {"query": "knowledge graph", "limit": 5}),
            ("resolve_skill", {"name": "knowledge-graph-rag"}),
        )
        for tool, arguments in cases:
            for _ in range(2):
                response = server.call_tool(tool, arguments)
                timing = response.get("timing")
                self.assertIsInstance(timing, dict)
                duration = timing.get("duration_ms")
                self.assertIsInstance(duration, (int, float))
                self.assertGreater(float(duration), 0.0)


if __name__ == "__main__":
    unittest.main()
