---
name: data-security-and-privacy-architecture
description: Designs classification, access, masking, privacy, entitlement and sensitive-data controls. Use when securing shared data, defining privacy controls, or classifying datasets.
---

# Data Security and Privacy Architecture

## When to use
Use when data contains sensitive, personal, confidential, regulated or high-value information.

## Objective
Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure
1. Classify data by sensitivity and purpose.
2. Identify users, roles and access needs.
3. Define entitlement model and approval flow.
4. Define masking, tokenisation or encryption.
5. Define row/column/object-level controls.
6. Define logging, monitoring and access evidence.
7. Define retention/privacy obligations.
8. Test denial and misuse cases.

## Required outputs
- Classification model
- Access matrix
- Entitlement workflow
- Masking/encryption requirements
- Audit/access evidence
- Negative tests

## Best-practice alignment
Apply DAMA-DMBOK2-style separation of data governance, architecture, modelling, security, integration/interoperability, master/reference data, metadata and quality. For cloud/shared data, apply CDMC-style expectations: ownership, classification, entitlement/access evidence, lineage/provenance, lifecycle/retention, quality controls and auditable evidence.

## Quality checks
- Access is least privilege.
- Sensitive fields are identified.
- Denial paths are tested.
- Sensitive values are not logged.
- Access evidence is auditable.

## Avoid
Do not rely on UI-only access controls or broad shared credentials.

## Verification
State artefacts produced, decisions made, assumptions, risks, validation performed and files changed.
