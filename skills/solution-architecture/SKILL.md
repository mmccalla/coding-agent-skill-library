---
name: solution-architecture
description: Shapes solution architecture with context, NFRs, options, decisions, C4-style views, risks and fitness functions. Use when choosing structure for a system or material change across services and platforms.
aliases:
  - solution-design
  - system-solution-architecture
  - c4-solution-architecture
  - architectural-options-analysis
---

# Solution Architecture

## When to use

Use this skill when a problem needs an end-to-end solution shape: system context, non-functional requirements (NFRs), at least two credible options, a recorded decision, C4-style context and container views, risks, and governance through fitness functions or explicit exceptions. Apply it before large builds, platform choices or cross-team integrations.

## When not to use

- Use `documentation-and-adrs` when the decision is already made and only needs a durable ADR or maintainer note.
- Use `spec-driven-development` for behaviour specs and acceptance criteria once the architecture direction is set.
- Use `business-capability-modeling` for stable business abilities and capability maps rather than technical solution structure.
- Use `cloud-platform-architecture` for landing zones, tenancy and shared platform foundations (when that skill is available).

## Objective

Produce a practical solution architecture artefact that ties business context to technical structure: NFRs, compared options, a justified decision, C4-style context/container views, risks and how fitness functions or exceptions will keep the design honest over time.

## Procedure

1. Capture context: problem statement, stakeholders, constraints, assumptions and interfaces to existing systems. State what success looks like for users and operators.
2. Elicit non-functional requirements (NFRs): availability, latency, throughput, security, privacy, cost, operability, accessibility and compliance expectations with measurable targets where possible.
3. Develop at least two architecture options (prefer three when risk is high). For each option, describe structure, key technologies, trade-offs and how NFRs are met or deferred.
4. Select a decision with explicit rationale, rejected alternatives and consequences. Link to an ADR when the decision must endure.
5. Draw C4-style views: Context (system and actors) and Container (deployable/runtime units, major data stores and communication). Add component views only when they clarify a critical boundary.
6. List risks, open questions and mitigations. Identify what must be proven early (spikes, prototypes, load or security tests).
7. Define governance: fitness functions or automated checks that protect architectural characteristics, plus any approved exceptions with owners and review dates.

## Required outputs

```markdown
# Solution architecture: <initiative>

## Context
- Problem:
- Stakeholders:
- Constraints / assumptions:

## Non-functional requirements (NFRs)
| NFR | Target | Measurement |

## Options
### Option A
- Summary:
- Pros / cons:
### Option B
- Summary:
- Pros / cons:

## Decision
- Chosen option:
- Rationale:
- Consequences:
- ADR link (if any):

## C4-style views
- Context: (actors, system, external systems)
- Containers: (apps, services, data stores, queues)

## Risks and spikes
| Risk | Impact | Mitigation / proof |

## Governance and fitness functions
| Characteristic | Fitness function / check | Exception (owner, expiry) |
```

## Rules

- Do not present a single option as inevitable without recording alternatives considered.
- Do not omit NFRs or treat them as “non-functional” afterthoughts.
- Do not skip Context and Container views when multiple systems or teams are involved.
- Do not encode exceptions without an owner and review date.
- Do not collapse business capability maps into deployment diagrams; keep capability and solution concerns distinct then link them.
- Do not claim TOGAF or C4 certification; use the methods as practical communication tools.

## Related skills

- `documentation-and-adrs` — durable decision records
- `spec-driven-development` — behaviour specs after architecture direction
- `business-capability-modeling` — business ability maps and ownership
- `cloud-platform-architecture` — platform, tenancy and landing-zone design

## References

- C4 model: https://c4model.com/
- The Open Group TOGAF: https://www.opengroup.org/togaf
- C4 model notation overview: https://c4model.com/diagrams

## Verification

- [ ] Context, stakeholders and constraints are stated.
- [ ] NFRs (non-functional requirements) have targets or explicit unknowns.
- [ ] At least two options are compared and a decision is recorded.
- [ ] C4-style context and container views are present.
- [ ] Risks, spikes and mitigations are listed.
- [ ] Governance, fitness functions or exceptions have owners.
