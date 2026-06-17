---
name: ci-cd-and-automation
description: Use when designing or changing build, test or deployment automation that needs explicit safety, permissions and verification.
---

# CI/CD and Automation

## When to use
Use this skill when modifying pipelines, build automation, release jobs, deployment gates or other automation that can change delivery behaviour.

## Objective

Keep automation safe, observable and least-privilege while still reducing manual effort and release risk.

## Operating procedure

1. Identify the pipeline stage and purpose.
2. List required inputs, secrets, permissions and outputs.
3. Add or preserve safety checks before the risky step runs.
4. Keep build, test and deploy responsibilities separated when practical.
5. Add failure reporting that is actionable and easy to trace.
6. Verify the pipeline with the narrowest useful run.

## Rules

- Do not echo secrets in logs.
- Do not widen permissions when a narrower path works.
- Do not bypass quality gates to make the pipeline pass.
- Do not make deploy steps irreversible without an explicit reason.

## Verification

- [ ] Pipeline or automation change scope stated.
- [ ] Permissions and safety controls preserved.
- [ ] Tests or checks run reported.
- [ ] Rollback path and residual delivery risk noted.

