---
name: logical-data-modelling
description: Defines logical entities, attributes, identifiers, relationships and constraints. Use when translating conceptual models to logical schemas or normalising entity designs.
---

# Logical Data Modelling

## When to use
Use when moving from conceptual model to implementable logical structure.

## Objective
Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure
1. Start from approved concepts.
2. Define entities and attributes.
3. Define identifiers, keys and relationships.
4. Define mandatory/optional attributes.
5. Define reference data and values.
6. Add integrity constraints and business rules.
7. Check normalisation and domain boundaries.
8. Validate against use cases and contracts.

## Required outputs
- Entity/attribute catalogue
- Identifiers and relationships
- Constraints and reference data
- Open modelling issues

## Best-practice alignment
Apply DAMA-DMBOK2-style separation of data governance, architecture, modelling, security, integration/interoperability, master/reference data, metadata and quality. For cloud/shared data, apply CDMC-style expectations: ownership, classification, entitlement/access evidence, lineage/provenance, lifecycle/retention, quality controls and auditable evidence.

## Quality checks
- Every entity traces to a business concept.
- Keys and lifecycle are explicit.
- Constraints are testable.
- No physical-platform assumptions.

## Avoid
Do not conflate logical model with API payloads or physical storage.

## Verification
State artefacts produced, decisions made, assumptions, risks, validation performed and files changed.
