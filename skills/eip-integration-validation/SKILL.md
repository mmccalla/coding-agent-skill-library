---
name: eip-integration-validation
description: Reviews integration designs against EIP, reliability, security and operability criteria. Use when validating architecture decisions, message topologies, broker configs or implementation plans.
aliases:
  - eip-validation
  - validate-integration-design-against-eip
  - integration-design-validation
---

# EIP Integration Validation

## When to use

Use after producing or receiving an integration design, architecture decision record, sequence diagram, event contract, API/event topology, broker configuration or implementation plan that should be checked against Enterprise Integration Patterns and production operability criteria.

## Objective

Review integration designs and implementations against EIP, distributed-systems risks and production operability criteria, and return severity-rated findings with precise remediation.

## Procedure

1. Classify each integration interaction as command, event, document, request/reply, stream, batch or query.
2. Map each interaction to EIP categories:
   - Integration style.
   - Channel.
   - Message construction.
   - Routing.
   - Transformation.
   - Endpoint.
   - System management.
3. Check correctness:
   - Pattern selection fits the problem.
   - Message intent is not ambiguous.
   - Contracts are versioned and testable.
   - Routing, correlation and sequencing are explicit.
   - Transformation preserves semantics.
   - Endpoint transaction and acknowledgement behaviour is safe.
4. Check resilience:
   - Duplicate handling.
   - Retry and backoff.
   - Dead-letter and invalid-message paths.
   - Back-pressure and consumer lag.
   - Ordering and replay.
   - Disaster recovery.
5. Check governance:
   - Ownership of messages, channels and schemas.
   - Data minimisation and PII handling.
   - Access control and encryption.
   - Auditability and retention.
   - Operational runbooks.
6. Rate issues by severity: Critical, High, Medium, Low.
7. Provide precise remediation steps, not generic advice.

## Required outputs

- Executive summary
- Pattern mapping table
- Findings by severity
- Recommended design changes
- Residual risks
- Test cases required before production

## Acceptance criteria

- Every integration flow has a named pattern or a justified exception.
- Every message has intent, schema, owner, version and metadata.
- Every channel has ownership, security, retention and error handling.
- Every consumer has retry, idempotency and acknowledgement behaviour.
- Every production flow has observability and runbook coverage.

## Guardrails

- Do not approve designs that lack dead-letter or invalid-message handling for critical flows.
- Do not approve non-idempotent consumers for at-least-once delivery unless duplicate delivery is impossible by construction.
- Do not approve canonical models without ownership and version governance.
- Do not approve designs where routing, transformation or process state is undocumented.

## Related skills

- `message-based-integration-design`
- `message-channel-design`
- `integration-message-construction`
- `message-routing-design`
- `message-transformation-design`
- `message-endpoint-design`
- `messaging-system-management`
- `code-review-and-quality`

## Verification

- [ ] Each flow is mapped to an EIP category or justified exception.
- [ ] Findings are severity-rated with remediation steps.
- [ ] Resilience and governance checks are complete.
- [ ] Residual risks and required tests are stated.
- [ ] Acceptance criteria are assessed explicitly.

## References

- EIP Table of Contents: https://www.enterpriseintegrationpatterns.com/patterns/messaging/toc.html
- EIP — Messaging Systems introduction: https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessagingComponentsIntro.html
- EIP — Messaging Channels introduction: https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessagingChannelsIntro.html
- EIP — Message Construction introduction: https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessageConstructionIntro.html
- EIP — Message Routing introduction: https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessageRoutingIntro.html
- EIP — Message Transformation introduction: https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessageTransformationIntro.html
- EIP — Messaging Endpoints introduction: https://www.enterpriseintegrationpatterns.com/patterns/messaging/MessagingEndpointsIntro.html
- EIP — System Management introduction: https://www.enterpriseintegrationpatterns.com/patterns/messaging/SystemManagementIntro.html

