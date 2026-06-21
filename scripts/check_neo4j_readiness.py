#!/usr/bin/env python3
"""Check live Neo4j readiness for the Skills KG retrieval path."""

from __future__ import annotations

import json
import sys
import time
from argparse import ArgumentParser
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import load_skills_neo4j, skills_config

REQUIRED_INDEXES = frozenset(
    {
        "skill_category_lookup",
        "skill_path_lookup",
        "bridge_assertion_source_lookup",
        "retrieval_unit_source_lookup",
        "skill_metadata_fulltext",
        "retrieval_unit_text_fulltext",
        "retrieval_unit_embedding_vector",
    }
)


class Neo4jReadinessReport(BaseModel):
    """Readiness result safe to print or return from API health checks."""

    model_config = ConfigDict(frozen=True)

    ready: bool
    database: str
    constraints_online: tuple[str, ...]
    indexes_online: tuple[str, ...]
    vector_query_ok: bool
    errors: tuple[str, ...]


def _record_value(record: Mapping[str, object], key: str) -> object:
    value = record.get(key)
    return value


def _normalise_records(records: Sequence[Mapping[str, object]]) -> tuple[Mapping[str, object], ...]:
    return tuple(dict(record) for record in records)


def _online_index_names(index_records: Sequence[Mapping[str, object]]) -> set[str]:
    names = set()
    for record in index_records:
        name = _record_value(record, "name")
        state = _record_value(record, "state")
        if isinstance(name, str) and str(state).upper() == "ONLINE":
            names.add(name)
    return names


def collect_readiness(driver: Any, settings: skills_config.Neo4jSettings) -> Neo4jReadinessReport:
    """Collect readiness evidence from a live Neo4j database."""

    errors: list[str] = []
    vector_query_ok = False
    with driver.session(database=settings.database) as session:
        constraint_records = _normalise_records(
            session.run("SHOW CONSTRAINTS YIELD name RETURN name")
        )
        index_records = _normalise_records(
            session.run(
                "SHOW INDEXES YIELD name, state, type, options RETURN name, state, type, options"
            )
        )
        constraints_online = {
            str(record["name"])
            for record in constraint_records
            if isinstance(record.get("name"), str)
        }
        indexes_online = _online_index_names(index_records)

        for constraint_name in sorted(load_skills_neo4j.REQUIRED_SCHEMA_ITEMS - constraints_online):
            errors.append(f"missing constraint: {constraint_name}")
        for index_name in sorted(REQUIRED_INDEXES - indexes_online):
            errors.append(f"missing index: {index_name}")

        if settings.vector_index in indexes_online:
            embedding = [0.0 for _ in range(settings.embedding_dimensions)]
            if embedding:
                embedding[0] = 1.0
            records = _normalise_records(
                session.run(
                    (
                        "CALL db.index.vector.queryNodes($index_name, 1, $embedding) "
                        "YIELD node, score "
                        "RETURN node.id AS retrieval_unit_id, score"
                    ),
                    index_name=settings.vector_index,
                    embedding=embedding,
                )
            )
            vector_query_ok = bool(records)
            if not vector_query_ok:
                errors.append("vector query returned no RetrievalUnit candidates")

    return Neo4jReadinessReport(
        ready=not errors,
        database=settings.database,
        constraints_online=tuple(sorted(constraints_online)),
        indexes_online=tuple(sorted(indexes_online)),
        vector_query_ok=vector_query_ok,
        errors=tuple(errors),
    )


def wait_for_neo4j(
    driver: Any,
    timeout_seconds: float = 60.0,
    poll_seconds: float = 1.0,
) -> None:
    """Wait for Neo4j connectivity, bounded for CI service startup."""

    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            driver.verify_connectivity()
            return
        except Exception as exc:  # pragma: no cover - timing dependent live boundary
            last_error = exc
            time.sleep(poll_seconds)
    raise TimeoutError("Neo4j did not become ready before timeout") from last_error


def main(argv: Sequence[str] | None = None) -> int:  # pragma: no cover
    parser = ArgumentParser(description="Check live Neo4j readiness for the Skills KG.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))

    settings = skills_config.load_settings()
    graph = load_skills_neo4j.neo4j_graph_from_settings(settings.neo4j)
    wait_for_neo4j(graph.driver)
    report = collect_readiness(graph.driver, settings.neo4j)
    if args.json:
        print(report.model_dump_json(indent=2))
    else:
        print(json.dumps(report.model_dump(), indent=2, sort_keys=True))
    return 0 if report.ready else 1


if __name__ == "__main__":
    sys.exit(main())
