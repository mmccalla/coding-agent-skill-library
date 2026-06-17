---
name: event-driven-architecture
description: Designs event-driven systems with asynchronous flows, brokers, producers, consumers and contracts. Use when architecting asynchronous, decoupled, or event-first systems.
---

# Event-Driven Architecture

## When to use
Use when designing asynchronous integration or event-first systems.

## Objective
Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure
1. Identify triggers and outcomes.
2. Separate events, commands and queries.
3. Identify producers/consumers.
4. Define topics/streams.
5. Define schemas/contracts.
6. Define ordering, partitioning, idempotency and replay.
7. Define failure handling.
8. Define observability.

## Required outputs
- Event flow
- Producers/consumers
- Topic/stream design
- Contracts
- Ordering/idempotency/replay decisions
- Operational controls

## Best-practice alignment
Apply event-driven best practice: business event semantics, producer/consumer ownership, schema contracts, compatibility, ordering, partitioning, idempotency, replay, retention, lineage, observability and operational SLOs.

## Quality checks
- Events have business meaning.
- Ownership is clear.
- Duplicate/replay behaviour is handled.
- Observability exists.

## Avoid
Do not use events to disguise tight coupling.

## Verification

- [ ] Required artefacts produced and linked to scope.
- [ ] Decisions, assumptions and risks stated explicitly.
- [ ] Quality checks or validation performed.
- [ ] Files changed reported with traceability preserved.

