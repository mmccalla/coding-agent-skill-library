---
name: message-channel-design
description: Designs message channels, delivery guarantees and error-channel boundaries. Use when defining queues, topics, streams, dead-letter handling, bridges, adapters or channel ownership.
aliases:
  - eip-message-channels
  - design-message-channels
  - messaging-channel-design
---

# Message Channel Design

## When to use

Use when defining queues, topics, streams, event buses, pub/sub channels, dead-letter handling, bridges, adapters or delivery guarantees for message-based integrations.

## Objective

Design message channels that transport messages safely, predictably and operably across distributed systems, with explicit ownership, retention and failure handling.

## Procedure

1. Identify whether each channel is command-oriented, event-oriented, document-oriented, error-oriented or control-oriented.
2. Choose the channel pattern:
   - Point-to-Point Channel for one logical consumer.
   - Publish-Subscribe Channel for fan-out to multiple independent subscribers.
   - Datatype Channel when payload type determines channel separation.
   - Invalid Message Channel for messages that are structurally or semantically invalid.
   - Dead Letter Channel for undeliverable messages.
   - Guaranteed Delivery when loss is unacceptable.
   - Channel Adapter to connect an application to the messaging system.
   - Messaging Bridge to connect different messaging systems.
   - Message Bus to provide a shared integration backbone.
3. Define channel naming, ownership, access control, retention, partitioning, ordering and schema policy.
4. Specify delivery semantics: at-most-once, at-least-once, effectively-once via idempotency, or transactional outbox/inbox.
5. Define poison-message handling: validation, retry, quarantine, dead-letter routing and reprocessing.
6. Add observability metadata: correlation ID, causation ID, producer, timestamp, schema version and trace context.

## Required outputs

- Channel catalogue
- Pattern used per channel
- Producer/consumer ownership
- Retention, ordering, replay and durability decisions
- Error-channel and dead-letter strategy
- Security and observability controls

## Guardrails

- Do not mix unrelated message types in one channel unless there is a clear compatibility and filtering strategy.
- Do not treat a dead-letter channel as a monitoring solution; it requires ownership, alerting and remediation.
- Do not promise exactly-once semantics without idempotent receivers and transaction-boundary analysis.
- Do not create shared channels without producer/consumer contract governance.

## Related skills

- `message-based-integration-design`
- `integration-message-construction`
- `message-routing-design`
- `message-endpoint-design`
- `messaging-system-management`
- `event-streaming-platform-design`
- `schema-registry-and-contracts`

## Verification

- [ ] Each channel has a named EIP pattern and owner.
- [ ] Delivery, retention and ordering decisions are explicit.
- [ ] Invalid-message and dead-letter paths are defined.
- [ ] Security and observability controls are present.
- [ ] Residual risks and assumptions are recorded.

## References

- [EIP — Message Channel](https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessageChannel.html)
- [EIP — Point-to-Point Channel](https://www.enterpriseintegrationpatterns.com/patterns/messaging/PointToPointChannel.html)
- [EIP — Publish-Subscribe Channel](https://www.enterpriseintegrationpatterns.com/patterns/messaging/PublishSubscribeChannel.html)
- [EIP — Datatype Channel](https://www.enterpriseintegrationpatterns.com/patterns/messaging/DatatypeChannel.html)
- [EIP — Invalid Message Channel](https://www.enterpriseintegrationpatterns.com/patterns/messaging/InvalidMessageChannel.html)
- [EIP — Dead Letter Channel](https://www.enterpriseintegrationpatterns.com/patterns/messaging/DeadLetterChannel.html)
- [EIP — Guaranteed Delivery](https://www.enterpriseintegrationpatterns.com/patterns/messaging/GuaranteedMessaging.html)
- [EIP — Channel Adapter](https://www.enterpriseintegrationpatterns.com/patterns/messaging/ChannelAdapter.html)
- [EIP — Messaging Bridge](https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessagingBridge.html)
- [EIP — Message Bus](https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessageBus.html)
