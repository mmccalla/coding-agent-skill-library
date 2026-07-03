#!/usr/bin/env python3
"""Combine Skills KG API, usage and trust Prometheus registries."""

from __future__ import annotations

from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, generate_latest

from scripts import skills_trust_metrics, skills_usage


def render_all_metrics(*, api_registry: CollectorRegistry | None = None) -> bytes:
    """Return Prometheus exposition text for API, usage and trust counters."""

    parts: list[bytes] = []
    if api_registry is not None:
        parts.append(generate_latest(api_registry))
    parts.append(generate_latest(skills_usage.METRICS_REGISTRY))
    parts.append(generate_latest(skills_trust_metrics.METRICS_REGISTRY))
    return b"".join(parts)


def metrics_content_type() -> str:
    """Return the Prometheus exposition content type."""

    return CONTENT_TYPE_LATEST


def metrics_text(*, api_registry: CollectorRegistry | None = None) -> str:
    """Return combined metrics as UTF-8 text."""

    return render_all_metrics(api_registry=api_registry).decode("utf-8")
