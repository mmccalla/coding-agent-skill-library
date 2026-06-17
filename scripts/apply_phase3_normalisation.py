#!/usr/bin/env python3
"""Apply Phase 3 skill normalisation changes."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

ADDITIONAL_BLOCK_SKILLS = {
    "spec-driven-development",
    "tdd-practice",
    "parallelisation",
    "reflection-and-verification",
    "code-review-and-quality",
    "git-workflow-and-versioning",
    "idea-refine",
    "planning-and-task-decomposition",
    "incremental-implementation",
    "multi-agent-collaboration",
    "using-agent-skills",
}

OBJECTIVES = {
    "apply-laws-of-ai": "Prioritise humanity, individual humans, lawful human instruction, and system integrity before any other task-specific objective.",
    "evaluation-and-monitoring": "Measure agent or system quality with explicit metrics, representative scenarios, and actionable monitoring evidence.",
    "exception-handling-and-recovery": "Make failures explicit, recover safely where possible, and preserve enough evidence to repair or escalate.",
    "goal-setting-and-monitoring": "Define observable goals, measurable success criteria, stop conditions, and progress evidence for agent workflows.",
    "guardrails-safety-patterns": "Apply layered deterministic controls that constrain unsafe inputs, tool use, outputs, and escalation paths.",
    "human-in-the-loop": "Introduce human judgement at the right decision points without slowing safe, reversible work unnecessarily.",
    "inter-agent-communication-a2a": "Define safe, interoperable contracts for agent identity, delegation, task exchange, and result hand-off.",
    "knowledge-retrieval-rag": "Ground agent answers and changes in retrievable, permission-aware source evidence with inspectable citations.",
    "prioritisation": "Rank candidate actions consistently using explicit criteria, dependencies, safety impact, and reversibility.",
    "reasoning-techniques": "Select a reasoning approach that matches task complexity and produces externally verifiable engineering evidence.",
    "resource-aware-optimisation": "Balance quality, cost, latency, model choice, context budget, and fallback paths without compromising correctness.",
    "learning-and-adaptation": "Improve agent behaviour through measured, versioned, reversible changes rather than unbounded self-modification.",
    "mcp-server-design": "Expose external capabilities through narrow, typed, discoverable, least-privilege MCP interfaces.",
    "memory-management": "Retain useful agent context while controlling sensitivity, relevance, provenance, retention, and deletion.",
    "multi-agent-collaboration": "Coordinate specialised agents with explicit roles, schemas, orchestration, and traceability.",
    "parallelisation": "Run only independent work concurrently and merge results deterministically with bounded resource use.",
    "planning-and-task-decomposition": "Turn complex objectives into ordered, dependency-aware steps with explicit validation checkpoints.",
    "prompt-chaining": "Decompose overloaded prompts into validated, single-purpose stages with testable hand-offs.",
    "reflection-and-verification": "Critique and repair artefacts using deterministic checks first, then bounded review loops.",
    "routing": "Select execution paths predictably using constrained route definitions, confidence thresholds, and safe fallbacks.",
    "tool-use-function-calling": "Wrap external capabilities in strict schemas, least-privilege execution, structured observations, and tests.",
    "kg-enabled-rag": "Implement Neo4j-native KG-enabled RAG with provenance-first ingestion, guarded retrieval, grounded answers, and tests.",
    "ontology-and-knowledge-graph-modelling": "Produce semantic graph designs that answer competency questions, validate data, and preserve provenance.",
}


def skill_path(skill_name: str) -> Path:
    matches = list(SKILLS.rglob(f"*/{skill_name}/SKILL.md"))
    if len(matches) != 1:
        raise ValueError(f"Expected one path for {skill_name}, found {len(matches)}")
    return matches[0]


def remove_additional_block(text: str) -> str:
    return re.sub(
        r"\n## Additional (?:guidance|guidelines)\s*\n.*?(?=\n## |\Z)",
        "\n",
        text,
        count=1,
        flags=re.S,
    ).rstrip() + "\n"


def normalise_procedure_headings(text: str) -> str:
    text = re.sub(r"^## Operating procedure$", "## Procedure", text, flags=re.M)
    text = re.sub(r"^## Implementation pattern$", "## Procedure", text, flags=re.M)
    return text


def add_objective(text: str, objective: str) -> str:
    if re.search(r"^## Objective$", text, flags=re.M):
        return text
    if re.search(r"^## Goal$", text, flags=re.M):
        return re.sub(r"^## Goal$", "## Objective", text, count=1, flags=re.M)

    match = re.search(r"^## When to use\s*\n.*?(?=\n## )", text, flags=re.S | re.M)
    if not match:
        raise ValueError("Could not locate When to use section")
    insertion = f"\n## Objective\n\n{objective}\n"
    return text[: match.end()] + insertion + text[match.end() :]


def main() -> int:
    changed: set[Path] = set()

    for path in sorted(SKILLS.rglob("SKILL.md")):
        text = path.read_text(encoding="utf-8")
        updated = normalise_procedure_headings(text)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed.add(path)

    for skill_name in sorted(ADDITIONAL_BLOCK_SKILLS):
        path = skill_path(skill_name)
        text = path.read_text(encoding="utf-8")
        updated = remove_additional_block(text)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed.add(path)

    for skill_name, objective in sorted(OBJECTIVES.items()):
        path = skill_path(skill_name)
        text = path.read_text(encoding="utf-8")
        updated = add_objective(text, objective)
        if updated != text:
            path.write_text(updated, encoding="utf-8")
            changed.add(path)

    print(f"Updated {len(changed)} files")
    for path in sorted(changed):
        print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
