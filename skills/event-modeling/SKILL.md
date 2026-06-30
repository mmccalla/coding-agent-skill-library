---
name: event-modeling
description: Discovers and models business events, commands, decisions and state changes. Use when event-storming, designing event timelines, or defining domain events.
aliases:
  - event-modelling
  - event-storming
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

## Decision aid

Start with sticky-note style discovery: commands in imperative form, events in past tense, decisions as policy points and read models as views. If a candidate event is named `UpdateCustomer`, challenge it until the business fact is clear, such as `CustomerAddressChanged`. Capture open questions where language is disputed.

## Verification

- [ ] Required artefacts produced and linked to scope.
- [ ] Decisions, assumptions and risks stated explicitly.
- [ ] Quality checks or validation performed.
- [ ] Files changed reported with traceability preserved.
