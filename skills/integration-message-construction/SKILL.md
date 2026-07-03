---
name: integration-message-construction
description: Defines integration message intent, envelopes, identifiers and lifecycle metadata. Use when creating command, event, document or request-reply message contracts and schemas.
aliases:
  - eip-message-construction
  - construct-integration-messages
  - message-construction
---

# Integration Message Construction

## When to use

Use when creating message schemas, event contracts, command payloads, request/reply payloads, metadata envelopes or compatibility rules for enterprise integrations.

## Objective

Define well-formed integration messages with clear intent, stable contracts and sufficient metadata for routing, processing, observability and recovery.

## Procedure

1. Classify message intent:
   - Command Message: instructs a receiver to perform an action.
   - Document Message: transfers a data structure for consumption.
   - Event Message: states that something happened.
   - Request-Reply: asks for a response, usually with Correlation Identifier and Return Address.
2. Define envelope and payload separately.
3. Include minimum standard metadata:
   - message_id
   - correlation_id
   - causation_id where useful
   - producer
   - produced_at
   - schema_name and schema_version
   - message_type
   - content_type / format indicator
   - expiry where relevant
   - traceparent or equivalent trace context
4. Define lifecycle semantics: creation, validation, expiry, retry, replay and archival.
5. Define compatibility rules: additive changes, deprecation, schema evolution and consumer tolerance.
6. Apply privacy and minimisation: include only data required by consumers; use references or Claim Check for large or sensitive payloads.

## Pattern selection guide

- Use Correlation Identifier to match replies, callbacks or related messages.
- Use Return Address when replies must be routed dynamically.
- Use Message Sequence when messages must be assembled or ordered as a set.
- Use Message Expiration when stale messages must not be processed.
- Use Format Indicator when multiple payload encodings or schema versions are possible.
- Use Claim Check when payload data is large, sensitive or better stored out-of-band.

## Required outputs

- Message type and intent
- Envelope schema
- Payload schema outline
- Validation and compatibility rules
- Privacy, security and retention considerations
- Example message, if requested

## Guardrails

- Do not model commands as events; commands request action, events record facts.
- Do not place routing-critical data only inside opaque payloads.
- Do not expose internal database schemas as integration contracts.
- Do not overload one message type with multiple unrelated meanings.

## Related skills

- `message-based-integration-design`
- `message-channel-design`
- `message-routing-design`
- `message-transformation-design`
- `schema-registry-and-contracts`
- `event-modeling`
- `data-contract-design`

## Verification

- [ ] Message intent is explicit and not ambiguous.
- [ ] Envelope and payload are separated.
- [ ] Required metadata fields are defined.
- [ ] Compatibility and privacy rules are stated.
- [ ] Residual risks and assumptions are recorded.

## References

- Enterprise Integration Patterns, Message Construction patterns: https://www.enterpriseintegrationpatterns.com/patterns/messaging/
