# KRAG v2 Target Operating Model

## Objective

Refactor the Skills KG into a real KRAG system where the graph materially improves retrieval and answer quality, and where newly added skill packs become first-class graph assets without manual bridge tuning.

## End-to-end operating flow

1. A developer adds a skill or skill pack to the library.
2. The ingestion pipeline registers the pack as a versioned source resource.
3. The parser preserves pack, skill and section structure and creates evidence anchors.
4. The ontology mapper produces validated semantic assertions from the source.
5. The graph loader writes canonical graph data and retrieval projections to Neo4j.
6. A user submits a natural-language query.
7. The runtime classifies the query intent and resolves named entities, aliases or concepts.
8. The planner selects graph-first, keyword-first, vector-first or hybrid retrieval.
9. The planner generates bounded read-only Cypher from approved query families.
10. The runtime executes Cypher and optional lexical or vector recall steps.
11. The ranker compresses retrieved evidence into a bounded answer context.
12. The LLM answers using only retrieved evidence and returns citations, uncertainty and abstention where required.

## Supported question classes

The first implementation should support these query classes explicitly:

1. `skill_lookup`
2. `skill_pack_discovery`
3. `alias_resolution`
4. `relationship_traversal`
5. `execution_context`
6. `governance_validation_lookup`
7. `multi_skill_synthesis`
8. `abstention_due_to_missing_evidence`

These question classes are intentionally narrower than open-ended chat. The runtime should classify into one of them before any graph query is generated.

## Graph role

The graph must play four roles at once:

1. canonical knowledge representation for skills and packs
2. provenance store for evidence used in answers
3. retrieval substrate for deterministic traversals and bounded Cypher
4. evaluation surface for validating whether graph-backed retrieval is better than vector-only retrieval

## Thin-slice implementation order

Build the system in this order:

1. ontology and validation rules
2. skill-pack ingestion and graph load
3. retrieval projection layer
4. query classification and safe Cypher planning
5. answer synthesis with citations
6. live evaluation and release gates

## Anti-goals

- No category-derived pseudo-semantics to make the graph appear more connected than it is.
- No arbitrary Cypher execution from LLM output.
- No graph writes from unvalidated extraction.
- No answer generation from graph neighborhood alone without evidence anchors.
- No production-quality claims until graph-backed queries beat the vector-only baseline for graph-relevant tasks.

## Minimum viable KRAG slice

The first end-to-end slice should answer:

"Which skill should I use for this task, why, what related skills matter, and what evidence in the library supports that recommendation?"

That slice must show:

- query intent
- alias or concept resolution
- planned graph query family
- generated bounded Cypher
- retrieved nodes, paths and evidence anchors
- final answer with citations

If that slice is not reliable, the broader KRAG architecture should not be expanded yet.
