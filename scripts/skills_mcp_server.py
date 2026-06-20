#!/usr/bin/env python3
"""Read-only Skills MCP server facade.

This module exposes in-process MCP-style capabilities with explicit schemas.
It intentionally does not expose arbitrary Cypher, writes or raw embeddings.
"""

from __future__ import annotations

import json
import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Mapping, NamedTuple, Sequence

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import embed_skill_chunks, load_skills_neo4j, retrieve_skills_hybrid


class ToolDefinition(NamedTuple):
    """MCP-style tool definition."""

    name: str
    description: str
    inputSchema: Mapping[str, object]


class ResourceDefinition(NamedTuple):
    """MCP-style resource definition."""

    uri: str
    name: str
    description: str
    mimeType: str


def _schema(properties: Mapping[str, object], required: Sequence[str]) -> dict[str, object]:
    return {
        "type": "object",
        "properties": dict(properties),
        "required": list(required),
        "additionalProperties": False,
    }


def _bounded_int(value: object, default: int, minimum: int, maximum: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        return default
    return max(minimum, min(value, maximum))


def _string(value: object) -> str:
    return value if isinstance(value, str) else ""


class SkillsMcpServer:
    """Read-only MCP-style facade over the skills retrieval graph."""

    def __init__(self, plan: load_skills_neo4j.LoadPlan) -> None:
        self._plan = plan

    @classmethod
    def for_test_fixture(cls) -> "SkillsMcpServer":
        return cls(retrieve_skills_hybrid.fixture_load_plan())

    @classmethod
    def from_repository(cls, skills_root: Path = Path("skills")) -> "SkillsMcpServer":
        plan = embed_skill_chunks.build_embedded_repository_load_plan(skills_root)
        return cls(plan)

    def list_tools(self) -> tuple[dict[str, object], ...]:
        tools = (
            ToolDefinition(
                name="search_skills",
                description="Search skills by keyword over skill names and chunk text.",
                inputSchema=_schema(
                    {
                        "query": {"type": "string", "minLength": 1},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 20},
                    },
                    ("query",),
                ),
            ),
            ToolDefinition(
                name="get_skill",
                description="Return one skill's bounded metadata and source chunks.",
                inputSchema=_schema(
                    {
                        "skill_id": {"type": "string", "minLength": 1},
                        "chunk_limit": {"type": "integer", "minimum": 1, "maximum": 10},
                    },
                    ("skill_id",),
                ),
            ),
            ToolDefinition(
                name="recommend_skills",
                description="Recommend connected skills for a task query with evidence.",
                inputSchema=_schema(
                    {
                        "query": {"type": "string", "minLength": 1},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 10},
                        "max_depth": {"type": "integer", "minimum": 0, "maximum": 3},
                        "token_budget": {"type": "integer", "minimum": 50, "maximum": 2000},
                    },
                    ("query",),
                ),
            ),
            ToolDefinition(
                name="get_skill_context",
                description="Return connected neighbouring skills and evidence paths.",
                inputSchema=_schema(
                    {
                        "skill_id": {"type": "string", "minLength": 1},
                        "limit": {"type": "integer", "minimum": 1, "maximum": 20},
                    },
                    ("skill_id",),
                ),
            ),
        )
        return tuple(tool._asdict() for tool in tools)

    def list_resources(self) -> tuple[dict[str, object], ...]:
        resources = (
            ResourceDefinition(
                uri="skills://ontology",
                name="Skills ontology",
                description="Conceptual ontology and graph contract for the skills KG.",
                mimeType="text/markdown",
            ),
            ResourceDefinition(
                uri="skills://contract",
                name="Skills MCP contract",
                description="Agent-safe tool semantics, result limits and evidence requirements.",
                mimeType="application/json",
            ),
        )
        return tuple(resource._asdict() for resource in resources)

    def handle_json_rpc(self, request: Mapping[str, object]) -> dict[str, object] | None:
        """Handle the small MCP JSON-RPC surface used by stdio clients."""

        request_id = request.get("id")
        method = _string(request.get("method"))
        if request_id is None:
            return None
        params = request.get("params")
        param_map = params if isinstance(params, dict) else {}
        if method == "initialize":
            return self._json_rpc_result(
                request_id,
                {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "skills-kg", "version": "0.1.0"},
                    "capabilities": {"tools": {}, "resources": {}},
                },
            )
        if method == "tools/list":
            return self._json_rpc_result(request_id, {"tools": self.list_tools()})
        if method == "resources/list":
            return self._json_rpc_result(request_id, {"resources": self.list_resources()})
        if method == "resources/read":
            uri = _string(param_map.get("uri"))
            return self._json_rpc_result(request_id, {"contents": self._read_resource(uri)})
        if method == "tools/call":
            tool_name = _string(param_map.get("name"))
            arguments = param_map.get("arguments")
            argument_map = arguments if isinstance(arguments, dict) else {}
            structured = self.call_tool(tool_name, argument_map)
            return self._json_rpc_result(
                request_id,
                {
                    "content": [{"type": "text", "text": json.dumps(structured, sort_keys=True)}],
                    "structuredContent": structured,
                },
            )
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Unsupported read-only Skills MCP method: {method}",
            },
        }

    @staticmethod
    def _json_rpc_result(request_id: object, result: Mapping[str, object]) -> dict[str, object]:
        return {"jsonrpc": "2.0", "id": request_id, "result": dict(result)}

    def _read_resource(self, uri: str) -> tuple[dict[str, object], ...]:
        if uri == "skills://ontology":
            text = "\n".join(
                (
                    "# Skills Public Ontology",
                    "",
                    "Skills are operational procedures for coding agents.",
                    "Categories group skills by practice area.",
                    "Sections and snippets provide source-backed evidence.",
                    "Relationships explain prerequisite, complementary and validating skills.",
                    "Task shapes, workflow stages and capabilities describe when a skill applies.",
                    "Responses should include source paths, section identifiers and rationale.",
                )
            )
            return ({"uri": uri, "mimeType": "text/markdown", "text": text},)
        if uri == "skills://contract":
            contract = {
                "read_only": True,
                "tools": [tool["name"] for tool in self.list_tools()],
                "limits": {
                    "recommend_skills.limit": 10,
                    "recommend_skills.max_depth": 3,
                    "get_skill.chunk_limit": 10,
                    "search_skills.limit": 20,
                },
                "exclusions": ["raw_cypher", "raw_embeddings", "write_tools"],
            }
            return (
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(contract, sort_keys=True),
                },
            )
        return (
            {
                "uri": uri,
                "mimeType": "application/json",
                "text": json.dumps({"status": "error", "message": "Resource not found"}),
            },
        )

    def call_tool(self, name: str, arguments: Mapping[str, object]) -> dict[str, object]:
        if name == "search_skills":
            return self._search_skills(arguments)
        if name == "get_skill":
            return self._get_skill(arguments)
        if name == "recommend_skills":
            return self._recommend_skills(arguments)
        if name == "get_skill_context":
            return self._get_skill_context(arguments)
        return {
            "status": "error",
            "message": f"Unsupported read-only Skills MCP tool: {name}",
        }

    def _skills(self) -> tuple[load_skills_neo4j.GraphNode, ...]:
        return tuple(node for node in self._plan.nodes if node.label == "Skill")

    def _chunks_for_skill(self, skill_id: str) -> tuple[load_skills_neo4j.GraphNode, ...]:
        return tuple(
            node
            for node in self._plan.nodes
            if node.label == "SkillChunk" and node.properties.get("skill_id") == skill_id
        )

    def _skill_by_id(self, skill_id: str) -> load_skills_neo4j.GraphNode | None:
        for skill in self._skills():
            if skill.id == skill_id:
                return skill
        return None

    def _search_skills(self, arguments: Mapping[str, object]) -> dict[str, object]:
        query = _string(arguments.get("query")).lower()
        limit = _bounded_int(arguments.get("limit"), 5, 1, 20)
        matches: list[dict[str, object]] = []
        for skill in self._skills():
            skill_name = _string(skill.properties.get("name"))
            chunks = self._chunks_for_skill(skill.id)
            haystack = " ".join(
                [skill_name, *(_string(chunk.properties.get("text")) for chunk in chunks)]
            ).lower()
            if query in haystack:
                matches.append(
                    {
                        "skill_id": skill.id,
                        "skill_name": skill_name,
                        "source_paths": sorted(
                            {
                                _string(chunk.properties.get("source_path"))
                                for chunk in chunks
                                if _string(chunk.properties.get("source_path"))
                            }
                        ),
                    }
                )
        return {"status": "ok", "results": matches[:limit]}

    def _get_skill(self, arguments: Mapping[str, object]) -> dict[str, object]:
        skill_id = _string(arguments.get("skill_id"))
        chunk_limit = _bounded_int(arguments.get("chunk_limit"), 3, 1, 10)
        skill = self._skill_by_id(skill_id)
        if skill is None:
            return {"status": "error", "message": f"Skill not found: {skill_id}"}
        chunks = self._chunks_for_skill(skill_id)[:chunk_limit]
        return {
            "status": "ok",
            "skill_id": skill.id,
            "skill_name": _string(skill.properties.get("name")),
            "chunks": [
                {
                    "chunk_id": chunk.id,
                    "text": _string(chunk.properties.get("text"))[:240],
                    "source_path": _string(chunk.properties.get("source_path")),
                    "section_id": _string(chunk.properties.get("section_id")),
                }
                for chunk in chunks
            ],
        }

    def _recommend_skills(self, arguments: Mapping[str, object]) -> dict[str, object]:
        query = _string(arguments.get("query"))
        limit = _bounded_int(arguments.get("limit"), 5, 1, 10)
        max_depth = _bounded_int(arguments.get("max_depth"), 2, 0, 3)
        token_budget = _bounded_int(arguments.get("token_budget"), 600, 50, 2000)
        result = retrieve_skills_hybrid.retrieve_hybrid_skills(
            self._plan,
            query,
            vector_candidates=(),
            limit=limit,
            max_depth=max_depth,
            token_budget=token_budget,
        )
        return {
            "status": "ok",
            "uncertain": result.uncertain,
            "message": result.message,
            "recommendations": [
                {
                    "skill_id": item.skill_id,
                    "skill_name": item.skill_name,
                    "score": item.score,
                    "rationale": item.why,
                    "evidence_snippets": item.evidence_snippets,
                    "source_paths": item.source_paths,
                    "section_ids": item.section_ids,
                    "evidence_paths": item.evidence_paths,
                }
                for item in result.recommendations
            ],
        }

    def _get_skill_context(self, arguments: Mapping[str, object]) -> dict[str, object]:
        skill_id = _string(arguments.get("skill_id"))
        limit = _bounded_int(arguments.get("limit"), 10, 1, 20)
        if self._skill_by_id(skill_id) is None:
            return {"status": "error", "message": f"Skill not found: {skill_id}"}
        related: list[str] = []
        evidence_paths: list[str] = []
        for relationship in self._plan.relationships:
            if relationship.source_id == skill_id:
                evidence_paths.append(
                    f"{relationship.source_id} -[{relationship.type}]-> {relationship.target_id}"
                )
                if relationship.target_label == "Skill":
                    related.append(relationship.target_id)
            elif relationship.target_id == skill_id:
                evidence_paths.append(
                    f"{relationship.source_id} -[{relationship.type}]-> {relationship.target_id}"
                )
                if relationship.source_label == "Skill":
                    related.append(relationship.source_id)
        return {
            "status": "ok",
            "skill_id": skill_id,
            "related_skill_ids": tuple(dict.fromkeys(related))[:limit],
            "evidence_paths": tuple(evidence_paths[:limit]),
        }


def main(argv: Sequence[str] | None = None) -> int:
    parser = ArgumentParser(description="Inspect read-only Skills MCP capabilities.")
    parser.add_argument("--list-tools", action="store_true")
    parser.add_argument("--list-resources", action="store_true")
    parser.add_argument("--stdio", action="store_true", help="Run stdio JSON-RPC MCP loop.")
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))
    server = SkillsMcpServer.from_repository()
    if args.list_tools:
        print(json.dumps(server.list_tools(), indent=2, sort_keys=True))
    elif args.list_resources:
        print(json.dumps(server.list_resources(), indent=2, sort_keys=True))
    else:
        stdio_loop(server)
    return 0


def stdio_loop(
    server: SkillsMcpServer,
    input_stream: Any = sys.stdin,
    output_stream: Any = sys.stdout,
) -> None:
    """Run a newline-delimited JSON-RPC loop without writing diagnostics to stdout."""

    for line in input_stream:
        if not isinstance(line, str) or not line.strip():
            continue
        try:
            request = json.loads(line)
            if not isinstance(request, dict):
                raise ValueError("request must be a JSON object")
            response = server.handle_json_rpc(request)
        except Exception as exc:  # pragma: no cover - defensive stdio boundary
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": str(exc)},
            }
        if response is not None:
            output_stream.write(json.dumps(response, sort_keys=True) + "\n")
            output_stream.flush()


if __name__ == "__main__":
    sys.exit(main())
