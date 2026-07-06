"""Tests for local Ollama graph query guardrails."""

from __future__ import annotations

import unittest
from unittest import mock

import httpx

from scripts.lib.config import skills_contracts
from scripts.runtime.api import skills_ollama


class SkillsOllamaTests(unittest.TestCase):
    def test_local_ollama_endpoint_is_normalised(self) -> None:
        endpoint = skills_ollama.normalise_ollama_endpoint("http://127.0.0.1:11434/")

        self.assertEqual("http://127.0.0.1:11434", endpoint)

    def test_endpoint_rejects_credentials_and_non_local_hosts(self) -> None:
        with self.assertRaises(skills_ollama.UnsafeOllamaEndpointError):
            skills_ollama.normalise_ollama_endpoint("http://user:secret@127.0.0.1:11434")
        with self.assertRaises(skills_ollama.UnsafeOllamaEndpointError):
            skills_ollama.normalise_ollama_endpoint("https://example.com")

    def test_model_selection_uses_allowlisted_environment_keys(self) -> None:
        model = skills_ollama.ollama_model_from_env(
            {"SKILLS_OLLAMA_MODEL": "llama3.1:8b", "UNRELATED_SECRET": "not-read"}
        )

        self.assertEqual("llama3.1:8b", model)

    def test_evidence_response_does_not_include_raw_prompt(self) -> None:
        request = skills_contracts.QuerySkillsRequest(query="How should I test graph retrieval?")
        recommendations = {
            "status": "ok",
            "recommendations": [
                {
                    "skill_name": "knowledge-graph-rag",
                    "rationale": "Relevant to graph retrieval.",
                    "source_paths": ["skills/knowledge-graph-rag/SKILL.md"],
                    "evidence_snippets": ["Use graph-grounded retrieval with provenance."],
                }
            ],
        }

        evidence = skills_ollama._evidence_from_recommendations(recommendations)

        self.assertIn("knowledge-graph-rag", evidence)
        self.assertNotIn(request.query, evidence)

    def test_direct_lookup_evidence_is_formatted_with_route_context(self) -> None:
        evidence_payload = {
            "status": "ok",
            "route": "direct_lookup",
            "routing": {"route": "direct_lookup", "confidence": 0.9},
            "skill": {
                "skill_id": "skill:knowledge-graph-rag",
                "skill_name": "knowledge-graph-rag",
                "retrieval_units": [
                    {
                        "retrieval_unit_id": "retrieval:skill:knowledge-graph-rag:section:0:objective",
                        "text": "Use KG-enabled RAG for graph-grounded retrieval.",
                        "source_path": "skills/knowledge-graph-rag/SKILL.md",
                        "heading_path": "Objective",
                        "section_id": "skill:knowledge-graph-rag:section:0-objective",
                        "line_start": 12,
                        "line_end": 12,
                    }
                ],
            },
            "context": {
                "related_skill_ids": ["skill:knowledge-retrieval-rag"],
                "evidence_paths": [
                    "skill:knowledge-graph-rag -[COMPLEMENTS]-> skill:knowledge-retrieval-rag"
                ],
            },
        }

        evidence = skills_ollama._evidence_from_payload(evidence_payload)

        self.assertIn("Evidence route: direct_lookup", evidence)
        self.assertIn("skill=knowledge-graph-rag", evidence)
        self.assertIn("related=skill:knowledge-retrieval-rag", evidence)
        self.assertNotIn("No recommendations were available", evidence)


class SkillsOllamaAsyncTests(unittest.IsolatedAsyncioTestCase):
    async def test_list_ollama_models_returns_available_and_running_models(self) -> None:
        class FakeAsyncClient:
            def __init__(self, timeout: float) -> None:
                self.timeout = timeout

            async def __aenter__(self) -> FakeAsyncClient:
                return self

            async def __aexit__(self, *_args: object) -> None:
                return None

            async def get(self, url: str) -> httpx.Response:
                request = httpx.Request("GET", url)
                if url.endswith("/api/ps"):
                    return httpx.Response(
                        200,
                        request=request,
                        json={"models": [{"name": "qwen3:1.7b"}]},
                    )
                return httpx.Response(
                    200,
                    request=request,
                    json={
                        "models": [
                            {"name": "codex-gemma4-12b-64k:latest"},
                            {"name": "kgrag-qwen3-4b:latest"},
                            {"name": "qwen3:1.7b"},
                        ]
                    },
                )

        with mock.patch.dict(skills_ollama.os.environ, {}, clear=True):
            with mock.patch.object(skills_ollama.httpx, "AsyncClient", FakeAsyncClient):
                response = await skills_ollama.list_ollama_models("http://127.0.0.1:11434")

        self.assertEqual("ok", response["status"])
        self.assertEqual(
            [
                {"name": "codex-gemma4-12b-64k:latest", "running": False},
                {"name": "kgrag-qwen3-4b:latest", "running": False},
                {"name": "qwen3:1.7b", "running": True},
            ],
            response["models"],
        )

    async def test_answer_graph_query_uses_user_selected_model(self) -> None:
        class FakeAsyncClient:
            def __init__(self, timeout: float) -> None:
                self.timeout = timeout
                self.posts: list[tuple[str, str]] = []

            async def __aenter__(self) -> FakeAsyncClient:
                return self

            async def __aexit__(self, *_args: object) -> None:
                return None

            async def post(self, url: str, json: object) -> httpx.Response:
                model_name = json["model"] if isinstance(json, dict) else ""
                self.posts.append((url, str(model_name)))
                request = httpx.Request("POST", url)
                return httpx.Response(
                    200,
                    request=request,
                    json={"message": {"content": "Use sre-practice."}},
                )

        fake_client: FakeAsyncClient | None = None

        def fake_client_factory(timeout: float) -> FakeAsyncClient:
            nonlocal fake_client
            fake_client = FakeAsyncClient(timeout)
            return fake_client

        request = skills_contracts.QuerySkillsRequest(
            query="What skills support SRE?",
            model="qwen3:1.7b",
        )
        recommendations = _recommendations_fixture()

        with mock.patch.dict(skills_ollama.os.environ, {}, clear=True):
            with mock.patch.object(skills_ollama.httpx, "AsyncClient", fake_client_factory):
                response = await skills_ollama.answer_graph_query(request, recommendations)

        self.assertIsNotNone(fake_client)
        assert fake_client is not None
        self.assertIn(
            ("http://127.0.0.1:11434/api/chat", "qwen3:1.7b"),
            fake_client.posts,
        )
        self.assertEqual("qwen3:1.7b", response["model"])


def _recommendations_fixture() -> dict[str, object]:
    return {
        "status": "ok",
        "recommendations": [
            {
                "skill_name": "sre-practice",
                "rationale": "Relevant to production reliability.",
                "source_paths": ["skills/sre-practice/SKILL.md"],
                "evidence_snippets": ["Connect user impact to service objectives."],
            }
        ],
    }


if __name__ == "__main__":
    unittest.main()
