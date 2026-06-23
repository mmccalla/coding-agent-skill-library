#!/usr/bin/env python3
"""Apply Phase 5: split knowledge-graph-rag into progressive-disclosure files."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "data-architecture" / "knowledge-graph-rag"
SKILL = SKILL_DIR / "SKILL.md"
REFERENCE = SKILL_DIR / "reference"


def section(text: str, start: str, end: str | None = None) -> str:
    start_idx = text.index(start)
    end_idx = text.index(end, start_idx) if end else len(text)
    return text[start_idx:end_idx].strip()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    original = SKILL.read_text(encoding="utf-8")
    if "## 0. Agent Execution Contract" not in original:
        print("knowledge-graph-rag already appears to use progressive disclosure; no changes made")
        return 0

    frontmatter_match = re.match(r"---\n(.*?)\n---\n", original, flags=re.S)
    if not frontmatter_match:
        raise ValueError("SKILL.md does not start with YAML frontmatter")

    frontmatter = frontmatter_match.group(1)
    metadata_lines: list[str] = []
    capture = False
    for line in frontmatter.splitlines():
        if line.startswith("version:"):
            capture = True
        if capture:
            metadata_lines.append(line)

    lifecycle_parts = [
        section(original, "## 0. Agent Execution Contract", "## 4. Code Generation Patterns"),
        section(original, "## 6. Security and Reliability Guardrails", "## Verification"),
    ]
    code_patterns = section(original, "## 4. Code Generation Patterns", "## 5. Testing Contract")
    testing_contract = section(original, "## 5. Testing Contract", "## 6. Security and Reliability Guardrails")

    write(REFERENCE / "metadata.yaml", "\n".join(metadata_lines))
    write(
        REFERENCE / "implementation-lifecycle.md",
        "# KG-Enabled RAG Implementation Lifecycle\n\n"
        "Detailed execution guidance for `knowledge-graph-rag/SKILL.md`. Load this file "
        "when implementation, architecture alignment, invariants, lifecycle steps, "
        "security guardrails or done criteria are needed.\n\n"
        + "\n\n".join(lifecycle_parts),
    )
    write(
        REFERENCE / "code-patterns.md",
        "# KG-Enabled RAG Code Patterns\n\n"
        "Detailed code and query patterns for `knowledge-graph-rag/SKILL.md`. Load this "
        "file when generating or reviewing KG-RAG schemas, persistence, retrieval "
        "or evaluator code.\n\n"
        + code_patterns,
    )
    write(
        REFERENCE / "testing-contract.md",
        "# KG-Enabled RAG Testing Contract\n\n"
        "Testing expectations for `knowledge-graph-rag/SKILL.md`. Load this file before "
        "claiming a KG-RAG implementation, refactor or hardening task is complete.\n\n"
        + testing_contract,
    )

    new_skill = """---
name: knowledge-graph-rag
description: Builds, refactors and hardens Neo4j-native KG-enabled RAG with LangGraph, hybrid retrieval, text-to-Cypher, and provenance. Use when implementing GraphRAG, graph-backed retrieval, or guarded text-to-Cypher pipelines.
---

# KG-Enabled RAG

## When to use

Use this skill when building, refactoring, reviewing or hardening Neo4j-native GraphRAG or KG-enabled RAG systems that require graph-aware retrieval, provenance-first ingestion, guarded text-to-Cypher, conceptual schema control or graph-backed answer generation.

Do not use it for generic document RAG, vector-only retrieval, or ontology-only design work where `knowledge-retrieval-rag` or `ontology-and-knowledge-graph-modeling` is sufficient.

## Objective

Implement Neo4j-native KG-enabled RAG with provenance-first ingestion, guarded retrieval, grounded answers, and tests.

## Procedure

1. Inspect the repository for existing graph, retrieval, LLM, prompt, evaluation, Neo4j, LangGraph, Pydantic, FastAPI and OpenTelemetry conventions.
2. Apply the non-negotiable invariants from `reference/implementation-lifecycle.md`: Neo4j-native storage by default, idempotent writes, curated conceptual schema, structured LLM outputs, evidence links and guarded Cypher.
3. Align to the smallest useful vertical slice rather than replacing the repository architecture wholesale.
4. Use `reference/implementation-lifecycle.md` for ingestion, resolution, retrieval, LangGraph orchestration, evaluation, security guardrails, done criteria and anti-patterns.
5. Use `reference/code-patterns.md` only when concrete schemas, Cypher, retriever or evaluator patterns are needed.
6. Use `reference/testing-contract.md` before claiming implementation, refactor or hardening work is complete.
7. Use `reference/metadata.yaml` when stack defaults, activation keywords or audience metadata are needed.

## Non-negotiable invariants

- Prefer Neo4j-native graph, full-text and vector indexes unless an ADR justifies another store.
- Use deterministic identifiers, `MERGE`/upsert semantics and transaction boundaries for repeatable ingestion.
- Never expose raw database metadata, embeddings, audit fields or unrestricted schema details directly to an LLM.
- Validate all LLM outputs with typed schemas and reject, repair or quarantine invalid extractions.
- Link every decision-relevant fact, relationship, claim, summary, answer and evaluation result to source evidence.
- Parameterise Cypher and default user-facing text-to-Cypher to read-only, bounded queries.

## Recommended architecture

Keep responsibilities separated: configuration, domain models, ingestion, graph persistence, retrieval, orchestration, generation, evaluation, observability, security, API and CLI. API layers should not contain business logic.

## Reference files

- `reference/metadata.yaml` — version, audience, activation keywords and default stack metadata.
- `reference/implementation-lifecycle.md` — detailed invariants, repository architecture, lifecycle steps, security guardrails, done criteria and anti-patterns.
- `reference/code-patterns.md` — conceptual schema config, Pydantic extraction models, idempotent Neo4j persistence, local/global search and evaluator examples.
- `reference/testing-contract.md` — required unit, integration, end-to-end and evaluation tests.

## Related skills

- `knowledge-retrieval-rag` — generic document-grounded RAG patterns.
- `ontology-and-knowledge-graph-modeling` — semantic modelling and competency questions.
- `data-lineage-and-provenance` — traceability for graph facts, retrieval evidence and generated answers.
- `guardrails-safety-patterns` — validation, policy and tool-use controls.
- `evaluation-and-monitoring` — retrieval, answer and operational quality measurement.

## Verification

- [ ] Relevant reference files were loaded for the task scope.
- [ ] Files changed reported.
- [ ] Commands and validations run with results stated.
- [ ] Behaviour intentionally changed described.
- [ ] Assumptions and residual risks or follow-up work stated.
"""

    write(SKILL, new_skill)
    print("Updated knowledge-graph-rag progressive disclosure files")
    for path in [
        SKILL,
        REFERENCE / "metadata.yaml",
        REFERENCE / "implementation-lifecycle.md",
        REFERENCE / "code-patterns.md",
        REFERENCE / "testing-contract.md",
    ]:
        print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
