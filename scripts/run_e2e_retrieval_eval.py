#!/usr/bin/env python3
"""Run realistic end-to-end Skills KG retrieval evaluation and emit an audit report."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.evaluate_skill_retrieval import (
    DEFAULT_DATASET,
    EvaluationCaseResult,
    evaluate_offline,
    filter_cases_by_promotion,
    load_cases,
    load_promoted_skill_ids,
)
from scripts.krag_cutover_acceptance import run_cutover_acceptance

REPO_ROOT = Path(__file__).resolve().parents[1]
REALISTIC_DATASET = (
    REPO_ROOT / "tests" / "fixtures" / "retrieval_evaluation" / "realistic_queries.json"
)


@dataclass(frozen=True)
class EvalArmSummary:
    name: str
    cases: int
    failed: int
    precision_at_1: float
    recall_at_k: float
    citation_coverage: float
    graph_lift_recall_at_k: float
    rank_failures: tuple[dict[str, object], ...]


def _rank_failures(
    case_results: tuple[EvaluationCaseResult, ...],
    cases_by_id: dict[str, object],
) -> tuple[dict[str, object], ...]:
    failures: list[dict[str, object]] = []
    for result in case_results:
        if result.passed:
            continue
        if not any("expected one of" in failure for failure in result.failures):
            continue
        case = cases_by_id[result.id]
        failures.append(
            {
                "id": result.id,
                "query": getattr(case, "query", ""),
                "expected_skill_ids": list(getattr(case, "expected_skill_ids", ())),
                "ranked_skill_ids": list(result.ranked_skill_ids),
                "failures": list(result.failures),
            }
        )
    return tuple(failures)


def _summarise_arm(name: str, report: object, cases_by_id: dict[str, object]) -> EvalArmSummary:
    failed = sum(1 for result in report.case_results if not result.passed)
    return EvalArmSummary(
        name=name,
        cases=report.cases,
        failed=failed,
        precision_at_1=report.precision_at_1,
        recall_at_k=report.recall_at_k,
        citation_coverage=report.citation_coverage,
        graph_lift_recall_at_k=report.graph_lift_recall_at_k,
        rank_failures=_rank_failures(report.case_results, cases_by_id),
    )


def run_realistic_e2e(
    *,
    skills_root: Path,
    golden_dataset: Path = DEFAULT_DATASET,
    realistic_dataset: Path = REALISTIC_DATASET,
) -> dict[str, object]:
    """Run release, full-corpus, realistic-confuser and cutover acceptance arms."""

    promoted_ids = load_promoted_skill_ids(skills_root)
    golden_cases = load_cases(golden_dataset)
    cases_by_id = {case.id: case for case in golden_cases}

    release_report = evaluate_offline(
        golden_dataset,
        limit=3,
        recall_threshold=0.0,
        mrr_threshold=0.0,
        source_threshold=0.0,
        uncertainty_threshold=0.0,
        case_filter="promoted_eligible",
        skills_root=skills_root,
    )
    full_report = evaluate_offline(
        golden_dataset,
        limit=3,
        recall_threshold=0.0,
        mrr_threshold=0.0,
        source_threshold=0.0,
        uncertainty_threshold=0.0,
        case_filter="all",
        skills_root=skills_root,
    )
    realistic_cases = load_cases(realistic_dataset) if realistic_dataset.is_file() else ()
    realistic_report = None
    if realistic_cases:
        realistic_report = evaluate_offline(
            realistic_dataset,
            limit=3,
            recall_threshold=0.0,
            mrr_threshold=0.0,
            source_threshold=0.0,
            uncertainty_threshold=0.0,
            case_filter="all",
            skills_root=skills_root,
        )

    cutover = run_cutover_acceptance(
        REPO_ROOT / "tests/fixtures/retrieval_evaluation/smoke_queries_promoted.json",
        limit=3,
    )

    payload: dict[str, object] = {
        "promoted_skill_count": len(promoted_ids),
        "golden_case_count": len(golden_cases),
        "release_eligible_case_count": len(
            filter_cases_by_promotion(golden_cases, promoted_ids, case_filter="promoted_eligible")
        ),
        "release_arm": asdict(_summarise_arm("release", release_report, cases_by_id)),
        "full_corpus_arm": asdict(_summarise_arm("full", full_report, cases_by_id)),
        "cutover_acceptance_passed": cutover.passed,
        "cutover_evaluation": cutover.evaluation.model_dump(),
    }
    if realistic_report is not None:
        realistic_by_id = {case.id: case for case in realistic_cases}
        payload["realistic_confuser_arm"] = asdict(
            _summarise_arm("realistic", realistic_report, realistic_by_id)
        )
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run realistic Skills KG e2e retrieval evaluation."
    )
    parser.add_argument("--skills-root", default=str(REPO_ROOT / "skills"))
    parser.add_argument("--golden-dataset", default=str(DEFAULT_DATASET))
    parser.add_argument("--realistic-dataset", default=str(REALISTIC_DATASET))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = run_realistic_e2e(
        skills_root=Path(args.skills_root),
        golden_dataset=Path(args.golden_dataset),
        realistic_dataset=Path(args.realistic_dataset),
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        release = report["release_arm"]
        full = report["full_corpus_arm"]
        print("Skills KG realistic e2e evaluation")
        print(f"Promoted skills: {report['promoted_skill_count']}")
        print(
            f"Release arm: cases={release['cases']} failed={release['failed']} "
            f"precision@1={release['precision_at_1']:.3f} recall@k={release['recall_at_k']:.3f}"
        )
        print(
            f"Full corpus: cases={full['cases']} failed={full['failed']} "
            f"precision@1={full['precision_at_1']:.3f} recall@k={full['recall_at_k']:.3f}"
        )
        print(f"Cutover acceptance: {'PASS' if report['cutover_acceptance_passed'] else 'FAIL'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
