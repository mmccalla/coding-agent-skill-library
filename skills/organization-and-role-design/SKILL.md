---
name: organization-and-role-design
description: Defines roles, decision rights, accountabilities, team boundaries and ownership. Use when designing teams, RACI matrices, or architecture governance roles.
aliases:
  - organisation-and-role-design
  - team-and-role-design
---

# Organisation and Role Design

## When to use
Use when clarifying who owns outcomes, decisions, data, services or capabilities.

## Objective
Produce a practical, concise, traceable architecture artefact that a coding agent can use to guide implementation or review.

## Procedure
1. Identify outcomes and decisions.
2. Define accountable roles.
3. Define consulted/informed roles.
4. Define escalation paths.
5. Define team boundaries.
6. Identify capacity/skill gaps.
7. Align to operating model.
8. Validate with stakeholders.

## Required outputs
- Role/accountability map
- Decision rights
- Escalation paths
- Team boundaries
- Gaps/risks

## Best-practice alignment
Align with **BIZBOK** business architecture practice: keep capabilities, value streams, processes, organisation, information concepts, initiatives and metrics separate, then link them from strategy to execution.

## Quality checks
- Accountability is not assigned to a committee.
- Decision rights are clear.
- Role overload is visible.

## Avoid
Do not confuse consultation with accountability.

## Mini example

For a shared streaming platform, assign one accountable platform owner, domain event owners, data stewards and support roles. Use RACI only after naming decision rights such as schema approval, access approval and incident escalation. If one role owns too many critical decisions, flag capacity risk and define an escalation path.

## References

- Business Architecture Guild BIZBOK (capabilities, value streams, organisation, information): https://www.businessarchitectureguild.org/
- The Open Group TOGAF Standard (business architecture domain): https://www.opengroup.org/togaf

## Verification

- [ ] Required artefacts produced and linked to scope.
- [ ] Decisions, assumptions and risks stated explicitly.
- [ ] Quality checks or validation performed.
- [ ] Files changed reported with traceability preserved.
