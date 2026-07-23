---
name: sre-practice
description: Applies SRE practices for production reliability, service ownership, resilience, toil reduction and operability. Use when owning production services, defining SLOs, or improving operational maturity.
aliases:
  - site-reliability-engineering
  - service-reliability
  - production-reliability
  - service-ownership
---

# SRE Practice

## When to use

Use this skill when working on production service design, operational readiness, reliability reviews, service ownership, resilience improvements, availability, latency, durability, on-call readiness, runbooks, safe automation, incident prevention or operational risk reduction.

## Objective

Improve service reliability by connecting user impact, service objectives, operational evidence, automation, incident learning and safe release practices.

## Procedure

1. Identify the service and its users.
2. Define the user-visible capability being protected.
3. Identify critical user journeys and dependencies.
4. Define or confirm SLIs and SLOs.
5. Identify failure modes and blast radius.
6. Check operational readiness: alerts, dashboards, logs, traces, runbooks and ownership.
7. Prefer simple, observable, reversible changes.
8. Add or update tests for reliability-critical behaviour.
9. Add operational evidence: metric, log, trace, dashboard, alert or runbook update.
10. State residual reliability risk and recommended next action.

## SRE design questions

```text
Service: What service or workflow is affected?
User impact: What user-visible failure are we preventing or reducing?
Objective: What reliability target or SLO is relevant?
Signal: How will we know the service is healthy or unhealthy?
Response: What should happen when the signal breaches threshold?
Recovery: How is the service restored?
Evidence: What metric, trace, log, test or runbook proves the change?
```

## Rules

- Do not equate reliability with “add more monitoring”.
- Do not add alerts without a clear owner and action.
- Do not pursue 100% reliability unless the requirement is explicit and justified.
- Do not improve backend health metrics while ignoring user-visible outcomes.
- Do not automate recovery that can make the failure worse.
- Do not hide failures behind retries without recording them.
- Do not introduce operational complexity without a clear reliability benefit.

## Implementation guidance

Prefer bounded retries with timeouts, circuit breakers, idempotent operations, meaningful health checks, graceful degradation, bulkheads, runbooks, clear service ownership and dashboards aligned to SLIs.

## Optional overlay

For product-specific DataOps/MCP examples, load `skills_docs/overlays/mas-dataops-mcp-overlay.md`.

## References

- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)
- [Google SRE Workbook](https://sre.google/workbook/table-of-contents/)

## Verification

- [ ] User impact and SLI/SLO or operational signal addressed.
- [ ] Reliability controls added or changed described.
- [ ] Tests, checks and observability evidence reported.
- [ ] Runbook updates and residual reliability risk stated.
