---
name: message-routing-design
description: Designs message routing, split, aggregate, resequence and orchestration flows. Use when building routers, filters, scatter-gather, process managers, routing slips or dynamic routes.
aliases:
  - eip-message-routing
  - design-message-routing
  - messaging-routing-design
---

# Message Routing Design

## When to use

Use for routers, filters, splitter/aggregator flows, scatter-gather, process managers, orchestration, dynamic routing and routing slips in message-based integrations.

## Objective

Design routing logic that directs messages to the correct receivers while preserving clarity, resilience, testability and operational control.

## Procedure

1. Identify whether routing is static, content-based, rule-driven, dynamic, recipient-list based or process-state driven.
2. Select routing patterns:
   - Message Router for general routing abstraction.
   - Content-based Router when route depends on message content.
   - Message Filter when irrelevant messages should be discarded or ignored.
   - Dynamic Router when routing rules change at runtime.
   - Recipient List when one message must go to multiple selected receivers.
   - Splitter when one message must be decomposed into smaller messages.
   - Aggregator when related messages must be recombined.
   - Resequencer when messages must be reordered.
   - Scatter-Gather when a request is broadcast and responses are consolidated.
   - Routing Slip when the route is carried with the message.
   - Process Manager when routing depends on long-running state.
3. Separate business routing rules from transport mechanics.
4. Make correlation, sequencing, timeout and partial-failure handling explicit.
5. Define deterministic tests for each route and edge case.
6. Instrument each routing decision for traceability.

## Required outputs

- Routing topology
- Pattern selection and rationale
- Routing rules
- Correlation, sequencing and timeout strategy
- Failure and compensation behaviour
- Test cases

## Guardrails

- Do not embed undocumented routing rules in ad hoc code.
- Do not create a central router that becomes an ungoverned business rules engine.
- Do not aggregate without clear completeness, timeout and partial-response rules.
- Do not use Process Manager where stateless routing is sufficient.

## Related skills

- `message-based-integration-design`
- `message-channel-design`
- `integration-message-construction`
- `message-transformation-design`
- `message-endpoint-design`
- `process-modeling`
- `stream-processing-patterns`

## Verification

- [ ] Routing patterns and rules are explicit.
- [ ] Correlation, sequencing and timeouts are defined.
- [ ] Failure and compensation behaviour is stated.
- [ ] Test cases cover routes and edge cases.
- [ ] Residual risks and assumptions are recorded.

## References

- Enterprise Integration Patterns, Message Routing patterns: https://www.enterpriseintegrationpatterns.com/patterns/messaging/
