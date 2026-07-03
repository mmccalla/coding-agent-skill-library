---
name: message-based-integration-design
description: Designs message-based enterprise integrations and EIP topologies. Use when choosing messaging, request-reply, file transfer, broker mediation, or integration style between systems.
aliases:
  - eip-integration-design
  - enterprise-integration-design
  - design-message-based-integration
---

# Message-Based Integration Design

## When to use

Use when designing or reviewing integrations between applications, services, SaaS products, data platforms, brokers, event streams, APIs, workflows or legacy systems, and the work needs an explicit Enterprise Integration Patterns (EIP) style and topology decision.

## Objective

Produce a practical, technology-agnostic integration design that selects the right interaction style, system boundaries, message contracts and EIP pattern set before implementation.

## Procedure

1. Identify the integration intent: data synchronisation, process orchestration, event notification, command execution, query, replication or migration.
2. Prefer asynchronous messaging when temporal decoupling, resiliency, buffering, retry or independent deployment is required.
3. Select a top-level style:
   - Messaging for frequent, reliable, asynchronous exchange.
   - Request-Reply only when the caller genuinely needs a response before continuing.
   - File Transfer or batch only when latency and freshness requirements allow it.
   - Shared Database only as an exception because it couples data model, ownership and operational lifecycle.
   - Remote Procedure Invocation only for tightly scoped synchronous interactions.
4. Define system boundaries, ownership and source of truth before choosing tooling.
5. Make message contracts explicit: schema, semantics, identifiers, versioning, compatibility and lifecycle.
6. Select channel, routing, transformation, endpoint and management patterns separately; do not collapse them into one undifferentiated integration layer.
7. Document trade-offs: coupling, latency, consistency, failure isolation, replayability, supportability and governance.

## Pattern selection guide

- Use Message Bus when many applications need a shared integration backbone.
- Use Message Broker when mediation, routing or transformation must be centralised.
- Use Pipes-and-Filters when processing can be decomposed into independent sequential steps.
- Use Process Manager when long-running stateful coordination is required.
- Use Request-Reply with Correlation Identifier and Return Address when asynchronous request/response is required.

## Required outputs

- Context and assumptions
- Recommended integration style
- Selected EIP patterns and rationale
- Message/channel topology
- Reliability, ordering, security and observability controls
- Key risks and mitigations

## Guardrails

- Do not recommend synchronous APIs merely because they are simpler to code.
- Do not use a central canonical model without explicit ownership, versioning and domain governance.
- Do not hide business process state inside middleware without auditability.
- Do not conflate events, commands and documents.
- Do not rely on exactly-once delivery without explaining broker/runtime limits and idempotency requirements.

## Related skills

- `message-channel-design`
- `integration-message-construction`
- `message-routing-design`
- `message-transformation-design`
- `message-endpoint-design`
- `messaging-system-management`
- `eip-integration-validation`
- `event-driven-architecture`
- `data-integration-and-interoperability`

## Verification

- [ ] Integration intent and style are explicit.
- [ ] System boundaries and ownership are defined.
- [ ] Selected EIP patterns are justified.
- [ ] Reliability, security and operability controls are stated.
- [ ] Residual risks and assumptions are recorded.

## References

- Enterprise Integration Patterns messaging catalogue: https://www.enterpriseintegrationpatterns.com/patterns/messaging/
