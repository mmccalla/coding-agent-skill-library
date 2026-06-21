#!/usr/bin/env python3
"""Evaluate Skills KG retrieval against golden queries."""

from __future__ import annotations

import json
import sys
import time
from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import embed_skill_chunks, retrieve_skills_hybrid, skills_config

DEFAULT_DATASET = Path("tests") / "fixtures" / "retrieval_evaluation" / "golden_queries.json"


class EvaluationCase(BaseModel):
    """One golden retrieval query."""

    model_config = ConfigDict(frozen=True)

    id: str = Field(min_length=1)
    query: str = Field(min_length=1)
    expected_skill_ids: tuple[str, ...]
    expect_uncertain: bool = False


class RetrievalEvaluationReport(BaseModel):
    """Aggregate retrieval evaluation metrics."""

    model_config = ConfigDict(frozen=True)

    passed: bool
    cases: int
    recall_at_k: float
    mean_reciprocal_rank: float
    source_coverage: float
    uncertainty_accuracy: float
    latency_ms: float
    failures: tuple[str, ...]


def load_cases(path: Path = DEFAULT_DATASET) -> tuple[EvaluationCase, ...]:
    """Load and validate golden retrieval cases."""

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("retrieval evaluation dataset must be a JSON array")
    return tuple(EvaluationCase.model_validate(item) for item in data)


def _reciprocal_rank(ranked_ids: Sequence[str], expected_ids: Sequence[str]) -> float:
    expected = set(expected_ids)
    for index, skill_id in enumerate(ranked_ids, start=1):
        if skill_id in expected:
            return 1.0 / index
    return 0.0


def evaluate_offline(
    dataset_path: Path = DEFAULT_DATASET,
    limit: int = 3,
    recall_threshold: float = 1.0,
    mrr_threshold: float = 1.0,
    source_threshold: float = 1.0,
    uncertainty_threshold: float = 1.0,
) -> RetrievalEvaluationReport:
    """Run deterministic offline retrieval evaluation."""

    start = time.perf_counter()
    settings = skills_config.load_settings()
    cases = load_cases(dataset_path)
    plan = embed_skill_chunks.build_embedded_repository_load_plan()
    embedder = embed_skill_chunks.DeterministicEmbeddingProvider(
        dimension=settings.neo4j.embedding_dimensions
    )
    positives = [case for case in cases if case.expected_skill_ids]
    hits = 0
    reciprocal_ranks: list[float] = []
    sourced = 0
    uncertainty_correct = 0
    failures: list[str] = []

    for case in cases:
        vector_candidates = embed_skill_chunks.query_vector_candidates(
            plan,
            case.query,
            embedder,
            limit=limit,
        )
        result = retrieve_skills_hybrid.retrieve_hybrid_skills(
            plan,
            case.query,
            vector_candidates=vector_candidates,
            limit=limit,
        )
        ranked_ids = tuple(item.skill_id for item in result.recommendations)
        if result.uncertain == case.expect_uncertain:
            uncertainty_correct += 1
        else:
            failures.append(f"{case.id}: uncertainty expected {case.expect_uncertain}")

        if not case.expected_skill_ids:
            continue
        if set(case.expected_skill_ids) & set(ranked_ids):
            hits += 1
        else:
            failures.append(
                f"{case.id}: expected one of {case.expected_skill_ids}, got {ranked_ids}"
            )
        reciprocal_ranks.append(_reciprocal_rank(ranked_ids, case.expected_skill_ids))
        matching = [
            item for item in result.recommendations if item.skill_id in set(case.expected_skill_ids)
        ]
        if matching and all(item.source_paths and item.section_ids for item in matching):
            sourced += 1
        else:
            failures.append(f"{case.id}: missing source or section coverage")

    positive_count = max(1, len(positives))
    recall_at_k = hits / positive_count
    mrr = sum(reciprocal_ranks) / positive_count
    source_coverage = sourced / positive_count
    uncertainty_accuracy = uncertainty_correct / max(1, len(cases))
    passed = (
        recall_at_k >= recall_threshold
        and mrr >= mrr_threshold
        and source_coverage >= source_threshold
        and uncertainty_accuracy >= uncertainty_threshold
    )
    if not passed:
        failures.append(
            "threshold failure: "
            f"recall={recall_at_k:.3f}, mrr={mrr:.3f}, "
            f"source={source_coverage:.3f}, uncertainty={uncertainty_accuracy:.3f}"
        )
    return RetrievalEvaluationReport(
        passed=passed,
        cases=len(cases),
        recall_at_k=round(recall_at_k, 6),
        mean_reciprocal_rank=round(mrr, 6),
        source_coverage=round(source_coverage, 6),
        uncertainty_accuracy=round(uncertainty_accuracy, 6),
        latency_ms=round((time.perf_counter() - start) * 1000, 3),
        failures=tuple(failures),
    )


def main(argv: Sequence[str] | None = None) -> int:  # pragma: no cover
    parser = ArgumentParser(description="Evaluate Skills KG retrieval quality.")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET))
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))
    report = evaluate_offline(Path(args.dataset), limit=args.limit)
    print(report.model_dump_json(indent=2))
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
