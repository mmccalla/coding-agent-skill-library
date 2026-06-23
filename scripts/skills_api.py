#!/usr/bin/env python3
"""FastAPI app for the read-only Skills KG GraphRAG capability."""

from __future__ import annotations

from contextlib import asynccontextmanager
import json
import logging
import os
import re
import sys
import time
import uuid
from collections.abc import Awaitable, Callable, Mapping
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, Query, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import (
    check_neo4j_readiness,
    load_skills_neo4j,
    skills_config,
    skills_contracts,
    skills_ollama,
)
from scripts.skills_mcp_server import SkillsMcpServer, build_fastmcp_server

ReadinessProvider = Callable[[], Mapping[str, object]]
QueryProvider = Callable[
    [skills_contracts.QuerySkillsRequest, Mapping[str, object]], Awaitable[Mapping[str, object]]
]
ModelProvider = Callable[[str], Awaitable[Mapping[str, object]]]
MAX_UPLOAD_BYTES = 256 * 1024
API_LOGGER_NAME = "skills_api"
METRICS_REGISTRY = CollectorRegistry()
REQUESTS_TOTAL = Counter(
    "skills_api_requests_total",
    "Total Skills API HTTP requests by method, route and status code.",
    ("method", "route", "status_code"),
    registry=METRICS_REGISTRY,
)
REQUEST_DURATION_SECONDS = Histogram(
    "skills_api_request_duration_seconds",
    "Skills API HTTP request duration in seconds by method, route and status code.",
    ("method", "route", "status_code"),
    registry=METRICS_REGISTRY,
)
OLLAMA_FAILURES_TOTAL = Counter(
    "skills_api_ollama_failures_total",
    "Total Ollama-related API failures by operation and error type.",
    ("operation", "error_type"),
    registry=METRICS_REGISTRY,
)
READINESS_STATE = Gauge(
    "skills_api_readiness_state",
    "Current Skills API dependency readiness state; 1 means ready and 0 means degraded.",
    ("database",),
    registry=METRICS_REGISTRY,
)
GRAPH_NODES = Gauge(
    "skills_api_graph_nodes",
    "Current Skills KG node count by label in the API graph snapshot.",
    ("label",),
    registry=METRICS_REGISTRY,
)
GRAPH_RELATIONSHIPS = Gauge(
    "skills_api_graph_relationships",
    "Current Skills KG relationship count by type in the API graph snapshot.",
    ("type",),
    registry=METRICS_REGISTRY,
)
RETRIEVAL_REQUESTS_TOTAL = Counter(
    "skills_api_retrieval_requests_total",
    "Total retrieval requests by API operation, selected route and uncertainty state.",
    ("operation", "route", "uncertain"),
    registry=METRICS_REGISTRY,
)
RETRIEVAL_RECOMMENDATION_COUNT = Histogram(
    "skills_api_retrieval_recommendation_count",
    "Number of recommendations returned by retrieval operations.",
    ("operation", "route", "uncertain"),
    buckets=(0, 1, 2, 3, 5, 10),
    registry=METRICS_REGISTRY,
)
RETRIEVAL_TOP_SCORE = Histogram(
    "skills_api_retrieval_top_score",
    "Top recommendation score by retrieval operation and selected route.",
    ("operation", "route", "uncertain"),
    buckets=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 2.0),
    registry=METRICS_REGISTRY,
)
logging.getLogger(API_LOGGER_NAME).setLevel(logging.INFO)


def _default_readiness() -> Mapping[str, object]:
    if os.environ.get("NEO4J_URI"):
        settings = skills_config.load_settings().neo4j
        graph = load_skills_neo4j.neo4j_graph_from_settings(settings)
        try:
            report = check_neo4j_readiness.collect_readiness(graph.driver, settings)
            return {
                "status": "ok" if report.ready else "degraded",
                "read_only": True,
                **report.model_dump(),
            }
        except Exception as exc:
            return {"status": "degraded", "read_only": True, "ready": False, "errors": [str(exc)]}
        finally:
            graph.driver.close()
    return {"status": "ok", "read_only": True}


def _default_server() -> SkillsMcpServer:
    if os.environ.get("NEO4J_URI"):
        settings = skills_config.load_settings()
        graph = load_skills_neo4j.neo4j_graph_from_settings(settings.neo4j)
        try:
            plan = load_skills_neo4j.load_plan_from_neo4j(graph.driver, settings.neo4j)
            return SkillsMcpServer(plan, settings)
        finally:
            graph.driver.close()
    return SkillsMcpServer.from_repository()


def create_app(
    server: SkillsMcpServer | None = None,
    readiness_provider: ReadinessProvider | None = None,
    query_provider: QueryProvider | None = None,
    model_provider: ModelProvider | None = None,
) -> FastAPI:
    """Create the FastAPI app with a narrow read-only Skills service boundary."""

    skills_server = server or _default_server()
    readiness = readiness_provider or _default_readiness
    answer_query = query_provider or skills_ollama.answer_graph_query
    list_models = model_provider or skills_ollama.list_ollama_models
    _record_graph_snapshot_metrics(skills_server)
    # The FastMCP HTTP app defaults to serving at "/mcp". When we mount it under
    # "/mcp" in this API, override the inner path so the external endpoint stays
    # cleanly at "/mcp" rather than "/mcp/mcp".
    mounted_mcp_server = build_fastmcp_server(skills_server)
    mounted_mcp_server.settings.streamable_http_path = "/"

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        # Mounted Starlette sub-app lifespans are not sufficient here; manage the
        # MCP session manager at the FastAPI boundary so the deployed /mcp transport
        # is initialized before requests arrive.
        async with mounted_mcp_server.session_manager.run():
            yield

    app = FastAPI(
        title="Skills KG GraphRAG",
        version="0.1.0",
        description="Read-only Neo4j-backed Skills KG GraphRAG API and MCP transport.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_request_context(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("x-request-id") or f"req_{uuid.uuid4().hex}"
        request.state.request_id = request_id
        start_time = time.perf_counter()
        response = await call_next(request)
        duration_seconds = time.perf_counter() - start_time
        duration_ms = round(duration_seconds * 1000, 2)
        route = _route_path(request)
        status_code = str(response.status_code)
        REQUESTS_TOTAL.labels(
            method=request.method,
            route=route,
            status_code=status_code,
        ).inc()
        REQUEST_DURATION_SECONDS.labels(
            method=request.method,
            route=route,
            status_code=status_code,
        ).observe(duration_seconds)
        response.headers["x-request-id"] = request_id
        _log_api_event(
            "api_request_completed",
            {
                "request_id": request_id,
                "method": request.method,
                "route": route,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response

    @app.get("/health/live")
    def health_live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready")
    def health_ready() -> Mapping[str, object]:
        report = readiness()
        _record_readiness_metrics(report)
        return report

    @app.get("/metrics")
    def metrics() -> Response:
        _record_graph_snapshot_metrics(skills_server)
        _record_readiness_metrics(readiness())
        return Response(generate_latest(METRICS_REGISTRY), media_type=CONTENT_TYPE_LATEST)

    @app.get("/skills/search")
    def search_skills(
        query: str = Query(min_length=1),
        limit: int = Query(default=5, ge=1, le=20),
    ) -> Mapping[str, object]:
        request = skills_contracts.SearchSkillsRequest(query=query, limit=limit)
        return skills_server.call_tool("search_skills", request.model_dump())

    @app.get("/skills/graph")
    def skills_graph() -> Mapping[str, object]:
        return skills_server.graph_summary()

    @app.post("/skills/route")
    def route_skill_query(
        request: skills_contracts.RouteSkillQueryRequest,
    ) -> Mapping[str, object]:
        return skills_server.call_tool("route_skill_query", request.model_dump())

    @app.post("/skills/upload/preview")
    async def upload_skill_preview(
        file: Annotated[UploadFile, File(...)],
    ) -> Mapping[str, object]:
        content = await file.read(MAX_UPLOAD_BYTES + 1)
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="Skill upload preview exceeds 256 KiB.")
        text = content.decode("utf-8", errors="replace")
        frontmatter = _extract_frontmatter(text)
        name = _frontmatter_value(frontmatter, "name")
        description = _frontmatter_value(frontmatter, "description")
        warnings: list[str] = []
        if file.filename != "SKILL.md":
            warnings.append("Expected filename SKILL.md for repository ingestion compatibility.")
        if not name:
            warnings.append("Missing frontmatter name.")
        if not description:
            warnings.append("Missing frontmatter description.")
        if "## When to use" not in text:
            warnings.append("Missing canonical '## When to use' section.")
        return {
            "status": "ok" if name and description else "warning",
            "filename": file.filename,
            "name": name,
            "description": description,
            "line_count": len(text.splitlines()),
            "word_count": len(re.findall(r"\b\w+\b", text)),
            "warnings": warnings,
            "persisted": False,
            "message": "Upload preview only; no graph writes are performed by this endpoint.",
        }

    @app.get("/mcp/technical-info")
    def mcp_technical_info() -> Mapping[str, object]:
        return skills_server.technical_info()

    @app.get("/ollama/models")
    async def ollama_models(
        api_request: Request,
        ollama_endpoint: str = Query(default=skills_ollama.DEFAULT_OLLAMA_ENDPOINT, min_length=1),
    ) -> Mapping[str, object]:
        try:
            return await list_models(ollama_endpoint)
        except skills_ollama.UnsafeOllamaEndpointError as exc:
            raise HTTPException(
                status_code=422,
                detail=_api_error_detail(
                    error_type="unsafe_ollama_endpoint",
                    message=str(exc),
                    operation="ollama.models",
                    request_id=_request_id(api_request),
                    hint="Use a local HTTP Ollama endpoint such as http://127.0.0.1:11434 or http://host.docker.internal:11434.",
                ),
            ) from exc
        except skills_ollama.OllamaQueryError as exc:
            raise HTTPException(
                status_code=502,
                detail=_api_error_detail(
                    error_type="ollama_model_discovery_failed",
                    message=str(exc),
                    operation="ollama.models",
                    request_id=_request_id(api_request),
                    hint="Check that Ollama is running, reachable from the API container, and responding to /api/tags.",
                ),
            ) from exc

    @app.get("/skills/resolve")
    def resolve_skill(
        name: str = Query(min_length=1, max_length=200),
    ) -> Mapping[str, object]:
        request = skills_contracts.ResolveSkillRequest(name=name)
        return skills_server.call_tool("resolve_skill", request.model_dump())

    @app.get("/skills/{skill_id}")
    def get_skill(
        skill_id: str,
        retrieval_unit_limit: int = Query(default=3, ge=1, le=10),
    ) -> Mapping[str, object]:
        request = skills_contracts.GetSkillRequest(
            skill_id=skill_id,
            retrieval_unit_limit=retrieval_unit_limit,
        )
        return skills_server.call_tool("get_skill", request.model_dump())

    @app.get("/skills/{skill_id}/context")
    def get_skill_context(
        skill_id: str,
        limit: int = Query(default=10, ge=1, le=20),
    ) -> Mapping[str, object]:
        request = skills_contracts.SkillContextRequest(skill_id=skill_id, limit=limit)
        return skills_server.call_tool("get_skill_context", request.model_dump())

    @app.get("/skills/{skill_id}/execution-guide")
    def get_skill_execution_guide(
        skill_id: str,
        related_limit: int = Query(default=10, ge=1, le=20),
    ) -> Mapping[str, object]:
        return skills_server.call_tool(
            "get_skill_execution_guide",
            {"skill_id": skill_id, "related_limit": related_limit},
        )

    @app.post("/skills/recommend")
    def recommend_skills(
        api_request: Request,
        request: skills_contracts.RecommendSkillsRequest,
    ) -> Mapping[str, object]:
        result = skills_server.call_tool("recommend_skills", request.model_dump())
        _record_retrieval_result(
            operation="skills.recommend",
            route="recommendation",
            request_id=_request_id(api_request),
            result=result,
        )
        return result

    @app.post("/skills/query")
    async def query_skills(
        api_request: Request,
        request: skills_contracts.QuerySkillsRequest,
    ) -> Mapping[str, object]:
        evidence = _query_evidence_for_route(
            skills_server,
            request,
            request_id=_request_id(api_request),
        )
        _record_query_evidence_selection(_request_id(api_request), evidence)
        try:
            return await answer_query(request, evidence)
        except skills_ollama.UnsafeOllamaEndpointError as exc:
            raise HTTPException(
                status_code=422,
                detail=_api_error_detail(
                    error_type="unsafe_ollama_endpoint",
                    message=str(exc),
                    operation="skills.query",
                    request_id=_request_id(api_request),
                    hint="Use a local HTTP Ollama endpoint. Docker deployments usually need http://host.docker.internal:11434.",
                ),
            ) from exc
        except skills_ollama.OllamaQueryError as exc:
            raise HTTPException(
                status_code=502,
                detail=_api_error_detail(
                    error_type="ollama_query_failed",
                    message=str(exc),
                    operation="skills.query",
                    request_id=_request_id(api_request),
                    hint="Check that Ollama is running, the selected model is installed, and the endpoint is reachable from the API container.",
                ),
            ) from exc

    app.mount("/mcp", mounted_mcp_server.streamable_http_app())
    return app


def _extract_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---\n", 4)
    return text[4:end] if end != -1 else ""


def _frontmatter_value(frontmatter: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", frontmatter, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _query_evidence_for_route(
    skills_server: SkillsMcpServer,
    request: skills_contracts.QuerySkillsRequest,
    request_id: str,
) -> Mapping[str, object]:
    routing = skills_server.call_tool("route_skill_query", {"query": request.query})
    route = routing.get("route")
    skill_id = routing.get("resolved_skill_id")
    if route == "direct_lookup" and isinstance(skill_id, str):
        skill = skills_server.call_tool(
            "get_skill",
            {"skill_id": skill_id, "retrieval_unit_limit": request.limit},
        )
        context = skills_server.call_tool(
            "get_skill_context",
            {"skill_id": skill_id, "limit": request.limit},
        )
        evidence = {
            "status": "ok",
            "route": "direct_lookup",
            "routing": routing,
            "skill": skill,
            "context": context,
        }
        _record_route_decision(request_id, evidence)
        return evidence
    if route == "context" and isinstance(skill_id, str):
        context = skills_server.call_tool(
            "get_skill_context",
            {"skill_id": skill_id, "limit": request.limit},
        )
        evidence = {
            "status": "ok",
            "route": "context",
            "routing": routing,
            "context": context,
        }
        _record_route_decision(request_id, evidence)
        return evidence
    if route == "execution_plan" and isinstance(skill_id, str):
        guide = skills_server.call_tool(
            "get_skill_execution_guide",
            {"skill_id": skill_id, "related_limit": request.limit},
        )
        evidence = {
            "status": "ok",
            "route": "execution_plan",
            "routing": routing,
            "execution_guide": guide,
        }
        _record_route_decision(request_id, evidence)
        return evidence

    recommendation_request = skills_contracts.RecommendSkillsRequest(
        query=request.query,
        limit=request.limit,
        max_depth=request.max_depth,
        token_budget=request.token_budget,
    )
    recommendations = skills_server.call_tool(
        "recommend_skills", recommendation_request.model_dump()
    )
    recommendation_evidence: dict[str, object] = {
        "status": "ok",
        "route": "recommendation",
        "routing": routing,
    }
    for key, value in recommendations.items():
        recommendation_evidence[key] = value
    _record_route_decision(request_id, recommendation_evidence)
    return recommendation_evidence


def _record_graph_snapshot_metrics(skills_server: SkillsMcpServer) -> None:
    counts = skills_server.graph_logical_counts()
    for label, count in counts["nodes"].items():
        GRAPH_NODES.labels(label=label).set(count)
    for relationship_type, count in counts["relationships"].items():
        GRAPH_RELATIONSHIPS.labels(type=relationship_type).set(count)


def _record_readiness_metrics(report: Mapping[str, object]) -> None:
    database = _safe_metric_label(report.get("database"), default="none")
    ready = report.get("ready")
    if isinstance(ready, bool):
        READINESS_STATE.labels(database=database).set(1.0 if ready else 0.0)


def _record_route_decision(request_id: str, evidence: Mapping[str, object]) -> None:
    routing = evidence.get("routing")
    routing_map = routing if isinstance(routing, dict) else {}
    route = _safe_metric_label(evidence.get("route"))
    _log_api_event(
        "skill_query_route_selected",
        {
            "request_id": request_id,
            "route": route,
            "suggested_tool": _safe_log_value(routing_map.get("suggested_tool")),
            "resolved_skill_id": _safe_log_value(routing_map.get("resolved_skill_id")),
            "confidence": _safe_number(routing_map.get("confidence")),
        },
    )
    _record_retrieval_result(
        operation="skills.query.evidence",
        route=route,
        request_id=request_id,
        result=evidence,
    )


def _record_query_evidence_selection(request_id: str, evidence: Mapping[str, object]) -> None:
    route = _safe_metric_label(evidence.get("route"))
    recommendation_count, top = _recommendation_summary(evidence)
    _log_api_event(
        "skill_query_evidence_selected",
        {
            "request_id": request_id,
            "route": route,
            "recommendation_count": recommendation_count,
            "top_skill_id": top["skill_id"],
            "top_skill_name": top["skill_name"],
            "top_score": top["score"],
        },
    )


def _record_retrieval_result(
    *,
    operation: str,
    route: str,
    request_id: str,
    result: Mapping[str, object],
) -> None:
    uncertain_value = bool(result.get("uncertain")) if "uncertain" in result else False
    uncertain = str(uncertain_value).lower()
    recommendation_count, top = _recommendation_summary(result)
    top_score = _safe_number(top.get("score"))
    RETRIEVAL_REQUESTS_TOTAL.labels(
        operation=operation,
        route=_safe_metric_label(route),
        uncertain=uncertain,
    ).inc()
    RETRIEVAL_RECOMMENDATION_COUNT.labels(
        operation=operation,
        route=_safe_metric_label(route),
        uncertain=uncertain,
    ).observe(recommendation_count)
    RETRIEVAL_TOP_SCORE.labels(
        operation=operation,
        route=_safe_metric_label(route),
        uncertain=uncertain,
    ).observe(top_score)
    _log_api_event(
        "skill_retrieval_completed",
        {
            "request_id": request_id,
            "operation": operation,
            "route": _safe_metric_label(route),
            "uncertain": uncertain_value,
            "recommendation_count": recommendation_count,
            "top_skill_id": top["skill_id"],
            "top_skill_name": top["skill_name"],
            "top_score": top_score,
        },
    )


def _recommendation_summary(result: Mapping[str, object]) -> tuple[int, dict[str, object]]:
    recommendations = result.get("recommendations")
    if not isinstance(recommendations, list):
        return 0, {"skill_id": "", "skill_name": "", "score": 0.0}
    first = recommendations[0] if recommendations and isinstance(recommendations[0], dict) else {}
    return len(recommendations), {
        "skill_id": _safe_log_value(first.get("skill_id")),
        "skill_name": _safe_log_value(first.get("skill_name")),
        "score": _safe_number(first.get("score")),
    }


def _safe_metric_label(value: object, *, default: str = "unknown") -> str:
    if isinstance(value, str) and value:
        return re.sub(r"[^a-zA-Z0-9_.:-]+", "_", value)[:80]
    return default


def _safe_log_value(value: object) -> str:
    return value if isinstance(value, str) else ""


def _safe_number(value: object) -> float:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return 0.0


def _request_id(request: Request) -> str:
    value = getattr(request.state, "request_id", "")
    return value if isinstance(value, str) and value else "req_unknown"


def _route_path(request: Request) -> str:
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    return path if isinstance(path, str) else request.url.path


def _api_error_detail(
    *,
    error_type: str,
    message: str,
    operation: str,
    request_id: str,
    hint: str,
) -> dict[str, str]:
    OLLAMA_FAILURES_TOTAL.labels(operation=operation, error_type=error_type).inc()
    _log_api_event(
        "api_request_failed",
        {
            "request_id": request_id,
            "operation": operation,
            "error_type": error_type,
        },
    )
    return {
        "error_type": error_type,
        "message": message,
        "operation": operation,
        "request_id": request_id,
        "hint": hint,
    }


def _log_api_event(event: str, fields: Mapping[str, object]) -> None:
    logging.getLogger(API_LOGGER_NAME).info(json.dumps({"event": event, **fields}, sort_keys=True))
