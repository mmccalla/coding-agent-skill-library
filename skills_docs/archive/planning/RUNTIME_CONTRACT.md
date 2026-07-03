# KRAG v2 Runtime Contract

## Objective

Answer user questions from graph structure plus source-backed evidence using bounded, validated retrieval plans.

## Runtime stages

### 1. Query classification

Every user query must be classified before retrieval into one of the approved query intents.

Minimum query intents:

- `skill_lookup`
- `skill_pack_discovery`
- `alias_resolution`
- `relationship_traversal`
- `execution_context`
- `governance_validation_lookup`
- `multi_skill_synthesis`
- `missing_evidence_abstention`

### 2. Entity and alias resolution

Resolve canonical skill ids, pack ids, aliases and governed concepts before planning Cypher. This must happen against first-class alias and ontology nodes, not only by scanning section text.

### 3. Retrieval strategy selection

Use the smallest sufficient strategy:

1. graph-first for known entities, related-skill traversals, constraints, procedure steps and verification checks
2. keyword-first for exact ids or canonical names
3. vector-first for vague exploratory questions
4. hybrid only when recall matters or the query is broad

### 4. Query planning

Generate a structured plan first. The plan must include:

- query intent
- resolved entities
- selected strategy
- approved query family
- parameter set
- result bounds

### 5. Safe text-to-Cypher

Cypher generation must be bounded by:

- approved labels
- approved relationship types
- approved query families
- read-only execution only
- depth limits
- cardinality limits

Generated Cypher must be validated before execution. If validation fails, the runtime must abstain or fall back to a safer retrieval path.

### 6. Evidence packaging

The runtime must return a bounded evidence set to the LLM that includes:

- canonical nodes retrieved
- path summaries where relevant
- evidence anchor ids
- source paths
- cited text fragments
- ranking rationale

### 7. Answer synthesis

The answerer must:

- separate facts from inferences from recommendations
- cite evidence for every material claim
- state uncertainty explicitly
- abstain when evidence is missing, weak or contradictory

## Required query families

The first implementation should support these Cypher families:

1. exact skill lookup by canonical id or alias
2. related-skill traversal with typed edges
3. capability and task-intent lookup
4. constraint and verification retrieval
5. pack-to-skill membership lookup
6. evidence-anchor retrieval for a selected skill

## Runtime anti-patterns

- No raw LLM-generated Cypher execution.
- No answer generation from graph neighborhoods without citations.
- No retrieval score based primarily on category-level bridges.
- No treating the graph as a decorative explanation layer after vector retrieval already decided the answer.
