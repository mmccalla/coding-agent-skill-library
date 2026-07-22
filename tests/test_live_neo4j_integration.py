"""Live Neo4j integration tests for the Skills KG."""

from __future__ import annotations

import os
from collections.abc import Sequence

import pytest

from scripts.graph.build import embed_skill_chunks
from scripts.graph.load import load_skills_neo4j
from scripts.lib.config import skills_config
from scripts.lib.config.repo_paths import REPO_ROOT
from scripts.lib.retrieval import retrieve_skills_hybrid
from scripts.runtime.docker import check_neo4j_readiness

pytestmark = pytest.mark.live_neo4j

SKILLS_ROOT = REPO_ROOT / "skills"
# Portable library size (skills/*/SKILL.md). Local Neo4j may briefly hold superseded
# Skill nodes until the live test purges ids absent from the current load plan.
EXPECTED_LIBRARY_SKILL_COUNT = 113
FULL_LIBRARY_RETRIEVAL_QUERY = (
    "When should I use apply-laws-of-ai as the mandatory session safety baseline?"
)


def _has_live_neo4j_env() -> bool:
    return all(os.environ.get(name) for name in ("NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"))


def _build_full_library_plan() -> load_skills_neo4j.LoadPlan:
    """Build the embedded full-library plan (respects SKILLS_EMBEDDING_PROVIDER)."""

    return embed_skill_chunks.build_embedded_repository_load_plan(skills_root=SKILLS_ROOT)


def _skill_ids_in_plan(plan: load_skills_neo4j.LoadPlan) -> tuple[str, ...]:
    return tuple(sorted(node.id for node in plan.nodes if node.label == "Skill"))


def _purge_skills_absent_from_plan(
    graph: load_skills_neo4j.Neo4jMergeGraph,
    database: str,
    skill_ids: Sequence[str],
) -> None:
    """Remove superseded Skill nodes not in the current library."""

    with graph.driver.session(database=database) as session:
        session.run(
            ("MATCH (s:Skill) WHERE NOT s.id IN $skill_ids DETACH DELETE s"),
            skill_ids=list(skill_ids),
        )


@pytest.mark.skipif(not _has_live_neo4j_env(), reason="live Neo4j environment is not configured")
def test_live_neo4j_full_library_load_is_idempotent_and_indexes_are_ready() -> None:
    """Full skills library: schema, indexes, vector search, and idempotent reload."""

    settings = skills_config.load_settings()
    graph = load_skills_neo4j.neo4j_graph_from_settings(settings.neo4j)
    plan = _build_full_library_plan()
    plan_skill_ids = _skill_ids_in_plan(plan)
    assert len(plan_skill_ids) == EXPECTED_LIBRARY_SKILL_COUNT
    expected_retrieval_units = sum(1 for node in plan.nodes if node.label == "RetrievalUnit")

    try:
        check_neo4j_readiness.wait_for_neo4j(graph.driver)
        schema = load_skills_neo4j.read_schema_statements()
        schema_params = {"embedding_dimensions": settings.neo4j.embedding_dimensions}

        load_skills_neo4j.load_plan(
            graph,
            plan,
            schema_statements=schema,
            schema_parameters=schema_params,
        )
        _purge_skills_absent_from_plan(graph, settings.neo4j.database, plan_skill_ids)
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
            FULL_LIBRARY_RETRIEVAL_QUERY,
            limit=3,
        )
    finally:
        graph.driver.close()

    assert first.logical_counts == second.logical_counts
    assert first.logical_counts["node:Skill"] == EXPECTED_LIBRARY_SKILL_COUNT
    # Unit counts may exceed the current extract when prior embed runs left alternate unit ids;
    # require at least the current plan coverage.
    assert first.logical_counts["node:RetrievalUnit"] >= expected_retrieval_units
    assert readiness.ready, readiness.errors
    assert readiness.vector_query_ok
    assert not retrieval.uncertain
    assert retrieval.recommendations
    assert retrieval.recommendations[0].skill_id == "skill:apply-laws-of-ai"
    assert retrieval.recommendations[0].source_paths
    assert retrieval.recommendations[0].section_ids
    assert retrieval.recommendations[0].score > 0 or retrieval.recommendations[0].graph_score > 0
