---
name: conceptual-data-modelling
description: Identify business concepts, entities and relationships without premature logical or physical design.
---

# Conceptual Data Modelling

## When to use
Use for business-facing models, BCM/value-stream-to-data translation, ontology input or domain concept clarification.

## Objective
Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure
1. Define scope and business questions.
2. Extract concepts from capabilities, value streams, processes and language.
3. Remove implementation-only items.
4. Define each concept in business terms.
5. Identify relationships with meaningful verbs.
6. Distinguish entity, event, role, classification and value object.
7. Link concepts to source artefacts and owners.

## Required outputs
- Concept list with definitions
- Relationship list with verbs
- Exclusions and rationale
- Traceability to business artefacts
- Open questions

## Best-practice alignment
Apply DAMA-DMBOK2-style separation of data governance, architecture, modelling, security, integration/interoperability, master/reference data, metadata and quality. For cloud/shared data, apply CDMC-style expectations: ownership, classification, entitlement/access evidence, lineage/provenance, lifecycle/retention, quality controls and auditable evidence.

## Quality checks
- Concepts use business language.
- No physical tables, columns or system artefacts unless business-significant.
- Relationships are meaningful.
- Scope is explicit.

## Avoid
Do not jump to physical schemas or over-normalise.

## Completion report
State artefacts produced, decisions made, assumptions, risks, validation performed and files changed.
