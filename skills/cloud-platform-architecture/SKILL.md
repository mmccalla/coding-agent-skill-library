---
name: cloud-platform-architecture
description: Designs cloud landing zones, tenancy, shared services and network or identity boundaries. Use when defining platform foundations for multiple workloads rather than a single application solution.
aliases:
  - landing-zone-design
  - cloud-foundation-architecture
  - multi-tenant-platform-architecture
---

# Cloud Platform Architecture

## When to use

Use this skill when designing or reviewing the **shared cloud platform** that hosts many workloads: landing zones, account or subscription organisation, tenancy models, shared services (identity, networking, logging, security tooling, artefact registries), and network or identity boundaries between environments and teams. Apply it to multi-account or multi-subscription foundations, platform team blueprints, isolation for regulated data, and shared agent or data platform hosting—not to the internal design of one product alone.

## When not to use

- Do not use this skill for end-to-end design of a single application or product — use `solution-architecture` when that skill is available, or the relevant domain architecture skills.
- Do not use it only to design an event streaming backbone — use `event-streaming-platform-design` (platform tenancy may still host the brokers).
- Do not use it only to design lakehouse layers for one analytics estate — use `lakehouse-and-medallion-architecture`.
- Do not use it only to author Terraform or Bicep modules — use `infrastructure-as-code` for declarative implementation of the platform design.

## Objective

Define a clear, operable cloud platform architecture: landing zone structure, tenancy and isolation model, shared services catalogue, and network/identity boundaries that enable teams to deploy safely with least privilege and consistent guardrails.

## Procedure

1. Capture platform drivers: organisational units, regulatory constraints, data classification, blast-radius tolerance, and whether tenancy is by team, product, environment or customer.
2. Design the landing zone topology (accounts, subscriptions, projects or folders) and environment separation (for example production versus non-production).
3. Define the tenancy model: shared platform versus dedicated resources, isolation boundaries, and who may create or modify tenancy.
4. Catalogue shared services (identity provider integration, network hubs, DNS, certificate management, logging and security baselines, artefact registries, secrets platforms) and their ownership.
5. Specify network and identity boundaries: ingress/egress controls, private connectivity, service identities, role boundaries and break-glass access.
6. Define platform guardrails (policy-as-code, baseline encryption, logging, tagging for allocation) and how application teams consume the platform.
7. Document operational ownership, onboarding path for new workloads, and residual platform risks (noisy neighbour, shared credential scope, cross-tenant data paths).
8. Hand off implementation details to infrastructure-as-code and delivery automation without collapsing platform decisions into ad hoc per-app networking.

## Required outputs or templates

```markdown
# Cloud platform architecture summary

## Landing zone
- Topology: <accounts / subscriptions / folders>
- Environments: <list>
- Tenancy model: <team / product / customer / hybrid>

## Shared services
| Service | Purpose | Owner | Consumers |
|---|---|---|---|
| Identity | ... | platform | all workloads |
| Network hub | ... | ... | ... |

## Boundaries
- Network: <segmentation, private endpoints, egress policy>
- Identity: <roles, workload identities, human access>
- Data: <classification and residency constraints>

## Guardrails
- Policy-as-code / baselines:
- Logging and security monitoring:
- Tagging / allocation standards:

## Risks and open decisions
- ...
```

## Rules

- Do not design a one-off network for a single system and call it a landing zone.
- Do not share production and non-production identity or network trust without explicit justification.
- Do not grant platform-wide admin rights to application teams by default.
- Do not omit tenancy and blast-radius decisions when hosting multi-tenant or agent platforms.
- Do not leave shared services without an operational owner and onboarding path.
- Do not implement platform changes without a reviewable infrastructure-as-code path when the organisation uses IaC.

## Related skills

- `solution-architecture`
- `event-streaming-platform-design`
- `lakehouse-and-medallion-architecture`
- `infrastructure-as-code`

## References

- AWS Landing Zone / Control Tower guidance: https://docs.aws.amazon.com/controltower/latest/userguide/what-is-control-tower.html
- Azure landing zone conceptual architecture: https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/
- Google Cloud landing zone design: https://cloud.google.com/architecture/landing-zones

## Verification

- [ ] Landing zone topology and environments are explicit.
- [ ] Tenancy and isolation model is documented.
- [ ] Shared services and owners are listed.
- [ ] Network and identity boundaries are defined.
- [ ] Platform guardrails and residual risks are recorded.
- [ ] Scope is platform-level, not a single-application solution design.
