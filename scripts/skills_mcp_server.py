#!/usr/bin/env python3
"""Read-only Skills MCP server facade.

This module exposes in-process MCP-style capabilities with explicit schemas.
It intentionally does not expose arbitrary Cypher, writes or raw embeddings.
"""

from __future__ import annotations

import json
import sys
from argparse import ArgumentParser
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import NamedTuple

from mcp.server.fastmcp import FastMCP

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import (
    embed_skill_chunks,
    load_skills_neo4j,
    retrieve_skills_hybrid,
    skills_config,
    skills_mcp_perf,
    skills_router,
    skills_usage,
)


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


def _string_list(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(item for item in value if isinstance(item, str) and item.strip())


def _enrich_recommendation_selection_trace(
    query: str,
    result: retrieve_skills_hybrid.HybridRetrievalResult,
) -> dict[str, object]:
    """Extend hybrid retrieval traces with MCP audit fields while preserving existing keys."""

    trace = dict(result.selection_trace)
    trace.setdefault("request", {"query": query})
    trace["tool"] = "recommend_skills"
    trace["query_intent"] = "recommendation"
    trace["usage_event_id"] = skills_router.usage_event_id("recommend_skills", query)
    rejected = trace.get("rejected", ())
    rejected_count = len(rejected) if isinstance(rejected, Sequence) else 0
    trace["filter"] = {
        "promotion_status": "promoted",
        "rejected_count": rejected_count,
    }
    trace["rank"] = [
        {
            "skill_id": item.skill_id,
            "skill_name": item.skill_name,
            "rank": index + 1,
            "score": item.score,
        }
        for index, item in enumerate(result.recommendations)
    ]
    selected = trace.get("selected")
    evidence_anchor_ids: list[str] = []
    if isinstance(selected, dict):
        anchors = selected.get("evidence_anchors", ())
        if isinstance(anchors, Sequence):
            for anchor in anchors:
                if not isinstance(anchor, Mapping):
                    continue
                anchor_id = _string(anchor.get("section_id")) or _string(
                    anchor.get("retrieval_unit_id")
                )
                if anchor_id:
                    evidence_anchor_ids.append(anchor_id)
    trace["evidence_anchor_ids"] = evidence_anchor_ids
    if result.uncertain:
        trace["abstention_reason"] = result.message
    return trace


class SkillsMcpServer:
    """Read-only MCP-style facade over the skills retrieval graph."""

    def __init__(
        self,
        plan: load_skills_neo4j.LoadPlan,
        settings: skills_config.SkillsKgSettings | None = None,
    ) -> None:
        self._plan = plan
        self._settings = settings or skills_config.load_settings()

    @classmethod
    def for_test_fixture(cls) -> SkillsMcpServer:
        # Small fixture graphs score lower than the full library; keep open abstention
        # so journey fixtures remain valid under production retrieval defaults.
        base = skills_config.load_settings(environ={})
        fixture_settings = skills_config.SkillsKgSettings(
            neo4j=base.neo4j,
            retrieval=skills_config.RetrievalSettings(
                min_confident_score=0.1,
                min_top1_margin=0.0,
                min_vector_candidate_score=base.retrieval.min_vector_candidate_score,
                default_token_budget=base.retrieval.default_token_budget,
                default_limit=base.retrieval.default_limit,
                max_limit=base.retrieval.max_limit,
                max_depth=base.retrieval.max_depth,
            ),
            mcp=base.mcp,
            api=base.api,
        )
        return cls(retrieve_skills_hybrid.fixture_load_plan(), fixture_settings)

    @classmethod
    def from_repository(cls, skills_root: Path = Path("skills")) -> SkillsMcpServer:
        plan = embed_skill_chunks.build_embedded_repository_load_plan(skills_root)
        return cls(plan)

    def reload_plan(self, plan: load_skills_neo4j.LoadPlan) -> None:
        """Replace the in-memory graph plan after admin ingest or repository reload."""

        self._plan = plan

    def reload_from_repository(self, skills_root: Path) -> None:
        """Rebuild the graph plan from an on-disk skills tree."""

        self.reload_plan(embed_skill_chunks.build_embedded_repository_load_plan(skills_root))

    def list_tools(self) -> tuple[dict[str, object], ...]:
        mcp_limits = self._settings.mcp
        tools = (
            ToolDefinition(
                name="search_skills",
                description="Search skills by keyword over skill names and retrieval-unit text.",
                inputSchema=_schema(
                    {
                        "query": {"type": "string", "minLength": 1},
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": mcp_limits.search_limit_max,
                        },
                    },
                    ("query",),
                ),
            ),
            ToolDefinition(
                name="get_skill",
                description="Return one skill's bounded metadata and retrieval units.",
                inputSchema=_schema(
                    {
                        "skill_id": {"type": "string", "minLength": 1},
                        "retrieval_unit_limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": mcp_limits.retrieval_unit_limit_max,
                        },
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
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": mcp_limits.recommend_limit_max,
                        },
                        "max_depth": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": self._settings.retrieval.max_depth,
                        },
                        "token_budget": {
                            "type": "integer",
                            "minimum": mcp_limits.token_budget_min,
                            "maximum": mcp_limits.token_budget_max,
                        },
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
                        "limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": mcp_limits.context_limit_max,
                        },
                    },
                    ("skill_id",),
                ),
            ),
            ToolDefinition(
                name="route_skill_query",
                description=(
                    "Classify a skill question as direct_lookup, recommendation, context or "
                    "execution_plan before selecting retrieval evidence."
                ),
                inputSchema=_schema(
                    {
                        "query": {"type": "string", "minLength": 1},
                    },
                    ("query",),
                ),
            ),
            ToolDefinition(
                name="resolve_skill",
                description="Resolve a human skill name or canonical id to a Skills KG skill id.",
                inputSchema=_schema(
                    {
                        "name": {"type": "string", "minLength": 1},
                    },
                    ("name",),
                ),
            ),
            ToolDefinition(
                name="get_skill_execution_guide",
                description=(
                    "Return when-to-use, objective, procedure, rules, verification checklist "
                    "and related skills for a resolved skill."
                ),
                inputSchema=_schema(
                    {
                        "skill_id": {"type": "string", "minLength": 1},
                        "related_limit": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": mcp_limits.context_limit_max,
                        },
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

    def read_resource(self, uri: str) -> tuple[dict[str, object], ...]:
        """Read a public, agent-safe MCP resource."""

        return self._read_resource(uri)

    def graph_summary(self) -> dict[str, object]:
        """Return a D3-friendly, bounded graph summary without raw embeddings."""

        nodes: list[dict[str, object]] = []
        for node in self._plan.nodes:
            if node.label not in {
                "Skill",
                "TaskShape",
                "WorkflowStage",
                "Capability",
                "ControlTheme",
                "KnowledgeDomain",
            }:
                continue
            nodes.append(
                {
                    "id": node.id,
                    "label": node.label,
                    "name": _string(node.properties.get("name")) or node.id,
                    "category": _string(node.properties.get("category")),
                    "source_path": _string(node.properties.get("path")),
                }
            )
        node_ids = {node["id"] for node in nodes}
        links = [
            {
                "source": relationship.source_id,
                "target": relationship.target_id,
                "type": relationship.type,
            }
            for relationship in self._plan.relationships
            if relationship.source_label == "Skill"
            and relationship.type
            in {
                "RELATED_TO",
                "PRECEDES",
                "REQUIRES",
                "COMPLEMENTS",
                "REFINES",
                "GOVERNS",
                "VALIDATES",
                "HAS_WORKFLOW_STAGE",
                "HAS_TASK_SHAPE",
                "HAS_CAPABILITY",
            }
            and relationship.source_id in node_ids
            and relationship.target_id in node_ids
        ]
        return {
            "status": "ok",
            "nodes": nodes,
            "links": links,
            "node_count": len(nodes),
            "link_count": len(links),
        }

    def graph_logical_counts(self) -> dict[str, dict[str, int]]:
        """Return bounded graph node and relationship counts for telemetry."""

        node_counts: dict[str, int] = {}
        for node in self._plan.nodes:
            node_counts[node.label] = node_counts.get(node.label, 0) + 1
        relationship_counts: dict[str, int] = {}
        for relationship in self._plan.relationships:
            relationship_counts[relationship.type] = (
                relationship_counts.get(relationship.type, 0) + 1
            )
        return {
            "nodes": dict(sorted(node_counts.items())),
            "relationships": dict(sorted(relationship_counts.items())),
        }

    def technical_info(self) -> dict[str, object]:
        """Return safe technical information for MCP clients and operators."""

        contract = json.loads(_string(self.read_resource("skills://contract")[0].get("text")))
        return {
            "status": "ok",
            "server_name": "skills-kg",
            "read_only": True,
            "tools": contract.get("tools", []),
            "resources": [resource["uri"] for resource in self.list_resources()],
            "limits": contract.get("limits", {}),
            "api_endpoints": [
                "GET /health/live",
                "GET /health/ready",
                "GET /skills/graph",
                "GET /skills/search",
                "GET /skills/{skill_id}",
                "GET /skills/{skill_id}/context",
                "GET /ollama/models",
                "POST /skills/route",
                "GET /skills/resolve",
                "GET /skills/{skill_id}/execution-guide",
                "POST /skills/recommend",
                "POST /skills/query",
                "POST /skills/upload/preview",
                "GET /mcp/technical-info",
            ],
        }

    @property
    def plan(self) -> load_skills_neo4j.LoadPlan:
        """Expose the bounded in-memory graph snapshot for internal API planning."""

        return self._plan

    def _read_resource(self, uri: str) -> tuple[dict[str, object], ...]:
        if uri == "skills://ontology":
            text = "\n".join(
                (
                    "# Skills Public Ontology",
                    "",
                    "Skills are operational procedures for coding agents.",
                    "Categories group skills by practice area.",
                    "Sections and retrieval units provide source-backed evidence with heading paths and line ranges.",
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
                    "recommend_skills.limit": self._settings.mcp.recommend_limit_max,
                    "recommend_skills.max_depth": self._settings.retrieval.max_depth,
                    "get_skill.retrieval_unit_limit": self._settings.mcp.retrieval_unit_limit_max,
                    "search_skills.limit": self._settings.mcp.search_limit_max,
                    "get_skill_context.limit": self._settings.mcp.context_limit_max,
                    "get_skill_execution_guide.related_limit": self._settings.mcp.context_limit_max,
                },
                "tool_selection": {
                    "direct_lookup": {
                        "when": "The request names one known skill or asks what a skill is.",
                        "tool": "resolve_skill",
                        "then": ["get_skill", "get_skill_context"],
                    },
                    "recommendation": {
                        "when": "The request asks which skills to use for a task or no exact skill is named.",
                        "tool": "recommend_skills",
                    },
                    "context": {
                        "when": "The request asks for related, prerequisite, complementary or neighbouring skills.",
                        "tool": "get_skill_context",
                    },
                    "execution_plan": {
                        "when": "The request asks how to apply, execute or verify a known skill.",
                        "tool": "get_skill_execution_guide",
                    },
                },
                "classification_rules": [
                    "Call route_skill_query before answering ambiguous natural-language skill questions.",
                    "Use resolve_skill before get_skill, get_skill_context or get_skill_execution_guide when users provide a human-readable name.",
                    "Use recommend_skills only for task-oriented recommendation prompts.",
                    "Use get_skill_execution_guide before acting from a skill so the agent has procedure, rules and verification evidence.",
                ],
                "evidence_requirements": {
                    "before_acting": [
                        "selected route",
                        "resolved skill id when applicable",
                        "source paths",
                        "heading paths and line ranges",
                        "section ids or evidence paths",
                        "verification checklist for execution_plan",
                    ],
                    "never_return": ["raw_cypher", "raw_embeddings", "secrets"],
                },
                "examples": [
                    {
                        "query": "tell me about accessibility-wcag",
                        "route": "direct_lookup",
                        "tool_sequence": ["route_skill_query", "resolve_skill", "get_skill"],
                    },
                    {
                        "query": "which skills should I use for a secure MCP server?",
                        "route": "recommendation",
                        "tool_sequence": ["route_skill_query", "recommend_skills"],
                    },
                    {
                        "query": "what is related to knowledge-graph-rag?",
                        "route": "context",
                        "tool_sequence": [
                            "route_skill_query",
                            "resolve_skill",
                            "get_skill_context",
                        ],
                    },
                    {
                        "query": "how do I apply tdd-practice?",
                        "route": "execution_plan",
                        "tool_sequence": [
                            "route_skill_query",
                            "resolve_skill",
                            "get_skill_execution_guide",
                        ],
                    },
                ],
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
        with skills_mcp_perf.tool_span(name, arguments) as span:
            if name == "search_skills":
                result = self._search_skills(arguments)
            elif name == "get_skill":
                result = self._get_skill(arguments)
            elif name == "recommend_skills":
                result = self._recommend_skills(arguments)
            elif name == "get_skill_context":
                result = self._get_skill_context(arguments)
            elif name == "route_skill_query":
                result = self._route_skill_query(arguments)
            elif name == "resolve_skill":
                result = self._resolve_skill(arguments)
            elif name == "get_skill_execution_guide":
                result = self._get_skill_execution_guide(arguments)
            else:
                result = {
                    "status": "error",
                    "message": f"Unsupported read-only Skills MCP tool: {name}",
                }
            return span.finish(result)

    def _skills(self) -> tuple[load_skills_neo4j.GraphNode, ...]:
        return tuple(node for node in self._plan.nodes if node.label == "Skill")

    def _retrieval_units_for_skill(self, skill_id: str) -> tuple[load_skills_neo4j.GraphNode, ...]:
        return tuple(
            node
            for node in self._plan.nodes
            if node.label == "RetrievalUnit" and node.properties.get("skill_id") == skill_id
        )

    def _skill_by_id(self, skill_id: str) -> load_skills_neo4j.GraphNode | None:
        for skill in self._skills():
            if skill.id == skill_id:
                return skill
        return None

    def _search_skills(self, arguments: Mapping[str, object]) -> dict[str, object]:
        query = _string(arguments.get("query")).lower()
        limit = _bounded_int(arguments.get("limit"), 5, 1, self._settings.mcp.search_limit_max)
        matches: list[dict[str, object]] = []
        for skill in self._skills():
            skill_name = _string(skill.properties.get("name"))
            retrieval_units = self._retrieval_units_for_skill(skill.id)
            haystack = " ".join(
                [
                    skill_name,
                    *(_string_list(skill.properties.get("aliases"))),
                    *(_string(unit.properties.get("text")) for unit in retrieval_units),
                ]
            ).lower()
            if query in haystack:
                with skills_mcp_perf.payload_construction():
                    matches.append(
                        {
                            "skill_id": skill.id,
                            "skill_name": skill_name,
                            "aliases": list(_string_list(skill.properties.get("aliases"))),
                            "source_paths": sorted(
                                {
                                    _string(unit.properties.get("source_path"))
                                    for unit in retrieval_units
                                    if _string(unit.properties.get("source_path"))
                                }
                            ),
                        }
                    )
        with skills_mcp_perf.payload_construction():
            return {"status": "ok", "results": matches[:limit]}

    def _get_skill(self, arguments: Mapping[str, object]) -> dict[str, object]:
        skill_id = _string(arguments.get("skill_id"))
        retrieval_unit_limit = _bounded_int(
            arguments.get("retrieval_unit_limit"), 3, 1, self._settings.mcp.retrieval_unit_limit_max
        )
        skill = self._skill_by_id(skill_id)
        if skill is None:
            with skills_mcp_perf.payload_construction():
                return {"status": "error", "message": f"Skill not found: {skill_id}"}
        retrieval_units = self._retrieval_units_for_skill(skill_id)[:retrieval_unit_limit]
        with skills_mcp_perf.payload_construction():
            return {
                "status": "ok",
                "skill_id": skill.id,
                "skill_name": _string(skill.properties.get("name")),
                "aliases": list(_string_list(skill.properties.get("aliases"))),
                "retrieval_units": [
                    {
                        "retrieval_unit_id": unit.id,
                        "text": _string(unit.properties.get("text"))[:240],
                        "source_path": _string(unit.properties.get("source_path")),
                        "heading_path": _string(unit.properties.get("heading_path")),
                        "section_id": _string(unit.properties.get("section_id")),
                        "line_start": unit.properties.get("line_start", 0),
                        "line_end": unit.properties.get("line_end", 0),
                    }
                    for unit in retrieval_units
                ],
            }

    def _recommend_skills(self, arguments: Mapping[str, object]) -> dict[str, object]:
        query = _string(arguments.get("query"))
        limit = _bounded_int(arguments.get("limit"), 5, 1, self._settings.mcp.recommend_limit_max)
        max_depth = _bounded_int(
            arguments.get("max_depth"), 2, 0, self._settings.retrieval.max_depth
        )
        token_budget = _bounded_int(
            arguments.get("token_budget"),
            600,
            self._settings.mcp.token_budget_min,
            self._settings.mcp.token_budget_max,
        )
        result = retrieve_skills_hybrid.retrieve_hybrid_skills(
            self._plan,
            query,
            vector_candidates=(),
            limit=limit,
            max_depth=max_depth,
            token_budget=token_budget,
            retrieval_settings=self._settings.retrieval,
        )
        with skills_mcp_perf.payload_construction():
            selection_trace = _enrich_recommendation_selection_trace(query, result)
            recommendations: list[dict[str, object]] = [
                {
                    "skill_id": item.skill_id,
                    "skill_name": item.skill_name,
                    "score": item.score,
                    "rationale": item.why,
                    "evidence_snippets": item.evidence_snippets,
                    "source_paths": item.source_paths,
                    "section_ids": item.section_ids,
                    "evidence_anchors": item.evidence_anchors,
                    "evidence_paths": item.evidence_paths,
                }
                for item in result.recommendations
            ]
            response: dict[str, object] = {
                "status": "ok",
                "uncertain": result.uncertain,
                "message": result.message,
                "selection_trace": selection_trace,
                "recommendations": recommendations,
            }
        selection_run_id = skills_usage.new_selection_run_id()
        for rank, recommendation in enumerate(recommendations, start=1):
            recommendation_skill_id = _string(recommendation.get("skill_id"))
            if recommendation_skill_id:
                skills_usage.record_skill_hit(
                    recommendation_skill_id,
                    "recommend_skills",
                    rank=rank,
                )
        if result.uncertain:
            skills_usage.record_abstention("recommend_skills", "low_confidence")
        skills_usage.emit_skill_selection_run(
            {
                "selection_run_id": selection_run_id,
                "tool": "recommend_skills",
                "query_intent": "recommendation",
                "uncertain": result.uncertain,
                "selected": [
                    _string(item.get("skill_id"))
                    for item in recommendations
                    if _string(item.get("skill_id"))
                ],
                "selection_trace": selection_trace,
            }
        )
        with skills_mcp_perf.payload_construction():
            return skills_usage.attach_usage_metadata(
                response,
                selection_run_id,
                tool="recommend_skills",
                uncertain=result.uncertain,
            )

    def _get_skill_context(self, arguments: Mapping[str, object]) -> dict[str, object]:
        skill_id = _string(arguments.get("skill_id"))
        limit = _bounded_int(arguments.get("limit"), 10, 1, self._settings.mcp.context_limit_max)
        if self._skill_by_id(skill_id) is None:
            with skills_mcp_perf.payload_construction():
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
        related_skill_ids = tuple(dict.fromkeys(related))[:limit]
        with skills_mcp_perf.payload_construction():
            response: dict[str, object] = {
                "status": "ok",
                "skill_id": skill_id,
                "related_skill_ids": list(related_skill_ids),
                "evidence_paths": list(evidence_paths[:limit]),
            }
        selection_run_id = skills_usage.new_selection_run_id()
        skills_usage.record_skill_hit(skill_id, "get_skill_context")
        skills_usage.emit_skill_selection_run(
            {
                "selection_run_id": selection_run_id,
                "tool": "get_skill_context",
                "query_intent": "context",
                "selected": [skill_id, *list(related_skill_ids)],
            }
        )
        with skills_mcp_perf.payload_construction():
            return skills_usage.attach_usage_metadata(
                response,
                selection_run_id,
                tool="get_skill_context",
            )

    def _route_skill_query(self, arguments: Mapping[str, object]) -> dict[str, object]:
        query = _string(arguments.get("query"))
        result = skills_router.route_skill_query(self._plan, query)
        selection_run_id = skills_usage.new_selection_run_id()
        resolved_skill_id = result.get("resolved_skill_id")
        if isinstance(resolved_skill_id, str) and resolved_skill_id:
            skills_usage.record_skill_hit(resolved_skill_id, "route_skill_query")
        selected: list[str] = []
        if isinstance(resolved_skill_id, str) and resolved_skill_id:
            selected.append(resolved_skill_id)
        skills_usage.emit_skill_selection_run(
            {
                "selection_run_id": selection_run_id,
                "tool": "route_skill_query",
                "query_intent": result.get("route"),
                "selected": selected,
                "confidence": result.get("confidence"),
                "suggested_tool": result.get("suggested_tool"),
            }
        )
        with skills_mcp_perf.payload_construction():
            return skills_usage.attach_usage_metadata(
                result,
                selection_run_id,
                tool="route_skill_query",
                route=result.get("route"),
            )

    def _resolve_skill(self, arguments: Mapping[str, object]) -> dict[str, object]:
        name = _string(arguments.get("name"))
        # Router work is handler time; payload construction is measured when the
        # response is serialised in ToolPerfSpan.finish().
        return skills_router.resolve_skill(self._plan, name)

    def _get_skill_execution_guide(self, arguments: Mapping[str, object]) -> dict[str, object]:
        skill_id = _string(arguments.get("skill_id"))
        related_limit = _bounded_int(
            arguments.get("related_limit"), 10, 1, self._settings.mcp.context_limit_max
        )
        result = skills_router.get_skill_execution_guide(
            self._plan,
            skill_id,
            related_limit=related_limit,
        )
        if result.get("status") != "ok":
            with skills_mcp_perf.payload_construction():
                return result
        selection_run_id = skills_usage.new_selection_run_id()
        skills_usage.record_execution_guide(skill_id, "get_skill_execution_guide")
        skills_usage.record_skill_hit(skill_id, "get_skill_execution_guide")
        skills_usage.emit_skill_selection_run(
            {
                "selection_run_id": selection_run_id,
                "tool": "get_skill_execution_guide",
                "query_intent": "execution_plan",
                "selected": [skill_id],
            }
        )
        with skills_mcp_perf.payload_construction():
            return skills_usage.attach_usage_metadata(
                result,
                selection_run_id,
                tool="get_skill_execution_guide",
            )


def build_fastmcp_server(server: SkillsMcpServer) -> FastMCP:
    """Build the official MCP SDK server for the Skills KG tools."""

    fastmcp = FastMCP("skills-kg", json_response=True)

    @fastmcp.tool(
        name="search_skills",
        description="Search skills by keyword over skill names and retrieval-unit text.",
        structured_output=True,
    )
    def search_skills(query: str, limit: int = 5) -> dict[str, object]:
        return server.call_tool("search_skills", {"query": query, "limit": limit})

    @fastmcp.tool(
        name="get_skill",
        description="Return one skill's bounded metadata and retrieval units.",
        structured_output=True,
    )
    def get_skill(skill_id: str, retrieval_unit_limit: int = 3) -> dict[str, object]:
        return server.call_tool(
            "get_skill",
            {"skill_id": skill_id, "retrieval_unit_limit": retrieval_unit_limit},
        )

    @fastmcp.tool(
        name="recommend_skills",
        description="Recommend connected skills for a task query with evidence.",
        structured_output=True,
    )
    def recommend_skills(
        query: str,
        limit: int = 5,
        max_depth: int = 2,
        token_budget: int = 600,
    ) -> dict[str, object]:
        return server.call_tool(
            "recommend_skills",
            {
                "query": query,
                "limit": limit,
                "max_depth": max_depth,
                "token_budget": token_budget,
            },
        )

    @fastmcp.tool(
        name="get_skill_context",
        description="Return connected neighbouring skills and evidence paths.",
        structured_output=True,
    )
    def get_skill_context(skill_id: str, limit: int = 10) -> dict[str, object]:
        return server.call_tool("get_skill_context", {"skill_id": skill_id, "limit": limit})

    @fastmcp.tool(
        name="route_skill_query",
        description=(
            "Classify a skill question as direct_lookup, recommendation, context or execution_plan."
        ),
        structured_output=True,
    )
    def route_skill_query(query: str) -> dict[str, object]:
        return server.call_tool("route_skill_query", {"query": query})

    @fastmcp.tool(
        name="resolve_skill",
        description="Resolve a human skill name or canonical id to a Skills KG skill id.",
        structured_output=True,
    )
    def resolve_skill(name: str) -> dict[str, object]:
        return server.call_tool("resolve_skill", {"name": name})

    @fastmcp.tool(
        name="get_skill_execution_guide",
        description=(
            "Return when-to-use, objective, procedure, rules, verification checklist and related skills."
        ),
        structured_output=True,
    )
    def get_skill_execution_guide(skill_id: str, related_limit: int = 10) -> dict[str, object]:
        return server.call_tool(
            "get_skill_execution_guide",
            {"skill_id": skill_id, "related_limit": related_limit},
        )

    @fastmcp.resource(
        "skills://ontology",
        name="Skills ontology",
        description="Conceptual ontology and graph contract for the skills KG.",
        mime_type="text/markdown",
    )
    def skills_ontology() -> str:
        return _string(server.read_resource("skills://ontology")[0].get("text"))

    @fastmcp.resource(
        "skills://contract",
        name="Skills MCP contract",
        description="Agent-safe tool semantics, result limits and evidence requirements.",
        mime_type="application/json",
    )
    def skills_contract() -> str:
        return _string(server.read_resource("skills://contract")[0].get("text"))

    return fastmcp


def main(argv: Sequence[str] | None = None) -> int:  # pragma: no cover
    parser = ArgumentParser(description="Inspect read-only Skills MCP capabilities.")
    parser.add_argument("--list-tools", action="store_true")
    parser.add_argument("--list-resources", action="store_true")
    parser.add_argument(
        "--sdk-stdio", action="store_true", help="Run official MCP SDK stdio server."
    )
    parser.add_argument("--fixture", action="store_true", help="Use a deterministic fixture graph.")
    parser.add_argument(
        "--metrics",
        action="store_true",
        help="Print combined usage and trust Prometheus metrics to stdout.",
    )
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))
    if args.metrics:
        from scripts.skills_metrics import metrics_text

        print(metrics_text(), end="")
        return 0
    server = (
        SkillsMcpServer.for_test_fixture() if args.fixture else SkillsMcpServer.from_repository()
    )
    if args.list_tools:
        print(json.dumps(server.list_tools(), indent=2, sort_keys=True))
    elif args.list_resources:
        print(json.dumps(server.list_resources(), indent=2, sort_keys=True))
    elif args.sdk_stdio:
        build_fastmcp_server(server).run(transport="stdio")
    else:
        build_fastmcp_server(server).run(transport="stdio")
    return 0


if __name__ == "__main__":
    sys.exit(main())
