---
name: ai-model-governance
description: Governs AI models through inventory, purpose, risk tier, approval, monitoring, drift, kill-switch and retirement. Use when introducing, changing or operating models in production or agent workflows.
aliases:
  - model-governance
  - ai-model-lifecycle
  - model-risk-management
  - nist-ai-rmf-governance
---

# AI Model Governance

## When to use

Use this skill when an organisation introduces, swaps, fine-tunes, promotes or retires an AI model (including embedding, ranking or agent-routing models), or when operating models need inventory, risk tiering, approval, continuous monitoring, kill-switch readiness or formal retirement. Align operational controls with NIST AI RMF Govern / Map / Measure / Manage intent.

## When not to use

- Use `apply-laws-of-ai` for the mandatory session-start safety baseline and instruction hierarchy, not model inventory or lifecycle.
- Use `evaluation-and-monitoring` for one-shot or change-gated metrics, baselines and regression suites without full model lifecycle ownership.
- Use `learning-and-adaptation` only for bounded, reversible improvement loops with measured outcomes.
- Use `krag-evaluation-governance` for KRAG-specific retrieval, graph and answer release gates.
- Use `human-in-the-loop` for individual approval packets when governance policy already requires a human gate.

## Objective

Maintain accountable control over models in use: known inventory, stated purpose, risk tier, approved operating envelope, monitoring for drift and harm, enforceable kill-switch, and planned retirement—so models are not deployed or left running without ownership and evidence.

## Procedure

1. Register or update the model in an inventory: identifier, provider, version, modality, hosting location, data classification of inputs/outputs and owning team.
2. State purpose and prohibited uses. Map intended users, tasks and decision impact (advisory versus automated action).
3. Assign a risk tier using impact on people, safety, finance, privacy, legal exposure and autonomy. Higher tiers require stronger approval and monitoring.
4. Obtain approval appropriate to the risk tier before production use or material change (weights, prompt system, tools attached, or autonomy level). Record approver and conditions.
5. Define Measure controls: quality, safety, latency, cost, drift and abuse signals; thresholds that trigger review or rollback.
6. Implement Manage controls: kill-switch or traffic cut-over, rollback to prior version, incident contacts and human escalation for high-impact failures.
7. Plan retirement: deprecation notice, consumer migration, data retention for audit, and removal from inventory when fully decommissioned.
8. Revisit governance when purpose, data, tools or autonomy change—not only when metrics regress.

## Required outputs

```markdown
# Model governance record: <model id>

## Inventory
- Model / version:
- Provider / hosting:
- Owner:
- Input / output classification:

## Purpose and prohibitions
- Intended use:
- Prohibited use:

## Risk tier
- Tier:
- Rationale (impact, autonomy, data):

## Approval
- Approver:
- Date / conditions:
- Evidence attached:

## Monitoring and drift
| Signal | Threshold | Action |

## Kill-switch and rollback
- Disable path:
- Rollback target:
- On-call / escalation:

## Retirement plan
- Sunset criteria:
- Consumer migration:
- Inventory update:

## Residual risks
```

## Rules

- Do not deploy or materially change a production model without inventory entry and risk-tiered approval.
- Do not treat session laws (`apply-laws-of-ai`) as a substitute for model lifecycle governance.
- Do not rely on a single evaluation run as ongoing governance; define continuous monitoring and kill-switch paths.
- Do not leave retired models reachable without an explicit exception and owner.
- Do not hide model identity, version or owner from operators who must respond to incidents.
- Do not claim legal compliance with every AI regulation; align operational practice to NIST AI RMF and organisational policy.

## Related skills

- `evaluation-and-monitoring` — metrics, baselines and regression evaluation
- `apply-laws-of-ai` — immutable session safety baseline
- `human-in-the-loop` — approval and escalation packets
- `learning-and-adaptation` — bounded improvement with measurement
- `krag-evaluation-governance` — KRAG release and governance gates

## References

- NIST AI Risk Management Framework (AI RMF 1.0): https://www.nist.gov/itl/ai-risk-management-framework
- NIST AI RMF playbook: https://airc.nist.gov/AI_RMF_Knowledge_Base/Playbook
- NIST AI RMF resources: https://www.nist.gov/artificial-intelligence

## Verification

- [ ] Model inventory entry is complete (identity, owner, version, classification).
- [ ] Purpose, prohibitions and risk tier are explicit.
- [ ] Approval evidence matches the risk tier.
- [ ] Monitoring, drift thresholds and kill-switch / rollback are defined.
- [ ] Retirement or deprecation path is stated when relevant.
- [ ] Scope is lifecycle governance, not session laws or one-shot metrics alone.
