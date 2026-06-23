"""Live MCP integration tests for the deployed Skills API transport."""

from __future__ import annotations

import asyncio
import os
from datetime import timedelta

import httpx
import pytest
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

pytestmark = pytest.mark.live_neo4j

DEFAULT_MCP_URL = os.environ.get("SKILLS_MCP_URL", "http://127.0.0.1:8000/mcp")


def _live_environment_configured() -> bool:
    return all(os.environ.get(name) for name in ("NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"))


async def _call_tool(
    session: ClientSession,
    name: str,
    arguments: dict[str, object],
) -> dict[str, object]:
    result = await session.call_tool(
        name,
        arguments,
        read_timeout_seconds=timedelta(seconds=30),
    )
    assert not result.isError
    payload = result.structuredContent
    assert isinstance(payload, dict)
    return payload


@pytest.mark.skipif(not _live_environment_configured(), reason="live Neo4j environment is not configured")
def test_live_streamable_http_mcp_tools_cover_balanced_query_shapes() -> None:
    async def run_client() -> None:
        try:
            response = httpx.get("http://127.0.0.1:8000/health/live", timeout=5.0)
        except httpx.HTTPError as exc:  # pragma: no cover - live environment dependent
            pytest.skip(f"live Skills API is not reachable: {exc}")
        if response.status_code != 200:
            pytest.skip(f"live Skills API is not healthy: {response.status_code}")

        async with streamable_http_client(DEFAULT_MCP_URL) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                tools = await session.list_tools()
                tool_names = {tool.name for tool in tools.tools}
                assert {
                    "route_skill_query",
                    "resolve_skill",
                    "search_skills",
                    "get_skill",
                    "recommend_skills",
                    "get_skill_context",
                    "get_skill_execution_guide",
                }.issubset(tool_names)

                routed_direct = await _call_tool(
                    session,
                    "route_skill_query",
                    {"query": "tell me about kg-enabled-rag"},
                )
                assert routed_direct["route"] == "direct_lookup"

                resolved = await _call_tool(session, "resolve_skill", {"name": "kg-enabled-rag"})
                assert resolved["skill_id"] == "skill:knowledge-graph-rag"

                skill_payload = await _call_tool(
                    session,
                    "get_skill",
                    {"skill_id": resolved["skill_id"], "retrieval_unit_limit": 4},
                )
                assert skill_payload["skill_name"] == "knowledge-graph-rag"
                assert "kg-enabled-rag" in skill_payload["aliases"]
                assert skill_payload["retrieval_units"]

                search_payload = await _call_tool(
                    session,
                    "search_skills",
                    {"query": "site-reliability-engineering", "limit": 5},
                )
                assert any(
                    item["skill_name"] == "sre-practice" for item in search_payload["results"]
                )

                routed_recommendation = await _call_tool(
                    session,
                    "route_skill_query",
                    {"query": "Which skills should I use for graph retrieval with ontology and provenance?"},
                )
                assert routed_recommendation["route"] == "recommendation"

                recommendation_payload = await _call_tool(
                    session,
                    "recommend_skills",
                    {"query": "graph retrieval ontology provenance", "limit": 3, "token_budget": 200},
                )
                assert recommendation_payload["recommendations"]
                assert recommendation_payload["recommendations"][0]["skill_name"] == "knowledge-graph-rag"

                routed_context = await _call_tool(
                    session,
                    "route_skill_query",
                    {"query": "What skills are related to knowledge-graph-rag?"},
                )
                assert routed_context["route"] == "context"

                context_payload = await _call_tool(
                    session,
                    "get_skill_context",
                    {"skill_id": resolved["skill_id"], "limit": 5},
                )
                assert "skill:knowledge-retrieval-rag" in context_payload["related_skill_ids"]

                routed_execution = await _call_tool(
                    session,
                    "route_skill_query",
                    {"query": "How do I apply knowledge-graph-rag as an execution plan?"},
                )
                assert routed_execution["route"] == "execution_plan"

                execution_payload = await _call_tool(
                    session,
                    "get_skill_execution_guide",
                    {"skill_id": resolved["skill_id"], "related_limit": 5},
                )
                assert execution_payload["verification_checklist"]
                assert execution_payload["evidence"]

    asyncio.run(run_client())
