---
name: toil-reduction-and-automation
description: Reduces repetitive operational work through safe, tested, observable automation. Use when identifying toil, automating runbooks, or improving operator efficiency.
---

# Toil Reduction and Automation

## When to use
Use this skill for repetitive manual operations, support tasks, deployments, data-quality remediation, report generation, repeated incident actions, operational scripts, runbook automation and workflow automation.

## Objective

Reduce toil without increasing operational risk, hiding judgement, weakening approval controls or creating unowned automation.

## Toil definition

Treat work as toil when it is manual, repetitive, automatable, tactical, interrupt-driven, linearly scaling with service growth and low in enduring value.

## Procedure

1. Identify the repeated manual task.
2. Estimate frequency, duration, error rate and operational risk.
3. Decide whether automation is justified.
4. Identify required approvals and safeguards.
5. Build the smallest safe automation.
6. Add tests and dry-run mode where practical.
7. Add logs, metrics and audit evidence.
8. Preserve manual override or rollback.
9. Document ownership and runbook usage.
10. Measure toil reduction after deployment.

## Automation safety checklist

```text
dry-run mode available
inputs validated
scope bounded
idempotent where possible
timeouts defined
retries bounded
audit events emitted
errors visible
rollback or compensation documented
human approval retained for high-risk actions
```

## Rules

- Do not automate a poorly understood or unstable process first; stabilise it.
- Do not automate judgement-heavy decisions without human approval.
- Do not remove approval gates for high-risk actions.
- Do not create scripts that require broad credentials when narrow permissions are sufficient.
- Do not hide failures behind automation.
- Do not create unowned background jobs.
- Do not optimise a rare task at the cost of high complexity.

## Optional overlay

For product-specific DataOps/MCP examples, load `skills_docs/overlays/mas-dataops-mcp-overlay.md`.

## References

- Google SRE Book — Eliminating Toil: https://sre.google/sre-book/eliminating-toil/

## Verification

- [ ] Toil reduced and expected benefit stated.
- [ ] Safeguards, dry-run or rollback path documented.
- [ ] Tests or checks run reported.
- [ ] Audit or telemetry added; residual automation risk stated.

