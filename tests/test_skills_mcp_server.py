"""Tests for the read-only Skills MCP server facade."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
import unittest
from io import StringIO
from pathlib import Path
from typing import Any

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "skills_mcp_server.py"


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("skills_mcp_server", SCRIPT)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SkillsMcpServerTests(unittest.TestCase):
    def test_capability_discovery_lists_read_only_tools_and_resources(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        tool_names = {tool["name"] for tool in server.list_tools()}
        resource_uris = {resource["uri"] for resource in server.list_resources()}

        self.assertEqual(
            {
                "search_skills",
                "get_skill",
                "recommend_skills",
                "get_skill_context",
                "route_skill_query",
                "resolve_skill",
                "get_skill_execution_guide",
            },
            tool_names,
        )
        self.assertIn("skills://ontology", resource_uris)
        self.assertIn("skills://contract", resource_uris)
        self.assertNotIn("skills://schema", resource_uris)
        self.assertNotIn("execute_cypher", tool_names)
        self.assertNotIn("load_skills", tool_names)
        for tool in server.list_tools():
            self.assertIn("inputSchema", tool)
            self.assertEqual("object", tool["inputSchema"]["type"])

    def test_recommend_skills_returns_bounded_grounded_context(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        response = server.call_tool(
            "recommend_skills",
            {
                "query": "graph rag ontology retrieval",
                "limit": 2,
                "token_budget": 60,
            },
        )

        self.assertEqual("ok", response["status"])
        self.assertLessEqual(len(response["recommendations"]), 2)
        first = response["recommendations"][0]
        self.assertEqual("kg-enabled-rag", first["skill_name"])
        self.assertTrue(first["evidence_snippets"])
        self.assertTrue(first["evidence_paths"])
        self.assertTrue(first["source_paths"])
        self.assertNotIn("embedding", repr(response))
        self.assertNotIn("MATCH ", repr(response))

    def test_get_skill_context_returns_related_connected_skills(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        response = server.call_tool(
            "get_skill_context",
            {"skill_id": "skill:kg-enabled-rag", "limit": 5},
        )

        self.assertEqual("ok", response["status"])
        self.assertEqual("skill:kg-enabled-rag", response["skill_id"])
        self.assertIn("skill:knowledge-retrieval-rag", response["related_skill_ids"])
        self.assertTrue(response["evidence_paths"])

    def test_route_skill_query_classifies_agent_request_shape(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        direct = server.call_tool("route_skill_query", {"query": "tell me about kg-enabled-rag"})
        recommendation = server.call_tool(
            "route_skill_query", {"query": "Which skills should I use for graph retrieval?"}
        )
        context = server.call_tool(
            "route_skill_query", {"query": "What skills are related to kg-enabled-rag?"}
        )
        execution_plan = server.call_tool(
            "route_skill_query", {"query": "How do I apply kg-enabled-rag as an execution plan?"}
        )

        self.assertEqual("direct_lookup", direct["route"])
        self.assertEqual("skill:kg-enabled-rag", direct["resolved_skill_id"])
        self.assertEqual("recommendation", recommendation["route"])
        self.assertEqual("context", context["route"])
        self.assertEqual("execution_plan", execution_plan["route"])
        for response in (direct, recommendation, context, execution_plan):
            self.assertGreaterEqual(response["confidence"], 0.6)
            self.assertIn("rationale", response)

    def test_resolve_skill_maps_names_to_canonical_skill_ids(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        response = server.call_tool("resolve_skill", {"name": "kg-enabled-rag"})

        self.assertEqual("ok", response["status"])
        self.assertEqual("skill:kg-enabled-rag", response["skill_id"])
        self.assertEqual("kg-enabled-rag", response["skill_name"])
        self.assertTrue(response["source_paths"])

    def test_get_skill_execution_guide_returns_actionable_sections(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        response = server.call_tool(
            "get_skill_execution_guide", {"skill_id": "skill:kg-enabled-rag"}
        )

        self.assertEqual("ok", response["status"])
        self.assertEqual("skill:kg-enabled-rag", response["skill_id"])
        self.assertTrue(response["when_to_use"])
        self.assertTrue(response["objective"])
        self.assertTrue(response["procedure"])
        self.assertTrue(response["rules"])
        self.assertTrue(response["verification_checklist"])
        self.assertIn("skill:knowledge-retrieval-rag", response["related_skill_ids"])
        self.assertTrue(response["evidence"])

    def test_unsupported_write_or_cypher_access_is_denied(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        for tool_name in ("execute_cypher", "delete_skill", "load_skills"):
            response = server.call_tool(tool_name, {"cypher": "DELETE FROM graph"})
            self.assertEqual("error", response["status"])
            self.assertIn("Unsupported read-only Skills MCP tool", response["message"])

    def test_json_rpc_mcp_discovery_and_tool_call(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        tools_response = server.handle_json_rpc(
            {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
        )
        call_response = server.handle_json_rpc(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "recommend_skills",
                    "arguments": {"query": "graph rag ontology retrieval", "limit": 1},
                },
            }
        )

        self.assertEqual("2.0", tools_response["jsonrpc"])
        self.assertIn("tools", tools_response["result"])
        self.assertEqual("ok", call_response["result"]["structuredContent"]["status"])
        self.assertEqual(1, len(call_response["result"]["structuredContent"]["recommendations"]))

    def test_json_rpc_resource_read_and_stdio_loop(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        resource_response = server.handle_json_rpc(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "resources/read",
                "params": {"uri": "skills://contract"},
            }
        )
        input_stream = StringIO(
            json.dumps({"jsonrpc": "2.0", "id": 4, "method": "initialize", "params": {}}) + "\n"
        )
        output_stream = StringIO()

        mcp.stdio_loop(server, input_stream=input_stream, output_stream=output_stream)
        stdio_response = json.loads(output_stream.getvalue())

        self.assertIn("contents", resource_response["result"])
        self.assertEqual("skills://contract", resource_response["result"]["contents"][0]["uri"])
        self.assertEqual("2.0", stdio_response["jsonrpc"])
        self.assertIn("serverInfo", stdio_response["result"])

        contract = json.loads(resource_response["result"]["contents"][0]["text"])
        self.assertIn("tool_selection", contract)
        self.assertEqual("resolve_skill", contract["tool_selection"]["direct_lookup"]["tool"])
        self.assertEqual(
            "get_skill_execution_guide",
            contract["tool_selection"]["execution_plan"]["tool"],
        )
        self.assertIn("evidence_requirements", contract)
        self.assertIn("examples", contract)

        ontology_response = server.handle_json_rpc(
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "resources/read",
                "params": {"uri": "skills://ontology"},
            }
        )
        ontology_text = ontology_response["result"]["contents"][0]["text"]
        self.assertNotIn("Neo4j", ontology_text)
        self.assertNotIn("embedding", ontology_text.lower())
        self.assertNotIn("contentHash", ontology_text)

    def test_json_rpc_notifications_do_not_emit_responses(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()
        input_stream = StringIO(
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
        )
        output_stream = StringIO()

        mcp.stdio_loop(server, input_stream=input_stream, output_stream=output_stream)

        self.assertEqual("", output_stream.getvalue())

        input_stream = StringIO(
            json.dumps({"jsonrpc": "2.0", "method": "tools/list", "params": {}}) + "\n"
        )
        output_stream = StringIO()

        mcp.stdio_loop(server, input_stream=input_stream, output_stream=output_stream)

        self.assertEqual("", output_stream.getvalue())

    def test_official_mcp_client_discovers_and_calls_sdk_stdio_server(self) -> None:
        async def run_client() -> None:
            server_params = StdioServerParameters(
                command=sys.executable,
                args=[str(SCRIPT), "--sdk-stdio", "--fixture"],
                cwd=REPO_ROOT,
            )
            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    tool_names = {tool.name for tool in tools.tools}
                    self.assertIn("recommend_skills", tool_names)
                    self.assertIn("route_skill_query", tool_names)

                    result = await session.call_tool(
                        "recommend_skills",
                        {"query": "graph rag ontology retrieval", "limit": 1},
                    )

            serialised = repr(result)
            self.assertIn("kg-enabled-rag", serialised)
            self.assertNotIn("MATCH ", serialised)
            self.assertNotIn("embedding=", serialised)

        asyncio.run(run_client())


if __name__ == "__main__":
    unittest.main()
