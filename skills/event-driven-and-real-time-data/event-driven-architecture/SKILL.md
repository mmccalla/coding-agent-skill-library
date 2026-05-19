---
name: event-driven-architecture
description: Design event-driven systems using asynchronous flows, events, brokers, producers, consumers and contracts.
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

## Completion report
State artefacts produced, decisions made, assumptions, risks, validation performed and files changed.
