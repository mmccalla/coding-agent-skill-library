#!/usr/bin/env python3
"""Typed request contracts shared by the Skills API and MCP adapters."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class RecommendSkillsRequest(BaseModel):
    """Validated request for skill recommendation."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)
    limit: PositiveInt = Field(default=5, le=10)
    max_depth: int = Field(default=2, ge=0, le=3)
    token_budget: PositiveInt = Field(default=600, ge=50, le=2000)


class QuerySkillsRequest(BaseModel):
    """Validated request for an Ollama-grounded graph query."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1, max_length=1000)
    ollama_endpoint: str = Field(default="http://127.0.0.1:11434", min_length=1, max_length=200)
    model: str | None = Field(default=None, min_length=1, max_length=120)
    limit: PositiveInt = Field(default=5, le=5)
    max_depth: int = Field(default=2, ge=0, le=3)
    token_budget: PositiveInt = Field(default=700, ge=100, le=2000)


class SearchSkillsRequest(BaseModel):
    """Validated request for skill search."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)
    limit: PositiveInt = Field(default=5, le=20)


class RouteSkillQueryRequest(BaseModel):
    """Validated request for agent-facing skill query routing."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1, max_length=1000)


class ResolveSkillRequest(BaseModel):
    """Validated request for resolving a skill name to a canonical id."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=200)


class SkillContextRequest(BaseModel):
    """Validated request for connected skill context."""

    model_config = ConfigDict(extra="forbid")

    skill_id: str = Field(min_length=1)
    limit: PositiveInt = Field(default=10, le=20)


class GetSkillRequest(BaseModel):
    """Validated request for one skill."""

    model_config = ConfigDict(extra="forbid")

    skill_id: str = Field(min_length=1)
    chunk_limit: PositiveInt = Field(default=3, le=10)
