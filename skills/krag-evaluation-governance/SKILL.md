---
name: krag-evaluation-governance
description: Evaluate and govern KRAG systems. Use when defining quality gates, test design, observability, safety, compliance, drift, cost, latency, grounding, and release readiness.
aliases:
  - krag evaluation governance
  - graphrag evaluation
  - krag quality gates
---

# KRAG Evaluation and Governance

## When to use

Use when defining quality gates, test sets, observability, governance controls, release criteria or failure policies for a KRAG system.

## Objective

Prove that the KRAG system retrieves the right evidence, constructs a valid graph, answers faithfully, and fails safely.

## Procedure

1. Define evaluation layers (source, graph, retrieval, answer, operational, governance).
2. Build the minimum test set covering lookup, traversal, synthesis, conflict, and abstention.
3. Establish quality gates and acceptance thresholds per layer.
4. Instrument observability for query intent, strategy, evidence, latency, and cost.
5. Run release checks and block promotion when gates fail.
6. Record remediation actions and governance evidence for audit.

## Evaluation layers

1. **Source quality**: parser coverage, structure preservation, extraction errors, checksum/version integrity.
2. **Graph quality**: schema conformance, duplicate rate, orphan rate, evidence coverage, relationship validity, entity-resolution precision/recall.
3. **Retrieval quality**: recall@k, precision@k, MRR/NDCG, graph path relevance, hybrid ranking lift over vector-only baseline.
4. **Answer quality**: groundedness, citation accuracy, completeness, contradiction handling, abstention quality.
5. **Operational quality**: latency, cost, index freshness, failure recovery, observability, access control, audit logs.
6. **Governance quality**: data classification, retention, lineage, policy-as-code checks, human approval for high-impact graph writes.

## Minimum test set

Create tests for:

- exact lookup
- vague semantic search
- multi-hop graph traversal
- impact analysis
- cross-document synthesis
- conflicting evidence
- stale evidence
- unauthorised data access
- missing evidence abstention
- regression against known gold answers

## Quality gates

Block release when:

- material claims lack evidence anchors
- LLM-generated facts bypass validation
- retrieval is not better than vector-only baseline for graph-relevant questions
- citations do not support the answer
- protected data appears in unauthorised retrieval results
- graph schema migrations are untested
- entity resolution creates unsafe merges

## Observability

Log per query:

- question type
- retrieval strategy
- graph queries and vector queries
- retrieved evidence IDs
- ranking scores
- answer citations
- latency and token/cost metrics
- abstention reason
- user feedback and evaluator scores

## Output format

Return evaluation plan, metrics, acceptance thresholds, test cases, release gates, monitoring signals, and remediation actions.

## Related skills

- `evaluation-and-monitoring` — generic evaluation and monitoring discipline
- `guardrails-safety-patterns` — safety and policy controls
- `krag-system-design` — architecture and backlog slices to evaluate
- `krag-ingestion-graph-construction` — graph quality and ingestion tests
- `krag-retrieval-answering` — retrieval and answer quality tests

## Verification

- [ ] Retrieval, graph, answer and operational quality gates are explicit.
- [ ] Release blockers and governance controls are defined.
- [ ] Observability and regression test expectations are stated.
