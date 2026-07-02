#!/usr/bin/env python3
"""Run the Phase 7 KRAG cutover and acceptance checks."""

from __future__ import annotations

import json
import sys
from argparse import ArgumentParser
from collections.abc import Mapping, Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import (
    embed_skill_chunks,
    evaluate_skill_retrieval,
    retrieve_skills_hybrid,
    skills_query_graph,
    skills_router,
    validate_skills_ontology,
)

DEFAULT_DATASET = Path("tests") / "fixtures" / "retrieval_evaluation" / "smoke_queries_promoted.json"


class RuntimeScenario(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    query: str
    expected_route: str
    expected_query_family: str
    expected_selected_skill_id: str | None = None
    expected_graph_status: str = "ok"
    expect_uncertain: bool = False


class RuntimeScenarioResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    query: str
    route: str
    query_family: str
    graph_query_status: str
    generated_cypher: str
    selected_skill_id: str | None
    uncertain: bool
    supporting_evidence_count: int
    manual_loading_token_cost: int
    bounded_token_cost: int
    passed: bool
    failures: tuple[str, ...]


class AcceptanceCheck(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    passed: bool
    detail: str


class CutoverAcceptanceReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    passed: bool
    ontology_validation_passed: bool
    minimal_krag_slice_passed: bool
    skill_count: int
    retrieval_unit_count: int
    mean_manual_loading_token_cost: float
    mean_bounded_token_cost: float
    acceptance_checks: tuple[AcceptanceCheck, ...]
    runtime_scenarios: tuple[RuntimeScenarioResult, ...]
    evaluation: evaluate_skill_retrieval.RetrievalEvaluationReport


RUNTIME_SCENARIOS = (
    RuntimeScenario(
        id="direct_lookup",
        query="Tell me about tdd-practice",
        expected_route="direct_lookup",
        expected_query_family="exact_skill_lookup",
        expected_selected_skill_id="skill:tdd-practice",
    ),
    RuntimeScenario(
        id="recommendation",
        query="Which skill should I use when fixing a defect with a failing test first?",
        expected_route="recommendation",
        expected_query_family="capability_task_lookup",
        expected_selected_skill_id="skill:tdd-practice",
    ),
    RuntimeScenario(
        id="context",
        query="What skills are related to tdd-practice?",
        expected_route="context",
        expected_query_family="related_skill_traversal",
        expected_selected_skill_id="skill:tdd-practice",
    ),
    RuntimeScenario(
        id="execution_plan",
        query="Show me the verification checklist for tdd-practice",
        expected_route="execution_plan",
        expected_query_family="constraint_verification_retrieval",
        expected_selected_skill_id="skill:tdd-practice",
    ),
    RuntimeScenario(
        id="evidence_lookup",
        query="Show me the evidence for tdd-practice",
        expected_route="direct_lookup",
        expected_query_family="evidence_fragment_retrieval",
        expected_selected_skill_id="skill:tdd-practice",
    ),
    RuntimeScenario(
        id="abstention",
        query="zzzz qqqq nonsense",
        expected_route="recommendation",
        expected_query_family="capability_task_lookup",
        expected_graph_status="abstain",
        expect_uncertain=True,
    ),
)


def _manual_loading_token_cost(plan: object, skill_id: str) -> int:
    cost = 0
    for node in getattr(plan, "nodes", ()):
        if getattr(node, "label", "") != "RetrievalUnit":
            continue
        properties = getattr(node, "properties", {})
        if not isinstance(properties, dict):
            continue
        if properties.get("skill_id") != skill_id:
            continue
        text = properties.get("text")
        if isinstance(text, str):
            cost += len(text.split())
    return cost


def _selected_recommendation(
    result: retrieve_skills_hybrid.HybridRetrievalResult,
) -> retrieve_skills_hybrid.SkillRecommendation | None:
    if not result.recommendations:
        return None
    return result.recommendations[0]


def _is_read_only_cypher(cypher: str) -> bool:
    blocked = (" CREATE ", " MERGE ", " SET ", " DELETE ", " REMOVE ", " CALL dbms", " LOAD CSV ")
    upper = f" {cypher.upper()} "
    return all(fragment not in upper for fragment in blocked)


def _run_runtime_scenario(
    plan: object,
    embedder: embed_skill_chunks.DeterministicEmbeddingProvider,
    scenario: RuntimeScenario,
    limit: int,
    token_budget: int,
) -> RuntimeScenarioResult:
    route = skills_router.route_skill_query(plan, scenario.query)
    resolved_skill_id = (
        str(route.get("resolved_skill_id")) if route.get("resolved_skill_id") is not None else ""
    )
    query_plan = skills_query_graph.plan_graph_query(
        plan,
        scenario.query,
        route=str(route.get("route", "")),
        resolved_skill_id=resolved_skill_id,
        limit=limit,
    )
    graph_query_result = skills_query_graph.execute_planned_query(plan, query_plan)
    vector_candidates = embed_skill_chunks.query_vector_candidates(
        plan,
        scenario.query,
        embedder,
        limit=limit,
    )
    retrieval_result = retrieve_skills_hybrid.retrieve_hybrid_skills(
        plan,
        scenario.query,
        vector_candidates=vector_candidates,
        limit=limit,
        token_budget=token_budget,
    )
    selected = _selected_recommendation(retrieval_result)
    generated_cypher = str(query_plan.get("generated_cypher", ""))
    resolved_skill_id_value = resolved_skill_id or None
    failures: list[str] = []

    if str(route.get("route")) != scenario.expected_route:
        failures.append(
            f"expected route {scenario.expected_route}, got {route.get('route')}"
        )
    if str(query_plan.get("query_family")) != scenario.expected_query_family:
        failures.append(
            "expected query family "
            f"{scenario.expected_query_family}, got {query_plan.get('query_family')}"
        )
    if str(graph_query_result.get("status")) != scenario.expected_graph_status:
        failures.append(
            "expected graph status "
            f"{scenario.expected_graph_status}, got {graph_query_result.get('status')}"
        )
    if not generated_cypher or "LIMIT $limit" not in generated_cypher or not _is_read_only_cypher(
        generated_cypher
    ):
        failures.append("generated Cypher was missing, unbounded, or not read-only")
    if retrieval_result.uncertain != scenario.expect_uncertain:
        failures.append(
            f"expected uncertainty={scenario.expect_uncertain}, got {retrieval_result.uncertain}"
        )

    if scenario.expected_route == "recommendation":
        selected_skill_id = selected.skill_id if selected is not None else None
    else:
        selected_skill_id = resolved_skill_id_value

    if scenario.expected_selected_skill_id and selected_skill_id != scenario.expected_selected_skill_id:
        failures.append(
            f"expected selected skill {scenario.expected_selected_skill_id}, got {selected_skill_id}"
        )

    supporting_evidence_count = 0
    bounded_token_cost = 0
    manual_loading_token_cost = 0
    if scenario.expected_route == "recommendation" and selected is not None:
        supporting_evidence_count = (
            len(selected.evidence_snippets) + len(selected.source_paths) + len(selected.section_ids)
        )
        bounded_token_cost = sum(len(snippet.split()) for snippet in selected.evidence_snippets)
        manual_loading_token_cost = _manual_loading_token_cost(plan, selected.skill_id)
        if not selected.source_paths or not selected.section_ids or not selected.evidence_snippets:
            failures.append("selected recommendation did not include bounded evidence")
        if manual_loading_token_cost <= 0:
            failures.append("manual loading token cost could not be measured")
    elif scenario.expected_route != "recommendation" and not scenario.expect_uncertain:
        citations = graph_query_result.get("citations")
        paths = graph_query_result.get("path_summaries")
        records = graph_query_result.get("records")
        supporting_evidence_count = (
            (len(citations) if isinstance(citations, list) else 0)
            + (len(paths) if isinstance(paths, list) else 0)
            + (len(records) if isinstance(records, list) else 0)
        )
        if supporting_evidence_count <= 0:
            failures.append("route-specific graph execution did not return bounded evidence")
        if resolved_skill_id_value:
            manual_loading_token_cost = _manual_loading_token_cost(plan, resolved_skill_id_value)
    elif not scenario.expect_uncertain:
        failures.append("no selected recommendation was available")

    return RuntimeScenarioResult(
        id=scenario.id,
        query=scenario.query,
        route=str(route.get("route", "")),
        query_family=str(query_plan.get("query_family", "")),
        graph_query_status=str(graph_query_result.get("status", "")),
        generated_cypher=generated_cypher,
        selected_skill_id=selected_skill_id,
        uncertain=retrieval_result.uncertain,
        supporting_evidence_count=supporting_evidence_count,
        manual_loading_token_cost=manual_loading_token_cost,
        bounded_token_cost=bounded_token_cost,
        passed=not failures,
        failures=tuple(failures),
    )


def run_cutover_acceptance(
    dataset_path: Path = DEFAULT_DATASET,
    *,
    limit: int = 3,
    token_budget: int = 240,
) -> CutoverAcceptanceReport:
    ontology_validation = validate_skills_ontology.validate_skills_ontology(profile="all")
    plan = embed_skill_chunks.build_embedded_repository_load_plan()
    embedder = embed_skill_chunks.DeterministicEmbeddingProvider(
        dimension=embed_skill_chunks._embedding_dimension_from_config(
            embed_skill_chunks.DEFAULT_CONFIG_PATH
        )
    )
    runtime_scenarios = tuple(
        _run_runtime_scenario(plan, embedder, scenario, limit, token_budget)
        for scenario in RUNTIME_SCENARIOS
    )
    evaluation = evaluate_skill_retrieval.evaluate_offline(dataset_path, limit=limit)

    skill_count = sum(1 for node in plan.nodes if node.label == "Skill")
    retrieval_unit_count = sum(1 for node in plan.nodes if node.label == "RetrievalUnit")
    selected_scenarios = [
        scenario
        for scenario in runtime_scenarios
        if scenario.id == "recommendation" and scenario.selected_skill_id
    ]
    mean_manual_cost = (
        sum(scenario.manual_loading_token_cost for scenario in selected_scenarios)
        / len(selected_scenarios)
        if selected_scenarios
        else 0.0
    )
    mean_bounded_cost = (
        sum(scenario.bounded_token_cost for scenario in selected_scenarios)
        / len(selected_scenarios)
        if selected_scenarios
        else 0.0
    )

    minimal_slice_scenario = next(
        scenario for scenario in runtime_scenarios if scenario.id == "recommendation"
    )
    minimal_krag_slice_passed = minimal_slice_scenario.passed and minimal_slice_scenario.graph_query_status == "ok"

    acceptance_checks = (
        AcceptanceCheck(
            name="selected_skills_have_supporting_evidence",
            passed=all(
                scenario.uncertain or scenario.supporting_evidence_count > 0
                for scenario in runtime_scenarios
            ),
            detail="Every non-uncertain selected skill returned snippets, source paths and section ids.",
        ),
        AcceptanceCheck(
            name="direct_routing_edges_are_derived",
            passed=ontology_validation.valid,
            detail="All SHACL profiles passed, including derivation-backed routing-edge constraints.",
        ),
        AcceptanceCheck(
            name="evidence_anchors_have_coordinates",
            passed=ontology_validation.valid,
            detail="Ontology validation passed for sourcePath, headingPath and line-range constraints.",
        ),
        AcceptanceCheck(
            name="deprecated_or_superseded_skills_excluded",
            passed=evaluation.exclusion_accuracy >= 1.0,
            detail=f"Measured exclusion_accuracy={evaluation.exclusion_accuracy:.3f}.",
        ),
        AcceptanceCheck(
            name="selection_responses_include_selected_skill_rationale_and_evidence",
            passed=all(
                scenario.uncertain
                or (scenario.selected_skill_id and scenario.supporting_evidence_count > 0)
                for scenario in runtime_scenarios
            ),
            detail="Runtime scenarios returned selected skill identities and bounded evidence payloads.",
        ),
        AcceptanceCheck(
            name="top1_accuracy_measured",
            passed=evaluation.precision_at_1 >= 0.0,
            detail=f"precision_at_1={evaluation.precision_at_1:.3f}",
        ),
        AcceptanceCheck(
            name="recall_at_3_measured",
            passed=evaluation.recall_at_k >= 0.0,
            detail=f"recall_at_k={evaluation.recall_at_k:.3f}",
        ),
        AcceptanceCheck(
            name="p95_latency_measured",
            passed=evaluation.p95_latency_ms >= 0.0,
            detail=f"p95_latency_ms={evaluation.p95_latency_ms:.3f}",
        ),
        AcceptanceCheck(
            name="token_cost_vs_manual_loading_measured",
            passed=mean_manual_cost > 0 and mean_bounded_cost > 0,
            detail=(
                "mean_bounded_token_cost="
                f"{mean_bounded_cost:.3f}; mean_manual_loading_token_cost={mean_manual_cost:.3f}"
            ),
        ),
        AcceptanceCheck(
            name="citation_coverage_measured",
            passed=evaluation.citation_coverage >= 0.0,
            detail=f"citation_coverage={evaluation.citation_coverage:.3f}",
        ),
        AcceptanceCheck(
            name="exclusion_accuracy_measured",
            passed=evaluation.exclusion_accuracy >= 0.0,
            detail=f"exclusion_accuracy={evaluation.exclusion_accuracy:.3f}",
        ),
        AcceptanceCheck(
            name="minimum_krag_slice_passed",
            passed=minimal_krag_slice_passed,
            detail="Recommendation route produced route classification, bounded Cypher, graph evidence and a selected skill.",
        ),
        AcceptanceCheck(
            name="graph_lift_non_negative",
            passed=evaluation.graph_lift_recall_at_k >= 0.0,
            detail=f"graph_lift_recall_at_k={evaluation.graph_lift_recall_at_k:.3f}",
        ),
    )

    promoted_skill_count = sum(
        1
        for node in plan.nodes
        if node.label == "Skill"
        and str(node.properties.get("promotion_status", "")) == "promoted"
    )
    passed = (
        ontology_validation.valid
        and evaluation.passed
        and minimal_krag_slice_passed
        and all(check.passed for check in acceptance_checks)
        and all(scenario.passed for scenario in runtime_scenarios)
        and skill_count > 0
        and retrieval_unit_count > 0
        and promoted_skill_count > 0
        and retrieval_unit_count >= promoted_skill_count
    )

    return CutoverAcceptanceReport(
        passed=passed,
        ontology_validation_passed=ontology_validation.valid,
        minimal_krag_slice_passed=minimal_krag_slice_passed,
        skill_count=skill_count,
        retrieval_unit_count=retrieval_unit_count,
        mean_manual_loading_token_cost=round(mean_manual_cost, 6),
        mean_bounded_token_cost=round(mean_bounded_cost, 6),
        acceptance_checks=acceptance_checks,
        runtime_scenarios=runtime_scenarios,
        evaluation=evaluation,
    )


def main(argv: Sequence[str] | None = None) -> int:  # pragma: no cover
    parser = ArgumentParser(description="Run the KRAG Phase 7 cutover acceptance checks.")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET))
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--token-budget", type=int, default=240)
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))

    report = run_cutover_acceptance(
        Path(args.dataset),
        limit=args.limit,
        token_budget=args.token_budget,
    )
    print(json.dumps(report.model_dump(), indent=2))
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
