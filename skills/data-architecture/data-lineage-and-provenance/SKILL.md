---
name: data-lineage-and-provenance
description: Tracks source-to-target lineage, transformation history, evidence, ownership and provenance. Use when documenting data flows, audit trails, or impact analysis for changes.
---

# Data Lineage and Provenance

## When to use
Use when data must be trusted, audited, explained, replayed, governed or traced.

For KG-enabled RAG or GraphRAG systems, use this alongside `skills/data-architecture/kg-enabled-rag/SKILL.md` so graph facts, retrieval evidence and generated answers remain source-traceable.

## Objective
Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure
1. Define lineage scope and grain.
2. Identify source, transformation and target assets.
3. Capture workflow, batch and run identifiers.
4. Capture schema/rule/transformation versions.
5. Link validation, cleansing, quarantine and refined decisions.
6. Capture actor/system provenance.
7. Store lineage in queryable form.
8. Test completeness for representative flows.

## Required outputs
- Lineage scope and grain
- Source/transformation/target links
- Run and batch identifiers
- Rule/transformation versions
- Evidence links
- Access controls

## Best-practice alignment
Apply DAMA-DMBOK2-style separation of data governance, architecture, modelling, security, integration/interoperability, master/reference data, metadata and quality. For cloud/shared data, apply CDMC-style expectations: ownership, classification, entitlement/access evidence, lineage/provenance, lifecycle/retention, quality controls and auditable evidence.

## Quality checks
- Lineage is operational, not just a static diagram.
- Transformation versions are captured.
- Sensitive values are not exposed.
- Evidence is queryable.

## Avoid
Do not claim trust without lineage/provenance evidence.

## Verification
State artefacts produced, decisions made, assumptions, risks, validation performed and files changed.
