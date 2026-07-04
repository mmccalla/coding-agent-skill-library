---
name: krag-system-design
description: Design compact, production-sensible Knowledge Graph-Augmented Retrieval systems. Use when defining KRAG or GraphRAG architecture, graph role, retrieval strategy, provenance model, backlog, or technical design tasks.
aliases:
  - krag system design
  - graphrag system design
---

# KRAG System Design

## When to use

Use when designing the end-to-end architecture, graph role, provenance model, retrieval role or implementation slices for a KRAG or GraphRAG system.

## Objective

Design a Knowledge Graph-Augmented Retrieval system where the graph materially improves retrieval, reasoning, provenance, navigation, governance, or explainability.

## Procedure

1. Classify the primary question class and intended graph role.
2. Choose storage, reasoning, and evidence models explicitly.
3. Outline the reference architecture from ingestion through evaluation.
4. State non-negotiable invariants for evidence, schema, and writes.
5. Define retrieval strategy, ranking signals, and abstention rules.
6. Produce architecture summary, schema outline, evaluation gates, and thin-slice backlog.

## Core decisions

Make these explicit before designing:

1. **Question class**: lookup, semantic search, relationship traversal, impact analysis, regulatory traceability, root-cause analysis, summarisation, or cross-document reasoning.
2. **Graph role**: resource catalogue, semantic index, evidence graph, domain graph, control graph, lineage graph, or operational twin.
3. **Storage pattern**: property graph, RDF/OWL, hybrid, graph-native vector index, or external vector store.
4. **Reasoning level**: deterministic traversal/rules, LLM-assisted inference, probabilistic ranking, or external ontology reasoning.
5. **Evidence model**: every answerable claim must trace to source spans, tables, records, or authoritative systems.

## Reference architecture

Use this minimal component model unless the repository already has one:

- **Ingestion**: parse source, preserve structure, create evidence anchors, extract candidate entities/relations/claims.
- **Normalisation**: canonicalise identifiers, deduplicate entities, map to ontology/schema, score confidence.
- **Graph store**: persist resources, evidence, entities, concepts, relationships, provenance, versions, and constraints.
- **Retrieval planner**: classify question, select graph/vector/keyword/hybrid strategy, generate safe graph queries.
- **Ranker**: combine semantic similarity, graph proximity, source authority, recency, and confidence.
- **Answerer**: synthesise grounded response with citations, uncertainty, and abstention when support is weak.
- **Evaluator**: test retrieval, grounding, graph quality, answer quality, latency, cost, safety, and drift.

## Non-negotiable invariants

- Do not create triples without source evidence.
- Do not store only chunks when document structure, claims, tables, sections, or entities are needed.
- Do not let LLM-generated graph writes bypass schema validation.
- Do not conflate ontology classes, instance entities, concepts, claims, and evidence spans.
- Do not answer from graph neighbourhood alone; require supporting evidence or explicit rule-derived facts.

## Output format

Return:

1. Architecture summary.
2. Graph schema outline.
3. Retrieval strategy.
4. Evaluation gates.
5. Key trade-offs and risks.
6. Implementation backlog in thin vertical slices.

## Related skills

- `knowledge-graph-rag` — Neo4j-native KG-backed retrieval implementation guidance
- `ontology-and-knowledge-graph-modeling` — ontology and semantic graph design
- `krag-ingestion-graph-construction` — ingestion and evidence graph construction
- `krag-retrieval-answering` — retrieval planning, ranking and answer synthesis
- `krag-evaluation-governance` — KRAG-specific evaluation and governance

## References

- [Neo4j documentation](https://neo4j.com/docs/)
- [W3C RDF](https://www.w3.org/RDF/)
- [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework)

## Verification

- [ ] Architecture, graph role and retrieval strategy are explicit.
- [ ] Evidence and provenance invariants are stated.
- [ ] Evaluation gates and implementation slices are defined.
