"""Tests for the FastAPI Skills GraphRAG service."""

from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from scripts.skills_api import create_app
from scripts.skills_mcp_server import SkillsMcpServer


class SkillsApiTests(unittest.TestCase):
    def test_health_and_readiness_endpoints_are_explicit(self) -> None:
        client = TestClient(create_app(SkillsMcpServer.for_test_fixture()))

        self.assertEqual({"status": "ok"}, client.get("/health/live").json())
        ready = client.get("/health/ready").json()

        self.assertEqual("ok", ready["status"])
        self.assertTrue(ready["read_only"])

    def test_recommend_endpoint_returns_bounded_grounded_result(self) -> None:
        client = TestClient(create_app(SkillsMcpServer.for_test_fixture()))

        response = client.post(
            "/skills/recommend",
            json={"query": "graph rag ontology retrieval", "limit": 1, "token_budget": 80},
        )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("ok", payload["status"])
        self.assertEqual(1, len(payload["recommendations"]))
        self.assertEqual("kg-enabled-rag", payload["recommendations"][0]["skill_name"])
        self.assertNotIn("MATCH ", response.text)
        self.assertNotIn("embedding", response.text.lower())

    def test_invalid_request_is_rejected_before_tool_execution(self) -> None:
        client = TestClient(create_app(SkillsMcpServer.for_test_fixture()))

        response = client.post("/skills/recommend", json={"query": "", "limit": 999})

        self.assertEqual(422, response.status_code)

    def test_graph_endpoint_returns_d3_safe_nodes_and_links(self) -> None:
        client = TestClient(create_app(SkillsMcpServer.for_test_fixture()))

        response = client.get("/skills/graph")

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertTrue(payload["nodes"])
        self.assertTrue(payload["links"])
        self.assertNotIn("embedding", response.text.lower())
        self.assertNotIn("MATCH ", response.text)

    def test_upload_preview_validates_skill_markdown_without_persisting(self) -> None:
        client = TestClient(create_app(SkillsMcpServer.for_test_fixture()))
        content = b"""---
name: example-skill
description: Use when validating a safe upload preview for a skill file.
---

# Example Skill

## When to use
Use when validating uploads.
"""

        response = client.post(
            "/skills/upload/preview",
            files={"file": ("SKILL.md", content, "text/markdown")},
        )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("ok", payload["status"])
        self.assertEqual("example-skill", payload["name"])
        self.assertFalse(payload["persisted"])

    def test_upload_preview_rejects_oversized_files(self) -> None:
        client = TestClient(create_app(SkillsMcpServer.for_test_fixture()))

        response = client.post(
            "/skills/upload/preview",
            files={"file": ("SKILL.md", b"x" * (257 * 1024), "text/markdown")},
        )

        self.assertEqual(413, response.status_code)

    def test_technical_info_exposes_mcp_safe_contract(self) -> None:
        client = TestClient(create_app(SkillsMcpServer.for_test_fixture()))

        response = client.get("/mcp/technical-info")

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertTrue(payload["read_only"])
        self.assertIn("recommend_skills", payload["tools"])
        self.assertNotIn("raw_embeddings", response.text)

    def test_cors_preflight_allows_separate_local_ui_deployable(self) -> None:
        client = TestClient(create_app(SkillsMcpServer.for_test_fixture()))

        response = client.options(
            "/skills/graph",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual("http://localhost:5173", response.headers["access-control-allow-origin"])


if __name__ == "__main__":
    unittest.main()
