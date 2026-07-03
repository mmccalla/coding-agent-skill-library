#!/usr/bin/env python3
"""Prometheus counters for Skills KG trust and promotion ingest gates."""

from __future__ import annotations

import re

from prometheus_client import CollectorRegistry, Counter

METRICS_REGISTRY = CollectorRegistry()

SKILLS_TRUST_REJECTED_TOTAL = Counter(
    "skills_trust_rejected_total",
    "Total skill files rejected by pre-ingest trust gates.",
    ("layer", "reason"),
    registry=METRICS_REGISTRY,
)
SKILLS_QUARANTINED_TOTAL = Counter(
    "skills_quarantined_total",
    "Total skills quarantined at ingest due to incomplete semantic mapping.",
    ("reason",),
    registry=METRICS_REGISTRY,
)
SKILLS_ADMIN_INGEST_TOTAL = Counter(
    "skills_admin_ingest_total",
    "Total admin skill ingest attempts by outcome.",
    ("outcome",),
    registry=METRICS_REGISTRY,
)


def record_trust_rejection(*, layer: str, reason: str, count: int = 1) -> None:
    """Record a trust-gate rejection for CI or operator metrics."""

    if count <= 0:
        return
    SKILLS_TRUST_REJECTED_TOTAL.labels(
        layer=_safe_metric_label(layer),
        reason=_safe_metric_label(reason),
    ).inc(count)


def record_promotion_quarantine(*, reason: str, count: int = 1) -> None:
    """Record quarantined skills discovered during extract/ingest."""

    if count <= 0:
        return
    SKILLS_QUARANTINED_TOTAL.labels(reason=_safe_metric_label(reason)).inc(count)


def record_admin_ingest(*, outcome: str, count: int = 1) -> None:
    """Record an admin ingest attempt outcome."""

    if count <= 0:
        return
    SKILLS_ADMIN_INGEST_TOTAL.labels(outcome=_safe_metric_label(outcome)).inc(count)


def _safe_metric_label(value: object, *, default: str = "unknown") -> str:
    if isinstance(value, str) and value:
        return re.sub(r"[^a-zA-Z0-9_.:-]+", "_", value)[:80]
    return default
