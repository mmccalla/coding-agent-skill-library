---
name: message-endpoint-design
description: Designs reliable message producers, consumers, gateways and receiver semantics. Use when building adapters, transactional clients, competing consumers, durable subscribers or idempotent receivers.
aliases:
  - eip-message-endpoints
  - implement-message-endpoints
  - messaging-endpoint-design
---

# Message Endpoint Design

## When to use

Use when building consumers, producers, adapters, service activators, gateways, transactional clients or event-driven processing components for message-based integrations.

## Objective

Design and implement reliable message-producing and message-consuming endpoints with explicit transaction, retry, concurrency and idempotency behaviour.

## Procedure

1. Select endpoint pattern:
   - Message Endpoint for application-specific send/receive logic.
   - Messaging Gateway to isolate application code from messaging APIs.
   - Messaging Mapper to map domain objects to messages.
   - Transactional Client when message send/receive must be transactionally coordinated.
   - Polling Consumer when the application controls receive timing.
   - Event-driven Consumer when the broker/runtime invokes processing.
   - Competing Consumers for horizontal consumption and throughput.
   - Selective Consumer to consume only messages matching criteria.
   - Durable Subscriber when pub/sub messages must survive subscriber downtime.
   - Idempotent Receiver where duplicate delivery is possible.
   - Service Activator to invoke application services from messages.
2. Define the transaction boundary: receive, process, persist, publish and acknowledge.
3. Implement idempotency using stable message IDs, business keys, inbox tables or deduplication stores.
4. Define retry policy: transient retry, backoff, max attempts, dead-letter and manual remediation.
5. Define concurrency, partitioning and ordering rules.
6. Expose metrics: lag, throughput, failures, duplicates, retries and processing time.

## Required outputs

- Endpoint pattern and rationale
- Transaction and acknowledgement model
- Idempotency design
- Retry and dead-letter handling
- Concurrency and ordering controls
- Implementation checklist or code skeleton, if requested

## Guardrails

- Do not acknowledge messages before durable processing unless loss is acceptable.
- Do not assume duplicate messages cannot occur.
- Do not combine business logic, broker APIs and schema mapping without clear boundaries.
- Do not scale consumers blindly where ordering or shared-state constraints exist.

## Related skills

- `message-based-integration-design`
- `message-channel-design`
- `integration-message-construction`
- `message-routing-design`
- `messaging-system-management`
- `exception-handling-and-recovery`
- `observability-and-telemetry`

## Verification

- [ ] Endpoint pattern and transaction boundary are explicit.
- [ ] Idempotency and acknowledgement behaviour are defined.
- [ ] Retry and dead-letter handling are stated.
- [ ] Concurrency, ordering and metrics are covered.
- [ ] Residual risks and assumptions are recorded.

## References

- [EIP — Message Endpoint](https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessageEndpoint.html)
- [EIP — Messaging Gateway](https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessagingGateway.html)
- [EIP — Messaging Mapper](https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessagingMapper.html)
- [EIP — Transactional Client](https://www.enterpriseintegrationpatterns.com/patterns/messaging/TransactionalClient.html)
- [EIP — Polling Consumer](https://www.enterpriseintegrationpatterns.com/patterns/messaging/PollingConsumer.html)
- [EIP — Event-Driven Consumer](https://www.enterpriseintegrationpatterns.com/patterns/messaging/EventDrivenConsumer.html)
- [EIP — Competing Consumers](https://www.enterpriseintegrationpatterns.com/patterns/messaging/CompetingConsumers.html)
- [EIP — Idempotent Receiver](https://www.enterpriseintegrationpatterns.com/patterns/messaging/IdempotentReceiver.html)
- [EIP — Service Activator](https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessagingAdapter.html)
- [EIP — Durable Subscriber](https://www.enterpriseintegrationpatterns.com/patterns/messaging/DurableSubscription.html)
