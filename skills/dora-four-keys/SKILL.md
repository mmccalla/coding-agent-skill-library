---
name: dora-four-keys
description: Uses DevOps Research and Assessment delivery metrics (classic Four Keys plus rework rate) to improve delivery performance without gaming metrics. Use when measuring deployment frequency, lead time, change failure rate, recovery time, or rework rate.
aliases:
  - devops-four-keys
  - delivery-metrics
  - dora-metrics
---

# DORA Delivery Metrics

## When to use
Use this skill when improving or analysing deployment frequency, lead time for changes, change failure rate, failed deployment recovery time, deployment rework rate, CI/CD flow, release process, delivery bottlenecks, deployment safety or engineering productivity evidence.

## Objective

Improve software delivery performance using DORA metrics while preserving reliability, safety, quality and learning culture.

## Metrics model (2024–2025)

DORA historically published **Four Keys**. From 2024 the model includes a fifth metric and groups measures into **throughput** and **instability**:

| Factor | Metric | Meaning |
|---|---|---|
| Throughput | Deployment frequency | How often the organisation successfully deploys to production or users. |
| Throughput | Lead time for changes | Time from code committed to successfully running in production. |
| Throughput | Failed deployment recovery time | Time to restore service after a deployment failure. |
| Instability | Change failure rate | Percentage of deployments causing degraded service, incidents, rollback or hotfix. |
| Instability | Deployment rework rate | Percentage of deployments that are unplanned work to fix production incidents. |

Keep the skill id `dora-four-keys` and alias `devops-four-keys` for discovery compatibility.

## Procedure

1. Identify the delivery workflow being measured.
2. Define what counts as a deployment.
3. Define the start and end point for lead time.
4. Define what counts as change failure.
5. Define how recovery time is measured.
6. Define how deployment rework rate is measured (unplanned incident-driven deployments).
7. Collect baseline data for throughput and instability metrics.
8. Identify bottlenecks or failure patterns.
9. Recommend improvement experiments.
10. Add or improve telemetry where measurement is weak.
11. Reassess after changes.

## Measurement guidance

```yaml
deployment_frequency:
  event: "successful production deployment"
  source: "CI/CD deployment records"

lead_time_for_changes:
  start: "commit merged to main"
  end: "deployment completed successfully"
  source: "git and CI/CD events"

change_failure_rate:
  numerator: "deployments causing incident, rollback, hotfix or customer-impacting defect"
  denominator: "all deployments"
  source: "deployment and incident records"

failed_deployment_recovery_time:
  start: "failure detected"
  end: "service restored"
  source: "incident timeline and telemetry"

deployment_rework_rate:
  numerator: "unplanned deployments triggered by production incidents"
  denominator: "all deployments"
  source: "deployment and incident records"
```

## Rules

- Do not use DORA metrics to rank or punish individuals.
- Do not increase deployment frequency by reducing quality gates irresponsibly.
- Do not reduce lead time by bypassing security, tests or approvals.
- Do not hide failures by redefining incidents away.
- Do not optimise one metric while damaging another.
- Do not treat DORA as a dashboard-only exercise; use it to drive improvement experiments.
- Do not confuse DORA delivery metrics with EU Digital Operational Resilience Act compliance.

## Improvement levers

| Problem | Possible improvement |
|---|---|
| Low deployment frequency | smaller batches, feature flags, better test automation |
| Long lead time | remove queue time, improve CI speed, reduce manual gates |
| High change failure rate | better tests, progressive delivery, smaller changes, observability |
| Slow recovery | rollback automation, runbooks, incident drills, canaries, feature flags |
| High rework rate | stronger pre-release validation, canaries, faster rollback, blameless learning |

## Optional overlay

For product-specific DataOps/MCP examples, load `skills_docs/overlays/mas-dataops-mcp-overlay.md`.

## References

- DORA metrics history (throughput and instability): https://dora.dev/insights/dora-metrics-history/
- DORA research home: https://dora.dev/

## Verification

- [ ] Metric affected and measurement source stated.
- [ ] Throughput and instability factors considered (including rework rate where relevant).
- [ ] Bottleneck or failure pattern identified.
- [ ] Improvement proposed or implemented described.
- [ ] Safety controls preserved; residual measurement risk noted.
