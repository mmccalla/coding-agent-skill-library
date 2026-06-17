---
name: data-lifecycle-and-retention-management
description: Designs lifecycle, retention, archival, deletion, legal hold and disposal controls. Use when defining data retention policies, archival strategy, or compliant deletion.
---

# Data Lifecycle and Retention Management

## When to use
Use for datasets, products, logs, events, metadata, quarantine stores and refined datasets with retention obligations.

## Objective
Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure
1. Identify data classes and lifecycle states.
2. Define retention by class and purpose.
3. Define archival/delete triggers.
4. Define legal hold exceptions.
5. Define ownership and approval.
6. Define disposal evidence.
7. Define lineage/audit impact.
8. Test retention enforcement.

## Required outputs
- Lifecycle states
- Retention schedule
- Archive/delete rules
- Legal hold process
- Disposal evidence
- Implementation checks

## Best-practice alignment
Apply DAMA-DMBOK2-style separation of data governance, architecture, modelling, security, integration/interoperability, master/reference data, metadata and quality. For cloud/shared data, apply CDMC-style expectations: ownership, classification, entitlement/access evidence, lineage/provenance, lifecycle/retention, quality controls and auditable evidence.

## Quality checks
- Retention is purpose-based.
- Disposal is auditable.
- Legal holds override deletion.
- Lineage/audit impact is explicit.

## Avoid
Do not keep data indefinitely because deletion is inconvenient.

## Verification

- [ ] Required artefacts produced and linked to scope.
- [ ] Decisions, assumptions and risks stated explicitly.
- [ ] Quality checks or validation performed.
- [ ] Files changed reported with traceability preserved.

