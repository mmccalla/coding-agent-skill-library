---
name: toil-reduction-and-automation
description: Identify and reduce repetitive operational work through safe, tested, observable and reversible automation.
---

# Toil Reduction and Automation

## When to use this skill

Use this skill for repetitive manual operations, support tasks, deployments, data-quality remediation, report generation, repeated incident actions, operational scripts, runbook automation and workflow automation.

## Objective

Reduce toil without increasing operational risk, hiding judgement, weakening approval controls or creating unowned automation.

## Toil definition

Treat work as toil when it is manual, repetitive, automatable, tactical, interrupt-driven, linearly scaling with service growth and low in enduring value.

## Operating procedure

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

## MAS DataOps MCP examples

Good candidates include routine validation summaries, quarantine review tasks, re-running validation after approved remediation, collecting evidence bundles, checking stale rule sets, schema-change alerts and runbook diagnostics.

High-risk automation requiring approval includes promoting generated rules, writing to refined production datasets, accepting quarantine exceptions, deleting quarantined records, changing policy and modifying source system records.

## Verification

Report toil reduced, expected time or error reduction, safeguards added, tests/checks run, dry-run or rollback path, audit or telemetry added and residual automation risk.
