---
name: schema-registry-and-contracts
description: Defines event schemas, compatibility, versioning and producer-consumer obligations. Use when governing Avro, JSON, or Protobuf schemas and registry compatibility policies.
---

# Schema Registry and Contracts

## When to use
Use when event payloads are shared or long-lived.

## Objective
Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure
1. Identify producer/consumers.
2. Define event semantics.
3. Choose schema format.
4. Define required/optional fields.
5. Define compatibility mode.
6. Define versioning/deprecation.
7. Define contract tests.
8. Define ownership/support.

## Required outputs
- Schema definition
- Compatibility policy
- Versioning rules
- Contract tests
- Ownership/support

## Best-practice alignment
Apply event-driven best practice: business event semantics, producer/consumer ownership, schema contracts, compatibility, ordering, partitioning, idempotency, replay, retention, lineage, observability and operational SLOs.

## Quality checks
- Compatibility is explicit.
- Semantic meaning is documented.
- Breaking changes are controlled.

## Avoid
Do not treat syntactic compatibility as sufficient.

## Decision template

Before registering a schema, capture event meaning, producer, consumers, required fields, optional fields, compatibility mode, semantic versioning rule, deprecation policy and contract tests. Treat syntactic compatibility as necessary but incomplete: a field can remain valid JSON while its business meaning changes and breaks consumers.

## Verification

- [ ] Required artefacts produced and linked to scope.
- [ ] Decisions, assumptions and risks stated explicitly.
- [ ] Quality checks or validation performed.
- [ ] Files changed reported with traceability preserved.

