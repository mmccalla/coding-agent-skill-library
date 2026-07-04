---
name: event-governance-and-lineage
description: Governs event ownership, classification, metadata, lineage, quality and lifecycle. Use when governing shared event catalogues, schemas, or stream ownership.
---

# Event Governance and Lineage

## When to use
Use when events are shared, reused, regulated or business-critical.

## Objective
Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure
1. Assign event owner.
2. Define catalogue metadata.
3. Classify sensitivity.
4. Link to capability/value stream/data product.
5. Capture producer/consumer lineage.
6. Define quality/contract checks.
7. Define retention/lifecycle.
8. Define access controls.

## Required outputs
- Owner
- Catalogue metadata
- Classification
- Lineage
- Quality checks
- Lifecycle/access policy

## Best-practice alignment
Apply event-driven best practice: business event semantics, producer/consumer ownership, schema contracts, compatibility, ordering, partitioning, idempotency, replay, retention, lineage, observability and operational SLOs.

## Quality checks
- No orphan streams.
- Sensitive data is classified.
- Producer/consumer lineage exists.

## Avoid
Do not rely on tribal knowledge for event meaning.

## Governance template

For each shared event, capture owner, business definition, source capability, producer, consumers, schema version, classification, retention, quality checks, lineage links and support contact. A catalogue entry is not complete until consumers can understand meaning, sensitivity, replay constraints and who approves breaking changes.

## References

- DAMA-DMBOK (DAMA International): https://www.dama.org/cpages/body-of-knowledge
- EDM Council CDMC (Cloud Data Management Capabilities): https://edmcouncil.org/frameworks/cdmc/
- CloudEvents specification: https://cloudevents.io/

## Verification

- [ ] Required artefacts produced and linked to scope.
- [ ] Decisions, assumptions and risks stated explicitly.
- [ ] Quality checks or validation performed.
- [ ] Files changed reported with traceability preserved.

