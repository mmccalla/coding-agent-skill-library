#!/usr/bin/env python3
"""Run the Skills KG pre-ingest CI gate for skill changes."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import (
    evaluate_skill_retrieval,
    load_skills_neo4j,
    skills_trust_metrics,
    validate_eval_corpus,
    validate_skill_trust,
    validate_skills_graph,
    validate_skills_ontology,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILLS_ROOT = REPO_ROOT / "skills"
DEFAULT_ONTOLOGY_GRAPH = REPO_ROOT / "skills_docs" / "ontology" / "skills.ttl"
DEFAULT_PROMOTED_SMOKE_DATASET = (
    REPO_ROOT / "tests" / "fixtures" / "retrieval_evaluation" / "smoke_queries_promoted.json"
)
EVAL_DIR = REPO_ROOT / "tests" / "fixtures" / "retrieval_evaluation"
DELTA_EVAL_DATASETS = (
    EVAL_DIR / "coverage_queries.json",
    EVAL_DIR / "realistic_queries.json",
    EVAL_DIR / "query_catalog.json",
    EVAL_DIR / "smoke_queries_promoted.json",
)


@dataclass(frozen=True)
class GateStepResult:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class IngestGateReport:
    passed: bool
    steps: tuple[GateStepResult, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "steps": [asdict(step) for step in self.steps],
        }


def trust_reports_for_skills_root(skills_root: Path) -> list[validate_skill_trust.TrustReport]:
    paths = [str(path) for path in sorted(skills_root.rglob("SKILL.md"))]
    return validate_skill_trust.validate_skill_trust_paths(paths)


def record_trust_gate_metrics(reports: list[validate_skill_trust.TrustReport]) -> None:
    for report in reports:
        if validate_skill_trust.ci_ingest_gate_passed(report):
            continue
        layer_result = report.layers["L2_security"]
        details = layer_result.details
        violations = details.get("violations", [])
        if isinstance(violations, list) and violations:
            for violation in violations:
                if isinstance(violation, dict):
                    reason = str(
                        violation.get("rule_id") or violation.get("message") or "violation"
                    )
                    skills_trust_metrics.record_trust_rejection(layer="L2_security", reason=reason)
                    continue
        skills_trust_metrics.record_trust_rejection(
            layer="L2_security", reason="security_gate_failed"
        )


def discover_changed_skill_names(
    *,
    base_ref: str | None = None,
    changed_skill_names: frozenset[str] | None = None,
) -> frozenset[str]:
    """Return skill folder names for changed `skills/*/SKILL.md` paths."""

    if changed_skill_names is not None:
        return changed_skill_names

    ref = base_ref or os.environ.get("DELTA_EVAL_BASE_REF")
    if not ref:
        return frozenset()

    result = subprocess.run(
        ["git", "diff", "--name-only", f"{ref}...", "--", "skills/"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return frozenset()

    names: set[str] = set()
    for line in result.stdout.splitlines():
        parts = Path(line.strip()).parts
        if len(parts) >= 2 and parts[0] == "skills" and parts[-1] == "SKILL.md":
            names.add(parts[1])
    return frozenset(names)


def build_delta_eval_cases(skill_names: frozenset[str]) -> list[dict[str, object]]:
    """Collect evaluation cases that exercise any of the changed skills."""

    if not skill_names:
        return []

    selected: dict[str, dict[str, object]] = {}
    for dataset_path in DELTA_EVAL_DATASETS:
        if not dataset_path.is_file():
            continue
        payload = json.loads(dataset_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            continue
        for raw in payload:
            if not isinstance(raw, dict):
                continue
            case = dict(raw)
            if case.get("expect_uncertain"):
                continue
            tagged_skill_names = {
                str(skill_id).removeprefix("skill:")
                for skill_id in (
                    *(
                        skill_id
                        for skill_id in case.get("expected_skill_ids", ())
                        if isinstance(skill_id, str)
                    ),
                    *(
                        skill_id
                        for skill_id in case.get("required_skill_ids", ())
                        if isinstance(skill_id, str)
                    ),
                )
            }
            if tagged_skill_names & skill_names:
                selected[str(case.get("id", ""))] = case
    return list(selected.values())


def run_delta_eval_step(
    *,
    skills_root: Path,
    retrieval_limit: int,
    base_ref: str | None = None,
    changed_skill_names: frozenset[str] | None = None,
) -> GateStepResult:
    """Run retrieval eval only for cases tied to changed skills."""

    skill_names = discover_changed_skill_names(
        base_ref=base_ref,
        changed_skill_names=changed_skill_names,
    )
    if not skill_names:
        return GateStepResult(
            name="delta_eval_changed_skills",
            passed=True,
            detail="no changed skills; skipped",
        )

    cases = build_delta_eval_cases(skill_names)
    if not cases:
        return GateStepResult(
            name="delta_eval_changed_skills",
            passed=True,
            detail=f"skills={sorted(skill_names)}; no matching eval cases",
        )

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as handle:
        json.dump(cases, handle, indent=2)
        handle.write("\n")
        temp_path = Path(handle.name)

    try:
        report = evaluate_skill_retrieval.evaluate_offline(
            temp_path,
            limit=retrieval_limit,
            skills_root=skills_root,
            source_threshold=0.5,
            recall_threshold=1.0,
            mrr_threshold=1.0,
        )
    finally:
        temp_path.unlink(missing_ok=True)

    rank_failures = [
        result.id
        for result in report.case_results
        if any("expected one of" in failure for failure in result.failures)
    ]
    passed = report.precision_at_1 >= 1.0 and not rank_failures
    return GateStepResult(
        name="delta_eval_changed_skills",
        passed=passed,
        detail=(
            f"skills={sorted(skill_names)}; cases={report.cases}; "
            f"precision@1={report.precision_at_1:.3f}; rank_failures={len(rank_failures)}"
        ),
    )


def record_promotion_metrics(records: dict[str, object]) -> None:
    skills = records.get("skills")
    if not isinstance(skills, list):
        return
    statuses = Counter(
        str(skill.get("promotion_status", "unknown")) for skill in skills if isinstance(skill, dict)
    )
    skills_trust_metrics.record_promotion_quarantine(
        reason="incomplete_mapping",
        count=statuses.get("quarantined", 0),
    )
    skills_trust_metrics.record_trust_rejection(
        layer="promotion",
        reason="rejected",
        count=statuses.get("rejected", 0),
    )


def run_ingest_gate(
    *,
    skills_root: Path = DEFAULT_SKILLS_ROOT,
    ontology_graph: Path = DEFAULT_ONTOLOGY_GRAPH,
    promoted_smoke_dataset: Path = DEFAULT_PROMOTED_SMOKE_DATASET,
    retrieval_limit: int = 3,
    delta_base_ref: str | None = None,
    changed_skill_names: frozenset[str] | None = None,
) -> IngestGateReport:
    """Execute the Phase 9 ingest gate pipeline."""

    steps: list[GateStepResult] = []

    trust_reports = trust_reports_for_skills_root(skills_root)
    record_trust_gate_metrics(trust_reports)
    l2_failures = [
        report.skill_path
        for report in trust_reports
        if not validate_skill_trust.ci_ingest_gate_passed(report)
    ]
    steps.append(
        GateStepResult(
            name="validate_skill_trust_l2",
            passed=not l2_failures,
            detail=(
                f"validated {len(trust_reports)} skill file(s); L2 failures={len(l2_failures)}"
            ),
        )
    )
    if l2_failures:
        return IngestGateReport(passed=False, steps=tuple(steps))

    graph_records = validate_skills_graph.build_records_from_skills(skills_root)
    graph_result = validate_skills_graph.validate_graph_records(graph_records)
    record_promotion_metrics(graph_records)
    steps.append(
        GateStepResult(
            name="validate_skills_graph",
            passed=graph_result.valid,
            detail=(
                "graph connectivity passed"
                if graph_result.valid
                else f"errors={len(graph_result.errors)}"
            ),
        )
    )
    if not graph_result.valid:
        return IngestGateReport(passed=False, steps=tuple(steps))

    ontology_result = validate_skills_ontology.validate_skills_ontology(
        ontology_graph,
        include_instances=True,
    )
    steps.append(
        GateStepResult(
            name="validate_skills_ontology_shacl",
            passed=ontology_result.valid,
            detail="SHACL validation with governed instances passed"
            if ontology_result.valid
            else "SHACL validation failed",
        )
    )
    if not ontology_result.valid:
        return IngestGateReport(passed=False, steps=tuple(steps))

    corpus_result = validate_eval_corpus.validate_all(skills_root=skills_root)
    steps.append(
        GateStepResult(
            name="validate_eval_corpus",
            passed=corpus_result.valid,
            detail="tiered evaluation corpora valid"
            if corpus_result.valid
            else f"errors={len(corpus_result.errors)}",
        )
    )
    if not corpus_result.valid:
        return IngestGateReport(passed=False, steps=tuple(steps))

    delta_step = run_delta_eval_step(
        skills_root=skills_root,
        retrieval_limit=retrieval_limit,
        base_ref=delta_base_ref,
        changed_skill_names=changed_skill_names,
    )
    steps.append(delta_step)
    if not delta_step.passed:
        return IngestGateReport(passed=False, steps=tuple(steps))

    evaluation = evaluate_skill_retrieval.evaluate_offline(
        promoted_smoke_dataset,
        limit=retrieval_limit,
        skills_root=skills_root,
        source_threshold=0.5,
    )
    steps.append(
        GateStepResult(
            name="evaluate_promoted_retrieval_smoke",
            passed=evaluation.passed,
            detail=(
                f"cases={evaluation.cases}, precision@1={evaluation.precision_at_1:.3f}, "
                f"recall@k={evaluation.recall_at_k:.3f}"
            ),
        )
    )
    if not evaluation.passed:
        return IngestGateReport(passed=False, steps=tuple(steps))

    load_plan = load_skills_neo4j.build_load_plan(graph_records)
    dry_run = load_skills_neo4j.dry_run_report(load_plan)
    node_lines = [line for line in dry_run.splitlines() if line.startswith("- ") and ": " in line]
    steps.append(
        GateStepResult(
            name="dry_run_load",
            passed=bool(node_lines),
            detail=f"dry-run produced {len(node_lines)} node/relationship summary line(s)",
        )
    )

    passed = all(step.passed for step in steps)
    return IngestGateReport(passed=passed, steps=tuple(steps))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Skills KG pre-ingest CI gate.")
    parser.add_argument("--skills-root", default=str(DEFAULT_SKILLS_ROOT))
    parser.add_argument("--ontology-graph", default=str(DEFAULT_ONTOLOGY_GRAPH))
    parser.add_argument("--promoted-smoke-dataset", default=str(DEFAULT_PROMOTED_SMOKE_DATASET))
    parser.add_argument("--retrieval-limit", type=int, default=3)
    parser.add_argument(
        "--delta-base-ref",
        default=os.environ.get("DELTA_EVAL_BASE_REF"),
        help="Git ref for change-scoped delta eval (e.g. origin/main).",
    )
    parser.add_argument(
        "--changed-skill",
        action="append",
        default=[],
        help="Force delta eval for a skill folder name (repeatable).",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON report")
    args = parser.parse_args(argv)

    forced_skills = frozenset(args.changed_skill) if args.changed_skill else None
    report = run_ingest_gate(
        skills_root=Path(args.skills_root),
        ontology_graph=Path(args.ontology_graph),
        promoted_smoke_dataset=Path(args.promoted_smoke_dataset),
        retrieval_limit=args.retrieval_limit,
        delta_base_ref=args.delta_base_ref,
        changed_skill_names=forced_skills,
    )

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        status = "PASS" if report.passed else "FAIL"
        print(f"{status}: Skills KG ingest gate")
        for step in report.steps:
            marker = "ok" if step.passed else "FAIL"
            print(f"- [{marker}] {step.name}: {step.detail}")
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
