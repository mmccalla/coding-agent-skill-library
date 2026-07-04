---
name: finops-practice
description: Applies FinOps Inform, Optimise and Operate practices for cloud and agent platform cost. Use when designing allocation, unit economics, budgets, forecasts, rightsizing, commitments or cost anomaly response across teams and platforms.
aliases:
  - finops
  - cloud-cost-management
  - cloud-financial-operations
---

# FinOps Practice

## When to use

Use this skill when managing **platform and organisational cost** for cloud, data and agent platforms. Apply it to allocation tags and labels, showback and chargeback, unit economics, budgets and forecasts, rightsizing, commitment and savings-plan strategy, and cost anomaly detection. Include agent platform cost drivers such as inference, embeddings, vector databases, storage, orchestration and egress. Use FinOps when finance, engineering and product need a shared operating model for spend visibility and continuous optimisation.

## When not to use

- Do not use this skill for **single agent-run** token, model-tier or session budgets — use `resource-aware-optimization`.
- Do not use it only to define reliability SLOs or error-budget policy — use `slo-error-budget-management`.
- Do not use it only to design a landing zone or tenancy model — use `cloud-platform-architecture` (cost allocation may still inform tagging standards).
- Do not use it only to measure quality metrics without cost ownership — use `evaluation-and-monitoring` for quality signals, then FinOps for spend ownership.

## Objective

Establish a FinOps operating loop — **Inform**, **Optimise**, **Operate** — so teams can see cost, improve unit economics and run budgets, forecasts and anomaly response with clear ownership across cloud and agent platforms.

## Procedure

1. **Inform**: inventory cost sources (compute, storage, network, managed services, inference APIs, embeddings, vector databases, egress) and define allocation dimensions (team, product, environment, workload, customer or cost centre).
2. Enforce consistent allocation tags or labels and map untagged spend to an owner; publish showback or chargeback reports stakeholders can act on.
3. Define unit economics (for example cost per active user, per workflow run, per 1k tokens served, per GB stored or per successful retrieval) and baselines for trend comparison.
4. Set budgets and forecasts with thresholds and owners; connect alerts to actionable channels, not silent dashboards.
5. **Optimise**: rightsizing, idle resource removal, storage tiering, commitment or savings-plan strategy, and architecture choices that reduce waste without harming reliability or safety.
6. **Operate**: run a recurring FinOps cadence (review anomalies, forecast variance, commitment coverage and unit-economic drift); assign remediation owners and due dates.
7. For agent platforms, separate platform-level spend (shared inference endpoints, vector stores, embedding pipelines) from product allocation so teams see both shared and attributable cost.
8. Revisit allocation and optimisation after material architecture or pricing changes.

## Required outputs or templates

```markdown
# FinOps decision record

Scope: <platform / product / account>
Phase focus: Inform / Optimise / Operate

## Allocation
- Dimensions: <team, product, env, ...>
- Tags/labels required: <keys>
- Showback or chargeback: <model>
- Untagged spend owner: <role>

## Unit economics
| Unit | Definition | Baseline | Current | Owner |
|---|---|---|---|---|
| e.g. cost per workflow run | total attributable spend / successful runs | ... | ... | ... |

## Budgets and forecasts
- Budget period and amount:
- Forecast method:
- Alert thresholds:
- Anomaly response owner:

## Optimisation backlog
| Opportunity | Estimated saving | Risk to reliability/safety | Owner | Status |
|---|---|---|---|---|
```

Include agent platform line items (inference, embeddings, vector DB, egress) when in scope.

## Rules

- Do not manage a single agent session’s token or model budget with this skill; use `resource-aware-optimization` for per-run resource trade-offs.
- Do not optimise cost by removing security, audit, backup or reliability controls without explicit acceptance of risk.
- Do not report platform spend without allocation ownership (showback or chargeback path).
- Do not buy commitments without usage evidence and a coverage plan.
- Do not ignore egress, idle environments or orphaned vector indexes as “small” line items.
- Do not treat FinOps as a one-off cost-cutting exercise; maintain Inform → Optimise → Operate cadence.

## Related skills

- `resource-aware-optimization`
- `cloud-platform-architecture`
- `slo-error-budget-management`
- `evaluation-and-monitoring`

## References

- FinOps Foundation Framework: https://www.finops.org/framework/
- FinOps Foundation: https://www.finops.org/

## Verification

- [ ] FinOps phase (Inform, Optimise, Operate) is explicit for the work.
- [ ] Allocation tags or showback/chargeback model is defined.
- [ ] Unit economics are stated for material workloads.
- [ ] Budgets, forecasts or anomaly response owners exist.
- [ ] Agent platform cost drivers are included when relevant.
- [ ] Optimisation actions do not silently weaken reliability or safety.
