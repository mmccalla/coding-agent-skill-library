---
name: metadata-management
description: Designs metadata for discoverability, governance, quality, lineage and operations. Use when building catalogues, data discovery, or operational metadata standards.
---

# Metadata Management

## When to use

Use for catalogues, glossaries, data product metadata, lineage metadata or governance evidence.

## Objective

Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure

1. Define metadata use cases.
2. Define metadata categories.
3. Identify authoritative sources.
4. Define required fields and owners.
5. Define capture/update mechanisms.
6. Link glossary, assets, contracts, lineage and quality.
7. Define stewardship workflow.
8. Measure completeness/freshness.

## Required outputs

- Metadata model
- Required fields
- Ownership and stewardship
- Capture/update approach
- Glossary, quality and lineage links
- Completeness metrics

## Best-practice alignment

Apply DAMA-DMBOK2-style separation of data governance, architecture, modelling, security, integration/interoperability, master/reference data, metadata and quality. For cloud/shared data, apply CDMC-style expectations: ownership, classification, entitlement/access evidence, lineage/provenance, lifecycle/retention, quality controls and auditable evidence.

## Quality checks

- Metadata has users and use cases.
- Critical fields are mandatory.
- Ownership and freshness are tracked.
- Manual entry is minimised.

## Avoid

Do not collect metadata with no use case or owner.

## References

- [DAMA-DMBOK (DAMA International)](https://www.dama.org/cpages/body-of-knowledge)
- [EDM Council CDMC (Cloud Data Management Capabilities)](https://edmcouncil.org/frameworks/cdmc/)
- [W3C DCAT 3](https://www.w3.org/TR/vocab-dcat-3/)

## Verification

- [ ] Required artefacts produced and linked to scope.
- [ ] Decisions, assumptions and risks stated explicitly.
- [ ] Quality checks or validation performed.
- [ ] Files changed reported with traceability preserved.
