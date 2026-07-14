"""Tests for the read-only Skills MCP server facade."""

from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
import time
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts/runtime/mcp/skills_mcp_server.py"


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

    def test_stdio_tool_schema_matches_cursor_friendly_mcp_servers(self) -> None:
        mcp = load_module()
        sanitized = mcp._sanitize_mcp_input_schema(
            {
                "title": "recommend_skillsArguments",
                "type": "object",
                "properties": {
                    "query": {
                        "title": "Query",
                        "type": "string",
                        "description": "Example query",
                        "minLength": 1,
                    }
                },
                "required": ["query"],
            }
        )
        self.assertNotIn("title", sanitized)
        self.assertNotIn("title", sanitized["properties"]["query"])
        self.assertEqual("Example query", sanitized["properties"]["query"]["description"])
        self.assertFalse(sanitized["additionalProperties"])

    def test_from_repository_fast_startup_uses_deterministic_embeddings_quickly(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.from_repository(REPO_ROOT / "skills", fast_startup=True)

        self.assertEqual(
            "deterministic-test-embedding",
            mcp._embedding_provider_from_plan(server.plan),
        )
        self.assertIsNone(server._embedding_upgrade_thread)

    def test_from_repository_fast_startup_schedules_production_embedding_upgrade(self) -> None:
        mcp = load_module()
        from scripts.lib.config import skills_config

        base = skills_config.load_settings(environ={})
        production_settings = skills_config.SkillsKgSettings(
            neo4j=base.neo4j.model_copy(update={"embedding_provider": "ollama-bge-m3"}),
            retrieval=base.retrieval,
            mcp=base.mcp,
            api=base.api,
        )
        with patch.object(mcp.skills_config, "load_settings", return_value=production_settings):
            server = mcp.SkillsMcpServer.from_repository(REPO_ROOT / "skills", fast_startup=True)
        self.assertIsNotNone(server._embedding_upgrade_thread)

    def test_stdio_full_repository_initializes_quickly_with_fast_startup(self) -> None:
        async def run_client() -> None:
            server_params = StdioServerParameters(
                command=sys.executable,
                args=[str(SCRIPT), "--sdk-stdio"],
                cwd=REPO_ROOT,
            )
            started = time.perf_counter()
            async with stdio_client(server_params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    elapsed = time.perf_counter() - started
                    self.assertLess(elapsed, 5.0)

        asyncio.run(run_client())

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
        self.assertTrue(first["source_paths"])
        self.assertTrue(first["evidence_anchors"])
        # Dedupe: section_ids and evidence_paths duplicate data already present on
        # evidence_anchors / source_paths; they remain in the usage-log selection_trace.
        self.assertNotIn("section_ids", first)
        self.assertNotIn("evidence_paths", first)
        anchor = first["evidence_anchors"][0]
        self.assertIn("section_id", anchor)
        self.assertIn("source_path", anchor)
        self.assertIn("heading_path", anchor)
        self.assertIn("line_start", anchor)
        self.assertIn("line_end", anchor)
        self.assertNotIn("embedding", repr(response))
        self.assertNotIn("MATCH ", repr(response))

    def test_recommend_skills_wire_evidence_is_deduplicated_not_rank_changed(self) -> None:
        """Lean wire projection must not change hybrid rank order or skill ids.

        Observed failure mode to prevent: dropping grounding fields that the
        contract requires (paths + heading/line), or changing which skills win.
        """

        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()
        args = {
            "query": "graph rag ontology retrieval",
            "limit": 2,
            "token_budget": 60,
        }

        with self.assertLogs("skills_usage", level="INFO") as captured:
            response = server.call_tool("recommend_skills", args)

        recommendations = response["recommendations"]
        self.assertTrue(recommendations)
        wire_ids = [item["skill_id"] for item in recommendations]
        for item in recommendations:
            self.assertNotIn("section_ids", item)
            self.assertNotIn("evidence_paths", item)
            self.assertIn("evidence_anchors", item)
            self.assertIn("evidence_snippets", item)
            self.assertIn("source_paths", item)
            self.assertIn("score", item)
            self.assertIn("rationale", item)

        audit_trace = None
        for line in captured.output:
            start = line.find("{")
            if start < 0:
                continue
            try:
                payload = json.loads(line[start:])
            except json.JSONDecodeError:
                continue
            if payload.get("event") != "skill_selection_run":
                continue
            if payload.get("tool") != "recommend_skills":
                continue
            audit_trace = payload.get("selection_trace")
            break

        self.assertIsInstance(audit_trace, dict)
        assert isinstance(audit_trace, dict)
        selected = audit_trace.get("selected")
        self.assertIsInstance(selected, dict)
        assert isinstance(selected, dict)
        self.assertEqual(wire_ids[0], selected.get("skill_id"))
        self.assertIn("section_ids", selected)
        self.assertIn("evidence_paths", selected)
        self.assertTrue(selected.get("section_ids"))
        self.assertTrue(selected.get("evidence_paths"))
        rank = audit_trace.get("rank")
        self.assertIsInstance(rank, list)
        assert isinstance(rank, list)
        self.assertEqual(wire_ids, [entry["skill_id"] for entry in rank[: len(wire_ids)]])

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

    def test_get_skill_accepts_bare_repository_slug(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        response = server.call_tool("get_skill", {"skill_id": "knowledge-graph-rag"})

        self.assertEqual("ok", response["status"])
        self.assertEqual("skill:knowledge-graph-rag", response["skill_id"])
        self.assertTrue(response["retrieval_units"])

    def test_get_skill_rejects_aliases_without_resolve_skill(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        response = server.call_tool("get_skill", {"skill_id": "kg-enabled-rag"})

        self.assertEqual("error", response["status"])
        self.assertIn("Skill not found", response["message"])

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

    def test_get_skill_context_accepts_bare_repository_slug(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        response = server.call_tool(
            "get_skill_context",
            {"skill_id": "knowledge-graph-rag", "limit": 5},
        )

        self.assertEqual("ok", response["status"])
        self.assertEqual("skill:knowledge-graph-rag", response["skill_id"])
        self.assertIn("skill:knowledge-retrieval-rag", response["related_skill_ids"])

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
            self.assertIn("suggested_tool", response)
            self.assertIn("evidence_required", response)
            self.assertNotIn(
                "selection_trace",
                response,
                msg="route_skill_query wire must omit selection_trace",
            )
            usage = response["usage"]
            self.assertIsInstance(usage, dict)
            self.assertTrue(str(usage.get("selection_run_id", "")).startswith("sel_"))
            self.assertEqual(response["route"], usage.get("route"))

    def test_route_skill_query_emits_selection_trace_to_usage_log(self) -> None:
        """Routing classification stays on the wire; fat evidence trace goes to audit."""

        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        with self.assertLogs("skills_usage", level="INFO") as captured:
            response = server.call_tool(
                "route_skill_query",
                {"query": "tell me about knowledge-graph-rag"},
            )

        self.assertEqual("direct_lookup", response["route"])
        self.assertEqual("skill:knowledge-graph-rag", response["resolved_skill_id"])
        self.assertEqual("get_skill", response["suggested_tool"])
        self.assertNotIn("selection_trace", response)
        wire_run_id = response["usage"]["selection_run_id"]

        audit_payload = None
        for line in captured.output:
            start = line.find("{")
            if start < 0:
                continue
            try:
                payload = json.loads(line[start:])
            except json.JSONDecodeError:
                continue
            if payload.get("event") != "skill_selection_run":
                continue
            if payload.get("tool") != "route_skill_query":
                continue
            audit_payload = payload
            break

        self.assertIsInstance(audit_payload, dict)
        assert isinstance(audit_payload, dict)
        self.assertEqual(wire_run_id, audit_payload.get("selection_run_id"))
        self.assertEqual("direct_lookup", audit_payload.get("query_intent"))
        self.assertIn("skill:knowledge-graph-rag", audit_payload.get("selected", []))
        trace = audit_payload.get("selection_trace")
        self.assertIsInstance(trace, dict)
        assert isinstance(trace, dict)
        self.assertEqual("route_skill_query", trace.get("tool"))
        self.assertEqual("direct_lookup", trace.get("query_intent"))
        self.assertIn("evidence", trace)
        self.assertIn("evidence_anchor_ids", trace)
        self.assertIn("filter", trace)

    def test_recommend_skills_omits_selection_trace_from_mcp_wire(self) -> None:
        """Agent-facing recommend payloads must not embed the fat audit trace.

        Cursor persists MCP tool JSON into the LLM conversation. Audit detail
        belongs in structured usage logs correlated by usage.selection_run_id.
        """

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
        self.assertNotIn(
            "selection_trace",
            response,
            msg="selection_trace must stay off the MCP wire for recommend_skills",
        )
        self.assertNotIn("rejected", response)
        self.assertIn("usage", response)
        usage = response["usage"]
        self.assertIsInstance(usage, dict)
        self.assertTrue(str(usage.get("selection_run_id", "")).startswith("sel_"))
        self.assertEqual("recommend_skills", usage.get("tool"))
        # Grounding fields for selected recommendations remain on the wire.
        if not response.get("uncertain"):
            recommendations = response.get("recommendations")
            self.assertIsInstance(recommendations, list)
            self.assertTrue(recommendations)
            first = recommendations[0]
            self.assertIn("skill_id", first)
            self.assertIn("evidence_anchors", first)
            self.assertTrue(first["evidence_anchors"])

    def test_recommend_skills_wire_omits_trace_when_uncertain(self) -> None:
        """Abstention responses must also omit selection_trace (failure mode)."""

        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        response = server.call_tool(
            "recommend_skills",
            {
                "query": "zzzz unrelated nonsense query with no skill overlap",
                "limit": 2,
                "token_budget": 40,
            },
        )

        self.assertEqual("ok", response["status"])
        self.assertNotIn("selection_trace", response)
        self.assertIn("usage", response)
        self.assertTrue(str(response["usage"].get("selection_run_id", "")).startswith("sel_"))

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
        # Graph edge strings duplicate related_skill_ids; keep anchors for grounding.
        self.assertNotIn("evidence_paths", response)
        first_anchor = response["evidence"][0]
        self.assertIn("source_path", first_anchor)
        self.assertIn("heading_path", first_anchor)
        self.assertIn("line_start", first_anchor)
        self.assertIn("line_end", first_anchor)
        self.assertIn("section_id", first_anchor)

    def test_get_skill_execution_guide_keeps_non_empty_evidence_never_blank(self) -> None:
        """Lean projection must not empty contract-required evidence anchors."""

        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        response = server.call_tool(
            "get_skill_execution_guide",
            {"skill_id": "skill:knowledge-graph-rag", "related_limit": 10},
        )

        self.assertEqual("ok", response["status"])
        evidence = response["evidence"]
        self.assertIsInstance(evidence, (list, tuple))
        self.assertGreaterEqual(len(evidence), 1)
        headings = {item.get("heading_path") for item in evidence}
        self.assertTrue(
            headings & {"When to use", "Objective", "Procedure", "Rules", "Verification"}
        )
        self.assertNotIn("evidence_paths", response)
        self.assertTrue(response["related_skill_ids"])
        self.assertTrue(response["verification_checklist"])

    def test_get_skill_execution_guide_accepts_bare_repository_slug(self) -> None:
        mcp = load_module()
        server = mcp.SkillsMcpServer.for_test_fixture()

        response = server.call_tool(
            "get_skill_execution_guide", {"skill_id": "knowledge-graph-rag"}
        )

        self.assertEqual("ok", response["status"])
        self.assertEqual("skill:knowledge-graph-rag", response["skill_id"])
        self.assertTrue(response["procedure"])

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
                        self.assertNotIn("title", properties[param_name])
                    self.assertIsNone(recommend_tool.outputSchema)
                    self.assertNotIn("title", recommend_tool.inputSchema)

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
