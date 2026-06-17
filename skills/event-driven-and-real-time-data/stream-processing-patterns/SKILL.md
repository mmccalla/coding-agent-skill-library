---
name: stream-processing-patterns
description: Designs stream filtering, enrichment, joins, windows and stateful processing. Use when implementing Flink, Spark Streaming, or kstreams-style processing logic.
---

# Stream Processing Patterns

## When to use
Use for real-time transformations or analytics.

## Objective
Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure
1. Define input/output streams.
2. Define processing semantics.
3. Choose event time or processing time.
4. Define windows/joins/state.
5. Handle late/duplicate events.
6. Define state recovery.
7. Define dead-letter/error flow.
8. Test event sequences.

## Required outputs
- Processing design
- State/window policy
- Late/duplicate handling
- Error flow
- Tests
- Metrics

## Best-practice alignment
Apply event-driven best practice: business event semantics, producer/consumer ownership, schema contracts, compatibility, ordering, partitioning, idempotency, replay, retention, lineage, observability and operational SLOs.

## Quality checks
- Event time choices are explicit.
- State recovery is designed.
- Poison events are handled.

## Avoid
Do not assume events arrive in order unless guaranteed.

## Verification
State artefacts produced, decisions made, assumptions, risks, validation performed and files changed.
