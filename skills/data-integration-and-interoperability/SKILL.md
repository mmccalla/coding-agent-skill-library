---
name: data-integration-and-interoperability
description: Designs batch, API, event, CDC, semantic and file-based integration patterns. Use when connecting systems, choosing integration styles, or resolving interoperability gaps.
---

# Data Integration and Interoperability

## When to use

Use when moving or sharing data between systems, domains, products or platforms.

## Objective

Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure

1. Identify source, target and consumers.
2. Define latency/consistency needs.
3. Choose pattern: batch, API, CDC, event, stream, file or semantic.
4. Define schema/contract.
5. Define transformation and quality checks.
6. Define error handling/reconciliation.
7. Define lineage and observability.
8. Define ownership/support.

## Required outputs

- Integration pattern decision
- Contract/schema
- Latency/consistency assumptions
- Error/reconciliation approach
- Lineage and support model

## Best-practice alignment

Apply DAMA-DMBOK2-style separation of data governance, architecture, modelling, security, integration/interoperability, master/reference data, metadata and quality. For cloud/shared data, apply CDMC-style expectations: ownership, classification, entitlement/access evidence, lineage/provenance, lifecycle/retention, quality controls and auditable evidence.

## Quality checks

- Pattern matches latency and coupling needs.
- Schema and semantics are explicit.
- Failures are observable.
- Reconciliation is possible where required.

## Avoid

Do not choose streaming where batch is simpler and sufficient.

## References

- [DAMA-DMBOK (DAMA International)](https://www.dama.org/cpages/body-of-knowledge)
- [EDM Council CDMC (Cloud Data Management Capabilities)](https://edmcouncil.org/frameworks/cdmc/)

## Verification

- [ ] Required artefacts produced and linked to scope.
- [ ] Decisions, assumptions and risks stated explicitly.
- [ ] Quality checks or validation performed.
- [ ] Files changed reported with traceability preserved.
