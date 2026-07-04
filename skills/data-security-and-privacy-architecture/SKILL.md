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

## Privacy compliance procedure

This is an operational procedure for agents, not legal advice.

1. Map personal data categories, purposes and systems involved in the change.
2. Confirm a lawful basis or organisational policy basis for processing where applicable.
3. Trigger a DPIA (data protection impact assessment) when processing is high risk (large-scale sensitive data, systematic monitoring, automated decisions with legal effect).
4. Define data-subject rights handling (access, rectification, erasure/DSAR paths) and response owners.
5. Align retention, deletion and transfer controls with `data-lifecycle-and-retention-management`.
6. Record evidence (classification, access logs, DPIA reference, retention rules).

## Avoid

Do not rely on UI-only access controls or broad shared credentials.
Do not treat privacy compliance as solved by encryption alone.

## Related skills

- `data-lifecycle-and-retention-management` — retention and deletion
- `threat-modeling` — abuse and exfiltration threats
- `human-in-the-loop` — approval for high-risk processing

## References

- [DAMA-DMBOK (DAMA International)](https://www.dama.org/cpages/body-of-knowledge)
- [EDM Council CDMC (Cloud Data Management Capabilities)](https://edmcouncil.org/frameworks/cdmc/)
- [ICO UK GDPR guidance](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/)

## Verification

- [ ] Required artefacts produced and linked to scope.
- [ ] Decisions, assumptions and risks stated explicitly.
- [ ] Quality checks or validation performed.
- [ ] Privacy compliance steps considered (DPIA trigger, data-subject rights, evidence).
- [ ] Files changed reported with traceability preserved.
