---
name: slo-error-budget-management
description: Defines SLIs, SLOs, error budgets, burn rates and release gates. Use when setting reliability targets, error budgets, or release gating policies.
---

# SLO and Error Budget Management

## When to use
Use this skill when defining or changing SLIs, SLOs, error budgets, burn-rate alerts, reliability targets, release gates, service-level dashboards, reliability acceptance criteria or production readiness checks.

## Objective

Create measurable reliability objectives that reflect user experience and guide engineering trade-offs between reliability, feature delivery and operational risk.

## Operating procedure

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
  fast_burn: "2% budget consumed in 1 hour"
  slow_burn: "10% budget consumed in 3 days"
policy:
  if_budget_healthy: "normal releases allowed"
  if_budget_at_risk: "increase review and testing"
  if_budget_exhausted: "freeze risky releases except reliability fixes"
```

## Rules

- Do not define SLOs only from infrastructure metrics.
- Do not set SLOs without a measurement method.
- Do not create alerts for every small SLO fluctuation.
- Do not use SLOs as individual performance targets.
- Do not change SLOs to hide poor reliability.
- Do not release high-risk changes when the error budget policy says stop.

## MAS DataOps MCP guidance

Recommended SLO candidates include `source_onboarding_success_rate`, `schema_discovery_success_rate`, `validation_run_success_rate`, `quarantine_write_success_rate`, `refined_write_success_rate`, `evidence_bundle_completion_rate`, `workflow_completion_latency` and `policy_decision_latency`.

## Verification

- [ ] SLI, SLO target and measurement window stated.
- [ ] Error budget policy and burn-rate alerting defined.
- [ ] Telemetry source and release impact noted.
- [ ] Residual measurement risk stated.

