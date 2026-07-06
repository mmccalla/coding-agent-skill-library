#!/usr/bin/env python3
"""Performance instrumentation for Skills MCP tool calls.

Records total duration plus a breakdown of payload construction, database I/O,
disk I/O, and request/response payload sizes. Metrics are process-local
Prometheus counters/histograms and are attached to each tool response under a
``timing`` key.
"""

from __future__ import annotations

import json
import logging
import re
import time
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Any

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
)

METRICS_REGISTRY = CollectorRegistry()
PERF_LOGGER_NAME = "skills_mcp_perf"

_DURATION_BUCKETS = (
    0.001,
    0.005,
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
)
_BYTE_BUCKETS = (
    0.0,
    100.0,
    500.0,
    1_000.0,
    2_500.0,
    5_000.0,
    10_000.0,
    25_000.0,
    50_000.0,
    100_000.0,
    250_000.0,
    1_000_000.0,
)

SKILLS_MCP_TOOL_CALLS_TOTAL = Counter(
    "skills_mcp_tool_calls_total",
    "Total Skills MCP tool invocations by tool name and status.",
    ("tool", "status"),
    registry=METRICS_REGISTRY,
)
SKILLS_MCP_TOOL_DURATION_SECONDS = Histogram(
    "skills_mcp_tool_duration_seconds",
    "Skills MCP tool total duration in seconds by tool name and status.",
    ("tool", "status"),
    buckets=_DURATION_BUCKETS,
    registry=METRICS_REGISTRY,
)
SKILLS_MCP_TOOL_HANDLER_SECONDS = Histogram(
    "skills_mcp_tool_handler_seconds",
    "Skills MCP tool non-I/O handler duration in seconds by tool name and status.",
    ("tool", "status"),
    buckets=_DURATION_BUCKETS,
    registry=METRICS_REGISTRY,
)
SKILLS_MCP_TOOL_PAYLOAD_CONSTRUCTION_SECONDS = Histogram(
    "skills_mcp_tool_payload_construction_seconds",
    "Skills MCP tool payload construction duration in seconds by tool name and status.",
    ("tool", "status"),
    buckets=_DURATION_BUCKETS,
    registry=METRICS_REGISTRY,
)
SKILLS_MCP_TOOL_DATABASE_IO_SECONDS = Histogram(
    "skills_mcp_tool_database_io_seconds",
    "Skills MCP tool database I/O duration in seconds by tool name and status.",
    ("tool", "status"),
    buckets=_DURATION_BUCKETS,
    registry=METRICS_REGISTRY,
)
SKILLS_MCP_TOOL_DISK_IO_SECONDS = Histogram(
    "skills_mcp_tool_disk_io_seconds",
    "Skills MCP tool disk I/O duration in seconds by tool name and status.",
    ("tool", "status"),
    buckets=_DURATION_BUCKETS,
    registry=METRICS_REGISTRY,
)
SKILLS_MCP_TOOL_REQUEST_BYTES = Histogram(
    "skills_mcp_tool_request_bytes",
    "Skills MCP tool request argument payload size in bytes by tool name and status.",
    ("tool", "status"),
    buckets=_BYTE_BUCKETS,
    registry=METRICS_REGISTRY,
)
SKILLS_MCP_TOOL_RESPONSE_BYTES = Histogram(
    "skills_mcp_tool_response_bytes",
    "Skills MCP tool response payload size in bytes by tool name and status.",
    ("tool", "status"),
    buckets=_BYTE_BUCKETS,
    registry=METRICS_REGISTRY,
)
SKILLS_MCP_TOOL_DATABASE_BYTES_READ = Histogram(
    "skills_mcp_tool_database_bytes_read",
    "Approximate database bytes read during a Skills MCP tool call.",
    ("tool", "status"),
    buckets=_BYTE_BUCKETS,
    registry=METRICS_REGISTRY,
)
SKILLS_MCP_TOOL_DISK_BYTES_READ = Histogram(
    "skills_mcp_tool_disk_bytes_read",
    "Approximate disk bytes read during a Skills MCP tool call.",
    ("tool", "status"),
    buckets=_BYTE_BUCKETS,
    registry=METRICS_REGISTRY,
)

logging.getLogger(PERF_LOGGER_NAME).setLevel(logging.INFO)

_ACTIVE_SPAN: ContextVar[ToolPerfSpan | None] = ContextVar("skills_mcp_perf_span", default=None)


@dataclass
class ByteAccumulator:
    """Mutable byte counter for I/O context managers."""

    bytes_read: int = 0

    def add(self, nbytes: int) -> None:
        self.bytes_read += max(0, int(nbytes))

    def add_payload(self, payload: object) -> None:
        self.add(payload_byte_size(payload))


@dataclass
class ToolPerfSpan:
    """Accumulates phase timings and sizes for one MCP tool invocation."""

    tool: str
    request_bytes: int = 0
    payload_construction_seconds: float = 0.0
    database_io_seconds: float = 0.0
    disk_io_seconds: float = 0.0
    database_bytes_read: int = 0
    disk_bytes_read: int = 0
    _started: float = field(default_factory=time.perf_counter)
    _token: Token[ToolPerfSpan | None] | None = field(default=None, repr=False)

    def add_payload_construction(self, duration_seconds: float) -> None:
        self.payload_construction_seconds += max(0.0, float(duration_seconds))

    def add_database_io(self, duration_seconds: float, bytes_read: int = 0) -> None:
        self.database_io_seconds += max(0.0, float(duration_seconds))
        self.database_bytes_read += max(0, int(bytes_read))

    def add_disk_io(self, duration_seconds: float, bytes_read: int = 0) -> None:
        self.disk_io_seconds += max(0.0, float(duration_seconds))
        self.disk_bytes_read += max(0, int(bytes_read))

    def finish(self, result: dict[str, object]) -> dict[str, object]:
        """Measure response size, record metrics, and attach timing metadata."""

        with payload_construction():
            response_bytes = payload_byte_size(result)
        duration_seconds = max(0.0, time.perf_counter() - self._started)
        status = result.get("status")
        status_label = status if isinstance(status, str) and status else "unknown"
        timing = build_timing_metadata(
            duration_seconds=duration_seconds,
            payload_construction_seconds=self.payload_construction_seconds,
            database_io_seconds=self.database_io_seconds,
            disk_io_seconds=self.disk_io_seconds,
            request_bytes=self.request_bytes,
            response_bytes=response_bytes,
            database_bytes_read=self.database_bytes_read,
            disk_bytes_read=self.disk_bytes_read,
        )
        record_tool_timing(tool=self.tool, status=status_label, timing=timing)
        return {**result, "timing": timing}


def payload_byte_size(payload: object) -> int:
    """Return a stable UTF-8 byte size for a JSON-serialisable payload."""

    return len(json.dumps(payload, sort_keys=True, default=str).encode("utf-8"))


def response_byte_size(payload: Mapping[str, object]) -> int:
    """Return a stable UTF-8 byte size for a tool response payload."""

    return payload_byte_size(payload)


def current_span() -> ToolPerfSpan | None:
    """Return the active tool performance span, if any."""

    return _ACTIVE_SPAN.get()


@contextmanager
def tool_span(tool: str, arguments: Mapping[str, object] | None = None) -> Iterator[ToolPerfSpan]:
    """Start a tool performance span for the current context."""

    span = ToolPerfSpan(
        tool=tool,
        request_bytes=payload_byte_size(dict(arguments or {})),
    )
    span._token = _ACTIVE_SPAN.set(span)
    try:
        yield span
    finally:
        if span._token is not None:
            _ACTIVE_SPAN.reset(span._token)
            span._token = None


@contextmanager
def payload_construction() -> Iterator[None]:
    """Attribute elapsed time to payload construction when a span is active."""

    span = current_span()
    started = time.perf_counter()
    try:
        yield
    finally:
        if span is not None:
            span.add_payload_construction(time.perf_counter() - started)


@contextmanager
def database_io() -> Iterator[ByteAccumulator]:
    """Attribute elapsed time and bytes to database I/O when a span is active."""

    accumulator = ByteAccumulator()
    span = current_span()
    started = time.perf_counter()
    try:
        yield accumulator
    finally:
        if span is not None:
            span.add_database_io(time.perf_counter() - started, accumulator.bytes_read)


@contextmanager
def disk_io() -> Iterator[ByteAccumulator]:
    """Attribute elapsed time and bytes to disk I/O when a span is active."""

    accumulator = ByteAccumulator()
    span = current_span()
    started = time.perf_counter()
    try:
        yield accumulator
    finally:
        if span is not None:
            span.add_disk_io(time.perf_counter() - started, accumulator.bytes_read)


def build_timing_metadata(
    *,
    duration_seconds: float,
    payload_construction_seconds: float,
    database_io_seconds: float,
    disk_io_seconds: float,
    request_bytes: int,
    response_bytes: int,
    database_bytes_read: int,
    disk_bytes_read: int,
) -> dict[str, object]:
    """Build the bounded timing object attached to tool responses."""

    duration = max(0.0, float(duration_seconds))
    payload_construction = max(0.0, float(payload_construction_seconds))
    database_io = max(0.0, float(database_io_seconds))
    disk_io = max(0.0, float(disk_io_seconds))
    accounted = payload_construction + database_io + disk_io
    handler = max(0.0, duration - accounted)
    return {
        "duration_ms": _ms(duration),
        "handler_ms": _ms(handler),
        "payload_construction_ms": _ms(payload_construction),
        "database_io_ms": _ms(database_io),
        "disk_io_ms": _ms(disk_io),
        "request_bytes": max(0, int(request_bytes)),
        "response_bytes": max(0, int(response_bytes)),
        "database_bytes_read": max(0, int(database_bytes_read)),
        "disk_bytes_read": max(0, int(disk_bytes_read)),
    }


def record_tool_timing(
    *,
    tool: str,
    status: str,
    timing: Mapping[str, object],
    response_bytes: int | None = None,
    duration_seconds: float | None = None,
) -> None:
    """Record Prometheus metrics and a structured log line for one tool call."""

    safe_tool = _safe_metric_label(tool)
    safe_status = _safe_metric_label(status, default="unknown")
    if duration_seconds is None:
        duration_seconds = _timing_float(timing, "duration_ms") / 1000.0
    if response_bytes is None:
        response_bytes = _timing_int(timing, "response_bytes")

    handler_seconds = _timing_float(timing, "handler_ms") / 1000.0
    payload_construction_seconds = _timing_float(timing, "payload_construction_ms") / 1000.0
    database_io_seconds = _timing_float(timing, "database_io_ms") / 1000.0
    disk_io_seconds = _timing_float(timing, "disk_io_ms") / 1000.0
    request_bytes = _timing_int(timing, "request_bytes")
    database_bytes_read = _timing_int(timing, "database_bytes_read")
    disk_bytes_read = _timing_int(timing, "disk_bytes_read")

    SKILLS_MCP_TOOL_CALLS_TOTAL.labels(tool=safe_tool, status=safe_status).inc()
    SKILLS_MCP_TOOL_DURATION_SECONDS.labels(tool=safe_tool, status=safe_status).observe(
        max(0.0, float(duration_seconds))
    )
    SKILLS_MCP_TOOL_HANDLER_SECONDS.labels(tool=safe_tool, status=safe_status).observe(
        max(0.0, handler_seconds)
    )
    SKILLS_MCP_TOOL_PAYLOAD_CONSTRUCTION_SECONDS.labels(tool=safe_tool, status=safe_status).observe(
        max(0.0, payload_construction_seconds)
    )
    SKILLS_MCP_TOOL_DATABASE_IO_SECONDS.labels(tool=safe_tool, status=safe_status).observe(
        max(0.0, database_io_seconds)
    )
    SKILLS_MCP_TOOL_DISK_IO_SECONDS.labels(tool=safe_tool, status=safe_status).observe(
        max(0.0, disk_io_seconds)
    )
    SKILLS_MCP_TOOL_REQUEST_BYTES.labels(tool=safe_tool, status=safe_status).observe(
        float(max(0, request_bytes))
    )
    SKILLS_MCP_TOOL_RESPONSE_BYTES.labels(tool=safe_tool, status=safe_status).observe(
        float(max(0, int(response_bytes)))
    )
    SKILLS_MCP_TOOL_DATABASE_BYTES_READ.labels(tool=safe_tool, status=safe_status).observe(
        float(max(0, database_bytes_read))
    )
    SKILLS_MCP_TOOL_DISK_BYTES_READ.labels(tool=safe_tool, status=safe_status).observe(
        float(max(0, disk_bytes_read))
    )

    payload = {
        "event": "mcp_tool_completed",
        "tool": safe_tool,
        "status": safe_status,
        **dict(timing),
    }
    logging.getLogger(PERF_LOGGER_NAME).info(json.dumps(payload, sort_keys=True))


def attach_timing_metadata(
    result: dict[str, object],
    *,
    timing: Mapping[str, object] | None = None,
    duration_seconds: float | None = None,
    response_bytes: int | None = None,
) -> dict[str, object]:
    """Attach bounded timing metadata without mutating the original result."""

    if timing is None:
        timing = build_timing_metadata(
            duration_seconds=duration_seconds or 0.0,
            payload_construction_seconds=0.0,
            database_io_seconds=0.0,
            disk_io_seconds=0.0,
            request_bytes=0,
            response_bytes=response_bytes or 0,
            database_bytes_read=0,
            disk_bytes_read=0,
        )
    return {**result, "timing": dict(timing)}


def instrument_tool_result(
    *,
    tool: str,
    result: dict[str, object],
    duration_seconds: float,
    arguments: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Record metrics for a completed tool call outside an active span."""

    request_bytes = payload_byte_size(dict(arguments or {}))
    serialization_started = time.perf_counter()
    response_bytes = payload_byte_size(result)
    payload_construction_seconds = time.perf_counter() - serialization_started
    status = result.get("status")
    status_label = status if isinstance(status, str) and status else "unknown"
    timing = build_timing_metadata(
        duration_seconds=duration_seconds,
        payload_construction_seconds=payload_construction_seconds,
        database_io_seconds=0.0,
        disk_io_seconds=0.0,
        request_bytes=request_bytes,
        response_bytes=response_bytes,
        database_bytes_read=0,
        disk_bytes_read=0,
    )
    record_tool_timing(tool=tool, status=status_label, timing=timing)
    return {**result, "timing": timing}


def metrics_text() -> str:
    """Return Prometheus exposition text for MCP tool performance metrics."""

    return generate_latest(METRICS_REGISTRY).decode("utf-8")


def metrics_content_type() -> str:
    """Return the Prometheus exposition content type."""

    return CONTENT_TYPE_LATEST


_SUMMARY_FIELDS = (
    "duration_ms",
    "handler_ms",
    "payload_construction_ms",
    "database_io_ms",
    "disk_io_ms",
    "request_bytes",
    "response_bytes",
    "database_bytes_read",
    "disk_bytes_read",
)


def summarise_timings(samples: Sequence[Mapping[str, Any]]) -> dict[str, object]:
    """Return min/mean/p50/p95/max for each timing and size field in samples."""

    if not samples:
        return {"count": 0, **{field: {} for field in _SUMMARY_FIELDS}}

    summary: dict[str, object] = {"count": len(samples)}
    for field_name in _SUMMARY_FIELDS:
        values = sorted(float(sample.get(field_name, 0.0)) for sample in samples)
        if field_name.endswith("_bytes") or field_name.endswith("_bytes_read"):
            int_values = [int(value) for value in values]
            summary[field_name] = {
                "min": min(int_values),
                "mean": round(sum(int_values) / len(int_values), 1),
                "p50": int(round(_percentile(values, 50))),
                "p95": int(round(_percentile(values, 95))),
                "max": max(int_values),
            }
        else:
            summary[field_name] = {
                "min": values[0],
                "mean": round(sum(values) / len(values), 3),
                "p50": _percentile(values, 50),
                "p95": _percentile(values, 95),
                "max": values[-1],
            }
    return summary


def _timing_float(timing: Mapping[str, object], key: str) -> float:
    value = timing.get(key, 0.0)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0
    return float(value)


def _timing_int(timing: Mapping[str, object], key: str) -> int:
    value = timing.get(key, 0)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0
    return int(value)


def _ms(seconds: float) -> float:
    return round(max(0.0, seconds) * 1000.0, 3)


def _percentile(sorted_values: list[float], percentile: int) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = (percentile / 100.0) * (len(sorted_values) - 1)
    lower = int(rank)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = rank - lower
    return round(sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight, 3)


def _safe_metric_label(value: object, *, default: str = "unknown") -> str:
    if isinstance(value, str) and value:
        return re.sub(r"[^a-zA-Z0-9_.:-]+", "_", value)[:80]
    return default
