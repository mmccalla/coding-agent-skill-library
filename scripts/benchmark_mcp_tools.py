#!/usr/bin/env python3
"""Baseline latency, phase, and payload-size report for Skills MCP tools.

Runs representative tool calls against the in-process MCP facade (no transport
overhead) so handler cost, payload construction, database/disk I/O and payload
sizes can be measured before optimisation.
"""

from __future__ import annotations

import json
import sys
import time
from argparse import ArgumentParser
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import skills_mcp_perf
from scripts.skills_mcp_server import SkillsMcpServer

DEFAULT_CASES: tuple[tuple[str, dict[str, object]], ...] = (
    ("search_skills", {"query": "knowledge graph", "limit": 5}),
    ("get_skill", {"skill_id": "skill:knowledge-graph-rag", "retrieval_unit_limit": 3}),
    (
        "recommend_skills",
        {"query": "design a knowledge graph RAG system", "limit": 5, "max_depth": 2},
    ),
    ("get_skill_context", {"skill_id": "skill:knowledge-graph-rag", "limit": 10}),
    ("route_skill_query", {"query": "how do I use knowledge-graph-rag?"}),
    ("resolve_skill", {"name": "knowledge-graph-rag"}),
    (
        "get_skill_execution_guide",
        {"skill_id": "skill:knowledge-graph-rag", "token_budget": 600},
    ),
)

_TIMING_KEYS = (
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


def build_server(*, fixture: bool, skills_root: Path) -> SkillsMcpServer:
    if fixture:
        return SkillsMcpServer.for_test_fixture()
    return SkillsMcpServer.from_repository(skills_root)


def run_case(
    server: SkillsMcpServer,
    tool: str,
    arguments: Mapping[str, object],
    *,
    iterations: int,
    warmup: int,
) -> dict[str, object]:
    for _ in range(max(0, warmup)):
        server.call_tool(tool, arguments)

    samples: list[dict[str, object]] = []
    statuses: list[str] = []
    for _ in range(iterations):
        response = server.call_tool(tool, arguments)
        timing = response.get("timing")
        if not isinstance(timing, dict):
            raise RuntimeError(f"Tool {tool!r} response missing timing metadata")
        sample: dict[str, object] = {}
        for key in _TIMING_KEYS:
            value = timing.get(key)
            if not isinstance(value, (int, float)):
                raise RuntimeError(
                    f"Tool {tool!r} returned invalid timing field {key!r}: {timing!r}"
                )
            sample[key] = float(value) if key.endswith("_ms") else int(value)
        status = response.get("status")
        statuses.append(status if isinstance(status, str) else "unknown")
        samples.append(sample)

    summary = skills_mcp_perf.summarise_timings(samples)
    status_counts: dict[str, int] = {}
    for status in statuses:
        status_counts[status] = status_counts.get(status, 0) + 1
    return {
        "tool": tool,
        "arguments": dict(arguments),
        "status_counts": status_counts,
        **summary,
    }


def run_benchmark(
    server: SkillsMcpServer,
    cases: Sequence[tuple[str, dict[str, object]]],
    *,
    iterations: int,
    warmup: int,
) -> dict[str, object]:
    started = time.perf_counter()
    results = [
        run_case(server, tool, arguments, iterations=iterations, warmup=warmup)
        for tool, arguments in cases
    ]
    return {
        "iterations": iterations,
        "warmup": warmup,
        "wall_time_ms": round((time.perf_counter() - started) * 1000.0, 3),
        "tools": results,
    }


def _mean(item: Mapping[str, Any], field_name: str) -> object:
    values = item[field_name]
    assert isinstance(values, dict)
    return values["mean"]


def render_report(report: Mapping[str, Any], *, source: str) -> str:
    lines = [
        "# Full System Run Report: MCP tool baseline",
        "",
        f"- Source: `{source}`",
        f"- Iterations per tool: {report['iterations']}",
        f"- Warmup iterations: {report['warmup']}",
        f"- Wall time: {report['wall_time_ms']} ms",
        "",
        "## Latency breakdown (mean ms)",
        "",
        "| Tool | n | status | total | handler | payload | db I/O | disk I/O |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    tools = report["tools"]
    assert isinstance(tools, list)
    for item in tools:
        status_counts = item["status_counts"]
        status = ", ".join(f"{name}={count}" for name, count in sorted(status_counts.items()))
        lines.append(
            "| {tool} | {count} | {status} | {total} | {handler} | {payload} | {db_io} | {disk_io} |".format(
                tool=item["tool"],
                count=item["count"],
                status=status,
                total=_mean(item, "duration_ms"),
                handler=_mean(item, "handler_ms"),
                payload=_mean(item, "payload_construction_ms"),
                db_io=_mean(item, "database_io_ms"),
                disk_io=_mean(item, "disk_io_ms"),
            )
        )

    lines.extend(
        [
            "",
            "## Payload and I/O sizes (mean bytes)",
            "",
            "| Tool | request | response | db bytes read | disk bytes read |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in tools:
        lines.append(
            "| {tool} | {request} | {response} | {db_bytes} | {disk_bytes} |".format(
                tool=item["tool"],
                request=_mean(item, "request_bytes"),
                response=_mean(item, "response_bytes"),
                db_bytes=_mean(item, "database_bytes_read"),
                disk_bytes=_mean(item, "disk_bytes_read"),
            )
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Timings are in-process handler cost only (no MCP transport, no HTTP).",
            "- `handler` is total time minus payload construction, database I/O and disk I/O.",
            "- `payload` includes response assembly and JSON size measurement.",
            "- `db I/O` / `disk I/O` are zero for the in-memory MCP snapshot path unless a tool "
            "loads from Neo4j or disk during the call.",
            "- `response_bytes` is the JSON payload size before the `timing` field is attached.",
            "- Use `/metrics` (`skills_mcp_tool_*`) for live process histograms after deployment.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixture",
        action="store_true",
        help="Benchmark the small test fixture graph (default).",
    )
    parser.add_argument(
        "--repository",
        action="store_true",
        help="Benchmark the full skills/ repository load plan.",
    )
    parser.add_argument(
        "--skills-root",
        type=Path,
        default=Path("skills"),
        help="Skills root when using --repository.",
    )
    parser.add_argument("--iterations", type=int, default=25, help="Measured iterations per tool.")
    parser.add_argument("--warmup", type=int, default=3, help="Warmup iterations discarded.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of the markdown report.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    use_fixture = not args.repository
    source = "fixture" if use_fixture else f"repository:{args.skills_root}"
    server = build_server(fixture=use_fixture, skills_root=args.skills_root)
    report = run_benchmark(
        server,
        DEFAULT_CASES,
        iterations=max(1, args.iterations),
        warmup=max(0, args.warmup),
    )
    report["source"] = source

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_report(report, source=source))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
