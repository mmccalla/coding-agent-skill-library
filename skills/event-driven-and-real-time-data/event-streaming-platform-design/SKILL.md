---
name: event-streaming-platform-design
description: Designs shared streaming platforms, topics, partitions, tenancy, retention and replay. Use when selecting or designing Kafka, Pulsar, or Event Hubs-style platforms.
---

# Event Streaming Platform Design

## When to use
Use for Kafka, Pulsar, Event Hubs or similar streaming platform foundations.

## Objective
Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure
1. Define workloads and tenants.
2. Define naming and environments.
3. Define topic/stream lifecycle.
4. Define partitioning and retention.
5. Define schema registry policy.
6. Define access controls and quotas.
7. Define observability and support model.
8. Define deprecation process.

## Required outputs
- Platform model
- Topic strategy
- Partition/retention policy
- Schema/access policy
- Quotas
- Support model

## Best-practice alignment
Apply event-driven best practice: business event semantics, producer/consumer ownership, schema contracts, compatibility, ordering, partitioning, idempotency, replay, retention, lineage, observability and operational SLOs.

## Quality checks
- Topics have owners.
- Partition strategy is explicit.
- Retention supports replay/compliance.
- Access is least privilege.

## Avoid
Do not allow unowned shared topics.

## Verification
State artefacts produced, decisions made, assumptions, risks, validation performed and files changed.
