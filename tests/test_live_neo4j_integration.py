"""Live Neo4j integration tests for the Skills KG."""

from __future__ import annotations

import os

import pytest

from scripts import (
    check_neo4j_readiness,
    embed_skill_chunks,
    load_skills_neo4j,
    retrieve_skills_hybrid,
    skills_config,
)
from tests.test_load_skills_neo4j import fixture_records

pytestmark = pytest.mark.live_neo4j

CI_FIXTURE_SKILL_COUNT = 2
CI_RETRIEVAL_QUERY = "baseline safety keep humans safe"


def _has_live_neo4j_env() -> bool:
    return all(os.environ.get(name) for name in ("NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"))


def _build_ci_fixture_plan() -> load_skills_neo4j.LoadPlan:
    settings = skills_config.load_settings()
    base_plan = load_skills_neo4j.build_load_plan(fixture_records())
    embedder = embed_skill_chunks.DeterministicEmbeddingProvider(
        dimension=settings.neo4j.embedding_dimensions
    )
    return embed_skill_chunks.embed_retrieval_units(base_plan, embedder)


@pytest.mark.skipif(not _has_live_neo4j_env(), reason="live Neo4j environment is not configured")
def test_live_neo4j_fixture_load_is_idempotent_and_indexes_are_ready() -> None:
    """Bounded CI fixture: schema, indexes, vector search, and idempotent reload."""
    settings = skills_config.load_settings()
    graph = load_skills_neo4j.neo4j_graph_from_settings(settings.neo4j)
    plan = _build_ci_fixture_plan()
    try:
        check_neo4j_readiness.wait_for_neo4j(graph.driver)
        schema = load_skills_neo4j.read_schema_statements()
        schema_params = {"embedding_dimensions": settings.neo4j.embedding_dimensions}

        first = load_skills_neo4j.load_plan(
            graph,
            plan,
            schema_statements=schema,
            schema_parameters=schema_params,
        )
        second = load_skills_neo4j.load_plan(
            graph,
            plan,
            schema_statements=schema,
            schema_parameters=schema_params,
        )
        readiness = check_neo4j_readiness.collect_readiness(graph.driver, settings.neo4j)
        retrieval = retrieve_skills_hybrid.retrieve_hybrid_skills_from_neo4j(
            graph.driver,
            settings,
            CI_RETRIEVAL_QUERY,
            limit=3,
        )
    finally:
        graph.driver.close()

    assert first.logical_counts == second.logical_counts
    assert first.logical_counts["node:Skill"] == CI_FIXTURE_SKILL_COUNT
    expected_retrieval_units = sum(1 for node in plan.nodes if node.label == "RetrievalUnit")
    assert first.logical_counts["node:RetrievalUnit"] == expected_retrieval_units
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
