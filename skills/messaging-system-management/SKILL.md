---
name: messaging-system-management
description: Designs observability, control, replay and operational safety for messaging integrations. Use when adding monitoring, wire taps, message stores, test messages, detours or remediation runbooks.
aliases:
  - eip-system-management
  - operate-message-based-integrations
  - messaging-operations
---

# Messaging System Management

## When to use

Use when adding monitoring, tracing, replay, audit, control channels, test messages, message stores, detours or operational remediation for message-based integrations.

## Objective

Design operational controls for message-based integrations so they can be observed, tested, controlled, recovered and audited in production.

## Procedure

1. Select management patterns:
   - Control Bus for operational commands and management signals.
   - Detour to reroute messages through alternate processing paths.
   - Wire Tap to inspect or copy message traffic without disrupting the main flow.
   - Message History to record processing path and handling events.
   - Message Store to persist messages for audit, replay or recovery.
   - Smart Proxy to preserve correlation or mediate replies.
   - Test Message to verify integration health.
   - Channel Purger to clear channels safely in controlled situations.
2. Define observability requirements: logs, metrics, traces, message lineage and dashboards.
3. Define operational runbooks for retries, dead-letter replay, poison messages, backfills, schema failures and consumer lag.
4. Define audit boundaries: what is stored, where, for how long and under whose ownership.
5. Add security controls: access control, encryption, secret handling, PII masking and administrative action logging.
6. Validate non-functional requirements using load, soak, failover, replay and chaos tests.

## Required outputs

- Operational pattern selection
- Observability and audit design
- Replay and remediation procedures
- SLOs, alerts and dashboards
- Security and compliance controls
- Test and recovery plan

## Guardrails

- Do not use Wire Tap to duplicate sensitive data without access-control and retention review.
- Do not create replay capability without idempotency and ordering analysis.
- Do not purge channels without explicit approval, backup and impact assessment.
- Do not treat logs as a substitute for message lineage.

## Related skills

- `message-based-integration-design`
- `message-channel-design`
- `message-endpoint-design`
- `eip-integration-validation`
- `observability-and-telemetry`
- `streaming-operations-and-slos`
- `incident-response-and-postmortems`

## Verification

- [ ] Operational patterns and ownership are explicit.
- [ ] Observability, audit and replay controls are defined.
- [ ] Runbooks cover lag, poison messages and schema failures.
- [ ] Security and retention controls are stated.
- [ ] Residual risks and assumptions are recorded.

## References

- Enterprise Integration Patterns, System Management patterns: https://www.enterpriseintegrationpatterns.com/patterns/messaging/
