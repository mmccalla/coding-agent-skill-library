---
name: master-and-reference-data-management
description: Designs master data, reference data, identifiers, hierarchies, survivorship and stewardship. Use when defining golden records, controlled vocabularies, or MDM patterns.
---

# Master and Reference Data Management

## When to use
Use where shared entities or controlled values need consistent identity across systems.

## Objective
Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure
1. Identify master/reference domain.
2. Define identifiers and matching keys.
3. Identify authoritative sources.
4. Define golden record or controlled-list approach.
5. Define survivorship rules.
6. Define hierarchy handling.
7. Define stewardship workflow.
8. Define publication/consumption model.

## Required outputs
- Domain and scope
- Identifiers and source hierarchy
- Survivorship rules
- Stewardship workflow
- Publication model
- Quality controls

## Best-practice alignment
Apply DAMA-DMBOK2-style separation of data governance, architecture, modelling, security, integration/interoperability, master/reference data, metadata and quality. For cloud/shared data, apply CDMC-style expectations: ownership, classification, entitlement/access evidence, lineage/provenance, lifecycle/retention, quality controls and auditable evidence.

## Quality checks
- Authority is clear.
- Merge/split rules are evidenced.
- Controlled values have lifecycle.
- Consumers know usage rules.

## Avoid
Do not create golden records without stewardship and survivorship rules.

## Verification
State artefacts produced, decisions made, assumptions, risks, validation performed and files changed.
