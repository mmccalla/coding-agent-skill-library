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


class SearchSkillsRequest(BaseModel):
    """Validated request for skill search."""

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)
    limit: PositiveInt = Field(default=5, le=20)


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
