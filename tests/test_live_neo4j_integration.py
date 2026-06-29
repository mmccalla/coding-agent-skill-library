"""Live Neo4j integration tests for the Skills KG."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from scripts import (
    check_neo4j_readiness,
    embed_skill_chunks,
    load_skills_neo4j,
    retrieve_skills_hybrid,
    skills_config,
)

pytestmark = pytest.mark.live_neo4j
EXPECTED_SKILL_COUNT = len(
    tuple((Path(__file__).resolve().parents[1] / "skills").glob("*/*/SKILL.md"))
)


def _has_live_neo4j_env() -> bool:
    return all(os.environ.get(name) for name in ("NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"))


@pytest.mark.skipif(not _has_live_neo4j_env(), reason="live Neo4j environment is not configured")
def test_live_neo4j_load_is_idempotent_and_indexes_are_ready() -> None:
    settings = skills_config.load_settings()
    graph = load_skills_neo4j.neo4j_graph_from_settings(settings.neo4j)
    try:
        check_neo4j_readiness.wait_for_neo4j(graph.driver)
        plan = embed_skill_chunks.build_embedded_repository_load_plan()

        first = load_skills_neo4j.load_plan(
            graph,
            plan,
            schema_statements=load_skills_neo4j.read_schema_statements(),
            schema_parameters={"embedding_dimensions": settings.neo4j.embedding_dimensions},
        )
        second = load_skills_neo4j.load_plan(
            graph,
            plan,
            schema_statements=load_skills_neo4j.read_schema_statements(),
            schema_parameters={"embedding_dimensions": settings.neo4j.embedding_dimensions},
        )
        readiness = check_neo4j_readiness.collect_readiness(graph.driver, settings.neo4j)
        retrieval = retrieve_skills_hybrid.retrieve_hybrid_skills_from_neo4j(
            graph.driver,
            settings,
            "approval before destructive command human review",
            limit=3,
        )
    finally:
        graph.driver.close()

    assert first.logical_counts == second.logical_counts
    assert first.logical_counts["node:Skill"] == EXPECTED_SKILL_COUNT
    assert first.logical_counts["node:RetrievalUnit"] >= EXPECTED_SKILL_COUNT
    assert readiness.ready, readiness.errors
    assert readiness.vector_query_ok
    assert not retrieval.uncertain
    assert retrieval.recommendations
    assert retrieval.recommendations[0].source_paths
    assert retrieval.recommendations[0].section_ids
    assert (
        retrieval.recommendations[0].full_text_score > 0
        or retrieval.recommendations[0].graph_score > 0
    )
