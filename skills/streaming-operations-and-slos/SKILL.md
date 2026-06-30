---
name: streaming-operations-and-slos
description: Designs operational controls for streaming: lag, freshness, replay, back-pressure and SLOs. Use when operating Kafka or streaming platforms or defining stream SLOs.
aliases:
  - real-time-operability
  - streaming-operability
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

## Decision aid

Define operability from user impact first: freshness for decisions, lag for consumers, error rate for quality and recovery time for incidents. Alert on symptoms that require action, not only broker health. A replay plan must state how to avoid duplicate side effects, how far back replay is safe and who approves catch-up after data loss.

## Verification

- [ ] Required artefacts produced and linked to scope.
- [ ] Decisions, assumptions and risks stated explicitly.
- [ ] Quality checks or validation performed.
- [ ] Files changed reported with traceability preserved.
