"""Tests for the FastAPI Skills GraphRAG service."""

from __future__ import annotations

import unittest
from collections.abc import Mapping

from fastapi.testclient import TestClient

from scripts import skills_contracts
from scripts.skills_api import create_app
from scripts.skills_mcp_server import SkillsMcpServer


class SkillsApiTests(unittest.TestCase):
    def test_health_and_readiness_endpoints_are_explicit(self) -> None:
        client = TestClient(create_app(SkillsMcpServer.for_test_fixture()))

        self.assertEqual({"status": "ok"}, client.get("/health/live").json())
        ready = client.get("/health/ready").json()

        self.assertEqual("ok", ready["status"])
        self.assertTrue(ready["read_only"])

    def test_metrics_include_readiness_and_graph_snapshot(self) -> None:
        client = TestClient(
            create_app(
                SkillsMcpServer.for_test_fixture(),
                readiness_provider=lambda: {
                    "status": "ok",
                    "read_only": True,
                    "ready": True,
                    "database": "neo4j",
                    "errors": [],
                },
            )
        )

        client.get("/health/ready")
        metrics_response = client.get("/metrics")

        self.assertEqual(200, metrics_response.status_code)
        self.assertIn("skills_api_readiness_state", metrics_response.text)
        self.assertIn('database="neo4j"', metrics_response.text)
        self.assertIn("skills_api_graph_nodes", metrics_response.text)
        self.assertIn('label="RetrievalUnit"', metrics_response.text)
        self.assertIn("skills_api_graph_relationships", metrics_response.text)
        self.assertIn('type="COMPLEMENTS"', metrics_response.text)

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
        self.assertEqual("knowledge-graph-rag", payload["recommendations"][0]["skill_name"])
        self.assertNotIn("MATCH ", response.text)
        self.assertNotIn("embedding", response.text.lower())
        metrics_response = client.get("/metrics")
        self.assertIn("skills_api_retrieval_requests_total", metrics_response.text)
        self.assertIn('operation="skills.recommend"', metrics_response.text)
        self.assertIn('route="recommendation"', metrics_response.text)
        self.assertIn("skills_api_retrieval_recommendation_count", metrics_response.text)
        self.assertIn("skills_api_retrieval_top_score", metrics_response.text)

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

    def test_mcp_mount_exposes_streamable_http_at_clean_mcp_path(self) -> None:
        app = create_app(SkillsMcpServer.for_test_fixture())
        mounted_route = next(
            route for route in app.routes if getattr(route, "path", None) == "/mcp"
        )

        self.assertEqual("/mcp", mounted_route.path)
        self.assertEqual("/", mounted_route.app.routes[0].path)

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

    def test_query_endpoint_uses_bounded_graph_evidence_and_safe_ollama_provider(self) -> None:
        async def fake_query_provider(
            request: skills_contracts.QuerySkillsRequest,
            recommendations: Mapping[str, object],
        ) -> Mapping[str, object]:
            return {
                "status": "ok",
                "answer": "Use knowledge-graph-rag with source evidence.",
                "model": "test-model",
                "ollama_endpoint": request.ollama_endpoint,
                "evidence": recommendations,
            }

        client = TestClient(
            create_app(SkillsMcpServer.for_test_fixture(), query_provider=fake_query_provider)
        )

        response = client.post(
            "/skills/query",
            json={
                "query": "How should I use graph retrieval?",
                "ollama_endpoint": "http://127.0.0.1:11434",
            },
        )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("ok", payload["status"])
        self.assertEqual("test-model", payload["model"])
        self.assertIn("knowledge-graph-rag", response.text)
        self.assertNotIn("secret", response.text.lower())

    def test_query_endpoint_passes_user_selected_model_to_provider(self) -> None:
        async def fake_query_provider(
            request: skills_contracts.QuerySkillsRequest,
            recommendations: Mapping[str, object],
        ) -> Mapping[str, object]:
            return {
                "status": "ok",
                "answer": "Use knowledge-graph-rag with source evidence.",
                "model": request.model,
                "ollama_endpoint": request.ollama_endpoint,
                "evidence": recommendations,
            }

        client = TestClient(
            create_app(SkillsMcpServer.for_test_fixture(), query_provider=fake_query_provider)
        )

        response = client.post(
            "/skills/query",
            json={
                "query": "How should I use graph retrieval?",
                "ollama_endpoint": "http://127.0.0.1:11434",
                "model": "qwen3:1.7b",
            },
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual("qwen3:1.7b", response.json()["model"])

    def test_query_endpoint_routes_direct_skill_lookup_before_generation(self) -> None:
        async def fake_query_provider(
            request: skills_contracts.QuerySkillsRequest,
            evidence: Mapping[str, object],
        ) -> Mapping[str, object]:
            return {
                "status": "ok",
                "answer": "knowledge-graph-rag is the direct skill profile.",
                "model": request.model,
                "ollama_endpoint": request.ollama_endpoint,
                "evidence": evidence,
            }

        client = TestClient(
            create_app(SkillsMcpServer.for_test_fixture(), query_provider=fake_query_provider)
        )

        response = client.post(
            "/skills/query",
            json={
                "query": "Tell me about knowledge-graph-rag",
                "ollama_endpoint": "http://127.0.0.1:11434",
                "model": "qwen3:1.7b",
            },
        )

        self.assertEqual(200, response.status_code)
        evidence = response.json()["evidence"]
        self.assertEqual("direct_lookup", evidence["route"])
        self.assertEqual("skill:knowledge-graph-rag", evidence["skill"]["skill_id"])
        self.assertIn("retrieval_units", evidence["skill"])
        self.assertNotIn("chunks", evidence["skill"])
        self.assertNotIn("recommendations", evidence)

    def test_route_resolve_and_execution_guide_endpoints_are_agent_readable(self) -> None:
        client = TestClient(create_app(SkillsMcpServer.for_test_fixture()))

        route_response = client.post(
            "/skills/route", json={"query": "How do I apply knowledge-graph-rag?"}
        )
        resolve_response = client.get("/skills/resolve", params={"name": "knowledge-graph-rag"})
        guide_response = client.get("/skills/skill:knowledge-graph-rag/execution-guide")

        self.assertEqual(200, route_response.status_code)
        self.assertEqual("execution_plan", route_response.json()["route"])
        self.assertEqual(200, resolve_response.status_code)
        self.assertEqual("skill:knowledge-graph-rag", resolve_response.json()["skill_id"])
        self.assertEqual(200, guide_response.status_code)
        self.assertTrue(guide_response.json()["verification_checklist"])

    def test_ollama_models_endpoint_returns_safe_model_choices(self) -> None:
        async def fake_model_provider(endpoint: str) -> Mapping[str, object]:
            return {
                "status": "ok",
                "ollama_endpoint": endpoint,
                "models": [
                    {"name": "qwen3:1.7b", "running": True},
                    {"name": "bge-m3:latest", "running": False},
                ],
            }

        client = TestClient(
            create_app(SkillsMcpServer.for_test_fixture(), model_provider=fake_model_provider)
        )

        response = client.get(
            "/ollama/models",
            params={"ollama_endpoint": "http://127.0.0.1:11434"},
        )

        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertEqual("ok", payload["status"])
        self.assertEqual("http://127.0.0.1:11434", payload["ollama_endpoint"])
        self.assertEqual("qwen3:1.7b", payload["models"][0]["name"])

    def test_query_endpoint_rejects_non_local_ollama_endpoint(self) -> None:
        client = TestClient(create_app(SkillsMcpServer.for_test_fixture()))

        response = client.post(
            "/skills/query",
            json={"query": "test", "ollama_endpoint": "https://example.com"},
        )

        self.assertEqual(422, response.status_code)

    def test_query_endpoint_returns_bad_gateway_for_ollama_failures(self) -> None:
        async def failing_query_provider(
            _request: skills_contracts.QuerySkillsRequest,
            _recommendations: Mapping[str, object],
        ) -> Mapping[str, object]:
            from scripts import skills_ollama

            raise skills_ollama.OllamaQueryError("Could not connect to local Ollama.")

        client = TestClient(
            create_app(SkillsMcpServer.for_test_fixture(), query_provider=failing_query_provider)
        )

        response = client.post(
            "/skills/query",
            json={"query": "test", "ollama_endpoint": "http://127.0.0.1:11434"},
        )

        self.assertEqual(502, response.status_code)
        self.assertTrue(response.headers["x-request-id"].startswith("req_"))
        detail = response.json()["detail"]
        self.assertEqual("ollama_query_failed", detail["error_type"])
        self.assertEqual("skills.query", detail["operation"])
        self.assertIn("Could not connect to local Ollama", detail["message"])
        self.assertIn("request_id", detail)
        self.assertIn("Check that Ollama is running", detail["hint"])

        metrics_response = client.get("/metrics")

        self.assertEqual(200, metrics_response.status_code)
        self.assertIn("skills_api_requests_total", metrics_response.text)
        self.assertIn("skills_api_ollama_failures_total", metrics_response.text)
        self.assertIn('operation="skills.query"', metrics_response.text)
        self.assertIn('error_type="ollama_query_failed"', metrics_response.text)


if __name__ == "__main__":
    unittest.main()
