---
name: observability-and-telemetry
description: Designs actionable logs, metrics, traces, dashboards and alerts for reliable operations. Use when instrumenting services, defining SLIs, or improving on-call signal quality.
---

# Observability and Telemetry

## When to use

Use this skill when adding or reviewing logs, metrics, traces, dashboards, alerts, telemetry standards, OpenTelemetry instrumentation, service health checks, operational evidence or workflow monitoring.

## Objective

Make service behaviour understandable from the outside so operators can detect, diagnose and respond to user-impacting issues quickly.

## Procedure

1. Identify the user journey or service behaviour to observe.
2. Define the key questions operators need to answer.
3. Select metrics for symptoms and causes.
4. Add structured logs for important decisions and failures.
5. Add traces across service boundaries and tool calls.
6. Create dashboards around user journeys and SLOs.
7. Add alerts only when action is required.
8. Include runbook links in alerts.
9. Avoid logging secrets or unnecessary sensitive data.
10. Validate telemetry in local or test environment.

## Telemetry types

| Type | Use for | Anti-pattern |
|---|---|---|
| Metrics | trends, rates, thresholds, SLOs | high-cardinality unbounded labels |
| Logs | discrete events, decisions, errors | unstructured noisy dumps |
| Traces | request/workflow path and latency | tracing without useful spans |
| Dashboards | operational review and triage | vanity metrics |
| Alerts | urgent action | non-actionable noise |

## Required span attributes for workflows

```yaml
workflow_id: "uuid"
request_id: "uuid"
source_id: "uuid"
batch_id: "uuid"
tenant_id: "string"
workflow_type: "string"
step_name: "string"
status: "success | failure | partial"
error_type: "string"
```

## Optional overlay

For product-specific DataOps/MCP examples, load `skills_docs/overlays/mas-dataops-mcp-overlay.md`.

## Alert quality test

Before adding an alert, answer what user impact it represents, who owns it, what action the responder should take, what dashboard or runbook helps, what threshold avoids noise and how the alert will be tested.

## Rules

- Do not log secrets, tokens, credentials or raw sensitive records.
- Do not alert on every internal cause if one user-impacting symptom alert is enough.
- Do not create dashboards with no decisions attached.
- Do not use unbounded labels such as raw user ID, record ID or SQL text.
- Do not mark a service healthy if dependencies required for readiness are unavailable.
- Do not rely only on logs where metrics or traces are needed.

## References

- [OpenTelemetry documentation](https://opentelemetry.io/docs/)
- [OpenTelemetry specification](https://opentelemetry.io/docs/specs/otel/)

## Verification

- [ ] Telemetry added or changed listed.
- [ ] User journey or SLO coverage stated.
- [ ] Sensitive-data handling considered.
- [ ] Validation performed and observability gaps noted.
