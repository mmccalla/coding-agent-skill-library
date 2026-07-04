---
name: business-information-concept-modeling
description: Derives business concepts and relationships from capabilities, value streams and processes. Use when linking business architecture artefacts to information concepts for data modelling.
aliases:
  - business-information-concept-modelling
  - information-concept-modeling
---

# Business Information Concept Modelling

## When to use

Use when translating business architecture into conceptual data, ontology or semantic models.

## Objective

Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure

1. Review business artefacts.
2. Extract nouns, events, roles and artefacts.
3. Normalise synonyms.
4. Define candidate concepts.
5. Define semantic relationships.
6. Remove implementation-only terms.
7. Link to source artefacts.
8. Hand off to conceptual data modelling.

## Required outputs

- Concept list
- Definitions
- Relationships
- Synonyms/homonyms
- Traceability
- Exclusions

## Best-practice alignment

Align with **BIZBOK** business architecture practice: keep capabilities, value streams, processes, organisation, information concepts, initiatives and metrics separate, then link them from strategy to execution.

## Quality checks

- Concepts have definitions.
- Relationships use business semantics.
- Traceability exists.

## Avoid

Do not convert every noun into an entity.

## Mini example

From an onboarding value stream, extract concepts such as `Customer`, `Application`, `Identity Evidence`, `Eligibility Decision` and `Account`. Record synonyms like applicant/customer, define relationships such as customer submits application, and exclude implementation-only terms such as API payload or staging table. Hand the agreed concepts to conceptual data modelling with source traceability.

## References

- [Business Architecture Guild — BIZBOK (information concepts)](https://www.businessarchitectureguild.org/)
- [DAMA-DMBOK (DAMA International)](https://www.dama.org/cpages/body-of-knowledge)

## Verification

- [ ] Required artefacts produced and linked to scope.
- [ ] Decisions, assumptions and risks stated explicitly.
- [ ] Quality checks or validation performed.
- [ ] Files changed reported with traceability preserved.
