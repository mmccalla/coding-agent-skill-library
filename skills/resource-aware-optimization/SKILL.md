---
name: resource-aware-optimization
description: Use when an agent must balance quality, cost, latency, compute, memory, model choice, bandwidth, context budget, or service availability.
aliases:
  - resource-aware-optimisation
  - performance-optimization
---

# Resource-Aware Optimisation

## When to use

Use this skill when a coding agent must operate within budgets: time, tokens, memory, CPU/GPU, API cost, context window, rate limits, latency, energy, or human review capacity.

## Objective

Balance quality, cost, latency, model choice, context budget, and fallback paths without compromising correctness.

## Procedure

1. Identify resource constraints and service limits.
2. Estimate task complexity before execution.
3. Select the cheapest reliable strategy that satisfies the success criteria.
4. Escalate to more capable models, deeper reasoning or broader search only when justified.
5. Monitor actual consumption during execution.
6. Fall back or degrade gracefully when limits are reached.

## Model/tool selection

Use small, fast models for classification, formatting, simple extraction and guardrail checks. Use larger models for architecture, ambiguous reasoning, multi-file code changes and synthesis. Use deterministic tools for tests, parsing, type checking, formatting and calculations.

## Implementation guidance

Maintain a resource budget object:

```json
{
  "max_cost_usd": 1.00,
  "max_latency_seconds": 60,
  "max_iterations": 5,
  "model_tier": "auto",
  "fallback_model": "small-fast",
  "context_budget_tokens": 120000
}
```

Log estimates and actuals so future routing decisions improve.

## Guardrails

- Do not use the most expensive model by default.
- Do not sacrifice correctness where safety, security or data integrity is at stake.
- Do not exceed user-defined budgets without approval.
- Prefer graceful degradation over total failure when the user can still receive value.
- For platform cloud spend, allocation, unit economics or FinOps reviews, use `finops-practice` instead of this skill.

## Related skills

- `finops-practice` — platform and cloud financial operations
- `performance-engineering` — application/platform latency and capacity
- `evaluation-and-monitoring` — cost as an operational metric

## Verification
- [ ] Resource budgets are explicit.
- [ ] Complexity estimate is captured.
- [ ] Model/tool routing is justified.
- [ ] Fallback path exists.
- [ ] Actual cost/latency/usage is reported where available.
