---
name: event-modelling
description: Discover and model business events, commands, decisions and state changes.
---

# Event Modelling

## When to use
Use when identifying event semantics before schema or topic design.

## Objective
Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure
1. Identify process/value stream.
2. Map trigger-to-outcome timeline.
3. Identify commands, events, decisions and read models.
4. Name events in past tense.
5. Define event meaning and payload concepts.
6. Identify correlation/causation IDs.
7. Validate language with business stakeholders.

## Required outputs
- Event timeline
- Command/event list
- Event definitions
- Payload concepts
- Identifiers
- Open questions

## Best-practice alignment
Apply event-driven best practice: business event semantics, producer/consumer ownership, schema contracts, compatibility, ordering, partitioning, idempotency, replay, retention, lineage, observability and operational SLOs.

## Quality checks
- Events are past-tense facts.
- Commands are not modelled as events.
- Names match business language.

## Avoid
Do not name events after database operations.

## Completion report
State artefacts produced, decisions made, assumptions, risks, validation performed and files changed.
