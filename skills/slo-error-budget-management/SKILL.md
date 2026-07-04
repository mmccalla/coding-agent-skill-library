---
name: slo-error-budget-management
description: Defines SLIs, SLOs, error budgets, burn rates and release gates. Use when setting reliability targets, error budgets, or release gating policies.
---

# SLO and Error Budget Management

## When to use

Use this skill when defining or changing SLIs, SLOs, error budgets, burn-rate alerts, reliability targets, release gates, service-level dashboards, reliability acceptance criteria or production readiness checks.

## Objective

Create measurable reliability objectives that reflect user experience and guide engineering trade-offs between reliability, feature delivery and operational risk.

## Procedure

1. Identify the user journey or service capability.
2. Define the service boundary.
3. Select SLIs that measure user-visible outcomes.
4. Define an SLO target and measurement window.
5. Calculate the error budget.
6. Define burn-rate thresholds and alerting.
7. Define the error-budget policy.
8. Link release decisions to error-budget state.
9. Add telemetry and dashboards to measure the SLI.
10. Add tests or checks that protect the SLI where practical.

## SLI examples

| Service area | Possible SLI |
|---|---|
| API | proportion of successful requests |
| API latency | proportion of requests below threshold |
| Workflow | proportion of workflows completed successfully |
| Batch processing | proportion of batches completed within SLA |
| Data quality | proportion of records successfully validated and routed |
| Quarantine | proportion of failed records written to quarantine |
| Refined write | proportion of passing records written successfully |
| Evidence | proportion of workflows with complete evidence bundles |

## SLO template

```yaml
service: "source-to-refined workflow"
user_journey: "process onboarded source batch"
sli:
  name: "workflow_success_rate"
  definition: "successful source-to-refined runs / total source-to-refined runs"
slo:
  target: "99.0%"
  window: "28 days"
error_budget:
  allowed_failure_rate: "1.0%"
burn_rate_alerts:
  # Prefer multi-window, multi-burn-rate alerts (long AND short windows).
  # Simplified budget-spend examples below; implement with burn-rate thresholds.
  fast_burn: "2% budget consumed in 1 hour"
  slow_burn: "10% budget consumed in 3 days"
policy:
  if_budget_healthy: "normal releases allowed"
  if_budget_at_risk: "increase review and testing"
  if_budget_exhausted: "freeze risky releases except reliability fixes"
```

## Multi-window burn-rate alerting

Prefer **multi-window, multi-burn-rate** alerts from the Google SRE Workbook: fire only when both a long window and a short window exceed the burn-rate threshold (AND logic). This reduces false pages from brief spikes while still catching sustained budget burn.

Example pattern for a 30-day SLO window:

| Severity | Long window | Short window | Typical burn-rate threshold |
|---|---|---|---|
| Page (fast burn) | 1 hour | 5 minutes | high (e.g. 14.4×) |
| Page / ticket (medium) | 6 hours | 30 minutes | medium (e.g. 6×) |
| Ticket (slow burn) | 3 days | 6 hours | near 1× |

Use the simplified budget-spend examples only as illustrations; implement alerts on burn rate relative to the error budget, not raw error rate alone.

## Rules

- Do not define SLOs only from infrastructure metrics.
- Do not set SLOs without a measurement method.
- Do not create alerts for every small SLO fluctuation.
- Do not use SLOs as individual performance targets.
- Do not change SLOs to hide poor reliability.
- Do not release high-risk changes when the error budget policy says stop.

## Optional overlay

For product-specific DataOps/MCP examples, load `skills_docs/overlays/mas-dataops-mcp-overlay.md`.

## References

- [Google SRE Workbook — Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)
- [Google SRE Book — Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)

## Verification

- [ ] SLI, SLO target and measurement window stated.
- [ ] Error budget policy and burn-rate alerting defined.
- [ ] Telemetry source and release impact noted.
- [ ] Residual measurement risk stated.
