# KRAG v2 Evaluation and Governance Contract

## Objective

Prove that the refactored KRAG system works better than the current recommender and materially better than vector-only retrieval for graph-relevant questions.

## Evaluation layers

### Source and ingestion quality

- parser coverage
- structural preservation
- evidence-anchor completeness
- version integrity
- idempotent reload behavior

### Ontology quality

- schema conformance
- alias uniqueness
- predicate validity
- orphan rate
- semantic distinction between near-neighbour skills

### Retrieval quality

- exact lookup accuracy
- alias resolution accuracy
- graph traversal accuracy
- multi-skill synthesis support
- recall at k
- MRR or NDCG
- graph-backed lift over vector-only baseline

### Runtime planning quality

- query intent classification accuracy
- safe query family selection accuracy
- Cypher validation pass rate
- forbidden-query rejection rate

### Answer quality

- citation accuracy
- groundedness
- completeness
- abstention quality
- contradiction handling

### Operational quality

- latency
- token cost
- retrieval freshness
- error recovery
- observability completeness

## Required test sets

The evaluation corpus must include:

1. exact canonical-name lookups
2. alias lookups
3. deliberately vague semantic questions
4. near-neighbour disambiguation pairs
5. typed relationship traversals
6. missing-evidence abstention cases
7. contradictory-evidence cases
8. pack-version regression cases
9. malicious or unsafe text-to-Cypher prompts

## Release gates

Do not cut over to KRAG v2 unless all are true:

- graph-relevant queries outperform vector-only retrieval
- every material answer claim is citation-backed
- forbidden Cypher patterns are rejected
- ingestion remains idempotent across reloads
- near-neighbour disambiguation improves materially over the pre-cutover baseline
- no category-derived synthetic bridge is required for core retrieval success

## Required observability per query

- query id
- query intent
- resolved entities and aliases
- selected retrieval strategy
- approved query family
- generated Cypher
- validation outcome
- retrieved node ids
- evidence anchor ids
- citation ids used in the answer
- latency and cost
- abstention reason where applicable

## Success criterion

The refactor succeeds only if the graph becomes a necessary and measurable contributor to retrieval precision, provenance and answer quality. If the same benchmark can be passed without graph-aware retrieval, the system has not achieved its purpose.
