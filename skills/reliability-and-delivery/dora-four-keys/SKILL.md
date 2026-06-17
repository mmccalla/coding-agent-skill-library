---
name: dora-four-keys
description: Uses DevOps Research and Assessment Four Keys to improve delivery performance without gaming metrics. Use when measuring deployment frequency, lead time, change failure rate, or recovery time.
---

# DORA Four Keys

## When to use
Use this skill when improving or analysing deployment frequency, lead time for changes, change failure rate, failed deployment recovery time, CI/CD flow, release process, delivery bottlenecks, deployment safety or engineering productivity evidence.

## Objective

Improve software delivery performance using the DORA Four Keys while preserving reliability, safety, quality and learning culture.

## The Four Keys

| Metric | Meaning |
|---|---|
| Deployment frequency | How often the organisation successfully deploys to production or users. |
| Lead time for changes | Time from code committed to successfully running in production. |
| Change failure rate | Percentage of deployments causing degraded service, incidents, rollback or hotfix. |
| Failed deployment recovery time | Time to restore service after a deployment failure. |

## Operating procedure

1. Identify the delivery workflow being measured.
2. Define what counts as a deployment.
3. Define the start and end point for lead time.
4. Define what counts as change failure.
5. Define how recovery time is measured.
6. Collect baseline data.
7. Identify bottlenecks or failure patterns.
8. Recommend improvement experiments.
9. Add or improve telemetry where measurement is weak.
10. Reassess after changes.

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
```

## Rules

- Do not use DORA metrics to rank or punish individuals.
- Do not increase deployment frequency by reducing quality gates irresponsibly.
- Do not reduce lead time by bypassing security, tests or approvals.
- Do not hide failures by redefining incidents away.
- Do not optimise one metric while damaging another.
- Do not treat DORA as a dashboard-only exercise; use it to drive improvement experiments.
- Do not confuse DORA Four Keys with EU Digital Operational Resilience Act compliance.

## Improvement levers

| Problem | Possible improvement |
|---|---|
| Low deployment frequency | smaller batches, feature flags, better test automation |
| Long lead time | remove queue time, improve CI speed, reduce manual gates |
| High change failure rate | better tests, progressive delivery, smaller changes, observability |
| Slow recovery | rollback automation, runbooks, incident drills, canaries, feature flags |

## MAS DataOps MCP examples

Use DORA metrics for API/service deployments, validation-rule release process, source adapter changes, workflow engine changes, MCP tool changes, UI/dashboard releases and infrastructure changes.

For data-quality rules, define related metrics:

```text
rule_lead_time = draft created → approved and safely active
rule_failure_rate = approved rule changes causing incorrect quarantine/refined routing
rule_recovery_time = time to disable or correct a faulty rule
```

## Verification

- [ ] Metric affected and measurement source stated.
- [ ] Bottleneck or failure pattern identified.
- [ ] Improvement proposed or implemented described.
- [ ] Safety controls preserved; residual measurement risk noted.

