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
    # Production default: BGE-M3 via Ollama. CI overrides with SKILLS_EMBEDDING_PROVIDER=deterministic.
    embedding_dimensions: PositiveInt = 1024
    embedding_provider: str = "ollama-bge-m3"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "bge-m3:567m"
    vector_similarity_function: str = "cosine"
    vector_index: str = "retrieval_unit_embedding_vector"
    metadata_fulltext_index: str = "skill_metadata_fulltext"
    retrieval_unit_fulltext_index: str = "retrieval_unit_text_fulltext"


class RetrievalSettings(BaseModel):
    """Shared retrieval scoring and response bounds."""

    model_config = ConfigDict(frozen=True)

    # Calibrated with bge-m3:567m on abstention_probes + semantic-challenge OOD.
    # OOD-safe promote with MV70 weights: margin 0.01 preserves ood_empty=1.0.
    min_confident_score: float = Field(default=0.35, ge=0.0, le=1.0)
    min_top1_margin: float = Field(
        default=0.01,
        ge=0.0,
        le=1.0,
        description="Abstain when top-1 and top-2 hybrid scores differ by less than this margin.",
    )
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
    retrieval_unit_limit_max: PositiveInt = 10
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

    env_overrides: dict[str, object] = {
        "uri": env.get("NEO4J_URI", ""),
        "user": env.get("NEO4J_USER", ""),
        "password": env.get("NEO4J_PASSWORD", ""),
        "database": env.get("NEO4J_DATABASE", "neo4j"),
        "embedding_provider": env.get("SKILLS_EMBEDDING_PROVIDER", ""),
        "ollama_base_url": env.get("SKILLS_OLLAMA_BASE_URL", ""),
        "ollama_model": env.get("SKILLS_OLLAMA_MODEL", ""),
    }
    if env.get("SKILLS_EMBEDDING_DIMENSIONS"):
        env_overrides["embedding_dimensions"] = int(env["SKILLS_EMBEDDING_DIMENSIONS"])
    neo4j_config.update({key: value for key, value in env_overrides.items() if value})

    return SkillsKgSettings(
        neo4j=Neo4jSettings(**neo4j_config),
        retrieval=RetrievalSettings(**retrieval_config),
        mcp=McpSettings(**mcp_config),
        api=ApiSettings(**api_config),
    )
