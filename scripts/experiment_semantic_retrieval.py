#!/usr/bin/env python3
"""Measure production BGE-M3 vs deterministic embeddings on challenge cases.

PR CI does not run this script. Use it for local/production measurement only.
"""

from __future__ import annotations

import json
import sys
from argparse import ArgumentParser
from collections.abc import Sequence
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import embed_skill_chunks, load_skills_neo4j, retrieve_skills_hybrid
from scripts.evaluate_skill_retrieval import load_cases

DEFAULT_DATASET = (
    Path("tests") / "fixtures" / "retrieval_evaluation" / "semantic_challenge_queries.json"
)


def _build_embedder(
    *,
    provider: str,
    dimensions: int,
    ollama_model: str,
    ollama_url: str,
) -> embed_skill_chunks.EmbeddingProvider:
    if provider == "ollama-bge-m3":
        return embed_skill_chunks.BgeM3OllamaEmbeddingProvider(
            model=ollama_model,
            base_url=ollama_url,
            dimension=dimensions,
        )
    return embed_skill_chunks.DeterministicEmbeddingProvider(dimension=dimensions)


def _unique_skill_ids(candidates: Sequence[embed_skill_chunks.VectorCandidate]) -> tuple[str, ...]:
    skill_ids: list[str] = []
    for candidate in candidates:
        if candidate.skill_id and candidate.skill_id not in skill_ids:
            skill_ids.append(candidate.skill_id)
    return tuple(skill_ids)


def evaluate_semantic_experiment(
    *,
    dataset_path: Path,
    skills_root: Path,
    provider: str,
    dimensions: int,
    limit: int,
    ollama_model: str,
    ollama_url: str,
) -> dict[str, object]:
    """Return vector-only and hybrid retrieval metrics for semantic challenge cases."""

    cases = load_cases(dataset_path)
    embedder = _build_embedder(
        provider=provider,
        dimensions=dimensions,
        ollama_model=ollama_model,
        ollama_url=ollama_url,
    )
    base_plan = load_skills_neo4j.build_repository_load_plan(skills_root)
    plan = embed_skill_chunks.embed_retrieval_units(base_plan, embedder)

    positive_cases = [case for case in cases if case.expected_skill_ids]
    negative_cases = [case for case in cases if not case.expected_skill_ids]
    vector_hits = 0
    hybrid_hits = 0
    hybrid_top1_hits = 0
    uncertainty_hits = 0
    case_results: list[dict[str, object]] = []

    for case in cases:
        vector_candidates = embed_skill_chunks.query_vector_candidates(
            plan,
            case.query,
            embedder,
            limit=limit,
        )
        vector_ranked_ids = _unique_skill_ids(vector_candidates)[:limit]
        hybrid = retrieve_skills_hybrid.retrieve_hybrid_skills(
            plan,
            case.query,
            vector_candidates,
            limit=limit,
        )
        hybrid_ranked_ids = tuple(
            recommendation.skill_id for recommendation in hybrid.recommendations
        )
        expected_ids = set(case.expected_skill_ids)

        vector_hit = bool(expected_ids & set(vector_ranked_ids))
        hybrid_hit = bool(expected_ids & set(hybrid_ranked_ids))
        hybrid_top1_hit = bool(hybrid_ranked_ids and hybrid_ranked_ids[0] in expected_ids)
        uncertainty_hit = case.expect_uncertain == hybrid.uncertain

        if case.expected_skill_ids:
            vector_hits += int(vector_hit)
            hybrid_hits += int(hybrid_hit)
            hybrid_top1_hits += int(hybrid_top1_hit)
        else:
            uncertainty_hits += int(uncertainty_hit)

        case_results.append(
            {
                "id": case.id,
                "query": case.query,
                "expected_skill_ids": list(case.expected_skill_ids),
                "vector_ranked_skill_ids": list(vector_ranked_ids),
                "hybrid_ranked_skill_ids": list(hybrid_ranked_ids),
                "uncertain": hybrid.uncertain,
                "vector_hit": vector_hit,
                "hybrid_hit": hybrid_hit,
                "hybrid_top1_hit": hybrid_top1_hit,
                "uncertainty_hit": uncertainty_hit,
            }
        )

    positive_count = max(1, len(positive_cases))
    negative_count = max(1, len(negative_cases))
    return {
        "provider": provider,
        "embedding_provider": embedder.provider_name,
        "embedding_dimensions": embedder.dimension,
        "dataset": str(dataset_path),
        "cases": len(cases),
        "positive_cases": len(positive_cases),
        "negative_cases": len(negative_cases),
        "vector_recall_at_k": round(vector_hits / positive_count, 6),
        "hybrid_recall_at_k": round(hybrid_hits / positive_count, 6),
        "hybrid_precision_at_1": round(hybrid_top1_hits / positive_count, 6),
        "ood_uncertainty_accuracy": round(uncertainty_hits / negative_count, 6),
        "case_results": case_results,
    }


def main(argv: Sequence[str] | None = None) -> int:  # pragma: no cover
    parser = ArgumentParser(description="Run semantic retrieval embedding experiment.")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET))
    parser.add_argument("--skills-root", default="skills")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument(
        "--provider",
        choices=("deterministic", "ollama-bge-m3"),
        default="deterministic",
    )
    parser.add_argument("--embedding-dimensions", type=int, default=1024)
    parser.add_argument("--ollama-model", default="bge-m3:567m")
    parser.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    parser.add_argument("--output", help="Optional JSON report path.")
    args = parser.parse_args(list(sys.argv[1:] if argv is None else argv))

    report = evaluate_semantic_experiment(
        dataset_path=Path(args.dataset),
        skills_root=Path(args.skills_root),
        provider=args.provider,
        dimensions=args.embedding_dimensions,
        limit=args.limit,
        ollama_model=args.ollama_model,
        ollama_url=args.ollama_url,
    )
    payload = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(f"{payload}\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":
    sys.exit(main())
