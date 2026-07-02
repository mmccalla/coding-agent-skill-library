#!/usr/bin/env python3
"""Shared usage instrumentation for Skills KG API and MCP paths."""

from __future__ import annotations

import json
import logging
import re
import uuid
from collections.abc import Mapping

from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Counter, generate_latest

METRICS_REGISTRY = CollectorRegistry()
USAGE_LOGGER_NAME = "skills_usage"

SKILLS_USAGE_HITS_TOTAL = Counter(
    "skills_usage_hits_total",
    "Total material skill appearances by skill id and MCP tool.",
    ("skill_id", "tool"),
    registry=METRICS_REGISTRY,
)
SKILLS_USAGE_RECOMMEND_RANK_TOTAL = Counter(
    "skills_usage_recommend_rank_total",
    "Recommendation rank distribution by skill id and rank bucket.",
    ("skill_id", "rank_bucket"),
    registry=METRICS_REGISTRY,
)
SKILLS_USAGE_EXECUTION_GUIDE_TOTAL = Counter(
    "skills_usage_execution_guide_total",
    "Total execution-guide loads by skill id and MCP tool.",
    ("skill_id", "tool"),
    registry=METRICS_REGISTRY,
)
SKILLS_USAGE_ABSTENTION_TOTAL = Counter(
    "skills_usage_abstention_total",
    "Total low-confidence or out-of-domain abstentions by tool and reason.",
    ("tool", "reason"),
    registry=METRICS_REGISTRY,
)

_QUERY_KEYS = frozenset({"query", "raw_query", "user_query"})
logging.getLogger(USAGE_LOGGER_NAME).setLevel(logging.INFO)


def new_selection_run_id() -> str:
    """Return a bounded selection-run identifier for trace correlation."""

    return f"sel_{uuid.uuid4().hex[:12]}"


def rank_bucket(rank: int) -> str:
    """Map a 1-based recommendation rank to a bounded Prometheus label."""

    if rank <= 1:
        return "1"
    if rank == 2:
        return "2"
    if rank == 3:
        return "3"
    if rank <= 5:
        return "4-5"
    return "6+"


def record_skill_hit(skill_id: str, tool_name: str, rank: int | None = None) -> None:
    """Record a skill appearance for usage metrics."""

    safe_skill_id = _safe_metric_label(skill_id)
    safe_tool = _safe_metric_label(tool_name)
    SKILLS_USAGE_HITS_TOTAL.labels(skill_id=safe_skill_id, tool=safe_tool).inc()
    if rank is not None:
        SKILLS_USAGE_RECOMMEND_RANK_TOTAL.labels(
            skill_id=safe_skill_id,
            rank_bucket=rank_bucket(rank),
        ).inc()


def record_execution_guide(skill_id: str, tool_name: str) -> None:
    """Record that an agent loaded an execution guide before acting."""

    SKILLS_USAGE_EXECUTION_GUIDE_TOTAL.labels(
        skill_id=_safe_metric_label(skill_id),
        tool=_safe_metric_label(tool_name),
    ).inc()


def record_abstention(tool_name: str, reason: str) -> None:
    """Record a low-confidence or out-of-domain abstention."""

    SKILLS_USAGE_ABSTENTION_TOTAL.labels(
        tool=_safe_metric_label(tool_name),
        reason=_safe_metric_label(reason),
    ).inc()


def sanitize_selection_log(log: Mapping[str, object]) -> dict[str, object]:
    """Remove raw user query fields before structured logging."""

    def _walk(value: object) -> object:
        if isinstance(value, dict):
            cleaned: dict[str, object] = {}
            for key, nested in value.items():
                if key in _QUERY_KEYS:
                    continue
                if key == "request" and isinstance(nested, dict):
                    request_payload = {
                        item_key: item_value
                        for item_key, item_value in nested.items()
                        if item_key not in _QUERY_KEYS
                    }
                    if request_payload:
                        cleaned[key] = _walk(request_payload)
                    continue
                cleaned[key] = _walk(nested)
            return cleaned
        if isinstance(value, list):
            return [_walk(item) for item in value]
        if isinstance(value, tuple):
            return [_walk(item) for item in value]
        return value

    walked = _walk(dict(log))
    return walked if isinstance(walked, dict) else {}


def emit_skill_selection_run(log: Mapping[str, object]) -> str:
    """Emit a structured JSON log line for a skill selection run."""

    payload = {"event": "skill_selection_run", **sanitize_selection_log(log)}
    line = json.dumps(payload, sort_keys=True)
    logging.getLogger(USAGE_LOGGER_NAME).info(line)
    return line


def attach_usage_metadata(
    result: dict[str, object],
    selection_run_id: str,
    **fields: object,
) -> dict[str, object]:
    """Attach bounded usage metadata to a successful MCP tool response."""

    if result.get("status") != "ok":
        return result
    usage: dict[str, object] = {"selection_run_id": selection_run_id}
    for key, value in fields.items():
        if value is not None:
            usage[key] = value
    return {**result, "usage": usage}


def usage_metrics_text() -> str:
    """Return Prometheus exposition text for usage counters."""

    return generate_latest(METRICS_REGISTRY).decode("utf-8")


def usage_metrics_content_type() -> str:
    """Return the Prometheus exposition content type."""

    return CONTENT_TYPE_LATEST


def _safe_metric_label(value: object, *, default: str = "unknown") -> str:
    if isinstance(value, str) and value:
        return re.sub(r"[^a-zA-Z0-9_.:-]+", "_", value)[:80]
    return default
