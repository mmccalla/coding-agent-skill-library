#!/usr/bin/env python3
"""Typed configuration for the Skills KG, retrieval, API and MCP layers."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, PositiveInt

DEFAULT_CONFIG_PATH = Path("configs") / "skills_kg.yaml"


class Neo4jSettings(BaseModel):
    """Neo4j connection and index settings.

    Passwords are intentionally excluded from repr/model dumps to avoid accidental log leakage.
    """

    model_config = ConfigDict(frozen=True)

    uri: str = ""
    user: str = ""
    password: str = Field(default="", repr=False, exclude=True)
    database: str = "neo4j"
    embedding_dimensions: PositiveInt = 1536
    embedding_provider: str = "deterministic-test-embedding"
    vector_similarity_function: str = "cosine"
    vector_index: str = "skill_chunk_embedding_vector"
    metadata_fulltext_index: str = "skill_metadata_fulltext"
    chunk_fulltext_index: str = "skill_chunk_text_fulltext"


class RetrievalSettings(BaseModel):
    """Shared retrieval scoring and response bounds."""

    model_config = ConfigDict(frozen=True)

    min_confident_score: float = Field(default=0.2, ge=0.0, le=1.0)
    min_vector_candidate_score: float = Field(default=0.2, ge=0.0, le=1.0)
    default_token_budget: PositiveInt = 1200
    default_limit: PositiveInt = 5
    max_limit: PositiveInt = 20
    max_depth: int = Field(default=3, ge=0, le=5)


class McpSettings(BaseModel):
    """Shared MCP tool limits."""

    model_config = ConfigDict(frozen=True)

    search_limit_max: PositiveInt = 20
    recommend_limit_max: PositiveInt = 10
    context_limit_max: PositiveInt = 20
    chunk_limit_max: PositiveInt = 10
    token_budget_min: PositiveInt = 50
    token_budget_max: PositiveInt = 2000


class ApiSettings(BaseModel):
    """HTTP API defaults and safety bounds."""

    model_config = ConfigDict(frozen=True)

    service_name: str = "skills-kg"
    request_timeout_seconds: PositiveInt = 10


class SkillsKgSettings(BaseModel):
    """Root settings object for the production Skills KG service."""

    model_config = ConfigDict(frozen=True)

    neo4j: Neo4jSettings = Field(default_factory=Neo4jSettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
    mcp: McpSettings = Field(default_factory=McpSettings)
    api: ApiSettings = Field(default_factory=ApiSettings)


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _nested_mapping(data: Mapping[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    return dict(value) if isinstance(value, dict) else {}


def load_settings(
    config_path: Path = DEFAULT_CONFIG_PATH,
    environ: Mapping[str, str] | None = None,
) -> SkillsKgSettings:
    """Load typed settings from YAML plus safe environment overrides."""

    env = os.environ if environ is None else environ
    raw = _read_yaml(config_path)
    neo4j_config = _nested_mapping(raw, "neo4j")
    retrieval_config = _nested_mapping(raw, "retrieval")
    mcp_config = _nested_mapping(raw, "mcp")
    api_config = _nested_mapping(raw, "api")

    env_overrides = {
        "uri": env.get("NEO4J_URI", ""),
        "user": env.get("NEO4J_USER", ""),
        "password": env.get("NEO4J_PASSWORD", ""),
        "database": env.get("NEO4J_DATABASE", "neo4j"),
    }
    neo4j_config.update({key: value for key, value in env_overrides.items() if value})

    return SkillsKgSettings(
        neo4j=Neo4jSettings(**neo4j_config),
        retrieval=RetrievalSettings(**retrieval_config),
        mcp=McpSettings(**mcp_config),
        api=ApiSettings(**api_config),
    )
