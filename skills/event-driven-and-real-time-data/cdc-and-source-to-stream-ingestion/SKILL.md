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

## Verification
State artefacts produced, decisions made, assumptions, risks, validation performed and files changed.
