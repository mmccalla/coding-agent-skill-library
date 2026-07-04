---
name: lakehouse-and-medallion-architecture
description: Designs raw, quarantine, cleansed, refined and serving lakehouse layers. Use when structuring medallion pipelines, lakehouse zones, or batch and stream serving layers.
---

# Lakehouse and Medallion Architecture

## When to use
Use for lakehouse, source-to-refined, medallion or Iceberg/Delta/Hudi-style architectures.

## Objective
Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure
1. Define source and ingestion mode.
2. Define raw retention and immutability.
3. Define validation/quarantine rules.
4. Define cleansed transformations.
5. Define refined products/consumers.
6. Define schema evolution and partitioning.
7. Define lineage, quality and audit evidence.
8. Define replay/recovery.

## Required outputs
- Layer definitions
- Quarantine/refined rules
- Table format and partitioning
- Schema evolution rules
- Lineage/quality evidence
- Replay procedure

## Best-practice alignment
Apply DAMA-DMBOK2-style separation of data governance, architecture, modelling, security, integration/interoperability, master/reference data, metadata and quality. For cloud/shared data, apply CDMC-style expectations: ownership, classification, entitlement/access evidence, lineage/provenance, lifecycle/retention, quality controls and auditable evidence.

## Quality checks
- Raw data is preserved.
- Failed records are quarantined with reasons.
- Refined data is quality-backed.
- Replay and lineage are possible.

## Avoid
Do not overwrite raw data or mix raw and refined records without labels.

## References

- DAMA-DMBOK (DAMA International): https://www.dama.org/cpages/body-of-knowledge
- EDM Council CDMC (Cloud Data Management Capabilities): https://edmcouncil.org/frameworks/cdmc/
- Databricks — Medallion Architecture: https://www.databricks.com/glossary/medallion-architecture

## Verification

- [ ] Required artefacts produced and linked to scope.
- [ ] Decisions, assumptions and risks stated explicitly.
- [ ] Quality checks or validation performed.
- [ ] Files changed reported with traceability preserved.

