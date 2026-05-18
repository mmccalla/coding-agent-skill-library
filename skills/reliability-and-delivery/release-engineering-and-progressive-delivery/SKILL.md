---
name: release-engineering-and-progressive-delivery
description: Improve deployment safety using release engineering, staged rollout, canary, blue/green, feature flags, rollback and deployment gates.
---

# Release Engineering and Progressive Delivery

## When to use this skill

Use this skill for deployment pipelines, release gates, rollback, canary releases, blue/green deployments, feature flags, schema or migration releases, production promotion, deployment safety and blast-radius reduction.

## Objective

Ship changes safely by reducing blast radius, validating progressively, enabling fast rollback and linking deployment decisions to evidence.

## Operating procedure

1. Identify the change and production risk.
2. Classify the release type: code, config, schema, policy, model, rule, infrastructure or data pipeline.
3. Define pre-release checks.
4. Define rollout strategy.
5. Define health and success signals.
6. Define rollback or disable path.
7. Define data compatibility requirements.
8. Add deployment evidence and audit.
9. Validate in the smallest safe environment first.
10. Monitor after release.

## Rollout strategies

| Strategy | Use when |
|---|---|
| Feature flag | behaviour can be toggled independently |
| Canary | gradual traffic or tenant exposure is possible |
| Blue/green | full environment swap is practical |
| Rolling deploy | stateless or horizontally scaled service |
| Shadow mode | output can be compared without user impact |
| Dark launch | dependencies can be exercised before exposure |
| Manual gate | risk requires human review |
| Freeze | error budget exhausted or incident active |

## Release checklist

```text
tests passed
security checks passed
migration compatibility checked
config validated
feature flag or rollback path exists
observability exists
owner identified
deployment window agreed where needed
user impact understood
evidence recorded
```

## Rules

- Do not deploy without rollback or disable path.
- Do not combine unrelated changes into one risky release.
- Do not deploy schema-breaking changes without compatibility strategy.
- Do not use feature flags without ownership and removal plan.
- Do not promote generated rules, policies or model behaviour without evaluation evidence.
- Do not ignore SLO/error budget state when releasing high-risk changes.
- Do not treat a successful deployment as a successful release until user-visible signals are healthy.

## MAS DataOps MCP release guidance

Use progressive delivery for new validation rules, generated expectation suites, cleansing rules, quarantine writer changes, refined writer changes, policy changes, source adapter changes and workflow routing changes.

Recommended pattern for new data-quality rules:

```text
draft
→ evaluate on sample
→ approve
→ shadow mode
→ warning-only mode
→ blocking mode for limited scope
→ broader production rollout
```

## Verification

Report release risk classification, rollout strategy, pre-release checks, rollback path, health signals, tests/checks run and residual release risk.
