"""Tests for the read-only Skills MCP server facade."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
import unittest
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

    def test_tool_parameters_include_descriptions(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        for tool in server.list_tools():
            properties = tool["inputSchema"]["properties"]
            self.assertIsInstance(properties, dict)
            for param_name, param_schema in properties.items():
                self.assertIn(
                    "description",
                    param_schema,
                    msg=f"{tool['name']}.{param_name} missing description",
                )
                self.assertTrue(
                    str(param_schema["description"]).strip(),
                    msg=f"{tool['name']}.{param_name} has empty description",
                )

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
        self.assertEqual("knowledge-graph-rag", first["skill_name"])
        self.assertTrue(first["evidence_snippets"])
        self.assertTrue(first["evidence_paths"])
        self.assertTrue(first["source_paths"])
        self.assertTrue(first["evidence_anchors"])
        self.assertNotIn("embedding", repr(response))
        self.assertNotIn("MATCH ", repr(response))

    def test_get_skill_returns_retrieval_units_not_legacy_chunks(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        response = server.call_tool("get_skill", {"skill_id": "skill:knowledge-graph-rag"})

        self.assertEqual("ok", response["status"])
        self.assertIn("retrieval_units", response)
        self.assertNotIn("chunks", response)
        first = response["retrieval_units"][0]
        self.assertIn("retrieval_unit_id", first)
        self.assertIn("heading_path", first)
        self.assertIn("line_start", first)
        self.assertIn("line_end", first)
        self.assertNotIn("chunk_id", first)

    def test_get_skill_context_returns_related_connected_skills(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        response = server.call_tool(
            "get_skill_context",
            {"skill_id": "skill:knowledge-graph-rag", "limit": 5},
        )

        self.assertEqual("ok", response["status"])
        self.assertEqual("skill:knowledge-graph-rag", response["skill_id"])
        self.assertIn("skill:knowledge-retrieval-rag", response["related_skill_ids"])
        self.assertTrue(response["evidence_paths"])

    def test_route_skill_query_classifies_agent_request_shape(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        direct = server.call_tool(
            "route_skill_query", {"query": "tell me about knowledge-graph-rag"}
        )
        recommendation = server.call_tool(
            "route_skill_query", {"query": "Which skills should I use for graph retrieval?"}
        )
        context = server.call_tool(
            "route_skill_query", {"query": "What skills are related to knowledge-graph-rag?"}
        )
        execution_plan = server.call_tool(
            "route_skill_query",
            {"query": "How do I apply knowledge-graph-rag as an execution plan?"},
        )

        self.assertEqual("direct_lookup", direct["route"])
        self.assertEqual("skill:knowledge-graph-rag", direct["resolved_skill_id"])
        self.assertEqual("recommendation", recommendation["route"])
        self.assertEqual("context", context["route"])
        self.assertEqual("execution_plan", execution_plan["route"])
        for response in (direct, recommendation, context, execution_plan):
            self.assertGreaterEqual(response["confidence"], 0.6)
            self.assertIn("rationale", response)
            trace = response["selection_trace"]
            self.assertEqual("route_skill_query", trace["tool"])
            self.assertEqual(response["route"], trace["query_intent"])
            self.assertTrue(str(trace["usage_event_id"]).startswith("sel-"))
            self.assertIn("filter", trace)

    def test_recommend_skills_includes_audit_selection_trace(self) -> None:
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

        trace = response["selection_trace"]
        self.assertEqual("recommend_skills", trace["tool"])
        self.assertEqual("recommendation", trace["query_intent"])
        self.assertTrue(str(trace["usage_event_id"]).startswith("sel-"))
        self.assertIn("filter", trace)
        self.assertIn("rank", trace)
        self.assertIn("evidence_anchor_ids", trace)
        self.assertIn("selected", trace)
        self.assertIn("request", trace)
        self.assertIn("rejected", trace)
        self.assertTrue(trace["selected"]["evidence_anchors"])

    def test_resolve_skill_maps_names_to_canonical_skill_ids(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        response = server.call_tool("resolve_skill", {"name": "knowledge-graph-rag"})

        self.assertEqual("ok", response["status"])
        self.assertEqual("skill:knowledge-graph-rag", response["skill_id"])
        self.assertEqual("knowledge-graph-rag", response["skill_name"])
        self.assertTrue(response["source_paths"])

    def test_resolve_skill_accepts_aliases(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        response = server.call_tool("resolve_skill", {"name": "kg-enabled-rag"})

        self.assertEqual("ok", response["status"])
        self.assertEqual("skill:knowledge-graph-rag", response["skill_id"])
        self.assertEqual("knowledge-graph-rag", response["skill_name"])

    def test_route_skill_query_does_not_false_positive_short_aliases_inside_other_words(
        self,
    ) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        response = server.call_tool(
            "route_skill_query",
            {
                "query": (
                    "Tell me about designing and building a web application using best practice "
                    "software engineering principles with separate front and back ends that "
                    "leverage real time streaming for communication between components."
                )
            },
        )

        self.assertEqual("recommendation", response["route"])
        self.assertIsNone(response["resolved_skill_id"])

    def test_get_skill_and_search_include_aliases(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        get_response = server.call_tool("get_skill", {"skill_id": "skill:knowledge-graph-rag"})
        search_response = server.call_tool("search_skills", {"query": "kg-enabled-rag", "limit": 3})

        self.assertIn("kg-enabled-rag", get_response["aliases"])
        self.assertEqual("knowledge-graph-rag", search_response["results"][0]["skill_name"])
        self.assertIn("kg-enabled-rag", search_response["results"][0]["aliases"])

    def test_get_skill_execution_guide_returns_actionable_sections(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        response = server.call_tool(
            "get_skill_execution_guide", {"skill_id": "skill:knowledge-graph-rag"}
        )

        self.assertEqual("ok", response["status"])
        self.assertEqual("skill:knowledge-graph-rag", response["skill_id"])
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

    def test_resource_contract_is_agent_readable(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        contract_resource = server.read_resource("skills://contract")
        ontology_resource = server.read_resource("skills://ontology")
        contract = json.loads(contract_resource[0]["text"])

        self.assertIn("tool_selection", contract)
        self.assertEqual("resolve_skill", contract["tool_selection"]["direct_lookup"]["tool"])
        self.assertEqual(
            "get_skill_execution_guide",
            contract["tool_selection"]["execution_plan"]["tool"],
        )
        self.assertIn("evidence_requirements", contract)
        self.assertIn(
            "heading paths and line ranges", contract["evidence_requirements"]["before_acting"]
        )
        self.assertIn("examples", contract)

        ontology_text = ontology_resource[0]["text"]
        self.assertNotIn("Neo4j", ontology_text)
        self.assertNotIn("embedding", ontology_text.lower())
        self.assertNotIn("contentHash", ontology_text)
        self.assertIn("retrieval units", ontology_text)

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

                    recommend_tool = next(
                        tool for tool in tools.tools if tool.name == "recommend_skills"
                    )
                    properties = recommend_tool.inputSchema.get("properties", {})
                    for param_name in ("query", "limit", "max_depth", "token_budget"):
                        self.assertIn("description", properties[param_name])
                        self.assertTrue(str(properties[param_name]["description"]).strip())

                    result = await session.call_tool(
                        "recommend_skills",
                        {"query": "graph rag ontology retrieval", "limit": 1},
                    )

            serialised = repr(result)
            self.assertIn("knowledge-graph-rag", serialised)
            self.assertNotIn("MATCH ", serialised)
            self.assertNotIn("embedding=", serialised)

        asyncio.run(run_client())


if __name__ == "__main__":
    unittest.main()
