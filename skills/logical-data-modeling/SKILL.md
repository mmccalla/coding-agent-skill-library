---
name: logical-data-modeling
description: Defines logical entities, attributes, identifiers, relationships and constraints. Use when translating conceptual models to logical schemas or normalising entity designs.
aliases:
  - logical-data-modelling
  - logical-data-model
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

## Physical design hand-off

When implementation requires storage decisions, extend the logical model deliberately:

1. Map entities to tables, collections or files without losing identifiers and relationships.
2. Choose primary/alternate keys and clustering or partition keys for access patterns.
3. Define indexes for critical queries; avoid unbounded secondary indexes.
4. Record physical constraints (nullability, types, sizes) and migration approach.
5. Hand off lakehouse layering to `lakehouse-and-medallion-architecture` when medallion zones apply.
6. Keep logical meaning authoritative; physical optimisations must not silently change semantics.

## Avoid

Do not conflate logical model with API payloads or physical storage without an explicit hand-off.
Do not introduce physical-platform assumptions into the logical model itself.

## Related skills

- `conceptual-data-modeling` — business concepts
- `lakehouse-and-medallion-architecture` — physical lakehouse layers
- `data-contract-design` — consumer-facing contracts

## References

- [DAMA-DMBOK (DAMA International)](https://www.dama.org/cpages/body-of-knowledge)
- [EDM Council CDMC (Cloud Data Management Capabilities)](https://edmcouncil.org/frameworks/cdmc/)

## Verification

- [ ] Required artefacts produced and linked to scope.
- [ ] Decisions, assumptions and risks stated explicitly.
- [ ] Quality checks or validation performed.
- [ ] Physical hand-off (keys, indexes, partitions) recorded when implementation proceeds.
- [ ] Files changed reported with traceability preserved.
