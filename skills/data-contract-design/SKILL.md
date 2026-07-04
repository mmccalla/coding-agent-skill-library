---
name: data-contract-design
description: Defines producer-consumer contracts for schema, semantics, quality, compatibility and operations. Use when formalising API, event, or dataset agreements between teams.
---

# Data Contract Design

## When to use

Use where a stable producer-consumer boundary exists for tables, files, APIs, events or data products.

## Objective

Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure

1. Identify producer and consumers.
2. Define interface and scope.
3. Define schema, semantics and constraints.
4. Define quality, freshness and completeness obligations.
5. Define compatibility/versioning.
6. Define classification and allowed use.
7. Define contract tests.
8. Define incident/deprecation process.

## Required outputs

- Producer/consumer list
- Schema and semantic definitions
- Quality/freshness obligations
- Compatibility policy
- Contract tests
- Deprecation process

## Best-practice alignment

Apply DAMA-DMBOK2-style separation of data governance, architecture, modelling, security, integration/interoperability, master/reference data, metadata and quality. For cloud/shared data, apply CDMC-style expectations: ownership, classification, entitlement/access evidence, lineage/provenance, lifecycle/retention, quality controls and auditable evidence.

Align producer-consumer contracts with the **Open Data Contract Standard (ODCS)** where a portable YAML/JSON contract is appropriate: fundamentals, schema, quality rules, team/ownership, roles, SLA, support channels and infrastructure. Prefer contract-first design, semantic versioning for breaking changes, contracts co-located with the data product, and executable validation in CI (for example Data Contract CLI).

## Quality checks

- Contract has syntax and semantics.
- Breaking changes are defined.
- Tests are specified.
- Ownership and support are explicit.

## Avoid

Do not define schemas without semantics or change management.
Do not treat contracts as documentation-only; enforce them with tests and pipeline checks.

## References

- [Open Data Contract Standard (ODCS)](https://bitol-io.github.io/open-data-contract-standard)
- [DAMA-DMBOK (DAMA International)](https://www.dama.org/cpages/body-of-knowledge)
- [EDM Council CDMC (Cloud Data Management Capabilities)](https://edmcouncil.org/frameworks/cdmc/)

## Verification

- [ ] Required artefacts produced and linked to scope.
- [ ] Decisions, assumptions and risks stated explicitly.
- [ ] Quality checks or validation performed.
- [ ] Files changed reported with traceability preserved.
