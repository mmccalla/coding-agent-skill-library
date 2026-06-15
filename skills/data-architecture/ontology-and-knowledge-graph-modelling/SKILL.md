---
name: ontology-kg-krag
description: Design, validate and use ontology-driven knowledge graphs for explainable KG-RAG/KRAG.
---

# Ontology, Knowledge Graph and KRAG

## When to use
Use for ontology design, semantic modelling, RDF/OWL/SHACL/SKOS, property-graph schemas, knowledge-graph population, graph validation, entity resolution, provenance, inference, semantic search, KG-RAG/KRAG or GraphRAG.

When the task moves from graph design into Neo4j-native retrieval, text-to-Cypher, ingestion safety, or GraphRAG implementation guidance, also load `skills/data-architecture/kg-enabled-rag/SKILL.md`.

Do not use for ordinary diagrams, generic vector-only RAG, or simple entity extraction unless semantic governance or graph retrieval is required.

## Goal
Produce a small, implementable semantic design that answers defined competency questions, validates graph data, preserves provenance, and supports explainable retrieval for LLM grounding.

## Operating rules
- Start from the user goal, decisions to support, and competency questions.
- Model only what is needed now; extend only from evidence or failed competency questions.
- Separate meaning from validation: ontology defines semantics; shapes/rules define data-quality constraints.
- Reuse external vocabularies only when definitions genuinely match.
- Do not create subclass links unless the child is always a valid kind of the parent.
- Prefer explicit predicates with business meaning; avoid vague edges such as `relatedTo`, `has`, `linksTo`, or `associatedWith` unless tightly defined.
- Keep identifiers stable and documented: URI/IRI/CURIE/key policy, namespace, versioning, canonical labels and aliases.
- Keep asserted, inferred and LLM-generated facts separate.
- Every graph fact used for decisions or retrieval must link to source evidence, extraction method, timestamp/version and confidence.
- Treat the LLM as an extractor, mapper, summariser or query assistant, not as an authority of record.

## Procedure
1. **Scope**: define domain boundary, users, use cases, competency questions, in/out scope and non-goals.
2. **Representation**: choose RDF/OWL/SHACL/SKOS when standards, inference and interoperability matter; choose property graph when traversal/application delivery is primary; document trade-offs.
3. **Core model**: define classes/concepts, predicates, properties, cardinalities, controlled terms, identifiers and provenance fields.
4. **Reuse**: map to standards/vocabularies where definitions align; record accepted, rejected and adapted terms.
5. **Constraints**: define SHACL or equivalent validation for required properties, datatypes, cardinality, controlled values, referential integrity and invalid patterns.
6. **Population**: specify extraction, normalisation, entity resolution, relationship creation, confidence scoring, duplicate handling and human review thresholds.
7. **Reasoning**: define allowed inference rules, materialisation strategy, contradiction handling and explanation requirements.
8. **KRAG design**: define retrieval units, entity linking, graph expansion depth, path constraints, community summaries, hybrid vector+graph search and answer citation rules.
9. **Evaluation**: test ontology consistency, shape conformance, extraction precision/recall, entity-resolution quality, retrieval relevance, answer faithfulness and source traceability.
10. **Evolution**: version ontology, shapes, mappings and graph data; document breaking changes, migration rules and deprecation policy.

## KRAG patterns
Use the simplest pattern that answers the question:
- **Entity-first retrieval**: resolve entities, then retrieve adjacent facts and evidence.
- **Path retrieval**: retrieve meaningful paths between entities with bounded depth and allowed predicates.
- **Subgraph retrieval**: retrieve a compact neighbourhood around relevant entities or documents.
- **Community retrieval**: summarise clusters/communities for broad questions.
- **Ontology-guided retrieval**: constrain retrieval by class, predicate, hierarchy, policy or shape.
- **Hybrid retrieval**: combine vector search for recall with graph traversal for precision, provenance and explanation.
- **Graph-to-query**: generate SPARQL/Cypher only against the approved schema; validate before execution.

## Required outputs
- Purpose, scope and competency questions.
- Classes/concepts with labels, definitions and examples.
- Predicates/relationships with direction, domain, range and meaning.
- Properties, identifiers, controlled vocabularies and namespace policy.
- Provenance model for source, method, timestamp/version and confidence.
- Constraints/shapes and validation checks.
- Inference rules, if any, with asserted vs inferred fact handling.
- KRAG retrieval design with grounding, citations and failure behaviour.
- Quality gates, risks, assumptions and open decisions.

## Quality gates
Pass only if:
- Each model element supports a use case or competency question.
- Relationship names are meaningful and directionally clear.
- External reuse is justified by definitional alignment.
- Constraints catch missing, invalid, duplicate and contradictory data.
- Retrieval returns source-backed evidence, not unsupported summaries.
- Generated answers cite graph/source evidence and state uncertainty.
- Security, privacy, access control and retention constraints are explicit where relevant.

## Avoid
- Ontology bloat, speculative classes, and premature upper-ontology work.
- Treating embeddings as a substitute for identifiers, semantics or provenance.
- Writing LLM-generated facts into the trusted graph without review or evidence.
- Mixing source text, extracted facts, inferred facts and generated summaries without type/provenance separation.
- Using generic relationships where a domain predicate is needed.
- Ignoring negative tests, adversarial prompts, stale sources or contradictory evidence.

## Verification
Report artefacts produced, key decisions, assumptions, trade-offs, risks, validation performed, unresolved issues and files changed.
