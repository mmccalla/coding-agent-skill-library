---
name: infrastructure-as-code
description: Manages declarative infrastructure with plan/apply workflows, drift control, secrets hygiene and review. Use when defining or changing cloud or platform resources through IaC rather than click-ops or CI alone.
aliases:
  - iac
  - declarative-infrastructure
  - terraform-practice
---

# Infrastructure as Code

## When to use

Use this skill when infrastructure must be defined, reviewed and applied as **declarative** code: compute, network, identity, data stores, platform baselines and shared services. Apply it to plan/apply (or equivalent preview/deploy) workflows, drift detection, module design, state management, secrets handling and peer review of infrastructure changes. Use it whenever click-ops would create untracked, non-reproducible environments.

## When not to use

- Do not use this skill only to design build and deploy pipelines — use `ci-cd-and-automation` for pipeline safety; IaC may be invoked from CI but remains a separate concern.
- Do not use it only for dependency and supply-chain controls — use `secure-sdlc-and-supply-chain` when that skill is available.
- Do not use it only to decide landing zone or tenancy topology — use `cloud-platform-architecture` for platform design, then implement with IaC.
- Do not use it only for progressive delivery of application releases — use `release-engineering-and-progressive-delivery`.

## Objective

Keep infrastructure reproducible, reviewable and least-privilege by expressing desired state declaratively, previewing changes with plan/apply discipline, controlling drift, protecting secrets and requiring review before privileged applies.

## Procedure

1. Express the desired infrastructure state in declarative code (for example Terraform, OpenTofu, Bicep, CloudFormation or Pulumi) under version control.
2. Separate configuration by environment and blast radius; avoid a single state file that couples unrelated systems when practical.
3. Run a plan (or preview) and review the exact create/update/destroy set before apply; treat unexpected destroys as stop-the-line events.
4. Apply only through an approved path (local with explicit approval, or CI with constrained credentials); record who applied what and when.
5. Manage secrets outside the repository: inject via a secrets manager or OIDC-federated roles; never commit credentials or long-lived keys in code or state that is broadly readable.
6. Detect and remediate drift: reconcile click-ops changes back into code or destroy unauthorised resources according to policy.
7. Require peer review for privileged modules (identity, network, production data stores) and pin provider/module versions intentionally.
8. Verify with the narrowest useful checks (plan in CI, policy-as-code, smoke tests) and state residual risk for any manual exception.

## Required outputs or templates

```markdown
# IaC change record

## Scope
- Resources / modules:
- Environments:
- State backend:

## Plan summary
- Creates:
- Updates:
- Destroys:
- Unexpected changes: none / <list>

## Secrets and identity
- Credentials path: OIDC / secrets manager / other
- No secrets in repo or world-readable state: yes / no

## Review
- Reviewer:
- Policy-as-code / checks:

## Apply
- Path: CI / approved local
- Drift notes:
- Residual risk:
```

## Rules

- Do not apply infrastructure changes without a reviewed plan when the change can destroy or expose resources.
- Do not commit secrets, private keys or unrestricted cloud credentials into IaC or state artefacts.
- Do not use CI/CD skill guidance alone as a substitute for declarative desired state and drift control.
- Do not leave production drift untracked after emergency click-ops; reconcile promptly.
- Do not grant apply roles broader than the modules being changed.
- Do not pin to floating `latest` providers or modules for production without an explicit risk acceptance.

## Related skills

- `ci-cd-and-automation`
- `secure-sdlc-and-supply-chain`
- `cloud-platform-architecture`
- `release-engineering-and-progressive-delivery`

## References

- [HashiCorp Terraform — Core workflow (plan/apply)](https://developer.hashicorp.com/terraform/intro/core-workflow)
- [OpenTofu documentation](https://opentofu.org/docs/)

## Verification

- [ ] Desired state is expressed declaratively in version control.
- [ ] Plan/apply (or equivalent) preview was reviewed before apply.
- [ ] Secrets are not stored in the repository.
- [ ] Drift handling is stated for any manual change.
- [ ] Review and least-privilege apply path are documented.
- [ ] Residual infrastructure risk is recorded.
