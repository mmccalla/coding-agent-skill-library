---
name: observability-and-telemetry
description: Designs actionable logs, metrics, traces, dashboards and alerts for reliable operations. Use when instrumenting services, defining SLIs, or improving on-call signal quality.
---

# Observability and Telemetry

## When to use
Use this skill when adding or reviewing logs, metrics, traces, dashboards, alerts, telemetry standards, OpenTelemetry instrumentation, service health checks, operational evidence or workflow monitoring.

## Objective

Make service behaviour understandable from the outside so operators can detect, diagnose and respond to user-impacting issues quickly.

## Operating procedure

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

## Required metrics for MAS DataOps MCP

```text
source_onboarding_count
schema_discovery_success_rate
metadata_generation_success_rate
profiling_success_rate
rule_generation_acceptance_rate
validation_pass_rate
validation_failure_rate
cleansing_success_rate
quarantine_record_count
quarantine_rate
refined_record_count
refined_write_success_rate
evidence_bundle_completion_rate
policy_denial_rate
tool_error_rate
workflow_success_rate
workflow_failure_rate
workflow_duration_seconds
```

## Alert quality test

Before adding an alert, answer what user impact it represents, who owns it, what action the responder should take, what dashboard or runbook helps, what threshold avoids noise and how the alert will be tested.

## Rules

- Do not log secrets, tokens, credentials or raw sensitive records.
- Do not alert on every internal cause if one user-impacting symptom alert is enough.
- Do not create dashboards with no decisions attached.
- Do not use unbounded labels such as raw user ID, record ID or SQL text.
- Do not mark a service healthy if dependencies required for readiness are unavailable.
- Do not rely only on logs where metrics or traces are needed.

## Verification

Report telemetry added or changed, user journey or SLO covered, metrics/logs/traces/dashboards/alerts affected, sensitive-data handling, validation performed and residual observability gaps.
