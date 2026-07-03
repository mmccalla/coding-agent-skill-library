#!/usr/bin/env python3
"""Evaluate Skills KG retrieval against golden queries."""

from __future__ import annotations

import json
import math
import re
import sys
import time
from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import embed_skill_chunks, retrieve_skills_hybrid, skills_config
from scripts import skills_query_graph, skills_router
from scripts.extract_skills_graph import extract_skills_graph_records

DEFAULT_DATASET = Path("tests") / "fixtures" / "retrieval_evaluation" / "golden_queries.json"
PROMOTED_RELEASE_DATASET = (
    Path("tests") / "fixtures" / "retrieval_evaluation" / "golden_queries_promoted_release.json"
)


class EvaluationCase(BaseModel):
    """One golden retrieval query."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(min_length=1)
    query: str = Field(min_length=1)
    expected_skill_ids: tuple[str, ...]
    required_skill_ids: tuple[str, ...] = ()
    excluded_skill_ids: tuple[str, ...] = ()
    expect_uncertain: bool = False
    promotion_tier: str | None = None


class EvaluationCaseResult(BaseModel):
    """One evaluated query result with governance-relevant signals."""

    model_config = ConfigDict(frozen=True)

    id: str
    passed: bool
    route: str
    query_family: str
    ranked_skill_ids: tuple[str, ...]
    vector_only_ranked_skill_ids: tuple[str, ...]
    uncertain: bool
    citation_covered: bool
    exclusion_passed: bool
    selection_trace_present: bool
    graph_query_plan_present: bool
    latency_ms: float
    token_cost: int
    failures: tuple[str, ...]


class RetrievalEvaluationReport(BaseModel):
    """Aggregate retrieval evaluation metrics."""

    model_config = ConfigDict(frozen=True)

    passed: bool
    cases: int
    precision_at_1: float
    recall_at_k: float
    mean_reciprocal_rank: float
    ndcg_at_k: float
    source_coverage: float
    citation_coverage: float
    exclusion_accuracy: float
    uncertainty_accuracy: float
    selection_trace_coverage: float
    query_plan_coverage: float
    exact_lookup_accuracy: float
    alias_resolution_accuracy: float
    graph_relevant_cases: int
    graph_relevant_recall_at_k: float
    vector_only_recall_at_k: float
    graph_lift_recall_at_k: float
    mean_token_cost_per_selection: float
    latency_ms: float
    p95_latency_ms: float
    case_results: tuple[EvaluationCaseResult, ...]
    failures: tuple[str, ...]


def load_cases(path: Path = DEFAULT_DATASET) -> tuple[EvaluationCase, ...]:
    """Load and validate golden retrieval cases."""

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("retrieval evaluation dataset must be a JSON array")
    return tuple(EvaluationCase.model_validate(item) for item in data)


def load_promoted_skill_ids(skills_root: Path | None = None) -> frozenset[str]:
    """Return skill ids currently marked promoted in the extract pipeline."""

    root = skills_root or Path("skills")
    records = extract_skills_graph_records(root.resolve())
    return frozenset(
        str(skill["id"])
        for skill in records["skills"]
        if str(skill.get("promotion_status", "")) == "promoted"
    )


def filter_cases_by_promotion(
    cases: Sequence[EvaluationCase],
    promoted_ids: frozenset[str],
    *,
    case_filter: str,
) -> tuple[EvaluationCase, ...]:
    """Filter golden cases for release (promoted-eligible) or diagnostic arms."""

    if case_filter == "all":
        return tuple(cases)
    if case_filter == "promoted_eligible":
        filtered: list[EvaluationCase] = []
        for case in cases:
            if case.promotion_tier == "release":
                filtered.append(case)
                continue
            expected = set(case.expected_skill_ids) | set(case.required_skill_ids)
            if expected & promoted_ids:
                filtered.append(case)
        return tuple(filtered)
    raise ValueError(
        f"Unknown case_filter '{case_filter}'. Expected one of: all, promoted_eligible"
    )


def _reciprocal_rank(ranked_ids: Sequence[str], expected_ids: Sequence[str]) -> float:
    expected = set(expected_ids)
    for index, skill_id in enumerate(ranked_ids, start=1):
        if skill_id in expected:
            return 1.0 / index
    return 0.0


def _dcg_at_k(ranked_ids: Sequence[str], expected_ids: Sequence[str], k: int) -> float:
    expected = set(expected_ids)
    score = 0.0
    for index, skill_id in enumerate(ranked_ids[:k], start=1):
        if skill_id in expected:
            score += 1.0 / math.log2(index + 1)
    return score


def _ndcg_at_k(ranked_ids: Sequence[str], expected_ids: Sequence[str], k: int) -> float:
    if not expected_ids:
        return 1.0
    ideal_hits = min(len(expected_ids), k)
    ideal = sum(1.0 / math.log2(index + 1) for index in range(1, ideal_hits + 1))
    if ideal == 0:
        return 0.0
    return _dcg_at_k(ranked_ids, expected_ids, k) / ideal


def _normalise_phrase(text: str) -> str:
    return re.sub(r"[^a-z0-9:]+", "-", text.lower()).strip("-")


def _contains_alias_phrase(normalised_text: str, alias: str) -> bool:
    pattern = rf"(?:^|[-:]){re.escape(alias)}(?:$|[-:])"
    return bool(re.search(pattern, normalised_text))


def _precision_at_1(ranked_ids: Sequence[str], expected_ids: Sequence[str]) -> float:
    if not ranked_ids or not expected_ids:
        return 0.0
    return 1.0 if ranked_ids[0] in set(expected_ids) else 0.0


def _p95(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return ordered[index]


def _vector_only_ranked_ids(
    vector_candidates: Sequence[embed_skill_chunks.VectorCandidate],
    limit: int,
    min_score: float,
) -> tuple[str, ...]:
    scores: dict[str, float] = {}
    for candidate in vector_candidates:
        if candidate.score < min_score:
            continue
        current = scores.get(candidate.skill_id, 0.0)
        if candidate.score > current:
            scores[candidate.skill_id] = candidate.score
    return tuple(
        skill_id
        for skill_id, _score in sorted(scores.items(), key=lambda item: (-item[1], item[0]))[:limit]
    )


def _skill_alias_map(plan: object) -> dict[str, tuple[str, ...]]:
    aliases: dict[str, tuple[str, ...]] = {}
    for node in getattr(plan, "nodes", ()):
        if getattr(node, "label", "") != "Skill":
            continue
        properties = getattr(node, "properties", {})
        if not isinstance(properties, dict):
            continue
        raw_aliases = properties.get("aliases")
        if isinstance(raw_aliases, list):
            aliases[getattr(node, "id")] = tuple(
                alias for alias in raw_aliases if isinstance(alias, str)
            )
        else:
            aliases[getattr(node, "id")] = ()
    return aliases


def _is_exact_lookup_case(case: EvaluationCase) -> bool:
    query_terms = case.query.strip().lower()
    for expected in case.expected_skill_ids:
        if query_terms == expected.removeprefix("skill:"):
            return True
    return False


def _is_alias_lookup_case(case: EvaluationCase, alias_map: Mapping[str, Sequence[str]]) -> bool:
    query_terms = _normalise_phrase(case.query.strip())
    for expected in case.expected_skill_ids:
        aliases = {
            _normalise_phrase(alias)
            for alias in alias_map.get(expected, ())
            if isinstance(alias, str) and alias.strip()
        }
        if any(alias and _contains_alias_phrase(query_terms, alias) for alias in aliases):
            return True
    return False


def _retrieval_units_for_skill(plan: object, skill_id: str) -> tuple[object, ...]:
    units: list[object] = []
    for node in getattr(plan, "nodes", ()):
        if getattr(node, "label", "") != "RetrievalUnit":
            continue
        properties = getattr(node, "properties", {})
        if isinstance(properties, dict) and properties.get("skill_id") == skill_id:
            units.append(node)
    return tuple(units)


def _token_cost_for_units(units: Sequence[object], limit: int) -> int:
    cost = 0
    for unit in units[:limit]:
        properties = getattr(unit, "properties", {})
        if not isinstance(properties, dict):
            continue
        text = properties.get("text")
        if isinstance(text, str):
            cost += len(text.split())
    return cost


def _route_aware_result(
    plan: object,
    case: EvaluationCase,
    route: Mapping[str, object],
    graph_query_plan: Mapping[str, object],
    graph_query_result: Mapping[str, object],
    recommendation_result: retrieve_skills_hybrid.HybridRetrievalResult,
    limit: int,
) -> tuple[
    tuple[str, ...],
    bool,
    bool,
    bool,
    bool,
    int,
]:
    route_name = str(route.get("route", ""))
    resolved_skill_id = str(route.get("resolved_skill_id") or "")
    if route_name == skills_router.ROUTE_RECOMMENDATION or not resolved_skill_id:
        ranked_ids = tuple(item.skill_id for item in recommendation_result.recommendations)
        matching = [
            item for item in recommendation_result.recommendations if item.skill_id in set(case.expected_skill_ids)
        ]
        source_covered = bool(matching and all(item.source_paths and item.section_ids for item in matching))
        citation_covered = bool(matching and all(item.evidence_snippets for item in matching))
        selection_trace_present = bool(recommendation_result.selection_trace)
        uncertain = recommendation_result.uncertain
        token_cost = sum(
            len(snippet.split())
            for recommendation in recommendation_result.recommendations
            for snippet in recommendation.evidence_snippets
        )
        return (
            ranked_ids,
            source_covered,
            citation_covered,
            selection_trace_present,
            uncertain,
            token_cost,
        )

    ranked_ids = (resolved_skill_id,)
    if route_name == skills_router.ROUTE_CONTEXT:
        records = graph_query_result.get("records")
        if isinstance(records, list):
            for record in records:
                if isinstance(record, dict):
                    related_skill_id = record.get("related_skill_id")
                    if isinstance(related_skill_id, str) and related_skill_id and related_skill_id != resolved_skill_id:
                        ranked_ids += (related_skill_id,)
        ranked_ids = ranked_ids[:limit]

    units = _retrieval_units_for_skill(plan, resolved_skill_id)
    citations = graph_query_result.get("citations")
    paths = graph_query_result.get("path_summaries")
    records = graph_query_result.get("records")
    source_covered = bool(units) or bool(isinstance(records, list) and records)
    citation_covered = bool(
        (isinstance(citations, list) and citations)
        or (isinstance(paths, list) and paths)
        or units
    )
    return (
        ranked_ids,
        source_covered,
        citation_covered,
        True,
        False,
        _token_cost_for_units(units, limit),
    )


def evaluate_offline(
    dataset_path: Path = DEFAULT_DATASET,
    limit: int = 3,
    recall_threshold: float = 1.0,
    mrr_threshold: float = 1.0,
    source_threshold: float = 1.0,
    uncertainty_threshold: float = 1.0,
    *,
    case_filter: str = "all",
    skills_root: Path | None = None,
) -> RetrievalEvaluationReport:
    """Run deterministic offline retrieval evaluation."""

    start = time.perf_counter()
    settings = skills_config.load_settings()
    all_cases = load_cases(dataset_path)
    promoted_ids = load_promoted_skill_ids(skills_root)
    cases = filter_cases_by_promotion(all_cases, promoted_ids, case_filter=case_filter)
    plan = embed_skill_chunks.build_embedded_repository_load_plan()
    embedder = embed_skill_chunks.DeterministicEmbeddingProvider(
        dimension=settings.neo4j.embedding_dimensions
    )
    alias_map = _skill_alias_map(plan)
    positives = [case for case in cases if case.expected_skill_ids]
    hits = 0
    top1_hits = 0
    reciprocal_ranks: list[float] = []
    ndcgs: list[float] = []
    sourced = 0
    cited = 0
    exclusion_passes = 0
    uncertainty_correct = 0
    selection_trace_present = 0
    query_plan_present = 0
    exact_cases = 0
    exact_hits = 0
    alias_cases = 0
    alias_hits = 0
    graph_relevant_cases = 0
    graph_relevant_hits = 0
    vector_only_graph_hits = 0
    token_costs: list[int] = []
    latencies: list[float] = []
    case_results: list[EvaluationCaseResult] = []
    failures: list[str] = []

    for case in cases:
        case_failures: list[str] = []
        vector_candidates = embed_skill_chunks.query_vector_candidates(
            plan,
            case.query,
            embedder,
            limit=limit,
        )
        vector_only_ids = _vector_only_ranked_ids(
            vector_candidates,
            limit,
            settings.retrieval.min_vector_candidate_score,
        )
        route = skills_router.route_skill_query(plan, case.query)
        graph_query_plan = skills_query_graph.plan_graph_query(
            plan,
            case.query,
            route=str(route.get("route", "")),
            resolved_skill_id=str(route.get("resolved_skill_id") or ""),
            limit=limit,
        )
        graph_query_result = skills_query_graph.execute_planned_query(plan, graph_query_plan)
        if graph_query_plan.get("status") == "ok":
            query_plan_present += 1
        case_start = time.perf_counter()
        result = retrieve_skills_hybrid.retrieve_hybrid_skills(
            plan,
            case.query,
            vector_candidates=vector_candidates,
            limit=limit,
        )
        latency_ms = (time.perf_counter() - case_start) * 1000
        latencies.append(latency_ms)
        (
            ranked_ids,
            source_covered,
            citation_covered,
            selection_trace_found,
            uncertain,
            token_cost,
        ) = _route_aware_result(
            plan,
            case,
            route,
            graph_query_plan,
            graph_query_result,
            result,
            limit,
        )
        token_costs.append(token_cost)
        if uncertain == case.expect_uncertain:
            uncertainty_correct += 1
        else:
            case_failures.append(f"{case.id}: uncertainty expected {case.expect_uncertain}")

        if selection_trace_found:
            selection_trace_present += 1

        if not case.expected_skill_ids:
            exclusion_ok = not any(skill_id in ranked_ids for skill_id in case.excluded_skill_ids)
            if exclusion_ok:
                exclusion_passes += 1
            case_results.append(
                EvaluationCaseResult(
                    id=case.id,
                    passed=not case_failures and exclusion_ok,
                    route=str(route.get("route", "")),
                    query_family=str(graph_query_plan.get("query_family", "")),
                    ranked_skill_ids=ranked_ids,
                    vector_only_ranked_skill_ids=vector_only_ids,
                    uncertain=uncertain,
                    citation_covered=True,
                    exclusion_passed=exclusion_ok,
                    selection_trace_present=selection_trace_found,
                    graph_query_plan_present=graph_query_plan.get("status") == "ok",
                    latency_ms=round(latency_ms, 3),
                    token_cost=token_cost,
                    failures=tuple(case_failures),
                )
            )
            failures.extend(case_failures)
            continue
        if set(case.expected_skill_ids) & set(ranked_ids):
            hits += 1
        else:
            case_failures.append(f"{case.id}: expected one of {case.expected_skill_ids}, got {ranked_ids}")
        if _precision_at_1(ranked_ids, case.expected_skill_ids):
            top1_hits += 1
        missing_required = tuple(
            skill_id for skill_id in case.required_skill_ids if skill_id not in ranked_ids
        )
        if missing_required:
            case_failures.append(f"{case.id}: missing required skills {missing_required}")
        unexpected = tuple(
            skill_id for skill_id in case.excluded_skill_ids if skill_id in ranked_ids
        )
        exclusion_ok = not unexpected
        if exclusion_ok:
            exclusion_passes += 1
        else:
            case_failures.append(f"{case.id}: excluded skills were ranked {unexpected}")
        reciprocal_ranks.append(_reciprocal_rank(ranked_ids, case.expected_skill_ids))
        ndcgs.append(_ndcg_at_k(ranked_ids, case.expected_skill_ids, limit))
        if source_covered:
            sourced += 1
        else:
            case_failures.append(f"{case.id}: missing source or section coverage")
        if citation_covered:
            cited += 1
        else:
            case_failures.append(f"{case.id}: missing citation-backed snippets")

        if _is_exact_lookup_case(case):
            exact_cases += 1
            if ranked_ids and ranked_ids[0] in set(case.expected_skill_ids):
                exact_hits += 1
        if _is_alias_lookup_case(case, alias_map):
            alias_cases += 1
            if ranked_ids and ranked_ids[0] in set(case.expected_skill_ids):
                alias_hits += 1

        if graph_query_plan.get("status") == "ok" and graph_query_plan.get("query_family") != "exact_skill_lookup":
            graph_relevant_cases += 1
            if set(case.expected_skill_ids) & set(ranked_ids):
                graph_relevant_hits += 1
            if set(case.expected_skill_ids) & set(vector_only_ids):
                vector_only_graph_hits += 1

        case_results.append(
            EvaluationCaseResult(
                id=case.id,
                passed=not case_failures,
                route=str(route.get("route", "")),
                query_family=str(graph_query_plan.get("query_family", "")),
                ranked_skill_ids=ranked_ids,
                vector_only_ranked_skill_ids=vector_only_ids,
                uncertain=uncertain,
                citation_covered=citation_covered,
                exclusion_passed=exclusion_ok,
                selection_trace_present=selection_trace_found,
                graph_query_plan_present=graph_query_plan.get("status") == "ok",
                latency_ms=round(latency_ms, 3),
                token_cost=token_cost,
                failures=tuple(case_failures),
            )
        )
        failures.extend(case_failures)

    positive_count = max(1, len(positives))
    case_count = max(1, len(cases))
    graph_case_count = max(1, graph_relevant_cases)
    recall_at_k = hits / positive_count
    precision_at_1 = top1_hits / positive_count
    mrr = sum(reciprocal_ranks) / positive_count
    ndcg = sum(ndcgs) / positive_count if ndcgs else 0.0
    source_coverage = sourced / positive_count
    citation_coverage = cited / positive_count
    exclusion_accuracy = exclusion_passes / case_count
    uncertainty_accuracy = uncertainty_correct / max(1, len(cases))
    selection_trace_coverage = selection_trace_present / case_count
    query_plan_coverage = query_plan_present / case_count
    exact_lookup_accuracy = exact_hits / max(1, exact_cases)
    alias_resolution_accuracy = alias_hits / max(1, alias_cases)
    graph_relevant_recall = graph_relevant_hits / graph_case_count if graph_relevant_cases else 0.0
    vector_only_graph_recall = (
        vector_only_graph_hits / graph_case_count if graph_relevant_cases else 0.0
    )
    graph_lift = graph_relevant_recall - vector_only_graph_recall
    mean_token_cost = sum(token_costs) / case_count
    latency_p95 = _p95(latencies)
    passed = (
        precision_at_1 >= recall_threshold
        and
        recall_at_k >= recall_threshold
        and mrr >= mrr_threshold
        and source_coverage >= source_threshold
        and uncertainty_accuracy >= uncertainty_threshold
        and citation_coverage >= source_threshold
        and exclusion_accuracy >= source_threshold
        and selection_trace_coverage >= uncertainty_threshold
        and query_plan_coverage >= uncertainty_threshold
    )
    if graph_relevant_cases and graph_lift < 0.0:
        passed = False
        failures.append(
            f"graph lift failure: graph_recall={graph_relevant_recall:.3f}, "
            f"vector_only_recall={vector_only_graph_recall:.3f}"
        )
    if not passed:
        failures.append(
            "threshold failure: "
            f"precision@1={precision_at_1:.3f}, recall={recall_at_k:.3f}, "
            f"mrr={mrr:.3f}, ndcg={ndcg:.3f}, source={source_coverage:.3f}, "
            f"citation={citation_coverage:.3f}, exclusion={exclusion_accuracy:.3f}, "
            f"trace={selection_trace_coverage:.3f}, plan={query_plan_coverage:.3f}, "
            f"uncertainty={uncertainty_accuracy:.3f}"
        )
    return RetrievalEvaluationReport(
        passed=passed,
        cases=len(cases),
        precision_at_1=round(precision_at_1, 6),
        recall_at_k=round(recall_at_k, 6),
        mean_reciprocal_rank=round(mrr, 6),
        ndcg_at_k=round(ndcg, 6),
        source_coverage=round(source_coverage, 6),
        citation_coverage=round(citation_coverage, 6),
        exclusion_accuracy=round(exclusion_accuracy, 6),
        uncertainty_accuracy=round(uncertainty_accuracy, 6),
        selection_trace_coverage=round(selection_trace_coverage, 6),
        query_plan_coverage=round(query_plan_coverage, 6),
        exact_lookup_accuracy=round(exact_lookup_accuracy, 6),
        alias_resolution_accuracy=round(alias_resolution_accuracy, 6),
        graph_relevant_cases=graph_relevant_cases,
        graph_relevant_recall_at_k=round(graph_relevant_recall, 6),
        vector_only_recall_at_k=round(vector_only_graph_recall, 6),
        graph_lift_recall_at_k=round(graph_lift, 6),
        mean_token_cost_per_selection=round(mean_token_cost, 6),
        latency_ms=round((time.perf_counter() - start) * 1000, 3),
        p95_latency_ms=round(latency_p95, 3),
        case_results=tuple(case_results),
        failures=tuple(failures),
    )


def main(argv: Sequence[str] | None = None) -> int:  # pragma: no cover
    parser = ArgumentParser(description="Evaluate Skills KG retrieval quality.")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET))
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument(
        "--case-filter",
        choices=("all", "promoted_eligible"),
        default="all",
        help="Evaluate all cases or only promoted-eligible release cases.",
    )
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))
    report = evaluate_offline(
        Path(args.dataset),
        limit=args.limit,
        case_filter=args.case_filter,
    )
    print(report.model_dump_json(indent=2))
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
