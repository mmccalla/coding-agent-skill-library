#!/usr/bin/env python3
"""FastAPI app for the read-only Skills KG GraphRAG capability."""

from __future__ import annotations

import os
import re
import sys
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import check_neo4j_readiness, load_skills_neo4j, skills_config, skills_contracts
from scripts.skills_mcp_server import SkillsMcpServer, build_fastmcp_server

ReadinessProvider = Callable[[], Mapping[str, object]]
MAX_UPLOAD_BYTES = 256 * 1024


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
) -> FastAPI:
    """Create the FastAPI app with a narrow read-only Skills service boundary."""

    skills_server = server or _default_server()
    readiness = readiness_provider or _default_readiness
    app = FastAPI(
        title="Skills KG GraphRAG",
        version="0.1.0",
        description="Read-only Neo4j-backed Skills KG GraphRAG API and MCP transport.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.get("/health/live")
    def health_live() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready")
    def health_ready() -> Mapping[str, object]:
        return readiness()

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

    @app.get("/skills/{skill_id}")
    def get_skill(
        skill_id: str,
        chunk_limit: int = Query(default=3, ge=1, le=10),
    ) -> Mapping[str, object]:
        request = skills_contracts.GetSkillRequest(skill_id=skill_id, chunk_limit=chunk_limit)
        return skills_server.call_tool("get_skill", request.model_dump())

    @app.get("/skills/{skill_id}/context")
    def get_skill_context(
        skill_id: str,
        limit: int = Query(default=10, ge=1, le=20),
    ) -> Mapping[str, object]:
        request = skills_contracts.SkillContextRequest(skill_id=skill_id, limit=limit)
        return skills_server.call_tool("get_skill_context", request.model_dump())

    @app.post("/skills/recommend")
    def recommend_skills(
        request: skills_contracts.RecommendSkillsRequest,
    ) -> Mapping[str, object]:
        return skills_server.call_tool("recommend_skills", request.model_dump())

    app.mount("/mcp", build_fastmcp_server(skills_server).streamable_http_app())
    return app


def _extract_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return ""
    end = text.find("\n---\n", 4)
    return text[4:end] if end != -1 else ""


def _frontmatter_value(frontmatter: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", frontmatter, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""
