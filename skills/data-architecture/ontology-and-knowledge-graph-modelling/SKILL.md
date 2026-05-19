---
name: ontology-and-knowledge-graph-modelling
description: Design ontologies, semantic models, knowledge graphs and inference-ready structures.
---

# Ontology and Knowledge Graph Modelling

## When to use
Use for semantic layers, RDF/OWL-style modelling, graph integration or inference/data-quality rules.

## Objective
Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure
1. Define purpose and competency questions.
2. Identify classes, concepts and relationships.
3. Reuse vocabularies only where definitions align.
4. Define labels, comments and predicate meanings.
5. Define constraints and validation rules.
6. Define identifiers and provenance.
7. Test consistency where tooling exists.
8. Link model to source artefacts and data products.

## Required outputs
- Competency questions
- Classes/concepts
- Relationships/predicates
- Constraints
- Provenance links
- Reasoning/validation checks

## Best-practice alignment
Apply DAMA-DMBOK2-style separation of data governance, architecture, modelling, security, integration/interoperability, master/reference data, metadata and quality. For cloud/shared data, apply CDMC-style expectations: ownership, classification, entitlement/access evidence, lineage/provenance, lifecycle/retention, quality controls and auditable evidence.

## Quality checks
- Relationships have meaningful semantics.
- External reuse is justified.
- Constraints support validation.
- Provenance is retained.

## Avoid
Do not add subclass relationships unless definitions genuinely match.

## Completion report
State artefacts produced, decisions made, assumptions, risks, validation performed and files changed.
