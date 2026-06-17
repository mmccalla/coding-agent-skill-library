---
name: real-time-operability
description: Designs operational controls for streaming: lag, freshness, replay, back-pressure and SLOs. Use when operating Kafka or streaming platforms or defining stream SLOs.
---

# Real-Time Operability

## When to use
Use when operating real-time pipelines or event streams.

## Objective
Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure
1. Define user impact.
2. Define SLIs for lag, freshness, throughput and error rate.
3. Define alerts and runbooks.
4. Define back-pressure behaviour.
5. Define replay/catch-up process.
6. Define dead-letter handling.
7. Define capacity and scaling.
8. Test operational scenarios.

## Required outputs
- SLIs/SLOs
- Dashboards/alerts
- Replay plan
- Back-pressure policy
- Dead-letter process
- Runbook

## Best-practice alignment
Apply event-driven best practice: business event semantics, producer/consumer ownership, schema contracts, compatibility, ordering, partitioning, idempotency, replay, retention, lineage, observability and operational SLOs.

## Quality checks
- Alerts are actionable.
- Replay is safe.
- Lag/freshness are visible.
- Capacity assumptions are explicit.

## Avoid
Do not equate broker health with pipeline health.

## Verification

- [ ] Required artefacts produced and linked to scope.
- [ ] Decisions, assumptions and risks stated explicitly.
- [ ] Quality checks or validation performed.
- [ ] Files changed reported with traceability preserved.

