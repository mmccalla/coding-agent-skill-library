---
name: cdc-and-source-to-stream-ingestion
description: Designs CDC and streaming ingestion from operational sources to event streams. Use when capturing database changes, replicating operational data, or building source-to-stream pipelines.
---

# CDC and Source-to-Stream Ingestion

## When to use
Use when turning database/file/API changes into streams.

## Objective
Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure
1. Identify source and owner.
2. Select capture method.
3. Define snapshot and incremental flow.
4. Define keys and ordering.
5. Define delete/tombstone handling.
6. Define schema evolution.
7. Define backfill/replay.
8. Define lag and reconciliation checks.

## Required outputs
- Capture design
- Keys/order handling
- Schema evolution
- Delete handling
- Backfill/replay
- Monitoring

## Best-practice alignment
Apply event-driven best practice: business event semantics, producer/consumer ownership, schema contracts, compatibility, ordering, partitioning, idempotency, replay, retention, lineage, observability and operational SLOs.

## Quality checks
- Source impact is understood.
- Deletes and updates are handled.
- Reconciliation exists.
- Lineage is preserved.

## Avoid
Do not treat raw CDC records as business events without translation.

## Decision template

Use this template before implementation: source system and owner; capture mode; snapshot boundary; primary key and ordering field; update/delete semantics; schema evolution path; reconciliation rule; replay and backfill limit; lag SLI; lineage record. If downstream consumers need business facts, translate raw CDC records into governed events before publishing.

## References

- Debezium documentation (CDC): https://debezium.io/documentation/
- CloudEvents specification: https://cloudevents.io/

## Verification

- [ ] Required artefacts produced and linked to scope.
- [ ] Decisions, assumptions and risks stated explicitly.
- [ ] Quality checks or validation performed.
- [ ] Files changed reported with traceability preserved.

