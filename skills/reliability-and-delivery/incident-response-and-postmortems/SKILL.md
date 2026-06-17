---
name: incident-response-and-postmortems
description: Handles incidents, recovery, postmortems and corrective actions with blameless, evidence-led practice. Use when responding to outages, writing postmortems, or defining incident runbooks.
---

# Incident Response and Postmortems

## When to use
Use this skill for incidents, outages, degraded service, failed deployments, failed workflows, data-quality pipeline failures, operational recovery, postmortems, corrective actions and incident runbooks.

## Objective

Restore service safely, preserve evidence, communicate clearly, learn from failure and implement corrective actions that reduce recurrence or impact.

## Incident response procedure

1. Confirm the incident and user impact.
2. Assign incident roles where appropriate.
3. Establish severity.
4. Stabilise the system.
5. Preserve evidence: logs, metrics, traces, deployment changes, workflow IDs and audit events.
6. Communicate status and next update time.
7. Mitigate or rollback using the safest available path.
8. Validate recovery from user-visible signals.
9. Record timeline and actions.
10. Create postmortem and corrective actions.

## Severity model

| Severity | Meaning | Example |
|---|---|---|
| SEV1 | Critical user or business impact | refined writes failing globally |
| SEV2 | Major degradation or partial outage | validation service failing for key source |
| SEV3 | Limited impact with workaround | single dashboard degraded |
| SEV4 | Low impact or internal issue | non-critical alert misconfigured |

## Postmortem structure

```markdown
# Postmortem: <incident title>

## Summary
What happened and who was affected.

## Impact
User, service, data, security or operational impact.

## Timeline
Timestamped events.

## Detection
How the issue was detected and whether detection was timely.

## Root cause and contributing factors
Technical, process, dependency and operational factors.

## What went well
Effective actions or controls.

## What went poorly
Gaps, delays or confusion.

## Where we got lucky
Risks that did not materialise.

## Corrective actions
Owner, due date, priority and validation method.
```

## Rules

- Do not blame individuals.
- Do not delete or overwrite incident evidence.
- Do not hide uncertainty in incident updates.
- Do not declare recovery based only on infrastructure health; validate user-visible behaviour.
- Do not create vague corrective actions such as “be more careful”.
- Do not implement risky remediation during an incident unless necessary and approved.
- Do not skip postmortems for high-impact or repeated incidents.

## MAS DataOps MCP incident examples

Examples include source-to-refined workflows stuck in running state, failed records not written to quarantine, passing records not written to refined, validation rules incorrectly promoted, evidence bundles missing and dashboards showing stale quality status.

## Verification

- [ ] Incident type and user impact stated.
- [ ] Mitigation or recovery actions documented.
- [ ] Evidence preserved and postmortem or runbook updates noted.
- [ ] Corrective actions and follow-up stated.

