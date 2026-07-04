---
name: risk-management
description: Identifies risks, scores likelihood and impact, selects treatment, assigns owners and review cadence. Use when building or updating a risk register, treating agent autonomy risks, or deciding mitigate, transfer, accept or avoid.
aliases:
  - risk-register
  - risk-treatment
  - enterprise-risk-management
---

# Risk Management

## When to use

Use this skill when work must identify, assess and treat risks with explicit owners and review cadence. Apply it to delivery programmes, platform changes, security and compliance exposure, operational failure modes, data and privacy impact, and **agent autonomy risks** such as unsupervised tool use, irreversible actions, prompt injection, data exfiltration via tools, runaway cost or multi-agent coordination failures. Use it whenever a risk register entry, treatment decision or residual-risk statement is required before proceeding.

## When not to use

- Do not use this skill only to rank a backlog or choose the next task — use `prioritization`.
- Do not use it only to challenge an uncertain hypothesis without a treatment plan — use `uncertainty-driven-development`.
- Do not use it for live incident stabilisation and postmortem learning alone — use `incident-response-and-postmortems`.
- Do not use it only to request approval for a single high-risk action — use `human-in-the-loop` (still record the risk if treatment is ongoing).

## Objective

Produce a maintained risk register in which each material risk has a clear description, likelihood and impact assessment, chosen treatment (mitigate, transfer, accept or avoid), accountable owner, review cadence and residual risk after treatment.

## Procedure

1. Frame the context: system or programme boundary, stakeholders, assets, threat sources and decision that depends on the risk view.
2. Identify risks, including agent-specific risks (autonomous tool calls, weak approval gates, untrusted retrieval or memory, model misbehaviour, supply-chain and secret exposure).
3. Assess each risk for likelihood and impact using an agreed scale; record assumptions and evidence, not intuition alone.
4. Select treatment for each risk: **mitigate** (controls), **transfer** (insurance, vendor, shared responsibility), **accept** (with explicit authority), or **avoid** (do not take the action or change scope).
5. Assign an owner, due date for controls, and a review cadence (for example weekly during delivery, monthly in steady state, or after every material change).
6. Implement or schedule treatments; link controls to tests, guardrails, runbooks or architectural changes where applicable.
7. Record residual risk and escalate acceptance of high residual risk to a human decision-maker before go-live or autonomy expansion.
8. Re-assess when scope, architecture, threat model or agent capabilities change.

## Required outputs or templates

```markdown
# Risk register entry

| Field | Value |
|---|---|
| Risk ID | RISK-NNN |
| Title | <short name> |
| Description | <what could go wrong and how> |
| Category | delivery / security / operational / agent-autonomy / compliance / other |
| Likelihood | low / medium / high (with rationale) |
| Impact | low / medium / high (with rationale) |
| Inherent risk | likelihood × impact summary |
| Treatment | mitigate / transfer / accept / avoid |
| Controls | <specific actions or controls> |
| Owner | <accountable person or role> |
| Review cadence | <interval or trigger> |
| Residual risk | <after treatment> |
| Acceptance | required / granted / not applicable |
| Evidence | <links to tests, policies, tickets> |
```

Also produce a short summary of top risks, treatments in progress and any accepted residual risk awaiting human approval.

## Rules

- Do not treat prioritisation of work items as a substitute for a risk register or treatment decision.
- Do not accept high residual risk without an explicit owner and recorded authority.
- Do not omit agent autonomy risks when agents can act, spend, write, delete or call external tools.
- Do not invent likelihood or impact scores without stating the basis for the score.
- Do not close a risk solely because an incident has not yet occurred.
- Do not leave treatments without an owner, due date or review cadence.
- Do not weaken security, safety or audit controls as an informal “accept” decision.

## Related skills

- `prioritization`
- `uncertainty-driven-development`
- `incident-response-and-postmortems`
- `human-in-the-loop`

## References

- [ISO 31000 risk management](https://www.iso.org/iso-31000-risk-management.html)
- [NIST Risk Management Framework (RMF)](https://csrc.nist.gov/projects/risk-management/about-rmf)

## Verification

- [ ] Risk register entries exist for material risks, including agent autonomy risks where relevant.
- [ ] Likelihood and impact are scored with rationale.
- [ ] Each risk has a treatment (mitigate, transfer, accept or avoid).
- [ ] Owner and review cadence are assigned.
- [ ] Residual risk and acceptance status are recorded.
- [ ] Treatments are linked to concrete controls or escalation.
