---
name: krag-retrieval-answering
description: Implement KRAG retrieval, graph traversal, query planning, hybrid search, answer synthesis, citations, and abstention. Use when building or debugging graph/vector/keyword retrieval and enterprise question answering.
aliases:
  - krag retrieval answering
  - graphrag retrieval
  - graph retrieval answering
---

# KRAG Retrieval and Answering

## When to use

Use when building or debugging the query planner, graph traversal, hybrid ranking, answer synthesis, citation formatting or abstention logic of a KRAG system.

## Objective

Answer questions using graph structure plus grounded evidence, not unverified model memory.

## Procedure

1. Classify the question (lookup, semantic discovery, traversal, impact analysis, synthesis).
2. Select the smallest sufficient retrieval strategy (graph, vector, keyword, hybrid, iterative).
3. Plan and execute bounded, read-only graph queries where applicable.
4. Rank candidates using semantic, graph proximity, authority, recency, and confidence signals.
5. Synthesise an answer with citations, uncertainty, and abstention when evidence is weak.

## Retrieval planner

Classify the question before querying:

- **Entity lookup**: find canonical entity and known attributes.
- **Semantic discovery**: retrieve relevant evidence by embedding and keyword search.
- **Relationship traversal**: follow typed paths between entities, controls, obligations, systems, teams, outcomes, risks, or processes.
- **Impact analysis**: expand from a changed entity across dependency, ownership, control, obligation, data-flow, and outcome relationships.
- **Global synthesis**: summarise communities, themes, or cross-document patterns.

## Strategy selection

Use the smallest sufficient strategy:

1. **Graph-first** for known entities, dependency paths, ownership, lineage, obligations, controls, and impact questions.
2. **Vector-first** for vague, natural-language, or exploratory questions.
3. **Keyword-first** for exact IDs, policy clauses, regulation names, control IDs, and error codes.
4. **Hybrid** when recall matters or when the user asks a broad enterprise question.
5. **Iterative retrieval** when first-pass evidence is incomplete, contradictory, or too generic.

## Ranking signals

Combine:

- semantic similarity
- exact match strength
- graph distance and path type
- source authority
- evidence confidence
- recency/version
- entity resolution confidence
- policy or ontology priority

## Answer synthesis rules

- Separate facts, inferences, and recommendations.
- Cite source evidence for every material claim.
- Explain graph paths used for impact or traceability questions.
- State uncertainty where evidence is incomplete, weak, stale, or conflicting.
- Abstain or ask for missing source data when the graph cannot support the answer.
- Never invent relationships to close a reasoning gap.

## Enterprise impact template

For questions such as “What customer outcomes, controls, teams and regulatory obligations are affected if we retire this platform?” retrieve:

1. target platform and aliases
2. upstream/downstream systems and data flows
3. supported products, journeys, services, and customer outcomes
4. owning, operating, support, risk, and compliance teams
5. linked controls, risks, policies, regulations, and obligations
6. current evidence, confidence, gaps, and unresolved dependencies

## Output format

Return retrieval plan, queries/pseudocode, evidence set, answer, citations, uncertainty, and follow-up data gaps.

## Related skills

- `knowledge-graph-rag` — Neo4j-native graph retrieval implementation
- `knowledge-retrieval-rag` — generic document-grounded retrieval discipline
- `krag-system-design` — architecture and retrieval role design
- `krag-evaluation-governance` — retrieval and answer quality gates

## References

- Neo4j documentation — querying and GraphRAG patterns: https://neo4j.com/docs/
- Retrieval-Augmented Generation (Lewis et al.): https://ai.meta.com/research/publications/retrieval-augmented-generation-for-knowledge-intensive-nlp-tasks/

## Verification

- [ ] Retrieval strategy selection is explicit and bounded.
- [ ] Answers separate facts, inferences and recommendations.
- [ ] Every material claim is grounded in cited evidence or abstained.
